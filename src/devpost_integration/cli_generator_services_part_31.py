from src.rm_ddd.core.health import ModuleHealth

    def _extract_method_arguments(self, method: callable) -> List[Dict[str, Any]]:
        """Extract method arguments for CLI generation"""
        try:
            sig = inspect.signature(method)
            arguments = []
            for param_name, param in sig.parameters.items():
                if param_name != 'self':
                    arg_info = {'name': param_name, 'type': str(param.annotation) if param.annotation != inspect.Parameter.empty else 'str', 'default': param.default if param.default != inspect.Parameter.empty else None, 'required': param.default == inspect.Parameter.empty}
                    arguments.append(arg_info)
            return arguments
        except:
            return []

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

