#!/usr/bin/env python3
"""
DAG Orchestration System Demo
============================

Comprehensive demonstration of the DAG orchestrated parallel execution system
showing all components working together.

Author: Beast Mode Framework
Date: 2025-01-27
"""

import asyncio
import time
from typing import List
from datetime import datetime

from src.dag_orchestration.core.dag_orchestrator import (
    DAGOrchestrator,
    OrchestrationConfig,
    create_orchestration_config
)
from src.dag_orchestration.execution.parallel_execution_engine import (
    TaskDefinition,
    ExecutionStrategy,
    create_task_definition
)
from src.dag_orchestration.execution.dependency_aware_scheduler import SchedulingStrategy


async def demo_task_function(task_name: str, duration: float = 1.0):
    """Demo task function that simulates work."""
    print(f"  🔄 Starting {task_name}...")
    await asyncio.sleep(duration)
    result = f"Completed {task_name} after {duration}s"
    print(f"  ✅ {result}")
    return result


def create_demo_tasks() -> List[TaskDefinition]:
    """Create a complex DAG of demo tasks."""
    tasks = []
    
    # Level 1: Independent foundation tasks
    tasks.extend([
        create_task_definition(
            "setup_database", 
            "Setup Database",
            execution_function=lambda: demo_task_function("Database Setup", 2.0),
            priority=3
        ),
        create_task_definition(
            "setup_cache", 
            "Setup Cache",
            execution_function=lambda: demo_task_function("Cache Setup", 1.5),
            priority=3
        ),
        create_task_definition(
            "load_config", 
            "Load Configuration",
            execution_function=lambda: demo_task_function("Config Loading", 0.5),
            priority=2
        )
    ])
    
    # Level 2: Tasks depending on foundation
    tasks.extend([
        create_task_definition(
            "migrate_schema", 
            "Migrate Database Schema",
            dependencies={"setup_database"},
            execution_function=lambda: demo_task_function("Schema Migration", 1.0),
            priority=2
        ),
        create_task_definition(
            "warm_cache", 
            "Warm Cache",
            dependencies={"setup_cache", "load_config"},
            execution_function=lambda: demo_task_function("Cache Warming", 1.0),
            priority=2
        ),
        create_task_definition(
            "validate_config", 
            "Validate Configuration",
            dependencies={"load_config"},
            execution_function=lambda: demo_task_function("Config Validation", 0.5),
            priority=1
        )
    ])
    
    # Level 3: Service initialization
    tasks.extend([
        create_task_definition(
            "start_api_server", 
            "Start API Server",
            dependencies={"migrate_schema", "validate_config"},
            execution_function=lambda: demo_task_function("API Server Start", 1.5),
            priority=1
        ),
        create_task_definition(
            "start_worker_pool", 
            "Start Worker Pool",
            dependencies={"warm_cache", "validate_config"},
            execution_function=lambda: demo_task_function("Worker Pool Start", 1.0),
            priority=1
        )
    ])
    
    # Level 4: Final integration
    tasks.append(
        create_task_definition(
            "health_check", 
            "System Health Check",
            dependencies={"start_api_server", "start_worker_pool"},
            execution_function=lambda: demo_task_function("Health Check", 0.5),
            priority=0
        )
    )
    
    return tasks


async def run_orchestration_demo():
    """Run comprehensive DAG orchestration demonstration."""
    print("🚀 DAG ORCHESTRATED PARALLEL EXECUTION SYSTEM DEMO")
    print("=" * 60)
    
    # Create orchestration configuration
    config = create_orchestration_config(
        max_workers=6,
        execution_strategy=ExecutionStrategy.CONSERVATIVE,
        scheduling_strategy=SchedulingStrategy.ADAPTIVE,
        enable_prefire_testing=True,
        enable_continuous_monitoring=False  # Disabled for demo
    )
    
    print(f"📋 Configuration:")
    print(f"   • Max Workers: {config.max_workers}")
    print(f"   • Execution Strategy: {config.execution_strategy.value}")
    print(f"   • Scheduling Strategy: {config.scheduling_strategy.value}")
    print(f"   • Prefire Testing: {config.enable_prefire_testing}")
    print()
    
    # Create DAG orchestrator
    orchestrator = DAGOrchestrator(config)
    
    # Display orchestrator info
    module_info = orchestrator.get_module_info()
    print(f"🎯 Orchestrator: {module_info['name']} v{module_info['version']}")
    
    health = orchestrator.get_health_status()
    print(f"💚 Health: {health.status.value} (score: {health.health_score:.2f})")
    print()
    
    # Create demo tasks
    tasks = create_demo_tasks()
    print(f"📝 Created {len(tasks)} tasks with complex dependencies")
    
    # Validate execution plan
    print("\n🔍 VALIDATION PHASE")
    print("-" * 30)
    
    validation_report = orchestrator.validate_execution_plan(tasks)
    print(f"✅ Plan Valid: {validation_report['plan_valid']}")
    print(f"📊 Readiness Score: {validation_report['readiness_score']:.2f}")
    print(f"🎯 Assessment: {validation_report['readiness_assessment']}")
    
    if validation_report['recommendations']:
        print("💡 Recommendations:")
        for rec in validation_report['recommendations']:
            print(f"   • {rec}")
    print()
    
    # Execute DAG
    print("🚀 EXECUTION PHASE")
    print("-" * 30)
    
    start_time = datetime.now()
    print(f"⏰ Starting execution at {start_time.strftime('%H:%M:%S')}")
    
    # Execute with orchestrator
    result = await orchestrator.execute_dag(tasks)
    
    end_time = datetime.now()
    print(f"⏰ Completed execution at {end_time.strftime('%H:%M:%S')}")
    print()
    
    # Display results
    print("📊 EXECUTION RESULTS")
    print("-" * 30)
    
    print(f"🆔 Orchestration ID: {result.orchestration_id}")
    print(f"📈 Status: {result.status.value}")
    print(f"⏱️  Duration: {result.duration_seconds:.2f} seconds")
    print(f"📋 Total Tasks: {result.total_tasks}")
    print(f"✅ Completed: {result.completed_tasks}")
    print(f"❌ Failed: {result.failed_tasks}")
    print(f"⏭️  Skipped: {result.skipped_tasks}")
    
    success_rate = result.completed_tasks / result.total_tasks if result.total_tasks > 0 else 0
    print(f"📊 Success Rate: {success_rate:.1%}")
    print()
    
    # Display task details
    print("📋 TASK EXECUTION DETAILS")
    print("-" * 30)
    
    for task_id, task_result in result.task_results.items():
        status_emoji = "✅" if task_result.status.value == "completed" else "❌"
        duration = task_result.duration_seconds or 0
        print(f"{status_emoji} {task_id}: {task_result.status.value} ({duration:.2f}s)")
    print()
    
    # Display performance metrics
    if result.performance_metrics:
        print("⚡ PERFORMANCE METRICS")
        print("-" * 30)
        
        engine_stats = result.performance_metrics.get('execution_engine_stats', {})
        if engine_stats:
            print(f"🔧 Execution Engine:")
            print(f"   • Success Rate: {engine_stats.get('success_rate', 0):.1%}")
            print(f"   • Total Tasks: {engine_stats.get('total_tasks_executed', 0)}")
        
        scheduler_stats = result.performance_metrics.get('scheduling_stats', {})
        if scheduler_stats:
            print(f"📅 Scheduler:")
            print(f"   • Strategy: {scheduler_stats.get('strategy', 'unknown')}")
            print(f"   • Decisions: {scheduler_stats.get('total_scheduling_decisions', 0)}")
        
        learning_insights = result.performance_metrics.get('learning_insights', {})
        if learning_insights and learning_insights.get('optimization_suggestions'):
            print(f"🧠 AI Learning Insights:")
            for suggestion in learning_insights['optimization_suggestions']:
                print(f"   • {suggestion['suggestion']} (confidence: {suggestion['confidence']:.1%})")
        print()
    
    # Display orchestrator statistics
    print("📈 ORCHESTRATOR STATISTICS")
    print("-" * 30)
    
    stats = orchestrator.get_orchestration_statistics()
    print(f"🎯 Total Orchestrations: {stats['total_orchestrations']}")
    print(f"✅ Successful: {stats['successful_orchestrations']}")
    print(f"❌ Failed: {stats['failed_orchestrations']}")
    print(f"📊 Success Rate: {stats['success_rate']:.1%}")
    print(f"⏱️  Average Duration: {stats['average_duration_seconds']:.2f}s")
    print()
    
    # Shutdown orchestrator
    await orchestrator.shutdown()
    print("🔚 Orchestrator shutdown completed")
    
    print("\n" + "=" * 60)
    print("✨ DAG ORCHESTRATED PARALLEL EXECUTION DEMO COMPLETED!")
    print("=" * 60)


if __name__ == "__main__":
    # Run the demo
    asyncio.run(run_orchestration_demo())