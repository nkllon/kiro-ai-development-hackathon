#!/usr/bin/env python3
"""
Empirical Testing of Parallel Execution Engine
==============================================

Real-world testing scenarios to generate empirical data about
parallel execution effectiveness and agent coordination patterns.
"""

import asyncio
import time
import random
from typing import List, Dict, Any
from datetime import datetime

from src.dag_orchestration.execution.parallel_execution_engine import (
    ParallelExecutionEngine,
    TaskDefinition,
    ExecutionStrategy,
    create_task_definition
)


class EmpiricalTestSuite:
    """Test suite for generating empirical data about parallel execution."""
    
    def __init__(self):
        self.engine = ParallelExecutionEngine(max_workers=8, execution_strategy=ExecutionStrategy.CONSERVATIVE)
        self.test_results = []
        
    def create_sample_task_function(self, task_name: str, duration_range: tuple = (0.1, 2.0)):
        """Create a sample task function with realistic work simulation."""
        def task_function():
            # Simulate realistic work with variable duration
            work_duration = random.uniform(*duration_range)
            start_time = time.time()
            
            # Simulate CPU work
            result = 0
            iterations = int(work_duration * 1000000)  # Scale iterations with duration
            for i in range(iterations):
                result += i * 0.001
            
            actual_duration = time.time() - start_time
            
            return {
                'task_name': task_name,
                'planned_duration': work_duration,
                'actual_duration': actual_duration,
                'result': result,
                'timestamp': datetime.now().isoformat()
            }
        
        return task_function
    
    async def test_simple_parallel_execution(self) -> Dict[str, Any]:
        """Test basic parallel execution without dependencies."""
        print("🔬 Testing Simple Parallel Execution...")
        
        # Create independent tasks
        tasks = []
        for i in range(10):
            task = create_task_definition(
                task_id=f"simple_task_{i}",
                name=f"Simple Task {i}",
                execution_function=self.create_sample_task_function(f"SimpleTask{i}", (0.2, 1.0))
            )
            tasks.append(task)
        
        start_time = time.time()
        results = await self.engine.execute_dag_parallel(tasks)
        execution_time = time.time() - start_time
        
        # Analyze results
        successful_tasks = sum(1 for r in results.values() if r.status.value == "completed")
        total_task_time = sum(r.duration_seconds for r in results.values() if r.duration_seconds)
        
        test_result = {
            'test_name': 'simple_parallel_execution',
            'total_tasks': len(tasks),
            'successful_tasks': successful_tasks,
            'execution_time': execution_time,
            'total_task_time': total_task_time,
            'parallelization_efficiency': total_task_time / execution_time if execution_time > 0 else 0,
            'success_rate': successful_tasks / len(tasks),
            'timestamp': datetime.now().isoformat()
        }
        
        self.test_results.append(test_result)
        print(f"✅ Simple parallel execution completed: {successful_tasks}/{len(tasks)} tasks successful")
        print(f"   Execution time: {execution_time:.2f}s, Total task time: {total_task_time:.2f}s")
        print(f"   Parallelization efficiency: {test_result['parallelization_efficiency']:.2f}x")
        
        return test_result
    
    async def test_dependency_chain_execution(self) -> Dict[str, Any]:
        """Test execution with linear dependency chain."""
        print("🔬 Testing Dependency Chain Execution...")
        
        # Create tasks with linear dependencies
        tasks = []
        for i in range(8):
            dependencies = {f"chain_task_{i-1}"} if i > 0 else set()
            task = create_task_definition(
                task_id=f"chain_task_{i}",
                name=f"Chain Task {i}",
                execution_function=self.create_sample_task_function(f"ChainTask{i}", (0.3, 0.8)),
                dependencies=dependencies
            )
            tasks.append(task)
        
        start_time = time.time()
        results = await self.engine.execute_dag_parallel(tasks)
        execution_time = time.time() - start_time
        
        # Analyze results
        successful_tasks = sum(1 for r in results.values() if r.status.value == "completed")
        total_task_time = sum(r.duration_seconds for r in results.values() if r.duration_seconds)
        
        test_result = {
            'test_name': 'dependency_chain_execution',
            'total_tasks': len(tasks),
            'successful_tasks': successful_tasks,
            'execution_time': execution_time,
            'total_task_time': total_task_time,
            'parallelization_efficiency': total_task_time / execution_time if execution_time > 0 else 0,
            'success_rate': successful_tasks / len(tasks),
            'timestamp': datetime.now().isoformat()
        }
        
        self.test_results.append(test_result)
        print(f"✅ Dependency chain execution completed: {successful_tasks}/{len(tasks)} tasks successful")
        print(f"   Execution time: {execution_time:.2f}s, Total task time: {total_task_time:.2f}s")
        print(f"   Parallelization efficiency: {test_result['parallelization_efficiency']:.2f}x")
        
        return test_result
    
    async def test_complex_dag_execution(self) -> Dict[str, Any]:
        """Test execution with complex DAG structure."""
        print("🔬 Testing Complex DAG Execution...")
        
        # Create complex DAG structure
        # Layer 1: Independent foundation tasks
        tasks = []
        
        # Foundation tasks (no dependencies)
        for i in range(3):
            task = create_task_definition(
                task_id=f"foundation_{i}",
                name=f"Foundation Task {i}",
                execution_function=self.create_sample_task_function(f"Foundation{i}", (0.2, 0.6))
            )
            tasks.append(task)
        
        # Layer 2: Tasks depending on foundation
        for i in range(4):
            dependencies = {f"foundation_{i % 3}"}  # Distribute dependencies
            task = create_task_definition(
                task_id=f"layer2_{i}",
                name=f"Layer 2 Task {i}",
                execution_function=self.create_sample_task_function(f"Layer2_{i}", (0.3, 0.9)),
                dependencies=dependencies
            )
            tasks.append(task)
        
        # Layer 3: Tasks with multiple dependencies
        for i in range(2):
            dependencies = {f"layer2_{i*2}", f"layer2_{i*2+1}"}
            task = create_task_definition(
                task_id=f"layer3_{i}",
                name=f"Layer 3 Task {i}",
                execution_function=self.create_sample_task_function(f"Layer3_{i}", (0.4, 1.2)),
                dependencies=dependencies
            )
            tasks.append(task)
        
        # Final task depending on all layer 3 tasks
        final_task = create_task_definition(
            task_id="final_task",
            name="Final Integration Task",
            execution_function=self.create_sample_task_function("FinalTask", (0.5, 1.5)),
            dependencies={"layer3_0", "layer3_1"}
        )
        tasks.append(final_task)
        
        start_time = time.time()
        results = await self.engine.execute_dag_parallel(tasks)
        execution_time = time.time() - start_time
        
        # Analyze results
        successful_tasks = sum(1 for r in results.values() if r.status.value == "completed")
        total_task_time = sum(r.duration_seconds for r in results.values() if r.duration_seconds)
        
        test_result = {
            'test_name': 'complex_dag_execution',
            'total_tasks': len(tasks),
            'successful_tasks': successful_tasks,
            'execution_time': execution_time,
            'total_task_time': total_task_time,
            'parallelization_efficiency': total_task_time / execution_time if execution_time > 0 else 0,
            'success_rate': successful_tasks / len(tasks),
            'dag_layers': 4,
            'max_parallel_tasks': 4,  # Layer 2 has 4 tasks that can run in parallel
            'timestamp': datetime.now().isoformat()
        }
        
        self.test_results.append(test_result)
        print(f"✅ Complex DAG execution completed: {successful_tasks}/{len(tasks)} tasks successful")
        print(f"   Execution time: {execution_time:.2f}s, Total task time: {total_task_time:.2f}s")
        print(f"   Parallelization efficiency: {test_result['parallelization_efficiency']:.2f}x")
        
        return test_result
    
    async def test_failure_isolation(self) -> Dict[str, Any]:
        """Test failure isolation and dependent task handling."""
        print("🔬 Testing Failure Isolation...")
        
        def failing_task():
            """Task that always fails."""
            time.sleep(0.2)  # Simulate some work before failing
            raise RuntimeError("Intentional test failure")
        
        # Create tasks with one failing task
        tasks = []
        
        # Independent successful tasks
        for i in range(3):
            task = create_task_definition(
                task_id=f"success_{i}",
                name=f"Success Task {i}",
                execution_function=self.create_sample_task_function(f"Success{i}", (0.2, 0.5))
            )
            tasks.append(task)
        
        # Failing task
        failing_task_def = create_task_definition(
            task_id="failing_task",
            name="Failing Task",
            execution_function=failing_task
        )
        tasks.append(failing_task_def)
        
        # Tasks that depend on the failing task (should be skipped)
        for i in range(2):
            task = create_task_definition(
                task_id=f"dependent_{i}",
                name=f"Dependent Task {i}",
                execution_function=self.create_sample_task_function(f"Dependent{i}", (0.3, 0.7)),
                dependencies={"failing_task"}
            )
            tasks.append(task)
        
        # Task that depends on successful tasks (should complete)
        independent_dependent = create_task_definition(
            task_id="independent_dependent",
            name="Independent Dependent Task",
            execution_function=self.create_sample_task_function("IndependentDependent", (0.4, 0.8)),
            dependencies={"success_0", "success_1"}
        )
        tasks.append(independent_dependent)
        
        start_time = time.time()
        results = await self.engine.execute_dag_parallel(tasks)
        execution_time = time.time() - start_time
        
        # Analyze results
        successful_tasks = sum(1 for r in results.values() if r.status.value == "completed")
        failed_tasks = sum(1 for r in results.values() if r.status.value == "failed")
        skipped_tasks = sum(1 for r in results.values() if r.status.value == "skipped")
        
        test_result = {
            'test_name': 'failure_isolation',
            'total_tasks': len(tasks),
            'successful_tasks': successful_tasks,
            'failed_tasks': failed_tasks,
            'skipped_tasks': skipped_tasks,
            'execution_time': execution_time,
            'isolation_effectiveness': (successful_tasks + skipped_tasks) / len(tasks),
            'timestamp': datetime.now().isoformat()
        }
        
        self.test_results.append(test_result)
        print(f"✅ Failure isolation test completed:")
        print(f"   Successful: {successful_tasks}, Failed: {failed_tasks}, Skipped: {skipped_tasks}")
        print(f"   Isolation effectiveness: {test_result['isolation_effectiveness']:.2%}")
        
        return test_result
    
    async def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """Run all empirical tests and generate comprehensive report."""
        print("🚀 Starting Comprehensive Empirical Test Suite")
        print("=" * 60)
        
        suite_start_time = time.time()
        
        # Run all test scenarios
        test_scenarios = [
            self.test_simple_parallel_execution,
            self.test_dependency_chain_execution,
            self.test_complex_dag_execution,
            self.test_failure_isolation
        ]
        
        for test_func in test_scenarios:
            try:
                await test_func()
                print()  # Add spacing between tests
            except Exception as e:
                print(f"❌ Test {test_func.__name__} failed: {e}")
                print()
        
        suite_execution_time = time.time() - suite_start_time
        
        # Generate comprehensive report
        total_tasks = sum(result['total_tasks'] for result in self.test_results)
        total_successful = sum(result['successful_tasks'] for result in self.test_results)
        avg_parallelization_efficiency = sum(
            result.get('parallelization_efficiency', 0) for result in self.test_results
        ) / len(self.test_results) if self.test_results else 0
        
        # Get engine statistics
        engine_stats = self.engine.get_execution_statistics()
        
        comprehensive_report = {
            'suite_summary': {
                'total_test_scenarios': len(test_scenarios),
                'successful_scenarios': len(self.test_results),
                'suite_execution_time': suite_execution_time,
                'total_tasks_across_all_tests': total_tasks,
                'total_successful_tasks': total_successful,
                'overall_success_rate': total_successful / total_tasks if total_tasks > 0 else 0,
                'average_parallelization_efficiency': avg_parallelization_efficiency,
                'timestamp': datetime.now().isoformat()
            },
            'individual_test_results': self.test_results,
            'engine_statistics': engine_stats,
            'empirical_insights': {
                'parallel_execution_effectiveness': avg_parallelization_efficiency > 2.0,
                'failure_isolation_working': any(
                    result.get('isolation_effectiveness', 0) > 0.8 
                    for result in self.test_results 
                    if result['test_name'] == 'failure_isolation'
                ),
                'dependency_management_functional': any(
                    result.get('success_rate', 0) > 0.9 
                    for result in self.test_results 
                    if 'dependency' in result['test_name']
                )
            }
        }
        
        print("📊 Comprehensive Test Suite Results:")
        print(f"   Test scenarios executed: {comprehensive_report['suite_summary']['successful_scenarios']}")
        print(f"   Total tasks executed: {total_tasks}")
        print(f"   Overall success rate: {comprehensive_report['suite_summary']['overall_success_rate']:.2%}")
        print(f"   Average parallelization efficiency: {avg_parallelization_efficiency:.2f}x")
        print(f"   Suite execution time: {suite_execution_time:.2f}s")
        
        return comprehensive_report


async def main():
    """Main execution function for empirical testing."""
    print("🔬 Empirical Parallel Execution Testing")
    print("Generating real-world data for agent effectiveness analysis")
    print("=" * 70)
    
    # Create and run test suite
    test_suite = EmpiricalTestSuite()
    
    try:
        comprehensive_report = await test_suite.run_comprehensive_test_suite()
        
        # Save results for analysis
        import json
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"empirical_parallel_execution_report_{timestamp}.json"
        
        with open(report_filename, 'w') as f:
            json.dump(comprehensive_report, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: {report_filename}")
        print("✅ Empirical testing completed successfully")
        
    except Exception as e:
        print(f"❌ Empirical testing failed: {e}")
        raise
    
    finally:
        # Cleanup
        test_suite.engine.shutdown()


if __name__ == "__main__":
    asyncio.run(main())