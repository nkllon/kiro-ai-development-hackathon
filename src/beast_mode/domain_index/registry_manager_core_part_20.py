
def get_cache_info(self, key: str) -> Optional[Dict[str, Any]]:
    """Get detailed cache information for a key"""
    return self._cache.get_entry_info(key)
