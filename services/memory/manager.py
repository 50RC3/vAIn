"""Memory management service for model storage."""

class MemoryManager:
    """Manages model weights and training data storage."""
    
    def __init__(self):
        self.storage = {}
        
    async def store(self, key: str, data: bytes):
        """Store data in memory."""
        self.storage[key] = data
