from datetime import datetime
from typing import Dict, List, Any

    def _parse_svg(self, svg_data: bytes) -> Dict[str, Any]:
        """
        Parse SVG to extract basic information.
        
        Args:
            svg_data: SVG content as bytes
            
        Returns:
            Dictionary with SVG information
        """
        try:
            root = ET.fromstring(svg_data.decode('utf-8'))
            width = root.get('width', '100')
            height = root.get('height', '100')
            viewbox = root.get('viewBox', '')
            parsed_width = self._parse_dimension(width)
            parsed_height = self._parse_dimension(height)
            viewbox_info = None
            if viewbox:
                try:
                    vb_parts = viewbox.split()
                    if len(vb_parts) == 4:
                        viewbox_info = {'x': float(vb_parts[0]), 'y': float(vb_parts[1]), 'width': float(vb_parts[2]), 'height': float(vb_parts[3])}
                except ValueError:
                    pass
            return {'width': parsed_width, 'height': parsed_height, 'viewbox': viewbox_info, 'namespace': root.tag.split('}')[0].strip('{') if '}' in root.tag else None}
        except ET.ParseError as e:
            text_content = svg_data.decode('utf-8', errors='ignore')
            return self._parse_svg_text(text_content)
