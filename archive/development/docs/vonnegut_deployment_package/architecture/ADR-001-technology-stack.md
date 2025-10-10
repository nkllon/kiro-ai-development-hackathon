# ADR-001: Technology Stack Selection

## Status
Accepted

## Context
The project requires appropriate technology choices for different components based on their specific use cases and requirements. While maintaining consistency where possible, some components benefit from specialized technology stacks.

## Decision
We will use **use-case appropriate technology stacks** with the following guidelines:

### Core Framework (Beast Mode)
- **Language**: Python 3.9+ (supports 3.9, 3.10, 3.11, 3.12)
- **Build System**: Hatchling with pyproject.toml configuration
- **Package Manager**: uv (preferred) with pip fallback
- **Web Framework**: FastAPI for REST APIs
- **Data Validation**: Pydantic v2+ for data models
- **Testing**: pytest with asyncio, mock, timeout, and coverage plugins
- **CLI Framework**: Click 8.0+

### Document Processing Services
- **Language**: Node.js/TypeScript (excellent for text processing and markdown)
- **Web Framework**: Express.js for REST APIs
- **Build System**: npm/yarn with TypeScript compilation
- **Testing**: Jest or Mocha with comprehensive coverage

## Rationale
1. **Python for Core Framework**: AI/ML integration, existing codebase, mature tooling
2. **Node.js for Document Services**: Superior text processing, markdown parsing ecosystem, JavaScript's strength with document manipulation
3. **Use Case Optimization**: Choose the best tool for each specific domain
4. **Developer Productivity**: Leverage language strengths rather than forcing uniformity

## Consequences
### Positive
- Optimal technology choice for each use case
- Leverages JavaScript's strength in document processing
- Python's strength in AI/ML for core framework
- Better performance and developer experience per domain

### Negative
- Multiple technology stacks to maintain
- Team needs expertise in both ecosystems
- More complex deployment and integration

## Compliance
- Core Beast Mode Framework: Python 3.9+
- Document processing services: Node.js/TypeScript
- New components: Choose based on use case appropriateness
- Integration: Use REST APIs for cross-language communication

## Related ADRs
- ADR-002: Service Integration Patterns (planned)
- ADR-003: Testing Standards Across Stacks (planned)