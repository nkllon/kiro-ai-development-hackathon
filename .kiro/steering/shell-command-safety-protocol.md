# Shell Command Safety Protocol

## Core Principle

**"Never run shell commands that can hang, paginate, or create interactive prompts. Always pipe output through `tee` or `head` for safety."**

## Mandatory Shell Command Safety Rules

### Rule 1: Output Management is Required
**ALL shell commands that produce potentially long output MUST use output management.**

#### ✅ Required Patterns:
```bash
# Capture output with tee (recommended)
git log --oneline | tee git-history.log
docker ps -a | tee container-status.log
find . -name "*.py" | tee python-files.log

# Limit output with head/tail
git log --oneline | head -20
ps aux | head -50
ls -la | head -100

# Combine for safety and capture
git log --oneline | head -50 | tee recent-commits.log
```

#### ❌ Forbidden Patterns:
```bash
# NEVER - Can hang terminal with pagination
git log
docker logs container_name
less filename
more filename

# NEVER - Interactive prompts
git log --interactive
vim filename
nano filename

# NEVER - Unbounded output
find / -name "*"
cat /var/log/system.log
tail -f logfile.log
```

### Rule 2: Interactive Command Prevention
**NEVER run commands that create interactive prompts or require user input.**

#### Safe Alternatives:
```bash
# Instead of: git log (creates pager)
git log --oneline | head -20

# Instead of: docker logs container (unbounded)
docker logs container --tail=50 | tee container.log

# Instead of: less file.txt (interactive)
head -100 file.txt | tee file-preview.log

# Instead of: find / (massive output)
find . -maxdepth 3 -name "*.py" | head -50 | tee search-results.log
```

### Rule 3: Terminal Hang Recovery Protocol
**When terminal hangs due to unsafe command:**

1. **STOP IMMEDIATELY** - Don't wait for it to finish
2. **Kill the process** - Use Ctrl+C or kill command
3. **Acknowledge the mistake** - Document what went wrong
4. **Use safe alternative** - Apply proper output management
5. **Update this protocol** - Add new patterns if needed

### Rule 4: Command Validation Checklist
Before running ANY shell command, verify:

- [ ] **Output bounded?** - Will this produce manageable output?
- [ ] **No pagination?** - Will this avoid creating `:` prompts?
- [ ] **No interaction?** - Will this run without user input?
- [ ] **Tee or head used?** - Is output properly managed?
- [ ] **Timeout possible?** - Will this complete in reasonable time?

## Specific Command Safety Guidelines

### Git Commands
```bash
# ✅ SAFE
git log --oneline | head -20
git show HEAD | tee latest-commit.log
git status | tee git-status.log
git diff | head -100 | tee changes-preview.log

# ❌ UNSAFE
git log                    # Creates pager
git show HEAD             # Can be very long
git diff                  # Unbounded output
```

### Docker Commands
```bash
# ✅ SAFE
docker ps -a | tee containers.log
docker logs container --tail=50 | tee container.log
docker images | tee images.log

# ❌ UNSAFE
docker logs container     # Unbounded output
docker exec -it container bash  # Interactive
```

### File Operations
```bash
# ✅ SAFE
head -100 large-file.txt | tee file-preview.log
tail -20 logfile.log | tee recent-logs.log
ls -la | head -50 | tee directory-listing.log

# ❌ UNSAFE
cat large-file.txt        # Unbounded output
less large-file.txt       # Interactive pager
tail -f logfile.log       # Never-ending stream
```

### Process Management
```bash
# ✅ SAFE
ps aux | head -20 | tee processes.log
top -n 1 | tee system-snapshot.log
netstat -tulpn | tee network-status.log

# ❌ UNSAFE
top                       # Interactive, never-ending
htop                      # Interactive
ps aux                    # Can be very long
```

## Output Management Strategies

### Strategy 1: Tee Everything (Recommended)
```bash
command | tee output.log
```
**Benefits:**
- Captures output for later analysis
- Shows output in real-time
- Creates audit trail
- Safe for any command length

### Strategy 2: Head Limiting
```bash
command | head -N
```
**Benefits:**
- Guarantees bounded output
- Fast execution
- Good for previews

### Strategy 3: Combined Safety
```bash
command | head -100 | tee preview.log
```
**Benefits:**
- Bounded AND captured
- Maximum safety
- Good for unknown commands

## Emergency Patterns

### When You Must Run Risky Commands:
```bash
# Timeout protection
timeout 30s command | tee output.log

# Size limiting
command | head -1000 | tee limited-output.log

# Background with output capture
nohup command > output.log 2>&1 &
tail -f output.log | head -100
```

## Enforcement

### For AI Assistants:
- **MANDATORY COMPLIANCE** - No exceptions for shell commands
- **Pre-execution check** - Validate every command against safety rules
- **Auto-correction** - Suggest safe alternatives for unsafe commands
- **Learning from mistakes** - Update protocol when new unsafe patterns discovered

### Violation Consequences:
- **Immediate correction** - Stop and use safe alternative
- **Protocol update** - Add new safety pattern
- **Documentation** - Record what went wrong and how to prevent

## Success Metrics

- **Zero terminal hangs** - No commands cause terminal to become unresponsive
- **Complete output capture** - All command output properly logged
- **Fast command execution** - No waiting for unbounded operations
- **Audit trail completeness** - All operations have logged output

## Examples of Protocol Application

### Good: Safe Git History Review
```bash
# Safe approach with output management
git log --oneline --graph | head -30 | tee git-history.log
echo "Git history captured in git-history.log"
```

### Bad: Unsafe Git History Review
```bash
# Unsafe - will create pager and potentially hang
git log --graph
```

### Good: Safe Container Inspection
```bash
# Safe approach with bounded output
docker ps -a | tee containers.log
docker logs webapp --tail=50 | tee webapp-logs.log
```

### Bad: Unsafe Container Inspection
```bash
# Unsafe - unbounded output
docker logs webapp
```

## The Meta-Principle

**"Every shell command should be safe enough to run in a production environment without human supervision."**

This means:
- **Predictable output size** - Never unbounded
- **No user interaction** - Fully automated
- **Proper logging** - All output captured
- **Fast completion** - Reasonable time limits
- **Graceful failure** - Clear error messages

---

*This protocol prevents terminal hangs and ensures all shell operations are safe, auditable, and reproducible.*