# Development Mode Steering Files

This directory contains steering files used during **Beast Mode framework development**. These are internal development guidelines for building the framework itself.

## Dev vs Production Steering

### Production Steering (`.kiro/steering/`)
- **Audience**: Developers using the Beast Mode framework
- **Purpose**: Guide AI assistants to use Beast Mode patterns correctly
- **Content**: Framework usage patterns, best practices, API guidance

### Development Steering (`.kiro/steering-dev/`)
- **Audience**: Beast Mode framework developers
- **Purpose**: Guide development of the framework itself
- **Content**: Internal patterns, architecture decisions, development workflows

## Deployment Modes

### Production Deployment
```bash
# Production mode uses only .kiro/steering/ files
export BEAST_MODE_ENV=production
# Only framework usage steering files are active
```

### Development Deployment
```bash
# Development mode uses both directories
export BEAST_MODE_ENV=development
# Both framework usage AND development steering files are active
```

## Switching Between Modes

Use the deployment script to switch modes:

```bash
# Switch to production mode (framework users)
./scripts/deploy-production-mode.sh

# Switch to development mode (framework developers)
./scripts/deploy-development-mode.sh
```

## Current Dev Steering Files

These files guide Beast Mode framework development:

- `hounds-protocol-implementation.md` - Internal development protocol
- `systematic-development-governance.md` - Development methodology
- `infrastructure-first-implementation.md` - Architecture patterns
- `executable-patch-code-governance.md` - Code quality standards
- `observer-mode-governance.md` - Development observability
- `bounded-dimensions-principle.md` - Resource constraints
- `prompt-writing-patterns.md` - AI interaction patterns

## Adding New Dev Steering Files

When adding development steering files:

1. Place in `.kiro/steering-dev/`
2. Use `inclusion: manual` or `inclusion: fileMatch` in frontmatter
3. Document the purpose and audience
4. Update this README

## Archive Recovery

To recover archived development steering files:

```bash
# Copy from archive if needed
cp archive/development/vonnegut_deployment_package/steering/*.md .kiro/steering-dev/
```