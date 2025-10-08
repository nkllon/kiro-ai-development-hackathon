# Quick Start Guide

Get up and running with the Beast Mode AI Development Framework in under 5 minutes!

## Prerequisites

- Python 3.9 or higher
- Git
- Basic familiarity with Python

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/beast-mode-ai-framework.git
   cd beast-mode-ai-framework
   ```

2. **Run the installation script:**
   ```bash
   # On Linux/macOS
   ./install.sh
   
   # On Windows
   install.bat
   ```

3. **Verify installation:**
   ```bash
   python -c "import src.beast_mode; print('✅ Beast Mode installed successfully!')"
   ```

## Your First Beast Mode Application

Create a simple application that demonstrates the core features:

```python
# examples/quick_start/basic_example.py
from src.beast_mode.core.reflective_module import ReflectiveModule
from src.beast_mode.ai_memory_palace.context_engine import ContextEngine
import os

# Set up environment (use your own values)
os.environ.setdefault('REDIS_HOST', 'localhost')
os.environ.setdefault('REDIS_PORT', '6379')
os.environ.setdefault('REDIS_PASSWORD', '')

class QuickStartDemo(ReflectiveModule):
    """A simple demonstration of Beast Mode capabilities."""
    
    def __init__(self):
        super().__init__("QuickStartDemo")
        self.context_engine = ContextEngine()
    
    def run_demo(self):
        """Run a quick demonstration."""
        self.log_info("🚀 Starting Beast Mode Quick Start Demo")
        
        # Demonstrate AI Memory Palace
        self.log_info("📚 Testing AI Memory Palace...")
        context = {
            "project": "Beast Mode Framework",
            "purpose": "AI-powered development workflows",
            "features": ["Memory Palace", "DAG Orchestration", "ReflectiveModule"]
        }
        
        # Store and retrieve context
        self.context_engine.store_context("demo_project", context)
        retrieved = self.context_engine.get_context("demo_project")
        
        if retrieved:
            self.log_info("✅ Memory Palace working correctly")
        else:
            self.log_warning("⚠️ Memory Palace not available (Redis required)")
        
        # Demonstrate health monitoring
        self.log_info("📊 Checking system health...")
        health = self.get_health_status()
        self.log_info(f"System health: {health['status']}")
        
        self.log_info("🎉 Quick Start Demo completed successfully!")
        return True

if __name__ == "__main__":
    demo = QuickStartDemo()
    demo.run_demo()
```

## Run the Example

```bash
python examples/quick_start/basic_example.py
```

Expected output:
```
🚀 Starting Beast Mode Quick Start Demo
📚 Testing AI Memory Palace...
✅ Memory Palace working correctly
📊 Checking system health...
System health: healthy
🎉 Quick Start Demo completed successfully!
```

## Next Steps

Now that you have Beast Mode running, explore these features:

### 1. AI Memory Palace
Advanced context management and retrieval:
```bash
python examples/demos/ai_memory_palace_demo.py
```

### 2. DAG Orchestration
Complex workflow management:
```bash
python examples/demos/dag_orchestration_demo.py
```

### 3. ReflectiveModule Pattern
Self-monitoring components:
```bash
python examples/demos/reflective_module_demo.py
```

## Configuration

### Environment Variables

Create a `.env` file in your home directory:

```bash
# ~/.env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password_here

# Optional: AI service keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

### Docker Setup (Optional)

For a complete environment with Redis and monitoring:

```bash
docker-compose up -d
```

This starts:
- Redis for data storage
- Prometheus for metrics
- Grafana for dashboards

## Troubleshooting

### Common Issues

**Import Error:**
```bash
# Ensure you're in the project directory
cd beast-mode-ai-framework
python -c "import src.beast_mode"
```

**Redis Connection Error:**
```bash
# Start Redis locally
redis-server

# Or use Docker
docker run -d -p 6379:6379 redis:7-alpine
```

**Permission Error:**
```bash
# Make install script executable
chmod +x install.sh
```

### Getting Help

- 📖 [Full Documentation](../../docs/README.md)
- 🐛 [Issue Tracker](https://github.com/your-org/beast-mode-ai-framework/issues)
- 💬 [Community Discussions](https://github.com/your-org/beast-mode-ai-framework/discussions)

## What's Next?

- Explore the [API Documentation](../../docs/api/README.md)
- Read the [Usage Guide](../../docs/usage/README.md)
- Check out [Advanced Examples](../demos/README.md)
- Learn about [Contributing](../../CONTRIBUTING.md)

Welcome to Beast Mode! 🎉