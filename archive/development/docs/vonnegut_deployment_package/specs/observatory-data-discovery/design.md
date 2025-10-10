# Design Document

## Overview

The Observatory Data Discovery system addresses the fundamental issue that while chart containers appear correctly, they lack real operational data. The unified reflective module system across Beast Mode should be generating substantial metrics, but this data isn't flowing properly to the Observatory's API endpoints.

This design focuses on creating a robust data discovery and integration pipeline that automatically finds, collects, and exposes real operational data from the Beast Mode framework's reflective modules.

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    Observatory Data Discovery                    │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Module        │  │   Data          │  │   API           │ │
│  │   Discovery     │  │   Aggregator    │  │   Integration   │ │
│  │   Engine        │  │                 │  │   Layer         │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│           │                     │                     │         │
│           ▼                     ▼                     ▼         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Reflective    │  │   Data          │  │   Observatory   │ │
│  │   Module        │  │   Pipeline      │  │   API           │ │
│  │   Registry      │  │   Validator     │  │   Endpoints     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │    Frontend Charts      │
                    │   (Existing System)     │
                    └─────────────────────────┘
```

### Data Flow Architecture

```
Reflective Modules → Module Discovery → Data Aggregation → API Integration → Frontend
       │                    │                 │               │            │
   get_metrics()      Auto-discovery    Real-time cache   Consistent API   Chart.js
   get_health()       Module registry   Data validation   JSON response    Updates
   Module info        Health tracking   Error handling    Fallback data    Real-time
```

## Components and Interfaces

### 1. Module Discovery Engine

**Purpose**: Automatically discover and catalog all reflective modules in the Beast Mode framework.

**Key Methods**:
```python
class ModuleDiscoveryEngine:
    async def discover_reflective_modules(self) -> Dict[str, ModuleInfo]
    async def validate_module_capabilities(self, module: Any) -> ModuleCapabilities
    async def refresh_module_registry(self) -> None
    def get_discovered_modules(self) -> Dict[str, ModuleInfo]
```

**Discovery Strategy**:
- Scan `src/beast_mode/` for classes inheriting from `ReflectiveModule`
- Use Python's `inspect` and `importlib` for safe module loading
- Validate that modules implement required interfaces (`get_metrics()`, `get_health_status()`)
- Handle import failures gracefully and log discovery issues

### 2. Data Aggregator

**Purpose**: Collect and aggregate real operational data from discovered modules.

**Key Methods**:
```python
class DataAggregator:
    async def collect_all_metrics(self) -> AggregatedMetrics
    async def collect_health_data(self) -> SystemHealthData
    async def collect_llm_usage_data(self) -> LLMUsageData
    def get_data_freshness(self) -> Dict[str, datetime]
```

**Data Collection Strategy**:
- Call `get_metrics()` on all discovered modules
- Aggregate health scores into system-wide health metrics
- Collect LLM usage data from cost tracker if available
- Cache data with timestamps for freshness tracking
- Handle module failures without breaking overall collection

### 3. API Integration Layer

**Purpose**: Ensure Observatory API endpoints return real operational data consistently.

**Enhanced `/api/dashboard/all-data` Endpoint**:
```python
async def consolidated_dashboard_data():
    """Enhanced endpoint with real data integration."""
    try:
        # Collect real data from all sources
        aggregated_data = await data_aggregator.collect_all_metrics()
        health_data = await data_aggregator.collect_health_data()
        llm_data = await data_aggregator.collect_llm_usage_data()
        
        return {
            "analytics": {
                "healthScore": health_data.overall_score,
                "componentCount": len(health_data.components),
                "uptime": health_data.system_uptime,
                "errorCount": health_data.total_errors,
                "warningCount": health_data.total_warnings
            },
            "costs": {
                "totalCost": llm_data.total_cost_today,
                "apiCalls": llm_data.total_calls,
                "providers": llm_data.cost_by_provider,
                "inputTokens": llm_data.total_input_tokens,
                "outputTokens": llm_data.total_output_tokens,
                "totalTokens": llm_data.total_tokens,
                "tokenRate": llm_data.tokens_per_minute
            },
            "metrics": {
                "responseTime": aggregated_data.avg_response_time,
                "errorRate": aggregated_data.error_rate_percent,
                "throughput": aggregated_data.operations_per_second,
                "memoryUsage": aggregated_data.memory_usage_mb,
                "cpuUsage": aggregated_data.cpu_usage_percent
            },
            "agents": {
                "active": aggregated_data.active_components,
                "tasks": aggregated_data.total_tasks,
                "coordination": health_data.coordination_score
            },
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "dataFreshness": data_aggregator.get_data_freshness()
        }
    except Exception as e:
        # Return structured fallback data
        return create_fallback_response(str(e))
```

### 4. Data Pipeline Validator

**Purpose**: Provide visibility into data flow and validate pipeline integrity.

**Key Methods**:
```python
class DataPipelineValidator:
    async def validate_data_sources(self) -> ValidationReport
    async def check_api_consistency(self) -> ConsistencyReport
    def log_data_flow(self, stage: str, data_count: int) -> None
    def get_pipeline_health(self) -> PipelineHealth
```

**Validation Checks**:
- Verify all expected data sources are available
- Check API endpoint response consistency
- Validate data freshness and completeness
- Monitor data collection performance
- Generate diagnostic reports for debugging

## Data Models

### AggregatedMetrics
```python
@dataclass
class AggregatedMetrics:
    timestamp: datetime
    active_components: int
    total_tasks: int
    avg_response_time: float
    error_rate_percent: float
    operations_per_second: float
    memory_usage_mb: float
    cpu_usage_percent: float
    data_sources: List[str]
```

### SystemHealthData
```python
@dataclass
class SystemHealthData:
    overall_score: float
    components: Dict[str, ComponentHealth]
    system_uptime: float
    total_errors: int
    total_warnings: int
    coordination_score: float
    last_updated: datetime
```

### LLMUsageData
```python
@dataclass
class LLMUsageData:
    total_cost_today: Decimal
    total_calls: int
    cost_by_provider: Dict[str, Decimal]
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    tokens_per_minute: float
    recent_calls: List[LLMAPICall]
    last_updated: datetime
```

## Error Handling

### Graceful Degradation Strategy

1. **Module Discovery Failures**: Continue with successfully discovered modules, log failures
2. **Data Collection Failures**: Use cached data where available, provide fallback values
3. **API Endpoint Errors**: Return structured error responses with partial data
4. **Redis Connection Issues**: Fall back to in-memory data collection
5. **Module Unresponsiveness**: Skip unresponsive modules, update health scores

### Error Response Format
```python
{
    "status": "partial_success",
    "error": "Some data sources unavailable",
    "available_data": {...},
    "missing_sources": ["cost_tracker", "analytics_engine"],
    "fallback_used": True,
    "timestamp": "2024-01-01T12:00:00Z"
}
```

## Testing Strategy

### Unit Tests
- Module discovery engine with mock modules
- Data aggregation with various data scenarios
- API endpoint responses with different data states
- Error handling for each failure mode

### Integration Tests
- End-to-end data flow from modules to API
- Real reflective module integration
- API consistency across multiple calls
- Performance under various load conditions

### Data Validation Tests
- Schema validation for all API responses
- Data freshness and consistency checks
- Fallback behavior validation
- Error response format verification

## Performance Considerations

### Data Collection Optimization
- Asynchronous module discovery and data collection
- Caching with configurable TTL (default 30 seconds)
- Batch processing for multiple module queries
- Connection pooling for database/Redis operations

### Memory Management
- Limit cached data retention (last 100 data points per metric)
- Periodic cleanup of stale module references
- Efficient data structures for aggregation
- Memory usage monitoring and alerts

### API Response Optimization
- Pre-aggregate common data combinations
- Compress large responses where appropriate
- Implement response caching for expensive operations
- Monitor and optimize slow API endpoints

## Security Considerations

### Data Access Control
- Validate module access permissions
- Sanitize data before API responses
- Log all data access attempts
- Implement rate limiting on discovery operations

### Error Information Disclosure
- Avoid exposing internal system details in error messages
- Log detailed errors internally, return sanitized messages to clients
- Validate all input parameters
- Implement proper authentication for sensitive endpoints

## Deployment Strategy

### Phased Implementation
1. **Phase 1**: Module discovery and basic data collection
2. **Phase 2**: API integration and data aggregation
3. **Phase 3**: Advanced validation and error handling
4. **Phase 4**: Performance optimization and monitoring

### Rollback Plan
- Feature flags for new data sources
- Fallback to existing API behavior if new system fails
- Database migration scripts for any schema changes
- Monitoring and alerting for data pipeline health

### Monitoring and Observability
- Metrics on data collection success rates
- API response time and error rate monitoring
- Data freshness and completeness tracking
- Module discovery and health monitoring