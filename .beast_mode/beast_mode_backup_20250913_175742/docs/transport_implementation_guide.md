# Beast Mode Transport Implementation Guide

## Overview

This guide provides comprehensive documentation for implementing custom transport layers in the Beast Mode messaging system. The pluggable transport architecture allows you to choose the best messaging backend for your specific requirements while maintaining a consistent API.

## Transport Interface

All transport implementations must inherit from `BeastModeTransport` and implement the following methods:

### Required Methods

#### `async def initialize(self, config: Dict[str, Any]) -> bool`
Initialize the transport with configuration parameters.

**Parameters:**
- `config`: Dictionary containing transport-specific configuration

**Returns:**
- `True` if initialization successful, `False` otherwise

**Example:**
```python
async def initialize(self, config: Dict[str, Any]) -> bool:
    self.redis_url = config.get('redis_url', 'redis://localhost:6379')
    self.connection_pool = redis.ConnectionPool.from_url(self.redis_url)
    return True
```

#### `async def send_message(self, message: BeastModeMessage) -> bool`
Send a message through the transport.

**Parameters:**
- `message`: BeastModeMessage instance to send

**Returns:**
- `True` if sent successfully, `False` otherwise

**Implementation Notes:**
- Handle serialization of the message
- Implement retry logic for failed sends
- Log errors appropriately

#### `async def subscribe(self, handler: Callable[[BeastModeMessage], None]) -> bool`
Subscribe to incoming messages with a handler function.

**Parameters:**
- `handler`: Function to call when messages are received

**Returns:**
- `True` if subscription successful, `False` otherwise

**Implementation Notes:**
- Support multiple handlers
- Handle deserialization of incoming messages
- Call handlers asynchronously when possible

#### `async def start_daemon(self) -> bool`
Start background daemon for message processing.

**Returns:**
- `True` if daemon started successfully, `False` otherwise

**Implementation Notes:**
- Start background tasks for message listening
- Initialize connection pools
- Set up health monitoring

#### `async def stop_daemon(self) -> None`
Stop background daemon gracefully.

**Implementation Notes:**
- Cancel background tasks
- Close connections
- Clean up resources

#### `def get_status(self) -> Dict[str, Any]`
Get current transport status and metrics.

**Returns:**
- Dictionary containing status information

**Recommended Status Fields:**
```python
{
    'transport_type': 'redis',
    'daemon_running': True,
    'connections_active': 5,
    'messages_sent': 1250,
    'messages_received': 890,
    'last_error': None,
    'uptime_seconds': 3600
}
```

#### `def get_capabilities(self) -> Dict[str, Any]`
Get transport-specific capabilities and features.

**Returns:**
- Dictionary describing transport capabilities

**Standard Capability Fields:**
```python
{
    'reliable_delivery': True,      # Guarantees message delivery
    'message_persistence': True,    # Messages survive restarts
    'shared_state': False,          # Provides shared state storage
    'scalability': 'high',          # low/moderate/high
    'operational_complexity': 'low' # low/moderate/high
}
```

## Implementation Steps

### 1. Create Transport Class

```python
from beast_mode.messaging.transport import BeastModeTransport
from beast_mode.messaging.models import BeastModeMessage

class MyTransport(BeastModeTransport):
    def __init__(self, **config):
        self.config = config
        # Initialize instance variables
    
    # Implement all required methods...
```

### 2. Register Transport

```python
from beast_mode.messaging.transport import TransportFactory

# Register your transport
TransportFactory.register_transport('my_transport', MyTransport)
```

### 3. Use Transport

```python
# Create transport instance
transport = TransportFactory.create_transport('my_transport', 
                                            connection_url='...',
                                            other_config='...')

# Initialize and use
await transport.initialize({})
await transport.start_daemon()
```

## Error Handling Patterns

### Connection Failures
```python
async def initialize(self, config: Dict[str, Any]) -> bool:
    try:
        self.connection = await create_connection(config['url'])
        return True
    except ConnectionError as e:
        logger.error(f"Failed to connect: {e}")
        return False
```

### Message Delivery Failures
```python
async def send_message(self, message: BeastModeMessage) -> bool:
    for attempt in range(self.max_retries):
        try:
            await self._send_with_timeout(message)
            return True
        except TimeoutError:
            if attempt == self.max_retries - 1:
                logger.error(f"Failed to send after {self.max_retries} attempts")
                return False
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### Handler Exceptions
```python
async def _call_handler(self, handler, message):
    try:
        if asyncio.iscoroutinefunction(handler):
            await handler(message)
        else:
            handler(message)
    except Exception as e:
        logger.error(f"Handler error for {message.type}: {e}")
        # Don't let handler errors break the transport
```

## Testing Your Transport

### Unit Tests
```python
import pytest
from your_transport import MyTransport

@pytest.mark.asyncio
async def test_transport_initialization():
    transport = MyTransport()
    result = await transport.initialize({'url': 'test://localhost'})
    assert result is True

@pytest.mark.asyncio
async def test_message_sending():
    transport = MyTransport()
    await transport.initialize({})
    
    message = BeastModeMessage(
        type="simple_message",
        source="test_agent",
        payload={"text": "test"}
    )
    
    result = await transport.send_message(message)
    assert result is True
```

### Integration Tests
```python
@pytest.mark.asyncio
async def test_end_to_end_messaging():
    transport1 = MyTransport(agent_id="sender")
    transport2 = MyTransport(agent_id="receiver")
    
    received_messages = []
    
    async def handler(message):
        received_messages.append(message)
    
    await transport2.subscribe(handler)
    await transport2.start_daemon()
    
    test_message = BeastModeMessage(
        type="simple_message",
        source="sender",
        target="receiver",
        payload={"text": "Hello!"}
    )
    
    await transport1.send_message(test_message)
    
    # Wait for message delivery
    await asyncio.sleep(0.1)
    
    assert len(received_messages) == 1
    assert received_messages[0].payload["text"] == "Hello!"
```

## Performance Considerations

### Connection Pooling
- Use connection pools for network-based transports
- Configure pool size based on expected load
- Monitor pool utilization

### Message Batching
- Consider batching small messages for efficiency
- Balance latency vs throughput requirements
- Implement configurable batch sizes

### Memory Management
- Implement message size limits
- Use streaming for large payloads
- Monitor memory usage in long-running processes

## Security Considerations

### Authentication
- Implement transport-level authentication
- Support credential rotation
- Use secure credential storage

### Encryption
- Encrypt messages in transit
- Support TLS/SSL for network transports
- Consider end-to-end encryption for sensitive data

### Authorization
- Implement access controls
- Support role-based permissions
- Audit message access

## Operational Excellence

### Monitoring
- Expose metrics via get_status()
- Implement health checks
- Monitor error rates and latencies

### Logging
- Use structured logging
- Include correlation IDs
- Log at appropriate levels

### Configuration
- Support environment-based configuration
- Validate configuration on startup
- Provide sensible defaults

## Example Implementations

See the following files for complete examples:
- `transport_examples.py` - Basic example transport
- `redis_transport.py` - Redis-based transport
- `nats_transport.py` - NATS-based transport (future)

## Troubleshooting

### Common Issues

**Transport not found**
```
ValueError: Unknown transport type: my_transport
```
Solution: Ensure transport is registered with TransportFactory

**Connection failures**
- Check network connectivity
- Verify configuration parameters
- Check authentication credentials

**Message delivery failures**
- Monitor transport status
- Check error logs
- Verify message format

**Performance issues**
- Monitor connection pool usage
- Check message sizes
- Review batching configuration

For additional support, see the Beast Mode documentation or contact the development team.