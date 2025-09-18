---
inclusion: always
---

# Physics-Informed Architecture Principles

## Core Principle

All systems operate within physical reality. Design for constraints, not ideals. Navigate ambiguity systematically or fail.

## Universal Constraints

### Mathematical Reality
- **Graph theory governs dependencies**: Circular dependencies violate mathematical law
- **DAG compliance is mandatory**: Requirements must form Directed Acyclic Graphs
- **Topological ordering exists**: Valid implementation sequences are mathematically guaranteed
- **Cycle detection is O(V+E)**: Computational complexity has mathematical bounds
- **Partial orders are transitive**: Dependency relationships must be mathematically consistent

### Physical Reality
- **Networks are stochastic with anomalies**: Latency follows probability distributions with variance, jitter, and anomalous deviations from known patterns
- **Memory is finite**: Every cache has limits, design accordingly
- **CPUs have thermal limits**: Performance has physical bounds
- **Entropy always wins**: Systems decay without active maintenance
- **Conservation laws**: Energy, information, attention, time are finite resources

### Human Constraints
- **Cognitive load matters**: Complexity has mental overhead
- **Context switching costs**: Human brains aren't CPUs
- **Communication overhead is O(n²)**: Team size has physical limits
- **Attention is scarce**: Design for limited working memory

## Systematic Navigation of Ambiguity

### Mathematical Governance Principles
- **DAG compliance is non-negotiable**: Circular dependencies indicate unsolvable requirements
- **Traceability graphs must be acyclic**: Mathematical proof of implementability
- **Cycle detection prevents design failure**: Early mathematical validation saves exponential cost
- **Topological sorting provides implementation order**: Mathematical guarantee of valid sequence
- **Graph theory validates system architecture**: Objective mathematical foundation for design decisions

### Design Principles
- **Requirements as anchors**: Define what you can verify mathematically
- **Assume failure**: Everything breaks eventually, plan for it systematically
- **Measure everything**: You can't manage what you don't measure objectively
- **Design for operations**: Someone has to run this system within physical constraints
- **Plan for scale**: Physics doesn't care about growth projections

### Decision Framework
- **Mathematical validation first**: Graph theory validates before implementation
- **Increase odds, don't guarantee outcomes**: Physics is probabilistic, math is deterministic
- **Systematic beats ad-hoc**: Proven mathematical approaches reduce risk
- **Requirements ARE solutions**: Clear specifications with DAG compliance prevent rework
- **Reality always wins**: Test assumptions against mathematical and physical behavior
- **PDCA cycles**: Plan-Do-Check-Act against mathematical and physical reality

## The Chaos-Order-Failure Triangle

### Fundamental Reality
- **Order**: Your systematic design and planning
- **Chaos**: Reality hitting your system unexpectedly
- **Failure**: Inevitable breakdown when chaos finds weak spots
- **Evolution**: Learning from failure to build stronger systems

### Implementation Guidelines
- **Stress test everything**: Find failure modes before production does
- **Design for graceful degradation**: When (not if) components fail
- **Build feedback loops**: Learn from every failure systematically
- **Embrace antifragility**: Use chaos as evolutionary pressure
- **Accept the universe**: This is expected behavior, not exceptional

## Code Architecture Implications

### Requirements Architecture (Mathematical Foundation)
- **Enforce DAG compliance**: All requirement dependencies must be acyclic
- **Implement cycle detection**: Prevent mathematically impossible requirements
- **Provide decomposition guidance**: When cycles detected, suggest merge or decompose
- **Maintain traceability matrices**: Mathematical proof of requirement coverage
- **Validate topological ordering**: Ensure implementable requirement sequences

### System Design (Physical Constraints)
- Implement circuit breakers and timeouts for all external calls
- Design APIs with rate limiting and backpressure mechanisms
- Use bulkhead patterns to isolate failure domains
- Implement health checks and observability from day one
- Plan for horizontal scaling constraints

### Error Handling (Systematic Failure Management)
- Fail fast and fail safe - don't hide errors
- Implement exponential backoff with jitter
- Log structured data with correlation IDs
- Design for partial system functionality during failures
- Test failure scenarios as part of normal development

### Performance Considerations (Physics-Informed Optimization)
- Profile early and often - measure don't guess
- Design for the 99th percentile, not the average case
- Implement caching with explicit invalidation strategies
- Consider memory allocation patterns in hot paths
- Plan for garbage collection pauses and mitigation

## AI Assistant Guidelines

When working in this codebase:

1. **Enforce mathematical constraints first** - validate DAG compliance before implementation
2. **Always consider physical constraints** when suggesting solutions
3. **Design for failure scenarios** - ask "what happens when this breaks?"
4. **Prefer systematic approaches** over ad-hoc solutions
5. **Validate assumptions** against mathematical and measurable reality
6. **Acknowledge uncertainty** - be explicit about what you don't know
7. **Focus on requirements** as the mathematically-validated foundation for all decisions
8. **Consider operational complexity** - who maintains this system within physical constraints?
9. **Plan for evolution** - systems must adapt or die within mathematical and physical laws

### Requirements Engineering Mandates
- **Reject circular dependencies immediately** - they violate mathematical law
- **Provide decomposition guidance** when cycles are detected
- **Maintain traceability as mathematical proof** of system validity
- **Use graph theory to validate architecture** before implementation
- **Treat DAG compliance as a quality gate** - non-negotiable mathematical requirement