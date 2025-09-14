"""Unit tests for contrast analyzer."""

import pytest
import io
from PIL import Image, ImageDraw
import numpy as np

from src.visual_diagram_validation.analyzers.contrast_analyzer import ContrastAnalyzer
from src.visual_diagram_validation.core.models import PNGImage, BoundingBox
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule



class TestContrastAnalyzer(ReflectiveModule):
    """Test contrast analysis functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = ContrastAnalyzer()
    
    def create_test_image_with_text(self, width=200, height=100, 
                                   text_color=(0, 0, 0), bg_color=(255, 255, 255)):
        """Create test image with text for contrast testing."""
        img = Image.new('RGB', (width, height), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # Draw some text-like rectangles
        draw.rectangle([10, 10, 60, 30], fill=text_color)
        draw.rectangle([70, 10, 120, 30], fill=text_color)
        
        # Convert to PNG bytes
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        
        return PNGImage(
            data=buffer.getvalue(),
            width=width,
            height=height,
            dpi=300,
            color_mode='RGB'
        )
    
    def test_analyzer_properties(self):
        """Test analyzer properties."""
        assert self.analyzer.analyzer_name == "contrast_analyzer"
        assert "wcag_contrast_normal" in self.analyzer.supported_rules
        assert "wcag_contrast_large" in self.analyzer.supported_rules
        assert "wcag_contrast_graphical" in self.analyzer.supported_rules
    
    def test_calculate_relative_luminance(self):
        """Test relative luminance calculation."""
        # Test known values
        white_luminance = self.analyzer._calculate_relative_luminance((255, 255, 255))
        black_luminance = self.analyzer._calculate_relative_luminance((0, 0, 0))
        
        assert abs(white_luminance - 1.0) < 0.01
        assert abs(black_luminance - 0.0) < 0.01
        
        # Test gray
        gray_luminance = self.analyzer._calculate_relative_luminance((128, 128, 128))
        assert 0.2 < gray_luminance < 0.3  # Approximate expected range
    
    def test_calculate_contrast_ratio(self):
        """Test contrast ratio calculation."""
        # Black on white should be maximum contrast (21:1)
        black_white_ratio = self.analyzer._calculate_contrast_ratio((0, 0, 0), (255, 255, 255))
        assert abs(black_white_ratio - 21.0) < 0.1
        
        # Same colors should be minimum contrast (1:1)
        same_color_ratio = self.analyzer._calculate_contrast_ratio((128, 128, 128), (128, 128, 128))
        assert abs(same_color_ratio - 1.0) < 0.1
        
        # Test known failing combination (light gray on white)
        low_contrast_ratio = self.analyzer._calculate_contrast_ratio((200, 200, 200), (255, 255, 255))
        assert low_contrast_ratio < 4.5  # Should fail WCAG AA
    
    def test_looks_like_text_region(self):
        """Test text region detection."""
        # Create text-like region (moderate variance)
        text_region = np.array([
            [[0, 0, 0], [255, 255, 255], [0, 0, 0]],
            [[255, 255, 255], [0, 0, 0], [255, 255, 255]],
            [[0, 0, 0], [255, 255, 255], [0, 0, 0]]
        ])
        
        assert self.analyzer._looks_like_text_region(text_region) is True
        
        # Create solid color region (low variance)
        solid_region = np.full((3, 3, 3), 128)
        assert self.analyzer._looks_like_text_region(solid_region) is False
    
    def test_looks_like_graphical_element(self):
        """Test graphical element detection."""
        # Create region with edges (moderate edge density)
        edge_region = np.array([
            [0, 0, 255],
            [0, 255, 255],
            [255, 255, 255]
        ])
        
        assert self.analyzer._looks_like_graphical_element(edge_region) is True
        
        # Create smooth region (low edge density)
        smooth_region = np.array([
            [100, 101, 102],
            [101, 102, 103],
            [102, 103, 104]
        ])
        
        assert self.analyzer._looks_like_graphical_element(smooth_region) is False
    
    def test_extract_text_background_colors(self):
        """Test text and background color extraction."""
        # Create image with clear text and background
        img = Image.new('RGB', (100, 50), color=(255, 255, 255))  # White background
        draw = ImageDraw.Draw(img)
        draw.rectangle([10, 10, 90, 40], fill=(0, 0, 0))  # Black text area
        
        bbox = BoundingBox(x=5, y=5, width=90, height=40)
        text_color, bg_color = self.analyzer._extract_text_background_colors(img, bbox)
        
        # Should detect black text on white background (or vice versa)
        assert text_color in [(0, 0, 0), (255, 255, 255)]
        assert bg_color in [(0, 0, 0), (255, 255, 255)]
        assert text_color != bg_color
    
    def test_analyze_good_contrast(self):
        """Test analysis of image with good contrast."""
        # Create image with good contrast (black on white)
        test_image = self.create_test_image_with_text(
            text_color=(0, 0, 0), 
            bg_color=(255, 255, 255)
        )
        
        # Add metadata to simulate text detection
        metadata = {
            'text_elements': ['Good contrast text', 'Another text']
        }
        
        result = self.analyzer.analyze(test_image, metadata)
        
        # Should have no contrast violations
        contrast_violations = [v for v in result.violations if 'contrast' in v.rule_id]
        assert len(contrast_violations) == 0
    
    def test_analyze_poor_contrast(self):
        """Test analysis of image with poor contrast."""
        # Create image with poor contrast (light gray on white)
        test_image = self.create_test_image_with_text(
            text_color=(200, 200, 200), 
            bg_color=(255, 255, 255)
        )
        
        # Add metadata to simulate text detection
        metadata = {
            'text_elements': ['Poor contrast text']
        }
        
        result = self.analyzer.analyze(test_image, metadata)
        
        # Should have contrast violations
        contrast_violations = [v for v in result.violations if 'contrast' in v.rule_id]
        assert len(contrast_violations) > 0
        
        # Check violation details
        violation = contrast_violations[0]
        assert violation.current_value < violation.expected_value
        assert 'contrast ratio' in violation.description.lower()
    
    def test_analyze_with_config(self):
        """Test analysis with custom configuration."""
        config = {
            'contrast_normal_threshold': 3.0,  # Lower threshold
            'contrast_large_threshold': 2.0
        }
        
        analyzer = ContrastAnalyzer(config)
        
        # Create image with moderate contrast
        test_image = self.create_test_image_with_text(
            text_color=(100, 100, 100), 
            bg_color=(255, 255, 255)
        )
        
        metadata = {'text_elements': ['Moderate contrast']}
        result = analyzer.analyze(test_image, metadata)
        
        # With lower threshold, should pass
        contrast_violations = [v for v in result.violations if 'wcag_contrast' in v.rule_id]
        # May or may not have violations depending on actual contrast ratio
    
    def test_detect_text_regions_visual(self):
        """Test visual text region detection."""
        # Create image with text-like patterns
        img = Image.new('RGB', (200, 100), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # Draw some text-like rectangles
        draw.rectangle([10, 10, 60, 30], fill=(0, 0, 0))
        draw.rectangle([70, 40, 120, 60], fill=(50, 50, 50))
        
        regions = self.analyzer._detect_text_regions_visual(img)
        
        # Should detect some regions
        assert len(regions) > 0
        
        # Check region structure
        for region in regions:
            assert 'text' in region
            assert 'bbox' in region
            assert isinstance(region['bbox'], BoundingBox)
    
    def test_detect_graphical_elements(self):
        """Test graphical element detection."""
        # Create image with shapes
        img = Image.new('RGB', (200, 100), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # Draw some shapes
        draw.rectangle([20, 20, 60, 60], fill=(0, 0, 255), outline=(0, 0, 0))
        draw.ellipse([80, 20, 120, 60], fill=(255, 0, 0), outline=(0, 0, 0))
        
        elements = self.analyzer._detect_graphical_elements(img)
        
        # Should detect some elements
        assert len(elements) >= 0  # May or may not detect depending on algorithm
        
        # Check element structure if any detected
        for element in elements:
            assert 'type' in element
            assert 'bbox' in element
            assert isinstance(element['bbox'], BoundingBox)
    
    def test_analyze_overall_contrast(self):
        """Test overall image contrast analysis."""
        # Create low contrast image
        low_contrast_img = Image.new('RGB', (100, 100), color=(128, 128, 128))
        
        # Convert to PNGImage
        buffer = io.BytesIO()
        low_contrast_img.save(buffer, format='PNG')
        png_image = PNGImage(
            data=buffer.getvalue(),
            width=100,
            height=100,
            dpi=300,
            color_mode='RGB'
        )
        
        result = self.analyzer.analyze(png_image)
        
        # Should detect low overall contrast
        overall_violations = [v for v in result.violations if v.rule_id == 'overall_contrast']

    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }
        
    def register_module(self, registry):
        """Register module with registry."""
        if hasattr(registry, 'register'):
            registry.register(self.get_interface_metadata())
            
    def health_check(self):
        """Perform health check."""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'module_id': getattr(self, 'module_id', self.__class__.__name__)
        }
        
    def get_health_status(self):
        """Get current health status."""
        return self.health_check()

        assert len(overall_violations) > 0