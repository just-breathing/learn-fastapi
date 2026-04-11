import time
import hashlib
import json
from functools import wraps
from typing import Any


# Global cache storage shared across all instances
_GLOBAL_CACHE = {}


def _make_hashable(obj: Any) -> str:
    """Convert any object to a hashable string for cache key."""
    try:
        # Try JSON serialization for basic types
        return json.dumps(obj, default=str, sort_keys=True)
    except (TypeError, ValueError):
        # Fallback to string representation
        return str(obj)


def cache(ttl_seconds: int = 300):
    """
    Decorator for in-memory caching with TTL (time-to-live).
    Uses a global cache shared across all instances.
    
    Args:
        ttl_seconds: Time-to-live in seconds
    """
    def decorator(func):        
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            class_name = self.__class__.__name__
            key_parts = [class_name, func.__name__]
            
            # For positional arguments
            for arg in args:
                key_parts.append(_make_hashable(arg))
            
            # For keyword arguments in sorted order
            for k in sorted(kwargs.keys()):
                key_parts.append(f"{k}={_make_hashable(kwargs[k])}")
            
            # Create hash of the key for shorter representation
            key_string = "|".join(key_parts)
            cache_key = hashlib.md5(key_string.encode()).hexdigest()
            
            # Check if cache entry exists and is still valid
            if cache_key in _GLOBAL_CACHE:
                cached_value, expiry_time = _GLOBAL_CACHE[cache_key]
                if time.time() < expiry_time:
                    return cached_value
                else:
                    # Cache expired, remove it
                    del _GLOBAL_CACHE[cache_key]
            
            # Cache miss or expired, call the function
            result = func(self, *args, **kwargs)
            
            # Store result with expiry time
            _GLOBAL_CACHE[cache_key] = (result, time.time() + ttl_seconds)
            return result
        
        return wrapper
    return decorator


def clear_all_cache():
    """Clear all caches. Useful for testing."""
    global _GLOBAL_CACHE
    _GLOBAL_CACHE.clear()

