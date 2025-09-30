#!/usr/bin/env python3
"""
Test Dependency-Aware Scheduler
==============================

Comprehensive testing of the dependency-aware scheduler to generate
empirical data about intelligent task scheduling effectiveness.
"""

import asyncio
import time
import random
from typing import List, Dict, Any
from datetime import datetime

from src.dag_orchestration.execution.dependency_aware_scheduler import (
    DependencyAwareScheduler,
    SchedulingStrategy,
    create_dependency_aware_scheduler
)
from src.dag_orchestration.execution.parallel_execution_engine import (
    TaskDefinition,
    create_task_definition,
    ExecutionContext,
    ExecutionStrategy
)


class SchedulerEmpiricalTester:
    """Empirical testing suite for dependency-aware scheduler."""
    
    def __init__(self):
        self.test_results = []
        
    def create_test_tasks(self, scenario: str) -> List[TaskDefinition]:
        """Create test tasks for different scheduling scenarios."""
        
        if scenario == "simple_priority":
            # Tasks with different priorities
            return [
                create_task_definition("high_priority", "High Priority Task", priority=10),
                create_task_definition("medium_priority", "Medium Priority Task", priority=5),
                create_task_definition("low_priority", "Low Priority Task", priority=1),
                create_task_definition("normal_priority", "Normal Priority Task", priority=3)
            ]
        
        elif scenario == "complex_dependencies":
            # Complex dependency structure for critical path testing
            tasks = []
            
            # Foundation layer (no dependencies)
            for i in range(3):
                task = create_task_definition(
                    f"foundation_{i}", 
                    f"Foundation Task {i}",
                    priority=5
                )
                task.estimated_duration = 2.0
                tasks.append(task)
            
            # Middle layer (depends on foundation)
            for i in range(4):
                deps = {f"foundation_{i % 3}"}
                task = create_task_definition(
                    f"middle_{i}",
                    f"Middle Task {i}",
                    dependencies=deps,
                    priority=3
                )
                task.estimated_duration = 1.5
                tasks.append(task)
            
            # Critical path task (long duration)
            critical_task = create_task_definition(
                "critical_long",
                "Critical Long Task",
                dependencies={"foundation_1"},
                priority=8
            )
            critical_task.estimated_duration = 5.0
            tasks.append(critical_task)
            
            # Final layer (depends on critical path)
            final_task = create_task_definition(
                "final",
                "Final Task",
                dependencies={"critical_long", "middle_2"},
                priority=10
            )
            final_task.estimated_duration = 1.0
            tasks.append(final_task)
            
            return tasks
        
        elif scenario == "resource_intensive":
            # Tasks with different resource requirements
            tasks = []
            
            # Light tasks
            for i in range(5):
                task = create_task_definition(f"light_{i}", f"Light Task {i}")
                task.resource_requirements = {"weight": 0.5}
                task.estimated_duration = 0.5
                tasks.append(task)
            
            # Heavy tasks
            for i in range(2):
                task = create_task_definition(f"heavy_{i}", f"Heavy Task {i}")
                task.resource_requirements = {"weight": 3.0}
                task.estimated_duration = 3.0
                tasks.append(task)
            
            # Mixed dependency task
            mixed_task = create_task_definition(
                "mixed",
                "Mixed Task",
                dependencies={"light_0", "heavy_0"}
            )
            mixed_task.resource_requirements = {"weight": 1.5}
            mixed_task.estimated_duration = 2.0
            tasks.append(mixed_task)
            
            return tasks
        
        else:
            return []
    
    def test_scheduling_strategy(self, strategy: SchedulingStrategy, scenario: str) -> Dict[str, Any]:
        """Test a specific scheduling strategy with a given scenario."""
        print(f"🔬 Testing {strategy.value} strategy with {scenario} scenario...")
        
        # Create scheduler and tasks
        scheduler = create_dependency_aware_scheduler(strategy)
        tasks = self.create_test_tasks(scenario)
        
        if not tasks:
            return {}
        
        start_time = time.time()
        
        # Register tasks
        scheduler.register_tasks(tasks)
        
        # Simulate scheduling decisions
        scheduling_decisions = []
        execution_context = ExecutionContext(
            execution_id="test_execution",
            strategy=ExecutionStrategy.CONSERVATIVE,
            max_workers=4,
            start_time=datetime.now()
        )
        
        # Add tasks to context
        for task in tasks:
            execution_context.tasks[task.task_id] = task
        
        # Simulate execution by getting scheduling decisions
        remaining_tasks = set(task.task_id for task in tasks)
        completed_tasks = set()
        
        while remaining_tasks:
            # Get next ready tasks
            ready_decisions = scheduler.get_next_ready_tasks(
                max_tasks=2, 
                execution_context=execution_context
            )
            
            if not ready_decisions:
                # No more ready tasks, simulate completion of a random active task
                if execution_context.active_futures:
                    # Pick a random active task to complete
                    completed_task = random.choice(list(execution_context.active_futures.keys()))
                    execution_context.active_futures.pop(completed_task)
                    execution_context.completed_tasks.add(completed_task)
                    completed_tasks.add(completed_task)
                    remaining_tasks.discard(completed_task)
                    
                    # Notify scheduler
                    newly_ready = scheduler.notify_task_completion(completed_task, success=True)
                    
                else:
                    break  # No progress possible
            else:
                # Process scheduling decisions
                for decision in ready_decisions:
                    scheduling_decisions.append(decision)
                    execution_context.active_futures[decision.task_id] = None  # Simulate future
                    remaining_tasks.discard(decision.task_id)
        
        execution_time = time.time() - start_time
        
        # Get scheduler statistics
        stats = scheduler.get_scheduling_statistics()
        
        # Analyze results
        total_estimated_duration = sum(
            getattr(task, 'estimated_duration', 1.0) for task in tasks
        )
        
        # Calculate scheduling efficiency metrics
        if scheduling_decisions:
            avg_priority_score = sum(d.priority_score for d in scheduling_decisions) / len(scheduling_decisions)
            scheduling_order_quality = self._evaluate_scheduling_order(scheduling_decisions, tasks)
        else:
            avg_priority_score = 0.0
            scheduling_order_quality = 0.0
        
        test_result = {
            'strategy': strategy.value,
            'scenario': scenario,
            'total_tasks': len(tasks),
            'scheduling_decisions': len(scheduling_decisions),
            'execution_time': execution_time,
            'total_estimated_duration': total_estimated_duration,
            'avg_priority_score': avg_priority_score,
            'scheduling_order_quality': scheduling_order_quality,
            'scheduler_statistics': stats,
            'timestamp': datetime.now().isoformat()
        }
        
        self.test_results.append(test_result)
        
        print(f"✅ {strategy.value} strategy completed:")
        print(f"   Scheduling decisions: {len(scheduling_decisions)}")
        print(f"   Execution time: {execution_time:.3f}s")
        print(f"   Average priority score: {avg_priority_score:.2f}")
        print(f"   Scheduling quality: {scheduling_order_quality:.2f}")
        
        return test_result
    
    def _evaluate_scheduling_order(self, decisions: List, tasks: List[TaskDefinition]) -> float:
        """Evaluate the quality of scheduling order (0.0 to 1.0)."""
        if not decisions:
            return 0.0
        
        # Simple heuristic: higher priority tasks should be scheduled earlier
        task_priorities = {task.task_id: task.priority for task in tasks}
        
        quality_score = 0.0
        total_comparisons = 0
        
        for i, decision1 in enumerate(decisions):
            for j, decision2 in enumerate(decisions[i+1:], i+1):
                priority1 = task_priorities.get(decision1.task_id, 0)
                priority2 = task_priorities.get(decision2.task_id, 0)
                
                # If higher priority task is scheduled first, that's good
                if priority1 >= priority2:
                    quality_score += 1.0
                
                total_comparisons += 1
        
        return quality_score / max(total_comparisons, 1)
    
    def run_comprehensive_scheduler_tests(self) -> Dict[str, Any]:
        """Run comprehensive tests across all strategies and scenarios."""
        print("🚀 Starting Comprehensive Scheduler Testing")
        print("=" * 60)
        
        strategies = [
            SchedulingStrategy.FIFO,
            SchedulingStrategy.PRIORITY,
            SchedulingStrategy.CRITICAL_PATH,
            SchedulingStrategy.RESOURCE_AWARE,
            SchedulingStrategy.ADAPTIVE
        ]
        
        scenarios = [
            "simple_priority",
            "complex_dependencies", 
            "resource_intensive"
        ]
        
        suite_start_time = time.time()
        
        # Test all combinations
        for strategy in strategies:
            for scenario in scenarios:
                try:
                    self.test_scheduling_strategy(strategy, scenario)
                    print()  # Add spacing
                except Exception as e:
                    print(f"❌ Test failed for {strategy.value} + {scenario}: {e}")
                    print()
        
        suite_execution_time = time.time() - suite_start_time
        
        # Generate comprehensive analysis
        comprehensive_report = self._analyze_all_results(suite_execution_time)
        
        print("📊 Comprehensive Scheduler Test Results:")
        print(f"   Total test combinations: {len(self.test_results)}")
        print(f"   Suite execution time: {suite_execution_time:.2f}s")
        
        if 'best_strategies' in comprehensive_report:
            best = comprehensive_report['best_strategies']
            print(f"   Best overall strategy: {best.get('overall', 'Unknown')}")
            print(f"   Best for priority handling: {best.get('priority_handling', 'Unknown')}")
            print(f"   Best for complex dependencies: {best.get('dependency_handling', 'Unknown')}")
        
        return comprehensive_report
    
    def _analyze_all_results(self, suite_execution_time: float) -> Dict[str, Any]:
        """Analyze all test results to generate insights."""
        if not self.test_results:
            return {}
        
        # Group results by strategy and scenario
        strategy_performance = {}
        scenario_performance = {}
        
        for result in self.test_results:
            strategy = result['strategy']
            scenario = result['scenario']
            
            if strategy not in strategy_performance:
                strategy_performance[strategy] = []
            strategy_performance[strategy].append(result)
            
            if scenario not in scenario_performance:
                scenario_performance[scenario] = []
            scenario_performance[scenario].append(result)
        
        # Calculate average performance metrics
        strategy_averages = {}
        for strategy, results in strategy_performance.items():
            avg_execution_time = sum(r['execution_time'] for r in results) / len(results)
            avg_quality = sum(r['scheduling_order_quality'] for r in results) / len(results)
            avg_priority_score = sum(r['avg_priority_score'] for r in results) / len(results)
            
            strategy_averages[strategy] = {
                'avg_execution_time': avg_execution_time,
                'avg_scheduling_quality': avg_quality,
                'avg_priority_score': avg_priority_score,
                'test_count': len(results)
            }
        
        # Identify best strategies
        best_strategies = {
            'overall': max(strategy_averages.keys(), 
                          key=lambda s: strategy_averages[s]['avg_scheduling_quality']),
            'fastest': min(strategy_averages.keys(),
                          key=lambda s: strategy_averages[s]['avg_execution_time']),
            'highest_priority': max(strategy_averages.keys(),
                                  key=lambda s: strategy_averages[s]['avg_priority_score'])
        }
        
        # Calculate improvement metrics
        baseline_quality = strategy_averages.get('fifo', {}).get('avg_scheduling_quality', 0)
        best_quality = max(s['avg_scheduling_quality'] for s in strategy_averages.values())
        quality_improvement = ((best_quality - baseline_quality) / max(baseline_quality, 0.01)) * 100
        
        return {
            'suite_summary': {
                'total_tests': len(self.test_results),
                'suite_execution_time': suite_execution_time,
                'strategies_tested': len(strategy_performance),
                'scenarios_tested': len(scenario_performance)
            },
            'strategy_performance': strategy_averages,
            'best_strategies': best_strategies,
            'performance_improvements': {
                'scheduling_quality_improvement_percent': quality_improvement,
                'baseline_strategy': 'fifo',
                'best_strategy': best_strategies['overall']
            },
            'individual_results': self.test_results,
            'empirical_insights': {
                'adaptive_strategy_effective': strategy_averages.get('adaptive', {}).get('avg_scheduling_quality', 0) > baseline_quality,
                'critical_path_optimization_working': strategy_averages.get('critical_path', {}).get('avg_scheduling_quality', 0) > baseline_quality,
                'resource_awareness_beneficial': strategy_averages.get('resource_aware', {}).get('avg_scheduling_quality', 0) > baseline_quality
            }
        }


async def main():
    """Main execution function for scheduler empirical testing."""
    print("🔬 Dependency-Aware Scheduler Empirical Testing")
    print("Generating data on intelligent task scheduling effectiveness")
    print("=" * 70)
    
    # Create and run test suite
    tester = SchedulerEmpiricalTester()
    
    try:
        comprehensive_report = tester.run_comprehensive_scheduler_tests()
        
        # Save results
        import json
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"scheduler_empirical_report_{timestamp}.json"
        
        with open(report_filename, 'w') as f:
            json.dump(comprehensive_report, f, indent=2, default=str)
        
        print(f"\n📄 Detailed scheduler report saved to: {report_filename}")
        print("✅ Scheduler empirical testing completed successfully")
        
    except Exception as e:
        print(f"❌ Scheduler testing failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())