"""Contrast analyzer for WCAG compliance checking."""

import io
import math
from typing import List, Dict, Any, Tuple, Optional
from PIL import Image, ImageDraw
import numpy as np

from .base_analyzer import BaseQualityAnalyzer
from ..core.models import PNGImage, Severity, ActionType, BoundingBox


class ContrastAnalyzer(BaseQualityAnalyzer):
    """Analyzer for color contrast compliance with WCAG standards."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize contrast analyzer."""
        super().__init__(config)
        
        # WCAG contrast thresholds
        self.normal_text_threshold = self.get_threshold("contrast_normal", 4.5)
        self.large_text_threshold = self.get_threshold("contrast_large", 3.0)
        self.graphical_threshold = self.get_threshold("contrast_graphical", 3.0)
        
        # Text size thresholds (in pixels, approximate)
        self.large_text_size = self.get_threshold("large_text_size", 18)
        self.bold_large_text_size = self.get_threshold("bold_large_text_size", 14)
    
    @property
    def analyzer_name(self) -> str:
        """Get analyzer name."""
        return "contrast_analyzer"
    
    @property
    def supported_rules(self) -> List[str]:
        """Get supported quality rules."""
        return [
            "wcag_contrast_normal",
            "wcag_contrast_large", 
            "wcag_contrast_graphical",
            "text_background_contrast",
            "element_contrast"
        ]
    
    def _perform_analysis(self, image: PNGImage, metadata: Dict[str, Any]) -> None:
        """
        Perform contrast analysis on the image.
        
        Args:
            image: PNGImage to analyze
            metadata: Processing metadata
        """
        # Convert to PIL Image for analysis
        pil_image = Image.open(io.BytesIO(image.data))
        
        # Detect text regions (simplified approach)
        text_regions = self._detect_text_regions(pil_image, metadata)
        
        # Analyze contrast for each text region
        for region in text_regions:
            self._analyze_text_contrast(pil_image, region)
        
        # Detect and analyze graphical elements
        graphical_elements = self._detect_graphical_elements(pil_image)
        
        for element in graphical_elements:
            self._analyze_graphical_contrast(pil_image, element)
        
        # Overall image contrast analysis
        self._analyze_overall_contrast(pil_image)
    
    def _detect_text_regions(self, image: Image.Image, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect text regions in the image.
        
        Args:
            image: PIL Image to analyze
            metadata: Processing metadata that might contain text info
            
        Returns:
            List of text region dictionaries
        """
        text_regions = []
        
        # Use metadata if available (from SVG processor, etc.)
        if 'text_elements' in metadata:
            # Create regions based on metadata
            for i, text in enumerate(metadata['text_elements']):
                # Estimate text region (simplified)
                region = {
                    'text': text,
                    'bbox': BoundingBox(
                        x=50 + (i * 150) % (image.width - 100),
                        y=30 + (i // 5) * 40,
                        width=min(len(text) * 8, 200),
                        height=20
                    ),
                    'estimated_size': 12,  # Default size
                    'is_bold': False
                }
                text_regions.append(region)
        
        # Fallback: detect text-like regions using image analysis
        if not text_regions:
            text_regions = self._detect_text_regions_visual(image)
        
        return text_regions
    
    def _detect_text_regions_visual(self, image: Image.Image) -> List[Dict[str, Any]]:
        """
        Detect text regions using visual analysis.
        
        Args:
            image: PIL Image to analyze
            
        Returns:
            List of detected text regions
        """
        # Convert to numpy array for analysis
        img_array = np.array(image)
        
        # Simple text detection based on color patterns
        # This is a simplified approach - production would use OCR
        text_regions = []
        
        # Look for rectangular regions with consistent colors (potential text)
        height, width = img_array.shape[:2]
        
        # Sample grid for potential text areas
        for y in range(0, height - 20, 30):
            for x in range(0, width - 50, 60):
                region_bbox = BoundingBox(x=x, y=y, width=50, height=20)
                
                # Extract region
                region = img_array[y:y+20, x:x+50]
                
                # Check if region looks like text (has contrast patterns)
                if self._looks_like_text_region(region):
                    text_regions.append({
                        'text': f'detected_text_{len(text_regions)}',
                        'bbox': region_bbox,
                        'estimated_size': 12,
                        'is_bold': False
                    })
        
        return text_regions[:10]  # Limit to avoid too many false positives
    
    def _looks_like_text_region(self, region: np.ndarray) -> bool:
        """
        Check if a region looks like it contains text.
        
        Args:
            region: Numpy array of image region
            
        Returns:
            True if region likely contains text
        """
        if region.size == 0:
            return False
        
        # Calculate variance in the region
        gray_region = np.mean(region, axis=2) if len(region.shape) == 3 else region
        variance = np.var(gray_region)
        
        # Text regions typically have moderate variance (not solid color, not noise)
        return 100 < variance < 2000
    
    def _analyze_text_contrast(self, image: Image.Image, text_region: Dict[str, Any]) -> None:
        """
        Analyze contrast for a specific text region.
        
        Args:
            image: PIL Image
            text_region: Text region information
        """
        bbox = text_region['bbox']
        
        # Extract text and background colors
        text_color, bg_color = self._extract_text_background_colors(image, bbox)
        
        # Calculate contrast ratio
        contrast_ratio = self._calculate_contrast_ratio(text_color, bg_color)
        
        # Determine appropriate threshold
        is_large_text = (text_region['estimated_size'] >= self.large_text_size or 
                        (text_region['is_bold'] and text_region['estimated_size'] >= self.bold_large_text_size))
        
        required_ratio = self.large_text_threshold if is_large_text else self.normal_text_threshold
        
        # Check if contrast meets requirements
        if contrast_ratio < required_ratio:
            severity = Severity.ERROR if contrast_ratio < required_ratio * 0.8 else Severity.WARNING
            
            self.add_violation(
                rule_id="wcag_contrast_normal" if not is_large_text else "wcag_contrast_large",
                severity=severity,
                current_value=contrast_ratio,
                expected_value=required_ratio,
                description=f"Text contrast ratio {contrast_ratio:.2f}:1 is below WCAG {'AA' if required_ratio >= 4.5 else 'A'} standard of {required_ratio}:1",
                location=bbox,
                category="accessibility"
            )
    
    def _analyze_graphical_contrast(self, image: Image.Image, element: Dict[str, Any]) -> None:
        """
        Analyze contrast for graphical elements.
        
        Args:
            image: PIL Image
            element: Graphical element information
        """
        bbox = element['bbox']
        
        # Extract element and background colors
        element_color, bg_color = self._extract_element_background_colors(image, bbox)
        
        # Calculate contrast ratio
        contrast_ratio = self._calculate_contrast_ratio(element_color, bg_color)
        
        # Check against graphical element threshold
        if contrast_ratio < self.graphical_threshold:
            severity = Severity.WARNING if contrast_ratio > self.graphical_threshold * 0.8 else Severity.ERROR
            
            self.add_violation(
                rule_id="wcag_contrast_graphical",
                severity=severity,
                current_value=contrast_ratio,
                expected_value=self.graphical_threshold,
                description=f"Graphical element contrast ratio {contrast_ratio:.2f}:1 is below WCAG standard of {self.graphical_threshold}:1",
                location=bbox,
                category="accessibility"
            )
    
    def _detect_graphical_elements(self, image: Image.Image) -> List[Dict[str, Any]]:
        """
        Detect graphical elements that need contrast checking.
        
        Args:
            image: PIL Image to analyze
            
        Returns:
            List of graphical element dictionaries
        """
        elements = []
        
        # Convert to numpy for analysis
        img_array = np.array(image)
        height, width = img_array.shape[:2]
        
        # Look for non-text graphical elements (shapes, lines, etc.)
        # This is simplified - production would use more sophisticated detection
        
        # Sample regions for potential graphical elements
        for y in range(0, height - 40, 50):
            for x in range(0, width - 40, 50):
                region_bbox = BoundingBox(x=x, y=y, width=40, height=40)
                
                # Extract region
                region = img_array[y:y+40, x:x+40]
                
                # Check if region contains graphical elements
                if self._looks_like_graphical_element(region):
                    elements.append({
                        'type': 'shape',
                        'bbox': region_bbox
                    })
        
        return elements[:5]  # Limit to avoid too many false positives
    
    def _looks_like_graphical_element(self, region: np.ndarray) -> bool:
        """
        Check if a region contains graphical elements.
        
        Args:
            region: Numpy array of image region
            
        Returns:
            True if region likely contains graphical elements
        """
        if region.size == 0:
            return False
        
        # Look for edges and shapes
        gray_region = np.mean(region, axis=2) if len(region.shape) == 3 else region
        
        # Calculate edge density
        edges = np.abs(np.diff(gray_region, axis=0)).sum() + np.abs(np.diff(gray_region, axis=1)).sum()
        edge_density = edges / region.size
        
        # Graphical elements typically have moderate edge density
        return 5 < edge_density < 50
    
    def _extract_text_background_colors(self, image: Image.Image, bbox: BoundingBox) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
        """
        Extract text and background colors from a region.
        
        Args:
            image: PIL Image
            bbox: Bounding box of text region
            
        Returns:
            Tuple of (text_color, background_color) as RGB tuples
        """
        # Extract region
        region = image.crop((bbox.x, bbox.y, bbox.x + bbox.width, bbox.y + bbox.height))
        
        # Convert to numpy array
        region_array = np.array(region)
        
        # Flatten to get all pixels
        pixels = region_array.reshape(-1, 3)
        
        # Find the two most common colors (assuming text and background)
        unique_colors, counts = np.unique(pixels, axis=0, return_counts=True)
        
        # Sort by frequency
        sorted_indices = np.argsort(counts)[::-1]
        
        if len(unique_colors) >= 2:
            # Most common is likely background, second most is likely text
            bg_color = tuple(unique_colors[sorted_indices[0]])
            text_color = tuple(unique_colors[sorted_indices[1]])
        else:
            # Fallback: use first color as text, white as background
            text_color = tuple(unique_colors[0]) if len(unique_colors) > 0 else (0, 0, 0)
            bg_color = (255, 255, 255)
        
        return text_color, bg_color
    
    def _extract_element_background_colors(self, image: Image.Image, bbox: BoundingBox) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
        """
        Extract element and background colors.
        
        Args:
            image: PIL Image
            bbox: Bounding box of element
            
        Returns:
            Tuple of (element_color, background_color) as RGB tuples
        """
        # Similar to text extraction but for graphical elements
        return self._extract_text_background_colors(image, bbox)
    
    def _calculate_contrast_ratio(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
        """
        Calculate WCAG contrast ratio between two colors.
        
        Args:
            color1: First color as RGB tuple
            color2: Second color as RGB tuple
            
        Returns:
            Contrast ratio (1:1 to 21:1)
        """
        # Calculate relative luminance for each color
        lum1 = self._calculate_relative_luminance(color1)
        lum2 = self._calculate_relative_luminance(color2)
        
        # Ensure lighter color is in numerator
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        
        # Calculate contrast ratio
        contrast_ratio = (lighter + 0.05) / (darker + 0.05)
        
        return contrast_ratio
    
    def _calculate_relative_luminance(self, color: Tuple[int, int, int]) -> float:
        """
        Calculate relative luminance according to WCAG formula.
        
        Args:
            color: RGB color tuple (0-255 values)
            
        Returns:
            Relative luminance (0-1)
        """
        # Convert to 0-1 range
        r, g, b = [c / 255.0 for c in color]
        
        # Apply gamma correction
        def gamma_correct(c):
            if c <= 0.03928:
                return c / 12.92
            else:
                return math.pow((c + 0.055) / 1.055, 2.4)
        
        r_linear = gamma_correct(r)
        g_linear = gamma_correct(g)
        b_linear = gamma_correct(b)
        
        # Calculate luminance using WCAG formula
        luminance = 0.2126 * r_linear + 0.7152 * g_linear + 0.0722 * b_linear
        
        return luminance
    
    def _analyze_overall_contrast(self, image: Image.Image) -> None:
        """
        Analyze overall image contrast characteristics.
        
        Args:
            image: PIL Image to analyze
        """
        # Convert to grayscale for overall contrast analysis
        gray_image = image.convert('L')
        gray_array = np.array(gray_image)
        
        # Calculate overall contrast metrics
        min_val = gray_array.min()
        max_val = gray_array.max()
        contrast_range = max_val - min_val
        
        # Check if image has sufficient overall contrast
        if contrast_range < 100:  # Low overall contrast
            self.add_violation(
                rule_id="overall_contrast",
                severity=Severity.WARNING,
                current_value=contrast_range,
                expected_value=100,
                description=f"Overall image contrast range {contrast_range} is low, may affect readability",
                category="visual_quality"
            )