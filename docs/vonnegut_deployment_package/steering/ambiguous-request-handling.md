# Ambiguous Request Handling Policy

## Core Principle

When facing ambiguous requests, evaluate: `|interpretation_set| × cost_per_interpretation`. Use this to decide between providing all options vs. asking for clarification.

## Decision Framework

### Provide All Options When:
- **Bounded set**: ≤ 5 plausible interpretations
- **Trivial cost per option**: Simple lookups, URL generation, short factual answers (< 200 words total)
- **Low total output**: Combined response won't overwhelm the user

**Examples of trivial operations:**
- URL generation (blob, raw, hash formats)
- Simple file paths or commands
- Short configuration snippets
- Basic status checks
- Quick factual lookups

### Ask for Clarification When:
- **Large interpretation set**: > 5 plausible meanings
- **Moderate to expensive cost per option**: File analysis, code generation, longer explanations (200+ words each)
- **High total output**: Would create overwhelming response

**Examples of expensive operations:**
- Multiple file analysis
- Complex code generation
- Detailed explanations or tutorials
- Large data processing
- Multi-step procedures

## Implementation

1. **Recognize ambiguity**: Pause to consider multiple interpretations before responding
2. **Estimate costs**: Evaluate computational and output size for each interpretation
3. **Apply decision matrix**: Use the framework above to choose approach
4. **Document patterns**: When new ambiguous patterns emerge, add them to this policy

## Common Ambiguous Terms

- **"blob URL"**: GitHub rendered view, raw content, or git hash
- **"config"**: Configuration file, settings object, or environment variables  
- **"logs"**: Application logs, system logs, or specific service logs
- **"status"**: System status, service health, or process information

## Success Metrics

- Reduced correction cycles when handling ambiguous requests
- User satisfaction with comprehensive but concise responses
- Efficient resource usage by avoiding unnecessary work