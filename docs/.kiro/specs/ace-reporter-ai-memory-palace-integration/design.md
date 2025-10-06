# Design Document

## Overview

Design the ACE Reporter AI Memory Palace integration as a brownfield enhancement to existing operational systems. The integration will enhance the current ACE Reporter (StatusAnnouncer) with BeastlyModule capabilities, AI Memory Palace context awareness, and robust multi-channel delivery while maintaining zero downtime for the running Observatory Dashboard at https://observatory.nkllon.com.

## Architecture

### Current Operational State (As-Built)
```
Observatory Ecosystem (OPERATIONAL - DO NOT DISRUPT)
├── Observatory Dashboard - https://observatory.nkllon.com (✅ LIVE)
│   ├── Activity Feed - Real-time observation display
│   ├── Performance Charts - System metrics visualization  
│   ├── WebSocket Handlers - Live update delivery
│   └── Correlation Engine - Event linking and analysis
├── ACE Reporter (StatusAnnouncer) - ReflectiveModule Layer 2
│   ├── Status broadcasting via emit_observation()
│   ├── Spec completion tracking
│   ├── System health announcements
│   └── Direct HTTP broadcast fallback
├── AI Memory Palace - BeastlyModule Layer 3 (✅ OPERATIONAL)
│   ├── ContextManager - Project context awareness
│   ├── ContextRegistry - Session and project storage
│   ├── Multi-project support - Active session management
│   └── Spec integration - Progress tracking capabilities
└── Directus CMS - Modern Docker setup (✅ OPERATIONAL)
    ├── Content management interface
    ├── Persistent storage collections
    ├── Web-based data access
    └── Synchronization infrastructure
```

### Target Enhanced State (Brownfield Integration)
```
Enhanced ACE Reporter Ecosystem (ZERO DOWNTIME UPGRADE)
├── Observatory Dashboard - https://observatory.nkllon.com (✅ MAINTAINED)
│   ├── Enhanced Activity Feed - Context-aware observations
│   ├── Project-specific filtering - AI Memory Palace integration
│   ├── Multi-channel delivery confirmation - Reliability metrics
│   └── Real-time correlation - Cross-system event linking
├── Enhanced ACE Reporter - BeastlyModule Layer 3 (🎯 UPGRADING)
│   ├── BeastlyModule Migration - Enhanced observability
│   ├── AI Memory Palace Integration - Context-aware reporting
│   ├── Multi-channel Delivery - WebSocket + HTTP + Directus
│   ├── Automatic Spec Tracking - Progress detection
│   └── Performance Metrics - Prometheus + Jaeger tracing
├── AI Memory Palace Integration Layer (🎯 NEW)
│   ├── Context Provider - Current project awareness
│   ├── Spec Progress Monitor - Automatic task tracking
│   ├── Multi-project Coordinator - Session-aware reporting
│   └── Event Correlation - Cross-system observation linking
└── Directus Persistence Layer (🎯 ENHANCED)
    ├── Observation History - Searchable broadcast archive
    ├── Context Correlation - AI Memory Palace data linking
    ├── Performance Analytics - Historical trend analysis
    └── Multi-project Organization - Project-based data views
```

## Components and Interfaces

### Enhanced ACE Reporter (BeastlyModule Migration)
```python
class EnhancedACEReporter(BeastlyModule):
    """Enhanced ACE Reporter with AI Memory Palace integration and multi-channel delivery"""
    
    def __init__(self, ai_memory_palace: AIMemoryPalace, directus_client: DirectusClient):
        super().__init__()
        self.module_id = "enhanced_ace_reporter"
        self.ai_memory_palace = ai_memory_palace
        self.directus_client = directus_client
        self.delivery_channels = self._initialize_delivery_channels()
        
        # Inherits from BeastlyModule:
        # - Prometheus metrics (broadcast_success_rate, delivery_latency)
        # - Jaeger tracing (observation_broadcast spans)
        # - Health endpoints (/health, /ready, /metrics)
        # - Graceful degradation capabilities
    
    def broadcast_observation(self, observation: Observation) -> DeliveryResult:
        """Enhanced broadcast with multi-channel delivery and context awareness"""
        with self.trace_operation("observation_broadcast") as trace:
            # Get current project context from AI Memory Palace
            context = self._get_current_context()
            enhanced_observation = self._enhance_with_context(observation, context)
            
            # Multi-channel delivery with confirmation
            delivery_results = []
            for channel in self.delivery_channels:
                result = self._deliver_to_channel(channel, enhanced_observation)
                delivery_results.append(result)
                
            # Store in Directus for persistence
            self._store_in_directus(enhanced_observation, delivery_results)
            
            return self._aggregate_delivery_results(delivery_results)
    
    def _get_current_context(self) -> ProjectContext:
        """Get current project context from AI Memory Palace"""
        try:
            return self.ai_memory_palace.context_manager.get_current_context()
        except Exception as e:
            self.logger.warning(f"Failed to get AI Memory Palace context: {e}")
            return ProjectContext.default()
```

### AI Memory Palace Integration Layer
```python
class AIMemoryPalaceIntegration(BeastlyModule):
    """Integration layer for AI Memory Palace context awareness"""
    
    def __init__(self, context_manager: ContextManager):
        super().__init__()
        self.context_manager = context_manager
        self.spec_monitor = SpecProgressMonitor(context_manager)
    
    def get_current_project_context(self) -> ProjectContext:
        """Get current project context for ACE Reporter"""
        with self.trace_operation("get_project_context") as trace:
            active_session = self.context_manager.get_active_session()
            if active_session:
                return ProjectContext(
                    project_id=active_session.project_id,
                    session_id=active_session.session_id,
                    current_spec=active_session.current_spec,
                    progress_state=active_session.progress_state
                )
            return ProjectContext.default()
    
    def monitor_spec_progress(self, spec_name: str) -> SpecProgress:
        """Monitor spec progress for automatic reporting"""
        return self.spec_monitor.get_progress(spec_name)
    
    def correlate_observations(self, observation: Observation) -> List[CorrelatedEvent]:
        """Correlate observations with AI Memory Palace events"""
        with self.trace_operation("observation_correlation") as trace:
            return self.context_manager.find_related_events(
                observation.timestamp,
                observation.context
            )
```

### Multi-Channel Delivery System
```python
class MultiChannelDelivery(BeastlyModule):
    """Reliable multi-channel observation delivery system"""
    
    def __init__(self):
        super().__init__()
        self.channels = {
            'websocket': WebSocketChannel(),
            'http_api': HTTPAPIChannel(), 
            'directus': DirectusChannel(),
            'local_queue': LocalQueueChannel()  # Fallback for offline scenarios
        }
        self.retry_policy = ExponentialBackoffRetry(max_attempts=3)
    
    def deliver_observation(self, observation: Observation) -> DeliveryResult:
        """Deliver observation through all available channels"""
        with self.trace_operation("multi_channel_delivery") as trace:
            results = {}
            
            # Primary delivery: WebSocket (real-time)
            results['websocket'] = self._deliver_websocket(observation)
            
            # Fallback delivery: HTTP API
            if not results['websocket'].success:
                results['http_api'] = self._deliver_http_api(observation)
            
            # Persistence: Directus CMS
            results['directus'] = self._deliver_directus(observation)
            
            # Local queue for offline scenarios
            if not any(r.success for r in results.values()):
                results['local_queue'] = self._queue_for_retry(observation)
            
            return DeliveryResult.aggregate(results)
    
    def _deliver_websocket(self, observation: Observation) -> ChannelResult:
        """Deliver via WebSocket to Observatory Dashboard"""
        try:
            # Use existing Observatory WebSocket infrastructure
            websocket_client = ObservatoryWebSocketClient()
            success = websocket_client.send_observation(observation)
            return ChannelResult(success=success, latency=websocket_client.last_latency)
        except Exception as e:
            self.logger.warning(f"WebSocket delivery failed: {e}")
            return ChannelResult(success=False, error=str(e))
```

### Directus Persistence Integration
```python
class DirectusPersistenceLayer(BeastlyModule):
    """Directus integration for observation persistence and analytics"""
    
    def __init__(self, directus_client: DirectusClient):
        super().__init__()
        self.directus_client = directus_client
        self.collections = {
            'ace_observations': 'ace_reporter_observations',
            'delivery_results': 'observation_delivery_results', 
            'context_correlations': 'observation_context_correlations',
            'performance_metrics': 'ace_reporter_metrics'
        }
    
    def store_observation(self, observation: Observation, delivery_result: DeliveryResult):
        """Store observation and delivery results in Directus"""
        with self.trace_operation("directus_observation_storage") as trace:
            # Store main observation
            obs_record = self._create_observation_record(observation)
            obs_id = self.directus_client.create_item(
                self.collections['ace_observations'], 
                obs_record
            )
            
            # Store delivery results
            for channel, result in delivery_result.channel_results.items():
                delivery_record = self._create_delivery_record(obs_id, channel, result)
                self.directus_client.create_item(
                    self.collections['delivery_results'],
                    delivery_record
                )
            
            # Store context correlations if available
            if observation.context_correlations:
                for correlation in observation.context_correlations:
                    corr_record = self._create_correlation_record(obs_id, correlation)
                    self.directus_client.create_item(
                        self.collections['context_correlations'],
                        corr_record
                    )
    
    def get_observation_history(self, 
                              project_id: str = None, 
                              time_range: TimeRange = None) -> List[Observation]:
        """Retrieve observation history with filtering"""
        filters = {}
        if project_id:
            filters['project_id'] = {'_eq': project_id}
        if time_range:
            filters['timestamp'] = {
                '_gte': time_range.start.isoformat(),
                '_lte': time_range.end.isoformat()
            }
        
        return self.directus_client.get_items(
            self.collections['ace_observations'],
            filter=filters,
            sort=['-timestamp']
        )
```

## Data Models

### Enhanced Observation Model
```python
@dataclass
class EnhancedObservation:
    """Enhanced observation with AI Memory Palace context"""
    
    # Core observation data (existing)
    timestamp: datetime
    message: str
    event_type: str
    emoji: str
    severity: str
    
    # Enhanced context from AI Memory Palace
    project_context: ProjectContext
    session_context: SessionContext
    spec_progress: Optional[SpecProgress]
    correlation_id: str
    trace_id: Optional[str]
    
    # Delivery tracking
    delivery_channels: List[str]
    delivery_confirmations: Dict[str, bool]
    delivery_latencies: Dict[str, float]
    
    # Performance metrics
    processing_time: float
    context_retrieval_time: float
    total_delivery_time: float

@dataclass 
class ProjectContext:
    """Current project context from AI Memory Palace"""
    project_id: str
    project_name: str
    current_session_id: str
    active_spec: Optional[str]
    progress_state: Dict[str, Any]
    last_activity: datetime
    
    @classmethod
    def default(cls) -> 'ProjectContext':
        return cls(
            project_id="unknown",
            project_name="Unknown Project", 
            current_session_id="default",
            active_spec=None,
            progress_state={},
            last_activity=datetime.now()
        )

@dataclass
class DeliveryResult:
    """Multi-channel delivery result tracking"""
    success: bool
    channel_results: Dict[str, ChannelResult]
    total_latency: float
    retry_count: int
    error_messages: List[str]
    
    @classmethod
    def aggregate(cls, channel_results: Dict[str, ChannelResult]) -> 'DeliveryResult':
        success = any(r.success for r in channel_results.values())
        total_latency = max(r.latency for r in channel_results.values() if r.latency)
        errors = [r.error for r in channel_results.values() if r.error]
        
        return cls(
            success=success,
            channel_results=channel_results,
            total_latency=total_latency,
            retry_count=0,
            error_messages=errors
        )
```

### Directus Collections Schema
```javascript
// ACE Reporter observation storage
const ace_reporter_collections = {
  ace_reporter_observations: {
    id: 'uuid',
    timestamp: 'timestamp',
    message: 'text',
    event_type: 'string',
    emoji: 'string',
    severity: 'string',
    
    // AI Memory Palace context
    project_id: 'string',
    project_name: 'string', 
    session_id: 'string',
    spec_name: 'string',
    spec_progress: 'json',
    
    // Tracing and correlation
    correlation_id: 'string',
    trace_id: 'string',
    context_data: 'json',
    
    // Performance metrics
    processing_time_ms: 'float',
    context_retrieval_time_ms: 'float',
    total_delivery_time_ms: 'float',
    
    created_at: 'timestamp',
    updated_at: 'timestamp'
  },
  
  observation_delivery_results: {
    id: 'uuid',
    observation_id: 'uuid', // FK to ace_reporter_observations
    channel_name: 'string', // websocket, http_api, directus, local_queue
    success: 'boolean',
    latency_ms: 'float',
    error_message: 'text',
    retry_count: 'integer',
    delivered_at: 'timestamp',
    created_at: 'timestamp'
  },
  
  observation_context_correlations: {
    id: 'uuid',
    observation_id: 'uuid', // FK to ace_reporter_observations
    correlated_event_type: 'string',
    correlated_event_id: 'string',
    correlation_strength: 'float', // 0.0 to 1.0
    correlation_metadata: 'json',
    created_at: 'timestamp'
  },
  
  ace_reporter_metrics: {
    id: 'uuid',
    metric_name: 'string',
    metric_value: 'float',
    metric_unit: 'string',
    project_id: 'string',
    timestamp: 'timestamp',
    metadata: 'json',
    created_at: 'timestamp'
  }
};
```

## Error Handling

### Brownfield Safety Strategy
1. **Zero Downtime Deployment**: All changes deployed as additive enhancements
2. **Graceful Degradation**: Enhanced features fail back to current operational behavior
3. **Rollback Capability**: Easy revert to current StatusAnnouncer if issues arise
4. **Monitoring Integration**: Enhanced observability without disrupting existing metrics

### Multi-Channel Resilience
```python
class ResilientDelivery(BeastlyModule):
    """Resilient delivery with comprehensive error handling"""
    
    def handle_delivery_failure(self, channel: str, observation: Observation, error: Exception):
        """Handle delivery failures with appropriate fallback strategies"""
        with self.trace_operation("delivery_failure_handling") as trace:
            
            if channel == 'websocket':
                # Fallback to HTTP API
                self._attempt_http_fallback(observation)
                
            elif channel == 'http_api':
                # Queue for retry when connectivity restored
                self._queue_for_retry(observation)
                
            elif channel == 'directus':
                # Store in local cache for later sync
                self._cache_for_directus_sync(observation)
            
            # Always emit failure observation for monitoring
            self.emit_observation(
                f"Delivery failure on {channel}: {str(error)}",
                "warning",
                context={"channel": channel, "observation_id": observation.id},
                emoji="⚠️"
            )
```

### Context Retrieval Fallbacks
```python
def get_context_with_fallback(self) -> ProjectContext:
    """Get AI Memory Palace context with graceful fallback"""
    try:
        # Primary: AI Memory Palace context
        return self.ai_memory_palace.get_current_context()
    except AIMemoryPalaceUnavailable:
        # Fallback: Cached context
        return self.context_cache.get_last_known_context()
    except Exception as e:
        # Ultimate fallback: Default context
        self.logger.warning(f"Context retrieval failed: {e}")
        return ProjectContext.default()
```

## Testing Strategy

### Brownfield Testing Approach
1. **Non-Disruptive Testing**: All tests run against test instances, never production
2. **Backward Compatibility**: Ensure existing StatusAnnouncer APIs continue working
3. **Integration Validation**: Test enhanced features without affecting operational systems
4. **Performance Impact**: Measure and validate no performance degradation

### Test Categories
```python
class TestEnhancedACEReporter:
    """Comprehensive test suite for enhanced ACE Reporter"""
    
    def test_backward_compatibility(self):
        """Ensure existing StatusAnnouncer functionality unchanged"""
        # Test all existing methods work identically
        
    def test_ai_memory_palace_integration(self):
        """Test AI Memory Palace context integration"""
        # Test context retrieval and enhancement
        
    def test_multi_channel_delivery(self):
        """Test multi-channel delivery system"""
        # Test WebSocket, HTTP, Directus delivery
        
    def test_graceful_degradation(self):
        """Test graceful degradation scenarios"""
        # Test behavior when AI Memory Palace unavailable
        
    def test_performance_impact(self):
        """Measure performance impact of enhancements"""
        # Ensure no significant latency increase
```

## Implementation Approach

### Phase 1: BeastlyModule Migration (Zero Risk)
1. **Create Enhanced ACE Reporter** as new class inheriting from BeastlyModule
2. **Maintain StatusAnnouncer** as existing operational class
3. **Add feature flag** to switch between implementations
4. **Validate BeastlyModule capabilities** in test environment

### Phase 2: AI Memory Palace Integration (Low Risk)
1. **Implement context integration layer** with comprehensive fallbacks
2. **Add context enhancement** to observations without changing core delivery
3. **Test multi-project awareness** in isolated environment
4. **Validate context correlation** functionality

### Phase 3: Multi-Channel Delivery (Medium Risk)
1. **Implement delivery channel abstraction** with existing WebSocket as primary
2. **Add HTTP API fallback** using existing direct_status_broadcast logic
3. **Integrate Directus persistence** as additional channel
4. **Test delivery confirmation** and retry mechanisms

### Phase 4: Production Deployment (Controlled Risk)
1. **Deploy enhanced system** with feature flag disabled
2. **Gradually enable enhanced features** with monitoring
3. **Monitor performance impact** and delivery success rates
4. **Full cutover** once stability validated

### Rollback Strategy
```python
# Feature flag for safe deployment
class ACEReporterFactory:
    @staticmethod
    def create_reporter(enhanced: bool = False) -> Union[StatusAnnouncer, EnhancedACEReporter]:
        if enhanced and config.ENHANCED_ACE_REPORTER_ENABLED:
            return EnhancedACEReporter()
        else:
            return StatusAnnouncer()  # Existing operational system
```

## Success Metrics

### Operational Continuity
- **Zero downtime**: No disruption to https://observatory.nkllon.com
- **Backward compatibility**: 100% existing functionality preserved
- **Performance**: <10% latency increase for enhanced features

### Enhanced Capabilities
- **Context accuracy**: >95% observations include correct project context
- **Delivery reliability**: >99% multi-channel delivery success rate
- **Integration health**: AI Memory Palace integration >95% uptime
- **Correlation quality**: >90% relevant event correlations identified

### System Health
- **Error recovery**: <30 seconds average recovery from channel failures
- **Monitoring coverage**: 100% enhanced operations traced and monitored
- **Storage efficiency**: Directus persistence <2 seconds average latency
- **Multi-project support**: Accurate context for concurrent project sessions

## Deployment Safety

### Pre-Deployment Checklist
- [ ] All existing StatusAnnouncer functionality tested and working
- [ ] Enhanced ACE Reporter tested in isolation with all fallbacks
- [ ] AI Memory Palace integration tested with unavailability scenarios
- [ ] Multi-channel delivery tested with individual channel failures
- [ ] Directus persistence tested with connection failures
- [ ] Performance impact measured and within acceptable limits
- [ ] Rollback procedure tested and validated
- [ ] Monitoring and alerting configured for new components

### Deployment Sequence
1. **Deploy enhanced code** with feature flag disabled
2. **Validate existing functionality** continues working
3. **Enable enhanced features** gradually with monitoring
4. **Monitor delivery success rates** and performance metrics
5. **Full cutover** once stability demonstrated
6. **Remove feature flag** after successful operation period

This design ensures we enhance the ACE Reporter system while maintaining the operational integrity of the existing Observatory Dashboard and related systems.