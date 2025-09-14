from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def render_to_png(self, input_data: bytes, width: int=2048, height: int=2048, dpi: int=300) -> PNGImage:
        """
        Convert SVG to PNG format.
        
        Args:
            input_data: SVG data as bytes
            width: Target width in pixels
            height: Target height in pixels
            dpi: Target DPI
            
        Returns:
            PNGImage object
            
        Raises:
            ValueError: If SVG cannot be processed
        """
        try:
            svg_info = self._parse_svg(input_data)
            target_width, target_height = self._calculate_dimensions(svg_info, width, height)
            png_data = self._rasterize_svg_simple(input_data, target_width, target_height, svg_info)
            return PNGProcessor.normalize_png(png_data, dpi, retina_scale=1.0)
        except Exception as e:
            raise ValueError(f'Failed to process SVG: {str(e)}')
