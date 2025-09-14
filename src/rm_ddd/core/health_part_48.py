
def is_unavailable(self) -> bool:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Check if module is unavailable."""
    return self.status in [ModuleStatus.UNAVAILABLE, ModuleStatus.SHUTTING_DOWN]
