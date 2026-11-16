"""Guard: the retired 98% self-generated claim must not reappear as accuracy.

w0-benchmark-honesty R8. Walks the repository for the retired-claim pattern
(the 98.0% top-1 figure, the 196/200 fraction, and the phrase "Top-1
diagnostic accuracy") and fails on any occurrence that is not either:

  - in an ALLOWED path — the retraction evidence, the historical results
    record, or the planning record (these ARE the retraction story),
  - in a PENDING_OWNED path — owned by a module that will retire the claim
    itself, or
  - explicitly labeled as the retired measurement on the same or an
    adjacent line (label markers below).

SHRINK PENDING_OWNED as its owning module lands — an empty list is the goal
state:
  - paper/**  -> `publication-truth` phase A retracts the claim in the paper.
  - patent/** -> `w3-patent` re-scopes the claims. Patent specification files
    are a legal artifact and are NEVER edited without explicit user say-so.
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RETIRED_CLAIM = re.compile(r"98(\.0)?\s*%|196/200|Top-1 diagnostic accuracy")

# Paths that legitimately contain the pattern: they ARE the retraction
# evidence, the labeled historical record, or the planning log of the claim.
ALLOWED_PREFIXES = (
    "data/benchmarks/",               # RETIREMENT.md + headered historical results
    ".planning/",                     # improvement-phase specs + phase-3 claim log
    "docs/research/public_release/",  # the research that established circularity
)

# Owned debt: the pattern still lives here until the owning module lands.
# SHRINK THIS LIST as each owner merges — an empty list is the goal state.
PENDING_OWNED_PREFIXES = (
    "paper/",   # publication-truth phase A
    "patent/",  # w3-patent (legal artifact — user gate)
)

# A hit outside the lists above is acceptable only if the hit line, or an
# adjacent line, carries an explicit retirement label (case-insensitive).
LABEL_MARKERS = (
    "retirement.md",
    "retracted",
    "retired",
    "not an accuracy",
    "internal-consistency",
    "internal consistency",
    "self-generated",
)

SKIP_DIRS = {
    ".git",
    "node_modules",
    "venv",
    "venv.nosync",
    ".next",
    "__pycache__",
    "dist",
    ".zcode",
}
SCAN_SUFFIXES = {".md", ".tex", ".py"}


def _retirement_violations() -> list:
    violations = []
    for path in sorted(PROJECT_ROOT.rglob("*")):
        if not path.is_file() or path.suffix not in SCAN_SUFFIXES:
            continue
        # This file contains the pattern literal by design.
        if path.name == "test_retired_claims_guard.py":
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        rel = path.relative_to(PROJECT_ROOT).as_posix()
        if any(rel == p or rel.startswith(p) for p in ALLOWED_PREFIXES):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        lines = text.splitlines()
        owned = any(rel == p or rel.startswith(p) for p in PENDING_OWNED_PREFIXES)
        for idx, line in enumerate(lines):
            if not RETIRED_CLAIM.search(line):
                continue
            if owned:
                continue
            window = lines[max(0, idx - 1): idx + 2]
            if any(marker in chunk.lower() for chunk in window for marker in LABEL_MARKERS):
                continue
            violations.append(f"{rel}:{idx + 1}: {line.strip()[:160]}")
    return violations


def test_no_unlabeled_retired_accuracy_claim_anywhere_in_repo():
    """No document may state the retired 98% figure as an accuracy result.

    Every occurrence must be allowlisted evidence, owned by
    publication-truth / w3-patent, or carry a retirement label adjacent to
    the claim (see data/benchmarks/RETIREMENT.md).
    """
    violations = _retirement_violations()
    assert not violations, (
        "The retired 98% self-generated claim reappeared without a retirement "
        "label. Every occurrence must be allowlisted evidence, owned by "
        "publication-truth/w3-patent, or labeled as the retired measurement "
        "(see data/benchmarks/RETIREMENT.md). Violations:\n  "
        + "\n  ".join(violations)
    )
