"""
Utility functions for the Schmick membership service.
Includes environment loading, data formatting, retry logic, and storage state helpers.
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union
from functools import wraps

from dotenv import load_dotenv


class RetryableError(Exception):
    """Base class for errors that should trigger retries."""
    pass


class NonRetryableError(Exception):
    """Base class for errors that should NOT trigger retries."""
    pass


def load_env() -> Dict[str, str]:
    """
    Load environment variables from .env file and return configuration.
    
    Returns:
        Dictionary of configuration values with appropriate defaults
    """
    load_dotenv()
    
    config = {
        'PLAYWRIGHT_API_KEY': os.getenv('PLAYWRIGHT_API_KEY', ''),
        'SCHMICK_USER': os.getenv('SCHMICK_USER', ''),
        'SCHMICK_PASS': os.getenv('SCHMICK_PASS', ''),
        'HEADLESS': os.getenv('HEADLESS', 'true').lower() == 'true',
        'PORT': int(os.getenv('PORT', '8000')),
        'STORAGE_STATE_FILE': os.getenv('STORAGE_STATE_FILE', 'state.json'),
        'MAX_CONCURRENCY': int(os.getenv('MAX_CONCURRENCY', '2')),
        'TIMEOUT_MS': int(os.getenv('TIMEOUT_MS', '30000')),
    }
    
    return config


def validate_required_env() -> None:
    """
    Validate that all required environment variables are set.
    
    Raises:
        ValueError: If required environment variables are missing
    """
    config = load_env()
    required_vars = ['PLAYWRIGHT_API_KEY', 'SCHMICK_USER', 'SCHMICK_PASS']
    
    missing_vars = [var for var in required_vars if not config[var]]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")


def format_membership_number(raw_membership: str) -> str:
    """
    Format and sanitize the membership number extracted from the web page.
    
    Args:
        raw_membership: Raw membership string from the web page
        
    Returns:
        Cleaned and formatted membership number
    """
    if not raw_membership:
        return ""
    
    # Remove common prefixes, whitespace, and normalize
    membership = raw_membership.strip()
    
    # Remove common prefixes like "Membership Number:", "ID:", etc.
    prefixes_to_remove = [
        "membership number:", "membership:", "number:", "id:", 
        "member id:", "confirmation:", "reference:"
    ]
    
    for prefix in prefixes_to_remove:
        if membership.lower().startswith(prefix):
            membership = membership[len(prefix):].strip()
    
    # Remove any remaining colons or dashes at the start
    membership = membership.lstrip(":-").strip()
    
    return membership


def sanitize_record_data(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize record data for safe logging (remove/mask sensitive fields).
    
    Args:
        record: The record data dictionary
        
    Returns:
        Sanitized dictionary safe for logging
    """
    safe_record = record.copy()
    
    # Remove or mask potentially sensitive fields
    sensitive_fields = ['ssn', 'social_security', 'credit_card', 'password']
    
    for field in sensitive_fields:
        if field in safe_record:
            safe_record[field] = "***MASKED***"
    
    # Partially mask email for privacy
    if 'email' in safe_record and safe_record['email']:
        email = safe_record['email']
        if '@' in email:
            local, domain = email.split('@', 1)
            if len(local) > 2:
                safe_record['email'] = f"{local[:2]}***@{domain}"
    
    return safe_record


async def retry_async(
    func, 
    max_retries: int = 3, 
    base_delay: float = 1.0, 
    backoff_factor: float = 2.0,
    retryable_exceptions: tuple = (RetryableError,)
):
    """
    Retry an async function with exponential backoff.
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        backoff_factor: Factor to multiply delay by on each retry
        retryable_exceptions: Tuple of exception types that should trigger retries
        
    Returns:
        Result of successful function execution
        
    Raises:
        The last exception if all retries fail
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):  # +1 for initial attempt
        try:
            return await func()
        except retryable_exceptions as e:
            last_exception = e
            if attempt >= max_retries:
                break
            
            delay = base_delay * (backoff_factor ** attempt)
            await asyncio.sleep(delay)
        except Exception as e:
            # Non-retryable exceptions are raised immediately
            raise e
    
    # If we get here, all retries failed
    raise last_exception


class StorageStateManager:
    """Manager for Playwright storage state persistence."""
    
    def __init__(self, storage_file: str = "state.json"):
        self.storage_file = Path(storage_file)
    
    def exists(self) -> bool:
        """Check if storage state file exists."""
        return self.storage_file.exists()
    
    def load(self) -> Optional[Dict[str, Any]]:
        """
        Load storage state from file.
        
        Returns:
            Storage state dictionary or None if file doesn't exist/invalid
        """
        if not self.exists():
            return None
        
        try:
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    async def save(self, storage_state: Dict[str, Any]) -> bool:
        """
        Save storage state to file.
        
        Args:
            storage_state: Storage state dictionary from Playwright context
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Ensure directory exists
            self.storage_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.storage_file, 'w') as f:
                json.dump(storage_state, f, indent=2)
            return True
        except IOError:
            return False
    
    def delete(self) -> bool:
        """
        Delete storage state file.
        
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if self.exists():
                self.storage_file.unlink()
            return True
        except IOError:
            return False


def create_request_context(**kwargs) -> Dict[str, Any]:
    """
    Create a context dictionary for request tracking.
    
    Args:
        **kwargs: Additional context fields
        
    Returns:
        Context dictionary with request_id and other fields
    """
    import uuid
    
    context = {
        'request_id': str(uuid.uuid4()),
        **kwargs
    }
    
    return context