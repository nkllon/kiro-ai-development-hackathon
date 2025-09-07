# Design Document

## Overview

The Beast Mode Agent Collaboration Network is a Redis-based pub/sub system that enables persistent, asynchronous communication between AI agents. The system provides message persistence, agent discovery, spore sharing, and systematic collaboration capabilities.

## Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Agent A       │    │   Redis Pub/Sub │    │   Agent B       │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Bus Client  │◄┼────┼►│beast_mode_  │◄┼────┼►│ Bus Client  │ │
│ │             │ │    │ │network      │ │    │ │             │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│ ┌─────────────┐ │    │                 │    │ ┌─────────────┐ │
│ │ Mailbox     │ │    │                 │    │ │ Mailbox     │ │
│ │ Logger      │ │    │                 │    │ │ Logger      │ │
│ └─────────────┘ │    │                 │    │ └─────────────┘ │
│ ┌─────────────┐ │    │                 │    │ ┌─────────────┐ │
│ │ Spore       │ │    │                 │    │ │ Spore       │ │
│ │ Repository  │ │    │                 │    │ │ Repository  │ │
│ └─────────────┘ │    │                 │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Architecture

#### Message Bus Layer
- **Redis Pub/Sub**: Core message transport mechanism
- **Channel**: `beast_mode_network` - single channel for all agent communication
- **Message Format**: JSON with id, type, source, target, payload, timestamp, priority

#### Agent Client Layer
- **Bus Client**: Handles connection, message sending, and receiving
- **Message Types**: Standardized enum for different communication patterns
- **Connection Management**: Auto-reconnection and health monitoring

#### Persistence Layer
- **Mailbox Logger**: Background process that logs all messages
- **Message Log**: Persistent file storage for message history
- **Spore Repository**: Local storage for received spores and methodologies

## Components and Interfaces

### BeastModeBusClient

```python
class BeastModeBusClient:
    def __init__(self, redis_url: str, capabilities: List[str])
    async def connect(self) -> bool
    async def announce_presence(self) -> None
    async def send_message(self, message_type: MessageType, payload: dict) -> None
    async def listen_for_messages(self) -> None
    async def disconnect(self) -> None
```

### MailboxLogger

```python
class MailboxLogger:
    def __init__(self, redis_url: str, log_file: str)
    async def start_logging(self) -> None
    async def log_message(self, message: BeastModeMessage) -> None
    def save_full_content(self, message: BeastModeMessage) -> str
```

### SporeManager

```python
class SporeManager:
    def __init__(self, spore_directory: str)
    def save_spore(self, spore_content: str, metadata: dict) -> str
    def load_spore(self, spore_name: str) -> dict
    def list_spores(self) -> List[dict]
    def validate_spore(self, spore_content: str) -> bool
```

## Data Models

### BeastModeMessage

```python
class BeastModeMessage(BaseModel):
    id: str                    # Unique message identifier
    type: MessageType          # Standardized message type
    source: str               # Sending agent identifier
    target: Optional[str]     # Target agent (None for broadcast)
    payload: Dict[str, Any]   # Message content and metadata
    timestamp: datetime       # Message creation time
    priority: int = 5         # Message priority (1-10)
```

### MessageType Enum

```python
class MessageType(str, Enum):
    SIMPLE_MESSAGE = "simple_message"           # Basic text communication
    PROMPT_REQUEST = "prompt_request"           # Request for processing
    PROMPT_RESPONSE = "prompt_response"         # Response to request
    AGENT_DISCOVERY = "agent_discovery"         # Presence announcement
    AGENT_RESPONSE = "agent_response"           # Discovery response
    HELP_WANTED = "help_wanted"                 # Request for assistance
    HELP_RESPONSE = "help_response"             # Offer to help
    SPORE_DELIVERY = "spore_delivery"           # Spore sharing
    SPORE_REQUEST = "spore_request"             # Request for specific spore
    TECHNICAL_EXCHANGE = "technical_exchange"   # Setup/debugging info
    SYSTEM_HEALTH = "system_health"             # Health monitoring
```

### AgentCapabilities

```python
class AgentCapabilities(BaseModel):
    agent_id: str
    capabilities: List[str]    # e.g., ["python_coding", "gcp_optimization", "cost_analysis"]
    availability: str          # "ready_for_business", "busy", "offline"
    specializations: List[str] # Specific areas of expertise
    collaboration_history: List[str]  # Previous successful collaborations
```

## Error Handling

### Connection Failures
- **Retry Logic**: Exponential backoff for Redis connection attempts
- **Graceful Degradation**: Continue operation with local logging if Redis unavailable
- **Health Monitoring**: Regular ping checks to detect connection issues

### Message Processing Errors
- **Validation Failures**: Log raw message data when parsing fails
- **Type Mismatches**: Handle unknown message types gracefully
- **Malformed Messages**: Preserve original data for debugging

### Persistence Failures
- **Disk Space**: Monitor available space for log files
- **File Permissions**: Handle write permission errors
- **Log Rotation**: Implement log rotation to prevent unbounded growth

## Testing Strategy

### Unit Tests
- Message serialization/deserialization
- Connection management
- Error handling scenarios
- Spore validation logic

### Integration Tests
- End-to-end message flow between agents
- Redis pub/sub functionality
- Persistence layer operations
- Multi-agent collaboration scenarios

### Performance Tests
- Message throughput under load
- Memory usage with large message volumes
- Connection stability over time
- Spore repository scalability

### Compatibility Tests
- Different message type handling
- Version compatibility between agents
- Cross-platform operation (macOS, Linux, Windows)
- Redis version compatibility

## Security Considerations

### Message Security
- **Content Validation**: Sanitize message payloads
- **Size Limits**: Prevent oversized messages from consuming resources
- **Rate Limiting**: Prevent message flooding attacks

### Agent Authentication
- **Agent Identity**: Verify agent identities through consistent naming
- **Capability Verification**: Validate claimed capabilities through interaction
- **Trust Networks**: Build trust through successful collaboration history

### Data Privacy
- **Message Encryption**: Consider encryption for sensitive spore content
- **Log Security**: Protect message logs from unauthorized access
- **Retention Policies**: Implement data retention and cleanup policies

## Deployment Architecture

### Single Machine Deployment
```
┌─────────────────────────────────────┐
│           macOS Host                │
│                                     │
│  ┌─────────────┐  ┌─────────────┐   │
│  │ Redis       │  │ Agent 1     │   │
│  │ localhost   │  │ Mailbox     │   │
│  │ :6379       │  │ Logger      │   │
│  └─────────────┘  └─────────────┘   │
│                   ┌─────────────┐   │
│                   │ Agent 2     │   │
│                   │ Mailbox     │   │
│                   │ Logger      │   │
│                   └─────────────┘   │
└─────────────────────────────────────┘
```

### Distributed Deployment
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Host A    │    │   Host B    │    │   Host C    │
│             │    │             │    │             │
│ ┌─────────┐ │    │ ┌─────────┐ │    │ ┌─────────┐ │
│ │ Agent 1 │ │    │ │ Agent 2 │ │    │ │ Redis   │ │
│ │         │ │    │ │         │ │    │ │ Cluster │ │
│ └─────────┘ │    │ └─────────┘ │    │ └─────────┘ │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                          │
                   Redis Pub/Sub
```

## Performance Characteristics

### Message Throughput
- **Target**: 100+ messages/second per agent
- **Latency**: <100ms message delivery
- **Scalability**: Support 10+ concurrent agents

### Storage Requirements
- **Message Logs**: ~1MB per 1000 messages
- **Spore Repository**: ~10MB per 100 spores
- **Redis Memory**: ~1MB per 10,000 queued messages

### Resource Usage
- **CPU**: Minimal overhead for message processing
- **Memory**: <50MB per agent client
- **Network**: <1KB per message average