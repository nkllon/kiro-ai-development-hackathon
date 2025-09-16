---
layout: default
title: Getting Started
description: Quick start guide for Kiro AI Development Hackathon
---

# 🚀 Getting Started with Kiro AI

Welcome to Kiro AI! This guide will help you get up and running quickly with our advanced AI development framework.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+** - [Download Python](https://www.python.org/downloads/)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **Docker** (optional) - [Download Docker](https://www.docker.com/get-started)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/nkllon/kiro-ai-development-hackathon.git
cd kiro-ai-development-hackathon
```

### 2. Install Dependencies

#### Option A: Using pip
```bash
pip install -r requirements.txt
```

#### Option B: Using UV (Recommended)
```bash
# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

### 3. Verify Installation

```bash
# Run the test suite
make test

# Check available commands
make help
```

## Quick Start

### Basic Usage

```python
from src.beast_mode import BeastModeOrchestrator
from src.rc1.migration import MigrationOrchestrator

# Initialize the Beast Mode system
orchestrator = BeastModeOrchestrator()

# Run a migration
migration = MigrationOrchestrator()
migration.plan_migration()
migration.execute_migration()
```

### Makefile System

Kiro AI includes a comprehensive Makefile system with 175 targets:

```bash
# Show all available targets
make help

# Build the project
make build

# Run tests
make test

# Start development environment
make dev

# Clean up
make clean

# Show project status
make status
```

## Development Setup

### 1. Install Development Dependencies

```bash
# Install with development extras
uv sync --extra dev

# Or with pip
pip install -r requirements-dev.txt
```

### 2. Install Pre-commit Hooks

```bash
pre-commit install
```

### 3. Run the Development Server

```bash
# Start the development environment
make dev

# Or run specific components
make start-beast-mode
make start-ghostbusters
```

## Project Structure

```
kiro-ai-development-hackathon/
├── src/                    # Source code
│   ├── beast_mode/         # Core Beast Mode framework
│   ├── rc1/               # RC1 migration tools
│   └── rm_ddd/            # Domain-driven design components
├── docs/                  # Documentation
├── examples/              # Example implementations
├── tests/                 # Test suites
├── scripts/               # Utility scripts
├── makefile_system/       # Makefile system
└── deployment/            # Deployment configurations
```

## First Project

### 1. Create a New Domain

```python
from src.rm_ddd import DomainEntity, AggregateRoot

@domain_entity("order_management")
class Order(AggregateRoot[str]):
    def __init__(self, order_id: str, customer_id: str):
        super().__init__(order_id, "order_management")
        self.customer_id = customer_id
        self.items = []
        self.status = "pending"
    
    def add_item(self, product_id: str, quantity: int, price: float):
        """Add item to order with domain validation"""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        self.items.append({
            "product_id": product_id,
            "quantity": quantity,
            "price": price
        })
```

### 2. Run Tests

```bash
# Run all tests
make test

# Run specific test category
make test-unit
make test-integration
make test-e2e
```

### 3. Build and Deploy

```bash
# Build the project
make build

# Deploy to development
make deploy-dev

# Deploy to production
make deploy-prod
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Beast Mode Configuration
BEAST_MODE_DEBUG=true
BEAST_MODE_LOG_LEVEL=INFO

# Database Configuration
DATABASE_URL=sqlite:///kiro_ai.db

# AI Configuration
OPENAI_API_KEY=your_api_key_here
ANTHROPIC_API_KEY=your_api_key_here
```

### Configuration Files

- `config/devpost_config.yaml` - DevPost integration settings
- `makefile_system/` - Makefile system configuration
- `deployment/` - Deployment configurations

## Examples

### Domain-Driven Design

```python
from src.rm_ddd import DomainService, ValueObject

class Money(ValueObject):
    def __init__(self, amount: float, currency: str):
        self.amount = amount
        self.currency = currency
    
    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)

@domain_service("order_management")
class OrderService:
    def calculate_total(self, order: Order) -> Money:
        total = sum(item["price"] * item["quantity"] for item in order.items)
        return Money(total, "USD")
```

### Beast Mode Integration

```python
from src.beast_mode import BeastModeOrchestrator
from src.beast_mode.pdca import PDCAOrchestrator

# Initialize Beast Mode
beast_mode = BeastModeOrchestrator()

# Run PDCA cycle
pdca = PDCAOrchestrator()
pdca.plan()
pdca.do()
pdca.check()
pdca.act()
```

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Ensure you're in the project root
cd kiro-ai-development-hackathon

# Check Python path
export PYTHONPATH=$PWD:$PYTHONPATH
```

#### 2. Dependency Issues
```bash
# Clean and reinstall
make clean
uv sync --reinstall

# Or with pip
pip install -r requirements.txt --force-reinstall
```

#### 3. Test Failures
```bash
# Run tests with verbose output
make test-verbose

# Run specific test
pytest tests/test_specific.py -v
```

### Getting Help

- **📚 Documentation**: [Complete Documentation](documentation/)
- **💬 Discussions**: [GitHub Discussions](https://github.com/nkllon/kiro-ai-development-hackathon/discussions)
- **🐛 Issues**: [GitHub Issues](https://github.com/nkllon/kiro-ai-development-hackathon/issues)
- **📧 Contact**: [Contact Information](mailto:contact@kiro-ai.dev)

## Next Steps

Now that you have Kiro AI set up, explore these resources:

1. **[Documentation](documentation/)** - Complete system documentation
2. **[Examples](examples/)** - Example implementations and tutorials
3. **[API Reference](api-reference/)** - Complete API documentation
4. **[Community](community/)** - Join the community and contribute

---

**Ready to build something amazing?** Start with our [examples](examples/) or dive into the [complete documentation](documentation/)!
