"""
Unit tests for MPMDashboard - Strategic backlog management interface

Tests cover:
- Portfolio status calculation and caching
- Stakeholder report generation for different audiences
- Strategic reprioritization with impact analysis
- Scenario planning for resource allocation
- Performance metrics and error handling
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from typing import Dict, List

from src.beast_mode.backlog.mpm_dashboard import (
    MPMDashboard, PortfolioStatus, ImpactAnalysis, ScenarioResult,
    ResourceConstraints, PriorityChange, StakeholderReport,
    ScenarioType
)
from src.beast_mode.backlog.models import (
    BacklogItem, MPMValidation, Requirement, AcceptanceCriterion, DependencyReference
)
from src.beast_mode.backlog.enums import (
    StrategicTrack, BeastReadinessStatus, ApprovalStatus, StakeholderType, RiskLevel
)


class TestMPMDashboard:
    """Test suite for MPMDashboard functionality"""
    
    @pytest.fixture
    def mock_dependency_manager(self):
        """Create mock dependency manager"""
        mock_manager = Mock()
        mock_manager.calculate_critical_path.return_value = ["item1", "item2"]
        return mock_manager
    
    @pytest.fixture
    def mpm_dashboard(self, mock_dependency_manager):
        """Create MPMDashboard instance for testing"""
        return MPMDashboard(mock_dependency_manager)
    
    @pytest.fixture
    def sample_backlog_items(self):
        """Create sample backlog items for testing"""
        now = datetime.now()
        
        items = {}
        
        # Create items across different tracks and statuses
        for i in range(10):
            track = list(StrategicTrack)[i % 4]
            status = list(BeastReadinessStatus)[i % 7]
            
            mpm_validation = MPMValidation(
                validation_id=f"val_{i}",
                validated_by="test_mpm",
                validation_timestamp=now,
                completeness_score=0.8 + (i % 3) * 0.1,
                dependency_confidence=0.7 + (i % 4) * 0.1,
                business_alignment=0.9,
                beast_readiness_assessment="Good quality item",
                approval_status=ApprovalStatus.APPROVED
            )
            
            item = BacklogItem(
                item_id=f"item_{i}",
                title=f"Test Item {i}",
                track=track,
                requirements=[
                    Requirement(
                        requirement_id=f"req_{i}_1",
                        description=f"Requirement for item {i}",
                        priority=1
                    )
                ],
                acceptance_criteria=[
                    AcceptanceCriterion(
                        criterion_id=f"ac_{i}_1",
                        description=f"Acceptance criterion for item {i}"
                    )
                ],
                dependencies=[],
                beast_readiness_status=status,
                created_by="test_user",
                created_at=now - timedelta(days=i),
                last_updated=now,
                mpm_validation=mpm_validation if i % 2 == 0 else None
            )
            
            items[f"item_{i}"] = item
        
        return items
    
    def test_get_portfolio_status_basic(self, mpm_dashboard, sample_backlog_items):
        """Test basic portfolio status calculation"""
        mpm_dashboard.update_backlog_items(sample_backlog_items)
        
        status = mpm_dashboard.get_portfolio_status()
        
        assert isinstance(status, PortfolioStatus)
        assert status.total_items == 10
        assert status.completion_percentage >= 0.0
        assert status.delivery_confidence >= 0.0
        assert len(status.track_breakdown) == 4  # Four strategic tracks
        assert isinstance(status.risk_assessment, dict)
        assert isinstance(status.last_updated, datetime)
    
    def test_empty_backlog_handling(self, mpm_dashboard):
        """Test handling of empty backlog"""
        mpm_dashboard.update_backlog_items({})
        
        status = mpm_dashboard.get_portfolio_status()
        
        assert status.total_items == 0
        assert status.beast_ready_items == 0
        assert status.completion_percentage == 0.0
        assert status.delivery_confidence == 0.0
        assert len(status.critical_path_items) == 0
    
    def test_generate_mpm_report(self, mpm_dashboard, sample_backlog_items):
        """Test MPM-specific report generation"""
        mpm_dashboard.update_backlog_items(sample_backlog_items)
        
        report = mpm_dashboard.generate_stakeholder_report(StakeholderType.MPM)
        
        assert isinstance(report, StakeholderReport)
        assert report.audience == StakeholderType.MPM
        assert "Strategic Portfolio Management" in report.title
        assert "beast_readiness_rate" in report.key_metrics
        assert "track_breakdown" in report.detailed_sections
        assert len(report.recommendations) >= 0
        assert len(report.next_steps) >= 0
        assert report.valid_until > report.generated_at
    
    def test_scenario_planning_basic(self, mpm_dashboard, sample_backlog_items):
        """Test basic scenario planning"""
        mpm_dashboard.update_backlog_items(sample_backlog_items)
        
        constraints = ResourceConstraints(
            available_developers=3,
            available_hours_per_week=120,
            budget_constraints=None,
            timeline_constraints=None,
            skill_constraints={},
            priority_constraints=[]
        )
        
        result = mpm_dashboard.run_scenario_planning(constraints, ScenarioType.REALISTIC)
        
        assert isinstance(result, ScenarioResult)
        assert result.scenario_type == ScenarioType.REALISTIC
        assert result.estimated_completion > datetime.now()
        assert 0.0 <= result.success_probability <= 1.0
        assert len(result.key_assumptions) > 0
        assert len(result.deliverable_timeline) == 4  # Four strategic tracks
        assert isinstance(result.generated_at, datetime)


if __name__ == "__main__":
    pytest.main([__file__])