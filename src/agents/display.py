"""Agent display metadata for the live execution stepper.

Single source of truth so the UI never advertises a model or technique the
running pipeline does not actually use.
"""

NODE_DISPLAY = {
    "triage": {"agent": "DEMAT Active Triage", "model": "Entropy Minimization"},
    "symptoms": {"agent": "NLP Agent", "model": "Clinical NLP (patterns + optional NER)"},
    "image": {"agent": "Vision Agent", "model": "ResNet (synthetic X-ray training set)"},
    "knowledge": {"agent": "RAG Agent", "model": "FAISS Vector Store"},
    "risk": {"agent": "Prediction Agent", "model": "GradientBoosting Risk Models"},
    "synthesis": {"agent": "Synthesis Agent", "model": "LLM Synthesis (rule-based fallback)"},
}
