from src.rm_ddd.core.registry import register_module

def to_json(self) -> str:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Convert message to JSON string."""
    return self.json()

@classmethod