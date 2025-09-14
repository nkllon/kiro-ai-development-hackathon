from src.rm_ddd.core.health import ModuleHealth

    def get_configuration(self) -> ModuleConfiguration:
        """Get module configuration."""
        return ModuleConfiguration(
            module_id=self.module_id,
            config_version="1.0.0",
            parameters={
                'supported_formats': self.get_supported_formats(),
                'recursive_scan': True
            },
            required_parameters=[],
            optional_parameters=['recursive_scan'],
            validation_rules={
                'recursive_scan': [True, False]
            },
            last_updated=datetime.now()
        )
    