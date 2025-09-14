from src.rm_ddd.core.registry import register_module

    def _extract_attr(self, tag: str, attr_name: str, default: float) -> float:
        """Extract numeric attribute value from SVG tag."""
        pattern = f"""{attr_name}\\s*=\\s*["']([^"']+)["']"""
        match = re.search(pattern, tag, re.IGNORECASE)
        if match:
            try:
                return float(re.sub('[^0-9.]', '', match.group(1)))
            except ValueError:
                pass
        return default
