from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def safe_serialize(data: Any, **kwargs) -> str:
        """
        Safely serialize data with fallback handling for problematic objects.
        
        Args:
            data: The data to serialize
            **kwargs: Additional arguments passed to json.dumps
            
        Returns:
            JSON string with safe serialization
        """
        try:
            return SerializationHandler.serialize_with_enums(data, **kwargs)
        except (TypeError, ValueError) as e:
            # Fallback: convert enums to values first
            try:
                converted_data = SerializationHandler.convert_enums_to_values(data)
                # Remove cls from kwargs to avoid conflicts
                fallback_kwargs = {k: v for k, v in kwargs.items() if k != 'cls'}
                return json.dumps(converted_data, **fallback_kwargs)
            except Exception as fallback_error:
                # Last resort: use default str conversion
                final_kwargs = {k: v for k, v in kwargs.items() if k != 'cls'}
                final_kwargs['default'] = str
                return json.dumps(data, **final_kwargs)


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

