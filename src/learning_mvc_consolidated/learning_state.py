#!/usr/bin/env python3
"""
🎯 LEARNING STATE MODULE
======================
Learning state management for Learning MVC System.
Extracted from learning_mvc_system.py for better organization.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 2.0
"""

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class LearningState:
    """Learning state for the system."""

    total_pages_analyzed: int
    successful_navigations: int
    failed_navigations: int
    discovered_patterns: Dict[str, Any]
    learned_selectors: Dict[str, List[str]]
    page_type_patterns: Dict[str, List[str]]
    button_patterns: Dict[str, List[str]]
    form_patterns: Dict[str, List[str]]


