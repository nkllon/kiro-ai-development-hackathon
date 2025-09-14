from datetime import datetime
from typing import Dict, List, Any

    def _calculate_dimensions(self, svg_info: Dict[str, Any], max_width: int, max_height: int) -> Tuple[int, int]:
        """Calculate optimal rendering dimensions."""
        svg_width = svg_info.get('width', 100)
        svg_height = svg_info.get('height', 100)
        if svg_info.get('viewbox'):
            vb = svg_info['viewbox']
            svg_width = vb['width']
            svg_height = vb['height']
        aspect_ratio = svg_width / svg_height if svg_height > 0 else 1.0
        if svg_width > max_width or svg_height > max_height:
            if aspect_ratio > 1:
                width = max_width
                height = int(max_width / aspect_ratio)
            else:
                height = max_height
                width = int(max_height * aspect_ratio)
        else:
            width = int(svg_width)
            height = int(svg_height)
        width = max(width, 100)
        height = max(height, 100)
        return (width, height)
