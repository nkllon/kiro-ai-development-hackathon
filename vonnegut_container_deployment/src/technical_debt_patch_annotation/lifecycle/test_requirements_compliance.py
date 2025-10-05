#!/usr/bin/env python3
"""
Requirements Compliance Tests for Patch Lifecycle Management System.

This test suite verifies that the lifecycle management system meets all
specified requirements from the technical debt patch annotation specification.

Requirements Coverage:
- 7.1: Patch creation dates and expected resolution timeframes
- 7.2: Automated notifications when patches approach expiration
- 7.3: Escalation for patches exceeding intended lifespan
- 7.4: Documentation and verification of patch cleanup completion
- 7.5: Validation of cleanup process through testing
"""

import unittest
import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.technical_debt_patch_annotation.core.models import PatchAnnotation, DebtLevel, BypassType
from src.technical_debt_patch_annotation.lifecycle.manager import (
    PatchLifecycleManager, NotificationConfig, NotificationType, PatchStatus, EMAIL_AVAILABLE
)


class TestRequirement71PatchTracking(unittest.TestCase):
    """Test Requirement 7.1: Patch creation dates and expected resolution timeframes."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = PatchLifecycleManager()
        self.sample_patch = PatchAnnotation(
            patch_id="TEST-PATCH-001",
            reason="Test patch for tracking",
            upstream_issue="TEST-ISSUE-001",
            cleanup_task="Remove test patch",
            debt_level=DebtLevel.MEDIUM,
            bypass_type=BypassType.ARCHITECTURE,
            created_date=datetime.now(),
            expected_resolution=datetime.now() + timedelta(days=14),
            component="test_component",
            created_by="test@example.com",
            assigned_to="assignee@example.com"
        )
    
    def test_track_patch_with_creation_date(self):
        """Test that patches are tracked with creation dates."""
        # Requirement 7.1: WHEN patches are created THEN they SHALL include creation dates
        self.manager.track_patch(self.sample_patch)
        
        # Verify patch is tracked
        self.assertIn(self.sample_patch.patch_id, self.manager.patches)
        tracked_patch = self.manager.patches[self.sample_patch.patch_id]
        
        # Verify creation date is preserved
        self.assertEqual(tracked_patch.created_date, self.sample_patch.created_date)
        self.assertIsInstance(tracked_patch.created_date, datetime)
    
    def test_track_patch_with_expected_resolution(self):
        """Test that patches are tracked with expected resolution timeframes."""
        # Requirement 7.1: WHEN patches are created THEN they SHALL include expected resolution timeframes
        self.manager.track_patch(self.sample_patch)
        
        tracked_patch = self.manager.patches[self.sample_patch.patch_id]
        
        # Verify expected resolution is preserved
        self.assertEqual(tracked_patch.expected_resolution, self.sample_patch.expected_resolution)
        self.assertIsInstance(tracked_patch.expected_resolution, datetime)
        
        # Verify expected resolution is after creation date
        self.assertGreater(tracked_patch.expected_resolution, tracked_patch.created_date)
    
    def test_lifecycle_event_creation(self):
        """Test that lifecycle events are created when tracking patches."""
        initial_events = len(self.manager.lifecycle_events)
        
        self.manager.track_patch(self.sample_patch)
        
        # Verify lifecycle event was created
        self.assertEqual(len(self.manager.lifecycle_events), initial_events + 1)
        
        event = self.manager.lifecycle_events[-1]
        self.assertEqual(event.patch_id, self.sample_patch.patch_id)
        self.assertEqual(event.event_type, "PATCH_CREATED")
        self.assertIn("expected_resolution", event.metadata)


class TestRequirement72AutomatedNotifications(unittest.TestCase):
    """Test Requirement 7.2: Automated notifications when patches approach expiration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = NotificationConfig(
            email_enabled=True,
            warning_days_before_expiration=7,
            alert_days_before_expiration=3
        )
        self.manager = PatchLifecycleManager(self.config)
        
        # Create patches with different expiration states
        now = datetime.now()
        
        self.approaching_patch = PatchAnnotation(
            patch_id="APPROACHING-001",
            reason="Patch approaching expiration",
            upstream_issue="ISSUE-001",
            cleanup_task="Clean up soon",
            expected_resolution=now + timedelta(days=5),  # 5 days from now
            assigned_to="dev@example.com"
        )
        
        self.expired_patch = PatchAnnotation(
            patch_id="EXPIRED-001",
            reason="Expired patch",
            upstream_issue="ISSUE-002",
            cleanup_task="Clean up immediately",
            expected_resolution=now - timedelta(days=2),  # 2 days ago
            assigned_to="dev@example.com"
        )
    
    def test_check_approaching_expiration(self):
        """Test detection of patches approaching expiration."""
        # Requirement 7.2: WHEN patches approach expiration THEN automated notifications SHALL be sent
        self.manager.track_patch(self.approaching_patch)
        
        categorized = self.manager.check_patch_deadlines()
        
        # Verify patch is categorized as approaching expiration
        self.assertIn(self.approaching_patch, categorized['approaching_expiration'])
        self.assertEqual(len(categorized['approaching_expiration']), 1)
    
    def test_check_expired_patches(self):
        """Test detection of expired patches."""
        # Requirement 7.2: WHEN patches approach expiration THEN automated notifications SHALL be sent
        self.manager.track_patch(self.expired_patch)
        
        categorized = self.manager.check_patch_deadlines()
        
        # Verify patch is categorized as expired
        self.assertIn(self.expired_patch, categorized['expired'])
        self.assertEqual(len(categorized['expired']), 1)
    
    @patch('smtplib.SMTP')
    def test_send_expiration_notifications(self, mock_smtp):
        """Test sending of expiration notifications."""
        # Requirement 7.2: WHEN patches approach expiration THEN automated notifications SHALL be sent to responsible teams
        mock_server = Mock()
        mock_smtp.return_value = mock_server
        
        # Configure SMTP server for the test
        self.config.smtp_server = "test.smtp.com"
        self.manager.config = self.config
        
        self.manager.track_patch(self.approaching_patch)
        
        # Send notifications
        sent_count = self.manager.send_notifications(
            NotificationType.EXPIRATION_WARNING, 
            [self.approaching_patch]
        )
        
        # Verify notification was sent
        self.assertEqual(sent_count, 1)
        self.assertEqual(self.manager.metrics['notifications_sent'], 1)
        
        # Verify SMTP was called (if email is available)
        if EMAIL_AVAILABLE:
            mock_smtp.assert_called_once()
            mock_server.send_message.assert_called_once()
        else:
            # If email not available, just verify the notification was recorded
            self.assertEqual(sent_count, 1)
    
    def test_notification_event_recording(self):
        """Test that notification events are recorded in lifecycle history."""
        self.manager.track_patch(self.approaching_patch)
        initial_events = len(self.manager.lifecycle_events)
        
        self.manager.send_notifications(NotificationType.EXPIRATION_WARNING, [self.approaching_patch])
        
        # Verify notification event was recorded
        self.assertGreater(len(self.manager.lifecycle_events), initial_events)
        
        notification_events = [
            e for e in self.manager.lifecycle_events 
            if e.event_type.startswith("NOTIFICATION_")
        ]
        self.assertEqual(len(notification_events), 1)
        
        event = notification_events[0]
        self.assertEqual(event.patch_id, self.approaching_patch.patch_id)
        self.assertIn("EXPIRATION_WARNING", event.event_type)


class TestRequirement73EscalationWorkflows(unittest.TestCase):
    """Test Requirement 7.3: Escalation for patches exceeding intended lifespan."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = NotificationConfig(escalation_days_after_expiration=5)
        self.manager = PatchLifecycleManager(self.config)
        
        # Create severely overdue patch
        now = datetime.now()
        self.overdue_patch = PatchAnnotation(
            patch_id="OVERDUE-001",
            reason="Severely overdue patch",
            upstream_issue="ISSUE-003",
            cleanup_task="Urgent cleanup required",
            debt_level=DebtLevel.HIGH,
            expected_resolution=now - timedelta(days=10),  # 10 days ago
            assigned_to="dev@example.com"
        )
    
    def test_escalate_overdue_patches(self):
        """Test escalation of patches exceeding intended lifespan."""
        # Requirement 7.3: WHEN patches exceed their intended lifespan THEN they SHALL be escalated for immediate attention
        self.manager.track_patch(self.overdue_patch)
        
        escalated_patches = self.manager.escalate_overdue_patches()
        
        # Verify patch was escalated
        self.assertIn(self.overdue_patch, escalated_patches)
        self.assertEqual(len(escalated_patches), 1)
        self.assertEqual(self.manager.metrics['escalations_triggered'], 1)
    
    def test_escalation_event_recording(self):
        """Test that escalation events are recorded."""
        self.manager.track_patch(self.overdue_patch)
        initial_events = len(self.manager.lifecycle_events)
        
        self.manager.escalate_overdue_patches()
        
        # Verify escalation event was recorded
        escalation_events = [
            e for e in self.manager.lifecycle_events 
            if e.event_type == "ESCALATED"
        ]
        self.assertEqual(len(escalation_events), 1)
        
        event = escalation_events[0]
        self.assertEqual(event.patch_id, self.overdue_patch.patch_id)
        self.assertIn("days_overdue", event.metadata)
        self.assertIn("escalation_level", event.metadata)
    
    def test_critical_debt_escalation_rule(self):
        """Test that critical debt patches are escalated more aggressively."""
        # Create critical debt patch that's only 2 days overdue
        now = datetime.now()
        critical_patch = PatchAnnotation(
            patch_id="CRITICAL-001",
            reason="Critical security patch",
            upstream_issue="SECURITY-001",
            cleanup_task="Fix security vulnerability",
            debt_level=DebtLevel.CRITICAL,
            expected_resolution=now - timedelta(days=2),  # 2 days ago
            assigned_to="security@example.com"
        )
        
        self.manager.track_patch(critical_patch)
        
        # Check if escalation rules apply
        applicable_rules = [
            rule for rule in self.manager.escalation_rules
            if rule.condition(critical_patch, now)
        ]
        
        # Verify critical debt escalation rule applies
        critical_rules = [r for r in applicable_rules if "Critical" in r.name]
        self.assertGreater(len(critical_rules), 0)
        
        # Verify highest escalation level for critical debt
        max_level = max(rule.escalation_level for rule in applicable_rules)
        self.assertEqual(max_level, 3)  # Director level


class TestRequirement74PatchResolutionDocumentation(unittest.TestCase):
    """Test Requirement 7.4: Documentation and verification of patch cleanup completion."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = PatchLifecycleManager()
        self.patch = PatchAnnotation(
            patch_id="RESOLVE-001",
            reason="Patch to be resolved",
            upstream_issue="ISSUE-004",
            cleanup_task="Complete cleanup task",
            component="test_component"
        )
        self.manager.track_patch(self.patch)
    
    def test_document_patch_resolution(self):
        """Test documentation of patch cleanup completion."""
        # Requirement 7.4: WHEN patch cleanup is completed THEN the resolution SHALL be documented and verified
        resolution_notes = "Successfully implemented proper solution"
        resolved_by = "developer@example.com"
        
        success = self.manager.document_patch_resolution(
            self.patch.patch_id, 
            resolution_notes, 
            resolved_by
        )
        
        # Verify resolution was documented
        self.assertTrue(success)
        self.assertEqual(self.manager.metrics['patches_resolved'], 1)
    
    def test_resolution_event_recording(self):
        """Test that resolution events are recorded with complete metadata."""
        resolution_notes = "Implemented proper retry mechanism"
        resolved_by = "senior-dev@example.com"
        initial_events = len(self.manager.lifecycle_events)
        
        self.manager.document_patch_resolution(
            self.patch.patch_id, 
            resolution_notes, 
            resolved_by
        )
        
        # Verify resolution event was recorded
        resolution_events = [
            e for e in self.manager.lifecycle_events 
            if e.event_type == "PATCH_RESOLVED"
        ]
        self.assertEqual(len(resolution_events), 1)
        
        event = resolution_events[0]
        self.assertEqual(event.patch_id, self.patch.patch_id)
        self.assertEqual(event.metadata['resolution_notes'], resolution_notes)
        self.assertEqual(event.metadata['resolved_by'], resolved_by)
        self.assertIn('days_to_resolution', event.metadata)
    
    @patch('smtplib.SMTP')
    def test_resolution_confirmation_notification(self, mock_smtp):
        """Test that resolution confirmation notifications are sent."""
        mock_server = Mock()
        mock_smtp.return_value = mock_server
        
        # Configure SMTP server for the test
        self.manager.config.smtp_server = "test.smtp.com"
        
        # Set up patch with assigned developer
        self.patch.assigned_to = "assignee@example.com"
        
        self.manager.document_patch_resolution(
            self.patch.patch_id, 
            "Resolution completed", 
            "resolver@example.com"
        )
        
        # Verify confirmation notification was sent (if email is available)
        if EMAIL_AVAILABLE:
            mock_smtp.assert_called_once()
            mock_server.send_message.assert_called_once()
        else:
            # If email not available, just verify the resolution was documented
            self.assertEqual(self.manager.metrics['patches_resolved'], 1)


class TestRequirement75CleanupValidation(unittest.TestCase):
    """Test Requirement 7.5: Validation of cleanup process through testing."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = PatchLifecycleManager()
        self.patch = PatchAnnotation(
            patch_id="VALIDATE-001",
            reason="Patch requiring validation",
            upstream_issue="ISSUE-005",
            cleanup_task="Validate cleanup completion",
            validation_criteria=["Tests pass", "No regressions", "Performance improved"]
        )
        self.manager.track_patch(self.patch)
    
    def test_validate_patch_cleanup_success(self):
        """Test successful validation of patch cleanup."""
        # Requirement 7.5: WHEN patches are removed THEN the cleanup process SHALL be validated through testing
        validation_results = {
            "Tests pass": True,
            "No regressions": True,
            "Performance improved": True,
            "tests_passed": True,
            "functionality_verified": True,
            "no_regressions": True
        }
        
        result = self.manager.validate_patch_cleanup(self.patch.patch_id, validation_results)
        
        # Verify validation passed
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
        
        # Verify patch was removed from tracking after successful validation
        self.assertNotIn(self.patch.patch_id, self.manager.patches)
    
    def test_validate_patch_cleanup_failure(self):
        """Test failed validation of patch cleanup."""
        validation_results = {
            "Tests pass": False,  # Validation criterion failed
            "No regressions": True,
            "Performance improved": True
        }
        
        result = self.manager.validate_patch_cleanup(self.patch.patch_id, validation_results)
        
        # Verify validation failed
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)
        
        # Verify patch remains in tracking after failed validation
        self.assertIn(self.patch.patch_id, self.manager.patches)
    
    def test_validation_event_recording(self):
        """Test that validation events are recorded."""
        validation_results = {"Tests pass": True, "No regressions": True}
        initial_events = len(self.manager.lifecycle_events)
        
        self.manager.validate_patch_cleanup(self.patch.patch_id, validation_results)
        
        # Verify validation event was recorded
        validation_events = [
            e for e in self.manager.lifecycle_events 
            if e.event_type in ["PATCH_VALIDATED", "VALIDATION_FAILED"]
        ]
        self.assertEqual(len(validation_events), 1)
        
        event = validation_events[0]
        self.assertEqual(event.patch_id, self.patch.patch_id)
        self.assertIn('validation_results', event.metadata)
        self.assertIn('validation_passed', event.metadata)
    
    def test_validation_criteria_checking(self):
        """Test that all validation criteria are checked."""
        # Missing validation criterion
        incomplete_results = {
            "Tests pass": True,
            "No regressions": True
            # Missing "Performance improved"
        }
        
        result = self.manager.validate_patch_cleanup(self.patch.patch_id, incomplete_results)
        
        # Verify validation failed due to missing criterion
        self.assertFalse(result.is_valid)
        
        # Check that error mentions the missing criterion
        missing_criterion_errors = [
            error for error in result.errors 
            if "Performance improved" in error
        ]
        self.assertGreater(len(missing_criterion_errors), 0)


class TestLifecycleReporting(unittest.TestCase):
    """Test lifecycle reporting capabilities."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = PatchLifecycleManager()
        
        # Create patches with different states
        now = datetime.now()
        
        patches = [
            PatchAnnotation(
                patch_id="REPORT-001",
                component="component_a",
                debt_level=DebtLevel.HIGH,
                expected_resolution=now + timedelta(days=5)
            ),
            PatchAnnotation(
                patch_id="REPORT-002",
                component="component_b",
                debt_level=DebtLevel.MEDIUM,
                expected_resolution=now - timedelta(days=3)  # Overdue
            )
        ]
        
        for patch in patches:
            self.manager.track_patch(patch)
    
    def test_lifecycle_report_generation(self):
        """Test generation of comprehensive lifecycle reports."""
        report = self.manager.get_lifecycle_report()
        
        # Verify report structure
        self.assertIn('summary', report)
        self.assertIn('status_breakdown', report)
        self.assertIn('debt_level_breakdown', report)
        self.assertIn('overdue_patches', report)
        self.assertIn('metrics', report)
        
        # Verify summary data
        self.assertEqual(report['summary']['total_active_patches'], 2)
        self.assertGreaterEqual(report['summary']['overdue_patches'], 1)
        
        # Verify overdue patches are identified
        self.assertGreater(len(report['overdue_patches']), 0)
        overdue_patch = report['overdue_patches'][0]
        self.assertIn('patch_id', overdue_patch)
        self.assertIn('days_overdue', overdue_patch)
        self.assertGreater(overdue_patch['days_overdue'], 0)
    
    def test_component_filtered_reporting(self):
        """Test component-specific lifecycle reporting."""
        report = self.manager.get_lifecycle_report(component="component_a")
        
        # Verify component filter is applied
        self.assertEqual(report['component_filter'], "component_a")
        self.assertEqual(report['summary']['total_active_patches'], 1)


def run_compliance_tests():
    """Run all requirements compliance tests."""
    test_classes = [
        TestRequirement71PatchTracking,
        TestRequirement72AutomatedNotifications,
        TestRequirement73EscalationWorkflows,
        TestRequirement74PatchResolutionDocumentation,
        TestRequirement75CleanupValidation,
        TestLifecycleReporting
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("Running Patch Lifecycle Management Requirements Compliance Tests...")
    print("=" * 70)
    
    success = run_compliance_tests()
    
    if success:
        print("\n✅ All requirements compliance tests passed!")
        print("\nRequirements Coverage Verified:")
        print("✓ 7.1: Patch creation dates and expected resolution timeframes")
        print("✓ 7.2: Automated notifications when patches approach expiration")
        print("✓ 7.3: Escalation for patches exceeding intended lifespan")
        print("✓ 7.4: Documentation and verification of patch cleanup completion")
        print("✓ 7.5: Validation of cleanup process through testing")
    else:
        print("\n❌ Some requirements compliance tests failed!")
        exit(1)