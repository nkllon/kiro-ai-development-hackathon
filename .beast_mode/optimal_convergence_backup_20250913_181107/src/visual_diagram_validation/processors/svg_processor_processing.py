"""
Svg Processor Processing

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

def can_process(self, input_data: bytes, filename: Optional[str]=None) -> bool:
    """
        Check if this processor can handle the input SVG data.
        
        Args:
            input_data: Raw SVG bytes
            filename: Optional filename
            
        Returns:
            True if can process, False otherwise
        """
    try:
        text_content = input_data.decode('utf-8', errors='ignore')
        text_lower = text_content.lower().strip()
        if '<svg' in text_lower:
            return True
        if text_lower.startswith('<?xml') and '<svg' in text_lower:
            return True
    except Exception:
        pass
    return False

def _parse_svg(self, svg_data: bytes) -> Dict[str, Any]:
    """
        Parse SVG to extract basic information.
        
        Args:
            svg_data: SVG content as bytes
            
        Returns:
            Dictionary with SVG information
        """
    try:
        root = ET.fromstring(svg_data.decode('utf-8'))
        width = root.get('width', '100')
        height = root.get('height', '100')
        viewbox = root.get('viewBox', '')
        parsed_width = self._parse_dimension(width)
        parsed_height = self._parse_dimension(height)
        viewbox_info = None
        if viewbox:
            try:
                vb_parts = viewbox.split()
                if len(vb_parts) == 4:
                    viewbox_info = {'x': float(vb_parts[0]), 'y': float(vb_parts[1]), 'width': float(vb_parts[2]), 'height': float(vb_parts[3])}
            except ValueError:
                pass
        return {'width': parsed_width, 'height': parsed_height, 'viewbox': viewbox_info, 'namespace': root.tag.split('}')[0].strip('{') if '}' in root.tag else None}
    except ET.ParseError as e:
        text_content = svg_data.decode('utf-8', errors='ignore')
        return self._parse_svg_text(text_content)

def _parse_dimension(self, dim_str: str) -> float:
    """Parse dimension string (e.g., '100px', '50%', '2in') to pixels."""
    if not dim_str:
        return 100.0
    numeric_part = re.sub('[^0-9.]', '', dim_str)
    try:
        value = float(numeric_part) if numeric_part else 100.0
        if 'in' in dim_str:
            value *= 96
        elif 'cm' in dim_str:
            value *= 37.8
        elif 'mm' in dim_str:
            value *= 3.78
        elif 'pt' in dim_str:
            value *= 1.33
        return value
    except ValueError:
        return 100.0

def _parse_svg_text(self, text_content: str) -> Dict[str, Any]:
    """Parse SVG from text when XML parsing fails."""
    width_match = re.search('width\\s*=\\s*["\\\']([^"\\\']+)["\\\']', text_content, re.IGNORECASE)
    height_match = re.search('height\\s*=\\s*["\\\']([^"\\\']+)["\\\']', text_content, re.IGNORECASE)
    viewbox_match = re.search('viewBox\\s*=\\s*["\\\']([^"\\\']+)["\\\']', text_content, re.IGNORECASE)
    width = self._parse_dimension(width_match.group(1) if width_match else '100')
    height = self._parse_dimension(height_match.group(1) if height_match else '100')
    viewbox_info = None
    if viewbox_match:
        try:
            vb_parts = viewbox_match.group(1).split()
            if len(vb_parts) == 4:
                viewbox_info = {'x': float(vb_parts[0]), 'y': float(vb_parts[1]), 'width': float(vb_parts[2]), 'height': float(vb_parts[3])}
        except ValueError:
            pass
    return {'width': width, 'height': height, 'viewbox': viewbox_info, 'parsed_as_text': True}
