"""
Structured logging configuration for the Schmick membership service.
Provides JSON-formatted logging with consistent structure for production use.
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs structured JSON logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        # Create the base log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add extra fields if they exist
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        if hasattr(record, 'salesforce_id'):
            log_entry["salesforce_id"] = record.salesforce_id
        if hasattr(record, 'event'):
            log_entry["event"] = record.event
        if hasattr(record, 'extra_data'):
            log_entry.update(record.extra_data)
            
        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry)


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance with structured JSON output.
    
    Args:
        name: The logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        
        # Set JSON formatter
        formatter = JSONFormatter()
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        logger.propagate = False
    
    return logger


class LoggerAdapter(logging.LoggerAdapter):
    """
    Adapter that adds consistent context to all log messages.
    Useful for adding request_id, salesforce_id, etc. to all logs in a request.
    """
    
    def __init__(self, logger: logging.Logger, extra: Dict[str, Any]):
        super().__init__(logger, extra)
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """Add extra context to log records."""
        # Merge extra data
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        kwargs['extra'].update(self.extra)
        return msg, kwargs
    
    def log_event(self, level: int, event: str, message: str, **extra_data):
        """Log an event with structured data."""
        extra = {'event': event}
        if extra_data:
            extra['extra_data'] = extra_data
        self.log(level, message, extra=extra)
    
    def info_event(self, event: str, message: str, **extra_data):
        """Log an info-level event."""
        self.log_event(logging.INFO, event, message, **extra_data)
    
    def error_event(self, event: str, message: str, **extra_data):
        """Log an error-level event."""
        self.log_event(logging.ERROR, event, message, **extra_data)
    
    def warning_event(self, event: str, message: str, **extra_data):
        """Log a warning-level event."""
        self.log_event(logging.WARNING, event, message, **extra_data)


def mask_sensitive_data(data: Dict[str, Any], sensitive_keys: set = None) -> Dict[str, Any]:
    """
    Mask sensitive data in dictionaries for safe logging.
    
    Args:
        data: Dictionary that may contain sensitive data
        sensitive_keys: Set of keys to mask (defaults to common sensitive keys)
        
    Returns:
        Dictionary with sensitive values masked
    """
    if sensitive_keys is None:
        sensitive_keys = {
            'password', 'pass', 'secret', 'key', 'token', 'auth', 
            'authorization', 'schmick_pass', 'api_key'
        }
    
    masked_data = {}
    for key, value in data.items():
        if any(sensitive_key in key.lower() for sensitive_key in sensitive_keys):
            masked_data[key] = "***MASKED***"
        elif isinstance(value, dict):
            masked_data[key] = mask_sensitive_data(value, sensitive_keys)
        else:
            masked_data[key] = value
    
    return masked_data