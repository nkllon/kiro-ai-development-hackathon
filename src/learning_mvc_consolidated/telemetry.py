#!/usr/bin/env python3
"""
🎯 TELEMETRY MODULE
=================
Telemetry event and page analysis classes for Learning MVC System.
Extracted from learning_mvc_system.py for better organization.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 2.0
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .page_types import PageType


@dataclass
class TelemetryEvent:
    """Telemetry event for comprehensive logging."""

    timestamp: float
    event_type: str
    page_url: str
    page_title: str
    data: Dict[str, Any]
    success: bool
    error: Optional[str] = None


@dataclass
class PageAnalysis:
    """Comprehensive page analysis."""

    url: str
    title: str
    page_type: PageType
    html_length: int
    form_count: int
    button_count: int
    input_count: int
    link_count: int
    image_count: int
    status_indicators: List[str]
    navigation_elements: List[Dict[str, Any]]
    interactive_elements: List[Dict[str, Any]]
    text_content: str
    meta_info: Dict[str, Any]
    analysis_timestamp: float


