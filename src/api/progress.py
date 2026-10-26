"""In-memory progress event bus for live multi-agent execution streaming.

One asyncio.Queue per run_id. The orchestrator publishes agent lifecycle
events through a plain callback; SSE route handlers subscribe and drain
the queue into a text/event-stream response.
"""

import asyncio
import time
from typing import Any, AsyncGenerator, Callable, Optional

from loguru import logger

from src.agents.display import NODE_DISPLAY

# Agent display metadata for stepper events — single source of truth in
# src/agents/display.py, shared with the orchestrator.
AGENT_META = NODE_DISPLAY

ProgressCallback = Callable[[dict], None]


class RunEventBus:
    """Per-run event queues with replay buffer and deferred cleanup."""

    def __init__(self):
        self._queues: dict[str, asyncio.Queue] = {}
        self._history: dict[str, list[dict]] = {}
        self._closed: set[str] = set()

    def create(self, run_id: str) -> None:
        self._queues[run_id] = asyncio.Queue()
        self._history[run_id] = []

    def publish(self, run_id: str, event: dict) -> None:
        if run_id not in self._queues or run_id in self._closed:
            return
        event.setdefault("ts", round(time.time(), 3))
        self._history[run_id].append(event)
        self._queues[run_id].put_nowait(event)

    def close(self, run_id: str) -> None:
        """Mark run closed; schedule queue cleanup so late events are dropped."""
        self._closed.add(run_id)
        try:
            loop = asyncio.get_running_loop()
            loop.call_later(120, self._cleanup, run_id)
        except RuntimeError:
            # No running loop (sync test context) — clean up immediately.
            self._cleanup(run_id)

    def _cleanup(self, run_id: str) -> None:
        self._queues.pop(run_id, None)
        self._history.pop(run_id, None)
        self._closed.discard(run_id)

    def history(self, run_id: str) -> list[dict]:
        return list(self._history.get(run_id, []))


# Module-level singleton shared by routes and orchestrator callbacks
event_bus = RunEventBus()


def make_progress_cb(run_id: str) -> ProgressCallback:
    """Return a plain callable the orchestrator uses to publish events."""
    def _cb(event: dict) -> None:
        try:
            event_bus.publish(run_id, event)
        except Exception as e:  # never let progress reporting break a run
            logger.debug(f"Progress publish failed for run {run_id}: {e}")
    return _cb


def format_sse(event: dict) -> str:
    """Serialize an event dict as one SSE frame."""
    import json
    etype = event.get("type", "message")
    return f"event: {etype}\ndata: {json.dumps(event)}\n\n"


async def stream_run_events(
    run_id: str,
    task: "asyncio.Task",
    result_event: str = "result",
    keepalive_seconds: float = 15.0,
) -> AsyncGenerator[str, None]:
    """Yield SSE frames for queued events until the pipeline task settles.

    Emits a terminal `result` frame with the task's return value (or an
    `error` frame on failure), then closes the run on the bus.
    """
    queue = event_bus._queues.get(run_id)
    if queue is None:
        yield format_sse({"type": "error", "message": "Unknown run"})
        return

    try:
        while True:
            if task.done() and queue.empty():
                break
            try:
                event = await asyncio.wait_for(queue.get(), timeout=keepalive_seconds)
                yield format_sse(event)
            except asyncio.TimeoutError:
                yield ": keep-alive\n\n"
                continue

        if task.cancelled():
            yield format_sse({"type": "error", "message": "Pipeline run cancelled"})
            return

        exc = task.exception()
        if exc is not None:
            logger.error(f"Streamed pipeline failed: {exc}")
            yield format_sse({"type": "error", "message": str(exc)})
            return

        result = task.result()
        if hasattr(result, "model_dump"):
            payload = result.model_dump()
        elif hasattr(result, "dict"):
            payload = result.dict()
        else:
            payload = result
        yield format_sse({"type": result_event, "data": payload})
    finally:
        event_bus.close(run_id)
