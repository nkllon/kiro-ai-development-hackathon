from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _parse_svg_text(self, text_content: str) -> Dict[str, Any]:
        """Parse SVG from text when XML parsing fails."""
        width_match = re.search('width\\s*=\\s*["\\\']([^"\\\']+)["\\\']', text_content, re.IGNORECASE)
        height_match = re.search('height\\s*=\\s*["\\\']([^"\\\']+)["\\\']', text_content, re.IGNORECASE)
        viewbox_match = re.search('viewBox\\s*=\\s*["\\\']([^"\\\']+)["\\\']', text_content, re.IGNORECASE)
        width = self._parse_dimension(width_match.group(1) if width_match else '100')
        height = self._parse_dimension(height_match.group(1) if height_match else '100')
        viewbox_info = None
        if viewbox_match:
            try:
                vb_parts = viewbox_match.group(1).split()
                if len(vb_parts) == 4:
                    viewbox_info = {'x': float(vb_parts[0]), 'y': float(vb_parts[1]), 'width': float(vb_parts[2]), 'height': float(vb_parts[3])}
            except ValueError:
                pass
        return {'width': width, 'height': height, 'viewbox': viewbox_info, 'parsed_as_text': True}
