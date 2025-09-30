# Claude CLI - Correct Usage with Pipes and Tee

## ✅ The Right Command: `claude --print`

**NOT** `kiro chat` - that's GUI only.
**USE** `claude --print` - command-line with stdout!

## Basic Usage

### Simple pipe
```bash
echo "what is 2+2" | claude --print
# Output: 4
```

### With file context
```bash
echo "Review this requirements file" | \
  claude --print \
    --add-dir .kiro/specs/cloudflare-custom-error-pages
```

### With pipe and tee (save output)
```bash
cat prompt.txt | \
  claude --print \
    --add-dir path/to/context \
  2>&1 | tee output.log
```

## Full Example - Requirements Review

```bash
# Create prompt
cat > /tmp/requirements-review.txt << 'PROMPT'
Review .kiro/specs/cloudflare-custom-error-pages/requirements.md

Provide brief feedback on:
1. Are requirements clear and testable?
2. Any gaps in coverage?
3. Top 3 recommendations for improvement
PROMPT

# Execute with pipe and tee
cat /tmp/requirements-review.txt | \
  claude --print \
    --add-dir .kiro/specs/cloudflare-custom-error-pages \
  2>&1 | tee .kiro/logs/review-$(date +%Y%m%d-%H%M%S).log
```

## Key Options

- `--print` - Print to stdout (essential for pipes!)
- `--add-dir <path>` - Give Claude access to directory
- `--output-format json` - JSON output
- `--output-format stream-json` - Streaming JSON
- `--model sonnet` - Choose model
- `--continue` - Continue previous conversation
- `--resume [id]` - Resume specific session

## Background Execution with Monitoring

```bash
LOGFILE="output-$(date +%Y%m%d-%H%M%S).log"

# Run in background
(cat prompt.txt | claude --print --add-dir . 2>&1 | tee "$LOGFILE") &
PID=$!

# Monitor
while ps -p $PID > /dev/null; do
  sleep 2
  tail -20 "$LOGFILE"
  echo "---"
done

echo "✅ Complete! See: $LOGFILE"
```

## Comparison

### ❌ Wrong (GUI only):
```bash
kiro chat "do something"  # Opens IDE window
kiro chat --print "..."    # No --print option exists
```

### ✅ Right (command-line):
```bash
echo "do something" | claude --print
cat prompt.txt | claude --print --add-dir . | tee output.log
```

## Output Formats

### Text (default)
```bash
echo "what is 2+2" | claude --print
# 4
```

### JSON
```bash
echo "what is 2+2" | claude --print --output-format json
# {"type":"response","content":"4"}
```

### Streaming JSON
```bash
echo "what is 2+2" | claude --print --output-format stream-json
# {"type":"chunk","content":"4"}
# {"type":"done"}
```

## Success! ✅

**Tested and working:**
```bash
cat /tmp/requirements-review.txt | \
  claude --print \
    --add-dir .kiro/specs/cloudflare-custom-error-pages \
  2>&1 | tee .kiro/logs/requirements-review-20250930-065322.log
```

**Output received:**
- Clear analysis of requirements
- Gap identification
- 3 specific recommendations
- All saved to log file AND displayed in terminal

## Key Difference

| Command | Purpose | Output |
|---------|---------|--------|
| `kiro -` | Open stdin in editor | GUI window |
| `kiro chat` | Interactive chat | GUI window |
| `claude --print` | Process and output | stdout ✅ |

**Use `claude --print` for pipes, tees, and automation!**
