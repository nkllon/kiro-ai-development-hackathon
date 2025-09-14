from src.rm_ddd.core.registry import register_module

    def _draw_circles(self, draw, svg_text: str, img_width: int, img_height: int, svg_info: Dict[str, Any]):
        """Draw circle/ellipse elements from SVG."""
        circle_pattern = '<(circle|ellipse)[^>]*>'
        for match in re.finditer(circle_pattern, svg_text, re.IGNORECASE):
            element_tag = match.group(0)
            if 'circle' in element_tag.lower():
                cx = self._extract_attr(element_tag, 'cx', 25)
                cy = self._extract_attr(element_tag, 'cy', 25)
                r = self._extract_attr(element_tag, 'r', 25)
                rx = ry = r
            else:
                cx = self._extract_attr(element_tag, 'cx', 25)
                cy = self._extract_attr(element_tag, 'cy', 25)
                rx = self._extract_attr(element_tag, 'rx', 25)
                ry = self._extract_attr(element_tag, 'ry', 25)
            scale_x = img_width / svg_info.get('width', img_width)
            scale_y = img_height / svg_info.get('height', img_height)
            x1 = int((cx - rx) * scale_x)
            y1 = int((cy - ry) * scale_y)
            x2 = int((cx + rx) * scale_x)
            y2 = int((cy + ry) * scale_y)
            draw.ellipse([x1, y1, x2, y2], fill='lightgreen', outline='green', width=2)
