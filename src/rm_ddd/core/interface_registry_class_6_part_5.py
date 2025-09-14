from src.rm_ddd.core.health import ModuleHealth

    def _extract_interface_info(cls):
        """Extract interface information from class"""
        interface_info = {
            'class_name': cls.__name__,
            'methods': [],
            'properties': [],
            'inheritance': [base.__name__ for base in cls.__bases__]
        }
        
        # Extract methods
        for name, method in cls.__dict__.items():
            if callable(method) and not name.startswith('_'):
                interface_info['methods'].append({
                    'name': name,
                    'signature': str(method.__annotations__) if hasattr(method, '__annotations__') else None
                })
        
        # Extract properties
        for name, prop in cls.__dict__.items():
            if isinstance(prop, property):
                interface_info['properties'].append(name)
        
        return interface_info

    