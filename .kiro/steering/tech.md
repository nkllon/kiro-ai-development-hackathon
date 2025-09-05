# Technology Standards & Architecture Policy

## Core Technology Principles

### Primary Technology Stack
**Language**: Python 3.9+ (systematic choice for AI/ML ecosystem)
**Philosophy**: Systematic over ad-hoc, proven over experimental
**Quality Standard**: >90% test coverage requirement (DR8 compliance)

### Architecture Mandates
**Reflective Module (RM) Pattern**: All modules must implement health monitoring and status interfaces
**Model-Driven Decisions**: Decisions based on project registry consultation  
**Systematic Approach**: No ad-hoc implementations, systematic tool repair
**PDCA Methodology**: Plan-Do-Check-Act cycles for all development tasks

## Quality Standards

### Universal Quality Gates
- **Coverage**: >90% test coverage requirement (DR8 compliance)
- **Testing**: Unit, integration, performance, security tests required
- **Automation**: CI/CD integration with quality gates
- **Analysis**: Automatic RCA on test failures

### Service Integration Standards
- **Health Endpoints**: `/health`, `/ready`, `/metrics` required
- **Observability**: Structured logging with correlation IDs
- **Configuration**: 12-factor app compliance, external secret management
- **Deployment**: Semantic versioning, OpenAPI/gRPC specifications

## Implementation Philosophy

### Systematic Superiority
- **No Ad-Hoc Solutions**: Every implementation follows systematic patterns
- **Model-Driven**: Decisions based on project registry consultation
- **PDCA Methodology**: Plan-Do-Check-Act cycles for all development
- **Physics-Informed**: Increase odds of success, reduce pain and rework