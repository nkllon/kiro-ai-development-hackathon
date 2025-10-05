# Intelligent HTTP Polling Fallback System

## Overview

The Intelligent HTTP Polling Fallback System (Task 2.2) provides a comprehensive solution for HTTP polling when WebSocket connections fail. It includes intelligent rate limiting, bot-safe headers, request deduplication, and exponential backoff strategies to avoid triggering security systems.

## Architecture

### Core Components

1. **IntelligentPoller** - Main orchestrator class
2. **RateLimiter** - Per-endpoint and global rate limiting
3. **RequestDeduplicator** - Request caching and batching
4. **BotSafeHeaders** - Bot-safe header management
5. **PollingStrategy** - Exponential backoff and jitter

### File Structure

```
src/beast_mode/observatory/polling/
├── __init__.py                 # Module exports
├── intelligent_poller.py      # Main poller class
├── rate_limiter.py           # Rate limiting logic
├── request_deduplicator.py   # Request deduplication
├── bot_safe_headers.py       # Bot-safe headers
└── polling_strategy.py       # Polling strategies

tests/unit/polling/
├── __init__.py
├── test_intelligent_poller.py
├── test_rate_limiter.py
├── test_request_deduplicator.py
└── test_polling_strategy.py
```

## Key Features

### 1. Bot-Safe Headers

The system uses carefully crafted headers that mimic legitimate browser behavior:

```python
BOT_SAFE_HEADERS = {
    "User-Agent": "Observatory-Internal/1.0 (WebSocket-Fallback)",
    "X-Observatory-Client": "internal-polling",
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json",
    "Cache-Control": "no-cache",
    "X-Polling-Reason": "websocket-fallback",
    "Connection": "keep-alive",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9"
}
```

### 2. Rate Limiting

Multi-level rate limiting with:
- **Global limits**: 60 requests/minute, 1000 requests/hour
- **Per-endpoint limits**: Reduced limits per endpoint
- **Concurrent limits**: Maximum 10 concurrent requests
- **Burst protection**: Maximum 5 requests per 10-second window

### 3. Request Deduplication

Intelligent request caching and batching:
- **Cache TTL**: 30 seconds default
- **Request batching**: 2-second window for batching
- **Deduplication**: Identical requests share responses
- **Client tracking**: Multiple clients can wait for same request

### 4. Polling Strategy

Adaptive polling with exponential backoff:
- **Base interval**: 5 seconds
- **Maximum interval**: 60 seconds
- **Exponential backoff**: 1.5x multiplier on failures
- **Jitter**: 10% randomization to prevent thundering herd
- **State management**: Normal, Backoff, Recovery, Suspended

## Usage Examples

### Basic Usage

```python
from beast_mode.observatory.polling import IntelligentPoller

# Create poller
poller = IntelligentPoller()

# Start polling
await poller.start()

# Poll single endpoint
result = await poller.poll_endpoint("https://api.example.com/data")
print(f"Success: {result.success}, Data: {result.data}")

# Start continuous polling
async def callback(endpoint, result):
    print(f"Poll result for {endpoint}: {result.success}")

await poller.start_polling("https://api.example.com/data", callback)

# Stop polling
await poller.stop()
```

### Context Manager Usage

```python
async with IntelligentPoller() as poller:
    result = await poller.poll_endpoint("https://api.example.com/data")
    # Poller automatically cleaned up
```

### Advanced Configuration

```python
from beast_mode.observatory.polling import IntelligentPoller
from beast_mode.observatory.polling.rate_limiter import RateLimitConfig
from beast_mode.observatory.polling.polling_strategy import PollingConfig

# Custom rate limiting
rate_config = RateLimitConfig(
    max_requests_per_minute=30,
    max_concurrent_requests=5,
    burst_limit=3
)

# Custom polling strategy
polling_config = PollingConfig(
    base_interval=3.0,
    max_interval=120.0,
    backoff_multiplier=2.0
)

# Create poller with custom config
poller = IntelligentPoller(
    rate_limit_config=rate_config,
    polling_config=polling_config,
    cache_ttl=60.0,
    batch_window=5.0
)
```

## Bot Protection Features

### Detection

The system automatically detects bot protection responses:
- HTTP status codes: 403, 429, 503, 1020, 1033
- Error messages containing: "bot", "captcha", "blocked", "rate limit"
- Response headers indicating bot detection

### Mitigation

When bot protection is detected:
- Automatic suspension of affected endpoints
- Exponential backoff with jitter
- Request pattern randomization
- Header sanitization

## Logging

All actions are logged in JSON format to stdout:

```json
{
  "timestamp": "2024-01-15T10:30:45.123456Z",
  "task": "2.2",
  "action": "polling_started",
  "status": "completed",
  "details": {
    "endpoint": "https://api.example.com/data",
    "active_endpoints": 1
  }
}
```

## Statistics

Comprehensive statistics tracking:

```python
stats = poller.get_stats()
print(f"Total polls: {stats['poller_stats']['total_polls']}")
print(f"Success rate: {stats['poller_stats']['successful_polls'] / stats['poller_stats']['total_polls']}")
print(f"Rate limited: {stats['poller_stats']['rate_limited_polls']}")
print(f"Bot protection events: {stats['poller_stats']['bot_protection_events']}")
```

## Testing

Run the comprehensive test suite:

```bash
# Run all polling tests
pytest tests/unit/polling/ -v

# Run specific component tests
pytest tests/unit/polling/test_rate_limiter.py -v
pytest tests/unit/polling/test_intelligent_poller.py -v
```

## Requirements Coverage

This implementation covers all specified requirements:

- **3.1**: Intelligent rate limiting with per-endpoint and global limits
- **3.2**: Bot-safe headers and request patterns
- **3.3**: Request deduplication and batching
- **3.4**: Exponential backoff with jitter
- **3.5**: Bot protection detection and mitigation
- **3.6**: Comprehensive JSON logging
- **3.7**: Statistics and monitoring
- **3.8**: Async/await support with proper resource management

## Performance Characteristics

- **Memory usage**: Minimal with automatic cleanup
- **CPU usage**: Low with efficient async operations
- **Network efficiency**: Optimized with deduplication and batching
- **Scalability**: Supports multiple concurrent endpoints
- **Reliability**: Robust error handling and recovery

## Security Considerations

- **Bot detection avoidance**: Carefully crafted headers and patterns
- **Rate limiting**: Prevents overwhelming target servers
- **Request randomization**: Avoids pattern detection
- **Error handling**: Graceful degradation on failures
- **Resource management**: Proper cleanup and memory management

## Future Enhancements

Potential improvements for future versions:
- Circuit breaker pattern for failing endpoints
- Adaptive rate limiting based on response times
- Machine learning for bot detection patterns
- Integration with monitoring systems
- Support for different HTTP methods
- WebSocket reconnection strategies