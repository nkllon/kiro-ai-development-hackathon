from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _detect_from_content(self, data: bytes) -> Optional[str]:
        """Detect format from content analysis."""
        try:
            # Try to decode as text for text-based formats
            text_content = data.decode('utf-8', errors='ignore')
            text_lower = text_content.lower().strip()
            
            # SVG detection
            if text_lower.startswith('<?xml') and '<svg' in text_lower:
                return 'svg'
            if text_lower.startswith('<svg'):
                return 'svg'
            
            # HTML detection
            if text_lower.startswith('<!doctype html') or text_lower.startswith('<html'):
                return 'html'
            
            # Mermaid detection (look for common Mermaid keywords)
            mermaid_keywords = ['graph', 'flowchart', 'sequencediagram', 'classDiagram', 
                              'stateDiagram', 'erDiagram', 'journey', 'gantt']
            
            # Check if content starts with mermaid syntax
            first_line = text_content.split('\n')[0].strip().lower()
            for keyword in mermaid_keywords:
                if first_line.startswith(keyword.lower()):
                    return 'mermaid'
            
            # Check for mermaid syntax patterns
            if any(keyword in text_lower for keyword in mermaid_keywords):
                # Additional validation - look for arrow syntax
                if '-->' in text_content or '--->' in text_content or '-.->' in text_content:
                    return 'mermaid'
        
        except UnicodeDecodeError:
            # Not a text-based format
            pass
        
        return None

