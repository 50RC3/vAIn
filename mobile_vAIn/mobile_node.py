import torch
import numpy as np
from typing import Dict, Any, Optional
import logging
from dataclasses import dataclass
import psutil
import asyncio

@dataclass
class MobileDeviceMetrics:
    battery_level: float
    available_memory: int
    cpu_usage: float
    network_strength: float
    storage_available: int

class MobileNode:
    def __init__(self, device_id: str, min_battery_level: float = 0.2):
        self.device_id = device_id
        self.min_battery_level = min_battery_level
        self.local_model = None
        self.logger = logging.getLogger(__name__)
        
    async def get_device_metrics(self) -> MobileDeviceMetrics:
        """Get current device metrics"""
        return MobileDeviceMetrics(
            battery_level=self._get_battery_level(),
            available_memory=psutil.virtual_memory().available,
            cpu_usage=psutil.cpu_percent(),
            network_strength=self._get_network_strength(),
            storage_available=psutil.disk_usage('/').free
        )

    def can_participate(self, metrics: Optional[MobileDeviceMetrics] = None) -> bool:
        """Check if device can participate in federated learning"""
        if metrics is None:
            metrics = asyncio.run(self.get_device_metrics())
        
        return (metrics.battery_level > self.min_battery_level and
                metrics.available_memory > 500_000_000 and  # 500MB
                metrics.cpu_usage < 80)

    async def train_local_model(self, data: Any, epochs: int = 1) -> Dict[str, Any]:
        """Train local model with device data"""
        if not self.can_participate():
            return None
            
        try:
            metrics = await self.get_device_metrics()
            results = await self._perform_training(data, epochs)
            return {
                "device_id": self.device_id,
                "model_updates": results,
                "metrics": metrics.__dict__
            }
        except Exception as e:
            self.logger.error(f"Training failed: {str(e)}")
            return None

    def receive_global_model(self, model_weights: Dict[str, Any]):
        """Update local model with global weights"""
        try:
            self.local_model.load_state_dict(model_weights)
            return True
        except Exception as e:
            self.logger.error(f"Failed to update local model: {str(e)}")
            return False

    def _get_battery_level(self) -> float:
        """Get device battery level - implement platform specific logic"""
        return 1.0  # Mock implementation

    def _get_network_strength(self) -> float:
        """Get network signal strength - implement platform specific logic"""
        return 1.0  # Mock implementation

    async def _perform_training(self, data: Any, epochs: int) -> Dict[str, Any]:
        """Perform actual model training - implement specific training logic"""
        pass  # Implement actual training logic
