import psutil
import logging
import time
from datetime import datetime

# Set up logging for the memory monitor module
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MemoryMonitor:
    def __init__(self, threshold=80, check_interval=60):
        """
        Initializes the memory monitor with an optional memory usage threshold.
        :param threshold: The memory usage percentage threshold for alerting (default 80%).
        :param check_interval: The time interval (in seconds) for checking memory usage (default 60 seconds).
        """
        self.threshold = threshold
        self.check_interval = check_interval

    def get_memory_usage(self):
        """
        Gets the current memory usage of the system.
        :return: Memory usage percentage.
        """
        memory = psutil.virtual_memory()
        return memory.percent

    def monitor(self):
        """
        Monitors the health and performance of the memory systems.
        Logs memory usage and triggers alerts if the usage exceeds the threshold.
        :return: Memory health status message.
        """
        try:
            # Get current memory usage
            memory_usage = self.get_memory_usage()

            # Log current memory usage
            logger.info(f"Current memory usage: {memory_usage}%")

            # Check if memory usage exceeds threshold and log an alert if it does
            if memory_usage > self.threshold:
                logger.warning(f"Memory usage has exceeded the threshold of {self.threshold}%!")
                health_status = f"High memory usage detected: {memory_usage}%"
            else:
                health_status = f"Memory usage is under control: {memory_usage}%"

            # Return health status
            return health_status

        except Exception as e:
            logger.error(f"Error monitoring memory health: {e}")
            return "Error in memory health monitoring."

    def log_memory_usage(self):
        """
        Logs the memory usage to a log file for historical tracking.
        """
        try:
            memory_usage = self.get_memory_usage()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"Memory usage at {timestamp}: {memory_usage}%")
        except Exception as e:
            logger.error(f"Error logging memory usage: {e}")
    
    def track_memory_usage(self):
        """
        Continuously track memory usage at the specified interval.
        Logs memory usage periodically and checks the health status.
        """
        try:
            logger.info("Starting memory tracking...")
            while True:
                self.log_memory_usage()
                health_status = self.monitor()
                logger.info(health_status)
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            logger.info("Memory monitoring stopped by user.")
        except Exception as e:
            logger.error(f"Error in tracking memory usage: {e}")

    def set_threshold(self, new_threshold):
        """
        Dynamically change the memory usage threshold.
        :param new_threshold: New threshold value to be set (0-100).
        """
        if 0 <= new_threshold <= 100:
            self.threshold = new_threshold
            logger.info(f"Memory usage threshold set to {new_threshold}%.")
        else:
            logger.warning("Invalid threshold value. Please provide a value between 0 and 100.")

    def change_check_interval(self, new_interval):
        """
        Dynamically change the memory check interval.
        :param new_interval: Time interval (in seconds) between checks.
        """
        if new_interval > 0:
            self.check_interval = new_interval
            logger.info(f"Memory check interval set to {new_interval} seconds.")
        else:
            logger.warning("Invalid check interval. Please provide a positive value.")
