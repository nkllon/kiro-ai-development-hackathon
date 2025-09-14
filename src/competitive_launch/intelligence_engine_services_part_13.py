from datetime import datetime
from typing import Dict, List, Any

    def update_health_status(self, status: str):
        """Update module health status."""
        self.health_status = status
        self.last_updated = datetime.now().isoformat()

"""
Intelligence Engine Services

This module was extracted from intelligence_engine.py
as part of RM-DDD compliance refactoring.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging
from .models import MarketConditions, CompetitiveThreat, CompetitorMove, MarketTrend, CustomerFeedback, CompetitiveAdvantage, SystematicMetrics, FMHImplementation, AccountabilityImplementation, RequirementsDrivenEvidence, TimeToMarketAdvantage, ThreatLevel
from src.rm_ddd.core.health import ModuleHealth

