"""
Bypass Detector Processing

This module was extracted from bypass_detector.py
as part of RM-DDD compliance refactoring.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from ..models import Decision, Actor, BypassAlert, EscalationAction, GovernanceIntervention, InterventionType
from ..models import TriggerEvent
from ..models import EscalationStep
from ..models import SuccessCriterion
from ..models import RollbackPlan
from src.rm_ddd.core.health import ModuleHealth


def _detect_process_circumvention(self, actor_id: str, governance_events: List[Dict]) -> Optional[BypassPattern]:
    """Detect attempts to circumvent established processes."""
    circumvention_events = [event for event in governance_events if event.get('event_type') in ['process_skip', 'alternative_path', 'unauthorized_access']]
    if len(circumvention_events) >= 3:
        return BypassPattern(pattern_type='process_circumvention', severity='high', evidence=[f'{len(circumvention_events)} process circumvention attempts', 'Multiple alternative paths used to avoid governance', 'Pattern suggests systematic process avoidance'], confidence=0.8, first_detected=datetime.now() - timedelta(days=1), last_detected=datetime.now())
    return None
