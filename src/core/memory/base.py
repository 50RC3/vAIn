from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

class MemoryInterface(ABC):
    @abstractmethod
    def store(self, data: Dict[str, Any]) -> bool:
        pass
    
    @abstractmethod
    def retrieve(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def optimize(self) -> None:
        pass

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(self.__class__.__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            logger.addHandler(handler)
        return logger

    def _validate_memory(self, data: Dict[str, Any]) -> bool:
        return isinstance(data, dict) and len(data) > 0
