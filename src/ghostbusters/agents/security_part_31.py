from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _should_analyze_file(self, file_path: Path) -> bool:
        """Determine if file should be analyzed for security issues"""
        skip_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.zip', '.tar', '.gz'}
        if file_path.suffix.lower() in skip_extensions:
            return False
        try:
            if file_path.stat().st_size > 10 * 1024 * 1024:
                return False
        except:
            pass
        return True
