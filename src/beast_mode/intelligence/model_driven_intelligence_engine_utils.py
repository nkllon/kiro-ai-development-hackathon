"""
Model Driven Intelligence Engine Utils

This module was extracted from model_driven_intelligence_engine.py
as part of RM-DDD compliance refactoring.
"""

import time
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from ..core.reflective_module import ReflectiveModule, HealthStatus
from .registry_intelligence_engine import RegistryIntelligenceEngine
from src.rm_ddd.core.health import ModuleHealth


def get_domain_tools(self, domain: str='general') -> List[str]:
    """Get tools available for a specific domain"""
    try:
        domain_tools = {'build': ['build_tool', 'test_runner', 'deployment_tool'], 'analysis': ['static_analyzer', 'quality_checker', 'metrics_collector'], 'orchestration': ['workflow_engine', 'task_scheduler', 'resource_manager'], 'intelligence': ['model_analyzer', 'decision_engine', 'pattern_matcher'], 'general': ['systematic_analyzer', 'model_validator', 'quality_checker']}
        tools = domain_tools.get(domain.lower(), domain_tools['general'])
        if hasattr(self.registry_engine, 'get_domain_specific_tools'):
            registry_tools = self.registry_engine.get_domain_specific_tools(domain)
            tools.extend(registry_tools)
        return tools
    except Exception as e:
        self.logger.error(f'Domain tool retrieval failed: {e}')
        return ['fallback_tool']
