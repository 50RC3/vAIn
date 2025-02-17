from typing import Dict, Any, Optional
from ..base import MemoryInterface
from ..utils.optimizer import MemoryOptimizer

class EpisodicMemory(MemoryInterface):
    def __init__(self):
        self.logger = self._setup_logger()
        self.storage = {}
        self.optimizer = MemoryOptimizer()

    def store(self, data: Dict[str, Any]) -> bool:
        try:
            self._validate_memory(data)
            optimized_data = self.optimizer.optimize(data)
            return self._persist_memory(optimized_data)
        except Exception as e:
            self.logger.error(f"Storage failed: {e}")
            return False

    def retrieve(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            return self.storage.get(self._generate_key(query))
        except Exception as e:
            self.logger.error(f"Retrieval failed: {e}")
            return None

    def optimize(self) -> None:
        self.storage = {k: self.optimizer.optimize(v) for k, v in self.storage.items()}

    def _generate_key(self, query: Dict[str, Any]) -> str:
        return str(hash(frozenset(query.items())))
