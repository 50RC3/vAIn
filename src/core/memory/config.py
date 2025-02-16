from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class MemoryConfig:
    max_size: int = 1024
    compression_threshold: int = 512
    cache_enabled: bool = True

class ConfigManager:
    def __init__(self):
        self.config = MemoryConfig()

    def update_from_dict(self, config_dict: Dict[str, Any]) -> None:
        for key, value in config_dict.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
