from datetime import datetime
from typing import Dict, List, Any

    def _extract_text_elements(self, svg_text: str) -> list[str]:
        """Extract text content from SVG."""
        text_pattern = '<text[^>]*>([^<]*)</text>'
        return [match.group(1).strip() for match in re.finditer(text_pattern, svg_text, re.IGNORECASE)]
