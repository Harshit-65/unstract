import importlib
import logging
from typing import Dict, Type

from unstract.connectors.queues.allowed_modules import is_allowed_module
from unstract.connectors.queues.base import QueueBase

logger = logging.getLogger(__name__)


class QueueRegister:
    """Register for queue implementations."""

    _registry: Dict[str, Type[QueueBase]] = {}

    @classmethod
    def register(cls, name: str, queue_class: Type[QueueBase]) -> None:
        """Register a queue implementation."""
        cls._registry[name] = queue_class

    @classmethod
    def get(cls, name: str) -> Type[QueueBase]:
        """Get a queue implementation."""
        if name not in cls._registry:
            # Validate module name against whitelist before importing
            module_name = f"unstract.connectors.queues.{name}"
            if not is_allowed_module(module_name):
                raise ValueError(f"Module {module_name} is not in the allowed modules list")
            
            try:
                module = importlib.import_module(module_name)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, QueueBase)
                        and attr is not QueueBase
                    ):
                        cls.register(name, attr)
                        break
            except (ImportError, AttributeError) as e:
                logger.error(f"Failed to import queue implementation {name}: {e}")
                raise ValueError(f"Queue implementation {name} not found") from e

        return cls._registry[name]
