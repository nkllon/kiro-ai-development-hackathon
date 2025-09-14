from src.rm_ddd.core.health import ModuleHealth

    def get_configuration(self) -> Dict[str, Any]:
        """Get module configuration."""
        return self.config_data.copy()
