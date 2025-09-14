
def reset_global_registry():
    """Reset the global registry (primarily for testing)."""
    global _global_registry
    with _registry_lock:
        if _global_registry:
            pass
        _global_registry = GlobalRegistry()

@property