import psutil
import logging
from typing import Dict, Any
from vain.core.base import VAInComponent
from .battery_optimizer import BatteryOptimizer
from .connection_handler import ConnectionHandler

logger = logging.getLogger("ResourceMonitor")

class ResourceMonitor(VAInComponent):
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize with configuration from vAIn system.
        """
        super().__init__(config)
        self.cpu_threshold = config.get('cpu_threshold', 80)
        self.memory_threshold = config.get('memory_threshold', 85)
        self.network_threshold = config.get('network_threshold', 1000)
        self.battery_threshold = config.get('battery_threshold', 20)

        self.battery_optimizer = BatteryOptimizer(self.battery_threshold)
        self.connection_handler = ConnectionHandler(
            config.get('node_id'),
            config.get('private_key'),
            config.get('network_address')
        )

    def get_cpu_usage(self):
        """
        Get the current CPU usage percentage.
        """
        return psutil.cpu_percent(interval=1)

    def get_memory_usage(self):
        """
        Get the current memory usage percentage.
        """
        return psutil.virtual_memory().percent

    def get_network_usage(self):
        """
        Get the current network usage in KB/s.
        """
        net_io = psutil.net_io_counters()
        return (net_io.bytes_sent + net_io.bytes_recv) / 1024  # Convert to KB/s

    def get_battery_percentage(self):
        """
        Get the current battery percentage.
        """
        return self.battery_optimizer.get_battery_percentage()

    async def optimize_resources(self):
        """
        Optimize resources based on the current system usage.
        """
        cpu_usage = self.get_cpu_usage()
        memory_usage = self.get_memory_usage()
        network_usage = self.get_network_usage()
        battery_percentage = self.get_battery_percentage()

        logger.info(f"CPU Usage: {cpu_usage:.2f}% | Memory Usage: {memory_usage:.2f}% | "
                    f"Network Usage: {network_usage:.2f} KB/s | Battery: {battery_percentage}%")

        if cpu_usage > self.cpu_threshold:
            logger.warning("High CPU usage detected. Triggering CPU optimization.")
            self.reduce_cpu_intensive_tasks()

        if memory_usage > self.memory_threshold:
            logger.warning("High memory usage detected. Triggering memory optimization.")
            self.free_memory()

        if network_usage > self.network_threshold:
            logger.warning("High network usage detected. Triggering network optimization.")
            self.connection_handler.throttle_network()

        if battery_percentage < self.battery_threshold:
            logger.warning("Low battery detected. Triggering battery optimization.")
            self.battery_optimizer.optimize_battery()

    def reduce_cpu_intensive_tasks(self):
        """
        Reduce CPU-intensive operations if the CPU usage is high.
        """
        logger.info("Reducing CPU-intensive tasks.")
        # Placeholder: Logic to pause/reduce CPU-intensive tasks

    def free_memory(self):
        """
        Free memory if memory usage is high.
        """
        logger.info("Freeing memory by suspending non-essential tasks.")
        # Placeholder: Logic to suspend memory-heavy tasks

    async def start(self):
        """
        Start monitoring as part of vAIn system.
        """
        try:
            while self.is_running:
                await self.optimize_resources()
                await asyncio.sleep(self.config.get('monitor_interval', 60))
        except Exception as e:
            logger.error(f"Error in resource monitoring: {e}")
            self.handle_error(e)
