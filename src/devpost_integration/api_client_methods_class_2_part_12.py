from src.rm_ddd.core.health import ModuleHealth

    def update_configuration(self, config: ModuleConfiguration) -> bool:
        """Update module configuration"""
        try:
            if hasattr(config, 'api_key'):
                self.api_key = config.api_key
            if hasattr(config, 'base_url'):
                self.base_url = config.base_url
            return True
        except Exception as e:
            logger.error(f"Configuration update failed: {e}")
            return False
    