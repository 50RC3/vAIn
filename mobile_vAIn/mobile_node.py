"""
Mobile node implementation for vAIn platform.

This module provides functionality for mobile device integration with the vAIn
platform, including device metrics collection, model updates, and resource monitoring.
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Dict, Optional

try:
    import psutil
    import wmi
    import pythoncom
except ImportError as e:
    raise ImportError(
        "Required packages not found. Please run: "
        "pip install psutil wmi pythoncom"
    ) from e

@dataclass
class DeviceMetrics:
    """
    Data class for storing device performance metrics.
    
    Attributes:
        cpu_usage: CPU utilization percentage
        memory_usage: Memory usage in percentage
        battery_level: Battery level percentage if available
        temperature: Device temperature in Celsius if available
    """
    cpu_usage: float
    memory_usage: float
    battery_level: Optional[float] = None
    temperature: Optional[float] = None

class MobileNode:
    """
    Represents a mobile device node in the vAIn network.
    
    Handles device monitoring, resource management, and communication
    with the main vAIn network for distributed learning tasks.
    """
    
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.logger = logging.getLogger(__name__)
        self._wmi = None
        self._setup_monitoring()

    def _setup_monitoring(self) -> None:
        """Initialize system monitoring components."""
        try:
            pythoncom.CoInitialize()
            self._wmi = wmi.WMI()
            self.logger.info("Device monitoring initialized for %s", self.device_id)
        except Exception as exc:
            self.logger.error("Failed to initialize monitoring: %s", str(exc))
            raise RuntimeError("Device monitoring setup failed") from exc

    async def collect_metrics(self) -> DeviceMetrics:
        """Collect current device performance metrics."""
        try:
            metrics = DeviceMetrics(
                cpu_usage=psutil.cpu_percent(),
                memory_usage=psutil.virtual_memory().percent
            )
            self.logger.debug("Metrics collected for %s", self.device_id)
            return metrics
        except Exception as exc:
            self.logger.error("Failed to collect metrics: %s", str(exc))
            raise RuntimeError("Metrics collection failed") from exc

    async def update_status(self) -> Dict[str, float]:
        """Update and return current device status."""
        metrics = await self.collect_metrics()
        return {
            "cpu_usage": metrics.cpu_usage,
            "memory_usage": metrics.memory_usage,
            "battery_level": metrics.battery_level or 0.0,
            "temperature": metrics.temperature or 0.0
        }

    def cleanup(self) -> None:
        """Release system resources."""
        if self._wmi:
            pythoncom.CoUninitialize()
