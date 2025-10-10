#!/usr/bin/env python3
"""
Constellation Execution Orchestrator

Manages parallel execution of constellation elaboration prompts
with dependency tracking and status monitoring.

Usage:
    python scripts/constellation_orchestrator.py [max_agents]
    python scripts/constellation_orchestrator.py 10
    python scripts/constellation_orchestrator.py --resume
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Optional
import argparse

# Import Redis streaming (optional)
try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.constellation_streaming.redis_stream import RedisStatusStream
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class ConstellationOrchestrator:
    def __init__(
        self,
        status_file: str = ".kiro/execution-status.json",
        max_agents: int = 10,
        prompts_dir: str = "prompts/staging",
        output_dir: str = ".kiro/execution-logs",
        enable_streaming: bool = True,
        redis_url: str = "redis://localhost:6379",
    ):
        self.status_file = Path(status_file)
        self.max_agents = max_agents
        self.prompts_dir = Path(prompts_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Redis streaming
        self.redis_stream: Optional[RedisStatusStream] = None
        if enable_streaming and REDIS_AVAILABLE:
            try:
                self.redis_stream = RedisStatusStream(redis_url)
                print("📡 Redis streaming enabled")
            except Exception as e:
                print(f"⚠️  Redis streaming unavailable: {e}")
                self.redis_stream = None

        # Load or initialize status
        self.status = self.load_or_init_status()
        self.agent_pool = asyncio.Semaphore(max_agents)

    def load_or_init_status(self) -> Dict:
        """Load existing status or initialize new execution"""
        if self.status_file.exists():
            with open(self.status_file) as f:
                status = json.load(f)
                print(f"📂 Resuming execution: {status['execution_id']}")
                return status

        print("🚀 Starting new execution")
        return self.init_status()

    def init_status(self) -> Dict:
        """Initialize new execution status"""
        execution_id = f"constellation-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # Define all prompts with dependencies
        # This is hardcoded for now, but could be loaded from DAG file
        prompts = self.define_prompt_dag()

        status = {
            "execution_id": execution_id,
            "started_at": datetime.now().isoformat(),
            "status": "pending",
            "max_agents": self.max_agents,
            "prompts": prompts,
        }

        self.save_status(status)
        return status

    def define_prompt_dag(self) -> Dict:
        """Define all prompts with their dependencies"""
        prompts = {}

        # Phase 1: Discovery (14 prompts)
        phase1 = {
            "phase-1a-constellation-inventory": {
                "dependencies": [],
                "estimated_min": 150,
            },
            "phase-1b1-stakeholder-extraction": {
                "dependencies": [],
                "estimated_min": 75,
            },
            "phase-1b2-stakeholder-dimension-analysis": {
                "dependencies": ["phase-1b1-stakeholder-extraction"],
                "estimated_min": 105,
            },
            "phase-1b3-stakeholder-journey-mapping": {
                "dependencies": ["phase-1b1-stakeholder-extraction"],
                "estimated_min": 105,
            },
            "phase-1c1-cms-dependency-scan": {
                "dependencies": [],
                "estimated_min": 83,
            },
            "phase-1c2-cms-data-model-extraction": {
                "dependencies": ["phase-1c1-cms-dependency-scan"],
                "estimated_min": 105,
            },
            "phase-1c3-cms-capability-analysis": {
                "dependencies": ["phase-1c1-cms-dependency-scan"],
                "estimated_min": 83,
            },
            "phase-1d1-ontology-batch1": {
                "dependencies": [],
                "estimated_min": 98,
            },
            "phase-1d2-ontology-batch2": {
                "dependencies": [],
                "estimated_min": 105,
            },
            "phase-1d3-ontology-batch3": {
                "dependencies": [],
                "estimated_min": 105,
            },
            "phase-1d4-ontology-batch4": {
                "dependencies": [],
                "estimated_min": 98,
            },
            "phase-1d5-ontology-consolidation": {
                "dependencies": [
                    "phase-1d1-ontology-batch1",
                    "phase-1d2-ontology-batch2",
                    "phase-1d3-ontology-batch3",
                    "phase-1d4-ontology-batch4",
                ],
                "estimated_min": 60,
            },
        }

        # Initialize all prompts with default structure
        for name, config in phase1.items():
            prompts[name] = {
                "status": "pending",
                "started_at": None,
                "completed_at": None,
                "duration_min": None,
                "agent_id": None,
                "dependencies": config["dependencies"],
                "estimated_min": config["estimated_min"],
                "outputs": [],
                "success": None,
                "error": None,
            }

        # Phase 2-5 prompts would be added similarly
        # For now, just Phase 1 for demonstration

        return prompts

    def save_status(self, status: Dict = None):
        """Save current status to file and stream to Redis"""
        if status is None:
            status = self.status

        # Save to file
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.status_file, "w") as f:
            json.dump(status, f, indent=2)

        # Stream to Redis
        if self.redis_stream:
            try:
                self.redis_stream.publish_status(status)
                self.redis_stream.cache_status(status)
            except Exception as e:
                # Don't fail if streaming fails
                pass

    def get_ready_prompts(self) -> List[str]:
        """Get prompts ready to execute (dependencies satisfied)"""
        ready = []
        for prompt, info in self.status["prompts"].items():
            if info["status"] == "pending":
                # Check if all dependencies are completed
                deps_satisfied = all(
                    self.status["prompts"].get(dep, {}).get("status") == "completed"
                    for dep in info["dependencies"]
                )
                if deps_satisfied:
                    ready.append(prompt)
        return ready

    def get_execution_stats(self) -> Dict:
        """Get current execution statistics"""
        total = len(self.status["prompts"])
        pending = sum(1 for p in self.status["prompts"].values() if p["status"] == "pending")
        running = sum(1 for p in self.status["prompts"].values() if p["status"] == "running")
        completed = sum(1 for p in self.status["prompts"].values() if p["status"] == "completed")
        failed = sum(1 for p in self.status["prompts"].values() if p["status"] == "failed")

        return {
            "total": total,
            "pending": pending,
            "running": running,
            "completed": completed,
            "failed": failed,
            "progress_percent": round((completed + failed) / total * 100, 1) if total > 0 else 0,
        }

    async def execute_prompt(self, prompt_name: str, agent_id: int):
        """Execute a single prompt"""
        async with self.agent_pool:
            try:
                # Update status to running
                agent_id_str = f"agent-{agent_id:03d}"
                self.status["prompts"][prompt_name]["status"] = "running"
                self.status["prompts"][prompt_name]["started_at"] = (
                    datetime.now().isoformat()
                )
                self.status["prompts"][prompt_name]["agent_id"] = agent_id_str
                self.save_status()

                # Stream prompt start event
                if self.redis_stream:
                    self.redis_stream.publish_prompt_update(
                        prompt_name, "running", agent_id=agent_id_str
                    )
                    self.redis_stream.publish_event(
                        "prompt_started",
                        f"Started {prompt_name}",
                        {"prompt": prompt_name, "agent": agent_id_str},
                    )

                # Execute the prompt
                prompt_file = self.prompts_dir / f"{prompt_name}.md"
                output_file = self.output_dir / f"{prompt_name}.out"
                error_file = self.output_dir / f"{prompt_name}.err"

                print(
                    f"[Agent {agent_id:03d}] 🔄 Starting: {prompt_name} (est. {self.status['prompts'][prompt_name]['estimated_min']} min)"
                )

                # Check if prompt file exists
                if not prompt_file.exists():
                    raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

                # Run claude with the prompt
                with open(prompt_file) as stdin_file:
                    proc = await asyncio.create_subprocess_exec(
                        "claude",
                        stdin=stdin_file,
                        stdout=open(output_file, "w"),
                        stderr=open(error_file, "w"),
                    )

                    await proc.wait()

                # Update status to completed
                self.status["prompts"][prompt_name]["status"] = "completed"
                self.status["prompts"][prompt_name]["completed_at"] = (
                    datetime.now().isoformat()
                )

                started = datetime.fromisoformat(
                    self.status["prompts"][prompt_name]["started_at"]
                )
                completed = datetime.fromisoformat(
                    self.status["prompts"][prompt_name]["completed_at"]
                )
                duration = (completed - started).total_seconds() / 60

                self.status["prompts"][prompt_name]["duration_min"] = round(duration, 1)
                self.status["prompts"][prompt_name]["success"] = proc.returncode == 0
                self.status["prompts"][prompt_name]["outputs"] = [str(output_file)]

                error_msg = None
                if proc.returncode != 0:
                    with open(error_file) as f:
                        error_msg = f.read()[:500]
                        self.status["prompts"][prompt_name]["error"] = error_msg

                self.save_status()

                # Stream prompt completion
                if self.redis_stream:
                    self.redis_stream.publish_prompt_update(
                        prompt_name,
                        "completed" if proc.returncode == 0 else "failed",
                        agent_id=agent_id_str,
                        duration_min=round(duration, 1),
                        error=error_msg,
                    )
                    self.redis_stream.publish_event(
                        "prompt_completed" if proc.returncode == 0 else "prompt_failed",
                        f"{'Completed' if proc.returncode == 0 else 'Failed'} {prompt_name} ({duration:.1f} min)",
                        {"prompt": prompt_name, "agent": agent_id_str, "duration_min": round(duration, 1)},
                    )

                emoji = "✅" if proc.returncode == 0 else "❌"
                print(
                    f"[Agent {agent_id:03d}] {emoji} {prompt_name} ({duration:.1f} min)"
                )

            except Exception as e:
                # Update status to failed
                error_str = str(e)
                self.status["prompts"][prompt_name]["status"] = "failed"
                self.status["prompts"][prompt_name]["error"] = error_str
                self.status["prompts"][prompt_name]["success"] = False
                self.save_status()

                # Stream failure
                if self.redis_stream:
                    self.redis_stream.publish_prompt_update(
                        prompt_name, "failed", error=error_str
                    )
                    self.redis_stream.publish_event(
                        "error",
                        f"Failed {prompt_name}: {error_str}",
                        {"prompt": prompt_name, "error": error_str},
                    )

                print(f"[Agent {agent_id:03d}] ❌ Failed: {prompt_name} - {e}")

    async def run(self):
        """Main execution loop"""
        self.status["status"] = "running"
        self.save_status()

        print(f"\n🚀 Starting execution with {self.max_agents} agents")
        print(f"📊 Total prompts: {len(self.status['prompts'])}")
        print(f"💾 Status file: {self.status_file}")
        print(f"📁 Output dir: {self.output_dir}\n")

        # Stream execution start event
        if self.redis_stream:
            self.redis_stream.publish_event(
                "execution_started",
                f"Execution started with {self.max_agents} agents",
                {"execution_id": self.status["execution_id"], "max_agents": self.max_agents},
            )

        agent_counter = 0
        running_tasks = set()
        heartbeat_counter = 0

        while True:
            # Publish heartbeat every 10 iterations (~10 seconds)
            heartbeat_counter += 1
            if heartbeat_counter % 10 == 0 and self.redis_stream:
                stats = self.get_execution_stats()
                self.redis_stream.publish_heartbeat(self.status["execution_id"], stats)
            # Get prompts ready to execute
            ready = self.get_ready_prompts()

            # Start new tasks up to agent limit
            for prompt in ready:
                if len(running_tasks) < self.max_agents:
                    agent_counter += 1
                    task = asyncio.create_task(self.execute_prompt(prompt, agent_counter))
                    running_tasks.add(task)
                else:
                    break

            # Wait for any task to complete
            if running_tasks:
                done, running_tasks = await asyncio.wait(
                    running_tasks, return_when=asyncio.FIRST_COMPLETED
                )

            # Check if all prompts are done
            all_done = all(
                info["status"] in ["completed", "failed"]
                for info in self.status["prompts"].values()
            )

            if all_done:
                break

            # If no tasks running and none ready, check if we're stuck
            if not running_tasks and not ready:
                # Check if there are still pending prompts
                pending = [
                    name
                    for name, info in self.status["prompts"].items()
                    if info["status"] == "pending"
                ]
                if pending:
                    print(
                        f"\n⚠️  Warning: {len(pending)} prompts pending but dependencies not satisfied"
                    )
                    print("Pending prompts:", pending[:5])
                break

            await asyncio.sleep(1)

        self.status["status"] = "completed"
        self.status["completed_at"] = datetime.now().isoformat()
        self.save_status()

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print execution summary"""
        total = len(self.status["prompts"])
        completed = sum(
            1 for p in self.status["prompts"].values() if p["status"] == "completed"
        )
        failed = sum(
            1 for p in self.status["prompts"].values() if p["status"] == "failed"
        )

        print("\n" + "=" * 80)
        print("EXECUTION SUMMARY")
        print("=" * 80)
        print(f"Execution ID: {self.status['execution_id']}")
        print(f"Total prompts: {total}")
        print(f"✅ Completed: {completed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success rate: {completed/total*100:.1f}%")

        if completed > 0:
            total_time = sum(
                p["duration_min"]
                for p in self.status["prompts"].values()
                if p["duration_min"] is not None
            )
            print(f"⏱️  Total execution time: {total_time:.1f} minutes")

        if failed > 0:
            print("\n❌ Failed prompts:")
            for name, info in self.status["prompts"].items():
                if info["status"] == "failed":
                    error = info.get("error", "Unknown error")[:100]
                    print(f"  - {name}: {error}")

        print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Execute constellation elaboration prompts in parallel"
    )
    parser.add_argument(
        "max_agents",
        type=int,
        nargs="?",
        default=10,
        help="Maximum number of concurrent agents (default: 10)",
    )
    parser.add_argument(
        "--resume", action="store_true", help="Resume from existing status file"
    )
    parser.add_argument(
        "--status",
        default=".kiro/execution-status.json",
        help="Status file path (default: .kiro/execution-status.json)",
    )
    parser.add_argument(
        "--no-streaming",
        action="store_true",
        help="Disable Redis streaming (file-only mode)",
    )
    parser.add_argument(
        "--redis-url",
        default="redis://localhost:6379",
        help="Redis connection URL (default: redis://localhost:6379)",
    )

    args = parser.parse_args()

    orchestrator = ConstellationOrchestrator(
        status_file=args.status,
        max_agents=args.max_agents,
        enable_streaming=not args.no_streaming,
        redis_url=args.redis_url,
    )

    try:
        asyncio.run(orchestrator.run())
    except KeyboardInterrupt:
        print("\n\n⚠️  Execution interrupted by user")
        print(f"💾 Status saved to: {orchestrator.status_file}")
        print("🔄 Resume with: python scripts/constellation_orchestrator.py --resume")
        sys.exit(1)


if __name__ == "__main__":
    main()
