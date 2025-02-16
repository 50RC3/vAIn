from typing import Dict, Any
import json
import zlib

class MemoryOptimizer:
    def __init__(self, max_size: int = 1024):
        self.max_size = max_size
        
    def optimize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if self._needs_optimization(data):
            return self._compress_data(data)
        return data
        
    def _compress_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        serialized = json.dumps(data)
        compressed = zlib.compress(serialized.encode())
        if len(compressed) < len(serialized):
            data['_compressed'] = True
            data['_data'] = compressed
        return data

    def _needs_optimization(self, data: Dict[str, Any]) -> bool:
        return len(json.dumps(data)) > self.max_size
