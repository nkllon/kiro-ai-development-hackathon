# Technology Stack & Build System

## Core Technologies

### Beast Mode Framework Stack
**Language**: Python 3.9+ (supports 3.9, 3.10, 3.11, 3.12)
**Build System**: Hatchling with pyproject.toml configuration
**Package Manager**: uv (preferred) with pip fallback
**Testing**: pytest with asyncio, mock, timeout, and coverage plugins

### Document Processing Stack
**Language**: Node.js/TypeScript (for document validation, markdown processing)
**Build System**: npm/yarn with TypeScript compilation
**Web Framework**: Express.js for REST APIs
**Testing**: Jest or Mocha with comprehensive coverage

## Key Dependencies

### AI & ML Libraries
- `openai>=1.0.0` - OpenAI API integration
- `anthropic>=0.7.0` - Anthropic Claude integration  
- `langgraph>=0.6.6` - Multi-agent workflow orchestration

### Core Framework
- `pydantic>=2.0.0` - Data validation and serialization
- `click>=8.0.0` - Command-line interface framework
- `jinja2>=3.1.0` - Template engine for code generation
- `pyyaml>=6.0.0` - YAML configuration parsing

### Development Tools
- `black>=23.0.0` - Code formatting (line length: 88)
- `ruff>=0.1.0` - Fast Python linter
- `mypy>=1.0.0` - Static type checking
- `pre-commit>=3.4.0` - Git hooks for quality gates

## Build & Development Commands

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

### Legacy CLI Operations
```bash
# Task analysis and execution
python3 cli.py analyze
python3 cli.py execute --simulate
python3 cli.py status

# Requirements audit
python3 cli.py requirements-audit
```

## Configuration Standards

**Line Length**: 88 characters (Black/Ruff standard)
**Python Target**: 3.9+ compatibility
**Test Timeout**: 30 seconds default
**Async Mode**: Auto-detection for pytest

## Quality Gates

- **Coverage**: >90% test coverage requirement (DR8 compliance)
- **Linting**: Ruff with E, W, F, I, B, C4, UP rules
- **Formatting**: Black with 88-character line length
- **Type Safety**: MyPy static analysis
- **Security**: Bandit integration for vulnerability scanning

## Universal Architecture Patterns

### Cross-Language Principles
**Reflective Module (RM)**: All modules must implement health monitoring and status interfaces
**Model-Driven**: Decisions based on project registry consultation
**Systematic Approach**: No ad-hoc implementations, systematic tool repair
**PDCA Cycles**: Plan-Do-Check-Act methodology for all development tasks
**>90% Test Coverage**: All components must achieve >90% test coverage (DR8 compliance)

### Language-Specific RM Implementation

#### Python RM Pattern
```python
from abc import ABC, abstractmethod

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

#### TypeScript/Node.js RM Pattern
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

#### Go RM Pattern
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

#### Rust RM Pattern
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

#### Java RM Pattern
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
## Unive
rsal Quality Gates

### Testing Standards (All Languages)
- **Coverage**: >90% test coverage requirement (DR8 compliance)
- **Test Types**: Unit, integration, performance, security tests
- **Test Automation**: CI/CD integration with quality gates
- **Failure Analysis**: Automatic RCA on test failures

### Code Quality Standards

#### Python Quality Gates
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

#### TypeScript/Node.js Quality Gates
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

#### Go Quality Gates
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

#### Rust Quality Gates
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

#### Java Quality Gates
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

## Universal PDCA Implementation

### PDCA Cycle Interface (Language Agnostic)

All components must implement systematic PDCA cycles:

1. **Plan**: Define objectives, success criteria, and approach
2. **Do**: Execute the planned approach with monitoring
3. **Check**: Validate results against success criteria
4. **Act**: Apply learnings and iterate

### Cross-Language Integration

#### REST API Standards
- **Health Endpoints**: `/health`, `/ready`, `/metrics`
- **Status Endpoints**: `/status`, `/info`, `/version`
- **Error Format**: Consistent JSON error responses
- **Logging**: Structured JSON logging with correlation IDs

#### Message Queue Integration
- **Event Format**: CloudEvents specification
- **Error Handling**: Dead letter queues with retry policies
- **Monitoring**: Distributed tracing with OpenTelemetry

#### Configuration Management
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

### Integration Requirements

All services must:
- Expose health/status endpoints
- Implement graceful shutdown
- Support distributed tracing
- Use structured logging
- Follow semantic versioning
- Provide OpenAPI/gRPC specifications