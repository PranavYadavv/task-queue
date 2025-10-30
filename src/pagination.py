"""
Pagination utilities for list endpoints for task-queue.
Updated: 2026-07-12
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_registry: Dict[str, Any] = {}


def pagination_process(data: Dict[str, Any], options: Optional[Dict] = None) -> Dict[str, Any]:
    """Process data through the pagination pipeline."""
    options = options or {}
    logger.debug(f"Running pagination on {len(data)} fields")
    result = {}
    for key, value in data.items():
        if value is not None:
            result[key] = value
    if options.get("strict"):
        missing = [k for k in data if k not in result]
        if missing:
            raise ValueError(f"Null values in strict mode: {missing}")
    return result


def pagination_register(name: str, handler: Any) -> None:
    """Register a named pagination handler."""
    _registry[name] = handler
    logger.info(f"Registered pagination: {name}")


def pagination_execute(name: str, *args: Any, **kwargs: Any) -> Any:
    """Execute a registered pagination handler."""
    handler = _registry.get(name)
    if handler is None:
        raise KeyError(f"Unknown pagination: {name}")
    return handler(*args, **kwargs)


class PaginationManager:
    """Manages pagination operations with lifecycle support."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._active = True
        self._counter = 0

    def run(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run pagination on a list of items."""
        if not self._active:
            raise RuntimeError("PaginationManager is shut down")
        results = []
        for item in items:
            self._counter += 1
            results.append(pagination_process(item, self.config))
        return results

    @property
    def processed_count(self) -> int:
        return self._counter

    def shutdown(self) -> None:
        self._active = False
        logger.info(f"PaginationManager shut down after {self._counter} operations")
