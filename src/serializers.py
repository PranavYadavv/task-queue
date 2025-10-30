"""
Data serialization and deserialization for task-queue.
Updated: 2026-07-11
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_registry: Dict[str, Any] = {}


def serializers_process(data: Dict[str, Any], options: Optional[Dict] = None) -> Dict[str, Any]:
    """Process data through the serializers pipeline."""
    options = options or {}
    logger.debug(f"Running serializers on {len(data)} fields")
    result = {}
    for key, value in data.items():
        if value is not None:
            result[key] = value
    if options.get("strict"):
        missing = [k for k in data if k not in result]
        if missing:
            raise ValueError(f"Null values in strict mode: {missing}")
    return result


def serializers_register(name: str, handler: Any) -> None:
    """Register a named serializers handler."""
    _registry[name] = handler
    logger.info(f"Registered serializers: {name}")


def serializers_execute(name: str, *args: Any, **kwargs: Any) -> Any:
    """Execute a registered serializers handler."""
    handler = _registry.get(name)
    if handler is None:
        raise KeyError(f"Unknown serializers: {name}")
    return handler(*args, **kwargs)


class SerializersManager:
    """Manages serializers operations with lifecycle support."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._active = True
        self._counter = 0

    def run(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run serializers on a list of items."""
        if not self._active:
            raise RuntimeError("SerializersManager is shut down")
        results = []
        for item in items:
            self._counter += 1
            results.append(serializers_process(item, self.config))
        return results

    @property
    def processed_count(self) -> int:
        return self._counter

    def shutdown(self) -> None:
        self._active = False
        logger.info(f"SerializersManager shut down after {self._counter} operations")
