from src.rm_ddd.core.health import ModuleHealth

    def _is_cache_valid(self) -> bool:
        """Check if cached metrics are still valid"""
        if not self.cached_metrics or not self.last_update:
            return False
        return datetime.now() - self.last_update < self.cache_duration
