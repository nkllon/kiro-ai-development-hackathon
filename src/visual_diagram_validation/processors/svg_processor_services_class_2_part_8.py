from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def extract_metadata(self, input_data: bytes) -> Dict[str, Any]:
        """
        Extract metadata from SVG content.
        
        Args:
            input_data: SVG data as bytes
            
        Returns:
            Dictionary containing SVG metadata
        """
        metadata = {'processor': 'SVGProcessor', 'format': 'svg', 'data_size': len(input_data)}
        try:
            svg_info = self._parse_svg(input_data)
            metadata.update(svg_info)
            text_content = input_data.decode('utf-8', errors='ignore')
            metadata['text_elements'] = self._extract_text_elements(text_content)
            metadata['shape_count'] = self._count_shapes(text_content)
        except Exception as e:
            metadata['parsing_error'] = str(e)
        return metadata

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

