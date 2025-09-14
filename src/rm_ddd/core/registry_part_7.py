from src.rm_ddd.core.health import ModuleHealth

    def uptime(self) -> timedelta:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Calculate module uptime since registration."""
        return datetime.now() - self.registration_time
