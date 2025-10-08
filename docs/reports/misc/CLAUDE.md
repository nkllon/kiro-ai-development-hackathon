# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Build, Test, and Quality Assurance
```bash
# Run all tests
python -m pytest tests/ -v --tb=short
make dev-test

# Run specific test types
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v
python -m pytest tests/ -k "test_pattern"
python -m pytest tests/ -m slow  # Run slow tests
python -m pytest tests/ -m "not slow"  # Skip slow tests

# Linting and formatting
python -m flake8 src/ --max-line-length=120
python -m mypy src/ --ignore-missing-imports
python -m black src/ --line-length=88
python -m isort src/

# Combined quality checks
make dev-lint
make dev-format

# Coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Beast Mode Framework Commands
```bash
# Show comprehensive help and available commands
make help

# System status and health checks
make observatory-status
make observatory-health
make infra-status
make infra-health

# DAG orchestration
make dag-validate
make dag-execute
make dag-monitor
make dag-status

# Beast Mode operations
make beast-test
make beast-compliance
make beast-validate-all

# Observatory operations
make observatory-deploy
make observatory-start
make observatory-stop
make observatory-logs
```

### Installation and Setup
```bash
# Install dependencies
pip install -r requirements.txt
make install

# Install package in editable mode
pip install -e .
```

## Architecture Overview

### Core Structure
This is an AI-Powered Spec-Driven Development Framework called "Beast Mode Framework" built for the Kiro AI Development Hackathon. It demonstrates systematic development excellence through integration with AI-assisted project management.

**Primary Source Structure:**
- `src/beast_mode/` - Main framework implementation
  - `analysis/` - Root Cause Analysis (RCA) and safety analysis
  - `api/` - REST API endpoints
  - `assessment/` - Production readiness and compliance validation
  - `autonomous/` - PDCA orchestration and autonomous agents
  - `backlog/` - Task and dependency management
  - `cli/` - Command-line interface
  - `compliance/` - Git analysis and compliance checking
  - `mcp_integrations/` - Model Context Protocol integrations (Google Calendar, etc.)
  - `observatory/` - Observatory system for monitoring and WebSocket management
  - `rmddd/` - RM-DDD framework core

**Configuration and Specifications:**
- `.kiro/` - Framework specifications and configuration (100+ feature specs)
  - `.kiro/specs/` - Individual feature specifications with requirements, design, and tasks
  - `.kiro/steering/` - Production steering files (framework usage patterns)
  - `.kiro/steering-dev/` - Development steering files (framework development patterns)
  - `.kiro/settings/` - MCP and other service configurations including steering-config.json

**Docker Services:**
- `docker/google-workspace-mcp/` - Google Workspace integration

**Testing:**
- `tests/unit/` - Unit tests
- `tests/integration/` - Integration tests
- Use pytest markers: `@pytest.mark.slow`, `@pytest.mark.integration`, `@pytest.mark.unit`

### Key Architectural Patterns

**Reflective Module (RM) Architecture:** The framework follows RM principles where components are decomposed into focused, single-responsibility modules rather than monolithic specifications. All modules should implement the ReflectiveModule pattern.

**PDCA-Driven Development:** Plan-Do-Check-Act cycles are fundamental to the framework's operation, with systematic orchestration and metrics collection.

**Spec-Driven Development:** Features are defined through comprehensive specifications in `.kiro/specs/` with requirements, design documents, and task breakdowns. Each spec typically contains:
- `requirements.md` - Feature requirements
- `design.md` - Design documentation
- `tasks.md` - Task breakdown

**MCP Integration:** Model Context Protocol is used for external service integrations, particularly for calendar and workspace management.

**Interface Governance:** Centralized interface registry prevents duplication. Always check `src/rm_ddd/core/interface_registry.py` before creating new interfaces.

## Steering System Integration

### Dual-Mode Steering System
Beast Mode uses a dual-mode steering system to serve different audiences:

**Production Mode** (`.kiro/steering/` only):
- For developers USING the Beast Mode framework
- Guides how to use ReflectiveModule, DAG orchestration, AI Memory Palace
- Deploy with: `./scripts/deploy-production-mode.sh`

**Development Mode** (`.kiro/steering/` + `.kiro/steering-dev/`):
- For developers BUILDING the Beast Mode framework itself  
- Additional internal development patterns and architecture guidance
- Deploy with: `./scripts/deploy-development-mode.sh`

### Steering Files Reference
- `security-credentials-governance.md` - Zero tolerance for hardcoded secrets
- `beast-mode-framework-patterns.md` - ReflectiveModule and systematic usage patterns
- `mathematical-governance-principle.md` - DAG orchestration and mathematical validation
- `quality-first-development.md` - >90% test coverage and systematic validation
- `ai-memory-palace-usage.md` - Persistent AI context management

### Using Steering Guidance
1. **Check current mode**: `cat .kiro/settings/steering-config.json | grep current_mode`
2. **Switch modes**: Use deployment scripts as needed
3. **Follow patterns**: Implement according to steering file guidance
4. **Validate compliance**: Ensure code follows systematic patterns

## Development Guidelines

### Critical Development Rules

**🎯 Steering System Compliance:** ALWAYS follow Beast Mode steering files in `.kiro/steering/` for systematic development patterns. Use deployment scripts to switch between production and development modes.

**🚫 ANTI-NO-VERIFY RULE:** NEVER use `--no-verify` or bypass quality gates.

**🐍 Python Execution:** Target Python 3.9+. Package is installed in editable mode.

**🔧 Interface Governance:** ALWAYS check interface registry before creating new interfaces to prevent duplication. Run `python src/rm_ddd/core/interface_duplication_detector.py` before interface changes.

**🏗️ Architecture Compliance:** ALL components must implement ReflectiveModule pattern (see `.kiro/steering/beast-mode-framework-patterns.md`).

**🔒 Security Compliance:** NEVER hardcode credentials - follow `.kiro/steering/security-credentials-governance.md`.

**📊 Mathematical Governance:** Use DAG orchestration and mathematical validation (see `.kiro/steering/mathematical-governance-principle.md`).

**🧪 Quality First:** Maintain >90% test coverage and systematic validation (see `.kiro/steering/quality-first-development.md`).

**🧠 AI Memory Palace:** Use persistent AI context management (see `.kiro/steering/ai-memory-palace-usage.md`).

### Working with Specifications
- All new features should have corresponding specs in `.kiro/specs/[feature-name]/`
- Each spec includes: `requirements.md`, `design.md`, and `tasks.md`
- Follow RM principles - avoid monolithic specifications
- Specs drive development - implement based on spec requirements

### Python Development Standards
- Target Python 3.9+
- Use Black for formatting (line length: 88)
- Use Ruff for linting with flake8 compatibility
- Use MyPy for type checking
- Pytest for testing with coverage reporting
- Type hints required for all functions
- Google-style docstrings required

### Testing Standards
- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- Maintain test coverage above reporting thresholds (>90% target)
- Use pytest markers: `@pytest.mark.slow`, `@pytest.mark.integration`, `@pytest.mark.unit`
- Run specific test types: `pytest -m unit`, `pytest -m integration`, `pytest -m "not slow"`

### Interface Development Workflow

**Before Creating Interfaces:**
1. Check existing interfaces in `src/rm_ddd/core/interface_registry.py`
2. Run `python src/rm_ddd/core/interface_duplication_detector.py`
3. Verify no conflicts exist

**During Interface Development:**
1. All interfaces MUST inherit from `ABC` and use `@abstractmethod`
2. Comprehensive type hints required for all methods
3. Google-style docstrings required
4. Single interface per file in most cases

**After Interface Creation:**
1. Register in central registry
2. Update all imports to use centralized interface
3. Run full test suite
4. Validate integration

### Docker Services
- Each service has its own dockerfile and docker-compose configuration
- MCP servers run as containerized services
- Check individual service README files for specific setup instructions

## Project Scripts and Entry Points

**Main CLI Entry Points:**
- `beast-mode` - Main CLI entry point (defined in pyproject.toml)
- `kiro-discovery` - Repository discovery tools (defined in pyproject.toml)

**Key Scripts:**
- `scripts/beast_mode_cli.py` - Beast Mode CLI implementation
- `scripts/deploy_observatory.py` - Deploy Observatory system
- Various specialized scripts for DAG orchestration, compliance, validation

## Project Dependencies

**Core:**
- pydantic (>=2.0.0) - Data validation
- click (>=8.0.0), typer (>=0.9.0), rich (>=13.0.0) - CLI framework

**ML/AI:**
- transformers (>=4.30.0), torch (>=2.0.0), scikit-learn (>=1.3.0)

**Testing:**
- pytest (>=7.0.0), pytest-cov (>=4.0.0), coverage (>=7.0.0)

**Dev Tools:**
- black (>=23.0.0), ruff (>=0.1.0), mypy (>=1.0.0), pre-commit (>=3.0.0)

**Monitoring:**
- prometheus-client (>=0.20.0), psutil (>=5.9.0)

**Optional:**
- `dev` - Development tools (black, ruff, mypy, pre-commit)
- `monitoring` - Monitoring tools (grafana-client, influxdb-client)
- `ml` - ML tools (tensorboard, wandb, jupyter)

## Quality Standards

### Code Quality
- Black formatting with 88 character line length
- Flake8/Ruff compliance - zero linting errors
- Type annotations required
- Comprehensive docstrings (Google style)

### Architecture Standards
- RM-DDD compliance - all modules implement ReflectiveModule
- Interface governance - registry-based duplication prevention
- Systematic prevention - proactive quality gates
- Zero technical debt goal

### Git Workflow
- Pre-commit hooks configured (`.pre-commit-config.yaml`)
- Never use `--no-verify` flag
- All commits must pass quality gates

## Important Context

### Project Mission
Demonstrate systematic development excellence through Beast Mode framework + AI-assisted development, targeting 10x velocity advantage over traditional approaches.

### Interface Duplication Crisis
The project previously had 48+ duplicate interface classes across 11+ files. Interface governance is now a critical focus:
- Always check interface registry before creating new interfaces
- Run duplication detection tools
- Follow consolidation procedures if duplicates found

### Spec-Driven Workflow
This project is heavily spec-driven with 100+ feature specifications. When working on features:
1. Start with requirements in `.kiro/specs/[feature]/requirements.md`
2. Review design in `.kiro/specs/[feature]/design.md`
3. Follow task breakdown in `.kiro/specs/[feature]/tasks.md`
4. Implement systematically following the spec

### Observatory System
The Observatory system provides monitoring, WebSocket management, and system health tracking. It's a critical component with:
- WebSocket support
- Cloudflare tunnel integration
- Real-time monitoring
- Health checks and recovery

## Development Workflow Pattern

1. **Steering Compliance First** - Review applicable steering files in `.kiro/steering/`
2. **Requirements Second** - Start with spec requirements
3. **Design Third** - Review/create design documentation following systematic patterns
4. **Code Fourth** - Implement with proper structure (ReflectiveModule, DAG orchestration, etc.)
5. **Quality Gates** - All code must pass linting, type checking, tests (>90% coverage)
6. **Documentation** - Update specs and docs as needed

### Deployment Mode Workflow

**For Framework Usage (Production Mode)**:
```bash
./scripts/deploy-production-mode.sh
# Follow .kiro/steering/ patterns for using Beast Mode
```

**For Framework Development (Development Mode)**:
```bash
./scripts/deploy-development-mode.sh  
# Follow both .kiro/steering/ and .kiro/steering-dev/ patterns
```

## Makefile System

The project uses a comprehensive Makefile system with modular targets:
- Main: `Makefile` - Primary orchestration
- Include: `makefiles/*.mk` - Modular targets
- Legacy: `Makefile.legacy` - Old Cloudflare-specific targets

Use `make help` to see all available targets organized by category.
