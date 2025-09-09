"""
Presentation components for the Hackathon Demo Framework.

This module provides systematic demo script generation, presentation materials
creation, and judge engagement optimization for hackathon presentations.
"""

from .demo_script_generator import DemoScriptGenerator
from .presentation_materials import PresentationMaterialsCreator
from .timing_optimizer import DemoTimingOptimizer

__all__ = [
    "DemoScriptGenerator",
    "PresentationMaterialsCreator",
    "DemoTimingOptimizer"
]