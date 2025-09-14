from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def _draw_text_placeholders(self, draw, svg_text: str, img_width: int, img_height: int):
        """Draw placeholder boxes for text elements."""
        text_pattern = '<text[^>]*>([^<]*)</text>'
        for i, match in enumerate(re.finditer(text_pattern, svg_text, re.IGNORECASE)):
            x = 10 + i * 120 % (img_width - 100)
            y = 30 + i // 5 * 30
            draw.rectangle([x, y, x + 100, y + 20], fill='lightyellow', outline='orange')
