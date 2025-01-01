import psutil
import logging
from battery_optimizer import BatteryOptimizer
from connection_handler import ConnectionHandler

logger = logging.getLogger("ResourceMonitor")

class ResourceMonitor:
    def __init__(self, cpu_threshold, memory_threshold, network_threshold, battery_threshold):
        """
        Initialize the resource monitor with specified thresholds.
        
        :param cpu_threshold: CPU usage percentage above which optimizations will be triggered.
        :param memory_threshold: Memory usage percentage above which optimizations will be triggered.
        :param network_threshold: Network usage in KB/s above which optimizations will be triggered.
        :param battery_threshold: Battery percentage below which optimizations will be triggered.
        """
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.network_threshold = network_threshold
        self.battery_threshold = battery_threshold

        self.battery_optimizer = BatteryOptimizer(battery_threshold)
        self.connection_handler = ConnectionHandler(network_threshold)

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

    def optimize_resources(self):
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
