from src.rm_ddd.core.registry import register_module

def analyzer_name(self) -> str:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Get analyzer name."""
    return 'contrast_analyzer'

@property