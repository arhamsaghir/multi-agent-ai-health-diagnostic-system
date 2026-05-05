"""Logging middleware for request/response tracking."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from loguru import logger
import time
import uuid


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every request with timing and unique ID."""

    async def dispatch(self, request: Request, call_next):
        """Process and log a single HTTP request.

        Assigns a unique request ID, logs method/path/timing,
        and injects X-Request-ID header into the response.

        Args:
            request: Incoming Starlette HTTP request.
            call_next: Next middleware/handler in the chain.

        Returns:
            HTTP response with X-Request-ID header added.
        """
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()

        logger.info(f"[{request_id}] {request.method} {request.url.path}")

        response = await call_next(request)

        duration = time.time() - start_time
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} "
            f"— {response.status_code} — {duration:.3f}s"
        )

        response.headers["X-Request-ID"] = request_id
        return response
