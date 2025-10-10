#!/usr/bin/env python3
"""
DAG Orchestration Interactive Demo
=================================

An interactive command-line interface for exploring DAG orchestration capabilities.
This demo allows users to create custom DAGs, experiment with different strategies,
and see real-time execution results.

Usage:
    python examples/demos/dag_orchestration_interactive.py

Author: Beast Mode Framework
Date: 2025-01-27
"""

import os
import sys
import time
import asyncio
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Set

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import DAG orchestration components
try:
    from src.dag_orchestration.core.dag_orchestrator import (
        DAGOrchestrator, OrchestrationConfig, OrchestrationResult
    )
    from src.dag_orchestration.execution.parallel_execution_engine import (
        ParallelExecutionEngine, TaskDefinition, ExecutionStrategy, 
        TaskExecutionStatus, create_task_definition
    )
    from src.dag_orchestration.execution.dependency_aware_scheduler import (
        DependencyAwareScheduler, SchedulingStrategy
    )
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  DAG orchestration modules not available: {e}")
    IMPORTS_AVAILABLE = False


class InteractiveDAGDemo:
    """Interactive DAG orchestration demonstration."""
    
    def __init__(self):
        if IMPORTS_AVAILABLE:
            self.orchestrator = DAGOrchestrator(OrchestrationConfig(
                max_workers=4,
                execution_strategy=ExecutionStrategy.CONSERVATIVE,
                scheduling_strategy=SchedulingStrategy.ADAPTIVE,
                enable_prefire_testing=True,
                enable_continuous_monitoring=True
            ))
        else:
            self.orchestrator = None
        
        self.custom_tasks = []
        self.execution_history = []
        self.task_templates = self._create_task_templates()
    
    def _create_task_templates(self) -> Dict[str, Dict[str, Any]]:
        """Create predefined task templates for easy DAG creation."""
        return {
            "data_processing": {
                "name": "Data Processing Task",
                "function": lambda: self._simulate_data_processing(),
                "duration_range": (1.0, 3.0),
                "resource_weight": 2.0,
                "description": "Processes data with moderate resource usage"
            },
            "ml_training": {
                "name": "ML Training Task",
                "function": lambda: self._simulate_ml_training(),
                "duration_range": (3.0, 6.0),
                "resource_weight": 4.0,
                "description": "CPU-intensive machine learning training"
            },
            "data_validation": {
                "name": "Data Validation Task",
                "function": lambda: self._simulate_data_validation(),
                "duration_range": (0.5, 1.5),
                "resource_weight": 1.0,
                "description": "Quick data validation and quality checks"
            },
            "api_call": {
                "name": "API Call Task",
                "function": lambda: self._simulate_api_call(),
                "duration_range": (0.5, 2.0),
                "resource_weight": 0.5,
                "description": "External API call with network I/O"
            },
            "file_processing": {
                "name": "File Processing Task",
                "function": lambda: self._simulate_file_processing(),
                "duration_range": (1.0, 2.5),
                "resource_weight": 1.5,
                "description": "File I/O and processing operations"
            },
            "reporting": {
                "name": "Reporting Task",
                "function": lambda: self._simulate_reporting(),
                "duration_range": (0.5, 1.0),
                "resource_weight": 0.8,
                "description": "Generate reports and summaries"
            }
        }
    
    def _simulate_data_processing(self):
        """Simulate data processing task."""
        duration = random.uniform(1.0, 3.0)
        time.sleep(duration)
        return {
            "status": "success",
            "records_processed": random.randint(1000, 10000),
            "processing_time": duration,
            "data_quality": random.uniform(0.85, 0.98)
        }
    
    def _simulate_ml_training(self):
        """Simulate ML training task."""
        duration = random.uniform(3.0, 6.0)
        time.sleep(duration)
        return {
            "status": "success",
            "model_accuracy": random.uniform(0.80, 0.95),
            "training_time": duration,
            "epochs": random.randint(50, 200),
            "loss": random.uniform(0.05, 0.25)
        }
    
    def _simulate_data_validation(self):
        """Simulate data validation task."""
        duration = random.uniform(0.5, 1.5)
        time.sleep(duration)
        return {
            "status": "success",
            "validation_errors": random.randint(0, 5),
            "validation_time": duration,
            "data_completeness": random.uniform(0.90, 1.0)
        }
    
    def _simulate_api_call(self):
        """Simulate API call task."""
        duration = random.uniform(0.5, 2.0)
        time.sleep(duration)
        # Simulate occasional API failures
        if random.random() < 0.1:  # 10% failure rate
            raise Exception("API call failed: Service temporarily unavailable")
        return {
            "status": "success",
            "response_time": duration,
            "data_retrieved": random.randint(100, 1000),
            "api_version": "v1.2"
        }
    
    def _simulate_file_processing(self):
        """Simulate file processing task."""
        duration = random.uniform(1.0, 2.5)
        time.sleep(duration)
        return {
            "status": "success",
            "files_processed": random.randint(10, 100),
            "total_size_mb": random.uniform(50, 500),
            "processing_time": duration
        }
    
    def _simulate_reporting(self):
        """Simulate reporting task."""
        duration = random.uniform(0.5, 1.0)
        time.sleep(duration)
        return {
            "status": "success",
            "report_generated": True,
            "report_size_kb": random.randint(100, 1000),
            "generation_time": duration
        }
    
    def display_banner(self):
        """Display the demo banner."""
        print("\n" + "=" * 70)
        print("🔄 DAG Orchestration - Interactive Demo")
        print("🐺 Beast Mode Framework")
        print("Explore parallel execution and dependency management!")
        print("=" * 70)
        
        if not IMPORTS_AVAILABLE:
            print("\n⚠️  Note: DAG orchestration modules not available.")
            print("This demo will run in simulation mode.")
        
        print("\nWelcome to the DAG orchestration interactive demo!")
        print("Create custom DAGs, experiment with strategies, and see real-time results.")
    
    def display_menu(self):
        """Display the main menu."""
        print("\n📋 Available Commands:")
        print("  1. 🏗️  Create Custom DAG")
        print("  2. 📦 Use Predefined DAG Template")
        print("  3. 🚀 Execute Current DAG")
        print("  4. ⚙️  Configure Orchestrator")
        print("  5. 📊 View Execution History")
        print("  6. 🏥 Check System Health")
        print("  7. 📈 View Performance Statistics")
        print("  8. 🛡️  Test Error Handling")
        print("  9. 📖 Show Help")
        print("  0. 🚪 Exit")
        print("\n" + "-" * 50)
    
    def create_custom_dag(self):
        """Interactive custom DAG creation."""
        print("\n🏗️  Create Custom DAG")
        print("-" * 30)
        
        self.custom_tasks.clear()
        
        print("Available task types:")
        for i, (task_type, template) in enumerate(self.task_templates.items(), 1):
            print(f"  {i}. {task_type}: {template['description']}")
        
        print("\nCreate your DAG by adding tasks and their dependencies.")
        print("Enter task details (or 'done' to finish):")
        
        while True:
            print(f"\n📋 Current DAG has {len(self.custom_tasks)} tasks")
            
            # Get task ID
            task_id = input("Task ID (or 'done' to finish): ").strip()
            if task_id.lower() == 'done':
                break
            
            if not task_id:
                print("❌ Task ID cannot be empty")
                continue
            
            # Check for duplicate task ID
            if any(task.task_id == task_id for task in self.custom_tasks):
                print(f"❌ Task ID '{task_id}' already exists")
                continue
            
            # Get task type
            print("Select task type:")
            task_types = list(self.task_templates.keys())
            for i, task_type in enumerate(task_types, 1):
                print(f"  {i}. {task_type}")
            
            try:
                type_choice = int(input("Task type (number): ").strip())
                if 1 <= type_choice <= len(task_types):
                    selected_type = task_types[type_choice - 1]
                    template = self.task_templates[selected_type]
                else:
                    print("❌ Invalid task type")
                    continue
            except ValueError:
                print("❌ Please enter a valid number")
                continue
            
            # Get dependencies
            if self.custom_tasks:
                print(f"Available tasks for dependencies: {[t.task_id for t in self.custom_tasks]}")
                deps_input = input("Dependencies (comma-separated, or press Enter for none): ").strip()
                if deps_input:
                    dependencies = set(dep.strip() for dep in deps_input.split(','))
                    # Validate dependencies exist
                    existing_task_ids = {t.task_id for t in self.custom_tasks}
                    invalid_deps = dependencies - existing_task_ids
                    if invalid_deps:
                        print(f"❌ Invalid dependencies: {invalid_deps}")
                        continue
                else:
                    dependencies = set()
            else:
                dependencies = set()
            
            # Get priority
            try:
                priority = int(input("Priority (1-10, default 5): ").strip() or "5")
                priority = max(1, min(10, priority))
            except ValueError:
                priority = 5
            
            # Create task definition
            task = create_task_definition(
                task_id=task_id,
                name=f"{template['name']} ({task_id})",
                execution_function=template['function'],
                dependencies=dependencies,
                priority=priority,
                resource_requirements={"weight": template['resource_weight']}
            )
            
            self.custom_tasks.append(task)
            print(f"✅ Added task '{task_id}' with {len(dependencies)} dependencies")
        
        if self.custom_tasks:
            print(f"\n🎉 Custom DAG created with {len(self.custom_tasks)} tasks!")
            self._display_dag_summary(self.custom_tasks)
        else:
            print("❌ No tasks added to DAG")
    
    def use_predefined_template(self):
        """Use a predefined DAG template."""
        print("\n📦 Predefined DAG Templates")
        print("-" * 30)
        
        templates = {
            "1": ("Data Pipeline", self._create_data_pipeline_template),
            "2": ("ML Workflow", self._create_ml_workflow_template),
            "3": ("Web Scraping", self._create_web_scraping_template),
            "4": ("ETL Process", self._create_etl_process_template)
        }
        
        print("Available templates:")
        for key, (name, _) in templates.items():
            print(f"  {key}. {name}")
        
        choice = input("\nSelect template (1-4): ").strip()
        
        if choice in templates:
            template_name, template_func = templates[choice]
            self.custom_tasks = template_func()
            print(f"✅ Loaded {template_name} template with {len(self.custom_tasks)} tasks!")
            self._display_dag_summary(self.custom_tasks)
        else:
            print("❌ Invalid template selection")
    
    def _create_data_pipeline_template(self) -> List[TaskDefinition]:
        """Create a data pipeline template."""
        return [
            create_task_definition("data_ingestion", "Data Ingestion", 
                                 self.task_templates["data_processing"]["function"], 
                                 set(), 10, {"weight": 2.0}),
            create_task_definition("data_validation", "Data Validation", 
                                 self.task_templates["data_validation"]["function"], 
                                 {"data_ingestion"}, 8, {"weight": 1.0}),
            create_task_definition("data_transformation", "Data Transformation", 
                                 self.task_templates["data_processing"]["function"], 
                                 {"data_validation"}, 9, {"weight": 3.0}),
            create_task_definition("data_export", "Data Export", 
                                 self.task_templates["file_processing"]["function"], 
                                 {"data_transformation"}, 7, {"weight": 1.5}),
            create_task_definition("generate_report", "Generate Report", 
                                 self.task_templates["reporting"]["function"], 
                                 {"data_export"}, 5, {"weight": 0.8})
        ]
    
    def _create_ml_workflow_template(self) -> List[TaskDefinition]:
        """Create an ML workflow template."""
        return [
            create_task_definition("data_preparation", "Data Preparation", 
                                 self.task_templates["data_processing"]["function"], 
                                 set(), 10, {"weight": 2.0}),
            create_task_definition("feature_engineering", "Feature Engineering", 
                                 self.task_templates["data_processing"]["function"], 
                                 {"data_preparation"}, 9, {"weight": 2.5}),
            create_task_definition("model_training", "Model Training", 
                                 self.task_templates["ml_training"]["function"], 
                                 {"feature_engineering"}, 10, {"weight": 4.0}),
            create_task_definition("model_validation", "Model Validation", 
                                 self.task_templates["data_validation"]["function"], 
                                 {"model_training"}, 8, {"weight": 1.5}),
            create_task_definition("model_deployment", "Model Deployment", 
                                 self.task_templates["api_call"]["function"], 
                                 {"model_validation"}, 9, {"weight": 1.0})
        ]
    
    def _create_web_scraping_template(self) -> List[TaskDefinition]:
        """Create a web scraping template."""
        return [
            create_task_definition("url_discovery", "URL Discovery", 
                                 self.task_templates["api_call"]["function"], 
                                 set(), 10, {"weight": 0.5}),
            create_task_definition("content_scraping", "Content Scraping", 
                                 self.task_templates["api_call"]["function"], 
                                 {"url_discovery"}, 9, {"weight": 2.0}),
            create_task_definition("content_processing", "Content Processing", 
                                 self.task_templates["data_processing"]["function"], 
                                 {"content_scraping"}, 8, {"weight": 2.5}),
            create_task_definition("data_storage", "Data Storage", 
                                 self.task_templates["file_processing"]["function"], 
                                 {"content_processing"}, 7, {"weight": 1.5})
        ]
    
    def _create_etl_process_template(self) -> List[TaskDefinition]:
        """Create an ETL process template."""
        return [
            create_task_definition("extract_source_1", "Extract Source 1", 
                                 self.task_templates["api_call"]["function"], 
                                 set(), 10, {"weight": 1.0}),
            create_task_definition("extract_source_2", "Extract Source 2", 
                                 self.task_templates["file_processing"]["function"], 
                                 set(), 10, {"weight": 1.5}),
            create_task_definition("transform_data", "Transform Data", 
                                 self.task_templates["data_processing"]["function"], 
                                 {"extract_source_1", "extract_source_2"}, 9, {"weight": 3.0}),
            create_task_definition("validate_transform", "Validate Transform", 
                                 self.task_templates["data_validation"]["function"], 
                                 {"transform_data"}, 8, {"weight": 1.0}),
            create_task_definition("load_warehouse", "Load Data Warehouse", 
                                 self.task_templates["file_processing"]["function"], 
                                 {"validate_transform"}, 9, {"weight": 2.0})
        ]
    
    def _display_dag_summary(self, tasks: List[TaskDefinition]):
        """Display a summary of the DAG structure."""
        print(f"\n📊 DAG Summary:")
        print(f"   📋 Total Tasks: {len(tasks)}")
        
        # Calculate dependency statistics
        total_deps = sum(len(task.dependencies) for task in tasks)
        print(f"   🔗 Total Dependencies: {total_deps}")
        
        # Show tasks by layer
        remaining_tasks = {task.task_id: task for task in tasks}
        layer = 0
        
        while remaining_tasks:
            layer += 1
            current_layer = []
            
            for task_id, task in list(remaining_tasks.items()):
                if not task.dependencies or all(dep not in remaining_tasks for dep in task.dependencies):
                    current_layer.append(task)
                    del remaining_tasks[task_id]
            
            if current_layer:
                print(f"   📊 Layer {layer}: {[task.task_id for task in current_layer]}")
            else:
                # Circular dependency detected
                print(f"   ⚠️  Circular dependency detected in remaining tasks: {list(remaining_tasks.keys())}")
                break
    
    async def execute_current_dag(self):
        """Execute the current DAG."""
        print("\n🚀 Execute Current DAG")
        print("-" * 30)
        
        if not self.custom_tasks:
            print("❌ No DAG created. Please create a DAG first.")
            return
        
        if not IMPORTS_AVAILABLE:
            print("📝 Simulating DAG execution...")
            print("✅ DAG executed successfully (simulated)")
            return
        
        print(f"🔄 Executing DAG with {len(self.custom_tasks)} tasks...")
        self._display_dag_summary(self.custom_tasks)
        
        # Show current configuration
        config = self.orchestrator._config
        print(f"\n⚙️  Configuration:")
        print(f"   👥 Max Workers: {config.max_workers}")
        print(f"   🎯 Execution Strategy: {config.execution_strategy.value}")
        print(f"   📅 Scheduling Strategy: {config.scheduling_strategy.value}")
        
        # Execute DAG
        start_time = datetime.now()
        print(f"\n🚀 Starting execution at {start_time.strftime('%H:%M:%S')}...")
        
        try:
            result = await self.orchestrator.execute_dag(self.custom_tasks.copy())
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Display results
            print(f"\n📊 Execution Results:")
            print(f"   🆔 Orchestration ID: {result.orchestration_id}")
            print(f"   📊 Status: {result.status.value}")
            print(f"   ⏱️  Duration: {duration:.2f}s")
            print(f"   ✅ Completed: {result.completed_tasks}/{result.total_tasks}")
            print(f"   ❌ Failed: {result.failed_tasks}")
            print(f"   ⏭️  Skipped: {result.skipped_tasks}")
            
            # Show task results
            if result.task_results:
                print(f"\n📋 Task Results:")
                for task_id, task_result in result.task_results.items():
                    status_emoji = {
                        TaskExecutionStatus.COMPLETED: "✅",
                        TaskExecutionStatus.FAILED: "❌",
                        TaskExecutionStatus.SKIPPED: "⏭️"
                    }.get(task_result.status, "❓")
                    
                    print(f"   {status_emoji} {task_id}: {task_result.status.value} ({task_result.duration_seconds:.2f}s)")
                    
                    if task_result.result and isinstance(task_result.result, dict):
                        for key, value in task_result.result.items():
                            if key != "status":
                                print(f"      📊 {key}: {value}")
            
            # Store in history
            self.execution_history.append({
                'timestamp': start_time,
                'duration': duration,
                'result': result,
                'task_count': len(self.custom_tasks)
            })
            
            print(f"\n🎉 Execution completed! Results stored in history.")
            
        except Exception as e:
            print(f"❌ Execution failed: {e}")
    
    def configure_orchestrator(self):
        """Configure orchestrator settings."""
        print("\n⚙️  Configure Orchestrator")
        print("-" * 30)
        
        if not IMPORTS_AVAILABLE:
            print("📝 Configuration not available in simulation mode")
            return
        
        current_config = self.orchestrator._config
        
        print("Current configuration:")
        print(f"   👥 Max Workers: {current_config.max_workers}")
        print(f"   🎯 Execution Strategy: {current_config.execution_strategy.value}")
        print(f"   📅 Scheduling Strategy: {current_config.scheduling_strategy.value}")
        print(f"   🧪 Prefire Testing: {current_config.enable_prefire_testing}")
        print(f"   📊 Continuous Monitoring: {current_config.enable_continuous_monitoring}")
        
        print("\nWhat would you like to configure?")
        print("  1. Max Workers")
        print("  2. Execution Strategy")
        print("  3. Scheduling Strategy")
        print("  4. Toggle Prefire Testing")
        print("  5. Toggle Continuous Monitoring")
        
        choice = input("Select option (1-5): ").strip()
        
        if choice == "1":
            try:
                workers = int(input(f"Max workers (current: {current_config.max_workers}): "))
                workers = max(1, min(16, workers))
                current_config.max_workers = workers
                print(f"✅ Max workers set to {workers}")
            except ValueError:
                print("❌ Invalid number")
        
        elif choice == "2":
            strategies = list(ExecutionStrategy)
            print("Execution strategies:")
            for i, strategy in enumerate(strategies, 1):
                print(f"  {i}. {strategy.value}")
            
            try:
                strategy_choice = int(input("Select strategy: "))
                if 1 <= strategy_choice <= len(strategies):
                    current_config.execution_strategy = strategies[strategy_choice - 1]
                    print(f"✅ Execution strategy set to {current_config.execution_strategy.value}")
                else:
                    print("❌ Invalid choice")
            except ValueError:
                print("❌ Invalid number")
        
        elif choice == "3":
            strategies = list(SchedulingStrategy)
            print("Scheduling strategies:")
            for i, strategy in enumerate(strategies, 1):
                print(f"  {i}. {strategy.value}")
            
            try:
                strategy_choice = int(input("Select strategy: "))
                if 1 <= strategy_choice <= len(strategies):
                    current_config.scheduling_strategy = strategies[strategy_choice - 1]
                    print(f"✅ Scheduling strategy set to {current_config.scheduling_strategy.value}")
                else:
                    print("❌ Invalid choice")
            except ValueError:
                print("❌ Invalid number")
        
        elif choice == "4":
            current_config.enable_prefire_testing = not current_config.enable_prefire_testing
            print(f"✅ Prefire testing {'enabled' if current_config.enable_prefire_testing else 'disabled'}")
        
        elif choice == "5":
            current_config.enable_continuous_monitoring = not current_config.enable_continuous_monitoring
            print(f"✅ Continuous monitoring {'enabled' if current_config.enable_continuous_monitoring else 'disabled'}")
        
        else:
            print("❌ Invalid choice")
    
    def view_execution_history(self):
        """View execution history."""
        print("\n📊 Execution History")
        print("-" * 30)
        
        if not self.execution_history:
            print("📝 No executions in history")
            return
        
        print(f"📋 Total executions: {len(self.execution_history)}")
        
        for i, execution in enumerate(self.execution_history[-10:], 1):  # Show last 10
            result = execution['result']
            print(f"\n🔢 Execution {i}:")
            print(f"   ⏰ Time: {execution['timestamp'].strftime('%H:%M:%S')}")
            print(f"   ⏱️  Duration: {execution['duration']:.2f}s")
            print(f"   📊 Status: {result.status.value}")
            print(f"   📋 Tasks: {execution['task_count']}")
            print(f"   ✅ Success Rate: {result.completed_tasks/result.total_tasks:.1%}")
        
        # Calculate statistics
        if len(self.execution_history) > 1:
            avg_duration = sum(e['duration'] for e in self.execution_history) / len(self.execution_history)
            success_rate = sum(1 for e in self.execution_history 
                             if e['result'].failed_tasks == 0) / len(self.execution_history)
            
            print(f"\n📈 Statistics:")
            print(f"   ⏱️  Average Duration: {avg_duration:.2f}s")
            print(f"   ✅ Overall Success Rate: {success_rate:.1%}")
    
    def check_system_health(self):
        """Check system health status."""
        print("\n🏥 System Health Check")
        print("-" * 30)
        
        if not IMPORTS_AVAILABLE:
            print("📝 System health check (simulated):")
            print("   ✅ All systems operational")
            return
        
        # Check orchestrator health
        health = self.orchestrator.get_health_status()
        print(f"🔧 Orchestrator Health:")
        print(f"   📊 Status: {health.status.value}")
        print(f"   💯 Health Score: {health.health_score:.2f}")
        print(f"   ⏱️  Uptime: {health.uptime_seconds:.1f}s")
        
        if health.issues:
            print(f"   ⚠️  Issues:")
            for issue in health.issues:
                print(f"      • {issue}")
        
        # Get module info
        info = self.orchestrator.get_module_info()
        print(f"\n📋 Module Information:")
        print(f"   🆔 Module ID: {info['module_id']}")
        print(f"   📝 Name: {info['name']}")
        print(f"   🔢 Version: {info['version']}")
        print(f"   🎯 Capabilities: {', '.join(info['capabilities'])}")
        
        # Component status
        component_status = info.get('component_status', {})
        if component_status:
            print(f"\n🔧 Component Status:")
            for component, status in component_status.items():
                status_emoji = "✅" if status in ["healthy", True] else "⚠️"
                print(f"   {status_emoji} {component}: {status}")
    
    def view_performance_statistics(self):
        """View performance statistics."""
        print("\n📈 Performance Statistics")
        print("-" * 30)
        
        if not IMPORTS_AVAILABLE:
            print("📝 Performance statistics (simulated):")
            print("   📊 Average execution time: 5.2s")
            print("   ✅ Success rate: 95%")
            return
        
        # Get execution statistics
        stats = self.orchestrator.get_execution_statistics()
        
        print("🔧 Orchestration Statistics:")
        orch_stats = stats.get('orchestration_statistics', {})
        print(f"   🔢 Total Orchestrations: {orch_stats.get('total_orchestrations', 0)}")
        print(f"   ✅ Successful: {orch_stats.get('successful_orchestrations', 0)}")
        print(f"   ❌ Failed: {orch_stats.get('failed_orchestrations', 0)}")
        print(f"   📈 Success Rate: {orch_stats.get('success_rate', 0):.1%}")
        
        # Execution engine statistics
        exec_stats = stats.get('execution_statistics', {})
        if exec_stats:
            print(f"\n⚡ Execution Engine:")
            print(f"   🔢 Total Executions: {exec_stats.get('total_executions', 0)}")
            print(f"   📊 Tasks Executed: {exec_stats.get('total_tasks_executed', 0)}")
            print(f"   📈 Average Tasks/Execution: {exec_stats.get('average_tasks_per_execution', 0):.1f}")
        
        # Scheduling statistics
        sched_stats = stats.get('scheduling_statistics', {})
        if sched_stats:
            print(f"\n📅 Scheduling:")
            print(f"   🎯 Strategy: {sched_stats.get('strategy', 'unknown')}")
            print(f"   🔢 Decisions Made: {sched_stats.get('total_scheduling_decisions', 0)}")
            print(f"   ⚡ Avg Decision Time: {sched_stats.get('average_scheduling_time_ms', 0):.1f}ms")
    
    def test_error_handling(self):
        """Test error handling capabilities."""
        print("\n🛡️  Test Error Handling")
        print("-" * 30)
        
        print("This will create a DAG with tasks that may fail to test error handling.")
        confirm = input("Continue? (y/n): ").strip().lower()
        
        if confirm != 'y':
            return
        
        # Create error-prone DAG
        def failing_task():
            if random.random() < 0.4:  # 40% failure rate
                raise Exception("Simulated task failure for testing")
            time.sleep(random.uniform(0.5, 1.0))
            return {"status": "success", "data": "processed"}
        
        error_tasks = [
            create_task_definition("stable_task", "Stable Task", 
                                 lambda: {"status": "success", "reliable": True}, 
                                 set(), 10, {"weight": 1.0}),
            create_task_definition("risky_task_1", "Risky Task 1", 
                                 failing_task, {"stable_task"}, 8, {"weight": 1.0}),
            create_task_definition("risky_task_2", "Risky Task 2", 
                                 failing_task, {"stable_task"}, 8, {"weight": 1.0}),
            create_task_definition("dependent_task", "Dependent Task", 
                                 lambda: {"status": "success", "depends_on_risky": True}, 
                                 {"risky_task_1", "risky_task_2"}, 6, {"weight": 1.0})
        ]
        
        self.custom_tasks = error_tasks
        print(f"✅ Created error-prone DAG with {len(error_tasks)} tasks")
        print("📋 Tasks: stable → risky_1, risky_2 → dependent")
        print("⚠️  Risky tasks have 40% failure rate")
        
        input("\nPress Enter to execute the error-prone DAG...")
        
        # Execute using the existing method
        if IMPORTS_AVAILABLE:
            asyncio.run(self.execute_current_dag())
        else:
            print("📝 Error handling test completed (simulated)")
    
    def show_help(self):
        """Display help information."""
        print("\n📖 DAG Orchestration Help")
        print("-" * 30)
        
        print("🔄 What is DAG Orchestration?")
        print("   DAG (Directed Acyclic Graph) orchestration manages the execution")
        print("   of tasks with dependencies, ensuring proper order and parallelization.")
        
        print("\n🎯 Key Features:")
        print("   • Dependency-aware task execution")
        print("   • Parallel processing with multiple strategies")
        print("   • Intelligent scheduling algorithms")
        print("   • Comprehensive error handling")
        print("   • Real-time monitoring and health checks")
        
        print("\n🚀 Getting Started:")
        print("   1. Create a DAG using templates or custom tasks (options 1-2)")
        print("   2. Configure execution settings (option 4)")
        print("   3. Execute your DAG (option 3)")
        print("   4. Monitor results and performance (options 5-7)")
        
        print("\n💡 Tips:")
        print("   • Start with predefined templates to learn the concepts")
        print("   • Experiment with different execution strategies")
        print("   • Use priorities to influence task scheduling")
        print("   • Monitor health and performance regularly")
        print("   • Test error handling with the built-in error simulation")
        
        print("\n🔗 Task Dependencies:")
        print("   • Tasks can depend on other tasks completing first")
        print("   • Dependencies form a directed acyclic graph (no cycles)")
        print("   • Failed tasks cause dependent tasks to be skipped")
        print("   • Parallel execution respects dependency constraints")
    
    async def run_interactive_demo(self):
        """Run the interactive demo."""
        self.display_banner()
        
        while True:
            self.display_menu()
            
            try:
                choice = input("Enter your choice (0-9): ").strip()
                
                if choice == "0":
                    print("\n👋 Thanks for exploring DAG orchestration!")
                    print("🔄 Remember: Dependencies matter, parallelism rocks!")
                    break
                elif choice == "1":
                    self.create_custom_dag()
                elif choice == "2":
                    self.use_predefined_template()
                elif choice == "3":
                    await self.execute_current_dag()
                elif choice == "4":
                    self.configure_orchestrator()
                elif choice == "5":
                    self.view_execution_history()
                elif choice == "6":
                    self.check_system_health()
                elif choice == "7":
                    self.view_performance_statistics()
                elif choice == "8":
                    self.test_error_handling()
                elif choice == "9":
                    self.show_help()
                else:
                    print("❌ Invalid choice. Please enter a number from 0-9.")
                
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Demo interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                input("Press Enter to continue...")


def main():
    """Main entry point."""
    demo = InteractiveDAGDemo()
    asyncio.run(demo.run_interactive_demo())


if __name__ == "__main__":
    main()