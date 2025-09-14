from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def __init__(self):
        """Initialize the format router."""
        self.processors: Dict[str, ProcessorInterface] = {}
        self._mime_to_format = {
            'image/svg+xml': 'svg',
            'application/pdf': 'pdf', 
            'text/html': 'html',
            'text/plain': 'mermaid',  # Mermaid is plain text
            'image/png': 'png',
            'image/jpeg': 'jpeg',
            'image/gif': 'gif'
        }
        