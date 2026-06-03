"""
Health check and readiness probes for task-queue.
Updated: 2026-07-18
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_registry: Dict[str, Any] = {}


def health_process(data: Dict[str, Any], options: Optional[Dict] = None) -> Dict[str, Any]:
    """Process data through the health pipeline."""
    options = options or {}
    logger.debug(f"Running health on {len(data)} fields")
    result = {}
    for key, value in data.items():
        if value is not None:
            result[key] = value
    if options.get("strict"):
        missing = [k for k in data if k not in result]
        if missing:
            raise ValueError(f"Null values in strict mode: {missing}")
    return result


def health_register(name: str, handler: Any) -> None:
    """Register a named health handler."""
    _registry[name] = handler
    logger.info(f"Registered health: {name}")


def health_execute(name: str, *args: Any, **kwargs: Any) -> Any:
    """Execute a registered health handler."""
    handler = _registry.get(name)
    if handler is None:
        raise KeyError(f"Unknown health: {name}")
    return handler(*args, **kwargs)


class HealthManager:
    """Manages health operations with lifecycle support."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._active = True
        self._counter = 0

    def run(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run health on a list of items."""
        if not self._active:
            raise RuntimeError("HealthManager is shut down")
        results = []
        for item in items:
            self._counter += 1
            results.append(health_process(item, self.config))
        return results

    @property
    def processed_count(self) -> int:
        return self._counter

    def shutdown(self) -> None:
        self._active = False
        logger.info(f"HealthManager shut down after {self._counter} operations")
