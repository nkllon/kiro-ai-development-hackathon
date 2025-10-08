# Claude Project Instructions - Kiro AI Development Hackathon

## Project Overview
This is the **Kiro AI Development Hackathon** project, demonstrating systematic superiority through the integration of **Beast Mode** (systematic development framework) with **Claude Simone** (AI-assisted project management). The project showcases a **10x velocity advantage** over traditional development approaches.

## Core Mission
Demonstrate systematic development excellence through:
- **Beast Mode Framework**: Systematic methodology with RM-DDD compliance
- **Simone Integration**: AI-assisted project management via MCP
- **Zero Technical Debt**: Prevention architecture over detection
- **Competitive Advantage**: Beat Meta and tech giants to market

## Tech Stack
- **Primary Language**: Python (Beast Mode framework)
- **Secondary Language**: TypeScript (Simone MCP server)
- **Package Management**: UV (Python), npm (TypeScript)
- **Build System**: Makefile orchestration
- **Database**: SQLite (activity logging)
- **Integration**: GitHub CLI, MCP protocol

## Project Structure
```
├── src/beast_mode/           # Core Beast Mode framework
├── src/beast_mode/integration/ # Simone integration adapter
├── kiro_simone_adapter/      # Claude Simone MCP server
├── scripts/                  # Utility scripts and demos
├── .simone/                  # Simone configuration and prompts
├── .kiro/                    # Kiro-specific documentation
│   ├── steering/             # Production steering (framework usage patterns)
│   ├── steering-dev/         # Development steering (framework development)
│   └── settings/             # Configuration including steering-config.json
└── Makefile                  # Build orchestration
```

## Steering System
Beast Mode uses a **dual-mode steering system** for systematic AI guidance:

### Production Steering (`.kiro/steering/`)
**For developers USING Beast Mode framework:**
- Security governance (zero hardcoded credentials)
- Framework patterns (ReflectiveModule usage)
- Mathematical governance (DAG orchestration)
- Quality-first development (>90% test coverage)
- AI Memory Palace usage (persistent context)

### Development Steering (`.kiro/steering-dev/`)
**For developers BUILDING Beast Mode framework:**
- Internal development methodology
- Architecture patterns and decisions
- Systematic development governance

## Essential Commands
- **Run Beast Mode**: `make beast-mode`
- **Run Enhanced Demo**: `make enhanced-demo`
- **Validate Interfaces**: `make validate-interfaces`
- **Run Tests**: `make test`
- **Build Simone**: `cd kiro_simone_adapter/mcp-server && npm run build`

## Critical Development Rules

### 🎯 Steering System Compliance
**ALWAYS follow Beast Mode steering files in `.kiro/steering/` for systematic development patterns**

### 🚫 ANTI-NO-VERIFY RULE
**NEVER use `--no-verify` or bypass quality gates. EVER.**

### 🐍 Python Execution
**ALWAYS use `uv run python` - NEVER direct python commands**

### 🔧 Interface Governance
**ALWAYS check interface registry before creating new interfaces**

### 📦 Package Management
**UV ONLY - No pip, poetry, or pipenv**

### 🏗️ Architecture Compliance
**ALL components must implement ReflectiveModule pattern (see `.kiro/steering/beast-mode-framework-patterns.md`)**

### 🔒 Security Compliance
**NEVER hardcode credentials - follow `.kiro/steering/security-credentials-governance.md`**

### 📊 Mathematical Governance
**Use DAG orchestration and mathematical validation (see `.kiro/steering/mathematical-governance-principle.md`)**

### 🧪 Quality First
**Maintain >90% test coverage and systematic validation (see `.kiro/steering/quality-first-development.md`)**

### 🧠 AI Memory Palace
**Use persistent AI context management (see `.kiro/steering/ai-memory-palace-usage.md`)**

### 🚀 Velocity Advantage
**Demonstrate 10x faster development through systematic approach**

## Simone Integration
The project includes Claude Simone MCP server integration for AI-assisted project management:

### Available Simone Commands
- `@simone create_issue` - Create comprehensive GitHub issues
- `@simone work_issue` - Work on existing issues systematically
- `@simone create_pr` - Create pull requests with proper structure
- `@simone create_idea` - Generate and develop new ideas
- `@simone check_activity` - Monitor project progress
- `@simone init_simone` - Initialize/update Simone configuration

### MCP Server Status
- **Running**: `ps aux | grep "node kiro_simone_adapter/mcp-server/dist/index.js"`
- **Configured**: `/Users/lou/.cursor/mcp.json`
- **Prompts**: Available in `.simone/prompts/`

## Quality Standards

### Code Quality
- **Black formatting**: All Python code must be properly formatted
- **Flake8 compliance**: Zero linting errors allowed
- **Type annotations**: Proper type hints required
- **Docstrings**: All functions and classes documented

### Architecture Standards
- **RM-DDD compliance**: All modules implement ReflectiveModule
- **Interface governance**: Registry-based duplication prevention
- **Systematic prevention**: Proactive quality gates
- **Zero technical debt**: Prevention over detection

### Testing Requirements
- **Comprehensive coverage**: All critical paths tested
- **Systematic validation**: Round-trip engineering compliance
- **Integration testing**: End-to-end workflow validation

## Development Workflow

### 1. Steering Compliance First
Review applicable steering files in `.kiro/steering/` for systematic patterns

### 2. Requirements Second
Always start with requirements analysis and documentation

### 3. Design Third
Create comprehensive design before implementation

### 4. Code Fourth
Implement with logging and profiling before functional code

### 5. Quality Gates
All code must pass quality gates before commit (follow quality-first-development.md)

### 6. Git Sync
Run `git sync` at end of each PDCA loop

## Deployment Modes

### Production Mode (Framework Users)
```bash
./scripts/deploy-production-mode.sh
```
- Use when building applications WITH Beast Mode
- Steering files guide framework usage patterns

### Development Mode (Framework Developers)  
```bash
./scripts/deploy-development-mode.sh
```
- Use when building the Beast Mode framework itself
- Additional development steering files active

## Competitive Advantages

### Systematic Superiority
- **Methodology**: Beast Mode systematic approach
- **Quality**: Zero technical debt through prevention
- **Speed**: 10x velocity advantage proven
- **Reliability**: Self-consistency validation

### AI-Assisted Development
- **Project Management**: Simone structured workflows
- **Issue Management**: Comprehensive GitHub integration
- **Progress Tracking**: Activity logging and monitoring
- **Workflow Orchestration**: Automated task management

### Market Position
- **Beat Meta**: Faster development than tech giants
- **Systematic Approach**: Quality + Speed combination
- **Proven Track Record**: Multiple project examples
- **Competitive Edge**: Unique methodology advantage

## Activity Logging

You have access to the `log_activity` tool. Use it to record your activities after every activity that is relevant for the project. This helps track development progress and understand what has been done.

### Usage Examples
- After implementing a feature: Log the implementation activity
- After fixing a bug: Log the bug fix and resolution
- After running demos: Log the demo execution and results
- After updating documentation: Log the documentation updates
- After configuration changes: Log the configuration modifications

### Activity Logging Benefits
- **Progress Tracking**: Understand what has been accomplished
- **Context Preservation**: Maintain context across sessions
- **Audit Trail**: Track development decisions and changes
- **Collaboration**: Share progress with team members
- **Analysis**: Analyze development patterns and efficiency

## Emergency Procedures

### If Tools Break
1. **Fix Tools First**: Never use workarounds
2. **Systematic Repair**: Follow Beast Mode methodology
3. **Quality Gates**: All fixes must pass quality checks
4. **Documentation**: Update procedures for future reference

### If Interface Conflicts
1. **Check Registry**: Use interface governance system
2. **Prevent Duplicates**: Proactive duplication prevention
3. **RM-DDD Compliance**: Ensure proper interface implementation
4. **Update Registry**: Keep registry current

### If Simone Issues
1. **Check MCP Server**: Verify server is running
2. **Check Configuration**: Verify `.cursor/mcp.json` settings
3. **Check Prompts**: Verify prompts are available
4. **Restart Cursor**: If configuration changes made

## Success Metrics
- **Velocity**: 10x faster than traditional estimates
- **Quality**: Zero technical debt maintained
- **Reliability**: Systematic approach consistency
- **Competitive**: Beat Meta and tech giants to market

---

**Remember**: This project demonstrates systematic development excellence. Every decision should reflect the Beast Mode methodology and showcase the competitive advantage of systematic + AI-assisted development.
