"""
Analysis-specific test fixtures
Provides fixtures for RM-RDI analysis system testing
"""

import pytest
from unittest.mock import Mock
from datetime import datetime


@pytest.fixture
def mock_analyzer():
    """Mock analyzer for testing"""
    analyzer = Mock()
    analyzer.analyzer_name = "test_analyzer"
    analyzer.analysis_in_progress = False
    analyzer.analysis_start_time = None
    analyzer.is_healthy.return_value = True
    analyzer.get_module_status.return_value = {
        "module_name": "rm_rdi_analyzer_test_analyzer",
        "analyzer_name": "test_analyzer",
        "status": "operational",
        "analysis_in_progress": False,
        "safety_status": {
            "is_safe": True,
            "resource_usage": {"cpu_percent": 25.0, "memory_mb": 100.0},
            "violations": [],
            "kill_switch_armed": True
        },
        "guarantees": [
            "READ_ONLY_OPERATIONS",
            "RESOURCE_LIMITED",
            "EMERGENCY_SHUTDOWN_AVAILABLE",
            "CANNOT_IMPACT_EXISTING_SYSTEMS"
        ]
    }
    analyzer.get_health_indicators.return_value = {
        "analyzer_health": {
            "analyzer_name": "test_analyzer",
            "analysis_in_progress": False,
            "last_analysis": None
        },
        "safety_health": {
            "safety_systems_operational": True,
            "resource_usage": {"cpu_percent": 25.0, "memory_mb": 100.0},
            "safety_violations": [],
            "emergency_shutdown_available": True
        }
    }
    return analyzer


@pytest.fixture
def mock_analysis_result():
    """Mock analysis result for testing"""
    from src.beast_mode.analysis.rm_rdi.data_models import AnalysisResult, AnalysisStatus
    
    return AnalysisResult(
        analysis_id="test_analysis_001",
        timestamp=datetime.now(),
        analysis_types=["test_analysis"],
        status=AnalysisStatus.COMPLETED,
        findings=["Test finding 1", "Test finding 2"],
        metrics={"test_metric": 0.85},
        priority=1,
        confidence=0.9,
        operator_notes=[
            "This analysis is READ-ONLY and cannot impact existing systems",
            "Use 'make analysis-kill' for emergency shutdown",
            "Analysis can be safely ignored or disabled at any time"
        ]
    )


@pytest.fixture
def mock_orchestrator():
    """Mock analysis orchestrator for testing"""
    orchestrator = Mock()
    orchestrator.orchestrator_name = "test_orchestrator"
    orchestrator.registered_analyzers = {}
    orchestrator.active_analyses = {}
    orchestrator.is_healthy.return_value = True
    orchestrator.get_module_status.return_value = {
        "module_name": "rm_rdi_orchestrator_test_orchestrator",
        "orchestrator_name": "test_orchestrator",
        "status": "operational",
        "registered_analyzers": [],
        "active_analyses": [],
        "safety_status": {
            "is_safe": True,
            "resource_usage": {"cpu_percent": 25.0, "memory_mb": 100.0},
            "violations": [],
            "kill_switch_armed": True
        }
    }
    return orchestrator


@pytest.fixture
def sample_workflow_config():
    """Sample workflow configuration for testing"""
    return {
        "workflow_id": "test_workflow",
        "analyzers": ["analyzer1", "analyzer2"],
        "execution_mode": "parallel",
        "timeout_seconds": 300,
        "safety_constraints": {
            "max_memory_mb": 1024,
            "max_cpu_percent": 50
        }
    }


@pytest.fixture
def mock_workflow_coordinator():
    """Mock workflow coordinator for testing"""
    coordinator = Mock()
    coordinator.create_workflow_plan.return_value = {
        "workflow_id": "test_workflow",
        "execution_plan": ["step1", "step2"],
        "estimated_duration": 120,
        "safety_validated": True
    }
    coordinator.execute_workflow.return_value = Mock(
        workflow_id="test_workflow",
        status="completed",
        results=[]
    )
    return coordinator