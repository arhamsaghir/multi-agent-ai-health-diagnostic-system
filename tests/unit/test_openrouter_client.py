"""Regression tests for the OpenRouter/OmniRoute client.

Free-tier models sometimes answer with a null content block. That used
to raise AttributeError inside the candidate loop, which surfaced as a
confusing failure instead of falling through to the next candidate.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.llm.openrouter_client import OpenRouterClient


def _response(content: str | None) -> SimpleNamespace:
    """Build a minimal chat-completion response object."""
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )


class _FakeCompletions:
    """Records the models requested and replays canned responses."""

    def __init__(self, responses: list) -> None:
        self.responses = list(responses)
        self.requested: list[str] = []

    def create(self, *, model: str, **_kwargs):
        self.requested.append(model)
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


@pytest.fixture
def client(monkeypatch) -> OpenRouterClient:
    """A client whose transport returns canned responses."""
    instance = OpenRouterClient()
    completions = _FakeCompletions([])
    instance.client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    return instance


def test_empty_completion_falls_through_to_next_candidate(client, monkeypatch) -> None:
    """A null content block must not raise — the next candidate is tried."""
    completions = _FakeCompletions([_response(None), _response("second answer")])
    client.client = SimpleNamespace(chat=SimpleNamespace(completions=completions))

    monkeypatch.setattr(
        "src.llm.openrouter_client.settings.use_omniroute", True, raising=False
    )

    answer = client.generate("hello")
    assert answer == "second answer"
    assert len(completions.requested) == 2


def test_blank_completion_is_treated_as_empty(client, monkeypatch) -> None:
    """Whitespace-only content is rejected the same way."""
    completions = _FakeCompletions([_response("   "), _response("usable")])
    client.client = SimpleNamespace(chat=SimpleNamespace(completions=completions))

    monkeypatch.setattr(
        "src.llm.openrouter_client.settings.use_omniroute", True, raising=False
    )

    assert client.generate("hello") == "usable"


def test_all_candidates_empty_returns_error_string(client, monkeypatch) -> None:
    """When every candidate is empty the caller gets a readable error."""
    completions = _FakeCompletions([_response(None)])
    client.client = SimpleNamespace(chat=SimpleNamespace(completions=completions))

    monkeypatch.setattr(
        "src.llm.openrouter_client.settings.use_omniroute", True, raising=False
    )

    answer = client.generate("hello")
    assert "Error generating response" in answer
