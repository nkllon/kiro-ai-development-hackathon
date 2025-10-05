# Constellation Orchestration - Quick Reference

## 🚀 Start Execution

```bash
# Start with 10 agents (recommended)
python3 scripts/constellation_orchestrator.py 10

# In separate terminal, start monitor
python3 scripts/constellation_monitor.py
```

## 📊 Check Status

```bash
# Quick status snapshot
./scripts/constellation_status.sh

# Live dashboard
python3 scripts/constellation_monitor.py

# Raw status file
cat .kiro/execution-status.json | jq '.'
```

## 🔄 Resume/Restart

```bash
# Resume after failure/interruption
python3 scripts/constellation_orchestrator.py --resume

# Start fresh (backup old state first)
mv .kiro/execution-status.json .kiro/execution-status.json.backup
python3 scripts/constellation_orchestrator.py 10
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `.kiro/execution-status.json` | Execution state tracking |
| `.kiro/execution-logs/*.out` | Prompt outputs |
| `.kiro/execution-logs/*.err` | Prompt errors |
| `.kiro/reports/` | Generated reports |
| `prompts/staging/*.md` | Prompt definitions |

## 🎯 Current Status

**Completed:** 1/106 prompts (0.9%)
- ✅ phase-1a-constellation-inventory (25.3 min)

**Remaining:** 105 prompts
- Phase 1: 13 prompts (discovery)
- Phase 2: 15 prompts (requirements)
- Phase 3: 15 prompts (design)
- Phase 4: 15 prompts (tasks)
- Phase 5: 19 prompts (consolidation)

## ⏱️ Estimated Timeline

| Agents | Duration |
|--------|----------|
| 5      | ~24 hours |
| 10     | ~12 hours |
| 20     | ~6 hours |

## 🔍 Debugging

```bash
# View failed prompts
cat .kiro/execution-status.json | jq '.prompts | to_entries[] | select(.value.status == "failed")'

# View specific prompt output
cat .kiro/execution-logs/phase-1a-constellation-inventory.out

# View specific prompt errors
cat .kiro/execution-logs/phase-1a-constellation-inventory.err

# Check currently running
cat .kiro/execution-status.json | jq '.prompts | to_entries[] | select(.value.status == "running")'
```

## ✅ Validation After Completion

```bash
# Check all specs have requirements.md (should be 108+)
find .kiro/specs -name "requirements.md" | wc -l

# Check all specs have design.md (should be 108+)
find .kiro/specs -name "design.md" | wc -l

# Check all specs have tasks.md (should be 108+)
find .kiro/specs -name "tasks.md" | wc -l

# Check generated reports
ls -la .kiro/reports/
```

## 📞 Quick Commands

```bash
# Start execution
python3 scripts/constellation_orchestrator.py 10

# Monitor (separate terminal)
python3 scripts/constellation_monitor.py

# Quick status
./scripts/constellation_status.sh

# Resume
python3 scripts/constellation_orchestrator.py --resume
```

---

**See full documentation:** `ORCHESTRATION-SETUP.md`
