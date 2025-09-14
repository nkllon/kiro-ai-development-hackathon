from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


class CountshapesClass:
    """Auto-generated class for functions."""

    def _count_shapes(self, svg_text: str) -> Dict[str, int]:
    """Count different shape types in SVG."""
    shapes = {'rectangles': len(re.findall('<rect[^>]*>', svg_text, re.IGNORECASE)), 'circles': len(re.findall('<circle[^>]*>', svg_text, re.IGNORECASE)), 'ellipses': len(re.findall('<ellipse[^>]*>', svg_text, re.IGNORECASE)), 'paths': len(re.findall('<path[^>]*>', svg_text, re.IGNORECASE)), 'lines': len(re.findall('<line[^>]*>', svg_text, re.IGNORECASE)), 'text': len(re.findall('<text[^>]*>', svg_text, re.IGNORECASE))}
    return shapes
