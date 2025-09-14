from datetime import datetime
from typing import Dict, List, Any

    def _detect_from_magic_numbers(self, data: bytes) -> Optional[str]:
        """Detect format from magic number signatures."""
        if len(data) < 8:
            return None
        
        # PNG signature
        if data.startswith(b'\x89PNG\r\n\x1a\n'):
            return 'png'
        
        # PDF signature
        if data.startswith(b'%PDF-'):
            return 'pdf'
        
        # JPEG signatures
        if data.startswith(b'\xff\xd8\xff'):
            return 'jpeg'
        
        # GIF signatures
        if data.startswith(b'GIF87a') or data.startswith(b'GIF89a'):
            return 'gif'
        
        return None
    