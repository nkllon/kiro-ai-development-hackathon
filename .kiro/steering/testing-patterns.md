---
inclusion: always
---

# Testing Patterns - Avoiding Common Pitfalls

## Core Principle

**"Test efficiently by mocking interfaces, not implementations. When testing CLI scripts or thin layers, mock the service layer to avoid initialization overhead and blocking."**

## Critical Pattern: ReflectiveModule Testing

### ⚠️ THE BLOCKING PROBLEM

**DO NOT instantiate `ReflectiveModule` subclasses in test fixtures** unless you are specifically testing the module's own methods.

```python
# ❌ WRONG - This will block async tests
@pytest.fixture
def mailbox_service(mock_redis):
    config = RedisConfig(host="localhost", port=6379)
    service = RedisMailboxService(agent_id="test-agent", redis_config=config)
    service.redis = mock_redis
    return service  # ← Triggers ReflectiveModule.__init__(), can block
```

**Why it blocks:**
- `ReflectiveModule.__init__()` may initialize monitoring, metrics, registration
- This initialization can trigger async operations or blocking calls
- Async tests hang waiting for initialization to complete

### ✅ THE SOLUTION - Mock the Interface

```python
# ✅ CORRECT - Mock the interface, not the implementation
@pytest.fixture
def mailbox_service(mock_redis):
    service = MagicMock()
    service.agent_id = "test-agent"
    service.inbox_stream = "beast:mailbox:test-agent:in"
    service.redis = mock_redis
    return service  # ← No initialization, just attributes
```

**Benefits:**
- No blocking initialization
- Tests run in ~0.1s instead of timing out
- Focus on testing the function logic, not the service internals
- Clear, minimal setup

**Example:** See `tests/unit/beast_mode/messaging/test_mailbox_cli.py:L41-48`

## Decision Tree: When to Mock vs Instantiate

```
Testing a CLI script that calls service methods?
├─ Mock the service interface (MagicMock with attributes)
│  Example: Testing run_mailbox_service.py
│
Testing service business logic?
├─ Mock external dependencies, instantiate the service
│  Example: Testing RedisMailboxService.send_message()
│
Testing ReflectiveModule features (health, metrics)?
└─ Instantiate in a controlled async context
   Example: Testing module health_check()
```

## Async Testing Best Practices

### 1. Quick Smoke Test Before Full Suite

When writing async tests for new functionality:

```bash
# Run one test with timeout to verify non-blocking
timeout 10 pytest tests/path/test_new.py::TestClass::test_first -v
```

If this times out, you have a blocking issue. Fix before writing more tests.

### 2. Use pytest-asyncio Correctly

```python
# ✅ Correct async test setup
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result == expected

# ✅ Async fixtures
@pytest.fixture
async def async_resource():
    resource = await create_resource()
    yield resource
    await resource.cleanup()
```

### 3. Mock Async Methods with AsyncMock

```python
from unittest.mock import AsyncMock

# ✅ Mock async methods properly
mock_client = AsyncMock()
mock_client.xrevrange = AsyncMock(return_value=[])
mock_client.xack = AsyncMock(return_value=1)
```

**Never use** `MagicMock()` for async methods - they won't be awaitable.

## CLI Testing Patterns

### Pattern: Testing CLI Functions That Use Services

For scripts in `scripts/` that use service classes:

```python
# The function we're testing (from scripts/run_mailbox_service.py)
async def _fetch_latest_messages(
    service: RedisMailboxService,
    count: int,
    ack: bool = False,
    trim: bool = False,
) -> None:
    # Function uses service.redis.client, service.inbox_stream, etc.
    pass

# ✅ Test by mocking the service interface
@pytest.mark.asyncio
async def test_fetch_latest_messages(mock_service, mock_redis_client):
    mock_redis_client.xrevrange.return_value = [
        (b"msg-id", {b"sender": b"alice", b"payload": b'{"text":"hi"}'})
    ]
    
    from scripts.run_mailbox_service import _fetch_latest_messages
    
    await _fetch_latest_messages(mock_service, count=1, ack=False, trim=False)
    
    # Verify the function called Redis correctly
    mock_redis_client.xrevrange.assert_called_once()
    assert mock_redis_client.xrevrange.call_args[1]["count"] == 1
```

### Pattern: Testing CLI Argument Parsing

```python
# Test argument parsing separately from business logic
def test_parse_args_with_ack_flag():
    from scripts.run_mailbox_service import parse_args
    
    args = parse_args(['test-agent', '--latest', '--ack'])
    
    assert args.agent_id == 'test-agent'
    assert args.latest is True
    assert args.ack is True
```

## Common Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Over-Integration in Unit Tests

```python
# ❌ DON'T: Call real Redis, real files, real network
@pytest.mark.asyncio
async def test_mailbox_service():
    service = RedisMailboxService(
        agent_id="test",
        redis_config=RedisConfig(host="localhost", port=6379)
    )
    await service.start()  # ← Requires real Redis
    # Test logic...
```

**Why it's bad:**
- Slow (network calls)
- Brittle (requires Redis to be running)
- Not a unit test (it's integration)

### ❌ Anti-Pattern 2: Mocking Too Much

```python
# ❌ DON'T: Mock the function you're trying to test
@patch('scripts.run_mailbox_service._fetch_latest_messages')
def test_fetch_latest_messages(mock_fetch):
    mock_fetch.return_value = None
    # This doesn't test anything!
```

### ❌ Anti-Pattern 3: Ignoring Blocking Tests

```python
# ❌ DON'T: Let tests run indefinitely
pytest tests/  # If a test blocks, investigate immediately!
```

**Always use timeouts during development:**
```bash
timeout 30 pytest tests/  # Fail fast if blocking
```

## Fixture Organization

### Layered Fixtures

```python
# Layer 1: Mock external clients
@pytest.fixture
def mock_redis_client():
    client = AsyncMock()
    client.xrevrange = AsyncMock(return_value=[])
    client.xack = AsyncMock(return_value=0)
    return client

# Layer 2: Mock foundation/connection layer
@pytest.fixture
def mock_redis_foundation(mock_redis_client):
    foundation = AsyncMock()
    foundation.initialize = AsyncMock(return_value=True)
    foundation.shutdown = AsyncMock()
    foundation.client = mock_redis_client
    return foundation

# Layer 3: Mock service interface
@pytest.fixture
def mock_service(mock_redis_foundation):
    service = MagicMock()
    service.agent_id = "test-agent"
    service.redis = mock_redis_foundation
    return service
```

**Benefits:**
- Composable fixtures
- Clear dependency hierarchy
- Each layer testable independently

## Test Organization

### Class-Based Organization

Group related tests in classes for clarity:

```python
class TestMailboxMessageDecoding:
    """Test message payload decoding with various field types."""
    
    def test_from_redis_fields_with_bytes(self): ...
    def test_from_redis_fields_with_strings(self): ...
    def test_from_redis_fields_with_mixed_types(self): ...

class TestLatestReadOnlyMode:
    """Test --latest read-only mode without destructive operations."""
    
    @pytest.mark.asyncio
    async def test_fetch_latest_no_messages(self): ...
    
    @pytest.mark.asyncio
    async def test_fetch_latest_single_message(self): ...

class TestErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.mark.asyncio
    async def test_redis_initialization_failure(self): ...
```

**Benefits:**
- Clear test organization
- Easy to run specific test categories
- Better test discovery and reporting

## Coverage Goals

### Per Module Coverage Targets

- **CLI scripts**: 55%+ (focus on main logic paths)
- **Service classes**: 80%+ (more comprehensive)
- **Core modules**: 90%+ (critical infrastructure)

### Running Coverage

```bash
# Test with coverage report
pytest tests/unit/path/test_module.py \
  --cov=scripts.module \
  --cov=src.package.module \
  --cov-report=term-missing

# Fail if coverage too low
pytest tests/ --cov=src --cov-report=term --cov-fail-under=90
```

## Debugging Blocked Tests

If a test blocks:

1. **Add timeout and run one test:**
   ```bash
   timeout 10 pytest tests/path/test_file.py::test_name -v -s
   ```

2. **Check for:**
   - ReflectiveModule instantiation
   - Real network/file operations
   - Unmocked async methods
   - Infinite loops in mocked methods

3. **Verify async mocking:**
   ```python
   # Check if async methods are mocked correctly
   assert isinstance(mock.method, AsyncMock)
   ```

4. **Add debug output:**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   # Run test to see where it blocks
   ```

## Real-World Example: Mailbox CLI Tests

**Situation:** Need to test `scripts/run_mailbox_service.py` with new `--ack` and `--trim` flags.

**Initial attempt (BLOCKED):**
```python
@pytest.fixture
def mailbox_service(mock_redis_foundation):
    config = RedisConfig(host="localhost", port=6379)
    service = RedisMailboxService(agent_id="test-agent", redis_config=config)
    service.redis = mock_redis_foundation
    return service  # ← Tests hung here
```

**Solution (WORKS):**
```python
@pytest.fixture
def mailbox_service(mock_redis_foundation):
    service = MagicMock()
    service.agent_id = "test-agent"
    service.inbox_stream = "beast:mailbox:test-agent:in"
    service.redis = mock_redis_foundation
    return service  # ← All 21 tests pass in 0.11s
```

**Lesson:** When testing CLI logic, you don't need real service objects—just their interface.

## Quick Reference

### Testing Checklist

Before writing tests:
- [ ] Identify what you're testing (CLI? Service? Core logic?)
- [ ] Choose appropriate mocking level (interface vs implementation)
- [ ] Check if target uses ReflectiveModule (if yes → mock interface)
- [ ] Write one test first, verify it doesn't block
- [ ] Use AsyncMock for async methods
- [ ] Organize tests in classes by functionality
- [ ] Aim for appropriate coverage (55%+ CLI, 90%+ core)

### Common Mock Patterns

```python
# Mock Redis client
mock_redis = AsyncMock()
mock_redis.xrevrange = AsyncMock(return_value=[...])

# Mock service interface
mock_service = MagicMock()
mock_service.attribute = "value"

# Mock async function
mock_func = AsyncMock(return_value="result")

# Mock exception
mock_method.side_effect = Exception("error message")
```

## Additional Resources

- **Example Test Suite:** `tests/unit/beast_mode/messaging/test_mailbox_cli.py`
- **ReflectiveModule Docs:** `src/rm_ddd/core/unified_reflective_module.py`
- **Async Testing:** `pytest-asyncio` documentation
- **Coverage Reports:** Run `make dev-test` for project-wide coverage

---

**Remember:** The agent you save in the future could be you. Write tests that are clear, fast, and maintainable.


