"""Simple retry utilities for Lab_3."""
import time
from functools import wraps


def retry(attempts=3, delay=1):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            last_exc = None
            for _ in range(attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    time.sleep(delay)
            raise last_exc

        return wrapper

    return decorator
