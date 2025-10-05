"""
Unit tests for deployment auditor data models.

Tests the core data structures and their validation logic.
"""

import pytest
import tempfile
import os
from datetime import datetime
from pathlib import Path

from src.deployment_auditor.models import (
    FileEvent, Violation, ClassifiedViolation, RemediationResult,
    FileMetadata, EventType, ViolationType, Severity,
    RemediationStep, ImpactAssessment, MonitoringStatus,
    ComplianceReport, ConfigurationSchema
)


class TestFileMetadata:
    """Test FileMetadata functionality."""
    
    def test_from_path_existing_file(self):
        """Test creating FileMetadata from an existing file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_path = f.name
        
        try:
            metadata = FileMetadata.from_path(temp_path)
            
            assert metadata.size > 0
            assert metadata.permissions is not None
            assert isinstance(metadata.created_at, datetime)
            assert isinstance(metadata.modified_at, datetime)
            assert metadata.file_hash is not None  # Small file should have hash
            
        finally:
            os.unlink(temp_path)
    
    def test_from_path_nonexistent_file(self):
        """Test creating FileMetadata from a non-existent file."""
        metadata = FileMetadata.from_path("/nonexistent/file.txt")
        
        assert metadata.size == 0
        assert metadata.permissions == "000"
        assert isinstance(metadata.created_at, datetime)
        assert isinstance(metadata.modified_at, datetime)
        assert metadata.file_hash is None


class TestFileEvent:
    """Test FileEvent functionality."""
    
    def test_create_event(self):
        """Test creating a FileEvent."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_path = f.name
        
        try:
            event = FileEvent.create_event(EventType.CREATED, temp_path)
            
            assert event.event_type == EventType.CREATED
            assert event.file_path == temp_path
            assert isinstance(event.timestamp, datetime)
            assert event.file_size > 0
            assert event.file_hash is not None
            
        finally:
            os.unlink(temp_path)
    
    def test_event_types(self):
        """Test all event types are available."""
        assert EventType.CREATED.value == "created"
        assert EventType.MODIFIED.value == "modified"
        assert EventType.DELETED.value == "deleted"
        assert EventType.MOVED.value == "moved"


class TestViolation:
    """Test Violation functionality."""
    
    def test_create_violation(self):
        """Test creating a Violation."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test database content")
            temp_path = f.name
        
        try:
            violation = Violation.create_violation(
                temp_path,
                "*.db",
                ViolationType.DATABASE_FILE
            )
            
            assert violation.file_path == temp_path
            assert violation.pattern_matched == "*.db"
            assert violation.violation_type == ViolationType.DATABASE_FILE
            assert isinstance(violation.detected_at, datetime)
            assert isinstance(violation.file_metadata, FileMetadata)
            
        finally:
            os.unlink(temp_path)
    
    def test_violation_types(self):
        """Test all violation types are available."""
        expected_types = [
            "database_file", "time_series_data", "log_file", "cache_file",
            "runtime_state", "binary_executable", "plugin_data", "credentials"
        ]
        
        actual_types = [vt.value for vt in ViolationType]
        
        for expected in expected_types:
            assert expected in actual_types


class TestClassifiedViolation:
    """Test ClassifiedViolation functionality."""
    
    def test_classified_violation_properties(self):
        """Test ClassifiedViolation convenience properties."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_path = f.name
        
        try:
            violation = Violation.create_violation(
                temp_path,
                "*.log",
                ViolationType.LOG_FILE
            )
            
            remediation_steps = [
                RemediationStep("add_to_gitignore", "Add pattern to .gitignore", automated=True)
            ]
            
            impact = ImpactAssessment(
                security_risk=3,
                compliance_risk=5,
                performance_impact=2,
                description="Log file in version control"
            )
            
            classified = ClassifiedViolation(
                violation=violation,
                severity=Severity.MEDIUM,
                risk_score=5,
                remediation_steps=remediation_steps,
                estimated_impact=impact
            )
            
            # Test convenience properties
            assert classified.file_path == temp_path
            assert classified.violation_type == ViolationType.LOG_FILE
            assert classified.severity == Severity.MEDIUM
            assert len(classified.remediation_steps) == 1
            
        finally:
            os.unlink(temp_path)


class TestRemediationResult:
    """Test RemediationResult functionality."""
    
    def test_add_action(self):
        """Test adding remediation actions."""
        result = RemediationResult(
            violation_id="test-violation-1",
            actions_taken=[],
            success=True
        )
        
        result.add_action(
            action_type="gitignore_update",
            target=".gitignore",
            success=True,
            details="Added *.log pattern"
        )
        
        assert len(result.actions_taken) == 1
        action = result.actions_taken[0]
        assert action.action_type == "gitignore_update"
        assert action.target == ".gitignore"
        assert action.success is True
        assert action.details == "Added *.log pattern"
        assert isinstance(action.timestamp, datetime)


class TestComplianceReport:
    """Test ComplianceReport functionality."""
    
    def test_add_violation(self):
        """Test adding violations to compliance report."""
        report = ComplianceReport(
            scan_timestamp=datetime.now(),
            total_files_scanned=100,
            violations_found=0,
            violations_by_severity={},
            violations_by_type={},
            remediation_summary={},
            recommendations=[]
        )
        
        # Create a test violation
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_path = f.name
        
        try:
            violation = Violation.create_violation(
                temp_path,
                "*.db",
                ViolationType.DATABASE_FILE
            )
            
            classified = ClassifiedViolation(
                violation=violation,
                severity=Severity.CRITICAL,
                risk_score=9,
                remediation_steps=[],
                estimated_impact=ImpactAssessment(8, 9, 3, "Critical database file")
            )
            
            report.add_violation(classified)
            
            assert report.violations_found == 1
            assert report.violations_by_severity[Severity.CRITICAL] == 1
            assert report.violations_by_type[ViolationType.DATABASE_FILE] == 1
            
        finally:
            os.unlink(temp_path)


class TestConfigurationSchema:
    """Test ConfigurationSchema functionality."""
    
    def test_default_config(self):
        """Test default configuration creation."""
        config = ConfigurationSchema.default_config()
        
        assert "watch_paths" in config.monitoring
        assert "deployment/" in config.monitoring["watch_paths"]
        assert config.monitoring["scan_interval"] == 60
        
        assert "database_files" in config.patterns
        assert config.patterns["database_files"]["severity"] == "CRITICAL"
        
        assert config.remediation["auto_gitignore"] is True
        assert config.prometheus["enabled"] is True
        assert config.prometheus["port"] == 9090


class TestSeverityLevels:
    """Test severity level enumeration."""
    
    def test_severity_values(self):
        """Test all severity levels are available."""
        assert Severity.CRITICAL.value == "critical"
        assert Severity.HIGH.value == "high"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.LOW.value == "low"
    
    def test_severity_ordering(self):
        """Test severity levels can be compared (if needed)."""
        severities = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]
        assert len(severities) == 4
        assert all(isinstance(s, Severity) for s in severities)