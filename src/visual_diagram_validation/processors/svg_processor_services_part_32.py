from datetime import datetime
from typing import Dict, List, Any

    def _count_shapes(self, svg_text: str) -> Dict[str, int]:
        """Count different shape types in SVG."""
        shapes = {'rectangles': len(re.findall('<rect[^>]*>', svg_text, re.IGNORECASE)), 'circles': len(re.findall('<circle[^>]*>', svg_text, re.IGNORECASE)), 'ellipses': len(re.findall('<ellipse[^>]*>', svg_text, re.IGNORECASE)), 'paths': len(re.findall('<path[^>]*>', svg_text, re.IGNORECASE)), 'lines': len(re.findall('<line[^>]*>', svg_text, re.IGNORECASE)), 'text': len(re.findall('<text[^>]*>', svg_text, re.IGNORECASE))}
        return shapes
