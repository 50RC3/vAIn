import gc
import logging
import psutil
import os

# Set up logging for the memory optimization module
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MemoryOptimizer:
    def __init__(self, threshold=90):
        """
        Initializes the memory optimizer with an optional threshold for memory usage.
        :param threshold: Memory usage percentage threshold for optimization actions.
        """
        self.threshold = threshold

    def get_memory_usage(self):
        """
        Gets the current memory usage of the system.
        :return: Memory usage percentage.
        """
        memory = psutil.virtual_memory()
        return memory.percent

    def optimize_memory(self):
        """
        Performs memory optimization tasks:
        - Collects garbage to free up unused objects.
        - Attempts to kill memory-intensive processes if necessary.
        - Optionally manages swap memory usage.
        :return: Optimization status message.
        """
        try:
            memory_usage = self.get_memory_usage()

            # Log memory usage before optimization
            logger.info(f"Memory usage before optimization: {memory_usage}%")

            # If memory usage exceeds the threshold, start optimizing
            if memory_usage > self.threshold:
                logger.warning(f"Memory usage exceeded the threshold of {self.threshold}%. Attempting optimization...")

                # Trigger garbage collection to free unused memory
                self.run_garbage_collection()

                # Try to release memory from unused processes (if needed)
                self.kill_heavy_processes()

                # Optionally manage swap memory if it’s heavily utilized
                self.free_swap_memory()

                # Log memory usage after optimization
                optimized_memory_usage = self.get_memory_usage()
                logger.info(f"Memory usage after optimization: {optimized_memory_usage}%")

                return f"Memory optimization completed. Usage reduced from {memory_usage}% to {optimized_memory_usage}%."

            else:
                return "Memory usage is below threshold, no optimization needed."

        except Exception as e:
            logger.error(f"Error during memory optimization: {e}")
            return "Error in memory optimization."

    def run_garbage_collection(self):
        """
        Forces garbage collection to clean up unused objects.
        """
        logger.info("Running garbage collection...")
        gc.collect()
        logger.info("Garbage collection completed.")

    def kill_heavy_processes(self):
        """
        Attempts to kill memory-intensive processes to free up system memory.
        """
        try:
            # Get all running processes and their memory usage
            processes = [(proc.pid, proc.info['name'], proc.info['memory_info'].rss / (1024 * 1024))  # in MB
                         for proc in psutil.process_iter(['pid', 'name', 'memory_info'])]

            # Sort processes by memory usage in descending order
            processes = sorted(processes, key=lambda proc: proc[2], reverse=True)

            # Kill processes that exceed a certain memory threshold (e.g., 500 MB)
            for pid, name, memory in processes:
                if memory > 500:  # Define your own memory threshold here
                    logger.warning(f"Terminating process {name} (PID {pid}) using {memory}MB of memory.")
                    psutil.Process(pid).terminate()

        except Exception as e:
            logger.error(f"Error killing heavy processes: {e}")

    def free_swap_memory(self):
        """
        Attempts to free swap memory if it's being heavily utilized.
        """
        try:
            swap = psutil.swap_memory()

            if swap.percent > 90:  # If swap memory usage exceeds 90%, try freeing it
                logger.warning(f"Swap memory usage is high ({swap.percent}%). Attempting to free swap memory...")
                os.system('sudo swapoff -a')  # Disable swap temporarily
                os.system('sudo swapon -a')   # Re-enable swap
                logger.info("Swap memory freed.")
            else:
                logger.info(f"Swap memory usage is under control: {swap.percent}%")

        except Exception as e:
            logger.error(f"Error managing swap memory: {e}")

