import time
from threading import Lock

_store = {}
_lock = Lock()


def cached(key: str, ttl_seconds: int, fetch_fn):
    """Return cached result if not expired, otherwise call fetch_fn and cache it."""
    now = time.time()
    with _lock:
        if key in _store:
            val, expires = _store[key]
            if now < expires:
                return val
        # Evict expired entries to prevent unbounded memory growth
        expired = [k for k, (_, exp) in _store.items() if now >= exp]
        for k in expired:
            del _store[k]

    try:
        result = fetch_fn()
    except Exception as e:
        print(f"[cache] fetch_fn failed for key '{key}': {e}")
        raise

    with _lock:
        _store[key] = (result, now + ttl_seconds)
    return result


def invalidate(prefix: str = None):
    """Clear cache entries. If prefix is given, only clear keys starting with it."""
    with _lock:
        if prefix is None:
            _store.clear()
        else:
            for k in list(_store):
                if k.startswith(prefix):
                    del _store[k]
