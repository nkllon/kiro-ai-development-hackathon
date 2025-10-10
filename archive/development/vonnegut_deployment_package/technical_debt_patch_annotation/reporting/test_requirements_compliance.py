#!/usr/bin/env python3
"""
Requirements Compliance Tests for Technical Debt Patch Annotation Reporting System

This test suite validates that the reporting and dashboard system meets all
specified requirements from the technical debt patch annotation specification.

Requirements tested: 8.1, 8.2, 8.3, 8.4, 8.5
"""

import unittest
from datetime import datetime, timedelta
from typing import List
from unittest.mock import Mock, patch

from ..core.models import PatchAnnotation, DebtLevel, BypassType
from .dashboard import (
    PatchDashboard, ReportGenerator, ReportFormat, TimeRange,
    InventoryReport, TrendAnalysis, ExecutiveDashboard, DashboardMetrics
)


class TestRequirement81InventoryReports(unittest.TestCase):
    """
    Test Requirement 8.1: WHEN reports are requested THEN they SHALL show 
    current patch inventory by component and severity
    """
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ReportGenerator()
        self.patches = self._create_test_patches()
    
    def _create_test_patches(self) -> List[PatchAnnotation]:
        """Create test patches with various components and severities."""
        patches = []
        
        # Component A - Critical and High patches
        patches.append(PatchAnnotation(
            reason="Critical security issue",
            upstream_issue="SEC-001",
            cleanup_task="Fix security vulnerability",
            debt_level=DebtLevel.CRITICAL,
            component="component_a",
            bypass_type=BypassType.SECURITY
        ))
        
        patches.append(PatchAnnotation(
            reason="High priority performance issue",
            upstream_issue="PERF-001",
            cleanup_task="Optimize performance",
            debt_level=DebtLevel.HIGH,
            component="component_a",
            bypass_type=BypassType.PERFORMANCE
        ))
        
        # Component B - Medium and Low patches
        patches.append(PatchAnnotation(
            reason="Medium integration issue",
            upstream_issue="INT-001",
            cleanup_task="Fix integration",
            debt_level=DebtLevel.MEDIUM,
            component="component_b",
            bypass_type=BypassType.INTEGRATION
        ))
        
        patches.append(PatchAnnotation(
            reason="Low priority cleanup",
            upstream_issue="CLEAN-001",
            cleanup_task="Code cleanup",
            debt_level=DebtLevel.LOW,
            component="component_b",
            bypass_type=BypassType.ARCHITECTURE
        ))
        
        return patches
    
    def test_inventory_report_shows_component_distribution(self):
        """Test that inventory report shows patches by component."""
        report = self.generator.generate_inventory_report(self.patches)
        
        # Verify report structure
        self.assertIsInstance(report, InventoryReport)
        self.assertEqual(report.total_patches, len(self.patches))
        
        # Verify component distribution
        self.assertIn('component_a', report.patches_by_component)
        self.assertIn('component_b', report.patches_by_component)
        
        # Verify component patch counts
        self.assertEqual(len(report.patches_by_component['component_a']), 2)
        self.assertEqual(len(report.patches_by_component['component_b']), 2)
    
    def test_inventory_report_shows_severity_distribution(self):
        """Test that inventory report shows patches by severity."""
        report = self.generator.generate_inventory_report(self.patches)
        
        # Verify severity distribution
        expected_distribution = {
            DebtLevel.CRITICAL.value: 1,
            DebtLevel.HIGH.value: 1,
            DebtLevel.MEDIUM.value: 1,
            DebtLevel.LOW.value: 1
        }
        
        self.assertEqual(report.severity_distribution, expected_distribution)
        
        # Verify patches are correctly categorized by severity
        self.assertEqual(len(report.patches_by_severity[DebtLevel.CRITICAL]), 1)
        self.assertEqual(len(report.patches_by_severity[DebtLevel.HIGH]), 1)
        self.assertEqual(len(report.patches_by_severity[DebtLevel.MEDIUM]), 1)
        self.assertEqual(len(report.patches_by_severity[DebtLevel.LOW]), 1)
    
    def test_inventory_report_includes_component_summaries(self):
        """Test that inventory report includes detailed component summaries."""
        report = self.generator.generate_inventory_report(self.patches)
        
        # Verify component summaries exist
        self.assertIn('component_a', report.component_summaries)
        self.assertIn('component_b', report.component_summaries)
        
        # Verify component summary structure
        comp_a_summary = report.component_summaries['component_a']
        required_fields = [
            'patch_count', 'debt_score', 'maintenance_burden',
            'critical_patches', 'high_patches', 'medium_patches', 'low_patches'
        ]
        
        for field in required_fields:
            self.assertIn(field, comp_a_summary)
        
        # Verify component A has higher debt score (critical + high patches)
        comp_b_summary = report.component_summaries['component_b']
        self.assertGreater(comp_a_summary['debt_score'], comp_b_summary['debt_score'])


class TestRequirement82TrendAnalysis(unittest.TestCase):
    """
    Test Requirement 8.2: WHEN trends are analyzed THEN reports SHALL show 
    patch creation and resolution rates over time
    """
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ReportGenerator()
        self.patches = self._create_time_distributed_patches()
    
    def _create_time_distributed_patches(self) -> List[PatchAnnotation]:
        """Create patches distributed over time for trend analysis."""
        patches = []
        base_date = datetime.now() - timedelta(days=30)
        
        # Create patches over the last 30 days
        for i in range(10):
            patch_date = base_date + timedelta(days=i * 3)
            patches.append(PatchAnnotation(
                reason=f"Issue {i}",
                upstream_issue=f"ISSUE-{i:03d}",
                cleanup_task=f"Fix issue {i}",
                debt_level=DebtLevel.MEDIUM,
                component=f"component_{i % 3}",
                bypass_type=BypassType.ARCHITECTURE,
                created_date=patch_date
            ))
        
        return patches
    
    def test_trend_analysis_generates_time_series_data(self):
        """Test that trend analysis generates time series data points."""
        trends = self.generator.generate_trend_analysis(
            self.patches, 
            TimeRange.LAST_30_DAYS
        )
        
        # Verify trend analysis structure
        self.assertIsInstance(trends, TrendAnalysis)
        self.assertEqual(trends.time_range, TimeRange.LAST_30_DAYS)
        
        # Verify data points are generated
        self.assertGreater(len(trends.data_points), 0)
        
        # Verify data points have required fields
        for data_point in trends.data_points:
            self.assertIsInstance(data_point.timestamp, datetime)
            self.assertIsInstance(data_point.patches_created, int)
            self.assertIsInstance(data_point.patches_resolved, int)
            self.assertIsInstance(data_point.total_active_patches, int)
            self.assertIsInstance(data_point.total_debt_score, float)
    
    def test_trend_analysis_identifies_creation_trends(self):
        """Test that trend analysis identifies patch creation trends."""
        trends = self.generator.generate_trend_analysis(
            self.patches, 
            TimeRange.LAST_30_DAYS
        )
        
        # Verify trend identification
        self.assertIn(trends.creation_trend, ['increasing', 'decreasing', 'stable'])
        self.assertIn(trends.resolution_trend, ['increasing', 'decreasing', 'stable'])
        self.assertIn(trends.net_debt_trend, ['increasing', 'decreasing', 'stable'])
    
    def test_trend_analysis_includes_performance_metrics(self):
        """Test that trend analysis includes performance metrics."""
        trends = self.generator.generate_trend_analysis(
            self.patches, 
            TimeRange.LAST_30_DAYS
        )
        
        # Verify performance metrics exist
        self.assertIsInstance(trends.performance_metrics, dict)
        
        # Verify key metrics are present
        expected_metrics = [
            'total_patches_created', 'total_patches_resolved',
            'average_daily_creation', 'current_debt_score'
        ]
        
        for metric in expected_metrics:
            self.assertIn(metric, trends.performance_metrics)
            self.assertIsInstance(trends.performance_metrics[metric], (int, float))


class TestRequirement83CleanupProgressTracking(unittest.TestCase):
    """
    Test Requirement 8.3: WHEN cleanup progress is tracked THEN reports SHALL 
    show forward pass completion status
    """
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ReportGenerator()
        self.patches = self._create_cleanup_test_patches()
    
    def _create_cleanup_test_patches(self) -> List[PatchAnnotation]:
        """Create patches for cleanup progress testing."""
        patches = []
        
        # Mix of patches in different cleanup states
        for i in range(5):
            patches.append(PatchAnnotation(
                reason=f"Cleanup test issue {i}",
                upstream_issue=f"CLEANUP-{i:03d}",
                cleanup_task=f"Resolve cleanup issue {i}",
                debt_level=DebtLevel.MEDIUM,
                component="cleanup_component",
                bypass_type=BypassType.ARCHITECTURE
            ))
        
        return patches
    
    def test_executive_dashboard_includes_cleanup_progress(self):
        """Test that executive dashboard includes cleanup progress tracking."""
        cleanup_data = {
            'completed_tasks': 15,
            'total_tasks': 25,
            'in_progress_tasks': 7,
            'blocked_tasks': 3
        }
        
        dashboard = self.generator.generate_executive_dashboard(
            self.patches, 
            cleanup_data
        )
        
        # Verify cleanup progress is included
        self.assertIsNotNone(dashboard.cleanup_progress)
        
        # Verify cleanup progress structure
        progress = dashboard.cleanup_progress
        self.assertIsInstance(progress.total_cleanup_tasks, int)
        self.assertIsInstance(progress.completed_tasks, int)
        self.assertIsInstance(progress.in_progress_tasks, int)
        self.assertIsInstance(progress.blocked_tasks, int)
        self.assertIsInstance(progress.completion_percentage, float)
        
        # Verify completion percentage calculation
        expected_percentage = (progress.completed_tasks / progress.total_cleanup_tasks) * 100
        self.assertEqual(progress.completion_percentage, expected_percentage)
    
    def test_cleanup_progress_includes_velocity_metrics(self):
        """Test that cleanup progress includes velocity metrics."""
        dashboard = self.generator.generate_executive_dashboard(self.patches)
        
        # Verify velocity metrics exist
        self.assertIsInstance(dashboard.cleanup_progress.velocity_metrics, dict)
        self.assertIn('patches_per_week', dashboard.cleanup_progress.velocity_metrics)


class TestRequirement84DebtImpactQuantification(unittest.TestCase):
    """
    Test Requirement 8.4: WHEN debt impact is assessed THEN reports SHALL 
    quantify maintenance burden and risk
    """
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ReportGenerator()
        self.patches = self._create_impact_test_patches()
    
    def _create_impact_test_patches(self) -> List[PatchAnnotation]:
        """Create patches for impact assessment testing."""
        patches = []
        
        # High-impact patches
        patches.append(PatchAnnotation(
            reason="Critical system failure",
            upstream_issue="CRIT-001",
            cleanup_task="Fix critical system",
            debt_level=DebtLevel.CRITICAL,
            component="core_system",
            bypass_type=BypassType.SECURITY
        ))
        
        # Medium-impact patches
        patches.append(PatchAnnotation(
            reason="Performance degradation",
            upstream_issue="PERF-001",
            cleanup_task="Optimize performance",
            debt_level=DebtLevel.HIGH,
            component="core_system",
            bypass_type=BypassType.PERFORMANCE
        ))
        
        return patches
    
    def test_executive_dashboard_quantifies_technical_debt(self):
        """Test that executive dashboard quantifies total technical debt."""
        dashboard = self.generator.generate_executive_dashboard(self.patches)
        
        # Verify debt quantification
        self.assertIsInstance(dashboard.total_technical_debt, float)
        self.assertGreater(dashboard.total_technical_debt, 0)
        
        # Verify risk assessment is included
        self.assertIsNotNone(dashboard.risk_assessment)
        self.assertIn(dashboard.risk_assessment.risk_level, ['low', 'moderate', 'high', 'critical'])
    
    def test_inventory_report_includes_maintenance_burden(self):
        """Test that inventory report includes maintenance burden assessment."""
        report = self.generator.generate_inventory_report(self.patches)
        
        # Verify component summaries include maintenance burden
        for component, summary in report.component_summaries.items():
            self.assertIn('maintenance_burden', summary)
            self.assertIsInstance(summary['maintenance_burden'], (int, float))
    
    def test_dashboard_metrics_include_risk_quantification(self):
        """Test that dashboard metrics include risk quantification."""
        metrics = self.generator.get_dashboard_metrics(self.patches)
        
        # Verify risk metrics
        self.assertIsInstance(metrics.system_health_score, float)
        self.assertGreaterEqual(metrics.system_health_score, 0)
        self.assertLessEqual(metrics.system_health_score, 100)
        
        # Verify top risk components are identified
        self.assertIsInstance(metrics.top_risk_components, list)


class TestRequirement85ExecutiveSummaries(unittest.TestCase):
    """
    Test Requirement 8.5: WHEN stakeholder updates are needed THEN reports 
    SHALL provide executive summaries with actionable insights
    """
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ReportGenerator()
        self.dashboard = PatchDashboard()
        self.patches = self._create_executive_test_patches()
    
    def _create_executive_test_patches(self) -> List[PatchAnnotation]:
        """Create patches for executive summary testing."""
        patches = []
        
        # Critical issues requiring executive attention
        patches.append(PatchAnnotation(
            reason="Security vulnerability in production",
            upstream_issue="SEC-CRITICAL-001",
            cleanup_task="Emergency security patch",
            debt_level=DebtLevel.CRITICAL,
            component="production_system",
            bypass_type=BypassType.SECURITY,
            expected_resolution=datetime.now() - timedelta(days=5)  # Overdue
        ))
        
        # High-impact business issue
        patches.append(PatchAnnotation(
            reason="Compliance violation risk",
            upstream_issue="COMP-HIGH-001",
            cleanup_task="Implement compliance controls",
            debt_level=DebtLevel.HIGH,
            component="compliance_system",
            bypass_type=BypassType.COMPLIANCE
        ))
        
        return patches
    
    def test_executive_dashboard_provides_actionable_insights(self):
        """Test that executive dashboard provides actionable insights."""
        dashboard = self.generator.generate_executive_dashboard(self.patches)
        
        # Verify actionable insights exist
        self.assertIsInstance(dashboard.actionable_insights, list)
        self.assertGreater(len(dashboard.actionable_insights), 0)
        
        # Verify insight structure
        for insight in dashboard.actionable_insights:
            required_fields = ['type', 'title', 'description', 'impact', 'effort', 'timeline']
            for field in required_fields:
                self.assertIn(field, insight)
    
    def test_executive_dashboard_includes_critical_issues(self):
        """Test that executive dashboard identifies critical issues."""
        dashboard = self.generator.generate_executive_dashboard(self.patches)
        
        # Verify critical issues are identified
        self.assertIsInstance(dashboard.critical_issues, list)
        self.assertGreater(len(dashboard.critical_issues), 0)
        
        # Verify critical issues mention security and overdue patches
        critical_text = ' '.join(dashboard.critical_issues).lower()
        self.assertIn('critical', critical_text)
    
    def test_executive_dashboard_includes_top_priorities(self):
        """Test that executive dashboard includes top priorities."""
        dashboard = self.generator.generate_executive_dashboard(self.patches)
        
        # Verify top priorities exist
        self.assertIsInstance(dashboard.top_priorities, list)
        self.assertGreater(len(dashboard.top_priorities), 0)
    
    def test_executive_dashboard_includes_roi_metrics(self):
        """Test that executive dashboard includes ROI metrics."""
        dashboard = self.generator.generate_executive_dashboard(self.patches)
        
        # Verify ROI metrics exist
        self.assertIsInstance(dashboard.roi_metrics, dict)
        self.assertGreater(len(dashboard.roi_metrics), 0)
        
        # Verify ROI metrics include financial impact
        roi_keys = list(dashboard.roi_metrics.keys())
        self.assertTrue(any('cost' in key.lower() or 'value' in key.lower() for key in roi_keys))
    
    def test_comprehensive_dashboard_provides_executive_summary(self):
        """Test that comprehensive dashboard provides executive summary."""
        comprehensive = self.dashboard.generate_comprehensive_report(
            self.patches,
            include_executive_summary=True
        )
        
        # Verify executive dashboard is included
        self.assertIn('executive_dashboard', comprehensive)
        self.assertIsNotNone(comprehensive['executive_dashboard'])
        
        # Verify summary section exists
        self.assertIn('summary', comprehensive)
        summary = comprehensive['summary']
        
        # Verify summary includes key executive metrics
        required_summary_fields = [
            'total_patches', 'system_health_score', 
            'critical_issues_count', 'cleanup_recommendations'
        ]
        
        for field in required_summary_fields:
            self.assertIn(field, summary)


class TestReportingSystemIntegration(unittest.TestCase):
    """Test overall reporting system integration and functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.dashboard = PatchDashboard()
        self.generator = ReportGenerator()
        self.patches = self._create_integration_test_patches()
    
    def _create_integration_test_patches(self) -> List[PatchAnnotation]:
        """Create comprehensive test patches for integration testing."""
        patches = []
        
        # Diverse set of patches for comprehensive testing
        patch_configs = [
            (DebtLevel.CRITICAL, BypassType.SECURITY, "security_service"),
            (DebtLevel.HIGH, BypassType.PERFORMANCE, "performance_service"),
            (DebtLevel.MEDIUM, BypassType.INTEGRATION, "integration_service"),
            (DebtLevel.LOW, BypassType.ARCHITECTURE, "architecture_service"),
            (DebtLevel.HIGH, BypassType.COMPLIANCE, "compliance_service")
        ]
        
        for i, (debt_level, bypass_type, component) in enumerate(patch_configs):
            patches.append(PatchAnnotation(
                reason=f"Integration test issue {i}",
                upstream_issue=f"INT-{i:03d}",
                cleanup_task=f"Fix integration issue {i}",
                debt_level=debt_level,
                component=component,
                bypass_type=bypass_type,
                created_date=datetime.now() - timedelta(days=i * 5),
                expected_resolution=datetime.now() + timedelta(days=30 - i * 5)
            ))
        
        return patches
    
    def test_report_export_functionality(self):
        """Test that reports can be exported in multiple formats."""
        report = self.generator.generate_inventory_report(self.patches)
        
        # Test JSON export
        json_path = self.generator.export_report(report, ReportFormat.JSON)
        self.assertTrue(json_path.endswith('.json'))
        
        # Test HTML export
        html_path = self.generator.export_report(report, ReportFormat.HTML)
        self.assertTrue(html_path.endswith('.html'))
        
        # Test CSV export
        csv_path = self.generator.export_report(report, ReportFormat.CSV)
        self.assertTrue(csv_path.endswith('.csv'))
    
    def test_dashboard_health_monitoring(self):
        """Test that dashboard components provide health monitoring."""
        # Test generator health
        generator_health = self.generator.get_health_status()
        self.assertIsNotNone(generator_health)
        self.assertIn(generator_health.status.value, ['healthy', 'warning', 'error'])
        
        # Test dashboard health
        dashboard_health = self.dashboard.get_health_status()
        self.assertIsNotNone(dashboard_health)
        self.assertIn(dashboard_health.status.value, ['healthy', 'warning', 'error'])
    
    def test_graceful_degradation(self):
        """Test that components handle graceful degradation."""
        # Test generator degradation
        generator_degradation = self.generator.graceful_degradation()
        self.assertTrue(generator_degradation.success)
        
        # Test dashboard degradation
        dashboard_degradation = self.dashboard.graceful_degradation()
        self.assertTrue(dashboard_degradation.success)


def run_requirements_compliance_tests():
    """Run all requirements compliance tests."""
    test_classes = [
        TestRequirement81InventoryReports,
        TestRequirement82TrendAnalysis,
        TestRequirement83CleanupProgressTracking,
        TestRequirement84DebtImpactQuantification,
        TestRequirement85ExecutiveSummaries,
        TestReportingSystemIntegration
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("Running Technical Debt Patch Annotation Reporting Requirements Compliance Tests...")
    print("=" * 80)
    
    success = run_requirements_compliance_tests()
    
    print("=" * 80)
    if success:
        print("✅ All requirements compliance tests passed!")
    else:
        print("❌ Some requirements compliance tests failed!")
    
    exit(0 if success else 1)