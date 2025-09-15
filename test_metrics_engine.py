#!/usr/bin/env python3
"""
Test Metrics Engine
==================

Test script for the Systematic Metrics Engine to verify it works correctly
and integrates with the PDCA Orchestrator.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Test metrics collection and systematic vs ad-hoc comparison
"""

import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from beast_mode.metrics.systematic_metrics_engine_core import (
    SystematicMetricsEngine,
    MetricsData,
)
from beast_mode.core.pdca_orchestrator_core import SystematicPDCAOrchestrator
from beast_mode.core.pdca_orchestrator_validation import PDCATask


def test_metrics_engine():
    """Test the Metrics Engine functionality."""
    print("🧪 Testing Systematic Metrics Engine")
    print("=" * 50)

    # Create metrics engine
    metrics_engine = SystematicMetricsEngine()

    # Test module info
    print("\n📋 Module Information:")
    module_info = metrics_engine.get_module_info()
    for key, value in module_info.items():
        print(f"   {key}: {value}")

    # Test health status
    print("\n🏥 Health Status:")
    health = metrics_engine.get_health_status()
    print(f"   Status: {health.status.value}")
    print(f"   Health Score: {health.health_score}")
    print(f"   Issues: {len(health.issues)}")

    # Test metric collection
    print("\n📊 Testing Metric Collection:")

    # Collect systematic metrics
    systematic_metrics = []
    systematic_metrics.append(
        metrics_engine.collect_metric(
            "development_speed",
            8.5,
            "tasks/hour",
            {"domain": "authentication", "complexity": "medium"},
            "systematic",
        )
    )
    systematic_metrics.append(
        metrics_engine.collect_metric(
            "quality_score",
            0.92,
            "score",
            {"domain": "database", "validation": "passed"},
            "systematic",
        )
    )
    systematic_metrics.append(
        metrics_engine.collect_metric(
            "bug_rate",
            0.05,
            "bugs/task",
            {"domain": "api", "testing": "comprehensive"},
            "systematic",
        )
    )

    print(f"   Collected {len(systematic_metrics)} systematic metrics")

    # Collect ad-hoc metrics (simulated)
    adhoc_metrics = []
    adhoc_metrics.append(
        MetricsData(
            timestamp=datetime.now(),
            metric_name="development_speed",
            value=5.2,
            unit="tasks/hour",
            context={"domain": "authentication", "complexity": "medium"},
            approach="ad-hoc",
        )
    )
    adhoc_metrics.append(
        MetricsData(
            timestamp=datetime.now(),
            metric_name="quality_score",
            value=0.68,
            unit="score",
            context={"domain": "database", "validation": "basic"},
            approach="ad-hoc",
        )
    )
    adhoc_metrics.append(
        MetricsData(
            timestamp=datetime.now(),
            metric_name="bug_rate",
            value=0.18,
            unit="bugs/task",
            context={"domain": "api", "testing": "minimal"},
            approach="ad-hoc",
        )
    )

    print(f"   Simulated {len(adhoc_metrics)} ad-hoc metrics")

    # Compare approaches
    print("\n🔍 Comparing Systematic vs Ad-hoc Approaches:")
    comparison = metrics_engine.compare_approaches(systematic_metrics, adhoc_metrics)

    for key, value in comparison.items():
        if key != "timestamp":
            print(f"   {key}: {value}")

    # Generate report
    print("\n📈 Metrics Report:")
    report = metrics_engine.generate_report()
    for key, value in report.items():
        if key != "timestamp":
            print(f"   {key}: {value}")

    print(f"\n✅ Metrics Engine test completed successfully!")
    return True


def test_pdca_metrics_integration():
    """Test integration between PDCA Orchestrator and Metrics Engine."""
    print(f"\n🔄 Testing PDCA Orchestrator + Metrics Engine Integration")
    print("=" * 60)

    # Create both components
    pdca_orchestrator = SystematicPDCAOrchestrator()
    metrics_engine = SystematicMetricsEngine()

    # Create test task
    test_task = PDCATask(
        task_id="integration_test_001",
        name="Integration Test Task",
        description="Test task to verify PDCA and Metrics integration",
        domain="integration",
        complexity="medium",
    )

    print(f"🎯 Test Task: {test_task.name}")

    # Execute PDCA cycle
    print(f"\n🔄 Executing PDCA Cycle...")
    pdca_result = pdca_orchestrator.execute_pdca_cycle(test_task)

    # Collect metrics from PDCA result
    print(f"\n📊 Collecting Metrics from PDCA Result...")

    # Systematic metrics from PDCA
    systematic_metrics = []
    systematic_metrics.append(
        metrics_engine.collect_metric(
            "systematic_score",
            pdca_result["systematic_score"],
            "score",
            {"task_id": test_task.task_id, "domain": test_task.domain},
            "systematic",
        )
    )
    systematic_metrics.append(
        metrics_engine.collect_metric(
            "success_rate",
            pdca_result["success_rate"],
            "rate",
            {"task_id": test_task.task_id, "domain": test_task.domain},
            "systematic",
        )
    )
    systematic_metrics.append(
        metrics_engine.collect_metric(
            "improvement_factor",
            pdca_result["improvement_factor"],
            "factor",
            {"task_id": test_task.task_id, "domain": test_task.domain},
            "systematic",
        )
    )

    # Simulate ad-hoc baseline metrics
    adhoc_metrics = []
    adhoc_metrics.append(
        MetricsData(
            timestamp=datetime.now(),
            metric_name="systematic_score",
            value=0.6,  # Lower baseline
            unit="score",
            context={"task_id": test_task.task_id, "domain": test_task.domain},
            approach="ad-hoc",
        )
    )
    adhoc_metrics.append(
        MetricsData(
            timestamp=datetime.now(),
            metric_name="success_rate",
            value=0.7,  # Lower baseline
            unit="rate",
            context={"task_id": test_task.task_id, "domain": test_task.domain},
            approach="ad-hoc",
        )
    )
    adhoc_metrics.append(
        MetricsData(
            timestamp=datetime.now(),
            metric_name="improvement_factor",
            value=1.0,  # Baseline
            unit="factor",
            context={"task_id": test_task.task_id, "domain": test_task.domain},
            approach="ad-hoc",
        )
    )

    # Compare approaches
    comparison = metrics_engine.compare_approaches(systematic_metrics, adhoc_metrics)

    print(f"\n📈 Integration Results:")
    print(f"   PDCA Systematic Score: {pdca_result['systematic_score']:.3f}")
    print(f"   PDCA Success Rate: {pdca_result['success_rate']:.3f}")
    print(f"   PDCA Improvement Factor: {pdca_result['improvement_factor']:.3f}")
    print(
        f"   Systematic vs Ad-hoc Improvement: {comparison['improvement_percentage']:.1f}%"
    )

    # Generate final report
    report = metrics_engine.generate_report()
    print(f"\n📊 Final Metrics Report:")
    for key, value in report.items():
        if key != "timestamp":
            print(f"   {key}: {value}")

    print(f"\n✅ Integration test completed successfully!")
    return True


def test_multiple_cycle_metrics():
    """Test metrics collection across multiple PDCA cycles."""
    print(f"\n🔄 Testing Multiple Cycle Metrics Collection")
    print("=" * 60)

    pdca_orchestrator = SystematicPDCAOrchestrator()
    metrics_engine = SystematicMetricsEngine()

    # Execute multiple cycles
    test_tasks = [
        PDCATask(
            task_id="multi_001",
            name="Task 1",
            description="First task",
            domain="domain1",
        ),
        PDCATask(
            task_id="multi_002",
            name="Task 2",
            description="Second task",
            domain="domain2",
        ),
        PDCATask(
            task_id="multi_003",
            name="Task 3",
            description="Third task",
            domain="domain3",
        ),
    ]

    systematic_metrics = []

    for i, task in enumerate(test_tasks, 1):
        print(f"\n🔄 Cycle {i}: {task.name}")

        # Execute PDCA cycle
        result = pdca_orchestrator.execute_pdca_cycle(task)

        # Collect metrics
        systematic_metrics.append(
            metrics_engine.collect_metric(
                "cycle_systematic_score",
                result["systematic_score"],
                "score",
                {"cycle": i, "task_id": task.task_id, "domain": task.domain},
                "systematic",
            )
        )

        print(f"   ✅ Systematic Score: {result['systematic_score']:.3f}")

    # Calculate average systematic performance
    avg_systematic_score = sum(m.value for m in systematic_metrics) / len(
        systematic_metrics
    )

    print(f"\n📊 Multiple Cycle Summary:")
    print(f"   Cycles Executed: {len(test_tasks)}")
    print(f"   Average Systematic Score: {avg_systematic_score:.3f}")
    print(f"   Total Metrics Collected: {len(metrics_engine.metrics_history)}")

    # Generate comprehensive report
    report = metrics_engine.generate_report()
    print(f"\n📈 Comprehensive Report:")
    for key, value in report.items():
        if key != "timestamp":
            print(f"   {key}: {value}")

    print(f"\n✅ Multiple cycle metrics test completed successfully!")
    return True


if __name__ == "__main__":
    print("🚀 Starting Metrics Engine Tests")
    print("=" * 60)

    # Test basic functionality
    success1 = test_metrics_engine()

    # Test PDCA integration
    success2 = test_pdca_metrics_integration()

    # Test multiple cycles
    success3 = test_multiple_cycle_metrics()

    if success1 and success2 and success3:
        print(f"\n🎉 All Metrics Engine tests passed!")
        sys.exit(0)
    else:
        print(f"\n❌ Some tests failed.")
        sys.exit(1)
