from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _detect_from_extension(self, filename: str) -> Optional[str]:
        """Detect format from file extension."""
        if not filename:
            return None
            
        filename_lower = filename.lower()
        
        # Direct extension mapping
        extension_map = {
            '.svg': 'svg',
            '.pdf': 'pdf',
            '.html': 'html',
            '.htm': 'html',
            '.mmd': 'mermaid',
            '.mermaid': 'mermaid',
            '.png': 'png',
            '.jpg': 'jpeg',
            '.jpeg': 'jpeg',
            '.gif': 'gif'
        }
        
        for ext, format_type in extension_map.items():
            if filename_lower.endswith(ext):
                return format_type
        
        return None
    