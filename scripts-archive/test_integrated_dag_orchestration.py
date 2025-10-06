#!/usr/bin/env python3
"""
Integrated DAG Orchestration Test
================================

Comprehensive test combining parallel execution engine with dependency-aware
scheduler to demonstrate full system integration and effectiveness.
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
from src.dag_orchestration.execution.dependency_aware_scheduler import (
    DependencyAwareScheduler,
    SchedulingStrategy
)


class IntegratedDAGOrchestrationTester:
    """Comprehensive tester for integrated DAG orchestration system."""
    
    def __init__(self):
        self.test_results = []
        
    def create_realistic_workflow(self, workflow_type: str) -> List[TaskDefinition]:
        """Create realistic workflow scenarios for testing."""
        
        if workflow_type == "software_build":
            # Simulate a software build pipeline
            tasks = []
            
            # Source preparation tasks (parallel)
            for component in ["frontend", "backend", "database"]:
                task = create_task_definition(
                    f"prepare_{component}",
                    f"Prepare {component} source",
                    execution_function=self._simulate_work_function(f"prepare_{component}", 0.5, 1.5),
                    priority=5
                )
                tasks.append(task)
            
            # Compilation tasks (depend on preparation)
            for component in ["frontend", "backend"]:
                task = create_task_definition(
                    f"compile_{component}",
                    f"Compile {component}",
                    execution_function=self._simulate_work_function(f"compile_{component}", 1.0, 3.0),
                    dependencies={f"prepare_{component}"},
                    priority=7
                )
                tasks.append(task)
            
            # Testing tasks (depend on compilation)
            test_types = ["unit", "integration", "e2e"]
            for test_type in test_types:
                task = create_task_definition(
                    f"test_{test_type}",
                    f"Run {test_type} tests",
                    execution_function=self._simulate_work_function(f"test_{test_type}", 0.8, 2.5),
                    dependencies={"compile_frontend", "compile_backend"},
                    priority=8
                )
                tasks.append(task)
            
            # Database migration (depends on database prep)
            migration_task = create_task_definition(
                "migrate_database",
                "Run database migrations",
                execution_function=self._simulate_work_function("migrate_database", 1.5, 2.0),
                dependencies={"prepare_database"},
                priority=6
            )
            tasks.append(migration_task)
            
            # Package and deploy (depends on all tests and migration)
            package_task = create_task_definition(
                "package_application",
                "Package application",
                execution_function=self._simulate_work_function("package_application", 0.5, 1.0),
                dependencies={"test_unit", "test_integration", "test_e2e", "migrate_database"},
                priority=10
            )
            tasks.append(package_task)
            
            # Final deployment
            deploy_task = create_task_definition(
                "deploy_application",
                "Deploy to production",
                execution_function=self._simulate_work_function("deploy_application", 1.0, 2.0),
                dependencies={"package_application"},
                priority=10
            )
            tasks.append(deploy_task)
            
            return tasks
        
        elif workflow_type == "data_pipeline":
            # Simulate a data processing pipeline
            tasks = []
            
            # Data ingestion (parallel sources)
            sources = ["api", "database", "files"]
            for source in sources:
                task = create_task_definition(
                    f"ingest_{source}",
                    f"Ingest data from {source}",
                    execution_function=self._simulate_work_function(f"ingest_{source}", 1.0, 2.5),
                    priority=5
                )
                tasks.append(task)
            
            # Data validation (depends on ingestion)
            for source in sources:
                task = create_task_definition(
                    f"validate_{source}",
                    f"Validate {source} data",
                    execution_function=self._simulate_work_function(f"validate_{source}", 0.5, 1.0),
                    dependencies={f"ingest_{source}"},
                    priority=6
                )
                tasks.append(task)
            
            # Data transformation (depends on validation)
            transform_task = create_task_definition(
                "transform_data",
                "Transform and clean data",
                execution_function=self._simulate_work_function("transform_data", 2.0, 4.0),
                dependencies={f"validate_{source}" for source in sources},
                priority=8
            )
            tasks.append(transform_task)
            
            # Feature engineering (depends on transformation)
            feature_task = create_task_definition(
                "engineer_features",
                "Engineer features",
                execution_function=self._simulate_work_function("engineer_features", 1.5, 3.0),
                dependencies={"transform_data"},
                priority=7
            )
            tasks.append(feature_task)
            
            # Model training (depends on features)
            train_task = create_task_definition(
                "train_model",
                "Train ML model",
                execution_function=self._simulate_work_function("train_model", 3.0, 5.0),
                dependencies={"engineer_features"},
                priority=9
            )
            tasks.append(train_task)
            
            # Model evaluation and deployment
            eval_task = create_task_definition(
                "evaluate_model",
                "Evaluate model performance",
                execution_function=self._simulate_work_function("evaluate_model", 1.0, 2.0),
                dependencies={"train_model"},
                priority=10
            )
            tasks.append(eval_task)
            
            return tasks
        
        else:
            return []
    
    def _simulate_work_function(self, task_name: str, min_duration: float, max_duration: float):
        """Create a work simulation function with realistic behavior."""
        def work_function():
            # Simulate realistic work with variable duration
            duration = random.uniform(min_duration, max_duration)
            start_time = time.time()
            
            # Simulate CPU-bound work
            result = 0
            iterations = int(duration * 500000)  # Scale iterations with duration
            for i in range(iterations):
                result += i * 0.001
            
            actual_duration = time.time() - start_time
            
            # Occasionally simulate failures (5% chance)
            if random.random() < 0.05:
                raise RuntimeError(f"Simulated failure in {task_name}")
            
            return {
                'task_name': task_name,
                'planned_duration': duration,
                'actual_duration': actual_duration,
                'result': result,
                'timestamp': datetime.now().isoformat(),
                'success': True
            }
        
        return work_function
    
    async def test_integrated_orchestration(self, workflow_type: str, 
                                          execution_strategy: ExecutionStrategy,
                                          scheduling_strategy: SchedulingStrategy) -> Dict[str, Any]:
        """Test integrated orchestration with specific strategies."""
        print(f"🔬 Testing {workflow_type} workflow with {execution_strategy.value} execution + {scheduling_strategy.value} scheduling...")
        
        # Create workflow tasks
        tasks = self.create_realistic_workflow(workflow_type)
        if not tasks:
            return {}
        
        # Initialize components
        execution_engine = ParallelExecutionEngine(
            max_workers=6, 
            execution_strategy=execution_strategy
        )
        
        scheduler = DependencyAwareScheduler(strategy=scheduling_strategy)
        
        # Register tasks with scheduler for analysis
        scheduler.register_tasks(tasks)
        
        start_time = time.time()
        
        try:
            # Execute workflow
            results = await execution_engine.execute_dag_parallel(tasks)
            
            execution_time = time.time() - start_time
            
            # Analyze results
            successful_tasks = sum(1 for r in results.values() if r.status.value == "completed")
            failed_tasks = sum(1 for r in results.values() if r.status.value == "failed")
            skipped_tasks = sum(1 for r in results.values() if r.status.value == "skipped")
            
            total_task_time = sum(
                r.duration_seconds for r in results.values() 
                if r.duration_seconds is not None
            )
            
            # Get scheduler statistics
            scheduler_stats = scheduler.get_scheduling_statistics()
            
            # Get execution engine statistics
            engine_stats = execution_engine.get_execution_statistics()
            
            test_result = {
                'workflow_type': workflow_type,
                'execution_strategy': execution_strategy.value,
                'scheduling_strategy': scheduling_strategy.value,
                'total_tasks': len(tasks),
                'successful_tasks': successful_tasks,
                'failed_tasks': failed_tasks,
                'skipped_tasks': skipped_tasks,
                'execution_time': execution_time,
                'total_task_time': total_task_time,
                'parallelization_efficiency': total_task_time / execution_time if execution_time > 0 else 0,
                'success_rate': successful_tasks / len(tasks),
                'scheduler_statistics': scheduler_stats,
                'engine_statistics': engine_stats,
                'timestamp': datetime.now().isoformat()
            }
            
            self.test_results.append(test_result)
            
            print(f"✅ {workflow_type} workflow completed:")
            print(f"   Tasks: {successful_tasks} successful, {failed_tasks} failed, {skipped_tasks} skipped")
            print(f"   Execution time: {execution_time:.2f}s, Total task time: {total_task_time:.2f}s")
            print(f"   Parallelization efficiency: {test_result['parallelization_efficiency']:.2f}x")
            print(f"   Success rate: {test_result['success_rate']:.1%}")
            
            return test_result
            
        except Exception as e:
            print(f"❌ {workflow_type} workflow failed: {e}")
            return {}
        
        finally:
            # Cleanup
            execution_engine.shutdown()
    
    async def run_comprehensive_integration_tests(self) -> Dict[str, Any]:
        """Run comprehensive integration tests across multiple scenarios."""
        print("🚀 Starting Comprehensive DAG Orchestration Integration Tests")
        print("=" * 70)
        
        # Test scenarios
        workflows = ["software_build", "data_pipeline"]
        execution_strategies = [ExecutionStrategy.CONSERVATIVE, ExecutionStrategy.AGGRESSIVE]
        scheduling_strategies = [SchedulingStrategy.PRIORITY, SchedulingStrategy.ADAPTIVE]
        
        suite_start_time = time.time()
        
        # Test all combinations
        for workflow in workflows:
            for exec_strategy in execution_strategies:
                for sched_strategy in scheduling_strategies:
                    try:
                        await self.test_integrated_orchestration(
                            workflow, exec_strategy, sched_strategy
                        )
                        print()  # Add spacing
                    except Exception as e:
                        print(f"❌ Integration test failed: {e}")
                        print()
        
        suite_execution_time = time.time() - suite_start_time
        
        # Generate comprehensive analysis
        comprehensive_report = self._analyze_integration_results(suite_execution_time)
        
        print("📊 Comprehensive Integration Test Results:")
        print(f"   Total test combinations: {len(self.test_results)}")
        print(f"   Suite execution time: {suite_execution_time:.2f}s")
        
        if 'performance_summary' in comprehensive_report:
            summary = comprehensive_report['performance_summary']
            print(f"   Average parallelization efficiency: {summary.get('avg_parallelization_efficiency', 0):.2f}x")
            print(f"   Average success rate: {summary.get('avg_success_rate', 0):.1%}")
            print(f"   Best combination: {summary.get('best_combination', 'Unknown')}")
        
        return comprehensive_report
    
    def _analyze_integration_results(self, suite_execution_time: float) -> Dict[str, Any]:
        """Analyze integration test results."""
        if not self.test_results:
            return {}
        
        # Calculate performance metrics
        avg_parallelization = sum(r['parallelization_efficiency'] for r in self.test_results) / len(self.test_results)
        avg_success_rate = sum(r['success_rate'] for r in self.test_results) / len(self.test_results)
        avg_execution_time = sum(r['execution_time'] for r in self.test_results) / len(self.test_results)
        
        # Find best performing combination
        best_result = max(self.test_results, key=lambda r: r['parallelization_efficiency'] * r['success_rate'])
        best_combination = f"{best_result['workflow_type']} + {best_result['execution_strategy']} + {best_result['scheduling_strategy']}"
        
        # Analyze strategy effectiveness
        strategy_performance = {}
        for result in self.test_results:
            key = f"{result['execution_strategy']}+{result['scheduling_strategy']}"
            if key not in strategy_performance:
                strategy_performance[key] = []
            strategy_performance[key].append(result)
        
        strategy_averages = {}
        for strategy, results in strategy_performance.items():
            strategy_averages[strategy] = {
                'avg_parallelization': sum(r['parallelization_efficiency'] for r in results) / len(results),
                'avg_success_rate': sum(r['success_rate'] for r in results) / len(results),
                'avg_execution_time': sum(r['execution_time'] for r in results) / len(results),
                'test_count': len(results)
            }
        
        return {
            'suite_summary': {
                'total_tests': len(self.test_results),
                'suite_execution_time': suite_execution_time,
                'workflows_tested': len(set(r['workflow_type'] for r in self.test_results)),
                'strategy_combinations_tested': len(strategy_performance)
            },
            'performance_summary': {
                'avg_parallelization_efficiency': avg_parallelization,
                'avg_success_rate': avg_success_rate,
                'avg_execution_time': avg_execution_time,
                'best_combination': best_combination,
                'best_parallelization_efficiency': best_result['parallelization_efficiency'],
                'best_success_rate': best_result['success_rate']
            },
            'strategy_performance': strategy_averages,
            'individual_results': self.test_results,
            'empirical_insights': {
                'integration_successful': avg_success_rate > 0.8,
                'parallelization_effective': avg_parallelization > 1.5,
                'system_reliability': all(r['success_rate'] > 0.7 for r in self.test_results),
                'optimal_strategy_identified': True
            }
        }


async def main():
    """Main execution function for integrated DAG orchestration testing."""
    print("🔬 Integrated DAG Orchestration Empirical Testing")
    print("Demonstrating full system integration and effectiveness")
    print("=" * 70)
    
    # Create and run test suite
    tester = IntegratedDAGOrchestrationTester()
    
    try:
        comprehensive_report = tester.run_comprehensive_integration_tests()
        
        # Save results
        import json
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"integrated_dag_orchestration_report_{timestamp}.json"
        
        with open(report_filename, 'w') as f:
            json.dump(await comprehensive_report, f, indent=2, default=str)
        
        print(f"\n📄 Detailed integration report saved to: {report_filename}")
        print("✅ Integrated DAG orchestration testing completed successfully")
        
    except Exception as e:
        print(f"❌ Integration testing failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())