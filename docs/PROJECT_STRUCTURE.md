# Project Structure

This document describes the organized structure of the Beast Mode AI Development Framework.

## Root Directory
```
kiro-ai-development-hackathon/
├── README.md                   # Main project documentation
├── LICENSE                     # Project license
├── pyproject.toml             # Python project configuration
├── requirements.txt           # Python dependencies
├── Makefile                   # Build and development commands
├── .gitignore                 # Git ignore patterns
├── .env.example              # Environment variables template
├── docker-compose.yml        # Docker composition (if present)
└── Dockerfile               # Docker configuration (if present)
```

## Source Code (`src/`)
All source code is organized in the `src/` directory with clear module separation:

- `src/beast_mode/` - Core Beast Mode framework
- `src/rm_ddd/` - Reflective Module DDD implementation
- `src/ai_memory_palace/` - AI Memory Palace system
- `src/dag_orchestration/` - DAG orchestration system
- `src/cms_platform/` - CMS platform implementation
- And other specialized modules...

## Examples (`examples/`)
Working examples and demonstrations:

- `examples/notebook/` - Jupyter notebook examples
- `examples/*.py` - Python example scripts
- Each example includes documentation and usage instructions

## Documentation (`docs/`)
Comprehensive documentation:

- `docs/README.md` - Documentation index
- `docs/api/` - API documentation
- `docs/guides/` - User guides and tutorials
- `docs/architecture/` - Architecture documentation

## Tests (`tests/`)
Test suite mirroring the source structure:

- `tests/unit/` - Unit tests
- `tests/integration/` - Integration tests
- `tests/fixtures/` - Test fixtures and data

## Configuration (`config/`)
Configuration files and templates:

- Configuration files for various services
- Environment-specific configurations
- Service configuration templates

## Data (`data/`)
Data files and datasets:

- Sample data for examples
- Configuration data
- Non-sensitive data files

## Deployment (`deployment/`)
Deployment configurations and scripts:

- Docker configurations
- Kubernetes manifests
- Deployment scripts and documentation

## Archive (`archive/`)
Archived development artifacts:

- Historical development files
- Backup directories
- Legacy code and experiments
- Assessment results and reports

## Kiro Configuration (`.kiro/`)
Kiro-specific configuration and specifications:

- `.kiro/specs/` - Feature specifications
- `.kiro/steering/` - AI assistant steering rules
- `.kiro/hooks/` - Agent automation hooks

## Scripts (`scripts/`)
Utility and automation scripts:

- Development and maintenance scripts
- Deployment automation
- Analysis and reporting tools
