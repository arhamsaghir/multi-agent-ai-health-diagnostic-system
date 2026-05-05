"""Base agent class that all specialist agents inherit from."""

from abc import ABC, abstractmethod
from typing import Any
from loguru import logger


class BaseAgent(ABC):
    """Abstract base class for all agents in the system."""

    name: str = "base_agent"
    description: str = ""

    def __init__(self):
        self._loaded = False
        self._load_error = None

    @abstractmethod
    async def run(self, input_data: Any) -> dict:
        """Execute the agent's primary function.

        Args:
            input_data: Input data specific to the agent type.

        Returns:
            Dictionary containing the agent's output and metadata.
        """
        pass

    def get_status(self) -> dict:
        """Return agent status information."""
        return {
            "name": self.name,
            "description": self.description,
            "status": "active" if self._loaded else "unloaded",
            "load_error": self._load_error,
        }

    def log(self, level: str, message: str):
        """Log a message with agent name prefix."""
        getattr(logger, level)(f"[{self.name}] {message}")
