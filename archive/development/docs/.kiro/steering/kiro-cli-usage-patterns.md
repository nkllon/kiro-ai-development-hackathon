# Kiro CLI Usage Patterns - Essential Reference

## Core Principle

**"Always use pipes and tees with Kiro CLI for proper input handling and audit trails."**

The Kiro CLI accepts stdin input with the `-` flag, and we ALWAYS combine this with `tee` for logging and audit purposes.

## The Golden Pattern

```bash
command | tee logfile.log | kiro -
```

This pattern:
- Captures output to a log file for audit trails
- Sends the same content to Kiro for AI processing
- Maintains a record of what was sent to the AI
- Enables reproducible AI interactions

## Essential Usage Patterns

### Basic Content Piping
```bash
# Send file content to Kiro
cat filename.txt | tee input-log.txt | kiro -

# Send command output to Kiro
ps aux | grep python | tee process-list.log | kiro -

# Send echo messages to Kiro
echo "Help me implement this feature" | tee prompt.log | kiro -
```

### Spec and Documentation Workflows
```bash
# Send spec content for implementation help
cat .kiro/specs/feature-name/tasks.md | tee spec-input.log | kiro -

# Send multiple spec files combined
cat .kiro/specs/feature-name/{requirements,design,tasks}.md | tee combined-spec.log | kiro -

# Send status updates and requests
echo "I completed the DAG system. What's next?" | tee status-query.log | kiro -
```

### Code Review and Analysis
```bash
# Send code for review
cat src/module/component.py | tee code-review.log | kiro -

# Send git diff for analysis
git diff HEAD~1 | tee git-changes.log | kiro -

# Send test results for troubleshooting
python -m pytest test_file.py -v 2>&1 | tee test-results.log | kiro -
```

### System Diagnostics and Troubleshooting
```bash
# Send error logs for analysis
python script.py 2>&1 | tee execution-log.txt | kiro -

# Send system status for troubleshooting
make dashboard-status 2>&1 | tee system-status.log | kiro -

# Send health check results
curl -s http://localhost:8888/health | tee health-check.log | kiro -
```

### Advanced Patterns
```bash
# Filter and send specific content
grep -A 5 "Phase 1:" .kiro/specs/feature/tasks.md | tee phase1-tasks.log | kiro -

# Send combined prompt and context
echo "Review this code:" && cat src/file.py | tee code-context.log | kiro -

# Send structured data
jq '.' config.json | tee config-formatted.log | kiro -
```

## Why This Pattern Matters

### Audit Trail Benefits
- **Reproducibility**: Can replay exact inputs to Kiro
- **Debugging**: Know exactly what was sent when issues occur
- **Learning**: Review successful interaction patterns
- **Compliance**: Maintain records of AI assistance requests

### Operational Benefits
- **Safety**: Never lose input due to CLI issues
- **Efficiency**: Reuse logged inputs for similar requests
- **Collaboration**: Share exact inputs with team members
- **Documentation**: Automatic logging of AI interactions

## Anti-Patterns to Avoid

### ❌ WRONG - Direct CLI usage without logging
```bash
kiro chat "help me with this"  # No audit trail
echo "help" | kiro -           # No logging
```

### ❌ WRONG - File redirection without tee
```bash
cat file.txt > temp.txt && kiro temp.txt  # Unnecessary file creation
echo "help" > prompt.txt && kiro prompt.txt  # Extra steps
```

### ✅ RIGHT - Always use pipe + tee + kiro -
```bash
echo "help me with this" | tee prompt.log | kiro -
cat file.txt | tee input.log | kiro -
```

## Log File Organization

### Recommended Log Directory Structure
```
logs/
├── kiro-inputs/
│   ├── YYYY-MM-DD/
│   │   ├── spec-queries/
│   │   ├── code-reviews/
│   │   ├── troubleshooting/
│   │   └── status-updates/
```

### Log File Naming Convention
```bash
# Use descriptive names with timestamps
echo "query" | tee logs/kiro-inputs/$(date +%Y-%m-%d)/query-$(date +%H%M%S).log | kiro -

# Use feature-specific names
cat .kiro/specs/dag-orchestration/tasks.md | tee logs/dag-orchestration-tasks-$(date +%Y%m%d).log | kiro -
```

## Integration with Existing Workflows

### Makefile Integration
```makefile
kiro-help:
	@echo "Send help request to Kiro with logging"
	@echo "What do you need help with?" | tee logs/kiro-help-$(shell date +%Y%m%d-%H%M%S).log | kiro -

kiro-status:
	@echo "Current project status and next steps needed" | tee logs/status-query-$(shell date +%Y%m%d).log | kiro -
```

### Script Integration
```bash
#!/bin/bash
# kiro-assist.sh - Helper script for Kiro interactions

LOGDIR="logs/kiro-inputs/$(date +%Y-%m-%d)"
mkdir -p "$LOGDIR"

if [ "$1" = "file" ]; then
    cat "$2" | tee "$LOGDIR/file-$(basename $2)-$(date +%H%M%S).log" | kiro -
elif [ "$1" = "prompt" ]; then
    echo "$2" | tee "$LOGDIR/prompt-$(date +%H%M%S).log" | kiro -
else
    echo "Usage: $0 {file|prompt} <content>"
fi
```

## Emergency Patterns

### When Kiro CLI is Unresponsive
```bash
# Save input for later processing
echo "urgent help needed" | tee emergency-$(date +%Y%m%d-%H%M%S).log
# Process later: cat emergency-*.log | kiro -
```

### Batch Processing Logged Inputs
```bash
# Reprocess previous inputs
for log in logs/kiro-inputs/2024-01-15/*.log; do
    echo "Reprocessing: $log"
    cat "$log" | kiro -
    sleep 2  # Rate limiting
done
```

## Success Metrics

- **100% of Kiro interactions logged** - Never lose input context
- **Reproducible AI assistance** - Can replay any interaction
- **Audit compliance** - Complete record of AI usage
- **Efficient troubleshooting** - Clear input/output correlation

## Remember

**"If it's not logged with tee, it didn't happen properly."**

Always use the pattern: `command | tee logfile.log | kiro -`

This ensures we maintain proper audit trails, enable reproducible AI interactions, and never lose valuable input context.

---

*Created to preserve essential Kiro CLI usage knowledge for all AI assistants working in this codebase. Never forget the pipe + tee + kiro - pattern!*