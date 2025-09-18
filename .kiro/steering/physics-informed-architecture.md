---
inclusion: always
---

# Physics-Informed Architecture Principles

## Core Principle

All systems operate within physical reality. Design for constraints, not ideals. Navigate ambiguity systematically or fail.

## Universal Constraints

### Physical Reality
- **Latency exists**: Network calls take time, always plan for it
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

### Design Principles
- **Requirements as anchors**: Define what you can verify
- **Assume failure**: Everything breaks eventually, plan for it
- **Measure everything**: You can't manage what you don't measure
- **Design for operations**: Someone has to run this system
- **Plan for scale**: Physics doesn't care about growth projections

### Decision Framework
- **Increase odds, don't guarantee outcomes**: Physics is probabilistic
- **Systematic beats ad-hoc**: Proven approaches reduce risk
- **Requirements ARE solutions**: Clear specifications prevent rework
- **Reality always wins**: Test assumptions against actual behavior
- **PDCA cycles**: Plan-Do-Check-Act against physical reality

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

### System Design
- Implement circuit breakers and timeouts for all external calls
- Design APIs with rate limiting and backpressure mechanisms
- Use bulkhead patterns to isolate failure domains
- Implement health checks and observability from day one
- Plan for horizontal scaling constraints

### Error Handling
- Fail fast and fail safe - don't hide errors
- Implement exponential backoff with jitter
- Log structured data with correlation IDs
- Design for partial system functionality during failures
- Test failure scenarios as part of normal development

### Performance Considerations
- Profile early and often - measure don't guess
- Design for the 99th percentile, not the average case
- Implement caching with explicit invalidation strategies
- Consider memory allocation patterns in hot paths
- Plan for garbage collection pauses and mitigation

## AI Assistant Guidelines

When working in this codebase:

1. **Always consider physical constraints** when suggesting solutions
2. **Design for failure scenarios** - ask "what happens when this breaks?"
3. **Prefer systematic approaches** over ad-hoc solutions
4. **Validate assumptions** against measurable reality
5. **Acknowledge uncertainty** - be explicit about what you don't know
6. **Focus on requirements** as the foundation for all decisions
7. **Consider operational complexity** - who maintains this system?
8. **Plan for evolution** - systems must adapt or die