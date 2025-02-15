
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

def setup_logger(name: str) -> logging.Logger:
    """
    Set up a logger with both file and console handlers.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create logs directory if it doesn't exist
    log_dir = Path("/C:/Users/Mr.V/Desktop/vAIn/logs")
    log_dir.mkdir(exist_ok=True)

    # Format for logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # File handler (rotating log files)
    file_handler = RotatingFileHandler(
        log_dir / "vain.log",
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

def log_error(logger: logging.Logger, error: Exception, context: str = ""):
    """Helper function for error logging"""
    logger.error(f"{context} Error: {str(error)}", exc_info=True)
