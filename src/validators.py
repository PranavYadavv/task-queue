"""
Input validation utilities for task-queue.
Updated: 2026-07-18
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_registry: Dict[str, Any] = {}


def validators_process(data: Dict[str, Any], options: Optional[Dict] = None) -> Dict[str, Any]:
    """Process data through the validators pipeline."""
    options = options or {}
    logger.debug(f"Running validators on {len(data)} fields")
    result = {}
    for key, value in data.items():
        if value is not None:
            result[key] = value
    if options.get("strict"):
        missing = [k for k in data if k not in result]
        if missing:
            raise ValueError(f"Null values in strict mode: {missing}")
    return result


def validators_register(name: str, handler: Any) -> None:
    """Register a named validators handler."""
    _registry[name] = handler
    logger.info(f"Registered validators: {name}")


def validators_execute(name: str, *args: Any, **kwargs: Any) -> Any:
    """Execute a registered validators handler."""
    handler = _registry.get(name)
    if handler is None:
        raise KeyError(f"Unknown validators: {name}")
    return handler(*args, **kwargs)


class ValidatorsManager:
    """Manages validators operations with lifecycle support."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._active = True
        self._counter = 0

    def run(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run validators on a list of items."""
        if not self._active:
            raise RuntimeError("ValidatorsManager is shut down")
        results = []
        for item in items:
            self._counter += 1
            results.append(validators_process(item, self.config))
        return results

    @property
    def processed_count(self) -> int:
        return self._counter

    def shutdown(self) -> None:
        self._active = False
        logger.info(f"ValidatorsManager shut down after {self._counter} operations")
