"""Unit tests for PNG processing utilities."""

import pytest
import io
from PIL import Image

from src.visual_diagram_validation.rendering.png_utils import PNGProcessor
from src.visual_diagram_validation.core.models import PNGImage


class TestPNGProcessor:
    """Test PNG processing functionality."""
    
    def create_test_png_bytes(self, width=100, height=100, mode='RGB'):
        """Helper to create test PNG bytes."""
        img = Image.new(mode, (width, height), color='white')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def test_normalize_png_basic(self):
        """Test basic PNG normalization."""
        test_data = self.create_test_png_bytes(100, 100)
        
        result = PNGProcessor.normalize_png(test_data, target_dpi=300, retina_scale=2.0)
        
        assert isinstance(result, PNGImage)
        assert result.width == 200  # 100 * 2.0 retina scale
        assert result.height == 200
        assert result.dpi == 300
        assert result.color_mode == 'RGB'
    
    def test_normalize_png_rgba_conversion(self):
        """Test RGBA to RGB conversion with transparency handling."""
        test_data = self.create_test_png_bytes(100, 100, mode='RGBA')
        
        result = PNGProcessor.normalize_png(test_data)
        
        assert result.color_mode == 'RGB'
        # Should have white background where transparency was
    
    def test_extract_metadata(self):
        """Test metadata extraction from PNG."""
        test_data = self.create_test_png_bytes(150, 200)
        
        metadata = PNGProcessor.extract_metadata(test_data)
        
        assert 'original_format' in metadata
        assert 'original_mode' in metadata
        assert 'original_size' in metadata
        assert metadata['original_size'] == (150, 200)
    
    def test_validate_png_quality_good(self):
        """Test validation of good quality PNG."""
        png_image = PNGImage(
            data=b"fake_data",
            width=1920,
            height=1080,
            dpi=300,
            color_mode='RGB'
        )
        
        validation = PNGProcessor.validate_png_quality(png_image)
        
        assert validation['is_valid'] is True
        assert len(validation['issues']) == 0
    
    def test_validate_png_quality_low_dpi(self):
        """Test validation catches low DPI."""
        png_image = PNGImage(
            data=b"fake_data",
            width=1920,
            height=1080,
            dpi=72,  # Low DPI
            color_mode='RGB'
        )
        
        validation = PNGProcessor.validate_png_quality(png_image)
        
        assert validation['is_valid'] is False
        assert any("Low DPI" in issue for issue in validation['issues'])
    
    def test_validate_png_quality_low_resolution(self):
        """Test validation catches low resolution."""
        png_image = PNGImage(
            data=b"fake_data",
            width=400,  # Low width
            height=300,  # Low height
            dpi=300,
            color_mode='RGB'
        )
        
        validation = PNGProcessor.validate_png_quality(png_image)
        
        assert validation['is_valid'] is False
        assert any("Low resolution" in issue for issue in validation['issues'])
    
    def test_create_test_image(self):
        """Test test image creation."""
        test_image = PNGProcessor.create_test_image(800, 600, 300)
        
        assert isinstance(test_image, PNGImage)
        assert test_image.width == 800
        assert test_image.height == 600
        assert test_image.dpi == 300
        assert test_image.metadata['test_image'] is True
    
    def test_retina_scaling_disabled(self):
        """Test normalization without retina scaling."""
        test_data = self.create_test_png_bytes(100, 100)
        
        result = PNGProcessor.normalize_png(test_data, retina_scale=1.0)
        
        assert result.width == 100  # No scaling
        assert result.height == 100
    
    def test_metadata_extraction_error_handling(self):
        """Test metadata extraction handles corrupted data gracefully."""
        corrupted_data = b"not_an_image"
        
        metadata = PNGProcessor.extract_metadata(corrupted_data)
        
        assert 'extraction_error' in metadata
        assert isinstance(metadata['extraction_error'], str)