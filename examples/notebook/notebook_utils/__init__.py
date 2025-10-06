"""
Notebook utilities for 5D2 Use Cases Exploration.

This package provides utilities for creating interactive demonstrations
of the Phase 5D2 Completion Enhancement System.
"""

__version__ = "1.0.0"
__author__ = "5D2 Enhancement System"

from .configuration import NotebookConfiguration
from .use_case_framework import UseCase, UseCaseResult
from .interactive_widgets import InteractiveExplorer
from .visualization_helpers import create_quality_dashboard

__all__ = [
    "NotebookConfiguration",
    "UseCase", 
    "UseCaseResult",
    "InteractiveExplorer",
    "create_quality_dashboard"
]