"""
Retry logic with backoff strategies for task-queue.
Updated: 2026-07-18
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_registry: Dict[str, Any] = {}


def retry_process(data: Dict[str, Any], options: Optional[Dict] = None) -> Dict[str, Any]:
    """Process data through the retry pipeline."""
    options = options or {}
    logger.debug(f"Running retry on {len(data)} fields")
    result = {}
    for key, value in data.items():
        if value is not None:
            result[key] = value
    if options.get("strict"):
        missing = [k for k in data if k not in result]
        if missing:
            raise ValueError(f"Null values in strict mode: {missing}")
    return result


def retry_register(name: str, handler: Any) -> None:
    """Register a named retry handler."""
    _registry[name] = handler
    logger.info(f"Registered retry: {name}")


def retry_execute(name: str, *args: Any, **kwargs: Any) -> Any:
    """Execute a registered retry handler."""
    handler = _registry.get(name)
    if handler is None:
        raise KeyError(f"Unknown retry: {name}")
    return handler(*args, **kwargs)


class RetryManager:
    """Manages retry operations with lifecycle support."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._active = True
        self._counter = 0

    def run(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run retry on a list of items."""
        if not self._active:
            raise RuntimeError("RetryManager is shut down")
        results = []
        for item in items:
            self._counter += 1
            results.append(retry_process(item, self.config))
        return results

    @property
    def processed_count(self) -> int:
        return self._counter

    def shutdown(self) -> None:
        self._active = False
        logger.info(f"RetryManager shut down after {self._counter} operations")
