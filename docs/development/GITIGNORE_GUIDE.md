# .gitignore Guide

## Overview

This document explains the patterns in our `.gitignore` file and their purposes. Understanding these patterns helps maintain a clean repository and prevents accidental commits of sensitive or unwanted files.

## Pattern Categories

### Python Development

**Purpose**: Prevent Python-specific build artifacts and cache files from being committed.

- `__pycache__/` - Python bytecode cache directories
- `*.py[cod]` - Compiled Python files (.pyc, .pyo, .pyd)
- `build/`, `dist/` - Package build artifacts
- `*.egg-info/` - Package metadata
- `.pytest_cache/` - Pytest cache files
- `.mypy_cache/` - MyPy type checker cache

### Security & Credentials (CRITICAL)

**Purpose**: Prevent accidental exposure of sensitive information.

- `.env*` - Environment files containing secrets
- `credentials/`, `secrets/` - Credential directories
- `*.key`, `*.pem` - Private keys and certificates
- `*credential*scan*.json` - Security scan reports that may contain sensitive data

**⚠️ CRITICAL**: Never commit files matching these patterns. They may contain:
- API keys and tokens
- Database passwords
- Private keys
- Authentication credentials

### Logs & Temporary Files

**Purpose**: Prevent accumulation of temporary files and logs.

- `*.log` - Log files
- `*.tmp`, `*.temp` - Temporary files
- `*.pid` - Process ID files
- `logs/`, `temp/` - Log and temporary directories

### Database Files

**Purpose**: Prevent large database files from being committed.

- `*.db`, `*.sqlite*` - SQLite database files
- `*.db-shm`, `*.db-wal` - SQLite shared memory and write-ahead log files

**Note**: Use database migrations and seed data instead of committing database files.

### Beast Mode Specific

**Purpose**: Prevent Beast Mode-specific runtime data from being committed.

- `metrics_data/` - Performance and execution metrics
- `**/grafana-data/`, `**/prometheus-data/` - Monitoring data (use Docker volumes)
- `.task-*-complete` - Task execution markers
- `memory_palace_data/` - AI Memory Palace runtime data
- `dag_execution_logs/` - DAG orchestration logs

### Backup & Archive Directories

**Purpose**: Prevent backup files from being committed to version control.

- `*backup*/`, `*.backup*` - Backup directories and files
- `archive_*/` - Archive directories
- `deployment_snapshots/` - Deployment backup snapshots

**Note**: Use proper backup systems instead of committing backup files.

### Development Tools & IDEs

**Purpose**: Prevent IDE-specific configuration files from being committed.

- `.vscode/` - Visual Studio Code settings
- `.idea/` - PyCharm/IntelliJ settings
- `*.swp`, `*.swo` - Vim swap files

### Operating System Files

**Purpose**: Prevent OS-specific files from being committed.

- `.DS_Store` - macOS folder metadata
- `Thumbs.db` - Windows thumbnail cache
- `*~` - Linux backup files

## Exceptions (Files to Keep)

Some files are explicitly kept despite matching ignore patterns:

- `!.env.example` - Example environment files for documentation
- `!.kiro/**/*.json` - Kiro configuration files
- `!examples/**/*.json` - Example data files
- `!tests/fixtures/**/*` - Test fixture files

## Best Practices

### For Developers

1. **Review before committing**: Always check what files you're committing
2. **Use environment variables**: Never hardcode secrets in source code
3. **Clean up regularly**: Remove temporary files and logs from your workspace
4. **Test on clean environments**: Ensure your code works without local artifacts

### For Code Reviews

1. **Check for ignored files**: Ensure no sensitive files are being committed
2. **Validate patterns**: Ensure new file types are properly ignored
3. **Update documentation**: Update this guide when adding new patterns

### For CI/CD

1. **Validate clean state**: Ensure builds work with clean repositories
2. **Security scanning**: Scan for accidentally committed credentials
3. **Size monitoring**: Monitor repository size to prevent bloat

## Adding New Patterns

When adding new ignore patterns:

1. **Categorize properly**: Add to the appropriate section
2. **Document purpose**: Explain why the pattern is needed
3. **Test thoroughly**: Ensure the pattern works as expected
4. **Update this guide**: Document the new pattern here

### Pattern Syntax

- `file.txt` - Ignore specific file
- `*.txt` - Ignore all .txt files
- `dir/` - Ignore entire directory
- `**/logs/` - Ignore logs directory anywhere in the tree
- `!keep.txt` - Exception: keep this file despite other patterns

## Troubleshooting

### File Still Being Tracked

If a file is still being tracked despite being in `.gitignore`:

```bash
# Remove from tracking but keep local file
git rm --cached filename

# Remove directory from tracking
git rm -r --cached directory/
```

### Pattern Not Working

1. Check pattern syntax
2. Ensure pattern is in correct section
3. Check for conflicting exception patterns
4. Test with `git check-ignore filename`

### Large Repository Size

If repository is still large:

1. Check for large files: `git ls-files | xargs ls -la | sort -k5 -rn | head`
2. Use git LFS for necessary large files
3. Consider repository cleanup tools

## Security Considerations

### Critical Patterns

These patterns are critical for security:

- `.env*` - Environment files
- `credentials/` - Credential directories  
- `*.key` - Private keys
- `*credential*scan*` - Security reports

### Regular Security Checks

1. **Scan regularly**: Use tools like `detect-secrets` to scan for credentials
2. **Audit commits**: Review commits for accidentally included secrets
3. **Rotate exposed credentials**: If credentials are accidentally committed, rotate them immediately

## Maintenance

### Regular Reviews

- Review `.gitignore` quarterly
- Remove obsolete patterns
- Add patterns for new file types
- Update documentation

### Performance Monitoring

- Monitor repository size
- Check for pattern effectiveness
- Optimize patterns for performance

## Related Documentation

- [Security Guidelines](../security/SECURITY.md)
- [Development Setup](../community/DEVELOPMENT_SETUP.md)
- [Contributing Guidelines](../../CONTRIBUTING.md)