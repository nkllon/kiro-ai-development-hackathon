#!/usr/bin/env python3
"""
Demo script for Forward Pass Cleanup Orchestration.

This script demonstrates the systematic cleanup planning and execution capabilities
of the ForwardPassOrchestrator, showing how patches are grouped by component,
ordered by dependencies, and validated through automated testing.

Usage:
    python demo_cleanup_orchestration.py
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

from ..core.models import PatchAnnotation, DebtLevel, BypassType
from .orchestrator import ForwardPassOrchestrator, CleanupCriteria


def create_sample_patches() -> list[PatchAnnotation]:
    """Create sample patches for demonstration."""
    patches = [
        PatchAnnotation(
            patch_id="PATCH-AUTH001",
            reason="Temporary workaround for OAuth token refresh race condition",
            upstream_issue="AUTH-456",
            cleanup_task="Implement proper token refresh synchronization",
            debt_level=DebtLevel.HIGH,
            bypass_type=BypassType.SECURITY,
            component="authentication",
            file_path="src/auth/token_manager.py",
            line_start=45,
            line_end=52,
            validation_criteria=[
                "Token refresh race condition eliminated",
                "All authentication tests pass",
                "No security vulnerabilities introduced"
            ],
            created_date=datetime.now() - timedelta(days=15),
            expected_resolution=datetime.now() + timedelta(days=7)
        ),
        PatchAnnotation(
            patch_id="PATCH-DB002",
            reason="Temporary connection pooling bypass for deadlock issues",
            upstream_issue="DB-789",
            cleanup_task="Implement proper connection pool management with deadlock detection",
            debt_level=DebtLevel.CRITICAL,
            bypass_type=BypassType.PERFORMANCE,
            component="database",
            file_path="src/db/connection_pool.py",
            line_start=123,
            line_end=135,
            validation_criteria=[
                "Connection pool deadlocks eliminated",
                "Database performance maintained",
                "Connection limits properly enforced"
            ],
            created_date=datetime.now() - timedelta(days=30),
            expected_resolution=datetime.now() - timedelta(days=5)  # Overdue
        ),
        PatchAnnotation(
            patch_id="PATCH-API003",
            reason="Rate limiting bypass for critical customer integration",
            upstream_issue="API-123",
            cleanup_task="Implement proper rate limiting with customer tier support",
            debt_level=DebtLevel.MEDIUM,
            bypass_type=BypassType.INTEGRATION,
            component="api_gateway",
            file_path="src/api/rate_limiter.py",
            line_start=67,
            line_end=74,
            validation_criteria=[
                "Rate limiting properly enforced",
                "Customer tier support implemented",
                "API performance tests pass"
            ],
            created_date=datetime.now() - timedelta(days=10),
            expected_resolution=datetime.now() + timedelta(days=14)
        ),
        PatchAnnotation(
            patch_id="PATCH-AUTH004",
            reason="Session timeout bypass for admin users",
            upstream_issue="AUTH-789",
            cleanup_task="Implement configurable session timeouts by user role",
            debt_level=DebtLevel.MEDIUM,
            bypass_type=BypassType.SECURITY,
            component="authentication",
            file_path="src/auth/session_manager.py",
            line_start=89,
            line_end=95,
            validation_criteria=[
                "Role-based session timeouts implemented",
                "Security audit passes",
                "Admin functionality preserved"
            ],
            created_date=datetime.now() - timedelta(days=8),
            expected_resolution=datetime.now() + timedelta(days=10)
        ),
        PatchAnnotation(
            patch_id="PATCH-CACHE005",
            reason="Cache invalidation bypass for real-time updates",
            upstream_issue="CACHE-456",
            cleanup_task="Implement selective cache invalidation with event-driven updates",
            debt_level=DebtLevel.LOW,
            bypass_type=BypassType.PERFORMANCE,
            component="caching",
            file_path="src/cache/invalidator.py",
            line_start=34,
            line_end=41,
            validation_criteria=[
                "Selective cache invalidation working",
                "Real-time updates preserved",
                "Cache hit ratio maintained"
            ],
            created_date=datetime.now() - timedelta(days=5),
            expected_resolution=datetime.now() + timedelta(days=21)
        )
    ]
    
    return patches


def demo_cleanup_planning():
    """Demonstrate cleanup planning capabilities."""
    print("🔧 Technical Debt Patch Cleanup Orchestration Demo")
    print("=" * 60)
    
    # Initialize orchestrator
    orchestrator = ForwardPassOrchestrator()
    
    # Set up component dependencies (database must be cleaned before API gateway)
    orchestrator.set_component_dependencies({
        'api_gateway': ['database', 'authentication'],
        'caching': ['database']
    })
    
    # Create sample patches
    patches = create_sample_patches()
    print(f"\n📋 Created {len(patches)} sample patches:")
    for patch in patches:
        status = "⚠️ OVERDUE" if patch.expected_resolution and patch.expected_resolution < datetime.now() else "✅ Active"
        print(f"  • {patch.patch_id} ({patch.debt_level.value}) - {patch.component} - {status}")
    
    # Demo 1: Plan cleanup for high-priority patches
    print(f"\n🎯 Demo 1: Planning cleanup for HIGH and CRITICAL debt patches")
    print("-" * 50)
    
    high_priority_criteria = CleanupCriteria(
        debt_levels=[DebtLevel.HIGH, DebtLevel.CRITICAL],
        include_expired=True
    )
    
    cleanup_plan = orchestrator.plan_cleanup_pass(high_priority_criteria, patches)
    
    print(f"📊 Cleanup Plan: {cleanup_plan.plan_name}")
    print(f"   Plan ID: {cleanup_plan.plan_id}")
    print(f"   Target Components: {', '.join(cleanup_plan.target_components)}")
    print(f"   Patches to Resolve: {len(cleanup_plan.patches_to_resolve)}")
    print(f"   Total Tasks: {len(cleanup_plan.execution_order)}")
    print(f"   Estimated Effort: {cleanup_plan.estimated_effort}")
    print(f"   Risk Level: {cleanup_plan.risk_assessment.value}")
    
    print(f"\n📝 Execution Order (optimized by dependencies):")
    for i, task in enumerate(cleanup_plan.execution_order, 1):
        print(f"   {i}. {task.component}: {task.description}")
        print(f"      Risk: {task.risk_level.value}, Effort: {task.estimated_effort}")
    
    # Demo 2: Component-based grouping
    print(f"\n🏗️ Demo 2: Component-based patch grouping")
    print("-" * 50)
    
    component_groups = orchestrator.group_patches_by_component(patches)
    for component, component_patches in component_groups.items():
        print(f"📦 {component.upper()} ({len(component_patches)} patches):")
        for patch in component_patches:
            print(f"   • {patch.patch_id}: {patch.reason[:50]}...")
    
    # Demo 3: Cleanup validation
    print(f"\n✅ Demo 3: Cleanup task validation")
    print("-" * 50)
    
    if cleanup_plan.execution_order:
        sample_task = cleanup_plan.execution_order[0]
        sample_task.status = sample_task.status.__class__.COMPLETED
        sample_task.completed_date = datetime.now()
        
        validation_result = orchestrator.validate_cleanup_completion(sample_task)
        
        print(f"🔍 Validating task: {sample_task.task_id}")
        print(f"   Validation Status: {'✅ PASSED' if validation_result.is_valid else '❌ FAILED'}")
        
        if validation_result.errors:
            print(f"   Errors: {len(validation_result.errors)}")
            for error in validation_result.errors:
                print(f"     • {error}")
        
        if validation_result.warnings:
            print(f"   Warnings: {len(validation_result.warnings)}")
            for warning in validation_result.warnings:
                print(f"     • {warning}")
    
    # Demo 4: Rollback planning
    print(f"\n🔄 Demo 4: Rollback plan generation")
    print("-" * 50)
    
    if cleanup_plan.rollback_plan:
        rollback = cleanup_plan.rollback_plan
        print(f"🛡️ Rollback Plan: {rollback.rollback_id}")
        print(f"   Estimated Rollback Time: {rollback.estimated_rollback_time}")
        print(f"   Rollback Steps ({len(rollback.rollback_steps)}):")
        for i, step in enumerate(rollback.rollback_steps[:3], 1):  # Show first 3 steps
            print(f"     {i}. {step}")
        if len(rollback.rollback_steps) > 3:
            print(f"     ... and {len(rollback.rollback_steps) - 3} more steps")
    
    # Demo 5: Plan execution simulation
    print(f"\n🚀 Demo 5: Cleanup plan execution (simulation)")
    print("-" * 50)
    
    execution_results = orchestrator.execute_cleanup_plan(cleanup_plan.plan_id)
    
    print(f"📈 Execution Results:")
    print(f"   Plan ID: {execution_results['plan_id']}")
    print(f"   Final Status: {execution_results['final_status'].upper()}")
    print(f"   Tasks Completed: {execution_results['tasks_completed']}")
    print(f"   Tasks Failed: {execution_results['tasks_failed']}")
    print(f"   Started: {execution_results['started_at']}")
    print(f"   Completed: {execution_results['completed_at']}")
    
    # Demo 6: Status monitoring
    print(f"\n📊 Demo 6: Cleanup status monitoring")
    print("-" * 50)
    
    status = orchestrator.get_cleanup_status(cleanup_plan.plan_id)
    
    print(f"📋 Plan Status: {status['plan_name']}")
    print(f"   Current Status: {status['status'].upper()}")
    print(f"   Progress: {status['progress']['completion_percentage']:.1f}% complete")
    print(f"   Tasks: {status['progress']['completed_tasks']}/{status['progress']['total_tasks']} completed")
    print(f"   Components: {', '.join(status['target_components'])}")
    print(f"   Risk Level: {status['risk_level']}")
    
    # Demo 7: Health status
    print(f"\n🏥 Demo 7: Orchestrator health status")
    print("-" * 50)
    
    health = orchestrator.get_orchestrator_status()
    print(f"💚 Orchestrator Health: {health['status'].upper()}")
    print(f"   Health Score: {health['health_score']:.1f}")
    print(f"   Active Plans: {health['active_plans']}")
    print(f"   Completed Plans: {health['completed_plans']}")
    print(f"   Component Dependencies: {health['component_dependencies']}")
    if health['issues']:
        print(f"   Issues: {', '.join(health['issues'])}")
    
    print(f"\n🎉 Demo completed successfully!")
    print(f"   The ForwardPassOrchestrator demonstrates systematic cleanup planning,")
    print(f"   component-based grouping, dependency-aware execution ordering,")
    print(f"   comprehensive validation, and rollback capabilities.")


if __name__ == "__main__":
    demo_cleanup_planning()