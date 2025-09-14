"""
Svg Processor Utils

This module was extracted from svg_processor.py
as part of RM-DDD compliance refactoring.
"""

import io
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, Tuple
from PIL import Image, ImageDraw
import re
from ..core.interfaces import ProcessorInterface
from ..core.models import PNGImage
from ..rendering.png_utils import PNGProcessor

@property
def supported_formats(self) -> list[str]:
    """Get supported formats."""
    return self._supported_formats
