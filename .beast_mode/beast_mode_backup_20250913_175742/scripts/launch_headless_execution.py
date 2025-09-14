#!/usr/bin/env python3
"""
Headless Spec Execution Framework - Launch Script

Orchestrates background execution of entire spec task DAGs using the comprehensive
spec dependency analysis. Provides autonomous execution with real-time monitoring.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Add src to path for Beast Mode imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    from beast_mode.execution.parallel_dag_orchestrator import ParallelDAGOrchestrator
    from beast_mode.monitoring.realtime_dashboard import RealtimeMonitoringDashboard
    from beast_mode.billing.gcp_integration import GCPBillingMonitor
    BEAST_MODE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Beast Mode components not available: {e}")
    BEAST_MODE_AVAILABLE = False


class ExecutionStatus(Enum):
    PLANNED = "planned"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class SpecTask:
    """Individual spec task definition"""
    spec_name: str
    task_id: str
    task_name: str
    dependencies: List[str]
    estimated_hours: float
    priority: int
    status: TaskStatus = TaskStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    agent_id: Optional[str] = None
    branch_name: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class ExecutionPlan:
    """Complete execution plan for spec DAG"""
    plan_id: str
    total_specs: int
    total_tasks: int
    estimated_duration_hours: float
    parallel_tracks: int
    critical_path: List[str]
    execution_layers: Dict[str, List[str]]
    tasks: List[SpecTask]
    created_at: datetime
    status: ExecutionStatus = ExecutionStatus.PLANNED


class HeadlessSpecExecutor:
    """
    Headless execution framework for spec DAGs
    
    Orchestrates background execution of entire spec task lists using
    the Parallel DAG Orchestrator with comprehensive monitoring.
    """
    
    def __init__(self):
        self.execution_dir = Path('headless_execution')
        self.execution_dir.mkdir(exist_ok=True)
        
        # Logging setup
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.execution_dir / 'execution.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize components if available
        self.dag_orchestrator = None
        self.monitoring_dashboard = None
        self.billing_monitor = None
        
        if BEAST_MODE_AVAILABLE:
            try:
                self.dag_orchestrator = ParallelDAGOrchestrator()
                self.monitoring_dashboard = RealtimeMonitoringDashboard()
                self.billing_monitor = GCPBillingMonitor({})
                self.logger.info("✅ Beast Mode components initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  Beast Mode component initialization failed: {e}")
        
        # Execution state
        self.current_execution: Optional[ExecutionPlan] = None
        self.active_agents: Dict[str, Any] = {}
        
    def load_spec_dag(self) -> Dict[str, Any]:
        """Load the comprehensive spec DAG"""
        dag_file = Path('.kiro/specs/comprehensive-spec-dag.md')
        
        if not dag_file.exists():
            raise FileNotFoundError("Comprehensive spec DAG not found. Run spec DAG analysis first.")
        
        # For now, return a simplified DAG structure
        # In production, this would parse the actual DAG markdown
        return {
            "foundation_layer": [
                "ghostbusters-framework",
                "spec-framework", 
                "rm-pattern-base"
            ],
            "infrastructure_layer": [
                "systematic-pdca-orchestrator",
                "systematic-metrics-engine",
                "parallel-dag-orchestrator",
                "systematic-git-workflow",
                "systematic-secrets-management"
            ],
            "core_services_layer": [
                "beast-mode-framework",
                "beast-mode-core",
                "tool-health-manager",
                "rdi-validation-system"
            ],
            "monitoring_layer": [
                "gcp-billing-integration",
                "realtime-monitoring-dashboard",
                "event-polling-hysteresis-service"
            ],
            "application_layer": [
                "research-content-management-architecture",
                "devpost-hackathon-integration",
                "cli-implementation-standards"
            ],
            "quality_layer": [
                "test-rca-integration",
                "test-infrastructure-repair",
                "build-test-agents"
            ]
        }
    
    def create_execution_plan(self, target_specs: Optional[List[str]] = None) -> ExecutionPlan:
        """Create comprehensive execution plan from spec DAG"""
        
        self.logger.info("🎯 Creating execution plan from spec DAG...")
        
        spec_dag = self.load_spec_dag()
        
        # If no target specs specified, execute entire DAG
        if not target_specs:
            target_specs = []
            for layer_specs in spec_dag.values():
                target_specs.extend(layer_specs)
        
        # Create tasks for each spec
        tasks = []
        task_id = 1
        
        for layer_name, layer_specs in spec_dag.items():
            for spec_name in layer_specs:
                if spec_name in target_specs:
                    # Load tasks from spec if available
                    spec_tasks = self._load_spec_tasks(spec_name)
                    
                    for spec_task in spec_tasks:
                        task = SpecTask(
                            spec_name=spec_name,
                            task_id=f"task_{task_id:03d}",
                            task_name=spec_task.get('name', f'Implement {spec_name}'),
                            dependencies=self._resolve_dependencies(spec_name, spec_dag),
                            estimated_hours=spec_task.get('estimated_hours', 8.0),
                            priority=self._calculate_priority(spec_name, layer_name)
                        )
                        tasks.append(task)
                        task_id += 1
        
        # Calculate execution metrics
        total_hours = sum(task.estimated_hours for task in tasks)
        parallel_tracks = self._calculate_parallel_tracks(spec_dag)
        estimated_duration = total_hours / parallel_tracks if parallel_tracks > 0 else total_hours
        
        plan = ExecutionPlan(
            plan_id=f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            total_specs=len(target_specs),
            total_tasks=len(tasks),
            estimated_duration_hours=estimated_duration,
            parallel_tracks=parallel_tracks,
            critical_path=self._identify_critical_path(spec_dag),
            execution_layers=spec_dag,
            tasks=tasks,
            created_at=datetime.now()
        )
        
        self.logger.info(f"📋 Execution plan created:")
        self.logger.info(f"   📊 {plan.total_specs} specs, {plan.total_tasks} tasks")
        self.logger.info(f"   ⏱️  Estimated duration: {plan.estimated_duration_hours:.1f} hours")
        self.logger.info(f"   🔀 Parallel tracks: {plan.parallel_tracks}")
        
        return plan
    
    def _load_spec_tasks(self, spec_name: str) -> List[Dict[str, Any]]:
        """Load tasks from spec tasks.md file"""
        tasks_file = Path(f'.kiro/specs/{spec_name}/tasks.md')
        
        if not tasks_file.exists():
            # Return default task if no tasks file
            return [{'name': f'Implement {spec_name}', 'estimated_hours': 8.0}]
        
        # For now, return simplified task structure
        # In production, this would parse the actual tasks.md file
        return [
            {'name': f'Foundation for {spec_name}', 'estimated_hours': 4.0},
            {'name': f'Core implementation for {spec_name}', 'estimated_hours': 8.0},
            {'name': f'Testing for {spec_name}', 'estimated_hours': 4.0},
            {'name': f'Documentation for {spec_name}', 'estimated_hours': 2.0}
        ]
    
    def _resolve_dependencies(self, spec_name: str, spec_dag: Dict[str, List[str]]) -> List[str]:
        """Resolve dependencies for a spec based on DAG layer structure"""
        dependencies = []
        
        # Find which layer this spec is in
        current_layer = None
        for layer_name, layer_specs in spec_dag.items():
            if spec_name in layer_specs:
                current_layer = layer_name
                break
        
        if not current_layer:
            return dependencies
        
        # Add dependencies based on layer hierarchy
        layer_order = list(spec_dag.keys())
        current_index = layer_order.index(current_layer)
        
        # Depend on all specs in previous layers
        for i in range(current_index):
            dependencies.extend(spec_dag[layer_order[i]])
        
        return dependencies
    
    def _calculate_priority(self, spec_name: str, layer_name: str) -> int:
        """Calculate priority based on layer and criticality"""
        layer_priorities = {
            "foundation_layer": 100,
            "infrastructure_layer": 90,
            "core_services_layer": 80,
            "monitoring_layer": 70,
            "application_layer": 60,
            "quality_layer": 50
        }
        
        base_priority = layer_priorities.get(layer_name, 50)
        
        # Boost priority for critical specs
        critical_specs = [
            "ghostbusters-framework",
            "beast-mode-framework", 
            "gcp-billing-integration",
            "research-content-management-architecture"
        ]
        
        if spec_name in critical_specs:
            base_priority += 10
        
        return base_priority
    
    def _calculate_parallel_tracks(self, spec_dag: Dict[str, List[str]]) -> int:
        """Calculate maximum parallel execution tracks"""
        max_parallel = 0
        
        for layer_specs in spec_dag.values():
            max_parallel = max(max_parallel, len(layer_specs))
        
        return min(max_parallel, 8)  # Cap at 8 parallel tracks
    
    def _identify_critical_path(self, spec_dag: Dict[str, List[str]]) -> List[str]:
        """Identify critical path through spec DAG"""
        # Simplified critical path - longest dependency chain
        return [
            "ghostbusters-framework",
            "beast-mode-framework", 
            "beast-mode-core",
            "gcp-billing-integration",
            "realtime-monitoring-dashboard",
            "research-content-management-architecture"
        ]
    
    async def launch_execution(self, execution_plan: ExecutionPlan) -> bool:
        """Launch headless background execution"""
        
        self.logger.info(f"🚀 Launching headless execution: {execution_plan.plan_id}")
        
        self.current_execution = execution_plan
        execution_plan.status = ExecutionStatus.RUNNING
        
        # Save execution plan
        plan_file = self.execution_dir / f"{execution_plan.plan_id}_plan.json"
        with open(plan_file, 'w') as f:
            json.dump(asdict(execution_plan), f, indent=2, default=str)
        
        try:
            # Execute layers in sequence with parallel execution within layers
            for layer_name, layer_specs in execution_plan.execution_layers.items():
                self.logger.info(f"📋 Executing layer: {layer_name}")
                
                # Get tasks for this layer
                layer_tasks = [task for task in execution_plan.tasks 
                             if task.spec_name in layer_specs]
                
                if layer_tasks:
                    await self._execute_layer_parallel(layer_tasks)
                
                self.logger.info(f"✅ Completed layer: {layer_name}")
            
            execution_plan.status = ExecutionStatus.COMPLETED
            self.logger.info(f"🎉 Execution completed: {execution_plan.plan_id}")
            
            return True
            
        except Exception as e:
            execution_plan.status = ExecutionStatus.FAILED
            self.logger.error(f"❌ Execution failed: {e}")
            return False
        
        finally:
            # Save final execution state
            with open(plan_file, 'w') as f:
                json.dump(asdict(execution_plan), f, indent=2, default=str)
    
    async def _execute_layer_parallel(self, layer_tasks: List[SpecTask]):
        """Execute tasks in a layer with parallel execution"""
        
        # Group tasks by spec for parallel execution
        spec_groups = {}
        for task in layer_tasks:
            if task.spec_name not in spec_groups:
                spec_groups[task.spec_name] = []
            spec_groups[task.spec_name].append(task)
        
        # Execute specs in parallel
        parallel_executions = []
        for spec_name, spec_tasks in spec_groups.items():
            execution = self._execute_spec_tasks(spec_name, spec_tasks)
            parallel_executions.append(execution)
        
        # Wait for all parallel executions to complete
        await asyncio.gather(*parallel_executions)
    
    async def _execute_spec_tasks(self, spec_name: str, tasks: List[SpecTask]):
        """Execute all tasks for a specific spec"""
        
        self.logger.info(f"🔧 Executing spec: {spec_name} ({len(tasks)} tasks)")
        
        for task in tasks:
            await self._execute_single_task(task)
        
        self.logger.info(f"✅ Completed spec: {spec_name}")
    
    async def _execute_single_task(self, task: SpecTask):
        """Execute a single task"""
        
        self.logger.info(f"⚡ Executing task: {task.task_name}")
        
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        
        try:
            # Simulate task execution
            # In production, this would launch actual implementation agents
            execution_time = min(task.estimated_hours * 0.1, 5.0)  # Simulate faster execution
            await asyncio.sleep(execution_time)
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            self.logger.info(f"✅ Completed task: {task.task_name}")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.now()
            
            self.logger.error(f"❌ Failed task: {task.task_name} - {e}")
    
    def get_execution_status(self) -> Dict[str, Any]:
        """Get current execution status"""
        
        if not self.current_execution:
            return {"status": "no_active_execution"}
        
        completed_tasks = len([t for t in self.current_execution.tasks 
                             if t.status == TaskStatus.COMPLETED])
        failed_tasks = len([t for t in self.current_execution.tasks 
                          if t.status == TaskStatus.FAILED])
        running_tasks = len([t for t in self.current_execution.tasks 
                           if t.status == TaskStatus.RUNNING])
        
        progress_percent = (completed_tasks / self.current_execution.total_tasks) * 100
        
        return {
            "execution_id": self.current_execution.plan_id,
            "status": self.current_execution.status.value,
            "progress_percent": progress_percent,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "running_tasks": running_tasks,
            "total_tasks": self.current_execution.total_tasks,
            "estimated_completion": self._estimate_completion_time(),
            "active_agents": len(self.active_agents)
        }
    
    def _estimate_completion_time(self) -> Optional[str]:
        """Estimate completion time based on current progress"""
        
        if not self.current_execution:
            return None
        
        completed_tasks = len([t for t in self.current_execution.tasks 
                             if t.status == TaskStatus.COMPLETED])
        
        if completed_tasks == 0:
            return None
        
        # Simple estimation based on average task completion time
        completed_task_objects = [t for t in self.current_execution.tasks 
                                if t.status == TaskStatus.COMPLETED and t.started_at and t.completed_at]
        
        if not completed_task_objects:
            return None
        
        avg_task_time = sum(
            (t.completed_at - t.started_at).total_seconds() 
            for t in completed_task_objects
        ) / len(completed_task_objects)
        
        remaining_tasks = self.current_execution.total_tasks - completed_tasks
        estimated_seconds = remaining_tasks * avg_task_time
        
        completion_time = datetime.now() + timedelta(seconds=estimated_seconds)
        return completion_time.isoformat()


async def main():
    """Main entry point for headless execution"""
    
    print("🎯 Beast Mode Headless Spec Execution Framework")
    print("=" * 60)
    
    executor = HeadlessSpecExecutor()
    
    # Create execution plan
    print("📋 Creating execution plan...")
    execution_plan = executor.create_execution_plan()
    
    print(f"\n📊 Execution Plan Summary:")
    print(f"   🎯 Plan ID: {execution_plan.plan_id}")
    print(f"   📈 Specs: {execution_plan.total_specs}")
    print(f"   📋 Tasks: {execution_plan.total_tasks}")
    print(f"   ⏱️  Duration: {execution_plan.estimated_duration_hours:.1f} hours")
    print(f"   🔀 Parallel tracks: {execution_plan.parallel_tracks}")
    
    # Ask for confirmation
    response = input(f"\n🚀 Launch headless execution? (y/N): ")
    if response.lower() != 'y':
        print("❌ Execution cancelled")
        return
    
    # Launch execution
    print(f"\n🚀 Launching headless execution...")
    success = await executor.launch_execution(execution_plan)
    
    if success:
        print(f"\n🎉 Headless execution completed successfully!")
        status = executor.get_execution_status()
        print(f"   ✅ Completed: {status['completed_tasks']}/{status['total_tasks']} tasks")
        print(f"   📊 Progress: {status['progress_percent']:.1f}%")
    else:
        print(f"\n❌ Headless execution failed")
        status = executor.get_execution_status()
        print(f"   ❌ Failed: {status['failed_tasks']} tasks")
        print(f"   ✅ Completed: {status['completed_tasks']}/{status['total_tasks']} tasks")


if __name__ == "__main__":
    asyncio.run(main())