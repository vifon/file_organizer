def cached_property(function):
    from functools import lru_cache
    return property(lru_cache(maxsize=1)(function))
