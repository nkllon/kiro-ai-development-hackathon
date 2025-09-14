
    def get_healthy_modules(self) -> List[RegisteredModule]:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Get all modules that are currently healthy."""
        with self._lock:
            return [module for module in self._modules.values() if module.is_healthy]
