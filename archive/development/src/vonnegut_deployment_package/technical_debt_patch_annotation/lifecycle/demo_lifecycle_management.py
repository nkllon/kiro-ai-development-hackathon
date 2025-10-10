#!/usr/bin/env python3
"""
Demo script for Technical Debt Patch Lifecycle Management System.

This script demonstrates the comprehensive lifecycle management capabilities
including patch tracking, deadline monitoring, notifications, and escalation workflows.

Usage:
    python demo_lifecycle_management.py
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.technical_debt_patch_annotation.core.models import PatchAnnotation, DebtLevel, BypassType
from src.technical_debt_patch_annotation.lifecycle.manager import (
    PatchLifecycleManager, NotificationConfig, NotificationType
)


def create_sample_patches() -> list[PatchAnnotation]:
    """Create sample patches with different lifecycle states."""
    now = datetime.now()
    
    patches = [
        # Active patch within timeframe
        PatchAnnotation(
            patch_id="PATCH-ACTIVE01",
            reason="Temporary workaround for API rate limiting",
            upstream_issue="API-ISSUE-123",
            cleanup_task="Replace with proper retry mechanism when API v2 available",
            debt_level=DebtLevel.MEDIUM,
            bypass_type=BypassType.INTEGRATION,
            created_date=now - timedelta(days=5),
            expected_resolution=now + timedelta(days=10),
            component="data_processor",
            file_path="src/data/processor.py",
            validation_criteria=["API v2 integration tests pass", "Rate limiting removed"],
            created_by="developer@company.com",
            assigned_to="team-lead@company.com"
        ),
        
        # Patch approaching expiration
        PatchAnnotation(
            patch_id="PATCH-WARN001",
            reason="Temporary database connection pooling bypass",
            upstream_issue="DB-POOL-456",
            cleanup_task="Implement proper connection pooling with retry logic",
            debt_level=DebtLevel.HIGH,
            bypass_type=BypassType.PERFORMANCE,
            created_date=now - timedelta(days=20),
            expected_resolution=now + timedelta(days=3),  # 3 days from now
            component="database_layer",
            file_path="src/db/connection.py",
            validation_criteria=["Connection pool tests pass", "No connection leaks"],
            created_by="senior-dev@company.com",
            assigned_to="database-team@company.com"
        ),
        
        # Expired patch
        PatchAnnotation(
            patch_id="PATCH-EXPIRED1",
            reason="Security bypass for legacy authentication",
            upstream_issue="AUTH-LEGACY-789",
            cleanup_task="Migrate to new authentication system",
            debt_level=DebtLevel.CRITICAL,
            bypass_type=BypassType.SECURITY,
            created_date=now - timedelta(days=30),
            expected_resolution=now - timedelta(days=5),  # 5 days ago
            component="auth_service",
            file_path="src/auth/legacy.py",
            validation_criteria=["New auth system deployed", "Legacy auth removed", "Security tests pass"],
            created_by="security-team@company.com",
            assigned_to="auth-team@company.com"
        ),
        
        # Severely overdue patch (should be escalated)
        PatchAnnotation(
            patch_id="PATCH-OVERDUE1",
            reason="Performance workaround for slow query",
            upstream_issue="QUERY-PERF-101",
            cleanup_task="Optimize database query and add proper indexing",
            debt_level=DebtLevel.HIGH,
            bypass_type=BypassType.PERFORMANCE,
            created_date=now - timedelta(days=45),
            expected_resolution=now - timedelta(days=15),  # 15 days ago
            component="reporting_service",
            file_path="src/reports/queries.py",
            validation_criteria=["Query performance improved", "Proper indexes added"],
            created_by="performance-team@company.com",
            assigned_to="backend-team@company.com"
        )
    ]
    
    return patches


def demo_patch_tracking():
    """Demonstrate patch tracking functionality."""
    print("=== Patch Lifecycle Management Demo ===\n")
    
    # Initialize lifecycle manager with custom configuration
    config = NotificationConfig(
        email_enabled=True,
        slack_enabled=False,
        dashboard_alerts_enabled=True,
        warning_days_before_expiration=7,
        alert_days_before_expiration=3,
        escalation_days_after_expiration=5
    )
    
    manager = PatchLifecycleManager(config)
    
    # Create and track sample patches
    patches = create_sample_patches()
    
    print("1. Tracking Sample Patches")
    print("-" * 40)
    for patch in patches:
        manager.track_patch(patch)
        print(f"✓ Tracking patch {patch.patch_id} in {patch.component}")
        print(f"  Debt Level: {patch.debt_level.value}")
        print(f"  Expected Resolution: {patch.expected_resolution}")
        print(f"  Assigned To: {patch.assigned_to}")
        print()
    
    return manager, patches


def demo_deadline_monitoring(manager):
    """Demonstrate deadline monitoring and categorization."""
    print("2. Deadline Monitoring and Categorization")
    print("-" * 40)
    
    categorized = manager.check_patch_deadlines()
    
    for category, patches in categorized.items():
        print(f"{category.replace('_', ' ').title()}: {len(patches)} patches")
        for patch in patches:
            days_info = ""
            if patch.expected_resolution:
                days_diff = (datetime.now() - patch.expected_resolution).days
                if days_diff > 0:
                    days_info = f"({days_diff} days overdue)"
                else:
                    days_info = f"({abs(days_diff)} days remaining)"
            
            print(f"  - {patch.patch_id} ({patch.debt_level.value}) {days_info}")
        print()
    
    return categorized


def demo_escalation_workflow(manager):
    """Demonstrate escalation workflow for overdue patches."""
    print("3. Escalation Workflow")
    print("-" * 40)
    
    escalated_patches = manager.escalate_overdue_patches()
    
    if escalated_patches:
        print(f"Escalated {len(escalated_patches)} overdue patches:")
        for patch in escalated_patches:
            print(f"  - {patch.patch_id} ({patch.debt_level.value}) in {patch.component}")
    else:
        print("No patches required escalation at this time.")
    
    print()


def demo_notification_system(manager, patches):
    """Demonstrate notification system."""
    print("4. Notification System")
    print("-" * 40)
    
    # Send notifications for different patch categories
    approaching_patches = [p for p in patches if p.patch_id == "PATCH-WARN001"]
    expired_patches = [p for p in patches if p.patch_id == "PATCH-EXPIRED1"]
    
    if approaching_patches:
        sent = manager.send_notifications(NotificationType.EXPIRATION_WARNING, approaching_patches)
        print(f"✓ Sent {sent} expiration warning notifications")
    
    if expired_patches:
        sent = manager.send_notifications(NotificationType.EXPIRATION_ALERT, expired_patches)
        print(f"✓ Sent {sent} expiration alert notifications")
    
    print()


def demo_patch_resolution(manager):
    """Demonstrate patch resolution and validation."""
    print("5. Patch Resolution and Validation")
    print("-" * 40)
    
    # Document resolution of a patch
    patch_id = "PATCH-ACTIVE01"
    resolution_notes = "Successfully implemented proper retry mechanism with exponential backoff"
    resolved_by = "developer@company.com"
    
    success = manager.document_patch_resolution(patch_id, resolution_notes, resolved_by)
    if success:
        print(f"✓ Documented resolution of {patch_id}")
        print(f"  Resolution: {resolution_notes}")
        print(f"  Resolved by: {resolved_by}")
    
    # Validate patch cleanup
    validation_results = {
        "API v2 integration tests pass": True,
        "Rate limiting removed": True,
        "tests_passed": True,
        "functionality_verified": True,
        "no_regressions": True
    }
    
    validation_result = manager.validate_patch_cleanup(patch_id, validation_results)
    print(f"✓ Validation result: {'PASSED' if validation_result.is_valid else 'FAILED'}")
    if validation_result.errors:
        print(f"  Errors: {validation_result.errors}")
    if validation_result.warnings:
        print(f"  Warnings: {validation_result.warnings}")
    
    print()


def demo_lifecycle_reporting(manager):
    """Demonstrate lifecycle reporting capabilities."""
    print("6. Lifecycle Reporting")
    print("-" * 40)
    
    # Generate comprehensive lifecycle report
    report = manager.get_lifecycle_report()
    
    print("Summary:")
    for key, value in report['summary'].items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print("\nStatus Breakdown:")
    for status, count in report['status_breakdown'].items():
        if count > 0:
            print(f"  {status.replace('_', ' ')}: {count}")
    
    print("\nDebt Level Breakdown:")
    for level, count in report['debt_level_breakdown'].items():
        if count > 0:
            print(f"  {level}: {count}")
    
    if report['overdue_patches']:
        print("\nOverdue Patches:")
        for patch_info in report['overdue_patches']:
            print(f"  - {patch_info['patch_id']} ({patch_info['debt_level']}) "
                  f"- {patch_info['days_overdue']} days overdue")
    
    print()


def demo_health_monitoring(manager):
    """Demonstrate health monitoring capabilities."""
    print("7. Health Monitoring")
    print("-" * 40)
    
    health_status = manager.get_health_status()
    
    print("Lifecycle Manager Health:")
    for key, value in health_status.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print()


def main():
    """Run the complete lifecycle management demo."""
    try:
        # Initialize and demonstrate patch tracking
        manager, patches = demo_patch_tracking()
        
        # Demonstrate deadline monitoring
        categorized = demo_deadline_monitoring(manager)
        
        # Demonstrate escalation workflow
        demo_escalation_workflow(manager)
        
        # Demonstrate notification system
        demo_notification_system(manager, patches)
        
        # Demonstrate patch resolution
        demo_patch_resolution(manager)
        
        # Demonstrate lifecycle reporting
        demo_lifecycle_reporting(manager)
        
        # Demonstrate health monitoring
        demo_health_monitoring(manager)
        
        print("=== Demo Complete ===")
        print("\nThe Patch Lifecycle Management System provides:")
        print("✓ Comprehensive patch tracking with creation dates and expiration monitoring")
        print("✓ Automated notifications for approaching and expired patches")
        print("✓ Escalation workflows for overdue patches with dashboard alerts")
        print("✓ Documentation and verification of patch cleanup completion")
        print("✓ Validation of cleanup process through systematic testing")
        print("✓ Detailed lifecycle reporting and health monitoring")
        
        print(f"\nRequirements Coverage:")
        print("✓ 7.1: Patch creation dates and expected resolution timeframes")
        print("✓ 7.2: Automated notifications when patches approach expiration")
        print("✓ 7.3: Escalation for patches exceeding intended lifespan")
        print("✓ 7.4: Documentation and verification of patch cleanup completion")
        print("✓ 7.5: Validation of cleanup process through testing")
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())