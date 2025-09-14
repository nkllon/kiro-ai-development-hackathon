"""
RDI Enhanced Test Module

Requirements Traceability:

Enhanced: 2025-09-14T06:24:55.787725
"""

    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = SVGProcessor()
    
    def test_supported_formats(self):
        """Test supported formats."""
        assert 'svg' in self.processor.supported_formats
    
    def test_can_process_valid_svg(self):
        """Test detection of valid SVG content."""
        svg_content = b'<svg width="100" height="100"><rect x="10" y="10" width="50" height="50"/></svg>'
        assert self.processor.can_process(svg_content) is True
    
    def test_can_process_xml_svg(self):
        """Test detection of SVG with XML declaration."""
        svg_content = b'<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"></svg>'
        assert self.processor.can_process(svg_content) is True
    
    def test_can_process_invalid_content(self):
        """Test rejection of non-SVG content."""
        invalid_content = b'This is not SVG content'
        assert self.processor.can_process(invalid_content) is False
    
    def test_parse_dimension_pixels(self):
        """Test parsing pixel dimensions."""
        assert self.processor._parse_dimension('100px') == 100.0
        assert self.processor._parse_dimension('50') == 50.0
    
    def test_parse_dimension_units(self):
        """Test parsing various units."""
        # Inches to pixels (96 DPI)
        assert self.processor._parse_dimension('1in') == 96.0
        
        # Points to pixels
        assert abs(self.processor._parse_dimension('72pt') - 95.76) < 1.0
        
        # Invalid/empty dimensions
        assert self.processor._parse_dimension('') == 100.0
        assert self.processor._parse_dimension('invalid') == 100.0
    
    def test_parse_svg_basic(self):
        """Test basic SVG parsing."""
        svg_data = b'<svg width="200" height="150" viewBox="0 0 200 150"></svg>'
        
        svg_info = self.processor._parse_svg(svg_data)
        
        assert svg_info['width'] == 200.0
        assert svg_info['height'] == 150.0
        assert svg_info['viewbox'] is not None
        assert svg_info['viewbox']['width'] == 200.0
        assert svg_info['viewbox']['height'] == 150.0
    
    def test_parse_svg_with_units(self):
        """Test SVG parsing with units."""
        svg_data = b'<svg width="2in" height="100px"></svg>'
        
        svg_info = self.processor._parse_svg(svg_data)
        
        assert svg_info['width'] == 192.0  # 2 * 96 DPI
        assert svg_info['height'] == 100.0
    
    def test_calculate_dimensions_aspect_ratio(self):
        """Test dimension calculation preserving aspect ratio."""
        svg_info = {'width': 200, 'height': 100}  # 2:1 aspect ratio
        
        width, height = self.processor._calculate_dimensions(svg_info, 1000, 1000)
        
        # Should preserve 2:1 aspect ratio
        assert width / height == 2.0
        assert width == 200  # Original size fits within max
        assert height == 100
    
    def test_calculate_dimensions_scaling(self):
        """Test dimension calculation with scaling."""
        svg_info = {'width': 2000, 'height': 1000}  # Larger than max
        
        width, height = self.processor._calculate_dimensions(svg_info, 800, 600)
        
        # Should scale down while preserving aspect ratio
        assert width <= 800
        assert height <= 600
        assert width / height == 2.0  # Preserve 2:1 aspect ratio
    
    def test_extract_metadata(self):
        """Test metadata extraction from SVG."""
        svg_data = b'''<svg width="100" height="100">
            <rect x="10" y="10" width="50" height="50"/>
            <circle cx="75" cy="25" r="15"/>
            <text x="10" y="90">Hello</text>
        </svg>'''
        
        metadata = self.processor.extract_metadata(svg_data)
        
        assert metadata['processor'] == 'SVGProcessor'
        assert metadata['format'] == 'svg'
        assert 'width' in metadata
        assert 'height' in metadata
        assert 'text_elements' in metadata
        assert 'shape_count' in metadata
        
        # Check shape counting
        shapes = metadata['shape_count']
        assert shapes['rectangles'] == 1
        assert shapes['circles'] == 1
        assert shapes['text'] == 1
    
    def test_extract_text_elements(self):
        """Test text element extraction."""
        svg_text = '<svg><text x="10" y="20">First Text</text><text x="30" y="40">Second Text</text></svg>'
        
        text_elements = self.processor._extract_text_elements(svg_text)
        
        assert len(text_elements) == 2
        assert 'First Text' in text_elements
        assert 'Second Text' in text_elements
    
    def test_extract_attr(self):
        """Test attribute extraction from SVG tags."""
        tag = '<rect x="10" y="20.5" width="100px" height="50"/>'
        
        assert self.processor._extract_attr(tag, 'x', 0) == 10.0
        assert self.processor._extract_attr(tag, 'y', 0) == 20.5
        assert self.processor._extract_attr(tag, 'width', 0) == 100.0
        assert self.processor._extract_attr(tag, 'nonexistent', 99) == 99.0
    
    def test_render_to_png_basic(self):
        """Test basic SVG to PNG rendering."""
        svg_data = b'<svg width="100" height="100"><rect x="10" y="10" width="50" height="50" fill="blue"/></svg>'
        
        result = self.processor.render_to_png(svg_data, width=200, height=200)
        
        assert isinstance(result, PNGImage)
        assert result.width > 0
        assert result.height > 0
        assert result.color_mode == 'RGB'
        assert result.dpi == 300
    
    def test_render_to_png_invalid_svg(self):
        """Test handling of invalid SVG data."""
        invalid_svg = b'<invalid>not svg</invalid>'
        
        with pytest.raises(ValueError, match="Failed to process SVG"):
            self.processor.render_to_png(invalid_svg)
    
    def test_parse_svg_text_fallback(self):
        """Test text-based parsing when XML parsing fails."""
        # Malformed XML that should fall back to text parsing
        malformed_svg = b'<svg width="100" height="50" viewBox="0 0 100 50"><rect></svg>'
        
        # Should not raise exception, should fall back to text parsing
        svg_info = self.processor._parse_svg(malformed_svg)
        
        assert 'width' in svg_info
        assert 'height' in svg_info
        assert svg_info.get('parsed_as_text') is True
    
    def test_count_shapes(self):
        """Test shape counting functionality."""
        svg_text = '''
        <svg>
            <rect x="0" y="0" width="50" height="50"/>
            <rect x="60" y="0" width="50" height="50"/>
            <circle cx="25" cy="75" r="20"/>
            <ellipse cx="75" cy="75" rx="20" ry="15"/>
            <path d="M 10 10 L 90 90"/>
            <line x1="0" y1="0" x2="100" y2="100"/>
            <text x="10" y="20">Sample Text</text>
        </svg>
        '''
        
        shapes = self.processor._count_shapes(svg_text)
        
        assert shapes['rectangles'] == 2
        assert shapes['circles'] == 1
        assert shapes['ellipses'] == 1
        assert shapes['paths'] == 1
        assert shapes['lines'] == 1
        assert shapes['text'] == 1