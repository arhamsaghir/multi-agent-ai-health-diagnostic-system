"""NLP Symptom Agent — Medical text understanding.

NLPAgent is exported lazily (PEP 562): an eager import here would make
``src.agents.nlp.assertion`` (imported by the data-layer preprocessor)
trigger the full agent import cycle at module-load time.
"""

from typing import Any

__all__ = ["NLPAgent"]


def __getattr__(name: str) -> Any:
    if name == "NLPAgent":
        from src.agents.nlp.agent import NLPAgent

        return NLPAgent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
