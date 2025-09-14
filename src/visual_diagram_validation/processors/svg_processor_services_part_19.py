from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def can_process(self, input_data: bytes, filename: Optional[str]=None) -> bool:
        """
        Check if this processor can handle the input SVG data.
        
        Args:
            input_data: Raw SVG bytes
            filename: Optional filename
            
        Returns:
            True if can process, False otherwise
        """
        try:
            text_content = input_data.decode('utf-8', errors='ignore')
            text_lower = text_content.lower().strip()
            if '<svg' in text_lower:
                return True
            if text_lower.startswith('<?xml') and '<svg' in text_lower:
                return True
        except Exception:
            pass
        return False
