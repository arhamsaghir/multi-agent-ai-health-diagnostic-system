"""Helpers for keeping patient-supplied free text out of logs.

Symptom descriptions are protected health information. Logs need to show that
input was received and to correlate it with a run, but the text itself must
never be written to disk verbatim.
"""

import hashlib


def text_fingerprint(text: str | None) -> str:
    """Return a non-reversible fingerprint of free-text clinical input.

    The fingerprint carries the input length (useful for spotting truncation)
    and a short SHA-256 prefix (useful for correlating log lines with a run),
    without disclosing the content.
    """
    if not text:
        return "empty"
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]
    return f"len={len(text)} sha256={digest}"


def redact(text: str | None, *secrets: str | None, placeholder: str = "<redacted>") -> str:
    """Replace every occurrence of the given secrets in ``text``.

    Exception messages raised by downstream libraries can echo back the input
    that triggered them (an LLM request body, a rejected prompt). Scrubbing
    the known patient strings keeps those diagnostics while removing the
    clinical content from the log line.
    """
    if not text:
        return ""
    for secret in secrets:
        if secret and len(secret) >= 4:
            text = text.replace(secret, placeholder)
    return text


def safe_error(exc: BaseException, *secrets: str | None) -> str:
    """Render an exception for logging with patient text scrubbed out."""
    return redact(f"{type(exc).__name__}: {exc}", *secrets)
