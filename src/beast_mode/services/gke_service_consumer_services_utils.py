"""
Gke Service Consumer Services Utils

This module was extracted from gke_service_consumer_services.py
as part of RM-DDD compliance refactoring.
"""

import time
import json
import uuid
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from ..core.reflective_module import ReflectiveModule, HealthStatus
from ..orchestration.pdca_orchestrator import PDCAOrchestrator
from ..intelligence.registry_intelligence_engine import RegistryIntelligenceEngine
from ..tools.makefile_health_manager import MakefileHealthManager
from ..testing.comprehensive_test_suite import ComprehensiveTestSuite

def request_tool_health_management_service(self, team_id: str, tool_context: Dict[str, Any], health_check_scope: str='comprehensive') -> ServiceResponse:
    """
        Provide tool health management service for GKE tool fixing capabilities
        Implements UC-09: Tool health management service for systematic tool repair
        """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    try:
        if team_id not in self.registered_teams:
            raise ValueError(f'Team {team_id} not registered')
        if self.service_status[ServiceType.TOOL_HEALTH_MANAGEMENT] == ServiceStatus.UNAVAILABLE:
            raise RuntimeError('Tool health management service currently unavailable')
        service_request = ServiceRequest(request_id=request_id, service_type=ServiceType.TOOL_HEALTH_MANAGEMENT, gke_team_id=team_id, project_context=tool_context, parameters={'health_check_scope': health_check_scope}, timestamp=datetime.now())
        self.active_requests[request_id] = service_request
        health_assessment = self.makefile_health_manager.perform_comprehensive_health_check(project_path=tool_context.get('project_path', '.'), check_scope=health_check_scope)
        repair_results = []
        if health_assessment['issues_found']:
            repair_results = self.makefile_health_manager.execute_systematic_repairs(health_assessment['issues'], systematic_only=True)
        health_report = self._generate_tool_health_report(health_assessment, repair_results, team_id)
        execution_time = int((time.time() - start_time) * 1000)
        response = ServiceResponse(request_id=request_id, service_type=ServiceType.TOOL_HEALTH_MANAGEMENT, status='success', result={'health_assessment': health_assessment, 'repair_results': repair_results, 'health_report': health_report, 'systematic_repairs_only': True, 'prevention_recommendations': self._generate_prevention_recommendations(health_assessment)}, execution_time_ms=execution_time, timestamp=datetime.now(), recommendations=self._generate_tool_health_recommendations(team_id, health_assessment))
        self._update_service_metrics('success', execution_time)
        del self.active_requests[request_id]
        return response
    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        self._update_service_metrics('error', execution_time)
        if request_id in self.active_requests:
            del self.active_requests[request_id]
        return ServiceResponse(request_id=request_id, service_type=ServiceType.TOOL_HEALTH_MANAGEMENT, status='error', result={}, execution_time_ms=execution_time, timestamp=datetime.now(), error_message=str(e), recommendations=['Verify tool context', 'Check project path', 'Review tool configuration'])

def _generate_tool_health_report(self, health_assessment: Dict[str, Any], repair_results: List[Dict[str, Any]], team_id: str) -> Dict[str, Any]:
    """Generate comprehensive tool health report"""
    return {'overall_health_score': health_assessment.get('health_score', 0.8), 'issues_resolved': len([r for r in repair_results if r.get('success', False)]), 'systematic_repairs_applied': len(repair_results), 'prevention_patterns_identified': health_assessment.get('prevention_patterns', []), 'team_specific_recommendations': self._get_team_tool_recommendations(team_id), 'health_trend': 'improving' if len(repair_results) > 0 else 'stable'}

def _generate_tool_health_recommendations(self, team_id: str, health_assessment: Dict[str, Any]) -> List[str]:
    """Generate tool health specific recommendations"""
    recommendations = ['Apply systematic approach to tool maintenance', 'Document tool health patterns for team knowledge']
    team_profile = self.registered_teams.get(team_id)
    if team_profile and 'makefile' not in team_profile.preferred_tools:
        recommendations.append('Consider Makefile adoption for systematic build processes')
    return recommendations

def _get_team_tool_recommendations(self, team_id: str) -> List[str]:
    """Get team-specific tool recommendations"""
    team_profile = self.registered_teams.get(team_id)
    if not team_profile:
        return ['Implement systematic tool health monitoring']
    recommendations = ['Maintain systematic approach to tool management']
    if 'docker' in team_profile.preferred_tools:
        recommendations.append('Consider container health monitoring integration')
    if 'kubernetes' in team_profile.preferred_tools:
        recommendations.append('Implement K8s resource health validation')
    return recommendations

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

