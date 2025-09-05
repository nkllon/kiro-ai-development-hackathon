"""
Git analysis components for compliance checking.

This module provides git repository analysis capabilities for identifying
commits, file changes, and mapping changes to task completions.
"""

from .analyzer import GitAnalyzer
from .file_change_detector import FileChangeDetector, FileChange, TaskMapping, AdvancedFileChangeAnalysis

__all__ = ["GitAnalyzer", "FileChangeDetector", "FileChange", "TaskMapping", "AdvancedFileChangeAnalysis"]