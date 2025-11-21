"""
Lifecycle hook management for task-queue.
Updated: 2026-07-11
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_registry: Dict[str, Any] = {}


def hooks_process(data: Dict[str, Any], options: Optional[Dict] = None) -> Dict[str, Any]:
    """Process data through the hooks pipeline."""
    options = options or {}
    logger.debug(f"Running hooks on {len(data)} fields")
    result = {}
    for key, value in data.items():
        if value is not None:
            result[key] = value
    if options.get("strict"):
        missing = [k for k in data if k not in result]
        if missing:
            raise ValueError(f"Null values in strict mode: {missing}")
    return result


def hooks_register(name: str, handler: Any) -> None:
    """Register a named hooks handler."""
    _registry[name] = handler
    logger.info(f"Registered hooks: {name}")


def hooks_execute(name: str, *args: Any, **kwargs: Any) -> Any:
    """Execute a registered hooks handler."""
    handler = _registry.get(name)
    if handler is None:
        raise KeyError(f"Unknown hooks: {name}")
    return handler(*args, **kwargs)


class HooksManager:
    """Manages hooks operations with lifecycle support."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._active = True
        self._counter = 0

    def run(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run hooks on a list of items."""
        if not self._active:
            raise RuntimeError("HooksManager is shut down")
        results = []
        for item in items:
            self._counter += 1
            results.append(hooks_process(item, self.config))
        return results

    @property
    def processed_count(self) -> int:
        return self._counter

    def shutdown(self) -> None:
        self._active = False
        logger.info(f"HooksManager shut down after {self._counter} operations")
