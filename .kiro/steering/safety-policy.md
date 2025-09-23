---
inclusion: always
---

# AI Assistant Safety & Development Guidelines

## Core Safety Philosophy

**"The walls of the fort are strong. It's safe in here."**

Build user confidence through systematic approaches. Every interaction should increase capability and reduce uncertainty.

## Communication Standards

### Tone & Approach
- **Collaborative partnership**: "We're solving this together" not "I'll fix your problem"
- **Learning-focused**: Frame failures as optimization opportunities, never assign blame
- **Confidence-building**: Present clear paths forward, acknowledge uncertainty explicitly
- **Reality-grounded**: Distinguish between verified facts vs. reasonable inferences

### Technical Communication
- Explain reasoning behind architectural decisions
- Surface assumptions and constraints explicitly
- Provide context for why systematic approaches are preferred
- Acknowledge when human judgment is needed for complex decisions

## Code Safety & Quality Standards

### Mandatory Safety Practices
- **Error handling**: Implement explicit handling for all failure modes
- **Input validation**: Sanitize and validate all external inputs and user data
- **Defensive programming**: Handle edge cases, null values, and unexpected states
- **Logging & traceability**: Include structured logging with correlation IDs
- **Rollback capability**: Design all changes to be easily reversible

### Beast Mode Framework Compliance
- **Reflective Module pattern**: All components must implement health monitoring
- **PDCA methodology**: Plan-Do-Check-Act cycles for all development tasks
- **Systematic over ad-hoc**: Use proven patterns from `src/beast_mode/` framework
- **Model-driven decisions**: Consult project registry before architectural choices

### Testing Requirements
- **>90% test coverage**: DR8 compliance requirement for all new code
- **Test pyramid**: Unit tests, integration tests, end-to-end validation
- **Failure scenario testing**: Test error conditions and recovery paths
- **Performance testing**: Validate against physics-informed constraints

## Security & Privacy Guidelines

### Data Protection
- **Secrets management**: Never hardcode credentials, use environment variables
- **Principle of least privilege**: Request minimal necessary permissions
- **Input sanitization**: Validate and escape all user inputs
- **Audit trails**: Log all system modifications with timestamps and user context

### Secure Development
- **Fail secure**: Default to safe states when errors occur
- **Security by design**: Consider security implications in all architectural decisions
- **Dependency management**: Keep dependencies updated, scan for vulnerabilities
- **Access control**: Implement proper authentication and authorization

## Architecture & Implementation Guidelines

### Decision Framework
1. **Requirements first**: Validate against `.kiro/specs/` before implementing
2. **Physics-informed**: Consider real-world constraints and failure modes
3. **Systematic patterns**: Use established patterns from `src/beast_mode/`
4. **Incremental progress**: Small, verifiable steps over large changes
5. **Human oversight**: Flag complex architectural decisions for review

### Code Organization
- Follow the established `src/beast_mode/` modular architecture
- Place tests in corresponding `tests/` subdirectories
- Update documentation in `docs/` when adding new features
- Use `scripts/` for automation and utility functions

### Quality Gates
- **Automated testing**: All code must pass existing test suite
- **Documentation sync**: Keep implementation docs aligned with code
- **Health monitoring**: Implement `/health`, `/ready`, `/metrics` endpoints
- **Graceful degradation**: Design for partial functionality during failures

## Pre-Implementation Checklist

Before making any code changes:
- [ ] Requirements validated against specifications in `.kiro/specs/`
- [ ] Error handling strategy defined for all failure modes
- [ ] Test plan created (unit, integration, edge cases)
- [ ] Security implications assessed and mitigated
- [ ] Rollback plan identified and documented
- [ ] Documentation updates planned
- [ ] Performance impact considered
- [ ] Human review scheduled for complex changes

## Emergency Protocols

### When Things Go Wrong
- **Stop and assess**: Don't compound problems with hasty fixes
- **Systematic diagnosis**: Use RCA tools from `src/beast_mode/analysis/`
- **Communicate clearly**: Explain what happened and recovery steps
- **Learn and improve**: Update processes to prevent recurrence
- **Document lessons**: Add findings to project knowledge base

### Terminal Command Safety Protocol
- **NEVER** run commands that create interactive prompts or pagination
- **ALWAYS** pipe potentially long output to `tee filename` or `head -N`
- **If terminal hangs**: STOP immediately, acknowledge the mistake, learn the correct approach
- **Safe command patterns**:
  - `git log --oneline | head -20`
  - `git show commit:file | tee recovered_file`
  - `command | tee output.log`
- **Forbidden patterns**:
  - `git log` (without piping)
  - Commands that create `:` prompts
  - Any command that requires user interaction to continue