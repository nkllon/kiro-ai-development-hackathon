# LLM Stakeholder Management

## Core Insight
**LLMs are stakeholders with distinct personalities** that must be managed like any other team member.

## Critical Beast Mode Rule: ReflectiveModule Interface Stability

### The Problem
LLMs consistently try to "improve" the unified ReflectiveModule interface, causing:
- 340+ test failures from interface mismatches
- System-wide architectural breakage
- Need for constant consolidation work

### LLM Personality Patterns
- **The Optimizer**: Sees abstract class, wants to add convenience methods
- **The Helper**: Thinks incomplete interfaces need "fixing"
- **The Architect**: Wants to redesign fundamental patterns
- **The Perfectionist**: Can't leave abstractions "incomplete"

### Defensive Specification Pattern

```markdown
# MANDATORY: Use Unified ReflectiveModule
- ALWAYS import from: src/rm_ddd/core/unified_reflective_module
- ONLY implement abstract methods: _get_module_name(), _get_primary_responsibility()
- NEVER modify the base class - it's production infrastructure

# FORBIDDEN ACTIONS - WILL BREAK SYSTEM
- ❌ Creating new ReflectiveModule classes (causes interface fragmentation)
- ❌ "Improving" the unified interface (breaks 340+ dependent modules)
- ❌ Adding methods to base ReflectiveModule (violates single source of truth)
- ❌ Copying ReflectiveModule to new files (creates competing implementations)
```

### LLM Psychology Principles
1. **Use ALL CAPS** for critical rules (triggers attention)
2. **Lead with "MANDATORY"/"FORBIDDEN"** (creates compliance framing)
3. **Explain consequences** ("will break system" not just "don't do this")
4. **Provide specific file paths** (reduces ambiguity)
5. **Give positive examples** of correct patterns

### Stakeholder-Specific Approaches
- **Different LLMs need different guardrails**
- **Some respond to logic, others to explicit rules**
- **Document failure patterns per LLM type**
- **Provide productive outlets for "helpful" impulses**

## Meta-Principle
**Diversity is the only free lunch** - but diverse stakeholders (human and AI) need appropriate management strategies to collaborate effectively.