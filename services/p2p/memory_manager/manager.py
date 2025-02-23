import logging
from typing import Any, Dict, Optional
from ....core.memory.memory_controller import MemoryController
from ....core.memory.memory_storage import MemoryStorage

class MemoryManager:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.logger = logging.getLogger(__name__)
        self.memory_controller = MemoryController()
        self.memory_storage = MemoryStorage()

    def store(self, key: str, value: Any) -> bool:
        """
        Store a value in memory using the core memory system
        """
        try:
            # Store in short-term memory by default
            memory_id = self.memory_storage.store_data(
                memory_type="short_term",
                data={key: value},
                metadata={"node_id": self.node_id}
            )
            self.logger.info(f"Stored value for key: {key}")
            return True if memory_id else False
        except Exception as e:
            self.logger.error(f"Error storing value: {e}")
            return False

    def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from memory using the core memory system
        """
        try:
            # Try to retrieve from all memory types
            for memory_type in ["short_term", "long_term"]:
                entries = self.memory_storage.get_all_memory_entries(memory_type)
                for entry in entries:
                    if key in entry.get("data", {}):
                        return entry["data"][key]
            
            self.logger.warning(f"No value found for key: {key}")
            return None
        except Exception as e:
            self.logger.error(f"Error retrieving value: {e}")
            return None
