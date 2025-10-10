"""
Tests for Productivity Triage Orchestrator
=========================================

Unit tests for the main Ghostbusters Productivity Triage orchestrator.

Author: Beast Mode Framework + Ghostbusters
Date: 2025-09-24
Purpose: Test the coordinator of coordinators!
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.beast_mode.ghostbusters.productivity_triage import (
    ProductivityTriageOrchestrator,
    TriageConfig,
    WorkArtifact,
    ArtifactType,
    DomainType,
    CompletionStatus,
    ReadinessStatus,
    ComplexityLevel,
    TriageStrategy,
)
from src.rm_ddd.core.unified_reflective_module import ModuleStatus, ModuleCapability


class TestProductivityTriageOrchestrator:
    """Test suite for ProductivityTriageOrchestrator"""
    
    def test_orchestrator_initialization(self):
        """Test that orchestrator initializes correctly"""
        orchestrator = ProductivityTriageOrchestrator()
        
        assert orchestrator.module_id == "ghostbusters_productivity_triage_orchestrator"
        assert orchestrator.config is not None
        assert orchestrator.current_operation is None
        assert len(orchestrator.triage_history) == 0
    
    def test_orchestrator_with_custom_config(self):
        """Test orchestrator initialization with custom config"""
        config = TriageConfig(
            scan_paths=["custom/path"],
            max_artifacts_to_process=500
        )
        
        orchestrator = ProductivityTriageOrchestrator(config)
        
        assert orchestrator.config.scan_paths == ["custom/path"]
        assert orchestrator.config.max_artifacts_to_process == 500
    
    def test_get_module_info(self):
        """Test ReflectiveModule get_module_info implementation"""
        orchestrator = ProductivityTriageOrchestrator()
        
        info = orchestrator.get_module_info()
        
        assert info["module_id"] == "ghostbusters_productivity_triage_orchestrator"
        assert info["module_name"] == "ProductivityTriageOrchestrator"
        assert info["version"] == "1.0.0"
        assert "capabilities" in info
        assert info["current_operation"] is None
        assert info["triage_operations_completed"] == 0
    
    def test_get_capabilities(self):
        """Test ReflectiveModule get_capabilities implementation"""
        orchestrator = ProductivityTriageOrchestrator()
        
        capabilities = orchestrator.get_capabilities()
        
        expected_capabilities = [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING,
        ]
        
        assert capabilities == expected_capabilities
    
    def test_get_health_status_healthy(self):
        """Test health status when orchestrator is healthy"""
        config = TriageConfig(scan_paths=["src/"])
        orchestrator = ProductivityTriageOrchestrator(config)
        
        health = orchestrator.get_health_status()
        
        assert health.module_id == "ghostbusters_productivity_triage_orchestrator"
        assert health.status == ModuleStatus.HEALTHY
        assert health.health_score == 1.0
        assert len(health.issues) == 0
    
    def test_get_health_status_unhealthy(self):
        """Test health status when orchestrator has issues"""
        # Create orchestrator with valid config first
        orchestrator = ProductivityTriageOrchestrator()
        
        # Then modify config to create unhealthy state
        orchestrator.config.scan_paths = []
        
        health = orchestrator.get_health_status()
        
        assert health.status in [ModuleStatus.WARNING, ModuleStatus.ERROR]
        assert health.health_score < 1.0
        assert "No scan paths configured" in health.issues
    
    def test_graceful_degradation(self):
        """Test graceful degradation functionality"""
        orchestrator = ProductivityTriageOrchestrator()
        
        result = orchestrator.graceful_degradation()
        
        assert result.success is True
        assert ModuleCapability.DATA_PROCESSING in result.degraded_capabilities
        assert ModuleCapability.CORE_FUNCTIONALITY in result.remaining_capabilities
    
    def test_assess_productivity_explosion_empty_workspace(self):
        """Test assessment with empty workspace"""
        orchestrator = ProductivityTriageOrchestrator()
        config = TriageConfig()
        
        # Mock the content discovery to return empty results
        with patch.object(orchestrator, '_initialize_content_discovery'):
            mock_discovery = Mock()
            mock_discovery.scan_workspace.return_value = []
            orchestrator._content_discovery = mock_discovery
            
            assessment = orchestrator.assess_productivity_explosion(config)
            
            assert assessment.total_artifacts == 0
            assert len(assessment.domains_affected) == 0
            assert assessment.integration_complexity == ComplexityLevel.LOW
            assert assessment.recommended_strategy == TriageStrategy.SYSTEMATIC_INTEGRATION
    
    def test_assess_productivity_explosion_with_artifacts(self):
        """Test assessment with multiple artifacts"""
        orchestrator = ProductivityTriageOrchestrator()
        config = TriageConfig()
        
        # Create mock artifacts
        artifacts = [
            WorkArtifact(
                path="src/test1.py",
                artifact_type=ArtifactType.CODE,
                domain=DomainType.TASK_QUEUE,
                completion_status=CompletionStatus.COMPLETE,
                integration_readiness=ReadinessStatus.READY
            ),
            WorkArtifact(
                path="src/test2.py", 
                artifact_type=ArtifactType.CODE,
                domain=DomainType.MCP_INTEGRATIONS,
                completion_status=CompletionStatus.PARTIAL,
                integration_readiness=ReadinessStatus.NEEDS_TESTS
            ),
        ]
        
        # Mock the content discovery
        with patch.object(orchestrator, '_initialize_content_discovery'):
            mock_discovery = Mock()
            mock_discovery.scan_workspace.return_value = artifacts
            orchestrator._content_discovery = mock_discovery
            
            assessment = orchestrator.assess_productivity_explosion(config)
            
            assert assessment.total_artifacts == 2
            assert DomainType.TASK_QUEUE in assessment.domains_affected
            assert DomainType.MCP_INTEGRATIONS in assessment.domains_affected
            assert assessment.completion_distribution[CompletionStatus.COMPLETE] == 1
            assert assessment.completion_distribution[CompletionStatus.PARTIAL] == 1
            assert assessment.readiness_distribution[ReadinessStatus.READY] == 1
            assert assessment.readiness_distribution[ReadinessStatus.NEEDS_TESTS] == 1
    
    def test_create_integration_plan(self):
        """Test integration plan creation"""
        orchestrator = ProductivityTriageOrchestrator()
        
        # Create mock assessment
        from src.beast_mode.ghostbusters.productivity_triage.models import ExplosionAssessment
        assessment = ExplosionAssessment(
            total_artifacts=5,
            domains_affected=[DomainType.TASK_QUEUE],
            integration_complexity=ComplexityLevel.MEDIUM,
            recommended_strategy=TriageStrategy.SYSTEMATIC_INTEGRATION
        )
        
        plan = orchestrator.create_integration_plan(assessment)
        
        assert plan.plan_id.startswith("plan_")
        assert isinstance(plan.estimated_duration, timedelta)
    
    def test_execute_integration(self):
        """Test integration execution"""
        orchestrator = ProductivityTriageOrchestrator()
        
        # Create mock integration plan
        from src.beast_mode.ghostbusters.productivity_triage.models import IntegrationPlan
        plan = IntegrationPlan(
            plan_id="test_plan",
            commit_groups=[],
            execution_order=[],
            quality_checkpoints=[],
            rollback_points=[]
        )
        
        results = orchestrator.execute_integration(plan)
        
        # For now, should return empty results (mock implementation)
        assert isinstance(results, list)
    
    def test_complexity_assessment(self):
        """Test integration complexity assessment logic"""
        orchestrator = ProductivityTriageOrchestrator()
        
        # Test different artifact counts
        assert orchestrator._assess_integration_complexity([]) == ComplexityLevel.LOW
        
        # Create artifacts for testing
        artifacts_5 = [Mock() for _ in range(5)]
        assert orchestrator._assess_integration_complexity(artifacts_5) == ComplexityLevel.LOW
        
        artifacts_25 = [Mock() for _ in range(25)]
        assert orchestrator._assess_integration_complexity(artifacts_25) == ComplexityLevel.MEDIUM
        
        artifacts_75 = [Mock() for _ in range(75)]
        assert orchestrator._assess_integration_complexity(artifacts_75) == ComplexityLevel.HIGH
        
        artifacts_150 = [Mock() for _ in range(150)]
        assert orchestrator._assess_integration_complexity(artifacts_150) == ComplexityLevel.CRITICAL
    
    def test_strategy_recommendation(self):
        """Test triage strategy recommendation logic"""
        orchestrator = ProductivityTriageOrchestrator()
        
        # Test different complexity levels
        artifacts = [Mock()]
        
        strategy = orchestrator._recommend_triage_strategy(artifacts, ComplexityLevel.LOW)
        assert strategy == TriageStrategy.SYSTEMATIC_INTEGRATION
        
        strategy = orchestrator._recommend_triage_strategy(artifacts, ComplexityLevel.MEDIUM)
        assert strategy == TriageStrategy.SYSTEMATIC_INTEGRATION
        
        strategy = orchestrator._recommend_triage_strategy(artifacts, ComplexityLevel.HIGH)
        assert strategy == TriageStrategy.SELECTIVE_INTEGRATION
        
        strategy = orchestrator._recommend_triage_strategy(artifacts, ComplexityLevel.CRITICAL)
        assert strategy == TriageStrategy.EMERGENCY_PRESERVATION
    
    def test_critical_issues_identification(self):
        """Test identification of critical issues"""
        orchestrator = ProductivityTriageOrchestrator()
        
        artifacts = [
            WorkArtifact(
                path="broken.py",
                artifact_type=ArtifactType.CODE,
                domain=DomainType.TASK_QUEUE,
                completion_status=CompletionStatus.BROKEN,
                integration_readiness=ReadinessStatus.NOT_READY
            ),
            WorkArtifact(
                path="conflict.py",
                artifact_type=ArtifactType.CODE,
                domain=DomainType.MCP_INTEGRATIONS,
                completion_status=CompletionStatus.COMPLETE,
                integration_readiness=ReadinessStatus.HAS_CONFLICTS
            ),
        ]
        
        issues = orchestrator._identify_critical_issues(artifacts)
        
        assert "1 broken artifacts detected" in issues
        assert "1 artifacts have conflicts" in issues
    
    def test_opportunities_identification(self):
        """Test identification of opportunities"""
        orchestrator = ProductivityTriageOrchestrator()
        
        artifacts = [
            WorkArtifact(
                path="ready.py",
                artifact_type=ArtifactType.CODE,
                domain=DomainType.TASK_QUEUE,
                completion_status=CompletionStatus.COMPLETE,
                integration_readiness=ReadinessStatus.READY
            ),
            WorkArtifact(
                path="complete.py",
                artifact_type=ArtifactType.CODE,
                domain=DomainType.MCP_INTEGRATIONS,
                completion_status=CompletionStatus.COMPLETE,
                integration_readiness=ReadinessStatus.NEEDS_TESTS
            ),
        ]
        
        opportunities = orchestrator._identify_opportunities(artifacts)
        
        assert "1 artifacts ready for immediate integration" in opportunities
        assert "2 complete implementations available" in opportunities


if __name__ == "__main__":
    pytest.main([__file__])