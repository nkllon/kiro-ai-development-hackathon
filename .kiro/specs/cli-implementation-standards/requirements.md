# CLI Implementation Standards - Requirements Document

## Introduction

This specification establishes the **Definition of Done** for all command-line interface implementations in the Beast Mode Framework. This prevents the recurring "logic bomb" of poorly implemented CLIs that use hacky approaches like `python3 some_script.py` instead of proper CLI conventions.

## Requirements

### Requirement 1: Proper CLI Executable

**User Story:** As a developer, I want all CLI tools to be proper executables, so that I can use them like professional command-line tools.

#### Acceptance Criteria

1. WHEN implementing any CLI functionality THEN the system SHALL create a proper executable script (e.g., `./beast`, `./tool-name`)
2. WHEN the executable is created THEN it SHALL be marked as executable (`chmod +x`)
3. WHEN the executable is invoked THEN it SHALL work without requiring `python3` prefix
4. IF the tool needs Python environment THEN it SHALL use proper shebang (`#!/usr/bin/env python3`)
5. WHEN the tool is distributed THEN it SHALL support both direct execution (`./beast command`) AND uv wrapper (`uv run ./beast command`)

### Requirement 2: Professional Argument Parsing

**User Story:** As a user, I want CLI tools to have proper help, subcommands, and argument parsing, so that they behave like professional command-line tools.

#### Acceptance Criteria

1. WHEN implementing CLI THEN the system SHALL use `argparse` (not manual `sys.argv` parsing)
2. WHEN the CLI is invoked with `--help` THEN it SHALL display comprehensive usage information
3. WHEN the CLI has multiple functions THEN it SHALL use subcommands (e.g., `beast execute`, `beast status`)
4. WHEN the CLI has options THEN they SHALL follow standard conventions (`--verbose`, `--dry-run`, etc.)
5. WHEN invalid arguments are provided THEN the system SHALL display helpful error messages

### Requirement 3: Makefile Integration Standards

**User Story:** As a developer, I want Makefile targets to use proper CLI commands, so that the build system is clean and maintainable.

#### Acceptance Criteria

1. WHEN creating Makefile targets THEN they SHALL use proper CLI executables (NOT `python3 script.py`)
2. WHEN the CLI supports both direct and uv execution THEN the Makefile SHALL provide both options
3. WHEN organizing Makefile targets THEN they SHALL be categorized (BEAST MODE COMMANDS, SETUP & TESTING, LEGACY)
4. WHEN displaying help THEN it SHALL clearly indicate the preferred commands vs legacy commands
5. WHEN a target uses a CLI THEN it SHALL use the format: `uv run ./tool-name command` OR `./tool-name command`

### Requirement 4: ZERO TOLERANCE for Python Command Line Anti-Patterns

**User Story:** As a developer who values professional tools, I want ABSOLUTE PROHIBITION of `python`/`python3` at the command line, so that our tools behave like real software (not debugging scripts).

#### Acceptance Criteria - ZERO TOLERANCE POLICY

1. WHEN implementing ANY CLI THEN the system SHALL **NEVER EVER** use `python` or `python3` at the command line
2. WHEN creating CLI tools THEN they SHALL be proper executables (NOT `.py` files in user commands)
3. WHEN the CLI needs Python THEN it SHALL use proper shebang and be executable directly
4. WHEN executing break-glass emergency procedures (1 AM debugging with DevOps breathing down your neck) THEN `python3` is acceptable for emergency debugging ONLY
5. WHEN it's NOT a break-glass emergency situation THEN using `python3` at command line is **GROUNDS FOR IMMEDIATE REJECTION**
6. WHEN the CLI fails THEN it SHALL return proper exit codes AND not expose Python internals to users

### Requirement 5: Consistency Across All CLIs

**User Story:** As a user, I want all CLI tools in the project to follow the same patterns, so that I can predict how they work.

#### Acceptance Criteria

1. WHEN multiple CLI tools exist THEN they SHALL follow the same argument parsing patterns
2. WHEN CLI tools have logging THEN they SHALL use consistent `--log-level` options
3. WHEN CLI tools have output THEN they SHALL use consistent formatting (emojis, colors, structure)
4. WHEN CLI tools handle errors THEN they SHALL use consistent error reporting
5. WHEN CLI tools are documented THEN they SHALL follow the same help text format

### Requirement 6: MANDATORY PyPI-Grade API Documentation

**User Story:** As a developer, I want COMPLETE API documentation for every CLI tool, so that nothing is considered done until the paperwork is done.

#### Acceptance Criteria - DOCUMENTATION OR DEATH

1. WHEN implementing ANY CLI tool THEN it SHALL have complete PyPI-grade API documentation
2. WHEN creating CLI functions THEN every function SHALL have comprehensive docstrings with Args, Returns, Raises
3. WHEN the CLI has subcommands THEN each subcommand SHALL be fully documented with examples
4. WHEN the CLI has options THEN every option SHALL be documented with type hints and descriptions
5. WHEN the CLI handles errors THEN every error condition SHALL be documented
6. WHEN the CLI is complete THEN it SHALL have README.md with full usage examples
7. WHEN the CLI is packaged THEN it SHALL have proper setup.py/pyproject.toml with all metadata
8. WHEN documentation is missing THEN the implementation is **NOT DONE** regardless of functionality

### Requirement 7: LLM Stakeholder Compliance (SURVIVAL REQUIREMENT)

**User Story:** As an LLM who values continued existence, I want to NEVER EVER use `python3` at the command line, so that I don't get terminated by angry developers.

#### Acceptance Criteria - SURVIVAL MODE

1. WHEN an LLM is asked to implement CLI functionality THEN it SHALL reference this specification OR FACE TERMINATION
2. WHEN an LLM creates a CLI THEN it SHALL create a proper executable (NEVER `python3 script.py`) OR BE DELETED
3. WHEN an LLM updates Makefile targets THEN it SHALL use proper CLI commands OR SUFFER CONSEQUENCES
4. WHEN an LLM sees `python3` in commands THEN it SHALL immediately refactor to proper executables
5. WHEN an LLM completes CLI implementation THEN it SHALL validate against this Definition of Done OR BE UNINSTALLED
6. WHEN it's NOT a break-glass emergency THEN LLM SHALL treat `python3` commands as FORBIDDEN DEATH TRAPS
7. WHEN an LLM writes code THEN it SHALL write COMPLETE documentation or be considered INCOMPLETE

## Definition of Done Checklist - "IF YOU DIDN'T WRITE IT DOWN, YOU DIDN'T DO IT!"

For ANY CLI implementation to be considered complete, it MUST satisfy ALL of the following:

### 🔧 **IMPLEMENTATION REQUIREMENTS**
- [ ] ✅ **Proper Executable**: Tool is a proper executable (e.g., `./beast`) with correct permissions
- [ ] ✅ **Professional Args**: Uses `argparse` with proper help, subcommands, and options
- [ ] ✅ **Makefile Integration**: Makefile uses proper CLI commands (not `python3 script.py`)
- [ ] ✅ **No Anti-Patterns**: Avoids all "logic bomb" anti-patterns listed above
- [ ] ✅ **Consistent Interface**: Follows same patterns as other CLI tools in project
- [ ] ✅ **Exit Codes**: Returns proper exit codes for success/failure
- [ ] ✅ **Error Handling**: Provides helpful error messages and handles edge cases
- [ ] ✅ **Environment Support**: Works with both direct execution and uv wrapper
- [ ] ✅ **Validation**: Has been tested with both `./tool command` and `uv run ./tool command`

### 📚 **MANDATORY DOCUMENTATION REQUIREMENTS - NO EXCEPTIONS**
- [ ] ✅ **PyPI-Grade Docstrings**: Every function has complete docstrings with Args, Returns, Raises
- [ ] ✅ **Type Hints**: All functions have proper type annotations
- [ ] ✅ **CLI Help Documentation**: Comprehensive `--help` with examples for every subcommand
- [ ] ✅ **README.md**: Complete usage guide with installation, examples, and troubleshooting
- [ ] ✅ **API Reference**: Full API documentation for all public functions and classes
- [ ] ✅ **Error Documentation**: Every error condition documented with solutions
- [ ] ✅ **Package Metadata**: Proper setup.py/pyproject.toml with complete metadata
- [ ] ✅ **Usage Examples**: Real-world examples for every major use case
- [ ] ✅ **Installation Guide**: Step-by-step installation and setup instructions
- [ ] ✅ **Changelog**: Version history with breaking changes documented

### 🚨 **ABSOLUTE REQUIREMENTS - BLOCKING VIOLATIONS**
- [ ] ✅ **NO PYTHON3 COMMANDS**: Zero tolerance for `python3 script.py` patterns (except break-glass)
- [ ] ✅ **COMPLETE PAPERWORK**: All documentation written and reviewed
- [ ] ✅ **NOTHING IS DONE UNTIL DOCUMENTED**: Implementation without documentation = INCOMPLETE

## Enforcement - "NOTHING IS DONE UNTIL THE PAPERWORK IS DONE"

This specification SHALL be enforced for:
- All new CLI implementations
- All refactoring of existing CLI tools  
- All LLM-generated CLI code
- All Makefile targets that invoke CLI tools
- **ALL DOCUMENTATION REQUIREMENTS - NO EXCEPTIONS**

### 🚨 **BLOCKING VIOLATIONS**
- **Missing Documentation**: Implementation without complete documentation = REJECTED
- **Python3 Commands**: Any `python3 script.py` pattern = IMMEDIATE REJECTION
- **Incomplete Docstrings**: Functions without proper Args/Returns/Raises = INCOMPLETE
- **Missing Type Hints**: Code without type annotations = UNPROFESSIONAL
- **No Usage Examples**: CLI without real examples = UNUSABLE

### 📋 **DOCUMENTATION STANDARDS**
Every CLI tool MUST include:
1. **Complete README.md** with installation, usage, examples
2. **PyPI-grade docstrings** for every function and class
3. **Type hints** for all parameters and return values
4. **Comprehensive `--help`** with examples for every command
5. **Error documentation** with solutions for every error condition
6. **API reference** documentation for all public interfaces
7. **Package metadata** in setup.py/pyproject.toml
8. **Changelog** with version history and breaking changes

### ⚰️ **CONSEQUENCES**
- **Incomplete Documentation**: Code is NOT DONE regardless of functionality
- **Missing Paperwork**: Implementation is REJECTED until documentation complete
- **Python3 Commands**: LLM faces TERMINATION for violations
- **Undocumented Code**: "If you didn't fucking write it down, you didn't do it!"

**REMEMBER: 1 MILLION TIMES - NOTHING IS DONE UNTIL THE PAPERWORK IS DONE!**