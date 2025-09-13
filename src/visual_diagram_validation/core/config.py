"""Configuration models for the Visual Diagram Quality Validation Pipeline."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class ValidationConfig:
    """Configuration for quality validation rules and thresholds."""
    audience_mode: str = "general"  # "executive", "technical", "general"
    contrast_threshold: float = 4.5  # WCAG AA standard
    max_colors: int = 7
    min_font_size: int = 12  # points
    enable_model_checking: bool = False
    brand_colors: Optional[List[str]] = None
    
    # Audience-specific overrides
    executive_min_font_size: int = 14
    executive_max_elements: int = 10
    technical_max_elements: int = 50
    
    # Rule enablement flags
    enable_contrast_check: bool = True
    enable_color_palette_check: bool = True
    enable_typography_check: bool = True
    enable_layout_check: bool = True
    enable_symbol_check: bool = True
    
    def get_effective_min_font_size(self) -> int:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Get minimum font size based on audience mode."""
        if self.audience_mode == "executive":
            return self.executive_min_font_size
        return self.min_font_size
    
    def get_effective_max_elements(self) -> int:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Get maximum element count based on audience mode."""
        if self.audience_mode == "executive":
            return self.executive_max_elements
        elif self.audience_mode == "technical":
            return self.technical_max_elements
        return 25  # general default


@dataclass
class RenderingConfig:
    """Configuration for image rendering and processing."""
    output_dpi: int = 300
    retina_scale: float = 2.0
    max_width: int = 4096
    max_height: int = 4096
    timeout_seconds: int = 30
    
    # Format-specific settings
    svg_background_color: str = "white"
    pdf_page_number: int = 1  # which page to process for multi-page PDFs
    html_viewport_width: int = 1920
    html_viewport_height: int = 1080
    
    # Performance settings
    enable_caching: bool = True
    max_cache_size_mb: int = 500
    parallel_processing: bool = True
    max_workers: int = 4