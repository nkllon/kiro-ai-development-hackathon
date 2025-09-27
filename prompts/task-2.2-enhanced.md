# Task 2.2: Intelligent HTTP Polling Fallback System

## Ontological Context (22 Dimensions)
- **Problem Taxonomy**: Aggressive HTTP polling triggers bot protection (Error 1033)
- **Infrastructure**: HTTP fallback when WebSocket connections fail
- **Solution Architecture**: Intelligent rate-limited polling with bot-safe patterns
- **Risk Assessment**: Polling must not trigger security systems
- **Performance**: Minimize polling frequency while maintaining functionality
- **Security**: Bot-safe headers, whitelisted patterns, rate limiting
- **Cost**: Reduce bandwidth usage through intelligent polling
- **Temporal**: Exponential backoff, maximum 60s intervals

## Task Requirements
Write IntelligentPoller class with rate limiting, implement bot-safe headers and request patterns, create request deduplication and batching logic.

**Requirements Coverage**: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8

## Implementation Instructions

**CRITICAL LOGGING REQUIREMENTS:**
- Log ALL actions in JSON format to stdout
- Use format: `{"timestamp": "ISO8601", "task": "2.2", "action": "description", "status": "in_progress|completed|error", "details": {...}}`
- Log polling attempts, rate limiting decisions, bot protection events
- Final log: `{"task": "2.2", "status": "completed", "summary": "Intelligent polling implemented"}`

**File Structure to Create:**
```
src/beast_mode/observatory/polling/
├── __init__.py
├── intelligent_poller.py
├── rate_limiter.py
├── request_deduplicator.py
├── bot_safe_headers.py
└── polling_strategy.py

tests/unit/polling/
├── test_intelligent_poller.py
├── test_rate_limiter.py
├── test_request_deduplicator.py
└── test_polling_strategy.py
```

**Core Implementation:**

```python
class IntelligentPoller:
    def __init__(self):
        self.base_interval = 5.0  # 5 seconds base
        self.max_interval = 60.0  # 60 seconds max
        self.backoff_multiplier = 1.5
        self.jitter_factor = 0.1
        self.active_endpoints = set()
        self.rate_limiter = RateLimiter()
        self.deduplicator = RequestDeduplicator()
        
    async def start_polling(self, endpoint: str)
    async def stop_polling(self, endpoint: str)
    async def poll_endpoint(self, endpoint: str)
    def calculate_next_interval(self, failures: int) -> float
```

**Bot-Safe Headers:**
```python
BOT_SAFE_HEADERS = {
    "User-Agent": "Observatory-Internal/1.0 (WebSocket-Fallback)",
    "X-Observatory-Client": "internal-polling",
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json",
    "Cache-Control": "no-cache",
    "X-Polling-Reason": "websocket-fallback"
}
```

**Rate Limiting Strategy:**
- Base interval: 5 seconds
- Exponential backoff on failures
- Jitter to prevent thundering herd
- Per-endpoint rate limiting
- Global rate limiting across all endpoints

**Request Deduplication:**
- Cache recent requests by endpoint + parameters
- Batch multiple client requests
- Deduplicate identical requests within time window
- Share responses across multiple clients

Begin implementation immediately with comprehensive error handling and bot protection awareness.