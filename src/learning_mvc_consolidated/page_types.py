#!/usr/bin/env python3
"""
🎯 PAGE TYPES MODULE
==================
Page type enumeration for Learning MVC System.
Extracted from learning_mvc_system.py for better organization.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 2.0
"""

from enum import Enum


class PageType(Enum):
    """Enumeration of detected page types."""

    UNKNOWN = "unknown"
    LOGIN = "login"
    AUTHENTICATION = "authentication"
    PROJECT_OVERVIEW = "project_overview"
    PROJECT_DETAILS = "project_details"
    ADDITIONAL_INFO = "additional_info"
    SUBMISSION = "submission"
    DASHBOARD = "dashboard"
    ERROR = "error"
    LOADING = "loading"

