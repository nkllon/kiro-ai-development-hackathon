from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def route_to_processor(self, format_type: str, input_data: bytes) -> ProcessorInterface:
        """
        Route to appropriate processor for the format.
        
        Args:
            format_type: Detected format string
            input_data: Raw input bytes
            
        Returns:
            ProcessorInterface for handling the format
            
        Raises:
            ValueError: If no processor available for format
        """
        format_key = format_type.lower()
        
        if format_key not in self.processors:
            raise ValueError(f"No processor available for format: {format_type}")
        
        processor = self.processors[format_key]
        
        # Double-check processor can handle this data
        if not processor.can_process(input_data):
            raise ValueError(f"Processor for {format_type} cannot handle this data")
        
        return processor

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

    