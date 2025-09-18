# Claude-Simone Integration for Interface Consolidation

## Overview

This project integrates the Claude-Simone framework with Cursor AI to systematically resolve the critical interface duplication crisis. The integration provides structured prompts and workflows that help Claude understand and manage the complex interface consolidation process.

## 🚨 Current Crisis

- **48+ duplicate interface classes** across 11+ files
- **0.00 consistency score** indicating complete specification conflicts
- **Multiple "authoritative" sources** claiming single source of truth
- **Integration failures** due to inconsistent interface contracts

## 🛠️ Setup Complete

### Installed Components
- ✅ **Claude Code CLI** - AI assistant integration
- ✅ **Docker** - GitHub MCP server support
- ✅ **Simone Framework** - Structured project management
- ✅ **Cursor Project Rules** - Interface governance

### Configuration Files Created
- `simone-interface-consolidation.md` - Simone framework specification
- `.cursor/rules` - Cursor AI project rules for interface governance
- `launch-claude-simone.sh` - Launch script for Claude-Simone integration
- `mcp-github-config.json` - GitHub MCP server configuration

## 🚀 How to Use

### Step 1: Launch Claude-Simone Integration

```bash
# Make sure Cursor is running and this project is open
./launch-claude-simone.sh
```

### Step 2: Authorize Claude
- You'll be prompted to log in with your Anthropic API key
- Follow the authorization process

### Step 3: Provide Simone Context
Copy and paste this prompt into the Claude terminal:

```
I'm working on resolving a critical interface duplication crisis in this codebase. Please review the Simone framework specification in `simone-interface-consolidation.md` and begin with Task 1: Interface Audit and Inventory.

The project has:
- 48+ duplicate interface classes across 11+ files
- 0.00 consistency score indicating complete conflicts
- Multiple "authoritative" sources claiming single source of truth

Please start by:
1. Reading the Simone framework specification
2. Analyzing the current interface duplication situation
3. Running the existing consolidation tools
4. Creating a comprehensive interface inventory

Use the existing tools in `src/rm_ddd/core/` for analysis and consolidation.
```

## 📋 Simone Framework Tasks

### Task 1: Interface Audit and Inventory
- Complete inventory of all interface definitions
- Categorize interfaces by domain and type
- Identify authoritative sources vs duplicates
- Generate comprehensive interface map

### Task 2: Consolidation Strategy Development
- Define consolidation criteria and priorities
- Create interface hierarchy and dependency map
- Design migration strategy for existing implementations
- Plan backward compatibility approach

### Task 3: Implementation of Consolidated Interfaces
- Create single source of truth for each interface
- Implement authoritative interface definitions
- Create comprehensive interface documentation
- Ensure all methods have proper type hints

### Task 4: Migration and Deprecation
- Update all imports to use consolidated interfaces
- Deprecate duplicate interface files
- Create migration scripts for existing code
- Update all documentation and examples

### Task 5: Governance and Prevention
- Implement systems to prevent future duplications
- Create interface registration validation
- Implement pre-commit hooks for duplication detection
- Add CI/CD integration for interface governance

## 🔧 Available Tools

### Interface Analysis Tools
- `src/rm_ddd/core/interface_consolidation_engine.py` - Consolidation engine
- `src/rm_ddd/core/interface_duplication_detector.py` - Duplication detection
- `scripts/unify_reflective_module_interfaces.py` - Unification scripts

### Interface Registry
- `src/rm_ddd/core/interface_registry.py` - Central interface registry
- `src/rm_ddd/core/unified_reflective_module.py` - Unified module system

### Quality Assurance
- Cursor project rules in `.cursor/rules`
- UV package management with `pyproject.toml`
- Comprehensive testing framework

## 📊 Success Metrics

### Interface Quality
- [ ] Zero interface duplications
- [ ] 100% consistency score
- [ ] All interfaces properly documented
- [ ] Complete test coverage

### Development Efficiency
- [ ] Clear interface discovery
- [ ] Automated duplication prevention
- [ ] Streamlined development workflow
- [ ] Reduced integration issues

### Architectural Integrity
- [ ] Single source of truth for interfaces
- [ ] Clear interface hierarchy
- [ ] Proper domain boundaries
- [ ] Consistent ubiquitous language

## 🚨 Emergency Procedures

### If Duplication Detected
1. STOP all interface work immediately
2. Run consolidation analysis
3. Identify authoritative source
4. Plan consolidation strategy
5. Execute consolidation plan
6. Verify no regressions

### If Integration Breaks
1. Check interface consistency
2. Verify import statements
3. Run interface validation
4. Fix inconsistencies
5. Test integration thoroughly

## 🔗 Useful Commands

### Run Interface Analysis
```bash
# Run duplication detection
uv run python src/rm_ddd/core/interface_duplication_detector.py

# Run consolidation engine
uv run python src/rm_ddd/core/interface_consolidation_engine.py

# Run unification scripts
uv run python scripts/unify_reflective_module_interfaces.py
```

### Quality Checks
```bash
# Run linting
uv run flake8 src/rm_ddd/core/

# Run type checking
uv run mypy src/rm_ddd/core/

# Run formatting
uv run black src/rm_ddd/core/
```

### GitHub Integration
```bash
# Set up GitHub MCP server (if needed)
export GITHUB_PERSONAL_ACCESS_TOKEN=your_token_here
./install-github-mcp.sh
```

## 📚 Documentation

### Key Documents
- `simone-interface-consolidation.md` - Simone framework specification
- `INTERFACE_DUPLICATION_ISSUE.md` - Detailed issue analysis
- `.cursor/rules` - Cursor AI project rules
- `README.md` - Project overview

### Related Specifications
- `docs/requirements/compatibility/unified_interfaces_requirements.md`
- `docs/design/compatibility/unified_interfaces_design.md`
- `.kiro/specs/beast-mode-interface-governance/`

## 🎯 Next Steps

1. **Launch Claude-Simone**: Run `./launch-claude-simone.sh`
2. **Provide Context**: Use the provided prompt to start Task 1
3. **Follow Tasks**: Work through the 5 tasks systematically
4. **Validate Results**: Ensure all success metrics are met
5. **Implement Governance**: Set up prevention systems

## 🆘 Troubleshooting

### Claude Not Responding
- Check Anthropic API key authorization
- Verify internet connection
- Restart Claude Code with `claude /ide`

### Interface Conflicts
- Check `.cursor/rules` for governance guidelines
- Run duplication detection tools
- Follow emergency procedures

### Integration Issues
- Verify all imports are updated
- Check interface consistency
- Run comprehensive test suite

---

**This integration provides a systematic approach to resolving the interface duplication crisis using the proven Claude-Simone framework methodology.**





