from datetime import datetime
from typing import Dict, List, Any

    def update_health_status(self, status: str):
        """Update module health status."""
        self.health_status = status
        self.last_updated = datetime.now().isoformat()

"""
Report Generator Core Core Core

This module was extracted from report_generator_core_core.py
as part of RM-DDD compliance refactoring.
"""

"""
Report_Generator - Consolidated Interface Definition

This file was consolidated from the core_core_core refactoring mess.
All duplicate definitions have been removed and this is now the single
authoritative source for report_generator.

Consolidated from: /Users/lou/kiro-2/kiro-ai-development-hackathon/src/beast_mode/compliance/reporting/report_generator_core_core_core.py
Consolidation date: 2025-09-13T10:15:07.455006
"""



from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import json
from ..interfaces import ComplianceReporter
from ..models import ComplianceAnalysisResult, ComplianceIssue, IssueSeverity, ComplianceIssueType, RemediationStep, Phase2ValidationResult

@dataclass