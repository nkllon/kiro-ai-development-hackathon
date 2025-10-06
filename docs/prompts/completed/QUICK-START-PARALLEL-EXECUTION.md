# Quick Start: Parallel Execution with Status Tracking

## System Overview

Execute all 90 constellation elaboration prompts in parallel with real-time progress monitoring and automatic dependency management.

## Prerequisites

```bash
# Ensure Python 3.9+ installed
python3 --version

# Ensure Claude CLI installed and configured
claude --version
```

## Quick Start (3 Steps)

### 1. Start Execution (Terminal 1)

```bash
# With 10 agents (recommended)
python scripts/constellation_orchestrator.py 10

# Or with 20 agents for faster execution
python scripts/constellation_orchestrator.py 20
```

**What happens:**
- Orchestrator loads the execution DAG
- Starts executing Phase 1 prompts in parallel (up to 10/20 concurrent)
- Tracks status in `.kiro/execution-status.json`
- Logs outputs to `.kiro/execution-logs/`

### 2. Monitor Progress (Terminal 2)

```bash
# Start live dashboard
python scripts/constellation_monitor.py

# Or with slower refresh (less CPU)
python scripts/constellation_monitor.py --refresh 5
```

**What you'll see:**
```
================================================================================
CONSTELLATION ELABORATION - EXECUTION DASHBOARD
================================================================================
🆔 Execution ID: constellation-20251004-100000
📊 Status: RUNNING | Agents: 10
🕐 Started: 2025-10-04T10:00:00

================================================================================
Progress: [████████████░░░░░░░░░░░░░░░░░░░░░░░░░░] 25.5%
Total: 90 | ⏳ Pending: 60 | 🔄 Running: 10 | ✅ Completed: 23 | ❌ Failed: 0
================================================================================

🔄 CURRENTLY RUNNING:
  [agent-005] phase-1b2-stakeholder-dimension-analysis [████░░░░░░░░] 45/105 min
  [agent-007] phase-1c2-cms-data-model-extraction     [██████░░░░░░] 63/105 min
  ...

✅ RECENTLY COMPLETED (last 5):
  [agent-001] phase-1a-constellation-inventory        150.2 min ≈
  [agent-002] phase-1b1-stakeholder-extraction        72.5 min
  ...

⏰ ESTIMATED COMPLETION: 2025-10-04 14:23:15 (180 min remaining)
```

### 3. Wait for Completion

Execution runs automatically. No further action needed!

**When complete:**
- Final summary printed to Terminal 1
- All outputs saved in `.kiro/execution-logs/`
- Status file shows complete execution history

---

## Features

### ✅ Automatic Dependency Management

Prompts automatically start when their dependencies complete:
```
phase-1b1-stakeholder-extraction (completes)
  ↓ (dependency satisfied)
phase-1b2-stakeholder-dimension-analysis (starts automatically)
```

### ✅ Real-Time Progress Tracking

Monitor shows:
- Overall progress bar
- Running tasks with elapsed time
- Recently completed tasks
- Failed tasks with errors
- Estimated completion time
- Phase-by-phase progress

### ✅ Resumable Execution

If interrupted (Ctrl+C or crash):
```bash
# Status is automatically saved
# Resume by running orchestrator again
python scripts/constellation_orchestrator.py --resume
```

### ✅ Parallel Execution

- Phase 1: Up to 14 prompts run concurrently
- Phases 2-4: Up to 10-12 batches run concurrently per layer
- Phase 5: Up to 6-7 prompts run concurrently

### ✅ Error Handling

- Failed prompts logged with full error details
- Other prompts continue execution
- Can retry failed prompts manually

---

## Usage Examples

### Standard Execution (10 agents)

```bash
# Terminal 1: Start execution
python scripts/constellation_orchestrator.py 10

# Terminal 2: Monitor progress
python scripts/constellation_monitor.py
```

**Timeline:** 2.5-3 days
**Cost:** ~$75-115

---

### Fast Execution (20 agents)

```bash
# Terminal 1: Start with 20 agents
python scripts/constellation_orchestrator.py 20

# Terminal 2: Monitor progress
python scripts/constellation_monitor.py
```

**Timeline:** 1.5-2 days
**Cost:** ~$75-115 (same - parallelization doesn't increase token usage)

---

### Background Execution

```bash
# Start in background
nohup python scripts/constellation_orchestrator.py 10 > orchestrator.log 2>&1 &

# Monitor in foreground
python scripts/constellation_monitor.py

# Or check status anytime
cat .kiro/execution-status.json | jq '.stats'
```

---

## Status File Format

`.kiro/execution-status.json`:
```json
{
  "execution_id": "constellation-20251004-100000",
  "started_at": "2025-10-04T10:00:00Z",
  "status": "running",
  "max_agents": 10,
  "prompts": {
    "phase-1a-constellation-inventory": {
      "status": "completed",
      "started_at": "2025-10-04T10:00:00Z",
      "completed_at": "2025-10-04T12:30:00Z",
      "duration_min": 150.2,
      "agent_id": "agent-001",
      "estimated_min": 150,
      "dependencies": [],
      "outputs": [".kiro/execution-logs/phase-1a-constellation-inventory.out"],
      "success": true,
      "error": null
    }
  }
}
```

---

## Output Files

All outputs saved to `.kiro/execution-logs/`:

```bash
.kiro/execution-logs/
├── phase-1a-constellation-inventory.out    # Claude's output
├── phase-1a-constellation-inventory.err    # Any errors
├── phase-1b1-stakeholder-extraction.out
├── phase-1b1-stakeholder-extraction.err
└── ...
```

---

## Troubleshooting

### Problem: "Status file not found"

**Solution:** Start orchestrator first:
```bash
python scripts/constellation_orchestrator.py 10
```

---

### Problem: Execution stuck (no tasks running, some pending)

**Cause:** Circular dependency or missing prompt file

**Solution:**
```bash
# Check which prompts are pending
cat .kiro/execution-status.json | jq '.prompts | to_entries[] | select(.value.status == "pending") | .key'

# Check their dependencies
cat .kiro/execution-status.json | jq '.prompts["phase-1d5-ontology-consolidation"].dependencies'

# Verify all dependency prompts completed
cat .kiro/execution-status.json | jq '.prompts["phase-1d1-ontology-batch1"].status'
```

---

### Problem: Failed prompt

**View error:**
```bash
# From status file
cat .kiro/execution-status.json | jq '.prompts["failed-prompt-name"].error'

# From error log
cat .kiro/execution-logs/failed-prompt-name.err
```

**Retry manually:**
```bash
# Mark as pending in status file
jq '.prompts["failed-prompt-name"].status = "pending"' .kiro/execution-status.json > tmp.json
mv tmp.json .kiro/execution-status.json

# Resume execution
python scripts/constellation_orchestrator.py --resume
```

---

### Problem: Want to pause execution

**Solution:**
```bash
# Press Ctrl+C in orchestrator terminal
# Status is automatically saved
# Resume later with:
python scripts/constellation_orchestrator.py --resume
```

---

## Advanced Usage

### Check Status Without Monitor

```bash
# Quick status
cat .kiro/execution-status.json | jq -r '
  "Total: \(.prompts | length)",
  "Completed: \([.prompts[] | select(.status == "completed")] | length)",
  "Running: \([.prompts[] | select(.status == "running")] | length)",
  "Failed: \([.prompts[] | select(.status == "failed")] | length)"
'
```

### Find Slowest Prompts

```bash
cat .kiro/execution-status.json | jq -r '
  .prompts | to_entries[] |
  select(.value.duration_min != null) |
  "\(.value.duration_min) min - \(.key)"
' | sort -rn | head -10
```

### Calculate Total Time Saved

```bash
# Sequential time (sum all durations)
cat .kiro/execution-status.json | jq '
  [.prompts[] | select(.duration_min != null) | .duration_min] | add
'

# Parallel time (started_at to completed_at)
# Shows time saved via parallelization
```

---

## Performance Tips

### Optimize for Speed

1. **Use 20 agents** for maximum parallelization
2. **Run on fast machine** with good network
3. **Minimize other CPU usage** during execution
4. **Use faster refresh** for monitor (10s instead of 2s)

### Optimize for Stability

1. **Use 10 agents** for reliable execution
2. **Run monitor in separate terminal** to avoid output mixing
3. **Save orchestrator logs** with nohup
4. **Regular status backups:**
   ```bash
   watch -n 300 'cp .kiro/execution-status.json .kiro/execution-status.backup.json'
   ```

---

## What Happens During Execution

### Phase 1 (Day 1 Morning, 2.5-3.5 hrs)
- All 14 Phase 1 prompts start in parallel
- Dependencies cascade (1b1→1b2, 1c1→1c2, etc.)
- Consolidation prompts wait for batches

### Phase 2-4 (Days 1-4, layer by layer)
- Bootstrap batch starts when Phase 1 complete
- Foundation batches start when Bootstrap complete
- Intelligence batches start when Foundation complete
- Application batches start when Intelligence complete
- Within each layer, batches run in parallel

### Phase 5 (Days 4-5, 8-10 hrs)
- CMS capability consolidations run in parallel (6 concurrent)
- Merge consolidation after capabilities complete
- CMS Architecture updates (sequential)
- Constellation mapping
- Final validation (3 parallel + roadmap)

---

## Success Indicators

✅ **Monitor shows smooth progression** of completed tasks
✅ **No failed prompts** (or minimal failures with clear errors)
✅ **ETA reasonable** and updating as tasks complete
✅ **Running tasks match agent count** (10 or 20)
✅ **All dependencies satisfied** before prompt starts

---

## After Execution

### 1. Review Summary

```bash
# View full summary
cat .kiro/execution-status.json | jq .

# Or just stats
python -c "
import json
with open('.kiro/execution-status.json') as f:
    status = json.load(f)
    total = len(status['prompts'])
    completed = sum(1 for p in status['prompts'].values() if p['status'] == 'completed')
    print(f'Completed: {completed}/{total} ({completed/total*100:.1f}%)')
"
```

### 2. Check Outputs

```bash
# All spec requirements.md files should be updated
find .kiro/specs -name "requirements.md" -newer .kiro/execution-status.json

# View consolidated reports
ls -lh .kiro/reports/
```

### 3. Validate Results

```bash
# Check all Phase 1 reports exist
ls .kiro/reports/constellation-inventory-2025.json
ls .kiro/reports/stakeholder-*.md
ls .kiro/reports/cms-*.yaml
ls .kiro/reports/dimension-coverage-*.md
```

---

## Next Steps After Completion

1. ✅ Review final execution summary
2. ✅ Validate all 108 specs have updated requirements.md
3. ✅ Review consolidated CMS requirements
4. ✅ Review stakeholder validation report
5. ✅ Begin implementation following execution roadmap

---

**Ready to start?**

```bash
# Terminal 1
python scripts/constellation_orchestrator.py 10

# Terminal 2
python scripts/constellation_monitor.py
```

🚀 Happy executing!
