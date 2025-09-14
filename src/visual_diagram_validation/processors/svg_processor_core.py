"""
Svg Processor Core

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


def __init__(self):
    """Initialize SVG processor."""
    self._supported_formats = ['svg']

def render_to_png(self, input_data: bytes, width: int=2048, height: int=2048, dpi: int=300) -> PNGImage:
    """
        Convert SVG to PNG format.
        
        Args:
            input_data: SVG data as bytes
            width: Target width in pixels
            height: Target height in pixels
            dpi: Target DPI
            
        Returns:
            PNGImage object
            
        Raises:
            ValueError: If SVG cannot be processed
        """
    try:
        svg_info = self._parse_svg(input_data)
        target_width, target_height = self._calculate_dimensions(svg_info, width, height)
        png_data = self._rasterize_svg_simple(input_data, target_width, target_height, svg_info)
        return PNGProcessor.normalize_png(png_data, dpi, retina_scale=1.0)
    except Exception as e:
        raise ValueError(f'Failed to process SVG: {str(e)}')

def extract_metadata(self, input_data: bytes) -> Dict[str, Any]:
    """
        Extract metadata from SVG content.
        
        Args:
            input_data: SVG data as bytes
            
        Returns:
            Dictionary containing SVG metadata
        """
    metadata = {'processor': 'SVGProcessor', 'format': 'svg', 'data_size': len(input_data)}
    try:
        svg_info = self._parse_svg(input_data)
        metadata.update(svg_info)
        text_content = input_data.decode('utf-8', errors='ignore')
        metadata['text_elements'] = self._extract_text_elements(text_content)
        metadata['shape_count'] = self._count_shapes(text_content)
    except Exception as e:
        metadata['parsing_error'] = str(e)
    return metadata

def _calculate_dimensions(self, svg_info: Dict[str, Any], max_width: int, max_height: int) -> Tuple[int, int]:
    """Calculate optimal rendering dimensions."""
    svg_width = svg_info.get('width', 100)
    svg_height = svg_info.get('height', 100)
    if svg_info.get('viewbox'):
        vb = svg_info['viewbox']
        svg_width = vb['width']
        svg_height = vb['height']
    aspect_ratio = svg_width / svg_height if svg_height > 0 else 1.0
    if svg_width > max_width or svg_height > max_height:
        if aspect_ratio > 1:
            width = max_width
            height = int(max_width / aspect_ratio)
        else:
            height = max_height
            width = int(max_height * aspect_ratio)
    else:
        width = int(svg_width)
        height = int(svg_height)
    width = max(width, 100)
    height = max(height, 100)
    return (width, height)

def _rasterize_svg_simple(self, svg_data: bytes, width: int, height: int, svg_info: Dict[str, Any]) -> bytes:
    """
        Simple SVG rasterization for basic shapes.
        In production, this would use librsvg or cairosvg.
        """
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    text_content = svg_data.decode('utf-8', errors='ignore')
    self._draw_rectangles(draw, text_content, width, height, svg_info)
    self._draw_circles(draw, text_content, width, height, svg_info)
    self._draw_text_placeholders(draw, text_content, width, height)
    output_buffer = io.BytesIO()
    img.save(output_buffer, format='PNG')
    return output_buffer.getvalue()

def _draw_rectangles(self, draw, svg_text: str, img_width: int, img_height: int, svg_info: Dict[str, Any]):
    """Draw rectangle elements from SVG."""
    rect_pattern = '<rect[^>]*>'
    for match in re.finditer(rect_pattern, svg_text, re.IGNORECASE):
        rect_tag = match.group(0)
        x = self._extract_attr(rect_tag, 'x', 0)
        y = self._extract_attr(rect_tag, 'y', 0)
        w = self._extract_attr(rect_tag, 'width', 50)
        h = self._extract_attr(rect_tag, 'height', 50)
        scale_x = img_width / svg_info.get('width', img_width)
        scale_y = img_height / svg_info.get('height', img_height)
        x1 = int(x * scale_x)
        y1 = int(y * scale_y)
        x2 = int((x + w) * scale_x)
        y2 = int((y + h) * scale_y)
        draw.rectangle([x1, y1, x2, y2], fill='lightblue', outline='blue', width=2)

def _draw_circles(self, draw, svg_text: str, img_width: int, img_height: int, svg_info: Dict[str, Any]):
    """Draw circle/ellipse elements from SVG."""
    circle_pattern = '<(circle|ellipse)[^>]*>'
    for match in re.finditer(circle_pattern, svg_text, re.IGNORECASE):
        element_tag = match.group(0)
        if 'circle' in element_tag.lower():
            cx = self._extract_attr(element_tag, 'cx', 25)
            cy = self._extract_attr(element_tag, 'cy', 25)
            r = self._extract_attr(element_tag, 'r', 25)
            rx = ry = r
        else:
            cx = self._extract_attr(element_tag, 'cx', 25)
            cy = self._extract_attr(element_tag, 'cy', 25)
            rx = self._extract_attr(element_tag, 'rx', 25)
            ry = self._extract_attr(element_tag, 'ry', 25)
        scale_x = img_width / svg_info.get('width', img_width)
        scale_y = img_height / svg_info.get('height', img_height)
        x1 = int((cx - rx) * scale_x)
        y1 = int((cy - ry) * scale_y)
        x2 = int((cx + rx) * scale_x)
        y2 = int((cy + ry) * scale_y)
        draw.ellipse([x1, y1, x2, y2], fill='lightgreen', outline='green', width=2)

def _draw_text_placeholders(self, draw, svg_text: str, img_width: int, img_height: int):
    """Draw placeholder boxes for text elements."""
    text_pattern = '<text[^>]*>([^<]*)</text>'
    for i, match in enumerate(re.finditer(text_pattern, svg_text, re.IGNORECASE)):
        x = 10 + i * 120 % (img_width - 100)
        y = 30 + i // 5 * 30
        draw.rectangle([x, y, x + 100, y + 20], fill='lightyellow', outline='orange')

def _extract_attr(self, tag: str, attr_name: str, default: float) -> float:
    """Extract numeric attribute value from SVG tag."""
    pattern = f"""{attr_name}\\s*=\\s*["']([^"']+)["']"""
    match = re.search(pattern, tag, re.IGNORECASE)
    if match:
        try:
            return float(re.sub('[^0-9.]', '', match.group(1)))
        except ValueError:
            pass
    return default

def _extract_text_elements(self, svg_text: str) -> list[str]:
    """Extract text content from SVG."""
    text_pattern = '<text[^>]*>([^<]*)</text>'
    return [match.group(1).strip() for match in re.finditer(text_pattern, svg_text, re.IGNORECASE)]

def _count_shapes(self, svg_text: str) -> Dict[str, int]:
    """Count different shape types in SVG."""
    shapes = {'rectangles': len(re.findall('<rect[^>]*>', svg_text, re.IGNORECASE)), 'circles': len(re.findall('<circle[^>]*>', svg_text, re.IGNORECASE)), 'ellipses': len(re.findall('<ellipse[^>]*>', svg_text, re.IGNORECASE)), 'paths': len(re.findall('<path[^>]*>', svg_text, re.IGNORECASE)), 'lines': len(re.findall('<line[^>]*>', svg_text, re.IGNORECASE)), 'text': len(re.findall('<text[^>]*>', svg_text, re.IGNORECASE))}
    return shapes

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

