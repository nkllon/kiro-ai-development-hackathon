from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def _draw_rectangles(self, draw, svg_text: str, img_width: int, img_height: int, svg_info: Dict[str, Any]):
        """Draw rectangle elements from SVG."""
        rect_pattern = '<rect[^>]*>'
        for match in re.finditer(rect_pattern, svg_text, re.IGNORECASE):
            rect_tag = match.group(0)
            x = self._extract_attr(rect_tag, 'x', 0)
            y = self._extract_attr(rect_tag, 'y', 0)
            w = self._extract_attr(rect_tag, 'width', 50)
            h = self._extract_attr(rect_tag, 'height', 50)
            scale_x = img_width / svg_info.get('width', img_width)
            scale_y = img_height / svg_info.get('height', img_height)
            x1 = int(x * scale_x)
            y1 = int(y * scale_y)
            x2 = int((x + w) * scale_x)
            y2 = int((y + h) * scale_y)
            draw.rectangle([x1, y1, x2, y2], fill='lightblue', outline='blue', width=2)
