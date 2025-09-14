"""
Response Automation Core Processing

This module was extracted from response_automation_core.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path
from .models import CompetitorMove, ThreatLevel, CompetitiveAdvantage, SystematicMetrics, FMHImplementation, RequirementsDrivenEvidence
from .real_time_monitor import CompetitorAnnouncement
from src.competitive_launch.real_time_monitor import CompetitorAnnouncement, ThreatLevel
from src.rm_ddd.core.health import ModuleHealth


def _convert_announcement_to_move(self, announcement: CompetitorAnnouncement) -> CompetitorMove:
    """Convert competitor announcement to competitor move."""
    return CompetitorMove(competitor=announcement.competitor, move_type=self._classify_move_type(announcement.title), description=announcement.title, impact_level=announcement.threat_level, detected_at=announcement.published_at, source_url=announcement.url, keywords=announcement.keywords_matched)
