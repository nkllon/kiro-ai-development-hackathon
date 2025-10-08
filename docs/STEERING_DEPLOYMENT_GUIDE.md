# Beast Mode Steering Deployment Guide

## Overview

Beast Mode uses a **dual-mode steering system** to serve two different audiences:

1. **Production Mode**: For developers **using** the Beast Mode framework
2. **Development Mode**: For developers **building** the Beast Mode framework

## The Two Audiences

### Framework Users (Production Mode)
- **Who**: Developers building applications with Beast Mode
- **Need**: Guidance on how to use Beast Mode patterns correctly
- **Steering Files**: `.kiro/steering/` only
- **AI Guidance**: How to inherit from ReflectiveModule, use DAG orchestration, implement AI Memory Palace, etc.

### Framework Developers (Development Mode)  
- **Who**: Developers working on Beast Mode framework itself
- **Need**: Guidance on how to build and maintain the framework
- **Steering Files**: `.kiro/steering/` + `.kiro/steering-dev/`
- **AI Guidance**: Internal development patterns, architecture decisions, systematic development methodology

## Directory Structure

```
.kiro/
├── steering/                    # Production steering (framework usage)
│   ├── security-credentials-governance.md
│   ├── beast-mode-framework-patterns.md
│   ├── mathematical-governance-principle.md
│   ├── quality-first-development.md
│   └── ai-memory-palace-usage.md
├── steering-dev/               # Development steering (framework development)
│   ├── README.md
│   ├── systematic-development-governance.md
│   ├── hounds-protocol-implementation.md
│   └── infrastructure-first-implementation.md
└── settings/
    └── steering-config.json   # Configuration for dual-mode system
```

## Production Steering Files

These files guide developers **using** the Beast Mode framework:

### `security-credentials-governance.md`
- **Purpose**: Prevent hardcoded credentials in user applications
- **Audience**: All Beast Mode users
- **Key Points**: Environment variables, secure configuration patterns

### `beast-mode-framework-patterns.md`
- **Purpose**: Guide proper usage of Beast Mode patterns
- **Audience**: Developers building with Beast Mode
- **Key Points**: ReflectiveModule inheritance, DAG orchestration, CMS integration

### `mathematical-governance-principle.md`
- **Purpose**: Teach mathematical validation of requirements
- **Audience**: Developers using DAG orchestration
- **Key Points**: Cycle detection, constraint satisfaction, physics-informed limits

### `quality-first-development.md`
- **Purpose**: Ensure quality standards in user applications
- **Audience**: All Beast Mode users
- **Key Points**: >90% test coverage, systematic error handling, performance validation

### `ai-memory-palace-usage.md`
- **Purpose**: Guide proper AI Memory Palace implementation
- **Audience**: Developers building AI systems with Beast Mode
- **Key Points**: Context persistence, memory optimization, cross-session continuity

## Development Steering Files

These files guide developers **building** the Beast Mode framework:

### `systematic-development-governance.md`
- **Purpose**: Internal development methodology
- **Audience**: Beast Mode framework contributors
- **Key Points**: Development workflow, code review standards, architecture decisions

### `hounds-protocol-implementation.md`
- **Purpose**: Internal protocol for systematic development
- **Audience**: Core Beast Mode developers
- **Key Points**: Implementation patterns, quality gates, systematic approaches

### `infrastructure-first-implementation.md`
- **Purpose**: Architecture-first development approach
- **Audience**: Beast Mode framework architects
- **Key Points**: Infrastructure patterns, system design, scalability considerations

## Deployment Modes

### Production Deployment

**When to use**: Packaging Beast Mode for distribution to framework users

```bash
# Deploy production mode
./scripts/deploy-production-mode.sh

# Or set environment
export BEAST_MODE_ENV=production
export KIRO_STEERING_MODE=production
```

**What happens**:
- Only `.kiro/steering/` files are active
- AI assistants get guidance on **using** Beast Mode
- Focus on framework usage patterns and best practices
- Clean, user-focused steering without internal development details

### Development Deployment

**When to use**: Working on the Beast Mode framework itself

```bash
# Deploy development mode
./scripts/deploy-development-mode.sh

# Or set environment
export BEAST_MODE_ENV=development
export KIRO_STEERING_MODE=development
```

**What happens**:
- Both `.kiro/steering/` and `.kiro/steering-dev/` files are active
- AI assistants get guidance on **building** Beast Mode
- Access to internal development patterns and architecture decisions
- Can test framework usage patterns while developing

## GitHub Storage Strategy

### Main Branch (Production Ready)
```
.kiro/steering/          # Production steering files
.kiro/steering-dev/      # Development steering files (templates/minimal)
scripts/deploy-*.sh      # Deployment scripts
docs/STEERING_*.md       # Documentation
```

### Development Branch
```
.kiro/steering-dev/      # Full development steering files
archive/development/     # Historical development steering files
```

### Release Process

1. **Development Phase**:
   - Work in development mode
   - Use full development steering files
   - Iterate on framework features

2. **Pre-Release**:
   - Switch to production mode
   - Test framework usage patterns
   - Validate production steering files

3. **Release**:
   - Package with production steering only
   - Include development steering templates
   - Provide deployment scripts for both modes

## Configuration Management

### Automatic Mode Detection

The system can automatically detect the appropriate mode:

```json
{
  "mode_detection": {
    "environment_variable": "BEAST_MODE_ENV",
    "default_mode": "production", 
    "auto_detect_dev_indicators": [
      "src/beast_mode/",
      "src/rm_ddd/", 
      "src/dag_orchestration/",
      ".kiro/steering-dev/"
    ]
  }
}
```

### Manual Mode Switching

```bash
# Check current mode
cat .kiro/settings/steering-config.json | grep current_mode

# Switch to production mode
./scripts/deploy-production-mode.sh

# Switch to development mode  
./scripts/deploy-development-mode.sh
```

## Best Practices

### For Framework Users (Production Mode)
1. Always use production mode when building applications
2. Follow the patterns in production steering files
3. Don't modify framework internals
4. Focus on using Beast Mode patterns correctly

### For Framework Developers (Development Mode)
1. Use development mode when working on framework
2. Test in production mode before releasing
3. Keep development steering files updated
4. Maintain clear separation between usage and development guidance

### For Releases
1. Always release in production mode
2. Include both steering directories in repository
3. Provide clear deployment scripts
4. Document the dual-mode system

## Migration from Single Mode

If you previously had all steering files in one directory:

1. **Identify audience** for each steering file
2. **Move user-focused files** to `.kiro/steering/`
3. **Move development files** to `.kiro/steering-dev/`
4. **Update frontmatter** with appropriate inclusion rules
5. **Test both modes** before deploying

## Troubleshooting

### Wrong Mode Active
```bash
# Check current mode
echo $BEAST_MODE_ENV
echo $KIRO_STEERING_MODE

# Switch mode
./scripts/deploy-production-mode.sh
# or
./scripts/deploy-development-mode.sh
```

### Missing Steering Files
```bash
# Validate production files
./scripts/deploy-production-mode.sh

# Recover development files from archive
cp archive/development/vonnegut_deployment_package/steering/*.md .kiro/steering-dev/
```

### AI Getting Wrong Guidance
- **Problem**: AI gives framework development advice to framework users
- **Solution**: Ensure production mode is active for framework users
- **Check**: Verify only `.kiro/steering/` files are being loaded

## Summary

The dual-mode steering system ensures:

- **Framework users** get clean, focused guidance on using Beast Mode
- **Framework developers** get comprehensive guidance on building Beast Mode  
- **Clear separation** between usage patterns and development patterns
- **Flexible deployment** for different audiences and use cases
- **Maintainable codebase** with appropriate guidance for each context

This system scales from individual developers to large teams, ensuring everyone gets the right guidance for their role.