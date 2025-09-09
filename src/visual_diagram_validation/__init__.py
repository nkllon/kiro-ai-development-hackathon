"""
Visual Diagram Quality Validation Pipeline

A systematic, deterministic pipeline for validating and improving diagram quality
across multiple formats (SVG, PDF, Mermaid, HTML/CSS) with real-time feedback.
"""

__version__ = "0.1.0"
__author__ = "Beast Mode Framework"

from .core.models import PNGImage, QualityViolation, Recommendation, QualityReport
from .core.interfaces import QualityAnalyzer, ProcessorInterface
from .core.config import ValidationConfig, RenderingConfig

__all__ = [
    "PNGImage",
    "QualityViolation", 
    "Recommendation",
    "QualityReport",
    "QualityAnalyzer",
    "ProcessorInterface",
    "ValidationConfig",
    "RenderingConfig"
]