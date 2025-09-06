"""
Git Providers Module

This module contains all git provider implementations following the
progressive enhancement pattern.
"""

from .git_provider import (
    GitProvider, 
    GitOperationResult, 
    GitOperationStatus,
    BranchInfo, 
    CommitInfo,
    FileStatus,
    MergeConflict
)

__all__ = [
    "GitProvider",
    "GitOperationResult", 
    "GitOperationStatus",
    "BranchInfo",
    "CommitInfo", 
    "FileStatus",
    "MergeConflict"
]