"""
Comprehensive Tests for Health Reporting and Alerting System

This module provides tests for reporting accuracy, alert triggering,
trend analysis, and performance validation.
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from typing import Dict, List

from src.beast_mode.domain_index.health_reporter import (
    HealthReportGenerator, HealthTrendAnalyzer, AlertManager,
    HealthReport, HealthTrend, Alert, AlertRule, AlertSeverity, AlertChannel
)
from src.beast_mode.domain_index.models import (
    Domain, HealthStatus, HealthStatusType, HealthIssue, HealthMetrics,
    IssueSeverity, IssueCategory, DomainTools, DomainMetadata, PackagePotential
)


class TestHealthTrendAnalyzer:
    """Test health trend analysis functionality"""
    
    def create_test_metrics(self, overall_score: float) -> HealthMetrics:
        """Create test health metrics"""
        return HealthMetrics(
            dependency_health_score=overall_score,
            pattern_coverage_score=overall_score,
            file_accessibility_score=overall_score,
            makefile_integration_score=overall_score,
            overall_health_score=overall_score
        )
    
    def test_trend_calculation_improving(self):
        """Test trend calculation for improving metrics"""
        analyzer = HealthTrendAnalyzer()
        
        # Simulate improving trend: 0.3 -> 0.5 -> 0.7 -> 0.9
        values = [0.3, 0.5, 0.7, 0.9]
        
        direction, strength = analyzer._calculate_trend(values)
        
        assert direction == "improving"
        assert strength > 0.1  # Should detect significant improvement
    
    def test_trend_calculation_degrading(self):
        """Test trend calculation for degrading metrics"""
        analyzer = HealthTrendAnalyzer()
        
        # Simulate degrading trend: 0.9 -> 0.7 -> 0.5 -> 0.3
        values = [0.9, 0.7, 0.5, 0.3]
        
        direction, strength = analyzer._calculate_trend(values)
        
        assert direction == "degrading"
        assert strength > 0.1  # Should detect significant degradation
    
    def test_trend_calculation_stable(self):
        """Test trend calculation for stable metrics"""
        analyzer = HealthTrendAnalyzer()
        
        # Simulate stable trend: 0.7 -> 0.71 -> 0.69 -> 0.7
        values = [0.7, 0.71, 0.69, 0.7]
        
        direction, strength = analyzer._calculate_trend(values)
        
        assert direction == "stable"
        assert strength < 0.1  # Should detect minimal change
    
    def test_record_and_analyze_metrics(self):
        """Test recording metrics and analyzing trends"""
        analyzer = HealthTrendAnalyzer({"trend_window_days": 1})
        
        domain_name = "test_domain"
        
        # Record metrics over time
        for score in [0.5, 0.6, 0.7, 0.8]:
            metrics = self.create_test_metrics(score)
            analyzer.record_health_metrics(domain_name, metrics)
        
        # Analyze trends
        trends = analyzer.analyze_domain_trends(domain_name)
        
        assert len(trends) > 0
        
        # Should detect improving trend in overall_health_score
        overall_trend = next((t for t in trends if t.metric_name == "overall_health_score"), None)
        assert overall_trend is not None
        assert overall_trend.trend_direction == "improving"
    
    def test_trending_domains_identification(self):
        """Test identification of domains with significant trends"""
        analyzer = HealthTrendAnalyzer()
        
        # Create degrading domain
        for score in [0.9, 0.7, 0.5, 0.3]:
            metrics = self.create_test_metrics(score)
            analyzer.record_health_metrics("degrading_domain", metrics)
        
        # Create stable domain
        for score in [0.7, 0.71, 0.69, 0.7]:
            metrics = self.create_test_metrics(score)
            analyzer.record_health_metrics("stable_domain", metrics)
        
        # Get trending domains
        degrading_domains = analyzer.get_trending_domains("degrading")
        
        assert len(degrading_domains) == 1
        assert degrading_domains[0][0] == "degrading_domain"
        assert degrading_domains[0][1] > 0.1  # Significant trend strength
    
    def test_data_retention(self):
        """Test that old data is properly cleaned up"""
        analyzer = HealthTrendAnalyzer({"trend_window_days": 1})
        
        domain_name = "test_domain"
        
        # Record old metrics (should be cleaned up)
        with patch('src.beast_mode.domain_index.health_reporter.datetime') as mock_datetime:
            old_time = datetime.now() - timedelta(days=2)
            mock_datetime.now.return_value = old_time
            
            metrics = self.create_test_metrics(0.5)
            analyzer.record_health_metrics(domain_name, metrics)
        
        # Record recent metrics
        metrics = self.create_test_metrics(0.8)
        analyzer.record_health_metrics(domain_name, metrics)
        
        # Should only have recent data
        trends = analyzer.analyze_domain_trends(domain_name)
        for trend in trends:
            assert len(trend.values) == 1  # Only recent data point


class TestAlertManager:
    """Test alert management functionality"""
    
    def create_test_health_status(self, overall_score: float, issues: List[HealthIssue] = None) -> HealthStatus:
        """Create test health status"""
        metrics = HealthMetrics(
            dependency_health_score=overall_score,
            pattern_coverage_score=overall_score,
            file_accessibility_score=overall_score,
            makefile_integration_score=overall_score,
            overall_health_score=overall_score
        )
        
        return HealthStatus(
            status=HealthStatusType.HEALTHY if overall_score > 0.7 else HealthStatusType.DEGRADED,
            last_check=datetime.now(),
            issues=issues or [],
            metrics=metrics
        )
    
    def test_threshold_alert_triggering(self):
        """Test threshold-based alert triggering"""
        alert_manager = AlertManager()
        
        # Create health status below threshold
        health_statuses = {
            "critical_domain": self.create_test_health_status(0.2),  # Below 0.3 threshold
            "healthy_domain": self.create_test_health_status(0.8)   # Above threshold
        }
        
        alerts = alert_manager.evaluate_alerts(health_statuses, {})
        
        # Should generate alert for critical domain only
        critical_alerts = [a for a in alerts if a.domain_name == "critical_domain"]
        healthy_alerts = [a for a in alerts if a.domain_name == "healthy_domain"]
        
        assert len(critical_alerts) > 0
        assert len(healthy_alerts) == 0
        
        # Check alert details
        alert = critical_alerts[0]
        assert alert.severity == AlertSeverity.CRITICAL
        assert "threshold" in alert.description.lower()
    
    def test_trend_alert_triggering(self):
        """Test trend-based alert triggering"""
        alert_manager = AlertManager()
        
        # Create degrading trends
        degrading_trend = HealthTrend(
            domain_name="degrading_domain",
            metric_name="overall_health_score",
            values=[0.9, 0.7, 0.5],
            timestamps=[datetime.now() - timedelta(hours=i) for i in range(3)],
            trend_direction="degrading",
            trend_strength=0.5
        )
        
        trends = {"degrading_domain": [degrading_trend]}
        
        alerts = alert_manager.evaluate_alerts({}, trends)
        
        # Should generate trend alert
        trend_alerts = [a for a in alerts if "trend" in a.title.lower()]
        assert len(trend_alerts) > 0
        
        alert = trend_alerts[0]
        assert alert.severity == AlertSeverity.HIGH
        assert alert.domain_name == "degrading_domain"
    
    def test_pattern_alert_triggering(self):
        """Test pattern-based alert triggering"""
        alert_manager = AlertManager()
        
        # Create health status with circular dependency issue
        circular_issue = HealthIssue(
            severity=IssueSeverity.CRITICAL,
            category=IssueCategory.DEPENDENCY,
            description="Circular dependency detected between domains A and B",
            suggested_fix="Break circular dependency"
        )
        
        health_statuses = {
            "problematic_domain": self.create_test_health_status(0.8, [circular_issue])
        }
        
        alerts = alert_manager.evaluate_alerts(health_statuses, {})
        
        # Should generate pattern alert for circular dependency
        pattern_alerts = [a for a in alerts if "circular" in a.title.lower()]
        assert len(pattern_alerts) > 0
        
        alert = pattern_alerts[0]
        assert alert.severity == AlertSeverity.HIGH
        assert alert.domain_name == "problematic_domain"
    
    def test_alert_cooldown(self):
        """Test alert cooldown functionality"""
        alert_manager = AlertManager()
        
        # Set short cooldown for testing
        for rule in alert_manager.alert_rules:
            rule.cooldown_minutes = 1
        
        health_statuses = {
            "critical_domain": self.create_test_health_status(0.2)
        }
        
        # First evaluation should generate alerts
        alerts1 = alert_manager.evaluate_alerts(health_statuses, {})
        assert len(alerts1) > 0
        
        # Immediate second evaluation should not generate alerts (cooldown)
        alerts2 = alert_manager.evaluate_alerts(health_statuses, {})
        assert len(alerts2) == 0
        
        # After cooldown period, should generate alerts again
        with patch('src.beast_mode.domain_index.health_reporter.datetime') as mock_datetime:
            future_time = datetime.now() + timedelta(minutes=2)
            mock_datetime.now.return_value = future_time
            
            alerts3 = alert_manager.evaluate_alerts(health_statuses, {})
            assert len(alerts3) > 0
    
    def test_alert_acknowledgment_and_resolution(self):
        """Test alert acknowledgment and resolution"""
        alert_manager = AlertManager()
        
        health_statuses = {
            "critical_domain": self.create_test_health_status(0.2)
        }
        
        alerts = alert_manager.evaluate_alerts(health_statuses, {})
        assert len(alerts) > 0
        
        alert = alerts[0]
        alert_id = alert.id
        
        # Test acknowledgment
        assert alert_manager.acknowledge_alert(alert_id)
        assert alert_manager.active_alerts[alert_id].acknowledged_at is not None
        
        # Test resolution
        assert alert_manager.resolve_alert(alert_id)
        assert alert_id not in alert_manager.active_alerts
    
    def test_custom_alert_rules(self):
        """Test adding custom alert rules"""
        alert_manager = AlertManager()
        
        # Add custom rule
        custom_rule = AlertRule(
            name="custom_test_rule",
            condition="threshold",
            severity=AlertSeverity.MEDIUM,
            channels=[AlertChannel.LOG],
            threshold_value=0.5,
            metric_name="dependency_health_score",
            cooldown_minutes=30
        )
        
        alert_manager.add_alert_rule(custom_rule)
        
        # Test custom rule triggering
        health_statuses = {
            "test_domain": self.create_test_health_status(0.4)  # Below 0.5 threshold
        }
        
        alerts = alert_manager.evaluate_alerts(health_statuses, {})
        
        custom_alerts = [a for a in alerts if a.rule_name == "custom_test_rule"]
        assert len(custom_alerts) > 0
        
        alert = custom_alerts[0]
        assert alert.severity == AlertSeverity.MEDIUM


class TestHealthReportGenerator:
    """Test health report generation functionality"""
    
    def create_mock_health_monitor(self):
        """Create mock health monitor"""
        mock_monitor = Mock()
        
        # Mock health statuses
        health_statuses = {
            "healthy_domain": HealthStatus(
                status=HealthStatusType.HEALTHY,
                last_check=datetime.now(),
                issues=[],
                metrics=HealthMetrics(
                    dependency_health_score=0.9,
                    pattern_coverage_score=0.8,
                    file_accessibility_score=0.9,
                    makefile_integration_score=0.8,
                    overall_health_score=0.85
                )
            ),
            "degraded_domain": HealthStatus(
                status=HealthStatusType.DEGRADED,
                last_check=datetime.now(),
                issues=[
                    HealthIssue(
                        severity=IssueSeverity.WARNING,
                        category=IssueCategory.PATTERN,
                        description="Pattern coverage below optimal",
                        suggested_fix="Review and update patterns"
                    )
                ],
                metrics=HealthMetrics(
                    dependency_health_score=0.6,
                    pattern_coverage_score=0.5,
                    file_accessibility_score=0.7,
                    makefile_integration_score=0.6,
                    overall_health_score=0.6
                )
            )
        }
        
        mock_monitor.check_all_domains.return_value = health_statuses
        mock_monitor.check_domain_health.side_effect = lambda name: health_statuses.get(name)
        
        return mock_monitor
    
    def create_mock_dependency_analyzer(self):
        """Create mock dependency analyzer"""
        mock_analyzer = Mock()
        
        mock_analyzer.perform_comprehensive_analysis.return_value = {
            "circular_dependencies": {
                "has_circular_dependencies": True,
                "cycles_found": 1,
                "dfs_cycles": [["A", "B", "A"]]
            },
            "orphaned_files": {
                "orphaned_files": ["orphan1.py", "orphan2.py"],
                "coverage_percentage": 85.0
            },
            "dependency_health": {
                "highly_coupled_domains": [{"domain": "coupled_domain", "dependent_count": 6}]
            }
        }
        
        mock_analyzer.analyze_domain_impact.return_value = {
            "target_domain": "test_domain",
            "change_type": "modify",
            "impact_metrics": {"affected_domain_count": 2},
            "risk_assessment": {"risk_level": "medium"}
        }
        
        return mock_analyzer
    
    def test_full_health_report_generation(self):
        """Test generation of comprehensive health report"""
        mock_monitor = self.create_mock_health_monitor()
        mock_analyzer = self.create_mock_dependency_analyzer()
        
        generator = HealthReportGenerator(
            health_monitor=mock_monitor,
            dependency_analyzer=mock_analyzer
        )
        
        report = generator.generate_full_health_report()
        
        # Verify report structure
        assert report.report_type == "full"
        assert report.total_domains == 2
        assert report.healthy_domains == 1
        assert report.degraded_domains == 1
        assert report.failed_domains == 0
        
        # Verify issue categorization
        assert len(report.warning_issues) > 0
        assert len(report.critical_issues) == 0  # No critical issues in mock data
        
        # Verify recommendations
        assert len(report.recommendations) > 0
        
        # Verify data freshness
        assert "health_data" in report.data_freshness
        assert report.data_freshness["health_data"] is not None
    
    def test_domain_specific_report_generation(self):
        """Test generation of domain-specific report"""
        mock_monitor = self.create_mock_health_monitor()
        mock_analyzer = self.create_mock_dependency_analyzer()
        
        generator = HealthReportGenerator(
            health_monitor=mock_monitor,
            dependency_analyzer=mock_analyzer
        )
        
        report = generator.generate_domain_report("healthy_domain")
        
        # Verify report structure
        assert report.report_type == "domain_specific"
        assert report.total_domains == 1
        assert report.healthy_domains == 1
        assert "healthy_domain" in report.domain_health_statuses
        
        # Verify domain-specific data
        domain_status = report.domain_health_statuses["healthy_domain"]
        assert domain_status.status == HealthStatusType.HEALTHY
    
    def test_trend_report_generation(self):
        """Test generation of trend analysis report"""
        mock_monitor = self.create_mock_health_monitor()
        
        generator = HealthReportGenerator(health_monitor=mock_monitor)
        
        # Add some trend data
        generator.trend_analyzer.historical_data["test_domain"]["overall_health_score"] = [
            (datetime.now() - timedelta(hours=3), 0.9),
            (datetime.now() - timedelta(hours=2), 0.7),
            (datetime.now() - timedelta(hours=1), 0.5)
        ]
        
        report = generator.generate_trend_report(days=1)
        
        # Verify report structure
        assert report.report_type == "trend"
        assert len(report.domain_trends) > 0
        
        # Verify trend data
        if "test_domain" in report.domain_trends:
            trends = report.domain_trends["test_domain"]
            assert len(trends) > 0
            
            overall_trend = next((t for t in trends if t.metric_name == "overall_health_score"), None)
            if overall_trend:
                assert overall_trend.trend_direction == "degrading"
    
    def test_report_export_json(self):
        """Test report export in JSON format"""
        mock_monitor = self.create_mock_health_monitor()
        
        generator = HealthReportGenerator(health_monitor=mock_monitor)
        report = generator.generate_full_health_report()
        
        # Export to JSON
        json_export = generator.export_report(report, "json")
        
        # Verify JSON structure
        parsed_json = json.loads(json_export)
        assert "report_id" in parsed_json
        assert "generated_at" in parsed_json
        assert "total_domains" in parsed_json
        assert "recommendations" in parsed_json
    
    def test_alert_integration(self):
        """Test integration with alert system"""
        mock_monitor = self.create_mock_health_monitor()
        
        generator = HealthReportGenerator(
            health_monitor=mock_monitor,
            config={"auto_alerting_enabled": True}
        )
        
        # Generate report (should trigger alerts)
        with patch.object(generator, '_process_alerts') as mock_process_alerts:
            report = generator.generate_full_health_report()
            
            # Should have processed alerts
            mock_process_alerts.assert_called_once()
    
    def test_report_history_management(self):
        """Test report history storage and retrieval"""
        mock_monitor = self.create_mock_health_monitor()
        
        generator = HealthReportGenerator(
            health_monitor=mock_monitor,
            config={"report_retention_days": 1}
        )
        
        # Generate multiple reports
        report1 = generator.generate_full_health_report()
        report2 = generator.generate_domain_report("healthy_domain")
        
        # Get history
        history = generator.get_report_history(days=7)
        assert len(history) == 2
        
        # Filter by type
        full_reports = generator.get_report_history(report_type="full", days=7)
        assert len(full_reports) == 1
        assert full_reports[0].report_type == "full"
    
    def test_alert_summary(self):
        """Test alert summary generation"""
        mock_monitor = self.create_mock_health_monitor()
        
        generator = HealthReportGenerator(health_monitor=mock_monitor)
        
        # Generate some alerts
        health_statuses = {
            "critical_domain": HealthStatus(
                status=HealthStatusType.FAILED,
                last_check=datetime.now(),
                issues=[],
                metrics=HealthMetrics(
                    dependency_health_score=0.1,
                    pattern_coverage_score=0.1,
                    file_accessibility_score=0.1,
                    makefile_integration_score=0.1,
                    overall_health_score=0.1
                )
            )
        }
        
        generator.alert_manager.evaluate_alerts(health_statuses, {})
        
        # Get alert summary
        summary = generator.get_alert_summary()
        
        assert "total_active_alerts" in summary
        assert "critical_alerts" in summary
        assert "recent_alerts" in summary
        assert summary["total_active_alerts"] > 0
    
    def test_performance_large_dataset(self):
        """Test performance with large number of domains"""
        # Create large mock dataset
        large_health_statuses = {}
        for i in range(100):
            large_health_statuses[f"domain_{i}"] = HealthStatus(
                status=HealthStatusType.HEALTHY,
                last_check=datetime.now(),
                issues=[],
                metrics=HealthMetrics(
                    dependency_health_score=0.8,
                    pattern_coverage_score=0.8,
                    file_accessibility_score=0.8,
                    makefile_integration_score=0.8,
                    overall_health_score=0.8
                )
            )
        
        mock_monitor = Mock()
        mock_monitor.check_all_domains.return_value = large_health_statuses
        
        generator = HealthReportGenerator(health_monitor=mock_monitor)
        
        # Generate report and measure time
        import time
        start_time = time.time()
        report = generator.generate_full_health_report()
        end_time = time.time()
        
        # Should complete within reasonable time (< 2 seconds for 100 domains)
        assert (end_time - start_time) < 2.0
        assert report.total_domains == 100
        assert report.generation_time_ms > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])