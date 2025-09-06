"""
GitKraken API Integration Module

This module provides a progressive enhancement approach to git operations,
offering GitKraken API features for licensed users while maintaining full
functionality for open source developers using standard git.

Key Components:
- GitProvider: Abstract interface for git operations
- StandardGitProvider: Baseline git functionality using command-line git
- GitKrakenProvider: Enhanced functionality using GitKraken API
- GitOperationsManager: Unified interface with automatic provider selection
"""

from .providers.git_provider import GitProvider, GitOperationResult, BranchInfo
from .providers.standard_git_provider import StandardGitProvider

# These will be implemented in subsequent tasks
# from .providers.gitkraken_provider import GitKrakenProvider
# from .managers.git_operations_manager import GitOperationsManager
# from .config.git_configuration_manager import GitConfigurationManager
# from .detection.license_detector import LicenseDetector

__version__ = "1.0.0"
__author__ = "Beast Mode Framework"

__all__ = [
    "GitProvider",
    "GitOperationResult", 
    "BranchInfo",
    "StandardGitProvider",
    # These will be added in subsequent tasks:
    # "GitKrakenProvider", 
    # "GitOperationsManager",
    # "GitConfigurationManager",
    # "LicenseDetector"
]