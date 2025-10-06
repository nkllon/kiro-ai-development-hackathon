# CLI Implementation Standards - Enforcement Notice

## 🚨 MANDATORY COMPLIANCE FOR ALL CLI IMPLEMENTATIONS

This document establishes **MANDATORY** standards for all command-line interface implementations in this project. These standards are now **REQUIRED** and violations will block code acceptance.

## The "Logic Bomb" Problem

The recurring pattern of implementing CLIs as `python3 some_script.py` is a **logic bomb** that creates:
- Unprofessional user experience
- Inconsistent command patterns  
- Maintenance nightmares
- Poor integration with build systems

## Definition of Done - CLI Implementation

**ALL CLI implementations MUST satisfy these requirements:**

### ✅ **REQUIRED: Proper Executable**
```bash
# ✅ CORRECT
./beast execute
uv run ./beast execute

# ❌ WRONG - BLOCKS CODE ACCEPTANCE
python3 clean_cli.py execute
python3 some_script.py command
```

### ✅ **REQUIRED: Professional Argument Parsing**
```python
# ✅ CORRECT - Uses argparse with subcommands
parser = argparse.ArgumentParser(description="Tool Description")
subparsers = parser.add_subparsers(dest="command")
execute_parser = subparsers.add_parser("execute", help="Execute tasks")

# ❌ WRONG - Manual argv parsing
if len(sys.argv) > 1 and sys.argv[1] == "execute":
```

### ✅ **REQUIRED: Makefile Integration**
```makefile
# ✅ CORRECT
execute:
	@echo "🚀 Starting execution..."
	uv run ./beast execute

# ❌ WRONG - BLOCKS CODE ACCEPTANCE  
execute:
	@echo "🚀 Starting execution..."
	python3 clean_cli.py execute
```

### ✅ **REQUIRED: Consistent Interface**
- All CLI tools use same argument patterns
- All tools support `--help` with comprehensive information
- All tools return proper exit codes (0=success, non-zero=failure)
- All tools handle errors gracefully with helpful messages

## Enforcement Policy

### For LLM Implementations
**When implementing CLI functionality, LLMs MUST:**
1. Create proper executable scripts (not `.py` files for user commands)
2. Use `argparse` for all argument parsing
3. Update Makefile targets to use proper CLI commands
4. Validate implementation against the Definition of Done checklist
5. Reference the full specification: `.kiro/specs/cli-implementation-standards/requirements.md`

### For Code Reviews
**Code reviewers MUST reject any CLI implementation that:**
- Uses `python3 script.py` patterns in user-facing commands
- Lacks proper argument parsing with `argparse`
- Doesn't provide comprehensive `--help` documentation
- Doesn't return proper exit codes
- Violates any item in the Definition of Done checklist

### For Project Maintenance
**All existing CLI implementations MUST be refactored to meet these standards.**

## Current Compliance Status

### ✅ **COMPLIANT: Beast Mode CLI**
- Executable: `./beast` ✅
- Argument parsing: `argparse` with subcommands ✅  
- Makefile integration: `uv run ./beast execute` ✅
- Help documentation: Comprehensive `--help` ✅
- Exit codes: Proper success/failure codes ✅

### ❌ **NON-COMPLIANT: Legacy Scripts**
- `clean_cli.py` - Should be refactored or removed
- Any `python3 script.py` patterns in Makefile
- Manual argument parsing implementations

## Implementation Example

**CORRECT CLI Implementation Pattern:**
```python
#!/usr/bin/env python3
"""
Professional CLI Tool
"""
import argparse
import sys

def cmd_execute(args):
    """Execute command implementation."""
    # Implementation here
    return 0  # Success exit code

def main():
    parser = argparse.ArgumentParser(description="Professional CLI Tool")
    subparsers = parser.add_subparsers(dest="command")
    
    execute_parser = subparsers.add_parser("execute", help="Execute tasks")
    execute_parser.add_argument("--option", help="Example option")
    
    args = parser.parse_args()
    
    if args.command == "execute":
        return cmd_execute(args)
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

## Conclusion

These standards are **NON-NEGOTIABLE** and apply to:
- All new CLI implementations
- All refactoring of existing tools
- All LLM-generated code
- All human-written code

**Compliance with these standards is MANDATORY for code acceptance.**

---

**Specification Reference:** `.kiro/specs/cli-implementation-standards/requirements.md`  
**Enforcement Date:** Immediate  
**Scope:** All CLI implementations in Beast Mode Framework