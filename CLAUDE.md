# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Build, Test, and Quality Assurance
```bash
# Run all tests
make test

# Run linting
make lint
make ruff

# Type checking
make mypy

# Code formatting
make format

# Run coverage
make coverage

# Full quality check (lint + type check + test)
make quality

# Python virtual environment setup
make venv

# Install dependencies
make install
```

### Beast Mode Framework Commands
```bash
# Show comprehensive help and available commands
make help
make beast-mode-help

# System status and health checks
make beast-mode-status
make beast-mode-health

# Execute PDCA cycle
make pdca-cycle

# Development utilities
make beast-mode-cli    # CLI interface
make devpost-cli       # DevPost integration
```

### Testing Commands
```bash
# Run specific test types
make test-unit
make test-integration
make test-slow        # Run slow tests

# Test with specific patterns
pytest tests/ -k "test_pattern"
pytest tests/unit/
pytest tests/integration/
```

## Architecture Overview

### Core Structure
This is an AI-Powered Spec-Driven Development Framework called "Beast Mode Framework" with the following key components:

**Primary Source Structure:**
- `src/beast_mode/` - Main framework implementation
  - `analysis/` - Root Cause Analysis (RCA) and safety analysis
  - `api/` - REST API endpoints
  - `assessment/` - Production readiness and compliance validation
  - `autonomous/` - PDCA orchestration and autonomous agents
  - `backlog/` - Task and dependency management
  - `billing/` - GCP integration and cost management
  - `cli/` - Command-line interface
  - `compliance/` - Git analysis and compliance checking
  - `mcp_integrations/` - Model Context Protocol integrations (Google Calendar, etc.)

**Configuration and Specifications:**
- `.kiro/` - Framework specifications and configuration
  - `.kiro/specs/` - Individual feature specifications with requirements, design, and tasks
  - `.kiro/settings/` - MCP and other service configurations

**Docker Services:**
- `docker/google-calendar-mcp/` - Google Calendar MCP server
- `docker/google-workspace-mcp/` - Google Workspace integration
- `docker/g2n-calendar-sse/` - Calendar Server-Sent Events service

### Key Architectural Patterns

**Reflective Module (RM) Architecture:** The framework follows RM principles where components are decomposed into focused, single-responsibility modules rather than monolithic specifications.

**PDCA-Driven Development:** Plan-Do-Check-Act cycles are fundamental to the framework's operation, with systematic orchestration and metrics collection.

**Spec-Driven Development:** Features are defined through comprehensive specifications in `.kiro/specs/` with requirements, design documents, and task breakdowns.

**MCP Integration:** Model Context Protocol is used for external service integrations, particularly for calendar and workspace management.

## Development Guidelines

### Working with Specifications
- All new features should have corresponding specs in `.kiro/specs/[feature-name]/`
- Each spec includes: `requirements.md`, `design.md`, and `tasks.md`
- Follow RM principles - avoid monolithic specifications

### Python Development
- Target Python 3.9+
- Use Black for formatting (line length: 88)
- Use Ruff for linting
- Use MyPy for type checking
- Pytest for testing with coverage reporting

### Testing Standards
- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- Maintain test coverage above reporting thresholds
- Use pytest markers: `@pytest.mark.slow`, `@pytest.mark.integration`, `@pytest.mark.unit`

### Docker Services
- Each service has its own dockerfile and docker-compose configuration
- MCP servers run as containerized services
- Check individual service README files for specific setup instructions

## Project Scripts
- `beast-mode` - Main CLI entry point
- `kiro-discovery` - Repository discovery tools

## Dependencies
- Core: pydantic, click, rich, typer
- ML: transformers, torch, scikit-learn
- Testing: pytest, pytest-cov, coverage
- Dev tools: black, ruff, mypy, pre-commit
- Monitoring: prometheus-client, psutil