# Parallel Execution & Status Tracking System

## Overview

System for executing 90 prompts in parallel with real-time status tracking, progress monitoring, and dependency management.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Execution Orchestrator                     │
│  - Reads DAG                                                 │
│  - Schedules prompts based on dependencies                   │
│  - Manages agent pool                                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ├─────────────────┬──────────────────┐
                              ▼                 ▼                  ▼
                    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
                    │   Agent Pool    │ │  Status Tracker │ │ Progress Monitor│
                    │  (10-20 agents) │ │   (Redis/JSON)  │ │   (Dashboard)   │
                    └─────────────────┘ └─────────────────┘ └─────────────────┘
                              │                 ▲                  ▲
                              └─────────────────┴──────────────────┘
                                     Status Updates
```

## Components

### 1. Execution Orchestrator
**File:** `scripts/constellation_orchestrator.py`

**Responsibilities:**
- Parse execution DAG
- Schedule prompts when dependencies satisfied
- Manage agent pool
- Handle failures and retries
- Coordinate completion

### 2. Status Tracker
**File:** `scripts/constellation_status.py`

**Responsibilities:**
- Track status of each prompt (pending/running/completed/failed)
- Store outputs and errors
- Provide status query API
- Persist state for resumption

### 3. Progress Monitor
**File:** `scripts/constellation_monitor.py`

**Responsibilities:**
- Real-time dashboard
- Progress visualization
- Estimated time remaining
- Resource utilization

### 4. Agent Pool Manager
**File:** `scripts/constellation_agents.py`

**Responsibilities:**
- Manage concurrent Claude agents
- Queue management
- Load balancing
- Rate limiting

---

## Implementation

### Status Tracking Schema

```json
{
  "execution_id": "constellation-2025-10-04-001",
  "started_at": "2025-10-04T10:00:00Z",
  "status": "running",
  "prompts": {
    "phase-1a-constellation-inventory": {
      "status": "completed",
      "started_at": "2025-10-04T10:00:00Z",
      "completed_at": "2025-10-04T12:30:00Z",
      "duration_min": 150,
      "agent_id": "agent-001",
      "outputs": [
        ".kiro/reports/constellation-inventory-2025.json"
      ],
      "success": true,
      "error": null
    },
    "phase-1b1-stakeholder-extraction": {
      "status": "running",
      "started_at": "2025-10-04T10:00:00Z",
      "completed_at": null,
      "duration_min": null,
      "agent_id": "agent-002",
      "outputs": [],
      "success": null,
      "error": null
    },
    "phase-2-bootstrap-batch1": {
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "duration_min": null,
      "agent_id": null,
      "dependencies": [
        "phase-1a-constellation-inventory",
        "phase-1b2-stakeholder-dimension-analysis",
        "phase-1c2-cms-data-model-extraction",
        "phase-1d5-ontology-consolidation"
      ],
      "dependencies_satisfied": false,
      "outputs": [],
      "success": null,
      "error": null
    }
  },
  "stats": {
    "total_prompts": 90,
    "pending": 75,
    "running": 14,
    "completed": 1,
    "failed": 0,
    "progress_percent": 1.1
  }
}
```

### Execution Orchestrator Implementation

```python
#!/usr/bin/env python3
"""
Constellation Execution Orchestrator

Manages parallel execution of constellation elaboration prompts
with dependency tracking and status monitoring.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set
import networkx as nx

class ConstellationOrchestrator:
    def __init__(
        self,
        dag_file: str,
        status_file: str,
        max_agents: int = 10,
        prompts_dir: str = "prompts/staging"
    ):
        self.dag = self.load_dag(dag_file)
        self.status_file = Path(status_file)
        self.max_agents = max_agents
        self.prompts_dir = Path(prompts_dir)
        self.status = self.init_status()
        self.agent_pool = asyncio.Semaphore(max_agents)

    def load_dag(self, dag_file: str) -> nx.DiGraph:
        """Load execution DAG from file"""
        # Parse Mermaid DAG or JSON DAG
        # For now, hardcode the dependencies
        dag = nx.DiGraph()

        # Phase 1 prompts
        phase1_prompts = [
            "phase-1a-constellation-inventory",
            "phase-1b1-stakeholder-extraction",
            "phase-1b2-stakeholder-dimension-analysis",
            "phase-1b3-stakeholder-journey-mapping",
            "phase-1c1-cms-dependency-scan",
            "phase-1c2-cms-data-model-extraction",
            "phase-1c3-cms-capability-analysis",
            "phase-1d1-ontology-batch1",
            "phase-1d2-ontology-batch2",
            "phase-1d3-ontology-batch3",
            "phase-1d4-ontology-batch4",
            "phase-1d5-ontology-consolidation"
        ]

        for p in phase1_prompts:
            dag.add_node(p, phase=1)

        # Add dependencies
        dag.add_edge("phase-1b1-stakeholder-extraction", "phase-1b2-stakeholder-dimension-analysis")
        dag.add_edge("phase-1b1-stakeholder-extraction", "phase-1b3-stakeholder-journey-mapping")
        dag.add_edge("phase-1c1-cms-dependency-scan", "phase-1c2-cms-data-model-extraction")
        dag.add_edge("phase-1c1-cms-dependency-scan", "phase-1c3-cms-capability-analysis")

        for batch in ["phase-1d1-ontology-batch1", "phase-1d2-ontology-batch2",
                      "phase-1d3-ontology-batch3", "phase-1d4-ontology-batch4"]:
            dag.add_edge(batch, "phase-1d5-ontology-consolidation")

        # Phase 2+ prompts would be added here
        # ...

        return dag

    def init_status(self) -> Dict:
        """Initialize or load execution status"""
        if self.status_file.exists():
            with open(self.status_file) as f:
                return json.load(f)

        status = {
            "execution_id": f"constellation-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "started_at": datetime.now().isoformat(),
            "status": "pending",
            "prompts": {}
        }

        for node in self.dag.nodes():
            status["prompts"][node] = {
                "status": "pending",
                "started_at": None,
                "completed_at": None,
                "duration_min": None,
                "agent_id": None,
                "dependencies": list(self.dag.predecessors(node)),
                "dependencies_satisfied": len(list(self.dag.predecessors(node))) == 0,
                "outputs": [],
                "success": None,
                "error": None
            }

        self.save_status(status)
        return status

    def save_status(self, status: Dict = None):
        """Save current status to file"""
        if status is None:
            status = self.status

        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2)

    def get_ready_prompts(self) -> List[str]:
        """Get prompts ready to execute (dependencies satisfied)"""
        ready = []
        for prompt, info in self.status["prompts"].items():
            if info["status"] == "pending":
                # Check if all dependencies are completed
                deps_satisfied = all(
                    self.status["prompts"][dep]["status"] == "completed"
                    for dep in info["dependencies"]
                )
                if deps_satisfied:
                    ready.append(prompt)
        return ready

    async def execute_prompt(self, prompt_name: str, agent_id: int):
        """Execute a single prompt"""
        async with self.agent_pool:
            try:
                # Update status to running
                self.status["prompts"][prompt_name]["status"] = "running"
                self.status["prompts"][prompt_name]["started_at"] = datetime.now().isoformat()
                self.status["prompts"][prompt_name]["agent_id"] = f"agent-{agent_id:03d}"
                self.save_status()

                # Execute the prompt
                prompt_file = self.prompts_dir / f"{prompt_name}.md"

                print(f"[Agent {agent_id:03d}] Starting: {prompt_name}")

                # Run claude with the prompt
                proc = await asyncio.create_subprocess_exec(
                    "claude",
                    stdin=open(prompt_file),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

                stdout, stderr = await proc.communicate()

                # Update status to completed
                self.status["prompts"][prompt_name]["status"] = "completed"
                self.status["prompts"][prompt_name]["completed_at"] = datetime.now().isoformat()

                started = datetime.fromisoformat(self.status["prompts"][prompt_name]["started_at"])
                completed = datetime.fromisoformat(self.status["prompts"][prompt_name]["completed_at"])
                duration = (completed - started).total_seconds() / 60

                self.status["prompts"][prompt_name]["duration_min"] = round(duration, 1)
                self.status["prompts"][prompt_name]["success"] = proc.returncode == 0

                if proc.returncode != 0:
                    self.status["prompts"][prompt_name]["error"] = stderr.decode()

                self.save_status()

                print(f"[Agent {agent_id:03d}] Completed: {prompt_name} ({duration:.1f} min)")

            except Exception as e:
                # Update status to failed
                self.status["prompts"][prompt_name]["status"] = "failed"
                self.status["prompts"][prompt_name]["error"] = str(e)
                self.status["prompts"][prompt_name]["success"] = False
                self.save_status()

                print(f"[Agent {agent_id:03d}] Failed: {prompt_name} - {e}")

    async def run(self):
        """Main execution loop"""
        self.status["status"] = "running"
        self.save_status()

        agent_counter = 0
        running_tasks = set()

        while True:
            # Get prompts ready to execute
            ready = self.get_ready_prompts()

            # Start new tasks up to agent limit
            for prompt in ready:
                if len(running_tasks) < self.max_agents:
                    agent_counter += 1
                    task = asyncio.create_task(
                        self.execute_prompt(prompt, agent_counter)
                    )
                    running_tasks.add(task)
                else:
                    break

            # Wait for any task to complete
            if running_tasks:
                done, running_tasks = await asyncio.wait(
                    running_tasks,
                    return_when=asyncio.FIRST_COMPLETED
                )

            # Check if all prompts are done
            all_done = all(
                info["status"] in ["completed", "failed"]
                for info in self.status["prompts"].values()
            )

            if all_done:
                break

            # If no tasks running and none ready, we might be stuck
            if not running_tasks and not ready:
                print("Warning: No tasks running and none ready. Checking for circular dependencies...")
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
        completed = sum(1 for p in self.status["prompts"].values() if p["status"] == "completed")
        failed = sum(1 for p in self.status["prompts"].values() if p["status"] == "failed")

        print("\n" + "="*80)
        print("EXECUTION SUMMARY")
        print("="*80)
        print(f"Total prompts: {total}")
        print(f"Completed: {completed}")
        print(f"Failed: {failed}")
        print(f"Success rate: {completed/total*100:.1f}%")

        if failed > 0:
            print("\nFailed prompts:")
            for name, info in self.status["prompts"].items():
                if info["status"] == "failed":
                    print(f"  - {name}: {info['error']}")

if __name__ == "__main__":
    import sys

    max_agents = int(sys.argv[1]) if len(sys.argv) > 1 else 10

    orchestrator = ConstellationOrchestrator(
        dag_file="prompts/staging/constellation-execution-dag-optimized.mmd",
        status_file=".kiro/execution-status.json",
        max_agents=max_agents
    )

    asyncio.run(orchestrator.run())
```

### Progress Monitor Dashboard

```python
#!/usr/bin/env python3
"""
Real-time Progress Monitor for Constellation Execution

Usage: python scripts/constellation_monitor.py
"""

import json
import time
from pathlib import Path
from datetime import datetime, timedelta
import sys

def clear_screen():
    print("\033[2J\033[H", end="")

def format_duration(seconds):
    """Format duration in human-readable format"""
    if seconds is None:
        return "N/A"
    return str(timedelta(seconds=int(seconds)))

def get_status_emoji(status):
    """Get emoji for status"""
    return {
        "pending": "⏳",
        "running": "🔄",
        "completed": "✅",
        "failed": "❌"
    }.get(status, "❓")

def monitor_execution(status_file: str, refresh_interval: int = 2):
    """Monitor execution with live dashboard"""
    status_path = Path(status_file)

    if not status_path.exists():
        print(f"Status file not found: {status_file}")
        print("Start execution first with: python scripts/constellation_orchestrator.py")
        return

    try:
        while True:
            clear_screen()

            with open(status_path) as f:
                status = json.load(f)

            # Header
            print("="*100)
            print("CONSTELLATION ELABORATION - EXECUTION DASHBOARD")
            print("="*100)
            print(f"Execution ID: {status['execution_id']}")
            print(f"Status: {status.get('status', 'unknown').upper()}")
            print(f"Started: {status.get('started_at', 'N/A')}")

            # Calculate stats
            prompts = status["prompts"]
            total = len(prompts)
            pending = sum(1 for p in prompts.values() if p["status"] == "pending")
            running = sum(1 for p in prompts.values() if p["status"] == "running")
            completed = sum(1 for p in prompts.values() if p["status"] == "completed")
            failed = sum(1 for p in prompts.values() if p["status"] == "failed")

            progress = (completed + failed) / total * 100

            # Progress bar
            bar_width = 50
            filled = int(bar_width * progress / 100)
            bar = "█" * filled + "░" * (bar_width - filled)

            print("\n" + "="*100)
            print(f"Progress: [{bar}] {progress:.1f}%")
            print(f"Total: {total} | Pending: {pending} | Running: {running} | Completed: {completed} | Failed: {failed}")
            print("="*100)

            # Currently running prompts
            if running > 0:
                print("\n🔄 CURRENTLY RUNNING:")
                for name, info in prompts.items():
                    if info["status"] == "running":
                        started = datetime.fromisoformat(info["started_at"])
                        elapsed = (datetime.now() - started).total_seconds() / 60
                        print(f"  [{info['agent_id']}] {name} ({elapsed:.1f} min elapsed)")

            # Recently completed
            recently_completed = [
                (name, info) for name, info in prompts.items()
                if info["status"] == "completed" and info["completed_at"]
            ]
            recently_completed.sort(key=lambda x: x[1]["completed_at"], reverse=True)

            if recently_completed:
                print("\n✅ RECENTLY COMPLETED (last 5):")
                for name, info in recently_completed[:5]:
                    print(f"  [{info['agent_id']}] {name} ({info['duration_min']:.1f} min)")

            # Failed prompts
            if failed > 0:
                print("\n❌ FAILED:")
                for name, info in prompts.items():
                    if info["status"] == "failed":
                        error = info.get("error", "Unknown error")[:80]
                        print(f"  {name}: {error}")

            # Next up
            ready = []
            for name, info in prompts.items():
                if info["status"] == "pending":
                    deps_satisfied = all(
                        prompts[dep]["status"] == "completed"
                        for dep in info["dependencies"]
                    )
                    if deps_satisfied:
                        ready.append(name)

            if ready and running < 10:  # Assuming max 10 agents
                print(f"\n⏳ READY TO START (next {min(5, len(ready))}):")
                for name in ready[:5]:
                    print(f"  {name}")

            # ETA calculation
            if completed > 0:
                avg_duration = sum(
                    p["duration_min"] for p in prompts.values()
                    if p["duration_min"] is not None
                ) / completed

                remaining = pending + running
                eta_min = (remaining * avg_duration) / (running if running > 0 else 1)
                eta = datetime.now() + timedelta(minutes=eta_min)

                print(f"\n⏰ ESTIMATED COMPLETION: {eta.strftime('%Y-%m-%d %H:%M:%S')} ({eta_min:.0f} min remaining)")

            print("\n" + "="*100)
            print(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("Press Ctrl+C to exit")

            # Check if execution is complete
            if status.get("status") == "completed":
                print("\n✅ EXECUTION COMPLETE!")
                break

            time.sleep(refresh_interval)

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
        sys.exit(0)

if __name__ == "__main__":
    monitor_execution(".kiro/execution-status.json", refresh_interval=2)
```

### Quick Status Check Script

```bash
#!/bin/bash
# scripts/constellation_status.sh
# Quick status check without live monitoring

STATUS_FILE=".kiro/execution-status.json"

if [ ! -f "$STATUS_FILE" ]; then
    echo "No execution in progress"
    exit 1
fi

echo "=== Constellation Execution Status ==="
echo

# Extract stats using jq
jq -r '
  "Execution ID: \(.execution_id)",
  "Started: \(.started_at)",
  "Status: \(.status)",
  "",
  "Progress:",
  "  Total: \(.prompts | length)",
  "  Pending: \([.prompts[] | select(.status == "pending")] | length)",
  "  Running: \([.prompts[] | select(.status == "running")] | length)",
  "  Completed: \([.prompts[] | select(.status == "completed")] | length)",
  "  Failed: \([.prompts[] | select(.status == "failed")] | length)"
' "$STATUS_FILE"
```

---

## Usage

### 1. Start Execution

```bash
# With 10 agents (default)
python scripts/constellation_orchestrator.py

# With 20 agents
python scripts/constellation_orchestrator.py 20

# With custom settings
python scripts/constellation_orchestrator.py \
  --agents 15 \
  --dag prompts/staging/constellation-execution-dag-optimized.mmd \
  --status .kiro/execution-status.json
```

### 2. Monitor Progress (Real-time Dashboard)

```bash
# In a separate terminal
python scripts/constellation_monitor.py

# With custom refresh rate
python scripts/constellation_monitor.py --refresh 5
```

### 3. Quick Status Check

```bash
./scripts/constellation_status.sh
```

### 4. Resume Failed Execution

```bash
# Automatically resumes from status file
python scripts/constellation_orchestrator.py --resume
```

---

## Alternative: GNU Parallel Approach

For simpler execution without custom orchestration:

```bash
#!/bin/bash
# scripts/execute_constellation_parallel.sh

# Phase 1 - All parallel
parallel -j 14 --bar --joblog logs/phase1.log \
  'claude < {} > logs/{/.}.out 2> logs/{/.}.err' \
  ::: prompts/staging/phase-1*.md

# Wait for Phase 1 to complete
wait

# Phase 2 - Bootstrap (sequential, only 1 batch)
claude < prompts/staging/phase-2-bootstrap-batch1.md

# Phase 2 - Foundation (parallel batches)
parallel -j 10 --bar --joblog logs/phase2-foundation.log \
  'claude < {} > logs/{/.}.out 2> logs/{/.}.err' \
  ::: prompts/staging/phase-2-foundation-batch*.md

# ... continue for other phases
```

**Advantages:**
- Simpler (no custom code)
- Built-in progress bar
- Job logging
- Easy to understand

**Disadvantages:**
- Less flexible dependency management
- No real-time dashboard
- Manual phase coordination

---

## Monitoring Outputs

### 1. Execution Log

```bash
tail -f .kiro/execution-status.json
```

### 2. Individual Prompt Logs

```bash
# See all outputs
ls -lh logs/

# View specific prompt output
cat logs/phase-1a-constellation-inventory.out

# View errors
cat logs/phase-1a-constellation-inventory.err
```

### 3. Progress Tracking

```bash
# Watch completion rate
watch -n 2 'jq ".prompts | map(select(.status == \"completed\")) | length" .kiro/execution-status.json'
```

---

## Error Handling & Recovery

### Automatic Retry

```python
# In orchestrator
async def execute_prompt_with_retry(self, prompt_name: str, agent_id: int, max_retries: int = 3):
    """Execute prompt with automatic retry on failure"""
    for attempt in range(max_retries):
        try:
            await self.execute_prompt(prompt_name, agent_id)
            if self.status["prompts"][prompt_name]["success"]:
                return
            else:
                print(f"Retry {attempt + 1}/{max_retries} for {prompt_name}")
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            print(f"Retry {attempt + 1}/{max_retries} after error: {e}")
            await asyncio.sleep(60)  # Wait before retry
```

### Manual Intervention

```bash
# Mark failed prompt as pending to retry
jq '.prompts["phase-1a-constellation-inventory"].status = "pending"' \
  .kiro/execution-status.json > temp.json && mv temp.json .kiro/execution-status.json

# Resume execution
python scripts/constellation_orchestrator.py --resume
```

---

## Next Steps

1. ✅ Created orchestrator architecture
2. ✅ Created status tracking system
3. ✅ Created monitoring dashboard
4. TODO: Implement full DAG loading
5. TODO: Add rate limiting for API calls
6. TODO: Add cost tracking
7. TODO: Add checkpoint/resume functionality
8. TODO: Build web-based dashboard (optional)
