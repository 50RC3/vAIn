import psutil
import logging
from datetime import datetime, timedelta

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BatteryOptimizer")

class BatteryOptimizer:
    def __init__(self, critical_level: int = 20, low_power_level: int = 50):
        """
        Initialize the Battery Optimizer.

        :param critical_level: Battery percentage below which critical optimization occurs.
        :param low_power_level: Battery percentage below which low-power optimizations are activated.
        """
        self.critical_level = critical_level
        self.low_power_level = low_power_level
        self.last_optimization = datetime.now()

    def get_battery_status(self) -> dict:
        """
        Retrieve current battery status.

        :return: A dictionary containing battery percentage, charging status, and remaining time.
        """
        battery = psutil.sensors_battery()
        if battery is None:
            logger.warning("Battery information is unavailable.")
            return {"percentage": None, "charging": None, "time_left": None}

        return {
            "percentage": battery.percent,
            "charging": battery.power_plugged,
            "time_left": battery.secsleft // 60 if battery.secsleft != -1 else None,
        }

    def optimize(self):
        """
        Optimize node tasks based on the current battery level.
        """
        status = self.get_battery_status()
        if status["percentage"] is None:
            return

        percentage = status["percentage"]
        charging = status["charging"]
        now = datetime.now()

        if percentage <= self.critical_level and not charging:
            logger.warning("Critical battery level! Activating emergency optimizations.")
            self.emergency_mode()

        elif percentage <= self.low_power_level and not charging:
            logger.info("Low battery detected. Activating low-power optimizations.")
            if now - self.last_optimization > timedelta(minutes=5):
                self.low_power_mode()
                self.last_optimization = now
        elif charging:
            logger.info("Device is charging. Full performance mode activated.")
            self.full_performance_mode()

    def emergency_mode(self):
        """
        Activate emergency power-saving measures.
        """
        logger.info("Switching to emergency mode:")
        logger.info("- Disabling non-critical background tasks.")
        logger.info("- Suspending large AI computations.")
        logger.info("- Suspending synchronization tasks.")
        # Add functionality to pause/suspend tasks
        self.suspend_sync()
        self.reduce_computation()

    def low_power_mode(self):
        """
        Activate low-power optimizations.
        """
        logger.info("Applying low-power optimizations:")
        logger.info("- Reducing data synchronization frequency.")
        logger.info("- Switching AI tasks to energy-efficient mode.")
        # Add functionality to optimize performance
        self.reduce_sync_frequency()
        self.adjust_computation_mode("low")

    def full_performance_mode(self):
        """
        Activate full performance when charging or battery is sufficient.
        """
        logger.info("Restoring full performance:")
        logger.info("- Resuming all tasks.")
        logger.info("- Restoring normal computation settings.")
        # Add functionality to resume tasks
        self.resume_sync()
        self.adjust_computation_mode("high")

    def suspend_sync(self):
        """Pause synchronization tasks."""
        logger.info("Synchronization tasks suspended.")

    def resume_sync(self):
        """Resume synchronization tasks."""
        logger.info("Synchronization tasks resumed.")

    def reduce_sync_frequency(self):
        """Adjust synchronization frequency for low-power mode."""
        logger.info("Synchronization frequency reduced.")

    def reduce_computation(self):
        """Reduce computation intensity."""
        logger.info("Computation intensity reduced to conserve energy.")

    def adjust_computation_mode(self, mode: str):
        """
        Adjust the AI computation mode.

        :param mode: Mode of operation ('low' or 'high').
        """
        logger.info(f"Computation mode adjusted to '{mode}'.")

# Example usage
if __name__ == "__main__":
    optimizer = BatteryOptimizer(critical_level=15, low_power_level=40)
    while True:
        optimizer.optimize()
