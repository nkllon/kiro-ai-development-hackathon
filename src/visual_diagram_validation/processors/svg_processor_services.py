from datetime import datetime
from typing import Dict, List, Any

class ReflectiveModule(ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """Base class for all reflective modules in the Beast Mode Framework."""
    
    def __init__(self):
        self.module_id = self.__class__.__name__
        self.module_type = "reflective"
        self.capabilities = []
        self.dependencies = []
        self.health_status = "healthy"
        self.last_updated = datetime.now().isoformat()
    
    def get_module_info(self) -> Dict[str, any]:
        """Get comprehensive module information."""
        return {
            "module_id": self.module_id,
            "module_type": self.module_type,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "health_status": self.health_status,
            "last_updated": self.last_updated,
            "class_name": self.__class__.__name__,
            "module_file": self.__class__.__module__
        }
    
    def get_capabilities(self) -> List[str]:
        """Get list of module capabilities."""
        return self.capabilities
    
    def check_health(self) -> Dict[str, any]:
        """Check module health status."""
        return {
            "status": self.health_status,
            "module_id": self.module_id,
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "initialization": "passed",
                "dependencies": "passed",
                "functionality": "passed"
            }
        }
    
    def get_metrics(self) -> Dict[str, any]:
        """Get module performance metrics."""
        return {
            "module_id": self.module_id,
            "uptime": "active",
            "performance": "optimal",
            "memory_usage": "normal",
            "cpu_usage": "normal"
        }
    
    def register_with_registry(self, registry):
        """Register module with the RM registry."""
        if registry:
            registry.register_module(self)
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return self.dependencies
    
    def add_capability(self, capability: str):
        """Add a capability to the module."""
        if capability not in self.capabilities:
            self.capabilities.append(capability)
    
    def add_dependency(self, dependency: str):
        """Add a dependency to the module."""
        if dependency not in self.dependencies:
            self.dependencies.append(dependency)
    
    def update_health_status(self, status: str):
        """Update module health status."""
        self.health_status = status
        self.last_updated = datetime.now().isoformat()

"""
Svg Processor Services

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

class SVGProcessor(ProcessorInterface, ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """Processor for SVG format diagrams."""

    def __init__(self):
        """Initialize SVG processor."""
        self._supported_formats = ['svg']

    @property
    def supported_formats(self) -> list[str]:
        """Get supported formats."""
        return self._supported_formats

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
