"""Assertion layer: negation scope, subject attribution, and polarity.

Deterministic, rule-based resolver inspired by NegEx/ConText that runs
alongside symptom pattern matching. Every extracted finding carries a
polarity (present | absent | hypothetical), a subject (self | family |
other | hypothetical), a certainty (explicit | hedged), and the character
span it was found at — see
`.planning/2026-10-28-aegismed-improvement-phase/specs/SPEC-w0-assertion-nlp.md`.

The live probe case this module exists for::

    "no fever, no cough, no chest pain"

must yield zero *present* findings. Before this layer, the regex extractor
reported all three as present.

Documented conventions (each pinned by cases in `tests/fixtures/assertion_golden.json`):

- Negation scope is clause-local. Clauses split on punctuation and on
  contrast/addition connectors (but, and, however, though, ...).
- A pre-positioned cue ("no fever") negates the symptoms that follow it in
  the same clause. An odd number of preceding cues means absent; an even
  non-zero number means present — "not without a fever" is therefore a
  positive assertion, per the spec's double-negation convention.
- A bare post-positioned cue ("fever, no", "chest pain - negative") negates
  the symptom it follows. Only answer-fragment cues (no / negative / none /
  denied / denies) count post-positionally; "never" or "not" after a
  symptom ("fever never went away") does not.
- "If I had a fever" style conditionals are hypothetical — excluded from
  triage, retained in the output (spec open question 2 recommendation).
- Lay constructions where the surface negation IS the complaint ("no
  appetite" = decreased appetite, "can't sleep" = insomnia) are mapped to
  the canonical symptom as PRESENT via NEGATIVE_CONSTRUCTIONS. The
  preprocessor preserves these forms so this layer can see them.
- Family ("my mother has diabetes") and third-party ("my friend has
  asthma") findings keep their subject tag; consumers filter on
  polarity == "present" and subject == "self" for triage input.

Patient text is never logged by this module.
"""

import re
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Cue tables
# ---------------------------------------------------------------------------

# Cues that negate a symptom when they appear BEFORE it in the same clause.
# Both apostrophe and apostrophe-stripped forms are listed because
# TextPreprocessor.clean() strips apostrophes ("can't" -> "cant") while
# raw-text callers (compute_initial_belief) do not. The alternation is
# built longest-first so "no history of" wins over "no" at the same position.
NEGATION_CUES = [
    "no history of",
    "no signs of",
    "no evidence of",
    "negative for",
    "free of",
    "haven't",
    "havent",
    "hasn't",
    "hasnt",
    "doesn't",
    "doesnt",
    "didn't",
    "didnt",
    "don't",
    "dont",
    "cannot",
    "can't",
    "cant",
    "do not",
    "does not",
    "did not",
    "have not",
    "has not",
    "denies",
    "denying",
    "denied",
    "deny",
    "never",
    "without",
    "neither",
    "nor",
    "not",
    "negative",
    "no",
]

# Cues that negate a symptom when they appear AFTER it in the same clause
# ("fever, no", "chest pain - negative"). Deliberately narrow: only
# answer-fragment cues. "never"/"not" after a symptom ("fever never went
# away") must NOT negate it.
POST_NEGATION_CUES = ["denies", "denied", "negative", "none", "no"]

# Conditional/hypothetical constructions. The symptom exists only in a
# counterfactual, so it is excluded from triage (spec open question 2).
HYPOTHETICAL_CUES = [
    "if i had",
    "if i were",
    "if i get",
    "if i develop",
    "what if",
    "suppose",
    "hypothetically",
    "let's say",
    "lets say",
    "not sure if",
    "in case",
    "imagine",
]

# Hedging cues: the finding is still present and self-reported, but the
# patient is uncertain — surfaced as certainty="hedged".
HEDGE_CUES = [
    "maybe",
    "might",
    "possibly",
    "perhaps",
    "i think",
    "i guess",
    "i feel like",
    "it seems",
    "seems like",
    "sort of",
    "kind of",
    "a bit of",
    "somewhat",
]

# Subject cues. Family/other findings are retained in the output but
# excluded from triage input.
FAMILY_PATTERN = re.compile(
    r"\b(?:my|our)\s+"
    r"(?:mother|father|mom|dad|brother|sister|grandmother|grandfather|"
    r"grandma|grandpa|uncle|aunt|auntie|cousin|wife|husband|son|daughter|"
    r"nephew|niece|parents|grandparents|father-in-law|mother-in-law|"
    r"brother-in-law|sister-in-law|family)\b"
    r"|\bfamily history of\b"
    r"|\brun(?:s)? in (?:my|our|the) family\b"
)

OTHER_PATTERN = re.compile(
    r"\b(?:my|a)\s+(?:friend|coworker|co-worker|colleague|neighbour|neighbor|"
    r"roommate|boss|teacher)\b"
    r"|\ba friend of mine\b"
    r"|\bsomeone (?:i know|else)\b"
)

# Lay constructions where the surface negation IS the symptom report. The
# patient denying a body function is reporting the corresponding finding as
# PRESENT. These are consumed before generic cue logic so "no" does not also
# negate a following symptom, and the preprocessor preserves their surface
# form so this table can see it.
NEGATIVE_CONSTRUCTIONS: Dict[str, Tuple[str, str]] = {
    "no appetite": ("decreased appetite", "gastrointestinal"),
    "not hungry": ("decreased appetite", "gastrointestinal"),
    "no energy": ("fatigue", "constitutional"),
    "can't sleep": ("insomnia", "psychiatric"),
    "cant sleep": ("insomnia", "psychiatric"),
    "not able to sleep": ("insomnia", "psychiatric"),
    "unable to sleep": ("insomnia", "psychiatric"),
    "can't breathe": ("shortness of breath", "respiratory"),
    "cant breathe": ("shortness of breath", "respiratory"),
    "cannot breathe": ("shortness of breath", "respiratory"),
}

# Lay phrasings that mean a canonical symptom outright (polarity-neutral:
# the phrase asserts the symptom regardless of cue position). The resolver
# maps them at find-time so negated occurrences ("not running a
# temperature") resolve to the canonical symptom with the right polarity —
# the preprocessor deliberately leaves negated scopes untouched, so this
# table is the negation-safe home for lay vocabulary. Keys are matched
# word-bounded; values are the canonical finding name and category.
LAY_SYMPTOM_ALIASES: Dict[str, Tuple[str, str]] = {
    "running a temperature": ("fever", "constitutional"),
    "running temperature": ("fever", "constitutional"),
    "running a high temperature": ("fever", "constitutional"),
    "high temperature": ("fever", "constitutional"),
    "feverish": ("fever", "constitutional"),
    "head hurts": ("headache", "neurological"),
    "head pain": ("headache", "neurological"),
    "head is pounding": ("headache", "neurological"),
    "dizzy": ("dizziness", "neurological"),
    "feeling dizzy": ("dizziness", "neurological"),
    "dizzy spells": ("dizziness", "neurological"),
    "lightheaded": ("dizziness", "neurological"),
    "nauseous": ("nausea", "gastrointestinal"),
    "upset stomach": ("nausea", "gastrointestinal"),
    "throwing up": ("vomiting", "gastrointestinal"),
    "throw up": ("vomiting", "gastrointestinal"),
    "stomach ache": ("abdominal pain", "gastrointestinal"),
    "stomach hurts": ("abdominal pain", "gastrointestinal"),
    "belly pain": ("abdominal pain", "gastrointestinal"),
    "tummy ache": ("abdominal pain", "gastrointestinal"),
    "constipated": ("constipation", "gastrointestinal"),
    "throat hurts": ("throat pain", "ENT"),
    "neck hurts": ("neck pain", "musculoskeletal"),
    "ears hurt": ("ear pain", "ENT"),
    "blocked nose": ("nasal congestion", "respiratory"),
    "stuffy nose": ("nasal congestion", "respiratory"),
    "nose is blocked": ("nasal congestion", "respiratory"),
    "nose is running": ("runny nose", "respiratory"),
    "aching joints": ("joint pain", "musculoskeletal"),
    "itchy skin": ("itching", "dermatological"),
    "skin is itchy": ("itching", "dermatological"),
    "exhausted": ("fatigue", "constitutional"),
    "feeling tired": ("fatigue", "constitutional"),
    "so tired": ("fatigue", "constitutional"),
    "feeling weak": ("weakness", "neurological"),
    "feel weak": ("weakness", "neurological"),
    "chest feels tight": ("chest tightness", "respiratory"),
}

# Medical conditions patients mention in passing (mostly for family-history
# attribution). Symptoms live in NLPAgent.SYMPTOM_PATTERNS; these are
# conditions rather than symptoms, but the extractor must still find and
# attribute them ("my mother has diabetes" must reach the output tagged
# subject=family and stay out of the triage belief).
CONDITION_PATTERNS = {
    "condition": r'\b(diabetes|asthma|hypertension|high blood pressure|cancer|stroke|'
                 r'heart disease|heart problem|thyroid problem|thyroid disease|'
                 r'kidney disease|epilepsy|arthritis|tuberculosis)\b',
}

# Phrases that contain a clause connector inside a single finding; masked
# with a SAME-LENGTH placeholder before clause splitting so they are never
# torn apart and all offsets stay valid.
PROTECTED_PHRASES = ["pins and needles", "fever and chills", "nausea and vomiting"]

_MASK_CHAR = "\x00"

_CLAUSE_SPLIT = re.compile(
    r"(?:[,;.!?\n]|\s+\b(?:but|however|though|although|whereas|and|plus|also|so)\b\s+)"
)

# A clause consisting of nothing but a post-negation answer fragment
# ("fever, no" — the comma also splits clauses, so the fragment must be
# merged back into the clause it answers).
_CUE_FRAGMENT_RE = re.compile(r"^(?:denies|denied|negative|none|no)[.,;!?]*$")


def _cue_regex(cues: List[str]) -> re.Pattern:
    ordered = sorted(set(cues), key=len, reverse=True)
    return re.compile(r"\b(?:" + "|".join(re.escape(c) for c in ordered) + r")\b")


_PRE_NEG_RE = _cue_regex(NEGATION_CUES)
_POST_NEG_RE = _cue_regex(POST_NEGATION_CUES)
_HYPO_RE = _cue_regex(HYPOTHETICAL_CUES)
_HEDGE_RE = _cue_regex(HEDGE_CUES)
_CONSTRUCTION_RE = re.compile(
    r"\b(?:" + "|".join(re.escape(s) for s in sorted(NEGATIVE_CONSTRUCTIONS, key=len, reverse=True)) + r")\b"
)


def _split_clauses(text: str) -> List[Tuple[str, int]]:
    """Split into clauses, returning (clause_text, absolute_start) pairs.

    Protected phrases are masked with a same-length placeholder for
    splitting and restored afterwards, so every offset stays valid against
    the original (lowercased) input.
    """
    masked = text
    for phrase in PROTECTED_PHRASES:
        if phrase in masked:
            masked = masked.replace(phrase, phrase[0] + _MASK_CHAR * (len(phrase) - 1))

    clauses: List[Tuple[str, int]] = []
    start = 0
    for match in _CLAUSE_SPLIT.finditer(masked):
        chunk = masked[start:match.start()]
        if chunk.strip():
            offset = start + (len(chunk) - len(chunk.lstrip()))
            clauses.append((chunk.strip(), offset))
        start = match.end()
    tail = masked[start:]
    if tail.strip():
        offset = start + (len(tail) - len(tail.lstrip()))
        clauses.append((tail.strip(), offset))

    restored = []
    for chunk, offset in clauses:
        for phrase in PROTECTED_PHRASES:
            chunk = chunk.replace(phrase[0] + _MASK_CHAR * (len(phrase) - 1), phrase)
        restored.append((chunk, offset))
    return restored


def _merge_cue_fragments(
    clauses: List[Tuple[str, int]],
) -> List[Tuple[str, int]]:
    """Merge bare post-negation fragments ("fever, no") into their predecessor.

    The comma in "fever, no" is both the post-cue separator and a clause
    boundary, so without this merge the cue lands in its own clause and the
    symptom reads as affirmative. Only fragments consisting solely of an
    answer-fragment cue are merged.
    """
    merged: List[Tuple[str, int]] = []
    for chunk, offset in clauses:
        if merged and _CUE_FRAGMENT_RE.match(chunk):
            prev_chunk, prev_offset = merged[-1]
            merged[-1] = (f"{prev_chunk}, {chunk}", prev_offset)
        else:
            merged.append((chunk, offset))
    return merged


def _construction_spans(clause: str) -> List[Tuple[int, int]]:
    """Spans of negative constructions in a clause (merged, non-overlapping)."""
    spans = [(m.start(), m.end()) for m in _CONSTRUCTION_RE.finditer(clause)]
    return _merge_spans(spans)


def _in_spans(pos: int, spans: List[Tuple[int, int]]) -> bool:
    return any(start <= pos < end for start, end in spans)


class AssertionResolver:
    """Resolves polarity, subject, and certainty for symptom/condition mentions.

    The symptom patterns are injected by the NLPAgent (they live there so the
    P0 regex fixes stay with the extractor); standalone users pass their own.
    """

    def __init__(self, symptom_patterns: Dict[str, str]):
        self._symptom_patterns = [
            (category, re.compile(pattern))
            for category, pattern in symptom_patterns.items()
        ]
        self._condition_patterns = [
            (category, re.compile(pattern))
            for category, pattern in CONDITION_PATTERNS.items()
        ]

    # -- public API ---------------------------------------------------------

    def analyze(self, text: str) -> List[Dict[str, Any]]:
        """Resolve every symptom/condition mention in `text`.

        Returns findings with keys: symptom, category, polarity, subject,
        certainty, span, rule. Polarity precedence when the same symptom is
        found in several clauses: present > absent > hypothetical (a present
        mention anywhere is never dropped — safer for triage).
        """
        if not text or not text.strip():
            return []

        findings: List[Dict[str, Any]] = []
        clauses = _merge_cue_fragments(_split_clauses(text.lower()))
        for clause, clause_offset in clauses:
            findings.extend(self._analyze_clause(clause, clause_offset))
        return self._dedupe(findings)

    # -- internals ----------------------------------------------------------

    def _term_hits(self, clause: str) -> List[Tuple[int, int, Dict[str, Any]]]:
        hits: List[Tuple[int, int, Dict[str, Any]]] = []
        for category, regex in self._symptom_patterns + self._condition_patterns:
            for m in regex.finditer(clause):
                surface = m.group(1)
                hits.append((m.start(1), m.end(1), {"symptom": surface, "category": category}))
        for alias, (canonical, category) in LAY_SYMPTOM_ALIASES.items():
            for m in re.finditer(rf"\b{re.escape(alias)}\b", clause):
                hits.append((m.start(), m.end(), {"symptom": canonical, "category": category}))
        return sorted(hits)

    @staticmethod
    def _clause_subject(clause: str) -> str:
        if FAMILY_PATTERN.search(clause):
            return "family"
        if OTHER_PATTERN.search(clause):
            return "other"
        return "self"

    def _analyze_clause(self, clause: str, clause_offset: int) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []
        subject = self._clause_subject(clause)
        conditional = bool(_HYPO_RE.search(clause))
        hedged = bool(_HEDGE_RE.search(clause))

        constructions = _construction_spans(clause)

        # Negative constructions first: the surface negation IS the complaint.
        for m in _CONSTRUCTION_RE.finditer(clause):
            surface = m.group(0)
            canonical, category = NEGATIVE_CONSTRUCTIONS[surface]
            findings.append({
                "symptom": canonical,
                "category": category,
                "polarity": "hypothetical" if conditional else "present",
                "subject": "hypothetical" if conditional else subject,
                "certainty": "hedged" if hedged and not conditional else "explicit",
                "span": (clause_offset + m.start(), clause_offset + m.end()),
                "rule": "negative-construction",
            })

        cue_spans = [
            (m.start(), m.end())
            for m in _PRE_NEG_RE.finditer(clause)
            if not _in_spans(m.start(), constructions)
        ]
        post_cue_positions = [
            m
            for m in _POST_NEG_RE.finditer(clause)
            if not _in_spans(m.start(), constructions)
        ]

        for pos_start, pos_end, meta in self._term_hits(clause):
            if _in_spans(pos_start, constructions):
                continue  # already resolved as a negative construction

            pre_cues = [c for c in cue_spans if c[1] <= pos_start]
            post_cues = [m for m in post_cue_positions if m.start() >= pos_end]

            if conditional:
                polarity, rule = "hypothetical", "conditional"
            elif len(pre_cues) % 2 == 1:
                polarity, rule = "absent", "pre-negation"
            elif len(pre_cues) >= 2:
                polarity, rule = "present", "double-negation"
            elif post_cues:
                polarity, rule = "absent", "post-negation"
            else:
                polarity, rule = "present", "affirmative"

            resolved_subject = "hypothetical" if conditional else subject
            findings.append({
                "symptom": meta["symptom"],
                "category": meta["category"],
                "polarity": polarity,
                "subject": resolved_subject,
                "certainty": "hedged" if hedged and polarity == "present" else "explicit",
                "span": (clause_offset + pos_start, clause_offset + pos_end),
                "rule": rule,
            })
        return findings

    @staticmethod
    def _dedupe(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        precedence = {"present": 0, "absent": 1, "hypothetical": 2}
        best: Dict[Tuple[str, str], Dict[str, Any]] = {}
        order: List[Tuple[str, str]] = []
        for f in findings:
            key = (f["symptom"], f["category"])
            if key not in best:
                best[key] = f
                order.append(key)
            elif precedence[f["polarity"]] < precedence[best[key]["polarity"]]:
                best[key] = f
        return [best[k] for k in order]


def _merge_spans(spans: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    if not spans:
        return []
    spans = sorted(spans)
    merged = [spans[0]]
    for start, end in spans[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return merged


def exclusion_spans(text: str) -> List[Tuple[int, int]]:
    """Text spans whose substring symptom matches must NOT score in triage.

    Pattern-free (usable from core code without importing the agent layer):
    covers negated regions — from the earliest governing pre-negation cue to
    the clause end ("no fever or chills" covers both), or clause start
    through the last post-negation cue ("fever, no") — plus whole clauses
    attributed to family/other or spoken hypothetically. Negative-construction
    surfaces ("no appetite") are NOT excluded: they are present complaints.
    """
    spans: List[Tuple[int, int]] = []
    clauses = _merge_cue_fragments(_split_clauses(text.lower()))
    for clause, clause_offset in clauses:
        subject = _clause_subject_static(clause)
        if subject in ("family", "other") or _HYPO_RE.search(clause):
            spans.append((clause_offset, clause_offset + len(clause)))
            continue

        constructions = _construction_spans(clause)
        pre_cues = [
            (m.start(), m.end())
            for m in _PRE_NEG_RE.finditer(clause)
            if not _in_spans(m.start(), constructions)
        ]
        post_cues = [
            m
            for m in _POST_NEG_RE.finditer(clause)
            if not _in_spans(m.start(), constructions)
        ]
        if pre_cues:
            first = min(c[0] for c in pre_cues)
            spans.append((clause_offset + first, clause_offset + len(clause)))
        elif post_cues:
            spans.append((clause_offset, clause_offset + max(m.end() for m in post_cues)))
    return _merge_spans(spans)


def negation_scopes(text: str) -> List[Tuple[int, int]]:
    """Spans where a negation cue governs the text (clause-local).

    Used by TextPreprocessor.normalize_symptoms so canonicalization never
    rewrites inside a negated scope (the negation must survive for this
    layer to resolve). Negative-construction surfaces ("no appetite") count
    as negated here — the preprocessor must preserve them so the resolver's
    NEGATIVE_CONSTRUCTIONS table can map them — but NOT in
    ``exclusion_spans``: there they are present complaints whose KB overlap
    should still score. Subject attribution is deliberately NOT considered.
    """
    spans: List[Tuple[int, int]] = []
    clauses = _merge_cue_fragments(_split_clauses(text.lower()))
    for clause, clause_offset in clauses:
        pre = [(m.start(), m.end()) for m in _PRE_NEG_RE.finditer(clause)]
        post = [m for m in _POST_NEG_RE.finditer(clause)]
        if pre:
            spans.append((clause_offset + min(c[0] for c in pre), clause_offset + len(clause)))
        elif post:
            spans.append((clause_offset, clause_offset + max(m.end() for m in post)))
    return _merge_spans(spans)


def _clause_subject_static(clause: str) -> str:
    if FAMILY_PATTERN.search(clause):
        return "family"
    if OTHER_PATTERN.search(clause):
        return "other"
    return "self"
