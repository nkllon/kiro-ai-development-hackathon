"""
Git Provider Validation

This module was extracted from git_provider.py
as part of RM-DDD compliance refactoring.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

def validate_branch_name(self, name: str) -> bool:
    """
        Validate branch name according to git rules.
        
        Args:
            name: Branch name to validate
            
        Returns:
            True if valid, False otherwise
        """
    if not name or len(name) == 0:
        return False
    if any((c.isspace() for c in name)):
        return False
    invalid_chars = ['~', '^', ':', '?', '*', '[', '\\']
    if any((char in name for char in invalid_chars)):
        return False
    if '..' in name:
        return False
    if '//' in name:
        return False
    if name.startswith('.') or name.endswith('.'):
        return False
    if name.startswith('-') or name.endswith('/'):
        return False
    if name.strip() == '':
        return False
    return True
