from src.rm_ddd.core.health import ModuleHealth

    def validate_data(self, data: Dict[str, Any], rules: Dict[str, Any]) -> bool:
        """Validate data against rules."""
        try:
            self.clear_errors()
            self.clear_warnings()
            
            # Basic validation logic
            for field, rule in rules.items():
                if field not in data:
                    self.add_error(f"Missing required field: {field}", field)
                elif rule.get("required") and not data[field]:
                    self.add_error(f"Required field is empty: {field}", field)
            
            self.is_valid = len(self.errors) == 0
            self._operation_count += 1
            return self.is_valid
        except Exception as e:
            logger.error(f"Data validation failed: {e}")
            self._errors += 1
            return False

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

    