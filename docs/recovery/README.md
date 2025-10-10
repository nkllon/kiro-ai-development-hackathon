# Recovery Documentation

This directory contains documentation for recovering, restoring, and understanding archived Beast Mode modules.

## Quick Links

| Document | Purpose | Use When |
|----------|---------|----------|
| [Beast Mode Module Restoration Guide](./beast-mode-module-restoration-guide.md) | Complete restoration procedures and known issues | You need to restore archived modules or understand why tests are failing |
| [Archive Module Index](./archive-module-index.md) | Comprehensive index of what's where in the archive | You need to find specific archived implementations or compare versions |

## When to Use This Documentation

### Scenario 1: Test Collection Errors

**Symptoms:**
- `pytest` shows "132 errors during collection"
- `ImportError: cannot import name 'X' from 'src.beast_mode.Y'`
- Tests reference `organization`, `self_refactoring`, `testing`, or `tool_health` modules

**Solution:**
1. Read [Beast Mode Module Restoration Guide](./beast-mode-module-restoration-guide.md)
2. Follow the "Quick Restore" section
3. Review "Known Issues After Restoration"

### Scenario 2: Finding Historical Implementations

**Symptoms:**
- Need to understand how something used to work
- Looking for old implementation of a feature
- Want to compare current vs archived code

**Solution:**
1. Use [Archive Module Index](./archive-module-index.md)
2. Check "Quick Access Commands" section
3. Use comparison commands to diff versions

### Scenario 3: Understanding Cleanup History

**Symptoms:**
- Want to know what was moved and when
- Need to understand rationale for archival
- Looking for git commit history

**Solution:**
1. Review "Historical Timeline" in [Beast Mode Module Restoration Guide](./beast-mode-module-restoration-guide.md)
2. Check the "Key Commits" section
3. Use git commands to explore further

## Quick Reference

### Restore All Missing Modules
```bash
git checkout 2fc465fd -- \
  src/beast_mode/organization \
  src/beast_mode/self_refactoring \
  src/beast_mode/testing \
  src/beast_mode/tool_health \
  src/beast_mode/observatory/ai_consultation/visual_regression.py
```

### Check Archive Locations
```bash
find archive/development -type d -name "organization" -o -name "self_refactoring" -o -name "testing" -o -name "tool_health"
```

### Verify Current State
```bash
ls -la src/beast_mode/ | grep -E "organization|self_refactoring|testing|tool_health"
```

## Important Notes

⚠️ **DO NOT**:
- Remove `@with_circuit_breaker` decorators without understanding their purpose
- Rename imports without investigating API changes
- Copy from archive without checking git history first

✅ **DO**:
- Check git history before making changes
- Document any modifications
- Verify with tests after restoration
- Read the known issues section

## Status

| Module | Status | Last Verified |
|--------|--------|---------------|
| Organization | ✅ Restored from `2fc465fd` | 2025-10-09 |
| Self-Refactoring | ✅ Restored from `2fc465fd` | 2025-10-09 |
| Testing | ✅ Restored from `2fc465fd` | 2025-10-09 |
| Tool Health | ✅ Restored from `2fc465fd` | 2025-10-09 |
| Visual Regression | ✅ Restored from `2fc465fd` | 2025-10-09 |

## Contributing

When updating this documentation:
1. Maintain the Quick Reference section
2. Update status table with dates
3. Add new scenarios as discovered
4. Link to specific sections, not just files

**Last Updated**: 2025-10-09

