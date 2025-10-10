# Design Document

## Overview

Design Directus as the web interface layer of the AI Memory Palace system, providing web-based access to the same context data that's accessible through CLI and API interfaces. Directus becomes an integral part of the AI Memory Palace architecture, not a separate system.

## Architecture

### Current State (AI Memory Palace Layer 3)
```
AI Memory Palace (BeastlyModule Layer 3)
├── Core Layer
│   ├── ContextManager - Main orchestrator with full tracing
│   ├── ContextRegistry - Storage with trace correlation
│   ├── ContextEngine - Processing with distributed spans
│   └── ContextValidator - Validation with trace tracking
├── Interface Layer
│   ├── CLI Interface - Built-in BeastlyModule CLI (✅ Working)
│   └── API Interface - REST/GraphQL endpoints (✅ Working)
└── Enhanced Observability - Jaeger + Prometheus + systematic monitoring
```

### Target State (Complete AI Memory Palace System)
```
AI Memory Palace (Complete System with Multiple Interfaces)
├── Core Layer (BeastlyModule Layer 3)
│   ├── ContextManager - Orchestration and business logic
│   ├── ContextRegistry - Data persistence and retrieval
│   ├── ContextEngine - Processing and intelligence
│   └── ContextValidator - Quality and integrity
├── Interface Layer
│   ├── CLI Interface - Built-in BeastlyModule CLI (✅ Working)
│   ├── API Interface - REST/GraphQL endpoints (✅ Working)
│   └── Web Interface - Directus CMS (🎯 Adding)
│       ├── DirectusWebInterface (BeastlyModule)
│       ├── Context visualization and management
│       ├── Project and session dashboards
│       └── Collaborative editing capabilities
└── Enhanced Observability (BeastlyModule Layer 3)
    ├── Jaeger distributed tracing across all interfaces
    ├── Prometheus metrics for web, CLI, and API usage
    └── Systematic monitoring and health checks
```

## Components and Interfaces

### DirectusWebInterface (BeastlyModule)
```python
class DirectusWebInterface(BeastlyModule):
    """Web interface layer for AI Memory Palace using Directus"""
    
    def __init__(self, context_manager: ContextManager):
        super().__init__()
        self.context_manager = context_manager
        # Inherits: tracing, metrics, CLI, health monitoring
        # Direct access to AI Memory Palace core - no synchronization needed
    
    def get_session_contexts_for_web(self, project_id: str) -> List[Dict]:
        """Get context data formatted for Directus web interface"""
        with self.trace_operation("web_context_retrieval") as trace:
            contexts = self.context_manager.registry.get_project_contexts(project_id)
            return [self._format_for_web(ctx) for ctx in contexts]
    
    def update_context_from_web(self, session_id: str, web_data: Dict) -> bool:
        """Update AI Memory Palace context from Directus web interface"""
        with self.trace_operation("web_context_update") as trace:
            context = self._parse_from_web(web_data)
            return self.context_manager.registry.update_context(session_id, context)
```

### DirectusDataAdapter (BeastlyModule)
```python
class DirectusDataAdapter(BeastlyModule):
    """Adapter to present AI Memory Palace data in Directus-compatible format"""
    
    def __init__(self, context_manager: ContextManager):
        super().__init__()
        self.context_manager = context_manager
        # Direct access to core AI Memory Palace data
    
    def get_directus_collections(self) -> Dict[str, Any]:
        """Present AI Memory Palace data as Directus collections"""
        return {
            'session_contexts': self._get_session_contexts_collection(),
            'context_events': self._get_context_events_collection(),
            'projects': self._get_projects_collection()
        }
    
    def handle_directus_mutation(self, collection: str, operation: str, data: Dict):
        """Handle Directus web interface changes to AI Memory Palace data"""
        with self.trace_operation("directus_mutation") as trace:
            # Direct updates to AI Memory Palace core
            if collection == 'session_contexts':
                return self._update_session_context(operation, data)
```

### Modern Docker Configuration
```yaml
# docker-compose.directus-modern.yml
version: '3.8'
services:
  directus-postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: directus_ai_memory_palace
      POSTGRES_USER: directus
      POSTGRES_PASSWORD: ${DIRECTUS_DB_PASSWORD}
    volumes:
      - directus_postgres_data:/var/lib/postgresql/data
    networks:
      - ai_memory_palace_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U directus"]
      interval: 10s
      timeout: 5s
      retries: 5

  directus:
    image: directus/directus:10.8
    ports:
      - "8055:8055"
    environment:
      KEY: ${DIRECTUS_KEY}
      SECRET: ${DIRECTUS_SECRET}
      DB_CLIENT: pg
      DB_HOST: directus-postgres
      DB_PORT: 5432
      DB_DATABASE: directus_ai_memory_palace
      DB_USER: directus
      DB_PASSWORD: ${DIRECTUS_DB_PASSWORD}
      ADMIN_EMAIL: ${DIRECTUS_ADMIN_EMAIL}
      ADMIN_PASSWORD: ${DIRECTUS_ADMIN_PASSWORD}
      PUBLIC_URL: http://localhost:8055
      CORS_ENABLED: true
      CORS_ORIGIN: true
    depends_on:
      directus-postgres:
        condition: service_healthy
    networks:
      - ai_memory_palace_network
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8055/server/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    volumes:
      - directus_uploads:/directus/uploads
      - ./directus/extensions:/directus/extensions

networks:
  ai_memory_palace_network:
    driver: bridge
    name: ai_memory_palace_net
    ipam:
      config:
        - subnet: 172.25.0.0/16

volumes:
  directus_postgres_data:
  directus_uploads:
```

## Data Models

### Directus Collections Schema
```javascript
// AI Memory Palace Context Collections
const collections = {
  // Session contexts from AI Memory Palace
  session_contexts: {
    id: 'uuid',
    session_id: 'string',
    project_id: 'string', 
    start_time: 'timestamp',
    end_time: 'timestamp',
    context_summary: 'text',
    project_state: 'json',
    status: 'string', // active, archived, restored
    created_at: 'timestamp',
    updated_at: 'timestamp'
  },
  
  // Context events from conversations
  context_events: {
    id: 'uuid',
    session_id: 'string',
    event_type: 'string',
    event_data: 'json',
    timestamp: 'timestamp',
    correlation_id: 'string',
    trace_id: 'string', // From BeastlyModule tracing
    created_at: 'timestamp'
  },
  
  // Project states and metadata
  projects: {
    id: 'uuid',
    project_id: 'string',
    name: 'string',
    description: 'text',
    current_state: 'json',
    last_activity: 'timestamp',
    session_count: 'integer',
    created_at: 'timestamp',
    updated_at: 'timestamp'
  },
  
  // Synchronization tracking
  sync_operations: {
    id: 'uuid',
    operation_type: 'string', // ai_to_directus, directus_to_ai
    entity_type: 'string',
    entity_id: 'string',
    status: 'string', // pending, completed, failed, conflict
    trace_id: 'string',
    error_message: 'text',
    created_at: 'timestamp',
    completed_at: 'timestamp'
  }
};
```

### Integration Points
```python
# AI Memory Palace → Directus Integration
class AIMemoryPalaceDirectusIntegration(BeastlyModule):
    """Integration layer with enhanced observability"""
    
    def on_context_stored(self, context: SessionContext):
        """Hook: When AI Memory Palace stores context"""
        with self.trace_operation("context_to_directus_sync") as trace:
            self.directus_client.create_session_context(context)
            self.emit_observation(
                "Context synced to Directus",
                "info",
                context={"session_id": context.session_id},
                emoji="🔄"
            )
    
    def on_directus_context_updated(self, session_id: str, changes: Dict):
        """Hook: When Directus context is modified"""
        with self.trace_operation("directus_to_context_sync") as trace:
            self.memory_palace.update_context(session_id, changes)
```

## Error Handling

### Graceful Degradation Strategy
1. **Directus Unavailable**: AI Memory Palace continues operating independently
2. **AI Memory Palace Unavailable**: Directus provides read-only access to cached data
3. **Network Issues**: Queue sync operations for retry when connectivity restored
4. **Sync Conflicts**: Present conflict resolution interface in Directus

### Conflict Resolution
```python
class ConflictResolver(BeastlyModule):
    """Resolve synchronization conflicts with tracing"""
    
    def resolve_context_conflict(self, 
                               ai_context: SessionContext, 
                               directus_context: Dict) -> SessionContext:
        """Resolve conflicts between AI Memory Palace and Directus data"""
        with self.trace_operation("conflict_resolution") as trace:
            # Timestamp-based resolution with user override option
            # Enhanced observability for conflict tracking
```

## Testing Strategy

### Integration Testing
- **End-to-end sync testing** between AI Memory Palace and Directus
- **Conflict resolution testing** with simulated concurrent modifications
- **Performance testing** with large context datasets
- **Observability validation** ensuring tracing and metrics work correctly

### BeastlyModule Compliance Testing
- **Enhanced observability** validation for all integration components
- **CLI interface testing** for DirectusClient and synchronization tools
- **Health monitoring** validation for integrated system
- **Graceful degradation** testing when services are unavailable

## Implementation Approach

### Phase 1: Modern Directus Setup
1. Create modern Docker Compose configuration without network conflicts
2. Implement DirectusClient as BeastlyModule with enhanced observability
3. Set up Directus collections schema for AI Memory Palace data
4. Validate Directus startup and basic connectivity

### Phase 2: Basic Integration
1. Implement one-way sync from AI Memory Palace to Directus
2. Create Directus interfaces for viewing context data
3. Add basic conflict detection and logging
4. Validate data integrity and synchronization

### Phase 3: Bidirectional Sync
1. Implement Directus → AI Memory Palace synchronization
2. Add real-time sync capabilities with WebSocket integration
3. Implement conflict resolution mechanisms
4. Add comprehensive observability and monitoring

### Phase 4: Enhanced Features
1. Add advanced Directus interfaces for context management
2. Implement search and filtering capabilities
3. Add collaboration features and user permissions
4. Create backup and recovery integration

## Success Metrics

- **Directus startup time**: < 60 seconds with health checks passing
- **Sync latency**: Context changes reflected in both systems within 5 seconds
- **Conflict resolution**: < 1% of sync operations result in unresolved conflicts
- **Observability coverage**: 100% of integration operations traced and monitored
- **Uptime**: Both systems maintain 99.9% availability with graceful degradation