# Quick Start Template

This template provides a minimal setup for getting started with Kiro AI Development Framework.

## What's Included

- Basic project structure
- Essential configuration files
- Example domain model
- Test setup
- Makefile integration

## Quick Setup

1. **Copy this template** to your project directory
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Run tests**: `make test`
4. **Start building**: Follow the examples in `src/`

## Project Structure

```
your-project/
├── src/                    # Your source code
│   ├── __init__.py
│   ├── domain/            # Domain models
│   └── services/          # Domain services
├── tests/                 # Test files
├── config/                # Configuration files
├── requirements.txt       # Python dependencies
├── Makefile              # Build automation
└── README.md             # This file
```

## Example Usage

```python
from src.domain import Order, OrderService

# Create a new order
order = Order("order-123", "customer-456")
order.add_item("product-789", 2, 29.99)

# Calculate total
service = OrderService()
total = service.calculate_total(order)
print(f"Total: ${total.amount}")
```

## Available Commands

- `make help` - Show all available commands
- `make test` - Run tests
- `make build` - Build the project
- `make clean` - Clean build artifacts
- `make dev` - Start development environment

## Next Steps

1. Explore the [complete documentation](https://nkllon.github.io/kiro-ai-development-hackathon/)
2. Check out [examples](https://github.com/nkllon/kiro-ai-development-hackathon/tree/main/examples)
3. Join the [community discussions](https://github.com/nkllon/kiro-ai-development-hackathon/discussions)

## Support

- **Documentation**: [docs.kiro-ai.dev](https://docs.kiro-ai.dev)
- **Issues**: [GitHub Issues](https://github.com/nkllon/kiro-ai-development-hackathon/issues)
- **Discussions**: [GitHub Discussions](https://github.com/nkllon/kiro-ai-development-hackathon/discussions)
