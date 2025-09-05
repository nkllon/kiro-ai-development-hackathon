# Implementation Reference Guide

## Overview
This document contains implementation examples, code patterns, and technical details that support the high-level policies defined in `.kiro/steering/`. These are reference materials for developers, not governance policies.

## Reflective Module (RM) Pattern Examples

### Python RM Pattern
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class ReflectiveModule(ABC):
    @abstractmethod
    def get_module_status(self) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def is_healthy(self) -> bool:
        pass
    
    @abstractmethod
    def get_health_indicators(self) -> List[HealthIndicator]:
        pass
```

### TypeScript/Node.js RM Pattern
```typescript
interface ReflectiveModule {
  getModuleStatus(): Promise<ModuleStatus>;
  isHealthy(): Promise<boolean>;
  getHealthIndicators(): Promise<HealthIndicator[]>;
  gracefulShutdown(): Promise<void>;
}

abstract class BaseReflectiveModule implements ReflectiveModule {
  abstract getModuleStatus(): Promise<ModuleStatus>;
  abstract isHealthy(): Promise<boolean>;
  abstract getHealthIndicators(): Promise<HealthIndicator[]>;
  
  async gracefulShutdown(): Promise<void> {
    // Default implementation
  }
}
```

### Go RM Pattern
```go
type ReflectiveModule interface {
    GetModuleStatus() (ModuleStatus, error)
    IsHealthy() (bool, error)
    GetHealthIndicators() ([]HealthIndicator, error)
    GracefulShutdown() error
}

type BaseReflectiveModule struct {
    name string
    version string
}
```

### Rust RM Pattern
```rust
use async_trait::async_trait;

#[async_trait]
pub trait ReflectiveModule {
    async fn get_module_status(&self) -> Result<ModuleStatus, Error>;
    async fn is_healthy(&self) -> Result<bool, Error>;
    async fn get_health_indicators(&self) -> Result<Vec<HealthIndicator>, Error>;
    async fn graceful_shutdown(&self) -> Result<(), Error>;
}
```

### Java RM Pattern
```java
public interface ReflectiveModule {
    CompletableFuture<ModuleStatus> getModuleStatus();
    CompletableFuture<Boolean> isHealthy();
    CompletableFuture<List<HealthIndicator>> getHealthIndicators();
    CompletableFuture<Void> gracefulShutdown();
}

public abstract class BaseReflectiveModule implements ReflectiveModule {
    protected final String name;
    protected final String version;
    
    public abstract CompletableFuture<ModuleStatus> getModuleStatus();
    public abstract CompletableFuture<Boolean> isHealthy();
    public abstract CompletableFuture<List<HealthIndicator>> getHealthIndicators();
}
```

## Development Commands Reference

### Environment Setup
```bash
# Install dependencies (preferred)
uv pip install -r requirements.txt

# Alternative with pip
pip install -r requirements.txt

# Development dependencies
pip install -e ".[dev]"
```

### Beast Mode Operations
```bash
# Execute tasks directly
./beast execute
uv run ./beast execute

# Check system status
./beast status
uv run ./beast status

# Run Beast Mode framework
make beast-mode
make pdca-cycle
make systematic-repair
```

### Testing & Quality
```bash
# Run all tests
pytest tests/ -v
make test

# Run tests with RCA on failures
make test-with-rca

# Code formatting
black src/ tests/
ruff check src/ tests/

# Type checking
mypy src/
```

## Quality Gate Examples

### Python Quality Gates
```bash
# Linting & Formatting
ruff check src/ tests/ --fix
black src/ tests/ --line-length 88
mypy src/ --strict

# Testing & Coverage
pytest tests/ --cov=src --cov-report=html --cov-fail-under=90
bandit -r src/ -f json

# Security & Dependencies
safety check
pip-audit
```

### TypeScript/Node.js Quality Gates
```bash
# Linting & Formatting
eslint src/ tests/ --fix
prettier --write src/ tests/
tsc --noEmit --strict

# Testing & Coverage
jest --coverage --coverageThreshold='{"global":{"branches":90,"functions":90,"lines":90,"statements":90}}'
npm audit --audit-level moderate

# Security
npm audit fix
snyk test
```

### Go Quality Gates
```bash
# Linting & Formatting
golangci-lint run
gofmt -s -w .
go vet ./...

# Testing & Coverage
go test -v -race -coverprofile=coverage.out ./...
go tool cover -func=coverage.out | grep total | awk '{print $3}' # Must be >90%

# Security
gosec ./...
go mod tidy && go mod verify
```

### Rust Quality Gates
```bash
# Linting & Formatting
cargo clippy -- -D warnings
cargo fmt --check

# Testing & Coverage
cargo test
cargo tarpaulin --out Html --output-dir coverage --fail-under 90

# Security
cargo audit
cargo deny check
```

### Java Quality Gates
```bash
# Linting & Formatting
./gradlew checkstyleMain checkstyleTest
./gradlew spotlessCheck

# Testing & Coverage
./gradlew test jacocoTestReport
# JaCoCo must show >90% coverage

# Security
./gradlew dependencyCheckAnalyze
./gradlew spotbugsMain spotbugsTest
```

## Configuration Standards

### Python Configuration
- **Line Length**: 88 characters (Black/Ruff standard)
- **Python Target**: 3.9+ compatibility
- **Test Timeout**: 30 seconds default
- **Async Mode**: Auto-detection for pytest

### Dependencies
```toml
# Core Framework
pydantic = ">=2.0.0"
click = ">=8.0.0"
jinja2 = ">=3.1.0"
pyyaml = ">=6.0.0"

# AI & ML Libraries
openai = ">=1.0.0"
anthropic = ">=0.7.0"
langgraph = ">=0.6.6"

# Development Tools
black = ">=23.0.0"
ruff = ">=0.1.0"
mypy = ">=1.0.0"
pre-commit = ">=3.4.0"
```

## File Naming Conventions

### Python Files
- **Modules**: `snake_case.py`
- **Classes**: `PascalCase` in snake_case files
- **CLI Scripts**: `*_cli.py`
- **Tests**: `test_*.py`

### Scripts Categories
- **Analysis**: `*_analyzer.py`, `*_analysis.py` - Data analysis tools
- **CLI Tools**: `*_cli.py` - Command-line utilities
- **Generators**: `*_generator.py` - Code and artifact generation
- **Validators**: `*_validator.py` - Validation and compliance tools
- **Fixers**: `*_fixer.py` - Automated repair tools
- **Integration**: `*_integration.py` - External system integration

### Documentation
- **Specifications**: `requirements.md`, `design.md`, `tasks.md`
- **Documentation**: `README.md`, `*.md`
- **Reports**: `*-report.md`, `*-analysis.md`

### Configuration
- **Python**: `pyproject.toml`, `requirements.txt`
- **Make**: `Makefile`, `makefiles/*.mk`
- **Git**: `.pre-commit-config.yaml`

## Integration Standards

### REST API Standards
- **Health Endpoints**: `/health`, `/ready`, `/metrics`
- **Status Endpoints**: `/status`, `/info`, `/version`
- **Error Format**: Consistent JSON error responses
- **Logging**: Structured JSON logging with correlation IDs

### Message Queue Integration
- **Event Format**: CloudEvents specification
- **Error Handling**: Dead letter queues with retry policies
- **Monitoring**: Distributed tracing with OpenTelemetry

### Configuration Management
- **Environment Variables**: 12-factor app compliance
- **Secrets**: External secret management (not in code)
- **Feature Flags**: Runtime configuration without deployment

## Language Selection Guidelines

### Use Case → Language Mapping
- **AI/ML, Data Processing**: Python (pandas, numpy, scikit-learn)
- **Document Processing, Web UIs**: TypeScript/Node.js (rich ecosystem)
- **High-Performance Services**: Go or Rust (concurrency, speed)
- **Enterprise Integration**: Java (ecosystem, tooling)
- **System Programming**: Rust or Go (safety, performance)
- **Rapid Prototyping**: Python or TypeScript (developer velocity)

## PDCA Implementation Examples

### PDCA Cycle Interface (Language Agnostic)

All components must implement systematic PDCA cycles:

1. **Plan**: Define objectives, success criteria, and approach
2. **Do**: Execute the planned approach with monitoring
3. **Check**: Validate results against success criteria
4. **Act**: Apply learnings and iterate

---

**Note**: This is a reference document. The actual governance policies are in `.kiro/steering/`. Use these examples to implement the systematic principles defined in the steering policies.