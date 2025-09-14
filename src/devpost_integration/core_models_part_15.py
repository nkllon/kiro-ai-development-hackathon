from src.rm_ddd.core.health import ModuleHealth

    def update_configuration(self, config: Dict[str, Any]) -> bool:
        """Update module configuration."""
        try:
            if 'operation_type' in config:
                self.operation_type = config['operation_type']
            return True
        except Exception as e:
            logger.error(f'Failed to update configuration: {e}')
            return False
