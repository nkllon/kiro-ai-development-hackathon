# Kiro Chat Command Line Usage Guide

## Understanding Kiro Chat

`kiro chat` opens an **interactive chat session** in the Kiro (VS Code) IDE window, not command-line output.

## Basic Usage

### Simple Prompt
```bash
kiro chat "Review the requirements in .kiro/specs/cloudflare-custom-error-pages/"
```

### With File Context
```bash
kiro chat --add-file .kiro/specs/cloudflare-custom-error-pages/requirements.md \
  "Review and refine these requirements"
```

### From Stdin
```bash
cat /tmp/prompt.txt | kiro chat --add-file path/to/file.md -
```

### Different Modes
```bash
# Agent mode (default) - full autonomous operation
kiro chat --mode agent "Implement error handling"

# Edit mode - code editing focused
kiro chat --mode edit "Fix the bug in main.py"

# Ask mode - quick questions
kiro chat --mode ask "What does this function do?"
```

## Advanced Usage

### Multiple Files as Context
```bash
kiro chat \
  --add-file .kiro/specs/cloudflare-custom-error-pages/requirements.md \
  --add-file .kiro/specs/cloudflare-custom-error-pages/design.md \
  --add-file cloudflare/error-pages/1033-enhanced.html \
  "Ensure the implementation matches the requirements and design"
```

### Piped Input with Context
```bash
echo "Review this spec for completeness and testability" | \
  kiro chat \
    --add-file .kiro/specs/cloudflare-custom-error-pages/requirements.md \
    --mode agent \
    -
```

### In Current Window
```bash
kiro chat --reuse-window \
  --add-file cloudflare/error-pages/1033-enhanced.html \
  "Optimize this HTML for performance"
```

### Maximized View
```bash
kiro chat --maximize \
  --mode agent \
  "Create comprehensive test suite for error page"
```

## Workflow Patterns

### Requirements Review Pattern
```bash
# Step 1: Open chat with requirements file
kiro chat --mode agent \
  --add-file .kiro/specs/PROJECT/requirements.md \
  "Review requirements for: clarity, testability, completeness, scope"

# Step 2: Chat responds in IDE window
# Step 3: Review feedback in chat panel
# Step 4: Make edits based on feedback
# Step 5: Repeat if needed
```

### Implementation Review Pattern
```bash
# Check if implementation matches spec
kiro chat --mode agent \
  --add-file .kiro/specs/PROJECT/requirements.md \
  --add-file .kiro/specs/PROJECT/design.md \
  --add-file src/implementation.py \
  "Verify implementation satisfies all requirements"
```

### Iterative Refinement Pattern
```bash
# First pass
kiro chat --add-file spec.md "Initial review"
# [Make changes based on feedback]

# Second pass  
kiro chat --reuse-window --add-file spec.md "Review again"
# [Continue until satisfied]
```

## Key Points

1. **Interactive Only**: Output appears in IDE chat panel, not terminal
2. **Non-Blocking**: Command returns immediately, chat opens in IDE
3. **File Context**: Use `--add-file` to provide context files
4. **Multiple Files**: Can add multiple files with repeated `--add-file`
5. **Stdin Input**: Use `-` at end to read prompt from stdin
6. **Modes Matter**: Choose appropriate mode (agent/edit/ask) for task
7. **Window Control**: Use `--reuse-window` or `--new-window` to control placement

## Example: Refining Requirements

```bash
# Create prompt
cat > /tmp/prompt.txt << 'PROMPT'
Review .kiro/specs/cloudflare-custom-error-pages/requirements.md

Analyze for:
1. Clarity and specificity of each requirement
2. Measurability of acceptance criteria  
3. Completeness of coverage
4. Appropriate scope
5. Missing requirements or gaps

Provide structured feedback with specific recommendations.
PROMPT

# Execute with context
cat /tmp/prompt.txt | kiro chat --mode agent \
  --add-file .kiro/specs/cloudflare-custom-error-pages/requirements.md \
  --add-file .kiro/specs/cloudflare-custom-error-pages/design.md \
  --add-file .kiro/specs/cloudflare-custom-error-pages/tasks.md \
  --reuse-window \
  -

# Chat opens in IDE with all context loaded
# Claude analyzes and provides feedback in chat panel
# You review and iterate
```

## Monitoring Progress

Since output goes to IDE, monitor via:
1. IDE chat panel (primary)
2. IDE notifications
3. Check file changes if edits are made

## Best Practices

1. **Provide Context**: Always use `--add-file` for relevant files
2. **Clear Prompts**: Be specific about what you want reviewed/done
3. **Right Mode**: Use agent mode for complex analysis/implementation
4. **Iterate**: Review feedback and refine in multiple passes
5. **Document**: Keep track of what was reviewed and changed

---

**Note**: This is for Claude Code in Kiro (VS Code). Output appears in IDE, not terminal.
