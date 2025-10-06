#!/usr/bin/env python3
"""
Constellation Elaboration DAG Orchestrator
Executes all 90 constellation elaboration prompts with dependency management
"""

import os
import sys
import json
import time
import asyncio
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict
import subprocess
import uuid

# Add src to path for Beast Mode imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, GracefulDegradationResult
from beast_mode.execution.dag_executor import DAGExecutor
from beast_mode.execution.task_registry import TaskRegistry


@dataclass
class PromptTask:
    """Represents a single prompt execution task"""
    name: str
    prompt_file: str
    dependencies: List[str]
    estimated_minutes: int
    status: str = "pending"  # pending, running, completed, failed
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_min: Optional[float] = None
    agent_id: Optional[str] = None
    outputs: List[str] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.outputs is None:
            self.outputs = []


class ConstellationOrchestrator(ReflectiveModule):
    """DAG-based orchestrator for constellation elaboration prompts"""
    
    def __init__(self, max_agents: int = 10):
        super().__init__()
        self.max_agents = max_agents
        self.execution_id = f"constellation-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.status_file = Path(".kiro/execution-status.json")
        self.logs_dir = Path(".kiro/execution-logs")
        self.prompts_dir = Path("prompts/staging")
        
        # Ensure directories exist
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize task registry
        self.task_registry = TaskRegistry()
        self.dag_executor = DAGExecutor(max_concurrent=max_agents)
        
        # Track running agents
        self.running_agents: Dict[str, asyncio.Task] = {}
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information"""
        return {
            "module_id": f"constellation_orchestrator_{self.execution_id}",
            "name": "Constellation Orchestrator",
            "version": "1.0.0",
            "description": "DAG-based orchestrator for constellation elaboration prompts",
            "execution_id": self.execution_id,
            "max_agents": self.max_agents
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.MONITORING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status"""
        return ModuleHealth(
            module_id=f"constellation_orchestrator_{self.execution_id}",
            status=ModuleStatus.HEALTHY,
            health_score=1.0,
            issues=[],
            last_check=datetime.now(timezone.utc),
            uptime_seconds=(datetime.now(timezone.utc) - self._start_time).total_seconds()
        )
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status"""
        return ModuleHealth(
            module_id=f"constellation_orchestrator_{self.execution_id}",
            status=ModuleStatus.HEALTHY,
            health_score=1.0,
            issues=[],
            last_check=datetime.now(timezone.utc),
            uptime_seconds=(datetime.now(timezone.utc) - self._start_time).total_seconds(),
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self):
        """Perform graceful degradation"""
        from src.rm_ddd.core.unified_reflective_module import GracefulDegradationResult
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=[],
            remaining_capabilities=self.get_capabilities()
        )
        
    def _load_task_definitions(self) -> Dict[str, PromptTask]:
        """Load task definitions with dependencies from actual staging prompts"""
        tasks = {}
        
        # Scan staging directory for actual prompts
        staging_prompts = list(self.prompts_dir.glob("*.md"))
        
        # Define core constellation tasks with dependencies
        core_tasks = [
            # Phase 1: Discovery (all parallel)
            ("phase-1a-constellation-inventory", [], 150),
            ("phase-1b-stakeholder-landscape-mapping", [], 120),
            ("phase-1c-cms-dependency-discovery", [], 90),
            ("phase-1d-ontology-gap-analysis", [], 105),
            
            # Phase 2: Requirements (sequential layers)
            ("phase-2-bootstrap-requirements", ["phase-1a-constellation-inventory"], 180),
            ("phase-2-foundation-requirements", ["phase-2-bootstrap-requirements"], 240),
            ("phase-2-intelligence-requirements", ["phase-2-foundation-requirements"], 300),
            ("phase-2-application-requirements", ["phase-2-intelligence-requirements"], 180),
            
            # Phase 3: Design (parallel based on requirements)
            ("phase-3-bootstrap-designs", ["phase-2-bootstrap-requirements"], 150),
            ("phase-3-foundation-designs", ["phase-2-foundation-requirements"], 200),
            ("phase-3-intelligence-designs", ["phase-2-intelligence-requirements"], 250),
            ("phase-3-application-designs", ["phase-2-application-requirements"], 150),
            
            # Phase 4: Tasks (parallel based on designs)
            ("phase-4-bootstrap-tasks", ["phase-3-bootstrap-designs"], 120),
            ("phase-4-foundation-tasks", ["phase-3-foundation-designs"], 160),
            ("phase-4-intelligence-tasks", ["phase-3-intelligence-designs"], 200),
            ("phase-4-application-tasks", ["phase-3-application-designs"], 120),
            
            # Phase 5: Consolidation (sequential)
            ("phase-5a-cms-requirements-consolidation", 
             ["phase-2-bootstrap-requirements", "phase-2-foundation-requirements", 
              "phase-2-intelligence-requirements", "phase-2-application-requirements"], 180),
            ("phase-5b-cms-architecture-update", ["phase-5a-cms-requirements-consolidation"], 120),
            ("phase-5c-constellation-cms-mapping", ["phase-5b-cms-architecture-update"], 90),
            ("phase-5d-stakeholder-validation", ["phase-5c-constellation-cms-mapping"], 60),
        ]
        
        # Create tasks for core constellation prompts
        for name, deps, est_min in core_tasks:
            prompt_file = f"{name}.md"
            if (self.prompts_dir / prompt_file).exists():
                tasks[name] = PromptTask(
                    name=name,
                    prompt_file=prompt_file,
                    dependencies=deps,
                    estimated_minutes=est_min
                )
        
        # Add batch tasks that exist in staging
        batch_dependencies = {
            # Phase 1 batches
            "phase-1b1-stakeholder-extraction": ["phase-1b-stakeholder-landscape-mapping"],
            "phase-1b2-stakeholder-dimension-analysis": ["phase-1b1-stakeholder-extraction"],
            "phase-1b3-stakeholder-journey-mapping": ["phase-1b2-stakeholder-dimension-analysis"],
            "phase-1c1-cms-dependency-scan": ["phase-1c-cms-dependency-discovery"],
            "phase-1c2-cms-data-model-extraction": ["phase-1c1-cms-dependency-scan"],
            "phase-1c3-cms-capability-analysis": ["phase-1c2-cms-data-model-extraction"],
            "phase-1d1-ontology-batch1": ["phase-1d-ontology-gap-analysis"],
            "phase-1d2-ontology-batch2": ["phase-1d1-ontology-batch1"],
            "phase-1d3-ontology-batch3": ["phase-1d2-ontology-batch2"],
            "phase-1d4-ontology-batch4": ["phase-1d3-ontology-batch3"],
            "phase-1d5-ontology-consolidation": ["phase-1d4-ontology-batch4"],
            
            # Phase 2 batches
            "phase-2-bootstrap-requirements-batch1": ["phase-2-bootstrap-requirements"],
            "phase-2-foundation-requirements-batch1": ["phase-2-foundation-requirements"],
            "phase-2-foundation-requirements-batch2": ["phase-2-foundation-requirements-batch1"],
            "phase-2-intelligence-requirements-batch1": ["phase-2-intelligence-requirements"],
            "phase-2-intelligence-requirements-batch2": ["phase-2-intelligence-requirements-batch1"],
            "phase-2-intelligence-requirements-batch3": ["phase-2-intelligence-requirements-batch2"],
            "phase-2-intelligence-requirements-batch4": ["phase-2-intelligence-requirements-batch3"],
            "phase-2-intelligence-requirements-batch5": ["phase-2-intelligence-requirements-batch4"],
            "phase-2-intelligence-requirements-batch6": ["phase-2-intelligence-requirements-batch5"],
            "phase-2-intelligence-requirements-batch7": ["phase-2-intelligence-requirements-batch6"],
            "phase-2-intelligence-requirements-batch8": ["phase-2-intelligence-requirements-batch7"],
            "phase-2-intelligence-requirements-batch9": ["phase-2-intelligence-requirements-batch8"],
            "phase-2-intelligence-requirements-batch10": ["phase-2-intelligence-requirements-batch9"],
            "phase-2-application-requirements-batch1": ["phase-2-application-requirements"],
            "phase-2-application-requirements-batch2": ["phase-2-application-requirements-batch1"],
        }
        
        # Add batch tasks that exist
        for prompt_file in staging_prompts:
            task_name = prompt_file.stem
            
            # Skip if already added as core task
            if task_name in tasks:
                continue
            
            # Determine dependencies and estimate
            dependencies = batch_dependencies.get(task_name, [])
            
            # Estimate based on task type
            if "batch" in task_name:
                est_min = 45  # Batch tasks are typically shorter
            elif task_name.startswith("phase-5"):
                est_min = 90   # Consolidation tasks
            elif task_name.startswith("phase-4"):
                est_min = 60   # Task definition
            elif task_name.startswith("phase-3"):
                est_min = 75   # Design tasks
            elif task_name.startswith("phase-2"):
                est_min = 90   # Requirements tasks
            elif task_name.startswith("phase-1"):
                est_min = 60   # Discovery tasks
            else:
                est_min = 30   # Other tasks
            
            tasks[task_name] = PromptTask(
                name=task_name,
                prompt_file=prompt_file.name,
                dependencies=dependencies,
                estimated_minutes=est_min
            )
        
        print(f"📋 Loaded {len(tasks)} constellation tasks from staging prompts")
        return tasks
    
    def _load_status(self) -> Dict:
        """Load execution status from file"""
        if self.status_file.exists():
            with open(self.status_file, 'r') as f:
                return json.load(f)
        
        # Initialize new status
        tasks = self._load_task_definitions()
        status = {
            "execution_id": self.execution_id,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "status": "running",
            "max_agents": self.max_agents,
            "prompts": {name: asdict(task) for name, task in tasks.items()}
        }
        self._save_status(status)
        return status
    
    def _save_status(self, status: Dict):
        """Save execution status to file"""
        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2)
    
    async def _execute_prompt(self, task_name: str, prompt_file: str) -> Dict:
        """Execute a single prompt using Claude CLI"""
        agent_id = f"agent-{int(time.time())}-{uuid.uuid4().hex[:6]}"
        
        # Update status to running
        status = self._load_status()
        status["prompts"][task_name].update({
            "status": "running",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "agent_id": agent_id
        })
        self._save_status(status)
        
        # Prepare output files
        output_file = self.logs_dir / f"{task_name}.out"
        error_file = self.logs_dir / f"{task_name}.err"
        
        try:
            # Execute Claude CLI with prompt
            prompt_path = self.prompts_dir / prompt_file
            
            if not prompt_path.exists():
                raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
            
            # Run Claude CLI
            start_time = time.time()
            
            with open(output_file, 'w') as out_f, open(error_file, 'w') as err_f:
                process = await asyncio.create_subprocess_exec(
                    'claude', 
                    stdin=asyncio.subprocess.PIPE,
                    stdout=out_f,
                    stderr=err_f
                )
                
                # Send prompt content to Claude
                with open(prompt_path, 'r') as prompt_f:
                    prompt_content = prompt_f.read()
                
                stdout, stderr = await process.communicate(prompt_content.encode())
                
                if process.returncode != 0:
                    raise subprocess.CalledProcessError(process.returncode, 'claude')
            
            duration_min = (time.time() - start_time) / 60
            
            # Update status to completed
            status = self._load_status()
            status["prompts"][task_name].update({
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "duration_min": duration_min,
                "outputs": [str(output_file)],
                "success": True,
                "error": None
            })
            self._save_status(status)
            
            return {"success": True, "duration_min": duration_min}
            
        except Exception as e:
            # Update status to failed
            status = self._load_status()
            status["prompts"][task_name].update({
                "status": "failed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "error": str(e),
                "success": False
            })
            self._save_status(status)
            
            return {"success": False, "error": str(e)}
    
    def _get_ready_tasks(self, status: Dict) -> List[str]:
        """Get tasks that are ready to run (dependencies satisfied)"""
        ready_tasks = []
        
        for task_name, task_data in status["prompts"].items():
            if task_data["status"] != "pending":
                continue
            
            # Check if all dependencies are completed
            dependencies_satisfied = True
            for dep in task_data["dependencies"]:
                if dep not in status["prompts"]:
                    dependencies_satisfied = False
                    break
                if status["prompts"][dep]["status"] != "completed":
                    dependencies_satisfied = False
                    break
            
            if dependencies_satisfied:
                ready_tasks.append(task_name)
        
        return ready_tasks
    
    async def execute(self, resume: bool = False):
        """Execute the constellation elaboration DAG"""
        print(f"🚀 Starting Constellation Elaboration Execution")
        print(f"📊 Execution ID: {self.execution_id}")
        print(f"🤖 Max Agents: {self.max_agents}")
        print(f"📁 Logs Directory: {self.logs_dir}")
        print("=" * 80)
        
        if resume:
            print("🔄 Resuming previous execution...")
        
        try:
            while True:
                status = self._load_status()
                
                # Get tasks ready to run
                ready_tasks = self._get_ready_tasks(status)
                
                # Remove completed agents
                completed_agents = []
                for agent_id, task in list(self.running_agents.items()):
                    if task.done():
                        completed_agents.append(agent_id)
                        del self.running_agents[agent_id]
                
                # Start new tasks if we have capacity and ready tasks
                available_slots = self.max_agents - len(self.running_agents)
                tasks_to_start = ready_tasks[:available_slots]
                
                for task_name in tasks_to_start:
                    task_data = status["prompts"][task_name]
                    prompt_file = task_data["prompt_file"]
                    
                    print(f"🔄 Starting: {task_name}")
                    
                    # Start the task
                    agent_task = asyncio.create_task(
                        self._execute_prompt(task_name, prompt_file)
                    )
                    self.running_agents[task_name] = agent_task
                
                # Check if we're done
                all_completed = all(
                    task_data["status"] in ["completed", "failed"]
                    for task_data in status["prompts"].values()
                )
                
                if all_completed and not self.running_agents:
                    break
                
                # Wait a bit before checking again
                await asyncio.sleep(2)
            
            # Final status update
            status = self._load_status()
            status["status"] = "completed"
            status["completed_at"] = datetime.now(timezone.utc).isoformat()
            self._save_status(status)
            
            # Print summary
            self._print_summary(status)
            
        except KeyboardInterrupt:
            print("\n🛑 Execution interrupted by user")
            status = self._load_status()
            status["status"] = "interrupted"
            self._save_status(status)
            
            # Cancel running tasks
            for task in self.running_agents.values():
                task.cancel()
            
            print("💾 Status saved. Resume with --resume flag")
    
    def _print_summary(self, status: Dict):
        """Print execution summary"""
        total = len(status["prompts"])
        completed = sum(1 for p in status["prompts"].values() if p["status"] == "completed")
        failed = sum(1 for p in status["prompts"].values() if p["status"] == "failed")
        
        print("\n" + "=" * 80)
        print("🎉 CONSTELLATION ELABORATION COMPLETE")
        print("=" * 80)
        print(f"📊 Total Tasks: {total}")
        print(f"✅ Completed: {completed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {completed/total*100:.1f}%")
        
        if failed > 0:
            print(f"\n❌ Failed Tasks:")
            for name, data in status["prompts"].items():
                if data["status"] == "failed":
                    print(f"  - {name}: {data.get('error', 'Unknown error')}")
        
        total_duration = sum(
            p.get("duration_min", 0) 
            for p in status["prompts"].values() 
            if p.get("duration_min")
        )
        print(f"\n⏱️  Total Execution Time: {total_duration:.1f} minutes")
        print(f"📁 Logs saved to: {self.logs_dir}")
        print(f"📊 Status file: {self.status_file}")


async def main():
    parser = argparse.ArgumentParser(description="Constellation Elaboration DAG Orchestrator")
    parser.add_argument("max_agents", type=int, nargs='?', default=10, 
                       help="Maximum number of concurrent agents (default: 10)")
    parser.add_argument("--resume", action="store_true", 
                       help="Resume previous execution")
    
    args = parser.parse_args()
    
    orchestrator = ConstellationOrchestrator(max_agents=args.max_agents)
    await orchestrator.execute(resume=args.resume)


if __name__ == "__main__":
    asyncio.run(main())