#!/usr/bin/env python3
"""
Parallel Execution Preparation for System Architecture Wiring Diagram
====================================================================

Prepares DAG-orchestrated parallel execution of system-architecture-wiring-diagram 
tasks using Cursor Code CLI instead of Kiro CLI for maximum efficiency.

Author: Beast Mode Framework
Date: 2025-09-30
Version: 1.0
"""

import os
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


@dataclass
class CursorTask:
    """Definition of a task for Cursor CLI execution."""
    task_id: str
    name: str
    spec_file: str
    dependencies: List[str] = field(default_factory=list)
    priority: int = 0
    estimated_duration_minutes: int = 30
    cursor_command: str = ""
    log_file: str = ""


class CursorParallelExecutionPreparer(ReflectiveModule):
    """
    Prepares parallel execution of system architecture tasks using Cursor CLI
    with proper DAG orchestration and dependency management.
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "CursorParallelExecutionPreparer"
        self.execution_timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.log_dir = f"logs/cursor-parallel-execution/{self.execution_timestamp}"
        
        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Define system architecture wiring diagram tasks
        self.tasks = self._define_system_architecture_tasks()
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": self.module_id,
            "name": "CursorParallelExecutionPreparer",
            "version": "1.0.0",
            "description": "Prepares parallel execution using Cursor CLI",
            "execution_timestamp": self.execution_timestamp,
            "total_tasks": len(self.tasks),
            "log_directory": self.log_dir
        }
    
    def get_capabilities(self) -> List[Any]:
        """Get module capabilities - RDI Compliant"""
        return ["parallel_execution", "dag_orchestration", "cursor_cli_integration"]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get module health status - RDI Compliant"""
        return {
            "status": "healthy",
            "tasks_defined": len(self.tasks),
            "dag_valid": self.validate_dag_structure(),
            "log_directory_exists": os.path.exists(self.log_dir)
        }
    
    def graceful_degradation(self) -> Dict[str, Any]:
        """Perform graceful degradation - RDI Compliant"""
        return {
            "success": True,
            "fallback_mode": "sequential_execution",
            "remaining_capabilities": ["basic_execution"]
        }
        
    def _define_system_architecture_tasks(self) -> List[CursorTask]:
        """Define all system architecture wiring diagram tasks with proper dependencies."""
        
        tasks = [
            # Phase 1: Infrastructure Discovery Engine
            CursorTask(
                task_id="1.4",
                name="Cloudflare Tunnel Discovery",
                spec_file=".kiro/specs/system-architecture-wiring-diagram/tasks.md",
                dependencies=[],  # Can run independently
                priority=10,
                estimated_duration_minutes=45,
                cursor_command="cursor --task 'Implement Cloudflare tunnel discovery (Task 1.4)' --spec .kiro/specs/system-architecture-wiring-diagram/tasks.md",
                log_file=f"{self.log_dir}/task-1.4-cloudflare-tunnel-discovery.log"
            ),
            
            CursorTask(
                task_id="1.6",
                name="Network Topology Discovery", 
                spec_file=".kiro/specs/system-architecture-wiring-diagram/tasks.md",
                dependencies=[],  # Can run independently
                priority=9,
                estimated_duration_minutes=40,
                cursor_command="cursor --task 'Implement network topology discovery (Task 1.6)' --spec .kiro/specs/system-architecture-wiring-diagram/tasks.md",
                log_file=f"{self.log_dir}/task-1.6-network-topology-discovery.log"
            ),
            
            # Phase 2: Relationship Analysis Engine (depends on Phase 1)
            CursorTask(
                task_id="2.1",
                name="DAG-Compliant Dependency Analysis",
                spec_file=".kiro/specs/system-architecture-wiring-diagram/tasks.md", 
                dependencies=["1.4", "1.6"],  # Needs infrastructure discovery
                priority=8,
                estimated_duration_minutes=50,
                cursor_command="cursor --task 'Implement DAG-compliant dependency analysis (Task 2.1)' --spec .kiro/specs/system-architecture-wiring-diagram/tasks.md",
                log_file=f"{self.log_dir}/task-2.1-dag-dependency-analysis.log"
            ),
            
            CursorTask(
                task_id="2.2",
                name="Comprehensive Data Flow Mapping",
                spec_file=".kiro/specs/system-architecture-wiring-diagram/tasks.md",
                dependencies=["1.4", "1.6"],  # Needs infrastructure discovery
                priority=8,
                estimated_duration_minutes=55,
                cursor_command="cursor --task 'Implement comprehensive data flow mapping (Task 2.2)' --spec .kiro/specs/system-architecture-wiring-diagram/tasks.md",
                log_file=f"{self.log_dir}/task-2.2-data-flow-mapping.log"
            ),
            
            CursorTask(
                task_id="2.3", 
                name="Automation Chain Analysis",
                spec_file=".kiro/specs/system-architecture-wiring-diagram/tasks.md",
                dependencies=["1.4", "1.6"],  # Needs infrastructure and Makefile analysis
                priority=7,
                estimated_duration_minutes=45,
                cursor_command="cursor --task 'Implement automation chain analysis (Task 2.3)' --spec .kiro/specs/system-architecture-wiring-diagram/tasks.md",
                log_file=f"{self.log_dir}/task-2.3-automation-chain-analysis.log"
            ),
            
            CursorTask(
                task_id="2.4",
                name="Error Propagation Analysis", 
                spec_file=".kiro/specs/system-architecture-wiring-diagram/tasks.md",
                dependencies=["2.1"],  # Needs dependency analysis first
                priority=6,
                estimated_duration_minutes=40,
                cursor_command="cursor --task 'Implement error propagation analysis (Task 2.4)' --spec .kiro/specs/system-architecture-wiring-diagram/tasks.md",
                log_file=f"{self.log_dir}/task-2.4-error-propagation-analysis.log"
            ),
            
            # Phase 3: UML Diagram Generation Engine (depends on Phase 2)
            CursorTask(
                task_id="3.1",
                name="Comprehensive Diagram Generation System",
                spec_file=".kiro/specs/system-architecture-wiring-diagram/tasks.md",
                dependencies=["2.1", "2.2"],  # Needs relationship analysis
                priority=5,
                estimated_duration_minutes=60,
                cursor_command="cursor --task 'Implement comprehensive diagram generation system (Task 3.1)' --spec .kiro/specs/system-architecture-wiring-diagram/tasks.md",
                log_file=f"{self.log_dir}/task-3.1-diagram-generation-system.log"
            ),
            
            CursorTask(
                task_id="3.2",
                name="Observatory-Specific Sequence Diagrams",
                spec_file=".kiro/specs/system-architecture-wiring-diagram/tasks.md", 
                dependencies=["2.2", "2.3"],  # Needs data flow and automation analysis
                priority=5,
                estimated_duration_minutes=50,
                cursor_command="cursor --task 'Implement Observatory-specific sequence diagrams (Task 3.2)' --spec .kiro/specs/system-architecture-wiring-diagram/tasks.md",
                log_file=f"{self.log_dir}/task-3.2-observatory-sequence-diagrams.log"
            ),
            
            CursorTask(
                task_id="3.3",
                name="Network Topology Visualization",
                spec_file=".kiro/specs/system-architecture-wiring-diagram/tasks.md",
                dependencies=["1.6", "2.2"],  # Needs network discovery and data flow
                priority=4,
                estimated_duration_minutes=45,
                cursor_command="cursor --task 'Implement network topology visualization (Task 3.3)' --spec .kiro/specs/system-architecture-wiring-diagram/tasks.md",
                log_file=f"{self.log_dir}/task-3.3-network-topology-visualization.log"
            ),
            
            CursorTask(
                task_id="3.4",
                name="Real-Time Diagram Updates",
                spec_file=".kiro/specs/system-architecture-wiring-diagram/tasks.md",
                dependencies=["3.1"],  # Needs base diagram system
                priority=3,
                estimated_duration_minutes=40,
                cursor_command="cursor --task 'Implement real-time diagram updates (Task 3.4)' --spec .kiro/specs/system-architecture-wiring-diagram/tasks.md",
                log_file=f"{self.log_dir}/task-3.4-real-time-diagram-updates.log"
            )
        ]
        
        return tasks
    
    def validate_dag_structure(self) -> bool:
        """Validate that tasks form a proper DAG without cycles."""
        # Build adjacency list
        graph = {}
        for task in self.tasks:
            graph[task.task_id] = task.dependencies
        
        # Topological sort to detect cycles
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            if node in rec_stack:
                return True
            if node in visited:
                return False
                
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if has_cycle(neighbor):
                    return True
                    
            rec_stack.remove(node)
            return False
        
        # Check all nodes for cycles
        for task_id in graph:
            if task_id not in visited:
                if has_cycle(task_id):
                    return False
        
        return True
    
    def get_execution_order(self) -> List[List[str]]:
        """Get execution order with parallel batches."""
        # Build dependency count
        in_degree = {}
        graph = {}
        
        for task in self.tasks:
            task_id = task.task_id
            in_degree[task_id] = len(task.dependencies)
            graph[task_id] = []
        
        # Build reverse graph
        for task in self.tasks:
            for dep in task.dependencies:
                if dep in graph:
                    graph[dep].append(task.task_id)
        
        # Topological sort with levels
        execution_order = []
        queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
        
        while queue:
            # Current level can execute in parallel
            current_level = sorted(queue, key=lambda x: next(t.priority for t in self.tasks if t.task_id == x), reverse=True)
            execution_order.append(current_level)
            
            # Process next level
            next_queue = []
            for task_id in current_level:
                for neighbor in graph[task_id]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        next_queue.append(neighbor)
            
            queue = next_queue
        
        return execution_order
    
    def generate_cursor_execution_scripts(self) -> Dict[str, str]:
        """Generate Cursor CLI execution scripts for parallel execution."""
        
        if not self.validate_dag_structure():
            raise ValueError("Task dependencies contain cycles - invalid DAG structure")
        
        execution_order = self.get_execution_order()
        scripts = {}
        
        # Generate master orchestration script
        master_script = f"""#!/bin/bash
# System Architecture Wiring Diagram - Parallel Execution with Cursor CLI
# Generated: {datetime.now().isoformat()}
# Execution ID: {self.execution_timestamp}

set -e  # Exit on any error

echo "🐺 Starting DAG-Orchestrated Parallel Execution with Cursor CLI 🐺"
echo "Execution ID: {self.execution_timestamp}"
echo "Log Directory: {self.log_dir}"
echo ""

# Create log directory
mkdir -p {self.log_dir}

# Function to run task with proper logging
run_task() {{
    local task_id="$1"
    local task_name="$2" 
    local cursor_cmd="$3"
    local log_file="$4"
    
    echo "[${{task_id}}] Starting: ${{task_name}}"
    echo "[${{task_id}}] Command: ${{cursor_cmd}}"
    echo "[${{task_id}}] Log: ${{log_file}}"
    
    # Execute with timeout and logging
    timeout 3600 bash -c "${{cursor_cmd}} 2>&1 | tee ${{log_file}}" || {{
        echo "[${{task_id}}] FAILED or TIMEOUT"
        return 1
    }}
    
    echo "[${{task_id}}] COMPLETED"
    return 0
}}

# Function to wait for parallel tasks
wait_for_tasks() {{
    local pids=("$@")
    local failed=0
    
    for pid in "${{pids[@]}}"; do
        if ! wait "$pid"; then
            failed=1
        fi
    done
    
    return $failed
}}

"""

        # Generate execution phases
        for phase_num, phase_tasks in enumerate(execution_order, 1):
            master_script += f"""
echo ""
echo "🚀 Phase {phase_num}: Executing {len(phase_tasks)} tasks in parallel"
echo "Tasks: {', '.join(phase_tasks)}"
echo ""

# Start parallel tasks for Phase {phase_num}
pids_{phase_num}=()
"""
            
            for task_id in phase_tasks:
                task = next(t for t in self.tasks if t.task_id == task_id)
                master_script += f"""
# Task {task_id}: {task.name}
run_task "{task_id}" "{task.name}" "{task.cursor_command}" "{task.log_file}" &
pids_{phase_num}+=($!)
"""
            
            master_script += f"""
# Wait for Phase {phase_num} completion
echo "Waiting for Phase {phase_num} tasks to complete..."
if ! wait_for_tasks "${{pids_{phase_num}[@]}}"; then
    echo "❌ Phase {phase_num} had failures - check logs in {self.log_dir}"
    exit 1
fi

echo "✅ Phase {phase_num} completed successfully"
"""

        master_script += f"""
echo ""
echo "🎉 All phases completed successfully!"
echo "📊 Execution Summary:"
echo "  - Total Tasks: {len(self.tasks)}"
echo "  - Execution Phases: {len(execution_order)}"
echo "  - Log Directory: {self.log_dir}"
echo ""
echo "📋 Next Steps:"
echo "  1. Review logs in {self.log_dir}/"
echo "  2. Validate task outputs"
echo "  3. Run integration tests"
echo "  4. Generate final documentation"
echo ""
"""

        scripts["master_execution.sh"] = master_script
        
        # Generate individual task scripts
        for task in self.tasks:
            task_script = f"""#!/bin/bash
# Individual Task Script: {task.task_id} - {task.name}
# Generated: {datetime.now().isoformat()}

set -e

echo "🔧 Task {task.task_id}: {task.name}"
echo "Dependencies: {', '.join(task.dependencies) if task.dependencies else 'None'}"
echo "Priority: {task.priority}"
echo "Estimated Duration: {task.estimated_duration_minutes} minutes"
echo ""

# Check dependencies (basic validation)
"""
            
            for dep in task.dependencies:
                task_script += f"""
if [ ! -f "{self.log_dir}/task-{dep}-*.log" ]; then
    echo "❌ Dependency {dep} not completed - missing log file"
    exit 1
fi
"""
            
            task_script += f"""
# Execute task
echo "Executing: {task.cursor_command}"
{task.cursor_command} 2>&1 | tee {task.log_file}

echo "✅ Task {task.task_id} completed successfully"
"""
            
            scripts[f"task_{task.task_id.replace('.', '_')}.sh"] = task_script
        
        return scripts
    
    def create_execution_status_tracker(self) -> str:
        """Create a status tracking script for monitoring execution."""
        
        tracker_script = f"""#!/bin/bash
# Execution Status Tracker for System Architecture Wiring Diagram
# Generated: {datetime.now().isoformat()}

LOG_DIR="{self.log_dir}"

echo "📊 System Architecture Wiring Diagram - Execution Status"
echo "Execution ID: {self.execution_timestamp}"
echo "Log Directory: $LOG_DIR"
echo ""

# Function to check task status
check_task_status() {{
    local task_id="$1"
    local task_name="$2"
    local log_pattern="$3"
    
    if ls ${{log_pattern}} 1> /dev/null 2>&1; then
        if grep -q "COMPLETED\\|✅" ${{log_pattern}} 2>/dev/null; then
            echo "✅ [${{task_id}}] ${{task_name}} - COMPLETED"
        elif grep -q "FAILED\\|❌\\|ERROR" ${{log_pattern}} 2>/dev/null; then
            echo "❌ [${{task_id}}] ${{task_name}} - FAILED"
        else
            echo "🔄 [${{task_id}}] ${{task_name}} - RUNNING"
        fi
    else
        echo "⏳ [${{task_id}}] ${{task_name}} - PENDING"
    fi
}}

echo "Task Status:"
"""
        
        for task in self.tasks:
            tracker_script += f"""check_task_status "{task.task_id}" "{task.name}" "{task.log_file}"
"""
        
        tracker_script += f"""
echo ""
echo "📁 Log Files:"
ls -la {self.log_dir}/ 2>/dev/null || echo "No log files yet"

echo ""
echo "🔍 Recent Activity:"
tail -n 5 {self.log_dir}/*.log 2>/dev/null | head -20 || echo "No recent activity"
"""
        
        return tracker_script
    
    def prepare_parallel_execution(self) -> Dict[str, Any]:
        """Prepare complete parallel execution environment."""
        
        # Validate DAG structure
        if not self.validate_dag_structure():
            raise ValueError("Invalid DAG structure - contains cycles")
        
        # Generate execution scripts
        scripts = self.generate_cursor_execution_scripts()
        
        # Create status tracker
        status_tracker = self.create_execution_status_tracker()
        
        # Write all scripts to files
        script_files = {}
        
        # Master execution script
        master_file = f"scripts/cursor_parallel_execution_{self.execution_timestamp}.sh"
        with open(master_file, 'w') as f:
            f.write(scripts["master_execution.sh"])
        os.chmod(master_file, 0o755)
        script_files["master_execution"] = master_file
        
        # Individual task scripts
        task_script_dir = f"scripts/cursor_tasks_{self.execution_timestamp}"
        os.makedirs(task_script_dir, exist_ok=True)
        
        for script_name, script_content in scripts.items():
            if script_name != "master_execution.sh":
                script_file = f"{task_script_dir}/{script_name}"
                with open(script_file, 'w') as f:
                    f.write(script_content)
                os.chmod(script_file, 0o755)
                script_files[script_name] = script_file
        
        # Status tracker script
        status_file = f"scripts/cursor_status_tracker_{self.execution_timestamp}.sh"
        with open(status_file, 'w') as f:
            f.write(status_tracker)
        os.chmod(status_file, 0o755)
        script_files["status_tracker"] = status_file
        
        # Generate execution summary
        execution_order = self.get_execution_order()
        
        summary = {
            "execution_id": self.execution_timestamp,
            "total_tasks": len(self.tasks),
            "execution_phases": len(execution_order),
            "estimated_total_duration_minutes": sum(t.estimated_duration_minutes for t in self.tasks),
            "log_directory": self.log_dir,
            "script_files": script_files,
            "execution_order": execution_order,
            "task_details": [
                {
                    "task_id": t.task_id,
                    "name": t.name,
                    "dependencies": t.dependencies,
                    "priority": t.priority,
                    "estimated_duration_minutes": t.estimated_duration_minutes,
                    "cursor_command": t.cursor_command,
                    "log_file": t.log_file
                }
                for t in self.tasks
            ]
        }
        
        # Write execution summary
        summary_file = f"logs/cursor_execution_summary_{self.execution_timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        summary["summary_file"] = summary_file
        
        return summary


def main():
    """Main execution function."""
    print("🐺 Preparing DAG-Orchestrated Parallel Execution with Cursor CLI 🐺")
    print()
    
    try:
        # Initialize preparer
        preparer = CursorParallelExecutionPreparer()
        
        # Prepare execution environment
        summary = preparer.prepare_parallel_execution()
        
        print("✅ Parallel execution environment prepared successfully!")
        print()
        print("📊 Execution Summary:")
        print(f"  - Execution ID: {summary['execution_id']}")
        print(f"  - Total Tasks: {summary['total_tasks']}")
        print(f"  - Execution Phases: {summary['execution_phases']}")
        print(f"  - Estimated Duration: {summary['estimated_total_duration_minutes']} minutes")
        print(f"  - Log Directory: {summary['log_directory']}")
        print()
        print("🚀 To start execution:")
        print(f"  bash {summary['script_files']['master_execution']}")
        print()
        print("📊 To monitor progress:")
        print(f"  bash {summary['script_files']['status_tracker']}")
        print()
        print("📋 Execution Order:")
        for i, phase in enumerate(summary['execution_order'], 1):
            print(f"  Phase {i}: {', '.join(phase)}")
        print()
        
        return summary
        
    except Exception as e:
        print(f"❌ Failed to prepare parallel execution: {e}")
        raise


if __name__ == "__main__":
    main()