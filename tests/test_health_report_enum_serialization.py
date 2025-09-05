"""
Unit tests for health report enum serialization functionality.

Tests that health reporting systems properly handle enum serialization
using the new EnumJSONEncoder and SerializationHandler.

Requirements: 6.2, 6.3 - Fix IssueSeverity enum attribute access issues
"""

import json
import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from dataclasses import dataclass, asdict

from src.beast_mode.core.health_monitoring import (
    HealthMonitoringSystem, HealthAlert, AlertSeverity
)
from src.beast_mode.compliance.models import IssueSeverity, ComplianceIssueType
from src.beast_mode.utils.enum_serialization import SerializationHandler


class TestHealthAlertSerialization:
    """Test health alert serialization with enums"""
    
    def test_health_alert_enum_serialization(self):
        """Test that HealthAlert objects with enums serialize correctly"""
        alert = HealthAlert(
            module_name="test_module",
            severity=AlertSeverity.CRITICAL,
            message="Test alert message",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            metric_value=0.3,
            threshold_value=0.8
        )
        
        # Convert to dict for serialization
        alert_dict = {
            "module_name": alert.module_name,
            "severity": alert.severity,
            "message": alert.message,
            "timestamp": alert.timestamp.isoformat(),
            "metric_value": alert.metric_value,
            "threshold_value": alert.threshold_value,
            "resolved": alert.resolved
        }
        
        # Serialize with enum handling
        result = SerializationHandler.serialize_with_enums(alert_dict)
        parsed = json.loads(result)
        
        assert parsed["severity"] == "critical"
        assert parsed["module_name"] == "test_module"
        assert parsed["message"] == "Test alert message"
        assert parsed["metric_value"] == 0.3
        assert parsed["threshold_value"] == 0.8
        assert parsed["resolved"] is False
    
    def test_multiple_alert_severities_serialization(self):
        """Test serialization of different alert severity levels"""
        severities = [
            AlertSeverity.INFO,
            AlertSeverity.WARNING,
            AlertSeverity.CRITICAL,
            AlertSeverity.EMERGENCY
        ]
        
        alerts_data = []
        for i, severity in enumerate(severities):
            alert_data = {
                "id": i,
                "severity": severity,
                "message": f"Test alert {i}"
            }
            alerts_data.append(alert_data)
        
        result = SerializationHandler.serialize_with_enums(alerts_data)
        parsed = json.loads(result)
        
        assert parsed[0]["severity"] == "info"
        assert parsed[1]["severity"] == "warning"
        assert parsed[2]["severity"] == "critical"
        assert parsed[3]["severity"] == "emergency"


class TestHealthMonitoringSystemSerialization:
    """Test health monitoring system report serialization"""
    
    def test_system_health_report_serialization(self):
        """Test that system health reports serialize correctly with enums"""
        # Create a mock health monitoring system
        health_monitor = HealthMonitoringSystem()
        
        # Create some test alerts with different severities
        test_alerts = [
            HealthAlert(
                module_name="module1",
                severity=AlertSeverity.WARNING,
                message="Warning alert",
                timestamp=datetime.now(),
                metric_value=0.6,
                threshold_value=0.8
            ),
            HealthAlert(
                module_name="module2",
                severity=AlertSeverity.CRITICAL,
                message="Critical alert",
                timestamp=datetime.now(),
                metric_value=0.2,
                threshold_value=0.5
            )
        ]
        
        # Add alerts to the monitoring system
        health_monitor.active_alerts = test_alerts
        
        # Get health report
        report = health_monitor.get_system_health_report()
        
        # Serialize the report
        result = SerializationHandler.serialize_with_enums(report)
        parsed = json.loads(result)
        
        # Check that enum values are properly serialized
        recent_alerts = parsed["recent_alerts"]
        assert len(recent_alerts) == 2
        assert recent_alerts[0]["severity"] == "warning"
        assert recent_alerts[1]["severity"] == "critical"
    
    def test_health_report_safe_serialization(self):
        """Test safe serialization of health reports with potential issues"""
        # Create a health report with mixed data types
        report_data = {
            "system_status": "healthy",
            "alerts": [
                {
                    "severity": AlertSeverity.CRITICAL,
                    "message": "Test alert"
                }
            ],
            "compliance_issues": [
                {
                    "severity": IssueSeverity.MEDIUM,
                    "type": ComplianceIssueType.TEST_FAILURE
                }
            ],
            "timestamp": datetime.now().isoformat()  # Pre-convert datetime to avoid fallback
        }
        
        # Should handle mixed enum types properly
        result = SerializationHandler.serialize_with_enums(report_data)
        parsed = json.loads(result)
        
        assert isinstance(parsed["system_status"], str)
        assert isinstance(parsed["alerts"][0]["severity"], str)
        assert isinstance(parsed["compliance_issues"][0]["severity"], str)
        assert parsed["alerts"][0]["severity"] == "critical"
        assert parsed["compliance_issues"][0]["severity"] == "medium"
        assert parsed["compliance_issues"][0]["type"] == "test_failure"


class TestComplianceIssueSerialization:
    """Test compliance issue serialization with IssueSeverity enum"""
    
    def test_issue_severity_enum_access(self):
        """Test that IssueSeverity enum values are accessible and serializable"""
        # Test all severity levels
        severities = [
            IssueSeverity.CRITICAL,
            IssueSeverity.HIGH,
            IssueSeverity.MEDIUM,
            IssueSeverity.LOW
        ]
        
        for severity in severities:
            # Should be able to access the value
            assert hasattr(severity, 'value')
            assert isinstance(severity.value, str)
            
            # Should be serializable
            data = {"severity": severity}
            result = SerializationHandler.serialize_with_enums(data)
            parsed = json.loads(result)
            assert parsed["severity"] == severity.value
    
    def test_compliance_issue_with_severity_serialization(self):
        """Test serialization of compliance issues with severity enums"""
        issue_data = {
            "issue_type": ComplianceIssueType.RDI_VIOLATION,
            "severity": IssueSeverity.HIGH,
            "description": "Test compliance issue",
            "affected_files": ["file1.py", "file2.py"],
            "remediation_steps": ["Step 1", "Step 2"],
            "blocking_merge": True
        }
        
        result = SerializationHandler.serialize_with_enums(issue_data)
        parsed = json.loads(result)
        
        assert parsed["issue_type"] == "rdi_violation"
        assert parsed["severity"] == "high"
        assert parsed["description"] == "Test compliance issue"
        assert parsed["affected_files"] == ["file1.py", "file2.py"]
        assert parsed["blocking_merge"] is True
    
    def test_mixed_severity_types_serialization(self):
        """Test serialization with mixed severity enum types"""
        mixed_data = {
            "health_alert": {
                "severity": AlertSeverity.CRITICAL,
                "message": "Health issue"
            },
            "compliance_issue": {
                "severity": IssueSeverity.HIGH,
                "description": "Compliance issue"
            },
            "system_status": "operational"
        }
        
        result = SerializationHandler.serialize_with_enums(mixed_data)
        parsed = json.loads(result)
        
        assert parsed["health_alert"]["severity"] == "critical"
        assert parsed["compliance_issue"]["severity"] == "high"
        assert parsed["system_status"] == "operational"


class TestHealthReportExportSerialization:
    """Test health report export functionality with enum serialization"""
    
    @dataclass
    class MockHealthReport:
        """Mock health report for testing"""
        generated_at: datetime
        system_status: str
        alerts: list
        issues: list
    
    def test_health_report_export_with_enums(self):
        """Test health report export handles enums correctly"""
        # Create a mock health report with enums
        report = self.MockHealthReport(
            generated_at=datetime(2024, 1, 1, 12, 0, 0),
            system_status="healthy",
            alerts=[
                {
                    "severity": AlertSeverity.WARNING,
                    "message": "Test alert"
                }
            ],
            issues=[
                {
                    "severity": IssueSeverity.MEDIUM,
                    "type": ComplianceIssueType.TEST_FAILURE,
                    "description": "Test issue"
                }
            ]
        )
        
        # Convert to dict (simulating asdict behavior)
        report_dict = asdict(report)
        
        # Export using enum-aware serialization
        def combined_handler(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif hasattr(obj, 'value'):  # Enum-like objects
                return obj.value
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        result = SerializationHandler.safe_serialize(report_dict, indent=2, default=combined_handler)
        parsed = json.loads(result)
        
        assert parsed["generated_at"] == "2024-01-01T12:00:00"
        assert parsed["system_status"] == "healthy"
        assert parsed["alerts"][0]["severity"] == "warning"
        assert parsed["issues"][0]["severity"] == "medium"
        assert parsed["issues"][0]["type"] == "test_failure"


class TestEnumAttributeAccess:
    """Test enum attribute access patterns that might cause issues"""
    
    def test_issue_severity_attribute_access(self):
        """Test various ways of accessing IssueSeverity enum attributes"""
        # Direct value access
        assert IssueSeverity.CRITICAL.value == "critical"
        assert IssueSeverity.HIGH.value == "high"
        assert IssueSeverity.MEDIUM.value == "medium"
        assert IssueSeverity.LOW.value == "low"
        
        # Name access
        assert IssueSeverity.CRITICAL.name == "CRITICAL"
        assert IssueSeverity.HIGH.name == "HIGH"
        
        # String representation
        assert str(IssueSeverity.CRITICAL) == "IssueSeverity.CRITICAL"
        
        # Comparison
        assert IssueSeverity.CRITICAL == IssueSeverity.CRITICAL
        assert IssueSeverity.HIGH != IssueSeverity.LOW
    
    def test_alert_severity_attribute_access(self):
        """Test various ways of accessing AlertSeverity enum attributes"""
        # Direct value access
        assert AlertSeverity.CRITICAL.value == "critical"
        assert AlertSeverity.WARNING.value == "warning"
        assert AlertSeverity.INFO.value == "info"
        assert AlertSeverity.EMERGENCY.value == "emergency"
        
        # Name access
        assert AlertSeverity.CRITICAL.name == "CRITICAL"
        assert AlertSeverity.WARNING.name == "WARNING"
        
        # String representation
        assert str(AlertSeverity.CRITICAL) == "AlertSeverity.CRITICAL"
    
    def test_enum_serialization_consistency(self):
        """Test that enum serialization is consistent across different contexts"""
        severity = IssueSeverity.HIGH
        
        # Direct serialization
        direct_result = SerializationHandler.serialize_with_enums({"severity": severity})
        direct_parsed = json.loads(direct_result)
        
        # Nested serialization
        nested_result = SerializationHandler.serialize_with_enums({
            "issue": {
                "severity": severity,
                "description": "test"
            }
        })
        nested_parsed = json.loads(nested_result)
        
        # List serialization
        list_result = SerializationHandler.serialize_with_enums([severity, "other_value"])
        list_parsed = json.loads(list_result)
        
        # All should produce the same enum value
        assert direct_parsed["severity"] == "high"
        assert nested_parsed["issue"]["severity"] == "high"
        assert list_parsed[0] == "high"


class TestRealWorldHealthReportScenarios:
    """Test real-world health reporting scenarios with enum serialization"""
    
    def test_comprehensive_health_report_serialization(self):
        """Test serialization of a comprehensive health report with multiple enum types"""
        comprehensive_report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_type": "comprehensive",
                "system_version": "1.0.0"
            },
            "system_health": {
                "overall_status": "degraded",
                "uptime_percentage": 99.5,
                "active_alerts": [
                    {
                        "module": "test_module",
                        "severity": AlertSeverity.WARNING,
                        "message": "Performance degradation detected",
                        "metric_value": 0.6,
                        "threshold_value": 0.8
                    },
                    {
                        "module": "compliance_module",
                        "severity": AlertSeverity.CRITICAL,
                        "message": "Compliance violation detected",
                        "metric_value": 0.3,
                        "threshold_value": 0.9
                    }
                ]
            },
            "compliance_status": {
                "overall_score": 85.5,
                "issues": [
                    {
                        "type": ComplianceIssueType.RDI_VIOLATION,
                        "severity": IssueSeverity.HIGH,
                        "description": "Requirements not properly traced"
                    },
                    {
                        "type": ComplianceIssueType.TEST_FAILURE,
                        "severity": IssueSeverity.MEDIUM,
                        "description": "Test coverage below threshold"
                    }
                ]
            },
            "recommendations": [
                "Address critical alerts immediately",
                "Review compliance violations",
                "Improve test coverage"
            ]
        }
        
        # Serialize the comprehensive report
        result = SerializationHandler.safe_serialize(comprehensive_report, indent=2)
        parsed = json.loads(result)
        
        # Verify all enum values are properly serialized
        alerts = parsed["system_health"]["active_alerts"]
        assert alerts[0]["severity"] == "warning"
        assert alerts[1]["severity"] == "critical"
        
        issues = parsed["compliance_status"]["issues"]
        assert issues[0]["type"] == "rdi_violation"
        assert issues[0]["severity"] == "high"
        assert issues[1]["type"] == "test_failure"
        assert issues[1]["severity"] == "medium"
        
        # Verify other data is preserved
        assert parsed["system_health"]["uptime_percentage"] == 99.5
        assert parsed["compliance_status"]["overall_score"] == 85.5
        assert len(parsed["recommendations"]) == 3