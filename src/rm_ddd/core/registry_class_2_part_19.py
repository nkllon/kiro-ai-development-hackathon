
def get_global_registry() -> GlobalRegistry:
    """
    Get the global registry instance.
    
    Returns:
        The singleton GlobalRegistry instance
    """
    global _global_registry
    with _registry_lock:
        if _global_registry is None:
            _global_registry = GlobalRegistry()
        return _global_registry
