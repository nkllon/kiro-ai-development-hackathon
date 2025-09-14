from datetime import datetime
from typing import Dict, List, Any

    def update_health_status(self, status: str):
        """Update module health status."""
        self.health_status = status
        self.last_updated = datetime.now().isoformat()

"""
Interfaces Services

This module was extracted from interfaces.py
as part of RM-DDD compliance refactoring.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncIterator
from .models import AnalysisResult, AnalysisContext, Delusion, RecoveryPlan, ValidationResult, ConsensusResult, MultiDimensionalResult, RecoveryAction, ValidationCertificate
from src.rm_ddd.core.health import ModuleHealth

