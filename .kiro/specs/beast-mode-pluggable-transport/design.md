# Design Document

## Overview

The Beast Mode Pluggable Transport Architecture transforms our current Redis-based messaging implementation into a flexible, extensible system that separates transport concerns from domain logic. The design preserves all existing functionality while enabling future transport alternatives through a clean abstraction layer. Redis is repositioned as the shared runtime model, providing fast collaborative state regardless of transport choice.

## Architecture

### Core Design Principles

**Separation of Concerns**: Transport layer is completely separated from Beast Mode domain logic
**Backward Compatibility**: All existing functionality preserved without changes
**Hybrid Architecture**: Redis provides shared state, pluggable transports handle messaging
**Incremental Migration**: Each refactor step maintains system stability
**Future Extensibility**: New transports can be added without affecting existing code

### System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Beast Mode Client                           │
├─────────────────────────────────────────────────────────────────────┤
│                     Domain Logic Layer                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │ Agent Registry  │  │ Spore Manager   │  │ Collaboration   │    │
│  │ & Discovery     │  │ & Replication   │  │ Protocols       │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
├─────────────────────────────────────────────────────────────────────┤
│                    Transport Abstraction                           │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              BeastModeTransport Interface                   │   │
│  │  • send_message()    • subscribe()    • start_daemon()     │   │
│  │  • get_status()      • stop_daemon()  • initialize()      │   │
│  └─────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────┤
│                    Transport Implementations                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │ RedisTransport  │  │ NATSTransport   │  │ KafkaTransport  │    │
│  │ (Our Current)   │  │ (Battle-tested) │  │ (High-scale)    │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
├─────────────────────────────────────────────────────────────────────┤
│                    Redis Shared Runtime Model                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │ Agent State     │  │ Spore Storage   │  │ Collaboration   │    │
│  │ & Capabilities  │  │ & Metadata      │  │ Sessions        │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### Transport Abstraction Layer

#### BeastModeTransport Interface
```python
from abc import ABC, abstractmethod
from typing import Callable, Dict, Any, Optional
from .models import BeastModeMessage

class BeastModeTransport(ABC):
    """Abstract base class for Beast Mode transport implementations"""
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the transport with configuration"""
        
    @abstractmethod
    async def send_message(self, message: BeastModeMessage) -> bool:
        """Send a message through this transport"""
        
    @abstractmethod
    async def subscribe(self, handler: Callable[[BeastModeMessage], None]) -> bool:
        """Subscribe to messages with the provided handler"""
        
    @abstractmethod
    async def start_daemon(self) -> bool:
        """Start background daemon for message processing"""
        
    @abstractmethod
    async def stop_daemon(self) -> None:
        """Stop background daemon gracefully"""
        
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get current transport status and metrics"""
        
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Get transport-specific capabilities and features"""
```

#### Transport Factory
```python
class TransportFactory:
    """Factory for creating transport instances"""
    
    _transports = {
        'redis': RedisTransport,
        'nats': NATSTransport,
        'kafka': KafkaTransport,
    }
    
    @classmethod
    def create_transport(cls, transport_type: str, **config) -> BeastModeTransport:
        """Create a transport instance of the specified type"""
        if transport_type not in cls._transports:
            raise ValueError(f"Unknown transport type: {transport_type}")
        
        return cls._transports[transport_type](**config)
    
    @classmethod
    def register_transport(cls, name: str, transport_class: type):
        """Register a new transport implementation"""
        cls._transports[name] = transport_class
```

### Redis Shared Runtime Model

#### Shared State Manager
```python
class BeastModeSharedState:
    """Manages shared state in Redis regardless of transport choice"""
    
    def __init__(self, redis_config: Dict[str, Any]):
        self.redis_client = redis.from_url(redis_config.get('url', 'redis://localhost:6379'))
        self.key_prefix = redis_config.get('key_prefix', 'beast_mode')
    
    async def update_agent_state(self, agent_id: str, state: Dict[str, Any]):
        """Update agent state in shared model"""
        key = f"{self.key_prefix}:agents:{agent_id}"
        await self.redis_client.hset(key, mapping=state)
    
    async def get_agent_state(self, agent_id: str) -> Dict[str, Any]:
        """Get agent state from shared model"""
        key = f"{self.key_prefix}:agents:{agent_id}"
        return await self.redis_client.hgetall(key)
    
    async def store_spore(self, spore_id: str, spore_data: Dict[str, Any]):
        """Store spore in shared model"""
        key = f"{self.key_prefix}:spores:{spore_id}"
        await self.redis_client.hset(key, mapping=spore_data)
    
    async def get_active_agents(self) -> List[str]:
        """Get list of currently active agents"""
        pattern = f"{self.key_prefix}:agents:*"
        keys = await self.redis_client.keys(pattern)
        return [key.split(':')[-1] for key in keys]
```

### Transport Implementations

#### Redis Transport (Existing Implementation Wrapped)
```python
class RedisTransport(BeastModeTransport):
    """Redis-based transport implementation (wraps existing code)"""
    
    def __init__(self, **config):
        self.daemon = BeastModeDaemon(**config)  # Our existing implementation
        self.config = config
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize Redis transport"""
        return await self.daemon.initialize()
    
    async def send_message(self, message: BeastModeMessage) -> bool:
        """Send message via Redis"""
        self.daemon.send_message(message)
        return True
    
    async def subscribe(self, handler: Callable[[BeastModeMessage], None]) -> bool:
        """Subscribe to Redis messages"""
        return await self.daemon.subscribe(handler)
    
    async def start_daemon(self) -> bool:
        """Start Redis daemon"""
        return self.daemon.start_daemon()
    
    async def stop_daemon(self) -> None:
        """Stop Redis daemon"""
        self.daemon.stop_daemon()
    
    def get_status(self) -> Dict[str, Any]:
        """Get Redis transport status"""
        return self.daemon.get_status()
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get Redis transport capabilities"""
        return {
            'reliable_delivery': False,
            'message_persistence': True,
            'shared_state': True,
            'scalability': 'moderate',
            'operational_complexity': 'low'
        }
```

#### NATS Transport (Future Implementation)
```python
class NATSTransport(BeastModeTransport):
    """NATS-based transport implementation"""
    
    def __init__(self, **config):
        self.nats_client = None
        self.config = config
        self.daemon_task = None
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize NATS connection"""
        import nats
        self.nats_client = await nats.connect(config.get('servers', ['nats://localhost:4222']))
        return True
    
    async def send_message(self, message: BeastModeMessage) -> bool:
        """Send message via NATS"""
        subject = f"beast_mode.{message.type}"
        data = message.model_dump_json().encode()
        await self.nats_client.publish(subject, data)
        return True
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get NATS transport capabilities"""
        return {
            'reliable_delivery': True,
            'message_persistence': True,
            'shared_state': False,
            'scalability': 'high',
            'operational_complexity': 'low'
        }
```

### Unified Client Interface

#### Beast Mode Client
```python
class BeastModeClient:
    """Unified client interface with pluggable transport"""
    
    def __init__(
        self, 
        agent_id: str, 
        transport_type: str = 'redis',
        transport_config: Optional[Dict[str, Any]] = None,
        redis_config: Optional[Dict[str, Any]] = None
    ):
        self.agent_id = agent_id
        
        # Create transport
        self.transport = TransportFactory.create_transport(
            transport_type, 
            agent_id=agent_id,
            **(transport_config or {})
        )
        
        # Create shared state manager
        self.shared_state = BeastModeSharedState(redis_config or {})
        
        # Domain logic components
        self.agent_registry = AgentRegistry(self.shared_state)
        self.spore_manager = SporeManager(self.shared_state)
        self.collaboration = CollaborationManager(self.shared_state)
    
    async def start(self) -> bool:
        """Start the Beast Mode client"""
        # Initialize transport
        if not await self.transport.initialize({}):
            return False
        
        # Start daemon
        if not await self.transport.start_daemon():
            return False
        
        # Register message handlers
        await self.transport.subscribe(self._handle_message)
        
        # Announce presence in shared state
        await self.shared_state.update_agent_state(self.agent_id, {
            'status': 'online',
            'transport': type(self.transport).__name__,
            'capabilities': self.get_capabilities()
        })
        
        return True
    
    async def send_message(self, message: BeastModeMessage):
        """Send message via transport and update shared state"""
        # Send via transport
        await self.transport.send_message(message)
        
        # Update shared state
        await self.shared_state.update_agent_state(self.agent_id, {
            'last_activity': datetime.now().isoformat(),
            'messages_sent': await self._increment_counter('messages_sent')
        })
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive client status"""
        return {
            'agent_id': self.agent_id,
            'transport': self.transport.get_status(),
            'shared_state': 'connected',  # Redis connection status
            'capabilities': self.get_capabilities()
        }
```

## Data Models

### Transport Configuration
```python
@dataclass
class TransportConfig:
    """Configuration for transport implementations"""
    transport_type: str = 'redis'
    connection_params: Dict[str, Any] = field(default_factory=dict)
    daemon_config: Dict[str, Any] = field(default_factory=dict)
    retry_config: Dict[str, Any] = field(default_factory=dict)
```

### Shared State Schema
```python
# Redis key patterns for shared state
AGENT_STATE_KEY = "beast_mode:agents:{agent_id}"
SPORE_KEY = "beast_mode:spores:{spore_id}"
SESSION_KEY = "beast_mode:sessions:{session_id}"
METRICS_KEY = "beast_mode:metrics:{metric_type}"

# Agent state structure
{
    "status": "online|offline|busy",
    "capabilities": ["spec_development", "database_optimization"],
    "transport": "RedisTransport|NATSTransport|KafkaTransport",
    "last_seen": "2025-01-07T10:30:00Z",
    "specialization": "HotRod|TiDB|...",
    "performance_metrics": {
        "messages_sent": 1250,
        "messages_received": 890,
        "collaboration_sessions": 5
    }
}
```

## Error Handling

### Transport Error Handling
- **Connection Failures**: Automatic retry with exponential backoff
- **Message Delivery Failures**: Transport-specific retry strategies
- **Daemon Crashes**: Automatic restart with state recovery
- **Configuration Errors**: Clear error messages with configuration validation

### Shared State Error Handling
- **Redis Connection Loss**: Graceful degradation with local caching
- **State Synchronization Issues**: Conflict resolution strategies
- **Data Corruption**: Validation and recovery mechanisms
- **Performance Degradation**: Monitoring and alerting

## Testing Strategy

### Transport Interface Testing
- **Abstract Interface Compliance**: Verify all transports implement the interface correctly
- **Behavioral Consistency**: Ensure all transports provide equivalent functionality
- **Error Handling**: Test failure scenarios across all transport implementations
- **Performance Characteristics**: Benchmark different transports under various loads

### Integration Testing
- **Cross-Transport Communication**: Verify agents using different transports can communicate
- **Shared State Consistency**: Test that Redis state remains consistent across transports
- **Migration Testing**: Validate smooth transitions between transport implementations
- **Backward Compatibility**: Ensure existing code works without modification

### Regression Testing
- **Existing Functionality**: All current features must work identically
- **Performance Regression**: No performance degradation in default configuration
- **API Compatibility**: All existing APIs must remain unchanged
- **Configuration Compatibility**: Existing configuration files must work

## Implementation Notes

### Migration Strategy
1. **Phase 1**: Extract transport interface without changing behavior
2. **Phase 2**: Wrap existing Redis implementation as RedisTransport
3. **Phase 3**: Verify all existing functionality works identically
4. **Phase 4**: Add alternative transport implementations
5. **Phase 5**: Add transport selection configuration

### Performance Considerations
- **Redis Shared State**: Optimized for fast access patterns
- **Transport Selection**: Choose based on reliability vs performance requirements
- **Hybrid Benefits**: Fast shared state + reliable messaging
- **Monitoring**: Comprehensive metrics for both transport and shared state

### Operational Excellence
- **Unified Monitoring**: Single dashboard for all transport types
- **Debugging Tools**: Clear separation between transport and domain issues
- **Configuration Management**: Simple transport selection and configuration
- **Documentation**: Comprehensive guides for each transport implementation