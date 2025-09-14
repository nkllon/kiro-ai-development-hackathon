from datetime import datetime
from typing import Dict, List, Any

    def update_health_status(self, status: str):
        """Update module health status."""
        self.health_status = status
        self.last_updated = datetime.now().isoformat()

"""
Controller Handlers

This module was extracted from controller.py
as part of RM-DDD compliance refactoring.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from .models import HackathonConfig, DemoPackage, DemoScript, ValidationResult, TechnicalAssessment, ComplianceAssessment, DemoEnvironment, SystematicEvidence, JudgeMaterials, PresentationMetrics, DEVPOST_HACKATHON_TEMPLATE, MLH_HACKATHON_TEMPLATE
from src.beast_mode.testing.test_orchestrator import BeastModeTestOrchestrator
from src.beast_mode.analysis.rca_analyzer import RCAPatternAnalyzer
from src.beast_mode.compliance.rdi_validator import RDIChainValidator
from .models import IsolationLevel
