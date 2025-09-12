"""
Orchestrator Core Core Validation

This module was extracted from orchestrator_core_core.py
as part of RM-DDD compliance refactoring.
"""

from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from pathlib import Path
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from .base import BaseOrchestrator, BaseAnalyzer, SafetyViolationError, AnalysisError
from .data_models import AnalysisResult, AnalysisStatus, AnalysisConfiguration
from .safety import get_safety_manager, is_safe_to_proceed, SafetyStatus
from .workflow import WorkflowCoordinator, AggregatedResult

def validate_analyzer_configuration(self, analyzer_name: str) -> Dict[str, Any]:
    """
        Validate configuration of a specific analyzer
        
        Args:
            analyzer_name: Name of analyzer to validate
            
        Returns:
            Dict containing validation results
        """
    if analyzer_name not in self.registered_analyzers:
        return {'analyzer_name': analyzer_name, 'is_valid': False, 'error': 'Analyzer not registered'}
    analyzer = self.registered_analyzers[analyzer_name]
    try:
        is_healthy = analyzer.is_healthy()
        status = analyzer.get_module_status()
        safety_status = analyzer.safety_manager.get_safety_status()
        return {'analyzer_name': analyzer_name, 'is_valid': True, 'is_healthy': is_healthy, 'status': status, 'safety_validated': safety_status.is_safe, 'configuration_valid': True}
    except Exception as e:
        return {'analyzer_name': analyzer_name, 'is_valid': False, 'error': f'Configuration validation failed: {str(e)}'}
