# Constellation Orchestration System - Setup & Usage

## Overview

Parallel execution system for 106 constellation elaboration prompts with real-time monitoring and dependency management.

## Components

### 1. Orchestrator (`scripts/constellation_orchestrator.py`)
- Manages parallel execution of prompts
- Handles dependencies between prompts
- Tracks status and progress
- Supports resume on failure

### 2. Monitor Dashboard (`scripts/constellation_monitor.py`)
- Real-time execution dashboard
- Progress visualization
- ETA calculation
- Running/completed/failed tracking

### 3. Status Check (`scripts/constellation_status.sh`)
- Quick status snapshot
- No live updates
- Works with or without `jq`

## Quick Start

### Option 1: Start with 10 Agents (Recommended)

```bash
# Terminal 1: Start orchestrator
python3 scripts/constellation_orchestrator.py 10

# Terminal 2: Monitor progress
python3 scripts/constellation_monitor.py
```

### Option 2: Start with Custom Agent Count

```bash
# With 20 agents (faster but more resource intensive)
python3 scripts/constellation_orchestrator.py 20

# With 5 agents (slower but lighter)
python3 scripts/constellation_orchestrator.py 5
```

### Option 3: Resume Failed Execution

```bash
# Automatically resumes from last state
python3 scripts/constellation_orchestrator.py --resume
```

## Usage Examples

### Start Execution
```bash
cd /Users/lou/kiro-2/kiro-ai-development-hackathon

# Start with 10 concurrent agents
python3 scripts/constellation_orchestrator.py 10
```

**What happens:**
- Creates `.kiro/execution-status.json` tracking file
- Starts Phase 1 prompts in parallel (no dependencies)
- Queues Phase 2+ prompts based on dependencies
- Outputs logs to `.kiro/execution-logs/`

### Monitor Progress (Live Dashboard)
```bash
# In separate terminal
python3 scripts/constellation_monitor.py
```

**Dashboard shows:**
- Overall progress bar
- Currently running prompts with elapsed time
- Recently completed prompts
- Failed prompts with errors
- ETA to completion
- Updates every 2 seconds

### Quick Status Check
```bash
./scripts/constellation_status.sh
```

**Output:**
- Execution ID and start time
- Total/pending/running/completed/failed counts
- Currently running prompts
- Recent completions
- Any failures

## Execution Flow

### Phase 1: Discovery (Parallel - 14 prompts)
All can run simultaneously:
- `phase-1a-constellation-inventory` (150 min)
- `phase-1b1-stakeholder-extraction` (75 min)
- `phase-1b2-stakeholder-dimension-analysis` (105 min) - depends on 1b1
- `phase-1b3-stakeholder-journey-mapping` (105 min) - depends on 1b1
- `phase-1c1-cms-dependency-scan` (83 min)
- `phase-1c2-cms-data-model-extraction` (105 min) - depends on 1c1
- `phase-1c3-cms-capability-analysis` (105 min) - depends on 1c1
- `phase-1d1-ontology-batch1` (105 min)
- `phase-1d2-ontology-batch2` (105 min)
- `phase-1d3-ontology-batch3` (105 min)
- `phase-1d4-ontology-batch4` (105 min)
- `phase-1d5-ontology-consolidation` (75 min) - depends on 1d1-1d4

### Phase 2-4: Sequential by Layer
Each phase waits for previous phase completion.

### Phase 5: Consolidation (Sequential)
Must run in order.

## Status File Format

`.kiro/execution-status.json`:
```json
{
  "execution_id": "constellation-20251004-120000",
  "started_at": "2025-10-04T12:00:00",
  "status": "running",
  "max_agents": 10,
  "prompts": {
    "phase-1a-constellation-inventory": {
      "status": "completed",
      "started_at": "2025-10-04T12:00:00",
      "completed_at": "2025-10-04T14:30:00",
      "duration_min": 150.0,
      "agent_id": "agent-001",
      "dependencies": [],
      "estimated_min": 150,
      "outputs": [".kiro/execution-logs/phase-1a-constellation-inventory.out"],
      "success": true,
      "error": null
    }
  }
}
```

## Output Locations

- **Status file:** `.kiro/execution-status.json`
- **Output logs:** `.kiro/execution-logs/*.out`
- **Error logs:** `.kiro/execution-logs/*.err`
- **Reports:** `.kiro/reports/` (created by prompts)

## Troubleshooting

### Check Status
```bash
# Quick check
./scripts/constellation_status.sh

# Detailed view
cat .kiro/execution-status.json | jq '.prompts | to_entries[] | select(.value.status == "failed")'
```

### Resume After Failure
```bash
# Orchestrator automatically detects existing status and resumes
python3 scripts/constellation_orchestrator.py --resume
```

### View Specific Prompt Output
```bash
# View output
cat .kiro/execution-logs/phase-1a-constellation-inventory.out

# View errors
cat .kiro/execution-logs/phase-1a-constellation-inventory.err
```

### Clear and Restart
```bash
# Backup old execution
mv .kiro/execution-status.json .kiro/execution-status.json.backup

# Start fresh
python3 scripts/constellation_orchestrator.py 10
```

## Performance Tuning

### Agent Count Guidelines
- **5 agents:** ~24 hours for full execution
- **10 agents:** ~12 hours for full execution (recommended)
- **20 agents:** ~6 hours for full execution (resource intensive)

### Resource Requirements
- **Memory:** ~2GB per agent (20GB for 10 agents)
- **CPU:** Modest (mostly I/O bound)
- **Network:** API calls to Claude

## Monitoring Options

### Option 1: Live Dashboard
```bash
python3 scripts/constellation_monitor.py
```
- Real-time updates every 2 seconds
- Full progress visualization
- ETA calculation

### Option 2: Quick Checks
```bash
# Run periodically
watch -n 30 './scripts/constellation_status.sh'
```

### Option 3: Log Tailing
```bash
# Watch status file changes
tail -f .kiro/execution-status.json
```

## Success Criteria

After completion:
- ✅ All 106 prompts status = "completed"
- ✅ All specs have requirements.md, design.md, tasks.md
- ✅ All reports generated in `.kiro/reports/`
- ✅ No failed prompts
- ✅ CMS Architecture updated to v3.0
- ✅ Repository Constellation updated with CMS mapping

## Next Steps After Completion

1. Review completion report: `.kiro/reports/constellation-elaboration-complete.md`
2. Review execution roadmap: `.kiro/reports/constellation-execution-roadmap-final.md`
3. Validate outputs:
   ```bash
   # Should show 108+ for each
   find .kiro/specs -name "requirements.md" | wc -l
   find .kiro/specs -name "design.md" | wc -l
   find .kiro/specs -name "tasks.md" | wc -l
   ```
4. Begin implementation following the roadmap

## Support

- **Orchestrator issues:** Check `.kiro/execution-logs/` for errors
- **Prompt failures:** Review individual prompt error logs
- **Status tracking:** Use `./scripts/constellation_status.sh`
- **Live monitoring:** Use `python3 scripts/constellation_monitor.py`

---

**Ready to execute!** Start with: `python3 scripts/constellation_orchestrator.py 10`
