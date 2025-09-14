from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _extract_text_elements(self, svg_text: str) -> list[str]:
        """Extract text content from SVG."""
        text_pattern = '<text[^>]*>([^<]*)</text>'
        return [match.group(1).strip() for match in re.finditer(text_pattern, svg_text, re.IGNORECASE)]

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

