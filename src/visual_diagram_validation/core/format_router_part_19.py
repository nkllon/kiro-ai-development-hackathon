from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def detect_format(self, input_data: bytes, filename: Optional[str] = None) -> str:
        """
        Detect the format of input data.
        
        Args:
            input_data: Raw input bytes
            filename: Optional filename for extension-based detection
            
        Returns:
            Detected format string
            
        Raises:
            ValueError: If format cannot be detected
        """
        # Try filename extension first if available
        if filename:
            format_from_extension = self._detect_from_extension(filename)
            if format_from_extension:
                return format_from_extension
        
        # Try magic number detection
        format_from_magic = self._detect_from_magic_numbers(input_data)
        if format_from_magic:
            return format_from_magic
        
        # Try content analysis for text-based formats
        format_from_content = self._detect_from_content(input_data)
        if format_from_content:
            return format_from_content
        
        raise ValueError("Unable to detect input format")

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

    