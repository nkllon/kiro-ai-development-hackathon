from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def can_process(self, input_data: bytes, filename: Optional[str] = None) -> bool:
        """
        Default implementation checks if format is in supported list.
        Subclasses should override for more sophisticated checking.
        """
        try:
            router = FormatRouter()
            detected_format = router.detect_format(input_data, filename)
            return detected_format.lower() in self._supported_formats
        except ValueError:
            return False
    