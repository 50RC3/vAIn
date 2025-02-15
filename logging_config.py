import os
import sys
import logging
import logging.config
from pathlib import Path
from python_json_logger import jsonlogger  # Fixed import statement
from dotenv import load_dotenv  # This will work after installing python-dotenv

# Load environment variables
load_dotenv()

# Create logs directory if it doesn't exist
log_dir = Path(__file__).parent / "logs"
try:
    log_dir.mkdir(exist_ok=True)
    
    # Create subdirectories for different components
    (log_dir / "ai_events").mkdir(exist_ok=True)
    (log_dir / "p2p").mkdir(exist_ok=True)
    (log_dir / "system").mkdir(exist_ok=True)
except Exception as e:
    print(f"Error creating log directories: {e}", file=sys.stderr)
    sys.exit(1)

class AIEventFormatter(jsonlogger.JsonFormatter):  # Updated class reference
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record['ai_component'] = getattr(record, 'ai_component', 'unknown')
        log_record['event_type'] = getattr(record, 'event_type', 'general')

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "ai_json": {
            "()": AIEventFormatter,
            "fmt": "%(asctime)s %(name)s %(levelname)s %(message)s %(ai_component)s %(event_type)s"
        },
        "p2p_json": {
            "()": jsonlogger.JsonFormatter,  # Updated class reference
            "fmt": "%(asctime)s %(name)s %(levelname)s %(message)s %(peer_id)s %(network_status)s"
        },
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "stream": "ext://sys.stdout"
        },
        "ai_events": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "ai_json",
            "filename": log_dir / "ai_events" / "ai_events.log",
            "maxBytes": 10485760,
            "backupCount": 5,
            "level": "DEBUG"
        },
        "p2p_events": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "p2p_json",
            "filename": log_dir / "p2p" / "p2p_events.log",
            "maxBytes": 10485760,
            "backupCount": 5,
            "level": "DEBUG"
        },
        "system_events": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "filename": log_dir / "system" / "system.log",
            "maxBytes": 10485760,
            "backupCount": 5,
            "level": "INFO"
        }
    },
    "loggers": {
        "": {
            "handlers": ["console", "system_events"],
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "propagate": True
        },
        "ai": {
            "handlers": ["ai_events"],
            "level": "DEBUG",
            "propagate": True
        },
        "p2p": {
            "handlers": ["p2p_events"],
            "level": "DEBUG",
            "propagate": True
        }
    }
}

def setup_logging():
    """Initialize logging configuration"""
    try:
        logging.config.dictConfig(LOGGING_CONFIG)
    except Exception as e:
        print(f"Error setting up logging configuration: {e}", file=sys.stderr)
        sys.exit(1)

def get_logger(name, component=None):
    """Get a logger with optional AI component specification"""
    logger = logging.getLogger(name)
    if component:
        logger = logging.LoggerAdapter(logger, {"ai_component": component})
    return logger
