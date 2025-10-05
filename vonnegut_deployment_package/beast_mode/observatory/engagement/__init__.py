"""
Live Dashboard Engagement System
================================

A comprehensive system for creating engaging, interactive, and emotionally intelligent
dashboard experiences that transform data visualization from passive consumption
to active engagement.

This module provides the core engagement framework that integrates with the
Beast Mode Observatory to deliver:

- Real-time data storytelling with contextual narratives
- Adaptive personality-driven dashboard behavior
- Intelligent attention management and progressive disclosure
- Multi-modal interaction with accessibility support
- GPU-accelerated animations and visual effects
- Collaborative engagement features
- Continuous learning and optimization

Author: Beast Mode Framework
Date: 2025-10-01
Version: 1.0.0
"""

# Import only what exists to avoid import errors
try:
    from .core.dashboard_engine import DashboardEngine
    from .core.interfaces import EngagementLevel, EngagementContext
    _core_available = True
except ImportError:
    _core_available = False

try:
    from .intelligence.data_storyteller import DataStorytellerEngine
    _storyteller_available = True
except ImportError:
    _storyteller_available = False

__version__ = "1.0.0"
__author__ = "Beast Mode Framework"

__all__ = []

if _core_available:
    __all__.extend(["DashboardEngine", "EngagementLevel", "EngagementContext"])

if _storyteller_available:
    __all__.append("DataStorytellerEngine")