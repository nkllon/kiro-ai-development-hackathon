from datetime import datetime
from typing import Dict, List, Any

    def update_health_status(self, status: str):
        """Update module health status."""
        self.health_status = status
        self.last_updated = datetime.now().isoformat()

"""Format detection and routing system for the validation pipeline."""

import mimetypes
from typing import List, Dict, Optional, Type
from ..core.interfaces import ProcessorInterface
from ..core.models import PNGImage
from src.rm_ddd.core.health import ModuleHealth


