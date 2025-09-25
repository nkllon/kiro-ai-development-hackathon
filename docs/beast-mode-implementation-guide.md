# Beast Mode Framework: Implementation Guide

## Overview

The Beast Mode framework implements fractal coordination patterns through systematic, PDCA-driven development. This guide provides practical instructions for deploying dual-mode governance in distributed systems.

## Core Principles

### 1. Reflective Module Pattern
All components inherit from `ReflectiveModule`:
```python
from beast_mode.core import ReflectiveModule

class MyComponent(ReflectiveModule):
    def __init__(self, config):
        super().__init__()
        self._config = config
        
    def health_check(self):
        return {"status": "healthy", "metrics": self.get_metrics()}
```

### 2. Dual-Mode Coordination
Implement both patterns in every component:

**Borg Pattern (Local Coordination)**:
```python
# Distributed consensus without central authority
async def coordinate_locally(self, peers):
    consensus = await self.redis_coordination.achieve_consensus(peers)
    return consensus.result
```

**Federation Pattern (Escalation Hierarchy)**:
```python
# Systematic escalation when local coordination fails
async def escalate_if_needed(self, task, timeout):
    if task.duration > timeout:
        await self.timeout_escalation.escalate(task)
```

## Architecture Components

### Task Queue System
```
src/beast_mode/task_queue/
├── models.py              # Data models and enums
├── state_machine.py       # Conversation and task state machines
├── persistence.py         # Multi-layered storage
├── coordination.py        # Distributed coordination
├── redis_operations.py    # Redis Streams operations
└── timeout_escalation.py  # Graduated response hierarchy
```

### Key Features

1. **Multi-Layered Persistence**
   - Hot storage: Active tasks in Redis
   - Warm storage: Recent tasks in database
   - Cold storage: Archived tasks in object storage

2. **Distributed Coordination**
   - Redis-based locking and consensus
   - CRDT conflict resolution
   - Automatic leader election

3. **Timeout Escalation**
   - Gentle reminders → Firm requests → Forceful intervention → Nuclear option
   - Configurable escalation thresholds
   - Callback-based notification system

## Quick Start

### 1. Installation
```bash
pip install beast-mode-framework
```

### 2. Basic Configuration
```python
config = {
    "redis": {"host": "localhost", "port": 6379},
    "persistence": {"hot_ttl": 3600, "warm_ttl": 86400},
    "escalation": {"levels": 4, "base_timeout": 30}
}
```

### 3. Initialize Task Queue
```python
from beast_mode.task_queue import TaskQueueManager

queue = TaskQueueManager(config)
await queue.initialize()
```

### 4. Submit Tasks
```python
task = await queue.submit_task(
    task_type="data_processing",
    payload={"input": "data.csv"},
    timeout=300
)
```

## Testing Strategy

### Unit Tests
```bash
pytest tests/unit/beast_mode/task_queue/ -v
```

### Integration Tests
```bash
pytest tests/integration/ -v
```

### Load Testing
```bash
python scripts/load_test.py --tasks=1000 --concurrency=50
```

## Monitoring and Observability

### Health Endpoints
- `/health` - Component health status
- `/ready` - Readiness for traffic
- `/metrics` - Performance metrics

### Structured Logging
```python
import structlog

logger = structlog.get_logger()
logger.info("task_submitted", task_id=task.id, correlation_id=ctx.correlation_id)
```

## Production Deployment

### Docker Configuration
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "-m", "beast_mode.task_queue.server"]
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: beast-mode-task-queue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: beast-mode-task-queue
  template:
    metadata:
      labels:
        app: beast-mode-task-queue
    spec:
      containers:
      - name: task-queue
        image: beast-mode:latest
        ports:
        - containerPort: 8080
```

## Advanced Implementation Patterns

### 1. Custom Task Types
Create domain-specific task types by extending the base task model:

```python
from beast_mode.task_queue.models import TaskBase, TaskStatus
from pydantic import Field
from typing import Dict, Any

class DataProcessingTask(TaskBase):
    """Custom task for data processing operations"""

    task_type: str = "data_processing"
    input_source: str = Field(..., description="Data source location")
    output_destination: str = Field(..., description="Output location")
    processing_options: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        schema_extra = {
            "example": {
                "input_source": "s3://bucket/data.csv",
                "output_destination": "s3://bucket/processed/",
                "processing_options": {"format": "parquet", "compression": "gzip"}
            }
        }

# Register the custom task type
from beast_mode.task_queue import TaskRegistry

@TaskRegistry.register("data_processing")
class DataProcessingHandler:
    async def execute(self, task: DataProcessingTask) -> Dict[str, Any]:
        # Implementation logic here
        return {"rows_processed": 1000, "output_size": "50MB"}
```

### 2. Advanced State Machine Patterns
Implement complex business logic with state machines:

```python
from beast_mode.task_queue.state_machine import StateMachine, State, Transition
from enum import Enum

class OrderProcessingStates(Enum):
    RECEIVED = "received"
    VALIDATED = "validated"
    PAYMENT_PENDING = "payment_pending"
    PAID = "paid"
    SHIPPING = "shipping"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderStateMachine(StateMachine):
    def __init__(self):
        super().__init__(initial_state=OrderProcessingStates.RECEIVED)

        # Define valid state transitions
        self.add_transition(
            from_state=OrderProcessingStates.RECEIVED,
            to_state=OrderProcessingStates.VALIDATED,
            condition=self.validate_order,
            action=self.send_validation_confirmation
        )

        self.add_transition(
            from_state=OrderProcessingStates.VALIDATED,
            to_state=OrderProcessingStates.PAYMENT_PENDING,
            condition=self.requires_payment,
            action=self.initiate_payment_flow
        )

    async def validate_order(self, context: Dict[str, Any]) -> bool:
        """Validate order data and inventory"""
        order_data = context.get("order_data", {})
        return await self.inventory_service.check_availability(order_data["items"])

    async def send_validation_confirmation(self, context: Dict[str, Any]) -> None:
        """Send confirmation email to customer"""
        await self.notification_service.send_email(
            template="order_validation_success",
            context=context
        )
```

### 3. Multi-Tenant Task Isolation
Implement tenant-aware task processing:

```python
from beast_mode.task_queue import TaskQueueManager
from beast_mode.core.security import TenantContext

class MultiTenantTaskQueue(TaskQueueManager):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.tenant_isolation = config.get("tenant_isolation", True)

    async def submit_task(self, task_data: Dict[str, Any], tenant_id: str) -> str:
        """Submit task with tenant context"""

        # Add tenant context to task
        task_data["tenant_id"] = tenant_id
        task_data["queue_name"] = f"tenant_{tenant_id}_tasks"

        # Apply tenant-specific resource limits
        tenant_limits = await self.get_tenant_limits(tenant_id)
        task_data["resource_limits"] = tenant_limits

        # Submit to tenant-specific queue
        return await super().submit_task(task_data)

    async def get_tenant_limits(self, tenant_id: str) -> Dict[str, Any]:
        """Get resource limits for tenant"""
        return {
            "max_memory": "1GB",
            "max_cpu": "2",
            "max_execution_time": 300,
            "priority": await self.tenant_service.get_priority(tenant_id)
        }
```

### 4. Event-Driven Architecture Integration
Connect tasks to event streams:

```python
from beast_mode.messaging import EventBus
from beast_mode.task_queue import TaskSubmitter

class EventDrivenTaskProcessor:
    def __init__(self, event_bus: EventBus, task_submitter: TaskSubmitter):
        self.event_bus = event_bus
        self.task_submitter = task_submitter

        # Register event handlers
        self.event_bus.subscribe("user.created", self.handle_user_created)
        self.event_bus.subscribe("order.placed", self.handle_order_placed)
        self.event_bus.subscribe("payment.completed", self.handle_payment_completed)

    async def handle_user_created(self, event: Dict[str, Any]) -> None:
        """Process new user registration"""
        user_data = event["payload"]

        # Submit welcome email task
        await self.task_submitter.submit_task({
            "task_type": "email_notification",
            "template": "welcome",
            "recipient": user_data["email"],
            "context": user_data,
            "priority": "high"
        })

        # Submit profile setup reminder task (delayed)
        await self.task_submitter.submit_task({
            "task_type": "delayed_notification",
            "template": "complete_profile",
            "recipient": user_data["email"],
            "delay": 86400,  # 24 hours
            "priority": "low"
        })

    async def handle_order_placed(self, event: Dict[str, Any]) -> None:
        """Process new order"""
        order_data = event["payload"]

        # Submit order processing pipeline
        pipeline_tasks = [
            {"task_type": "inventory_check", "order_id": order_data["id"]},
            {"task_type": "payment_processing", "order_id": order_data["id"]},
            {"task_type": "shipping_label", "order_id": order_data["id"]},
        ]

        await self.task_submitter.submit_pipeline(pipeline_tasks)
```

## Best Practices

### 1. Error Handling
Implement comprehensive error handling with specific recovery strategies:

```python
from beast_mode.core.exceptions import (
    RetryableError, FatalError, CircuitBreakerError
)
from beast_mode.resilience import CircuitBreaker, RetryPolicy

class RobustTaskHandler:
    def __init__(self):
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=CircuitBreakerError
        )

        self.retry_policy = RetryPolicy(
            max_attempts=3,
            backoff_strategy="exponential",
            base_delay=1.0,
            max_delay=30.0
        )

    @self.circuit_breaker.protected
    @self.retry_policy.apply
    async def execute_task(self, task: TaskBase) -> Dict[str, Any]:
        try:
            result = await self._execute_core_logic(task)
            return {"status": "success", "result": result}

        except ConnectionError as e:
            # Network issues are typically retryable
            raise RetryableError(f"Network connection failed: {e}")

        except ValueError as e:
            # Data validation errors are typically fatal
            raise FatalError(f"Invalid input data: {e}")

        except Exception as e:
            # Unknown errors should be investigated
            await self.logger.error(
                "Unexpected error in task execution",
                task_id=task.id,
                error=str(e),
                traceback=traceback.format_exc()
            )
            raise FatalError(f"Unexpected error: {e}")

    async def _execute_core_logic(self, task: TaskBase) -> Any:
        """Core task execution logic"""
        # Implementation specific to task type
        pass
```

### 2. Performance Optimization
Implement comprehensive performance monitoring and optimization:

```python
from beast_mode.monitoring import PerformanceTracker
from beast_mode.caching import CacheManager
from contextlib import asynccontextmanager

class OptimizedTaskProcessor:
    def __init__(self, config: Dict[str, Any]):
        self.performance_tracker = PerformanceTracker()
        self.cache_manager = CacheManager(config["cache"])
        self.profile_enabled = config.get("profiling", False)

    @asynccontextmanager
    async def performance_context(self, operation: str):
        """Track performance metrics for operations"""
        start_time = time.time()
        memory_start = psutil.Process().memory_info().rss

        try:
            yield
        finally:
            duration = time.time() - start_time
            memory_end = psutil.Process().memory_info().rss
            memory_delta = memory_end - memory_start

            await self.performance_tracker.record_metrics({
                "operation": operation,
                "duration": duration,
                "memory_delta": memory_delta,
                "timestamp": time.time()
            })

    async def execute_with_caching(
        self,
        task: TaskBase,
        cache_key: Optional[str] = None,
        cache_ttl: int = 3600
    ) -> Dict[str, Any]:
        """Execute task with intelligent caching"""

        if cache_key:
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result

        async with self.performance_context(f"task_{task.task_type}"):
            result = await self._execute_task(task)

        if cache_key:
            await self.cache_manager.set(cache_key, result, ttl=cache_ttl)

        return result

    async def _execute_task(self, task: TaskBase) -> Dict[str, Any]:
        """Optimized task execution with profiling"""
        if self.profile_enabled:
            import cProfile
            import pstats

            pr = cProfile.Profile()
            pr.enable()

            try:
                result = await self._core_execution(task)
            finally:
                pr.disable()

                # Save profiling data
                stats = pstats.Stats(pr)
                profile_data = stats.sort_stats('cumulative')
                await self.save_profile_data(task.id, profile_data)
        else:
            result = await self._core_execution(task)

        return result
```

### 3. Security Implementation
Implement comprehensive security measures:

```python
from beast_mode.security import (
    InputValidator, AuditLogger, AccessController
)
from cryptography.fernet import Fernet

class SecureTaskProcessor:
    def __init__(self, config: Dict[str, Any]):
        self.input_validator = InputValidator(config["validation_rules"])
        self.audit_logger = AuditLogger(config["audit"])
        self.access_controller = AccessController(config["rbac"])
        self.encryption_key = Fernet(config["encryption_key"])

    async def secure_task_execution(
        self,
        task: TaskBase,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute task with full security controls"""

        # 1. Validate all inputs
        validation_result = await self.input_validator.validate(
            task.dict(),
            schema=task.get_validation_schema()
        )
        if not validation_result.is_valid:
            await self.audit_logger.log_security_violation(
                event_type="input_validation_failed",
                user_id=user_context["user_id"],
                task_id=task.id,
                violations=validation_result.violations
            )
            raise SecurityError("Input validation failed")

        # 2. Check access permissions
        has_access = await self.access_controller.check_permission(
            user_id=user_context["user_id"],
            resource=f"task:{task.task_type}",
            action="execute"
        )
        if not has_access:
            await self.audit_logger.log_access_denied(
                user_id=user_context["user_id"],
                resource=f"task:{task.task_type}",
                action="execute"
            )
            raise PermissionError("Access denied")

        # 3. Encrypt sensitive data
        if task.contains_sensitive_data():
            task.payload = self.encrypt_sensitive_fields(task.payload)

        # 4. Execute with audit trail
        try:
            await self.audit_logger.log_task_start(task, user_context)
            result = await self._execute_validated_task(task)
            await self.audit_logger.log_task_completion(task, result, user_context)
            return result

        except Exception as e:
            await self.audit_logger.log_task_error(task, str(e), user_context)
            raise

    def encrypt_sensitive_fields(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive fields in task payload"""
        sensitive_fields = ["ssn", "credit_card", "password", "api_key"]

        for field in sensitive_fields:
            if field in payload:
                encrypted_value = self.encryption_key.encrypt(
                    str(payload[field]).encode()
                )
                payload[field] = encrypted_value.decode()

        return payload
```

## Troubleshooting

### Common Issues

**Task Queue Deadlock**:
```bash
# Check Redis coordination state
redis-cli HGETALL "beast_mode:coordination:locks"
```

**Escalation Not Triggering**:
```python
# Verify timeout configuration
logger.info("escalation_config", config=queue.escalation_config)
```

**Performance Degradation**:
```bash
# Monitor system metrics
curl http://localhost:8080/metrics
```

## Contributing

### Development Setup
```bash
git clone https://github.com/your-org/beast-mode-framework
cd beast-mode-framework
pip install -e ".[dev]"
pre-commit install
```

### Running Tests
```bash
make test
make lint
make type-check
```

### Documentation
```bash
make docs
```

## Support

- GitHub Issues: https://github.com/your-org/beast-mode-framework/issues
- Documentation: https://beast-mode-framework.readthedocs.io
- Community: https://discord.gg/ehpXzyRNkr