from src.rm_ddd.core.registry import register_module

def _get_cache_key(self, url: str, params: Optional[Dict[str, Any]]) -> str:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Generate cache key for request."""
    key_parts = [url]
    if params:
        sorted_params = sorted(params.items())
        key_parts.append(str(sorted_params))
    return '|'.join(key_parts)
