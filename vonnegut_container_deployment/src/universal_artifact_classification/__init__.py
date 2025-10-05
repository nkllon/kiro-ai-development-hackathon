"""
Universal Artifact Classification - The Adaptive Babel Fish

A learning, adaptive artifact classification system that understands artifacts
in their native form without transformation or metadata patching.
"""

from .adaptive_babel_fish import AdaptiveBabelFish
from .models import ArtifactUnderstanding, ClassificationResult, LearningEvent

__all__ = [
    "AdaptiveBabelFish",
    "ArtifactUnderstanding", 
    "ClassificationResult",
    "LearningEvent"
]