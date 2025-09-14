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
from src.rm_ddd.core.health import ModuleHealth


@property
def supported_formats(self) -> list[str]:
    """Get supported formats."""
    return self._supported_formats

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

