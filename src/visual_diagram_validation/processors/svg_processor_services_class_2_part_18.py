from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def _extract_text_elements(self, svg_text: str) -> list[str]:
        """Extract text content from SVG."""
        text_pattern = '<text[^>]*>([^<]*)</text>'
        return [match.group(1).strip() for match in re.finditer(text_pattern, svg_text, re.IGNORECASE)]
