"""WebSocket connection management for Beast Mode Observatory."""

from .connection import WebSocketConnection, ConnectionState, ConnectionStatus
from .retry_strategy import ExponentialBackoffRetry
from .health_validator import (
    WebSocketHealthValidator,
    HealthStatus,
    QualityMetrics,
    FailureIndicator,
    HealthCheckResult
)
from .endpoint_monitor import EndpointMonitor, MonitoringConfig, Alert
from .quality_metrics import (
    QualityMetricsCollector,
    MetricsSnapshot,
    MetricsAggregation,
    QualityThresholds
)
from .failure_detector import (
    FailureDetector,
    FailureSeverity,
    FailureType,
    FailureRule
)
from .exceptions import (
    WebSocketConnectionError,
    WebSocketTimeoutError,
    WebSocketAuthenticationError,
    WebSocketRateLimitError,
)

# Connection optimization components
from .connection_pool import (
    ConnectionPool,
    ConnectionPoolConfig,
    PoolStrategy,
    PoolMetrics,
)
from .message_optimizer import (
    MessageOptimizer,
    MessageOptimizerConfig,
    MessagePriority,
    BatchStrategy,
    MessageBatch,
    OptimizationMetrics,
)
from .compression_handler import (
    CompressionHandler,
    CompressionConfig,
    CompressionAlgorithm,
    SerializationFormat,
    CompressionResult,
    CompressionMetrics,
)

__all__ = [
    # Core connection management
    "WebSocketConnection",
    "ConnectionState",
    "ConnectionStatus",
    "ExponentialBackoffRetry",
    
    # Health validation system
    "WebSocketHealthValidator",
    "HealthStatus",
    "QualityMetrics",
    "FailureIndicator",
    "HealthCheckResult",
    
    # Endpoint monitoring
    "EndpointMonitor",
    "MonitoringConfig",
    "Alert",
    
    # Quality metrics
    "QualityMetricsCollector",
    "MetricsSnapshot",
    "MetricsAggregation",
    "QualityThresholds",
    
    # Failure detection
    "FailureDetector",
    "FailureSeverity",
    "FailureType",
    "FailureRule",
    
    # Exceptions
    "WebSocketConnectionError",
    "WebSocketTimeoutError",
    "WebSocketAuthenticationError",
    "WebSocketRateLimitError",
    
    # Connection optimization
    "ConnectionPool",
    "ConnectionPoolConfig",
    "PoolStrategy",
    "PoolMetrics",
    "MessageOptimizer",
    "MessageOptimizerConfig",
    "MessagePriority",
    "BatchStrategy",
    "MessageBatch",
    "OptimizationMetrics",
    "CompressionHandler",
    "CompressionConfig",
    "CompressionAlgorithm",
    "SerializationFormat",
    "CompressionResult",
    "CompressionMetrics",
]