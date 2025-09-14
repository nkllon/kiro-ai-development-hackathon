from datetime import datetime
from typing import Dict, List, Any

    def update_health_status(self, status: str):
        """Update module health status."""
        self.health_status = status
        self.last_updated = datetime.now().isoformat()

"""
Security Core Core Core

This module was extracted from security_core_core.py
as part of RM-DDD compliance refactoring.
"""

"""
Security - Consolidated Interface Definition

This file was consolidated from the core_core_core refactoring mess.
All duplicate definitions have been removed and this is now the single
authoritative source for security.

Consolidated from: /Users/lou/kiro-2/kiro-ai-development-hackathon/src/ghostbusters/agents/security_core_core_core.py
Consolidation date: 2025-09-13T10:15:07.547410
"""



import re
import hashlib
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
import logging
from ..core.interfaces import GhostbustersExpertAgent
from ..core.models import AnalysisResult, AnalysisContext, Finding, Recommendation, FindingType, Severity, CodeLocation
import stat
import stat
import stat
from src.rm_ddd.core.health import ModuleHealth

