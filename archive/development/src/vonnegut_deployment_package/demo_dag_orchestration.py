#!/usr/bin/env python3
"""
Demo DAG Orchestration System

Demonstrates the complete DAG-based orchestration system with
the Directus integration task list.
"""

import sys
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from beast_mode.orchestration import (
    DAGValidator,
    ParallelOrchestrator,
    ExecutionMode
)
from beast_mode.orchestration.task_parser import TaskParser


def setup_logging():
    """Setup logging for demo"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger('DAGOrchestrationDemo')


def main():
    """Main demo function"""
    logger = setup_logging()
    logger.info("🚀 DAG Orchestration System Demo")
    logger.info("=" * 60)
    
    try:
        # Step 1: Parse the task file
        task_file = Path('.kiro/specs/directus-ai-memory-palace-integration/tasks.md')
        if not task_file.exists():
            logger.error(f"Task file not found: {task_file}")
            return 1
        
        logger.info("📋 Parsing task file...")
        parser = TaskParser()
        task_nodes = parser.parse_task_file(str(task_file))
        logger.info(f"   Parsed {len(task_nodes)} tasks")
        
        # Step 2: Validate DAG
        logger.info("\n🔍 Validating DAG structure...")
        validator = DAGValidator()
        report = validator.validate_dag(task_nodes)
        
        if not report.is_valid:
            logger.error("❌ DAG validation failed:")
            for error in report.validation_errors:
                logger.error(f"   - {error}")
            return 1
        
        logger.info("✅ DAG validation successful!")
        logger.info(f"   Total tasks: {report.total_tasks}")
        logger.info(f"   Execution waves: {len(report.execution_waves)}")
        logger.info(f"   Max parallelism: {report.max_parallelism}")
        logger.info(f"   Critical path: {' → '.join(report.critical_path[:3])}{'...' if len(report.critical_path) > 3 else ''}")
        
        # Step 3: Show execution plan
        logger.info("\n📊 Execution Plan:")
        for i, wave in enumerate(report.execution_waves, 1):
            logger.info(f"   Wave {i}: {len(wave)} tasks - {', '.join(wave[:3])}{'...' if len(wave) > 3 else ''}")
        
        # Step 4: Demonstrate orchestration (dry run)
        logger.info("\n🎭 Demonstrating orchestration (dry run)...")
        orchestrator = ParallelOrchestrator(max_parallel_tasks=4)
        
        # Register mock task functions
        def create_mock_task(task_id):
            def mock_task():
                import time
                import random
                # Simulate variable task duration
                duration = random.uniform(0.5, 2.0)
                time.sleep(duration)
                return f"Mock execution of {task_id} completed in {duration:.1f}s"
            return mock_task
        
        for task_id in task_nodes:
            orchestrator.register_task(task_id, create_mock_task(task_id))
        
        # Execute first few tasks only for demo
        demo_tasks = dict(list(task_nodes.items())[:6])  # First 6 tasks
        
        logger.info(f"   Executing {len(demo_tasks)} tasks for demonstration...")
        result = orchestrator.orchestrate_dag_execution(
            demo_tasks,
            execution_mode=ExecutionMode.IN_PROCESS,
            fail_fast=False
        )
        
        # Step 5: Show results
        logger.info("\n📈 Orchestration Results:")
        logger.info(f"   Total tasks: {result.total_tasks}")
        logger.info(f"   Successful: {result.successful_tasks}")
        logger.info(f"   Failed: {result.failed_tasks}")
        logger.info(f"   Waves executed: {result.waves_executed}")
        logger.info(f"   Total duration: {result.total_duration_seconds:.2f}s")
        logger.info(f"   Parallelization efficiency: {result.parallelization_efficiency:.2f}")
        
        # Show wave details
        logger.info("\n🌊 Wave Execution Details:")
        for wave_result in result.wave_results:
            logger.info(f"   Wave {wave_result.wave_number}:")
            logger.info(f"     Tasks: {len(wave_result.tasks_in_wave)}")
            logger.info(f"     Successful: {len(wave_result.successful_tasks)}")
            logger.info(f"     Duration: {wave_result.wave_duration_seconds:.2f}s")
            if wave_result.failed_tasks:
                logger.info(f"     Failed: {', '.join(wave_result.failed_tasks)}")
        
        # Step 6: Show system capabilities
        logger.info("\n🔧 System Capabilities:")
        logger.info("   ✅ Mathematical DAG validation with cycle detection")
        logger.info("   ✅ Topological sorting for optimal execution order")
        logger.info("   ✅ Parallel execution with dependency constraints")
        logger.info("   ✅ Independent task isolation and failure handling")
        logger.info("   ✅ Real-time monitoring and progress tracking")
        logger.info("   ✅ Comprehensive rollback and recovery mechanisms")
        
        # Step 7: Show next steps
        logger.info("\n🎯 Next Steps:")
        logger.info("   1. Run full orchestration: python scripts/orchestrate_directus_integration.py")
        logger.info("   2. Test system: python scripts/test_dag_orchestration.py")
        logger.info("   3. Monitor execution: tail -f orchestration.log")
        
        # Cleanup
        orchestrator.cleanup()
        
        logger.info("\n🎉 Demo completed successfully!")
        logger.info("=" * 60)
        return 0
        
    except Exception as e:
        logger.error(f"💥 Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())