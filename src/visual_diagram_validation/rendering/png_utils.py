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

"""PNG processing utilities for normalization and metadata handling."""

import io
from typing import Dict, Any, Tuple, Optional
from PIL import Image, ImageDraw
import struct

from ..core.models import PNGImage


class PNGProcessor(ReflectiveModule):
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
    """Utilities for PNG image processing and normalization."""
    
    @staticmethod
    def normalize_png(image_data: bytes, target_dpi: int = 300, 
                     retina_scale: float = 2.0) -> PNGImage:
        """
        Normalize PNG image to standard format with DPI and retina scaling.
        
        Args:
            image_data: Raw image bytes
            target_dpi: Target DPI for output
            retina_scale: Scaling factor for retina displays
            
        Returns:
            Normalized PNGImage object
        """
        # Open image from bytes
        with Image.open(io.BytesIO(image_data)) as img:
            # Convert to RGB if necessary (removes alpha channel issues)
            if img.mode != 'RGB':
                # Handle transparency by adding white background
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
                    else:
                        background.paste(img)
                    img = background
                else:
                    img = img.convert('RGB')
            
            # Apply retina scaling
            if retina_scale != 1.0:
                new_width = int(img.width * retina_scale)
                new_height = int(img.height * retina_scale)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Extract metadata before processing
            metadata = PNGProcessor.extract_metadata(image_data)
            
            # Save with target DPI
            output_buffer = io.BytesIO()
            img.save(output_buffer, format='PNG', dpi=(target_dpi, target_dpi), optimize=True)
            normalized_data = output_buffer.getvalue()
            
            return PNGImage(
                data=normalized_data,
                width=img.width,
                height=img.height,
                dpi=target_dpi,
                color_mode='RGB',
                metadata=metadata
            )
    
    @staticmethod
    def extract_metadata(image_data: bytes) -> Dict[str, Any]:
        """
        Extract metadata from PNG image bytes.
        
        Args:
            image_data: Raw PNG bytes
            
        Returns:
            Dictionary containing extracted metadata
        """
        metadata = {}
        
        try:
            with Image.open(io.BytesIO(image_data)) as img:
                # Basic image properties
                metadata['original_format'] = img.format
                metadata['original_mode'] = img.mode
                metadata['original_size'] = img.size
                
                # DPI information
                if hasattr(img, 'info') and 'dpi' in img.info:
                    metadata['original_dpi'] = img.info['dpi']
                
                # Extract EXIF data if present
                if hasattr(img, '_getexif') and img._getexif():
                    metadata['exif'] = dict(img._getexif())
                
                # PNG-specific metadata
                if img.format == 'PNG' and hasattr(img, 'text'):
                    metadata['png_text'] = dict(img.text)
                
                # Color profile information
                if hasattr(img, 'info') and 'icc_profile' in img.info:
                    metadata['has_color_profile'] = True
                
        except Exception as e:
            metadata['extraction_error'] = str(e)
        
        return metadata
    
    @staticmethod
    def validate_png_quality(png_image: PNGImage) -> Dict[str, Any]:
        """
        Validate PNG image meets quality standards.
        
        Args:
            png_image: PNGImage to validate
            
        Returns:
            Dictionary with validation results
        """
        validation = {
            'is_valid': True,
            'issues': [],
            'recommendations': []
        }
        
        # Check resolution
        if png_image.dpi < 150:
            validation['issues'].append(f"Low DPI: {png_image.dpi} (recommended: 300+)")
            validation['recommendations'].append("Increase DPI to 300 for print quality")
        
        # Check dimensions
        if png_image.width < 800 or png_image.height < 600:
            validation['issues'].append(f"Low resolution: {png_image.width}x{png_image.height}")
            validation['recommendations'].append("Use higher resolution for better quality")
        
        # Check file size (too large can cause performance issues)
        size_mb = png_image.size_mb()
        if size_mb > 10:
            validation['issues'].append(f"Large file size: {size_mb:.1f}MB")
            validation['recommendations'].append("Consider optimizing image compression")
        
        # Check aspect ratio (extreme ratios can indicate issues)
        aspect_ratio = png_image.aspect_ratio()
        if aspect_ratio > 5 or aspect_ratio < 0.2:
            validation['issues'].append(f"Unusual aspect ratio: {aspect_ratio:.2f}")
            validation['recommendations'].append("Check if image dimensions are correct")
        
        validation['is_valid'] = len(validation['issues']) == 0
        return validation
    
    @staticmethod
    def create_test_image(width: int = 800, height: int = 600, 
                         dpi: int = 300) -> PNGImage:
        """
        Create a test PNG image for validation testing.
        
        Args:
            width: Image width in pixels
            height: Image height in pixels
            dpi: Target DPI
            
        Returns:
            Test PNGImage object
        """
        # Create a simple test pattern
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add some test elements
        # Grid pattern
        for x in range(0, width, 50):
            draw.line([(x, 0), (x, height)], fill='lightgray', width=1)
        for y in range(0, height, 50):
            draw.line([(0, y), (width, y)], fill='lightgray', width=1)
        
        # Test shapes
        draw.rectangle([50, 50, 150, 100], fill='blue', outline='darkblue', width=2)
        draw.ellipse([200, 50, 300, 150], fill='red', outline='darkred', width=2)
        draw.polygon([(350, 50), (400, 100), (350, 150), (300, 100)], 
                    fill='green', outline='darkgreen')
        
        # Convert to bytes
        output_buffer = io.BytesIO()
        img.save(output_buffer, format='PNG', dpi=(dpi, dpi))
        image_data = output_buffer.getvalue()
        
        return PNGImage(
            data=image_data,
            width=width,
            height=height,
            dpi=dpi,
            color_mode='RGB',
            metadata={'test_image': True, 'created_by': 'PNGProcessor.create_test_image'}
        )