"""
Change Detector Core Processing

This module was extracted from change_detector_core.py
as part of RM-DDD compliance refactoring.
"""

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

def _parse_image_dimensions_basic(self, file_path: Path) -> Optional[Tuple[int, int]]:
    """Basic image dimension parsing without external libraries."""
    try:
        with open(file_path, 'rb') as f:
            if file_path.suffix.lower() == '.png':
                f.seek(16)
                width = int.from_bytes(f.read(4), 'big')
                height = int.from_bytes(f.read(4), 'big')
                return (width, height)
            elif file_path.suffix.lower() in ('.jpg', '.jpeg'):
                return None
    except Exception:
        pass
    return None
