from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()
