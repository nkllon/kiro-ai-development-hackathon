#!/usr/bin/env python3
"""
Test DAG Orchestration System

Tests the DAG validation, task parsing, and orchestration components
to ensure they work correctly with the Directus integration task list.
"""

import sys
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from beast_mode.orchestration import (
    DAGValidator,
    IndependentTaskExecutor,
    ParallelOrchestrator,
    ExecutionMode,
    TaskNode
)
from beast_mode.orchestration.task_parser import TaskParser


def setup_logging():
    """Setup logging for testing"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger('DAGOrchestrationTest')


def test_dag_validator():
    """Test DAG validator with simple task graph"""
    logger = logging.getLogger('test_dag_validator')
    logger.info("Testing DAG validator")
    
    # Create simple test tasks
    tasks = {
        'task_a': TaskNode(
            task_id='task_a',
            dependencies=[],
            dependents=['task_b', 'task_c'],
            metadata={'title': 'Task A'}
        ),
        'task_b': TaskNode(
            task_id='task_b',
            dependencies=['task_a'],
            dependents=['task_d'],
            metadata={'title': 'Task B'}
        ),
        'task_c': TaskNode(
            task_id='task_c',
            dependencies=['task_a'],
            dependents=['task_d'],
            metadata={'title': 'Task C'}
        ),
        'task_d': TaskNode(
            task_id='task_d',
            dependencies=['task_b', 'task_c'],
            dependents=[],
            metadata={'title': 'Task D'}
        )
    }
    
    validator = DAGValidator()
    report = validator.validate_dag(tasks)
    
    logger.info(f"Validation result: {report.result.value}")
    logger.info(f"Is valid: {report.is_valid}")
    logger.info(f"Execution waves: {report.execution_waves}")
    logger.info(f"Critical path: {report.critical_path}")
    
    assert report.is_valid, f"DAG should be valid but got errors: {report.validation_errors}"
    assert len(report.execution_waves) == 3, f"Expected 3 waves, got {len(report.execution_waves)}"
    
    logger.info("✅ DAG validator test passed")
    return True


def test_cyclic_dag():
    """Test DAG validator with cyclic dependencies"""
    logger = logging.getLogger('test_cyclic_dag')
    logger.info("Testing cyclic DAG detection")
    
    # Create cyclic task graph
    tasks = {
        'task_a': TaskNode(
            task_id='task_a',
            dependencies=['task_c'],  # Creates cycle: A -> C -> B -> A
            dependents=['task_b'],
            metadata={'title': 'Task A'}
        ),
        'task_b': TaskNode(
            task_id='task_b',
            dependencies=['task_a'],
            dependents=['task_c'],
            metadata={'title': 'Task B'}
        ),
        'task_c': TaskNode(
            task_id='task_c',
            dependencies=['task_b'],
            dependents=['task_a'],
            metadata={'title': 'Task C'}
        )
    }
    
    validator = DAGValidator()
    report = validator.validate_dag(tasks)
    
    logger.info(f"Validation result: {report.result.value}")
    logger.info(f"Is valid: {report.is_valid}")
    logger.info(f"Cycles detected: {report.cycles}")
    
    assert not report.is_valid, "Cyclic DAG should be invalid"
    assert len(report.cycles) > 0, "Should detect at least one cycle"
    
    logger.info("✅ Cyclic DAG detection test passed")
    return True


def test_task_executor():
    """Test independent task executor"""
    logger = logging.getLogger('test_task_executor')
    logger.info("Testing independent task executor")
    
    executor = IndependentTaskExecutor()
    
    # Test simple task execution
    def test_task():
        import time
        time.sleep(0.1)
        return "Test task completed"
    
    result = executor.execute_task_isolated(
        'test_task_1',
        test_task,
        args=[],
        kwargs={}
    )
    
    logger.info(f"Task result: success={result.success}, output='{result.output}'")
    logger.info(f"Duration: {result.duration_seconds:.3f}s")
    
    assert result.success, f"Task should succeed but got error: {result.error}"
    assert result.duration_seconds > 0, "Task should have measurable duration"
    
    # Cleanup
    executor.cleanup_task_context('test_task_1')
    
    logger.info("✅ Task executor test passed")
    return True


def test_parallel_orchestrator():
    """Test parallel orchestrator with simple DAG"""
    logger = logging.getLogger('test_parallel_orchestrator')
    logger.info("Testing parallel orchestrator")
    
    # Create simple task graph
    tasks = {
        'task_1': TaskNode(
            task_id='task_1',
            dependencies=[],
            dependents=['task_2', 'task_3'],
            metadata={'title': 'Task 1'}
        ),
        'task_2': TaskNode(
            task_id='task_2',
            dependencies=['task_1'],
            dependents=['task_4'],
            metadata={'title': 'Task 2'}
        ),
        'task_3': TaskNode(
            task_id='task_3',
            dependencies=['task_1'],
            dependents=['task_4'],
            metadata={'title': 'Task 3'}
        ),
        'task_4': TaskNode(
            task_id='task_4',
            dependencies=['task_2', 'task_3'],
            dependents=[],
            metadata={'title': 'Task 4'}
        )
    }
    
    orchestrator = ParallelOrchestrator(max_parallel_tasks=2)
    
    # Register simple task functions
    def create_task_function(task_id):
        def task_func():
            import time
            time.sleep(0.1)
            return f"{task_id} completed"
        return task_func
    
    for task_id in tasks:
        orchestrator.register_task(task_id, create_task_function(task_id))
    
    # Execute orchestration
    result = orchestrator.orchestrate_dag_execution(
        tasks,
        execution_mode=ExecutionMode.IN_PROCESS,
        fail_fast=False
    )
    
    logger.info(f"Orchestration result:")
    logger.info(f"  Total tasks: {result.total_tasks}")
    logger.info(f"  Successful: {result.successful_tasks}")
    logger.info(f"  Failed: {result.failed_tasks}")
    logger.info(f"  Waves: {result.waves_executed}")
    logger.info(f"  Duration: {result.total_duration_seconds:.3f}s")
    logger.info(f"  Efficiency: {result.parallelization_efficiency:.2f}")
    
    assert result.successful_tasks == 4, f"All 4 tasks should succeed, got {result.successful_tasks}"
    assert result.failed_tasks == 0, f"No tasks should fail, got {result.failed_tasks}"
    assert result.waves_executed == 3, f"Should execute 3 waves, got {result.waves_executed}"
    
    # Cleanup
    orchestrator.cleanup()
    
    logger.info("✅ Parallel orchestrator test passed")
    return True


def test_task_parser():
    """Test task parser with sample markdown"""
    logger = logging.getLogger('test_task_parser')
    logger.info("Testing task parser")
    
    # Create sample markdown content
    sample_markdown = """# Test Tasks

## Phase 1: Setup
- [ ] 1.1 Initialize system
  - Set up basic configuration
  - _Requirements: 1.1_ | _Dependencies: none_

- [ ] 1.2 Configure database
  - Create database schema
  - _Requirements: 1.2_ | _Dependencies: 1.1_

## Phase 2: Implementation
- [ ] 2.1 Implement feature A
  - Build core functionality
  - _Requirements: 2.1_ | _Dependencies: 1.2_

- [ ] 2.2 Implement feature B
  - Build secondary functionality
  - _Requirements: 2.2_ | _Dependencies: 1.2_

- [ ] 2.3 Integration testing
  - Test all features together
  - _Requirements: 2.3_ | _Dependencies: 2.1, 2.2_
"""
    
    # Write to temporary file
    temp_file = Path('/tmp/test_tasks.md')
    temp_file.write_text(sample_markdown)
    
    try:
        parser = TaskParser()
        task_nodes = parser.parse_task_file(str(temp_file))
        
        logger.info(f"Parsed {len(task_nodes)} tasks")
        for task_id, node in task_nodes.items():
            logger.info(f"  {task_id}: deps={node.dependencies}, title='{node.metadata['title']}'")
        
        # Validate parsing
        assert len(task_nodes) == 5, f"Should parse 5 tasks, got {len(task_nodes)}"
        assert 'task_1.1' in task_nodes, "Should have task_1.1"
        assert 'task_2.3' in task_nodes, "Should have task_2.3"
        
        # Test DAG validation on parsed tasks
        validator = DAGValidator()
        report = validator.validate_dag(task_nodes)
        
        logger.info(f"Parsed DAG validation: valid={report.is_valid}")
        if not report.is_valid:
            logger.error(f"Validation errors: {report.validation_errors}")
        
        assert report.is_valid, "Parsed DAG should be valid"
        
    finally:
        # Cleanup
        if temp_file.exists():
            temp_file.unlink()
    
    logger.info("✅ Task parser test passed")
    return True


def main():
    """Run all tests"""
    logger = setup_logging()
    logger.info("Starting DAG orchestration system tests")
    
    tests = [
        test_dag_validator,
        test_cyclic_dag,
        test_task_executor,
        test_parallel_orchestrator,
        test_task_parser
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            logger.info(f"\n{'='*50}")
            logger.info(f"Running {test.__name__}")
            logger.info(f"{'='*50}")
            
            if test():
                passed += 1
                logger.info(f"✅ {test.__name__} PASSED")
            else:
                failed += 1
                logger.error(f"❌ {test.__name__} FAILED")
                
        except Exception as e:
            failed += 1
            logger.error(f"❌ {test.__name__} FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
    
    logger.info(f"\n{'='*50}")
    logger.info(f"TEST RESULTS")
    logger.info(f"{'='*50}")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Total:  {passed + failed}")
    
    if failed == 0:
        logger.info("🎉 All tests passed!")
        return 0
    else:
        logger.error(f"💥 {failed} tests failed!")
        return 1


if __name__ == "__main__":
    exit(main())