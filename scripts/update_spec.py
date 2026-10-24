"""Fill in the report spec boilerplate from known project details.

Run from anywhere: `python scripts/update_spec.py`
"""

from pathlib import Path

SPEC_PATH = Path(__file__).resolve().parents[1] / "REPORT_SPEC.md"

content = SPEC_PATH.read_text(encoding="utf-8")

# Update the global boilerplate section with what we learned, keeping unknowns as prompts.
content = content.replace(
    "* **Title:** [PENDING USER INPUT]",
    "* **Title:** Multi-Agent AI Health Diagnostic System (Multi-agent AI system for "
    "medical diagnosis using agentic AI orchestration, deep learning, and RAG)",
)
content = content.replace(
    "* **Institution:** Ajay Kumar Garg Engineering College, Ghaziabad "
    "(Dr. A.P.J. Abdul Kalam Technical University, Lucknow)",
    "* **Institution:** [PENDING USER INPUT]",
)

SPEC_PATH.write_text(content, encoding="utf-8")
print(f"Updated {SPEC_PATH}")
