import hashlib
import logging
import mimetypes
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime
from dataclasses import dataclass
from ..models import FileChangeEvent, ChangeType
from PIL import Image
from PIL import Image
from PIL import Image
from PIL import Image
from PIL import Image
from PIL import Image
from .change_detector_core_core_core import *
from .change_detector_core_core_processing import *
from src.rm_ddd.core.health import ModuleHealth


    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

