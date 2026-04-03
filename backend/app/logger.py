"""
Logging configuration and utilities
تنظیمات ثبت فعالیت‌ها
"""

import logging
import json
from logging.handlers import RotatingFileHandler
from datetime import datetime
from app.config import settings
import os

def setup_logging():
    """Configure logging with file and console handlers"""
    
    # Create logs directory if not exists
    os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


# Initialize logger
logger = setup_logging()

def log_detection(plate_number: str, confidence: float, plate_type: str, 
                  processing_time: float, status: str = "success"):
    """Log plate detection event"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": "plate_detected",
        "plate_number": plate_number,
        "confidence": confidence,
        "plate_type": plate_type,
        "processing_time_ms": processing_time * 1000,
        "status": status
    }
    logger.info(json.dumps(log_entry))


def log_error(error_type: str, error_message: str, context: dict = None):
    """Log error event"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": "error",
        "error_type": error_type,
        "error_message": error_message,
        "context": context or {}
    }
    logger.error(json.dumps(log_entry))


def log_api_request(method: str, path: str, status_code: int, 
                   response_time: float):
    """Log API request"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": "api_request",
        "method": method,
        "path": path,
        "status_code": status_code,
        "response_time_ms": response_time * 1000
    }
    logger.info(json.dumps(log_entry))