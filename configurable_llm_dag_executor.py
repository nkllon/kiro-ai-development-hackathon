#!/usr/bin/env python3
"""
Configurable LLM DAG Executor - CLI Agnostic
============================================

A DAG executor that can use any LLM CLI (Kiro, Claude, OpenAI, etc.)
and properly captures outputs for system architecture implementation.
"""

import asyncio
import subprocess
import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class LLMProvider(Enum):
    """Supported LLM CLI providers."""
    KIRO = "kiro"
    CLAUDE = "claude" 
    CURSOR = "cursor"
    OPENAI = "openai"
    LLM = "llm"
    SHELL_GPT = "sgpt"
    AIDER = "aider"


@dataclass
class LLMConfig:
    """Configuration for LLM CLI."""
    provider: LLMProvider
    command: str
    args: List[str]
    stdin_flag: str = "-"
    output_capture: bool = True
    timeout_seconds: int = 300


class ConfigurableLLMDAGExecutor:
    """
    CLI-agnostic DAG executor that can use any LLM provider
    and properly capture outputs for verification.
    """
    
    def __init__(self, llm_config: Optional[LLMConfig] = None):
        self.execution_id = f"llm-dag-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.log_dir = Path(f"logs/llm-dag/{self.execution_id}")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Default to Kiro if no config provided
        self.llm_config = llm_config or self._get_default_llm_config()
        self.active_processes = {}
        
        # Validate LLM CLI is available
        self._validate_llm_cli()
        
    def _get_default_llm_config(self) -> LLMConfig:
        """Get default LLM configuration (tries to detect available CLI)."""
        
        # Try to detect available LLM CLIs
        available_clis = self._detect_available_clis()
        
        if "cursor" in available_clis:
            return LLMConfig(
                provider=LLMProvider.CURSOR,
                command="cursor",
                args=["--print", "-"],
                output_capture=True
            )
        elif "kiro" in available_clis:
            return LLMConfig(
                provider=LLMProvider.KIRO,
                command="kiro",
                args=["-"],
                output_capture=True
            )
        elif "claude" in available_clis:
            return LLMConfig(
                provider=LLMProvider.CLAUDE,
                command="claude",
                args=["-"],
                output_capture=True
            )
        elif "llm" in available_clis:
            return LLMConfig(
                provider=LLMProvider.LLM,
                command="llm",
                args=["-"],
                output_capture=True
            )
        else:
            # Fallback to echo (for testing)
            return LLMConfig(
                provider=LLMProvider.KIRO,  # Default enum
                command="echo",
                args=["[MOCK LLM RESPONSE]"],
                output_capture=True
            )
    
    def _detect_available_clis(self) -> List[str]:
        """Detect which LLM CLIs are available on the system."""
        available = []
        
        cli_commands = ["kiro", "claude", "cursor", "llm", "sgpt", "aider"]
        
        for cli in cli_commands:
            try:
                result = subprocess.run(
                    ["which", cli], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                if result.returncode == 0:
                    available.append(cli)
            except Exception:
                continue
                
        return available
    
    def _validate_llm_cli(self):
        """Validate that the configured LLM CLI is available."""
        try:
            result = subprocess.run(
                ["which", self.llm_config.command],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                print(f"⚠️  Warning: {self.llm_config.command} not found in PATH")
                print(f"   Available CLIs: {self._detect_available_clis()}")
                
        except Exception as e:
            print(f"❌ Error validating LLM CLI: {e}")
    
    def create_task_prompt(self, task_id: str, task_name: str, dependencies: List[str] = None) -> str:
        """Create a comprehensive prompt for the LLM to execute a specific task."""
        
        dependencies_text = f"Dependencies: {', '.join(dependencies)}" if dependencies else "Dependencies: None"
        
        prompt = f"""
SYSTEM ARCHITECTURE WIRING DIAGRAM IMPLEMENTATION
Task ID: {task_id}
Task: {task_name}
{dependencies_text}
Execution ID: {self.execution_id}
LLM Provider: {self.llm_config.provider.value}

CONTEXT:
You are implementing the System Architecture Wiring Diagram specification.
- Spec Location: .kiro/specs/system-architecture-wiring-diagram/
- Use ReflectiveModule pattern from src.rm_ddd.core.unified_reflective_module
- Follow Beast Mode systematic approaches
- Create production-ready code with >90% test coverage

SPECIFIC TASK IMPLEMENTATION:
{self._get_task_details(task_id)}

REQUIREMENTS:
1. Read the full spec requirements and design documents
2. Implement systematic, production-ready code
3. Create comprehensive tests
4. Use proper error handling and logging
5. Follow mathematical governance principles
6. Integrate with existing Beast Mode framework

DELIVERABLES:
- Working implementation with tests
- Integration with existing Beast Mode framework  
- Documentation updates
- Health monitoring endpoints
- Prometheus metrics integration

EXECUTION INSTRUCTIONS:
- Implement the code systematically
- Create all necessary files and directories
- Write comprehensive tests
- Document integration points
- Report completion status when done

IMPORTANT: Please provide actual code implementation, not just acknowledgment.

Execute this task now and report when complete.
"""
        return prompt.strip()
    
    def _get_task_details(self, task_id: str) -> str:
        """Get specific implementation details for each task."""
        
        task_details = {
            "1.1_project_structure_setup": """
Create the project structure and InfrastructureDiscoverer class:

1. Create directory structure:
   - src/system_architecture/discovery/
   - src/system_architecture/analysis/
   - src/system_architecture/generation/
   - src/system_architecture/orchestration/

2. Implement InfrastructureDiscoverer class:
   - Inherit from ReflectiveModule
   - Implement service discovery methods
   - Add Observatory WebSocket client integration
   - Create enhanced data models with versioning
   - Add comprehensive error handling

3. Create discovery interfaces for services, network topology, and automation scripts
""",
            "1.2_observatory_websocket_integration": """
Implement Observatory WebSocket integration:

1. Create ObservatoryWebSocketClient class
2. Implement real-time service discovery
3. Add WebSocket endpoint health monitoring
4. Create correlation ID tracking system
5. Implement connection recovery procedures
""",
            "1.3_service_discovery_scanner": """
Implement comprehensive service discovery scanner:

1. Build unified scanner for Observatory/Prometheus/Grafana
2. Create configuration parser for YAML/JSON configs
3. Implement network analyzer for port mappings
4. Add ReflectiveModule health validation
5. Map WebSocket endpoints and script relationships
""",
            "2.1_dag_dependency_analysis": """
Implement DAG-compliant dependency analysis:

1. Create RelationshipMapper class with mathematical validation
2. Build dependency graph analysis with cycle detection
3. Implement DAG Registry integration
4. Map ReflectiveModule initialization sequences
5. Create dependency visualization with validation status
""",
            "2.2_data_flow_mapping": """
Implement comprehensive data flow mapping:

1. Trace metrics flow from ReflectiveModule → Observatory → Prometheus → Grafana
2. Map WebSocket real-time metrics streaming
3. Document systematic error handling with correlation IDs
4. Create integration flow mapping (ACE Reporter → AI Memory Palace → DAG Registry)
5. Map WebSocket message flows and emoji rain data flow
"""
        }
        
        return task_details.get(task_id, f"Implement {task_id} according to the specification requirements.")
    
    async def execute_llm_task(self, task_id: str, task_name: str, dependencies: List[str] = None) -> Dict[str, Any]:
        """
        Execute a task using the configured LLM CLI and capture full output.
        """
        
        print(f"🚀 Executing {self.llm_config.provider.value} task: {task_id}")
        
        # Create task prompt
        prompt = self.create_task_prompt(task_id, task_name, dependencies)
        
        # Create log files
        prompt_file = self.log_dir / f"{task_id}-prompt.txt"
        output_file = self.log_dir / f"{task_id}-output.txt"
        error_file = self.log_dir / f"{task_id}-error.txt"
        
        # Save prompt
        with open(prompt_file, 'w') as f:
            f.write(prompt)
        
        # Build command
        if self.llm_config.output_capture:
            # Use tee to capture both log and pass to LLM
            cmd = f'cat "{prompt_file}" | tee "{prompt_file}.sent" | {self.llm_config.command} {" ".join(self.llm_config.args)} > "{output_file}" 2> "{error_file}"'
        else:
            # Simple execution
            cmd = f'cat "{prompt_file}" | {self.llm_config.command} {" ".join(self.llm_config.args)}'
        
        try:
            start_time = datetime.now()
            
            # Execute command
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE if not self.llm_config.output_capture else None,
                stderr=subprocess.PIPE if not self.llm_config.output_capture else None,
                text=True
            )
            
            # Wait for completion with timeout
            stdout, stderr = process.communicate(timeout=self.llm_config.timeout_seconds)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Read captured output if using file capture
            output_content = ""
            error_content = ""
            
            if self.llm_config.output_capture:
                if output_file.exists():
                    output_content = output_file.read_text()
                if error_file.exists():
                    error_content = error_file.read_text()
            else:
                output_content = stdout or ""
                error_content = stderr or ""
            
            result = {
                "task_id": task_id,
                "status": "completed" if process.returncode == 0 else "failed",
                "exit_code": process.returncode,
                "duration_seconds": duration,
                "output": output_content,
                "error": error_content,
                "prompt_file": str(prompt_file),
                "output_file": str(output_file) if self.llm_config.output_capture else None,
                "llm_provider": self.llm_config.provider.value
            }
            
            # Analyze output quality
            result["output_analysis"] = self._analyze_output_quality(output_content)
            
            print(f"✅ Task {task_id} completed in {duration:.2f}s")
            if result["output_analysis"]["has_code"]:
                print(f"   📝 Generated {result['output_analysis']['code_blocks']} code blocks")
            
            return result
            
        except subprocess.TimeoutExpired:
            process.kill()
            return {
                "task_id": task_id,
                "status": "timeout",
                "exit_code": -1,
                "duration_seconds": self.llm_config.timeout_seconds,
                "error": f"Task timed out after {self.llm_config.timeout_seconds} seconds",
                "llm_provider": self.llm_config.provider.value
            }
            
        except Exception as e:
            return {
                "task_id": task_id,
                "status": "error",
                "exit_code": -1,
                "error": str(e),
                "llm_provider": self.llm_config.provider.value
            }
    
    def _analyze_output_quality(self, output: str) -> Dict[str, Any]:
        """Analyze the quality and content of LLM output."""
        
        analysis = {
            "length": len(output),
            "has_code": "```" in output or "def " in output or "class " in output,
            "code_blocks": output.count("```"),
            "has_imports": "import " in output or "from " in output,
            "has_classes": "class " in output,
            "has_functions": "def " in output,
            "mentions_reflective_module": "ReflectiveModule" in output,
            "mentions_beast_mode": "beast_mode" in output or "Beast Mode" in output,
            "has_error_handling": "try:" in output or "except" in output,
            "has_logging": "logging" in output or "logger" in output,
            "quality_score": 0.0
        }
        
        # Calculate quality score
        score = 0.0
        if analysis["has_code"]: score += 0.3
        if analysis["has_classes"]: score += 0.2
        if analysis["has_functions"]: score += 0.2
        if analysis["mentions_reflective_module"]: score += 0.1
        if analysis["has_error_handling"]: score += 0.1
        if analysis["has_logging"]: score += 0.1
        
        analysis["quality_score"] = min(score, 1.0)
        
        return analysis
    
    async def execute_dag_tasks(self, tasks: List[Dict[str, Any]], execution_mode: str = "parallel") -> Dict[str, Any]:
        """Execute a list of DAG tasks with dependency management and parallel execution."""
        
        print(f"🐺 CONFIGURABLE LLM DAG EXECUTION STARTED 🐺")
        print(f"LLM Provider: {self.llm_config.provider.value}")
        print(f"Command: {self.llm_config.command}")
        print(f"Execution Mode: {execution_mode}")
        print(f"Execution ID: {self.execution_id}")
        print(f"Total tasks: {len(tasks)}")
        print(f"Log directory: {self.log_dir}")
        print()
        
        results = {}
        completed_tasks = set()
        failed_tasks = set()
        
        if execution_mode == "parallel":
            results = await self._execute_parallel_dag(tasks)
        else:
            results = await self._execute_sequential_dag(tasks)
        
        # Count results
        completed_count = len([r for r in results.values() if r.get("status") == "completed"])
        failed_count = len([r for r in results.values() if r.get("status") == "failed"])
        
        # Generate execution report
        execution_report = {
            "execution_id": self.execution_id,
            "llm_provider": self.llm_config.provider.value,
            "execution_mode": execution_mode,
            "total_tasks": len(tasks),
            "completed_tasks": completed_count,
            "failed_tasks": failed_count,
            "tasks": results,
            "log_directory": str(self.log_dir),
            "timestamp": datetime.now().isoformat()
        }
        
        # Save execution report
        report_file = f"CONFIGURABLE_LLM_DAG_EXECUTION_REPORT_{self.execution_id}.json"
        with open(report_file, 'w') as f:
            json.dump(execution_report, f, indent=2, default=str)
        
        print(f"\n🎯 CONFIGURABLE LLM DAG EXECUTION COMPLETED")
        print(f"Total tasks: {execution_report['total_tasks']}")
        print(f"Completed: {execution_report['completed_tasks']}")
        print(f"Failed: {execution_report['failed_tasks']}")
        print(f"📊 Execution report saved to: {report_file}")
        
        return execution_report
    
    async def _execute_sequential_dag(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute tasks sequentially with dependency checking."""
        
        results = {}
        completed_tasks = set()
        
        # Sort tasks by dependencies (simple topological sort)
        remaining_tasks = tasks.copy()
        
        while remaining_tasks:
            # Find tasks with satisfied dependencies
            ready_tasks = [
                task for task in remaining_tasks
                if all(dep in completed_tasks for dep in task.get("dependencies", []))
            ]
            
            if not ready_tasks:
                print("❌ Circular dependency detected or missing dependencies!")
                break
            
            # Execute ready tasks
            for task in ready_tasks:
                task_id = task["task_id"]
                task_name = task["name"]
                dependencies = task.get("dependencies", [])
                
                print(f"🚀 Executing task {task_id}: {task_name}")
                result = await self.execute_llm_task(task_id, task_name, dependencies)
                results[task_id] = result
                
                if result["status"] == "completed":
                    completed_tasks.add(task_id)
                    print(f"✅ Task {task_id} completed successfully")
                else:
                    print(f"❌ Task {task_id} failed: {result.get('error', 'Unknown error')}")
                
                remaining_tasks.remove(task)
        
        return results
    
    async def _execute_parallel_dag(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute tasks in parallel where dependencies allow."""
        
        results = {}
        completed_tasks = set()
        remaining_tasks = tasks.copy()
        
        while remaining_tasks:
            # Find tasks with satisfied dependencies
            ready_tasks = [
                task for task in remaining_tasks
                if all(dep in completed_tasks for dep in task.get("dependencies", []))
            ]
            
            if not ready_tasks:
                print("❌ No more tasks can be executed - possible circular dependency!")
                break
            
            print(f"🔄 Executing {len(ready_tasks)} tasks in parallel...")
            
            # Execute ready tasks in parallel (limited concurrency)
            semaphore = asyncio.Semaphore(4)  # Max 4 concurrent tasks
            
            async def execute_with_semaphore(task):
                async with semaphore:
                    task_id = task["task_id"]
                    task_name = task["name"]
                    dependencies = task.get("dependencies", [])
                    
                    print(f"🚀 Starting parallel task {task_id}: {task_name}")
                    result = await self.execute_llm_task(task_id, task_name, dependencies)
                    return task_id, result, task
            
            # Execute all ready tasks concurrently
            parallel_results = await asyncio.gather(
                *[execute_with_semaphore(task) for task in ready_tasks],
                return_exceptions=True
            )
            
            # Process results
            for result in parallel_results:
                if isinstance(result, Exception):
                    print(f"❌ Parallel execution error: {result}")
                    continue
                
                task_id, task_result, task = result
                results[task_id] = task_result
                
                if task_result["status"] == "completed":
                    completed_tasks.add(task_id)
                    print(f"✅ Parallel task {task_id} completed successfully")
                else:
                    print(f"❌ Parallel task {task_id} failed: {task_result.get('error', 'Unknown error')}")
                
                remaining_tasks.remove(task)
        
        return results


def load_system_architecture_tasks() -> Dict[str, Any]:
    """Load system architecture tasks from JSON configuration."""
    
    config_file = Path("system_architecture_dag_tasks.json")
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            return json.load(f)
    else:
        # Fallback to basic tasks if config file not found
        return {
            "task_groups": {
                "foundation": {
                    "tasks": [
                        {
                            "task_id": "1.1",
                            "name": "Set up project structure and core discovery system",
                            "dependencies": []
                        }
                    ]
                }
            }
        }

def create_system_architecture_tasks() -> List[Dict[str, Any]]:
    """Create system architecture tasks for DAG execution from JSON config."""
    
    config = load_system_architecture_tasks()
    tasks = []
    
    # Extract all tasks from task groups
    for group_name, group_data in config.get("task_groups", {}).items():
        for task in group_data.get("tasks", []):
            tasks.append({
                "task_id": task["task_id"],
                "name": task["name"],
                "dependencies": task.get("dependencies", []),
                "group": group_name,
                "priority": task.get("priority", "medium"),
                "estimated_duration": task.get("estimated_duration_minutes", 30),
                "requirements": task.get("requirements", []),
                "deliverables": task.get("deliverables", [])
            })
    
    return tasks


async def main():
    """Main execution function with command line argument support."""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="System Architecture DAG Executor")
    parser.add_argument("--tasks", help="Task group to execute (e.g., 'foundation', 'discovery_parallel')")
    parser.add_argument("--mode", choices=["sequential", "parallel"], default="parallel", help="Execution mode")
    parser.add_argument("--llm", choices=["kiro", "claude", "cursor", "llm", "openai"], help="LLM provider to use")
    parser.add_argument("--dry-run", action="store_true", help="Show tasks that would be executed without running them")
    
    args = parser.parse_args()
    
    # Create configurable executor
    llm_config = None
    if args.llm:
        llm_config = LLMConfig(
            provider=LLMProvider(args.llm),
            command=args.llm,
            args=["-"],
            output_capture=True
        )
    
    executor = ConfigurableLLMDAGExecutor(llm_config)
    
    # Load task configuration
    config = load_system_architecture_tasks()
    
    # Create tasks based on arguments
    if args.tasks:
        # Execute specific task group
        if args.tasks in config.get("task_groups", {}):
            group_tasks = config["task_groups"][args.tasks]["tasks"]
            tasks = []
            for task in group_tasks:
                tasks.append({
                    "task_id": task["task_id"],
                    "name": task["name"],
                    "dependencies": task.get("dependencies", []),
                    "group": args.tasks,
                    "priority": task.get("priority", "medium"),
                    "estimated_duration": task.get("estimated_duration_minutes", 30),
                    "requirements": task.get("requirements", []),
                    "deliverables": task.get("deliverables", [])
                })
        else:
            print(f"❌ Task group '{args.tasks}' not found!")
            print(f"Available groups: {list(config.get('task_groups', {}).keys())}")
            return
    else:
        # Execute all tasks
        tasks = create_system_architecture_tasks()
    
    if args.dry_run:
        print("🔍 DRY RUN - Tasks that would be executed:")
        for task in tasks:
            deps = ", ".join(task.get("dependencies", [])) or "None"
            print(f"  {task['task_id']}: {task['name']} (deps: {deps})")
        return
    
    # Execute DAG
    result = await executor.execute_dag_tasks(tasks, execution_mode=args.mode)
    
    return result


if __name__ == "__main__":
    asyncio.run(main())