from src.rm_ddd.core.health import ModuleHealth

    def _analyze_methods(self, module: ReflectiveModule) -> List[Dict[str, Any]]:
        """Analyze module methods for CLI generation"""
        methods = []
        try:
            for method_name in dir(module):
                if not method_name.startswith('_'):
                    method = getattr(module, method_name)
                    if callable(method) and (not isinstance(method, property)):
                        method_info = {'name': method_name, 'description': self._extract_method_docstring(method), 'arguments': self._extract_method_arguments(method), 'return_type': self._extract_method_return_type(method)}
                        methods.append(method_info)
        except Exception as e:
            pass
        return methods

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

