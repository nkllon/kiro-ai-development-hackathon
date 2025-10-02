# Node B Management System

Systematic lifecycle management, monitoring, and coordination for Node B instances within the Beast Mode decentralized AI coordination network.

## Overview

The Node B Management System provides a comprehensive framework for deploying, monitoring, and maintaining autonomous AI coordination nodes that participate in distributed task execution and network consensus through Redis pub/sub channels.

## Architecture

### Core Components

- **NodeBComponent**: Base class inheriting from ReflectiveModule for systematic observability
- **RedisConnectionManager**: Secure Redis connection management with credential handling
- **Core Interfaces**: Standardized interfaces for lifecycle, health, and network management

### Directory Structure

```
src/node_b_management/
├── __init__.py                 # Main package exports
├── README.md                   # This documentation
├── core/                       # Core interfaces and base classes
│   ├── __init__.py
│   ├── interfaces.py           # Core interfaces (INodeLifecycle, IHealthMonitoring, etc.)
│   ├── node_b_component.py     # NodeBComponent base class
│   └── redis_connection_manager.py  # Secure Redis connection management
├── lifecycle/                  # Lifecycle management components (future)
├── health/                     # Health monitoring components (future)
├── network/                    # Network communication components (future)
├── security/                   # Security management components (future)
└── coordination/               # Multi-instance coordination components (future)
```

## Quick Start

### Basic Usage

```python
import asyncio
from node_b_management import NodeBComponent

class MyNodeBManager(NodeBComponent):
    def __init__(self):
        super().__init__("my_manager", "node_1")
    
    async def example_operation(self):
        # Your Node B logic here
        self.increment_message_count("processed")
        return "Operation completed"

async def main():
    manager = MyNodeBManager()
    
    # Check health
    health = manager.get_health_status()
    print(f"Health: {health.status.value}")
    
    # Get module info
    info = manager.get_module_info()
    print(f"Module: {info['module_id']}")
    
    # Validate Beast Mode compliance
    compliance = await manager.validate_beast_mode_compliance()
    print(f"Compliance: {compliance}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Redis Configuration

Set environment variables for secure Redis connection:

```bash
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_PASSWORD=your_secure_password
export REDIS_DB=0
export REDIS_SSL=false
```

**IMPORTANT**: Never hardcode Redis passwords. Always use environment variables.

## Core Interfaces

### INodeLifecycle

Manages Node B instance lifecycle:

- `start_node(node_id, config)` - Start a Node B instance
- `stop_node(node_id, graceful)` - Stop a Node B instance
- `restart_node(node_id)` - Restart with exponential backoff
- `get_node_state(node_id)` - Get current node state
- `validate_configuration(config)` - Validate configuration

### IHealthMonitoring

Provides comprehensive health monitoring:

- `get_health_status(node_id)` - Get health metrics
- `generate_diagnostic_report(node_id)` - Generate diagnostics
- `check_redis_connectivity(node_id)` - Test Redis connection
- `monitor_performance(node_id)` - Monitor resource usage

### INetworkCommunication

Handles network communication and coordination:

- `send_message(message)` - Send network message
- `receive_messages(node_id)` - Receive pending messages
- `participate_in_consensus(node_id, proposal)` - Join consensus
- `handle_challenge_response(node_id, challenge)` - Handle challenges
- `adapt_to_topology_change(node_id, topology)` - Adapt to changes

## Beast Mode Integration

### ReflectiveModule Compliance

All components inherit from ReflectiveModule providing:

- **Health Endpoints**: `/health`, `/ready`, `/metrics`
- **Prometheus Metrics**: Automatic metrics collection
- **Structured Logging**: Correlation IDs and tracing
- **Error Handling**: Systematic error recovery
- **Graceful Degradation**: Fault tolerance

### Example Health Check

```python
# Health endpoint automatically available
curl http://localhost:8000/health

# Get detailed health status
health = component.get_health_status()
print(f"Status: {health.status.value}")
print(f"Score: {health.health_score}")
print(f"Issues: {health.issues}")
```

## Security Features

### Secure Credential Management

- Environment variable-based configuration
- No hardcoded passwords or secrets
- SSL/TLS support for Redis connections
- Automatic credential validation

### Security Validation

```python
# Validate security configuration
redis_manager = RedisConnectionManager()
connection_info = redis_manager.get_connection_info()
print(f"SSL enabled: {connection_info['ssl']}")
```

## Development Status

### ✅ Completed (Task 1)

- [x] Project structure and directory organization
- [x] Core interfaces (INodeLifecycle, IHealthMonitoring, INetworkCommunication)
- [x] NodeBComponent base class with ReflectiveModule inheritance
- [x] RedisConnectionManager with secure credential handling
- [x] Beast Mode framework integration
- [x] Basic health monitoring and metrics

### 🚧 In Progress (Future Tasks)

- [ ] NodeLifecycleManager implementation
- [ ] HealthMonitoringCoordinator implementation
- [ ] NetworkCommunicationCoordinator implementation
- [ ] SecurityConfigurationManager implementation
- [ ] MultiInstanceCoordinator implementation
- [ ] Integration with existing Node B implementations
- [ ] Comprehensive testing suite
- [ ] Operational documentation

## Requirements Mapping

This implementation addresses the following requirements from the specification:

- **Requirement 4.1, 4.2**: Secure Redis credential management via environment variables
- **Requirement 6.1, 6.2**: ReflectiveModule inheritance for systematic observability
- **Requirement 6.3**: Prometheus metrics and structured logging
- **Requirement 6.4**: Beast Mode error handling patterns
- **Requirement 6.6**: Redis coordination infrastructure

## Examples

See `examples/node_b_basic_usage.py` for a complete working example demonstrating:

- Component instantiation
- Health monitoring
- Metrics collection
- Beast Mode compliance validation
- Activity simulation

## Contributing

When extending the Node B Management System:

1. **Inherit from NodeBComponent** for all major components
2. **Follow interface contracts** defined in `core/interfaces.py`
3. **Use environment variables** for all configuration
4. **Implement proper error handling** with logging
5. **Add comprehensive tests** for new functionality
6. **Update documentation** with examples

## License

Part of the Beast Mode Framework - Kiro AI Development Hackathon submission.