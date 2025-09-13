# Kiro AI Development Hackathon - Project Constitution

## Project Info
**Name:** Kiro AI Development Hackathon  
**Description:** Beast Mode systematic development framework demonstrating 10x velocity advantage through AI-assisted development

## Tech Stack
- **Language:** Python (primary), TypeScript (Simone integration)
- **Framework:** Beast Mode (systematic development), MCP Server (Simone)
- **Package Manager:** UV (Python), npm (TypeScript)
- **Database:** SQLite (activity logging)

## Structure
- `src/beast_mode/` - Core Beast Mode framework
- `src/beast_mode/integration/` - Simone integration adapter
- `kiro_simone_adapter/` - Claude Simone MCP server
- `scripts/` - Utility scripts and demos
- `.simone/` - Simone configuration and prompts

## Essential Commands
- **Run Beast Mode:** `make beast-mode`
- **Run tests:** `make test`
- **Run enhanced demo:** `make enhanced-demo`
- **Validate interfaces:** `make validate-interfaces`
- **Build Simone:** `cd kiro_simone_adapter/mcp-server && npm run build`

## Critical Rules
1. **NEVER use `--no-verify`** - All commits must pass quality gates
2. **ALWAYS use UV for Python** - No pip, poetry, or pipenv
3. **Interface governance required** - Use registry before creating interfaces
4. **Zero technical debt policy** - Prevention over detection
5. **Beast Mode methodology** - Follow systematic development approach






