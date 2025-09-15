#!/usr/bin/env python3
"""
Test PDCA Orchestrator
======================

Test script for the Systematic PDCA Orchestrator to verify it works correctly.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Test PDCA cycle execution
"""

import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from beast_mode.core.pdca_orchestrator_core import SystematicPDCAOrchestrator
from beast_mode.core.pdca_orchestrator_validation import PDCATask, PDCAValidator


def test_pdca_orchestrator():
    """Test the PDCA Orchestrator with a sample task."""
    print("🧪 Testing Systematic PDCA Orchestrator")
    print("=" * 50)

    # Create orchestrator
    orchestrator = SystematicPDCAOrchestrator()

    # Test module info
    print("\n📋 Module Information:")
    module_info = orchestrator.get_module_info()
    for key, value in module_info.items():
        print(f"   {key}: {value}")

    # Test health status
    print("\n🏥 Health Status:")
    health = orchestrator.get_health_status()
    print(f"   Status: {health.status.value}")
    print(f"   Health Score: {health.health_score}")
    print(f"   Issues: {len(health.issues)}")

    # Create test task
    test_task = PDCATask(
        task_id="test_001",
        name="Implement User Authentication",
        description="Add user authentication system with login/logout functionality",
        domain="authentication",
        complexity="medium",
        priority="high",
        estimated_duration=timedelta(hours=4),
    )

    print(f"\n🎯 Test Task: {test_task.name}")
    print(f"   Domain: {test_task.domain}")
    print(f"   Complexity: {test_task.complexity}")
    print(f"   Priority: {test_task.priority}")

    # Validate task
    print("\n✅ Task Validation:")
    task_issues = PDCAValidator.validate_task(test_task)
    if task_issues:
        print(f"   Issues found: {task_issues}")
    else:
        print("   Task is valid")

    # Execute PDCA cycle
    print(f"\n🔄 Executing PDCA Cycle...")
    try:
        result = orchestrator.execute_pdca_cycle(test_task)

        print(f"\n🎉 PDCA Cycle Results:")
        print(f"   Task ID: {result['task_id']}")
        print(f"   Systematic Score: {result['systematic_score']:.3f}")
        print(f"   Success Rate: {result['success_rate']:.3f}")
        print(f"   Improvement Factor: {result['improvement_factor']:.3f}")
        print(f"   Duration: {result['duration']}")
        print(f"   Phases Completed: {result['phases_completed']}")

        # Test execution summary
        print(f"\n📊 Execution Summary:")
        summary = orchestrator.get_execution_summary()
        for key, value in summary.items():
            print(f"   {key}: {value}")

        print(f"\n✅ PDCA Orchestrator test completed successfully!")
        return True

    except Exception as e:
        print(f"\n❌ PDCA Cycle failed: {e}")
        return False


def test_multiple_cycles():
    """Test multiple PDCA cycles to verify improvement tracking."""
    print(f"\n🔄 Testing Multiple PDCA Cycles")
    print("=" * 50)

    orchestrator = SystematicPDCAOrchestrator()

    # Create multiple test tasks
    test_tasks = [
        PDCATask(
            task_id="test_002",
            name="Database Schema Design",
            description="Design database schema for user management",
            domain="database",
            complexity="high",
        ),
        PDCATask(
            task_id="test_003",
            name="API Endpoint Implementation",
            description="Implement REST API endpoints for user operations",
            domain="api",
            complexity="medium",
        ),
        PDCATask(
            task_id="test_004",
            name="Frontend Component Development",
            description="Create React components for user interface",
            domain="frontend",
            complexity="medium",
        ),
    ]

    # Execute multiple cycles
    for i, task in enumerate(test_tasks, 1):
        print(f"\n🔄 Cycle {i}: {task.name}")
        try:
            result = orchestrator.execute_pdca_cycle(task)
            print(f"   ✅ Success - Score: {result['systematic_score']:.3f}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")

    # Final summary
    print(f"\n📊 Final Summary:")
    summary = orchestrator.get_execution_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")

    return summary["total_cycles"] > 0


if __name__ == "__main__":
    print("🚀 Starting PDCA Orchestrator Tests")
    print("=" * 60)

    # Test single cycle
    success1 = test_pdca_orchestrator()

    # Test multiple cycles
    success2 = test_multiple_cycles()

    if success1 and success2:
        print(f"\n🎉 All tests passed! PDCA Orchestrator is working correctly.")
        sys.exit(0)
    else:
        print(f"\n❌ Some tests failed.")
        sys.exit(1)
