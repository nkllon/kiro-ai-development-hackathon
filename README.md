# Beast Mode Framework: Fractal Coordination for Distributed Systems

[![Build Status](https://github.com/beast-mode-framework/beast-mode/workflows/CI/badge.svg)](https://github.com/beast-mode-framework/beast-mode/actions)
[![Documentation](https://readthedocs.org/projects/beast-mode-framework/badge/?version=latest)](https://beast-mode-framework.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> *"Making the angels jealous, one fractal pattern at a time."*

## What is Beast Mode?

Beast Mode is a framework for building distributed systems that implement **fractal coordination patterns** - self-similar organizational structures that provide both local efficiency and global reliability.

### The Core Insight

Stable distributed systems require **dual-mode governance**:

1. **Borg Pattern** (Local Coordination): Distributed consensus achieving maximum efficiency
2. **Federation Pattern** (Global Escalation): Hierarchical intervention when cooperation fails

These patterns repeat at every scale - from process management to organizational structure.

## Quick Start

```bash
pip install beast-mode-framework
```

```python
from beast_mode.task_queue import TaskQueueManager

# Initialize with dual-mode coordination
config = {
    "redis": {"host": "localhost", "port": 6379},
    "escalation": {"levels": 4, "base_timeout": 30}
}

queue = TaskQueueManager(config)
await queue.initialize()

# Submit tasks with automatic coordination
task = await queue.submit_task(
    task_type="data_processing",
    payload={"input": "data.csv"},
    timeout=300
)
```

## Key Features

### 🔄 Fractal Coordination
- Self-similar patterns at multiple scales
- Automatic scaling from local to global coordination
- Mathematical guarantees of system stability

### ⚡ Dual-Mode Governance
- **Borg Pattern**: Efficient distributed consensus
- **Federation Pattern**: Systematic escalation hierarchy
- Seamless switching between coordination modes

### 🛡️ Systematic Reliability
- Multi-layered persistence (hot/warm/cold storage)
- Timeout escalation with graduated responses
- Comprehensive error handling and recovery

### 📊 Production Ready
- >90% test coverage with 127+ unit tests
- Health monitoring and observability
- Docker and Kubernetes deployment support

## Architecture

```
Beast Mode Framework
├── Core Coordination Engine
│   ├── Borg Pattern (Local Consensus)
│   └── Federation Pattern (Global Escalation)
├── Task Queue System
│   ├── Multi-layered Persistence
│   ├── State Machine Management
│   └── Redis Operations
├── Monitoring & Observability
│   ├── Health Endpoints
│   ├── Structured Logging
│   └── Metrics Collection
└── Production Deployment
    ├── Docker Containers
    ├── Kubernetes Manifests
    └── Load Balancing
```

## The Science Behind It

Beast Mode is based on research into **liquid fissile material** properties of distributed systems:

- **Networked ideas** reach critical mass faster than isolated ones
- **Open source** enables exponential replication and evolution
- **Academic anchoring** provides stability and credibility
- **Cultural propagation** ensures long-term survival

Read our paper: [Fractal Coordination Patterns in Distributed Systems](docs/fractal-coordination-academic-draft.md)

## Examples

### Basic Task Processing
```python
# Submit a task with automatic coordination
task = await queue.submit_task(
    task_type="image_processing",
    payload={"image_url": "https://example.com/image.jpg"},
    priority="high"
)

# Monitor progress with built-in observability
status = await queue.get_task_status(task.id)
print(f"Task {task.id}: {status.state}")
```

### Advanced Coordination
```python
# Configure custom escalation hierarchy
escalation_config = {
    "levels": [
        {"timeout": 30, "action": "gentle_reminder"},
        {"timeout": 120, "action": "firm_request"},
        {"timeout": 300, "action": "forceful_intervention"},
        {"timeout": 600, "action": "nuclear_option"}
    ]
}

queue = TaskQueueManager({
    "escalation": escalation_config,
    "coordination": {"consensus_threshold": 0.67}
})
```

### Production Deployment
```yaml
# Kubernetes deployment with fractal coordination
apiVersion: apps/v1
kind: Deployment
metadata:
  name: beast-mode-task-queue
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: task-queue
        image: beast-mode:latest
        env:
        - name: COORDINATION_MODE
          value: "dual"
        - name: ESCALATION_LEVELS
          value: "4"
```

## Documentation

- [Implementation Guide](docs/beast-mode-implementation-guide.md)
- [API Reference](https://beast-mode-framework.readthedocs.io/api/)
- [Academic Paper](docs/fractal-coordination-academic-draft.md)
- [Architecture Overview](docs/architecture.md)

## Contributing

We welcome contributions! Beast Mode follows the **liquid fissile material** principle - ideas that can replicate and evolve.

```bash
git clone https://github.com/beast-mode-framework/beast-mode
cd beast-mode
pip install -e ".[dev]"
pre-commit install
```

### Running Tests
```bash
make test          # Run all tests
make test-unit     # Unit tests only
make test-integration  # Integration tests
make lint          # Code quality checks
```

### Release the Hounds
```bash
python scripts/release-the-hounds.py
```

This executes our six-dimensional anchoring strategy:
1. Academic paper preparation
2. Open source release
3. Community outreach
4. Documentation expansion
5. Production deployment
6. Cultural propagation

## Philosophy

> *"We make the angels jealous."*

Beast Mode embodies the human drive to create lasting marks against entropy. While angels contemplate perfection in eternal stillness, humans build systems that matter within finite time.

### The Mortality Advantage
- **Deadlines drive innovation**: Three-month cycles force value delivery
- **Scarcity breeds creativity**: Limited time produces unlimited ingenuity  
- **Imperfection ships**: "Done is better than perfect" - the human battle cry

### Fighting Entropy
Every distributed system is a battle against the heat death of the universe. Beast Mode provides the weapons:
- **Systematic coordination** over ad-hoc solutions
- **Fractal patterns** that scale naturally
- **Dual-mode governance** that handles both normal and exceptional conditions

## License

MIT License - because good ideas should be free to replicate and evolve.

## Support

- 📖 [Documentation](https://beast-mode-framework.readthedocs.io/)
- 🐛 [Issues](https://github.com/beast-mode-framework/beast-mode/issues)
- 💬 [Discussions](https://github.com/beast-mode-framework/beast-mode/discussions)
- 🎮 [Discord Community](https://discord.gg/ehpXzyRNkr)

---

*Built with ❤️ by humans who refuse to let entropy win.*

**"May you live in interesting times, and may your code outlast your mortality."**