"""
Retry utilities for handling transient API failures.
"""
import time
import logging
from functools import wraps
from typing import Callable, TypeVar, Any

logger = logging.getLogger(__name__)

T = TypeVar('T')


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator to retry a function with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds before first retry
        backoff_factor: Multiplier for delay on each retry
        exceptions: Tuple of exception types to catch and retry
    
    Returns:
        Decorated function that retries on failure
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries - 1:
                        # Last attempt failed, raise the exception
                        logger.error(
                            f"{func.__name__} failed after {max_retries} attempts: {e}"
                        )
                        raise
                    
                    # Log warning and retry
                    logger.warning(
                        f"{func.__name__} attempt {attempt + 1}/{max_retries} failed: {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    time.sleep(delay)
                    delay *= backoff_factor
            
            # Should never reach here, but just in case
            if last_exception:
                raise last_exception
            raise RuntimeError("Retry logic error")
        
        return wrapper
    return decorator
