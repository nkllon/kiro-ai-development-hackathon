# Maintenance Procedures Documentation

## Overview

This document provides comprehensive maintenance procedures for the Beast Mode framework, covering component updates, configuration changes, CMS-based configuration management, version control workflows, rolling updates, and coordination with existing Beast Mode components to prevent service disruption.

## CMS-Based Configuration Management

### Directus CMS Configuration Management (ADR-010 Compliance)

**Directus CMS Location**: `localhost:8055`
**Fallback Strategy**: File-based configuration when Directus unavailable

#### 1. Configuration Schema Management

**Configuration Collections in Directus**:
```javascript
// Observatory Configuration Collection
{
  collection: "observatory_config",
  fields: [
    { field: "id", type: "integer", primary: true },
    { field: "component_name", type: "string", required: true },
    { field: "config_key", type: "string", required: true },
    { field: "config_value", type: "json", required: true },
    { field: "environment", type: "string", default: "production" },
    { field: "version", type: "string", required: true },
    { field: "created_at", type: "timestamp", readonly: true },
    { field: "updated_at", type: "timestamp", readonly: true },
    { field: "updated_by", type: "string", required: true }
  ]
}

// WebSocket Configuration Collection
{
  collection: "websocket_config",
  fields: [
    { field: "id", type: "integer", primary: true },
    { field: "endpoint_path", type: "string", required: true },
    { field: "max_connections", type: "integer", default: 100 },
    { field: "rate_limit_per_minute", type: "integer", default: 60 },
    { field: "authentication_required", type: "boolean", default: false },
    { field: "message_types", type: "json", required: true },
    { field: "enabled", type: "boolean", default: true }
  ]
}
```

#### 2. Configuration Update Procedures

**Step 1: Access Directus Admin Interface**
```bash
# Verify Directus availability
curl -s http://localhost:8055/server/ping
# Expected: "pong"

# Access admin interface
open http://localhost:8055/admin
# Login with admin credentials
```

**Step 2: Update Configuration Values**
```javascript
// Example: Update WebSocket connection limits
PUT http://localhost:8055/items/websocket_config/1
{
  "max_connections": 250,
  "rate_limit_per_minute": 100,
  "updated_by": "maintenance_user"
}
```

**Step 3: Validate Configuration Changes**
```bash
# Test configuration retrieval
curl -s "http://localhost:8055/items/websocket_config" \
  -H "Authorization: Bearer $DIRECTUS_TOKEN"

# Verify configuration applied to Observatory
curl -s http://localhost:8888/config/websocket
```

**Step 4: Apply Configuration to Running Services**
```bash
# Trigger configuration reload
curl -X POST http://localhost:8888/admin/reload-config \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Verify configuration applied
make dashboard-status | grep -A 10 "WebSocket Status"
```

#### 3. Configuration Backup and Restore

**Backup Configuration**:
```bash
# Create configuration backup
curl -s "http://localhost:8055/items/observatory_config" \
  -H "Authorization: Bearer $DIRECTUS_TOKEN" \
  > config_backup_$(date +%Y%m%d_%H%M%S).json

# Backup WebSocket configuration
curl -s "http://localhost:8055/items/websocket_config" \
  -H "Authorization: Bearer $DIRECTUS_TOKEN" \
  > websocket_config_backup_$(date +%Y%m%d_%H%M%S).json
```

**Restore Configuration**:
```bash
# Restore from backup
curl -X POST "http://localhost:8055/items/observatory_config" \
  -H "Authorization: Bearer $DIRECTUS_TOKEN" \
  -H "Content-Type: application/json" \
  -d @config_backup_20250103_104500.json
```

### File-Based Configuration Fallback

**Fallback Configuration Structure**:
```yaml
# config/observatory_fallback.yml
observatory:
  server:
    host: "localhost"
    port: 8888
    log_level: "INFO"
  
  websocket:
    endpoints:
      - path: "/ws/observatory"
        max_connections: 250
        rate_limit_per_minute: 100
        authentication_required: false
      - path: "/ws/emoji-rain"
        max_connections: 100
        rate_limit_per_minute: 20
        authentication_required: false
  
  redis:
    primary:
      host: "192.168.1.119"
      port: 6379
    fallback:
      host: "localhost"
      port: 6380
  
  monitoring:
    prometheus:
      enabled: true
      metrics_interval: 15
    health_checks:
      enabled: true
      interval: 30
```

**Fallback Activation Procedure**:
```python
class ConfigurationManager(ReflectiveModule):
    """Manages configuration with CMS and file-based fallback."""
    
    def __init__(self):
        super().__init__()
        self.module_id = "ConfigurationManager"
        self._directus_available = False
        self._fallback_config = None
        
    async def load_configuration(self) -> Dict[str, Any]:
        """Load configuration with fallback strategy."""
        try:
            # Try Directus CMS first
            config = await self._load_from_directus()
            self._directus_available = True
            return config
            
        except Exception as e:
            self._logger.warning(f"Directus unavailable, using fallback: {e}")
            self._directus_available = False
            return self._load_from_fallback()
    
    async def _load_from_directus(self) -> Dict[str, Any]:
        """Load configuration from Directus CMS."""
        # Implementation for Directus configuration loading
        pass
    
    def _load_from_fallback(self) -> Dict[str, Any]:
        """Load configuration from fallback files."""
        with open('config/observatory_fallback.yml', 'r') as f:
            return yaml.safe_load(f)
```

## Component Update Procedures

### 1. Observatory Server Updates

**Pre-Update Checklist**:
- [ ] Backup current configuration
- [ ] Verify system health status
- [ ] Schedule maintenance window
- [ ] Notify stakeholders of planned downtime

**Update Procedure**:

**Step 1: Prepare Update Environment**
```bash
# Create backup of current installation
cp -r /path/to/observatory /path/to/observatory_backup_$(date +%Y%m%d)

# Backup configuration
make config-backup

# Verify system health before update
make health-check
```

**Step 2: Download and Validate Update**
```bash
# Download update package
wget https://releases.observatory.com/v2.1.0/observatory-v2.1.0.tar.gz

# Verify checksum
sha256sum observatory-v2.1.0.tar.gz
# Compare with published checksum

# Extract update
tar -xzf observatory-v2.1.0.tar.gz
```

**Step 3: Apply Update with Rolling Deployment**
```bash
# Stop Observatory server gracefully
make dashboard-stop

# Apply update
cp -r observatory-v2.1.0/* /path/to/observatory/

# Update dependencies
pip install -r requirements.txt

# Run database migrations if needed
python scripts/migrate_configuration.py

# Start Observatory server
make dashboard-up

# Verify update successful
make dashboard-status
curl http://localhost:8888/version
```

**Step 4: Post-Update Validation**
```bash
# Comprehensive health check
make health-check DEEP_CHECK=true

# Test all WebSocket endpoints
for endpoint in observatory emoji-rain anomalies doctor-status; do
  echo "Testing /ws/$endpoint"
  timeout 10 wscat -c "ws://localhost:8888/ws/$endpoint" -x '{"type":"ping"}'
done

# Verify integration points
curl http://localhost:8888/integrations/status

# Monitor for 15 minutes
watch -n 30 'make dashboard-status'
```

### 2. WebSocket Endpoint Updates

**Hot-Reload WebSocket Configuration**:
```bash
# Update WebSocket configuration in Directus
curl -X PATCH "http://localhost:8055/items/websocket_config/1" \
  -H "Authorization: Bearer $DIRECTUS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "max_connections": 300,
    "rate_limit_per_minute": 120
  }'

# Trigger hot-reload without service restart
curl -X POST http://localhost:8888/admin/reload-websocket-config \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Verify configuration applied
curl http://localhost:8888/websocket/config
```

**WebSocket Handler Update Procedure**:
```python
class WebSocketUpdateManager(ReflectiveModule):
    """Manages WebSocket handler updates without service disruption."""
    
    async def update_websocket_handler(self, new_handler_config: Dict[str, Any]):
        """Update WebSocket handler with zero-downtime deployment."""
        # 1. Create new handler instance
        new_handler = WebSocketHandler(new_handler_config)
        
        # 2. Initialize new handler
        await new_handler.initialize()
        
        # 3. Gradually migrate connections
        await self._migrate_connections(self._current_handler, new_handler)
        
        # 4. Replace handler atomically
        old_handler = self._current_handler
        self._current_handler = new_handler
        
        # 5. Cleanup old handler
        await old_handler.graceful_shutdown()
        
        self._logger.info("WebSocket handler updated successfully")
```

### 3. Redis Coordination Updates

**Redis Configuration Update**:
```bash
# Update Redis configuration
redis-cli -h 192.168.1.119 -p 6379 CONFIG SET maxmemory 2gb
redis-cli -h 192.168.1.119 -p 6379 CONFIG SET maxmemory-policy allkeys-lru

# Persist configuration changes
redis-cli -h 192.168.1.119 -p 6379 CONFIG REWRITE

# Verify configuration applied
redis-cli -h 192.168.1.119 -p 6379 CONFIG GET maxmemory
```

**Redis Failover Testing**:
```bash
# Test failover mechanism
# Temporarily stop primary Redis
redis-cli -h 192.168.1.119 -p 6379 DEBUG SLEEP 30

# Verify Observatory fails over to fallback
curl http://localhost:8888/health | jq '.redis_status'
# Expected: {"primary": "disconnected", "fallback": "connected"}

# Verify failback when primary recovers
# Wait for primary Redis to recover
sleep 35

# Check failback occurred
curl http://localhost:8888/health | jq '.redis_status'
# Expected: {"primary": "connected", "fallback": "standby"}
```

## Version Control Workflows

### 1. Configuration Version Control

**Git-Based Configuration Management**:
```bash
# Initialize configuration repository
cd /path/to/config
git init
git remote add origin https://github.com/company/beast-mode-config.git

# Create configuration branches
git checkout -b production
git checkout -b staging
git checkout -b development

# Commit configuration changes
git add observatory_config.yml websocket_config.yml
git commit -m "Update WebSocket connection limits for production"
git push origin production
```

**Configuration Deployment Pipeline**:
```yaml
# .github/workflows/config-deployment.yml
name: Configuration Deployment
on:
  push:
    branches: [production, staging]

jobs:
  deploy-config:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Validate Configuration
        run: |
          python scripts/validate_config.py
          
      - name: Deploy to Directus
        run: |
          python scripts/deploy_config_to_directus.py \
            --environment ${{ github.ref_name }} \
            --directus-url ${{ secrets.DIRECTUS_URL }} \
            --token ${{ secrets.DIRECTUS_TOKEN }}
            
      - name: Trigger Service Reload
        run: |
          curl -X POST ${{ secrets.OBSERVATORY_URL }}/admin/reload-config \
            -H "Authorization: Bearer ${{ secrets.ADMIN_TOKEN }}"
```

### 2. Code Deployment Workflows

**Rolling Deployment Strategy**:
```bash
#!/bin/bash
# scripts/rolling_deployment.sh

set -e

DEPLOYMENT_ID="deploy_$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="/backups/$DEPLOYMENT_ID"

echo "🚀 Starting rolling deployment: $DEPLOYMENT_ID"

# Step 1: Create backup
echo "📦 Creating backup..."
mkdir -p $BACKUP_DIR
cp -r /app/observatory $BACKUP_DIR/
cp /app/config/* $BACKUP_DIR/

# Step 2: Health check before deployment
echo "🏥 Pre-deployment health check..."
if ! make health-check; then
  echo "❌ Pre-deployment health check failed"
  exit 1
fi

# Step 3: Deploy new version
echo "📥 Deploying new version..."
tar -xzf observatory-new-version.tar.gz -C /app/

# Step 4: Update dependencies
echo "📦 Updating dependencies..."
pip install -r /app/observatory/requirements.txt

# Step 5: Run migrations
echo "🔄 Running migrations..."
python /app/observatory/scripts/migrate.py

# Step 6: Graceful restart
echo "🔄 Performing graceful restart..."
make dashboard-restart

# Step 7: Post-deployment validation
echo "✅ Post-deployment validation..."
sleep 30  # Allow service to fully start

if make health-check DEEP_CHECK=true; then
  echo "🎉 Deployment successful: $DEPLOYMENT_ID"
  # Cleanup old backups (keep last 5)
  ls -t /backups/ | tail -n +6 | xargs -r rm -rf
else
  echo "❌ Deployment validation failed, rolling back..."
  make dashboard-stop
  cp -r $BACKUP_DIR/observatory /app/
  cp $BACKUP_DIR/config/* /app/config/
  make dashboard-up
  echo "🔄 Rollback complete"
  exit 1
fi
```

## Rolling Updates

### 1. Zero-Downtime Observatory Updates

**Blue-Green Deployment Strategy**:
```python
class BlueGreenDeploymentManager(ReflectiveModule):
    """Manages blue-green deployments for zero-downtime updates."""
    
    def __init__(self):
        super().__init__()
        self.module_id = "BlueGreenDeploymentManager"
        self._blue_instance = None
        self._green_instance = None
        self._active_instance = "blue"
        
    async def deploy_new_version(self, version: str, config: Dict[str, Any]):
        """Deploy new version using blue-green strategy."""
        inactive_instance = "green" if self._active_instance == "blue" else "blue"
        
        self._logger.info(f"Deploying version {version} to {inactive_instance} instance")
        
        # 1. Deploy to inactive instance
        await self._deploy_to_instance(inactive_instance, version, config)
        
        # 2. Health check inactive instance
        if not await self._health_check_instance(inactive_instance):
            raise DeploymentError(f"Health check failed for {inactive_instance} instance")
        
        # 3. Switch traffic to new instance
        await self._switch_traffic(inactive_instance)
        
        # 4. Verify traffic switch successful
        await asyncio.sleep(30)  # Allow traffic to stabilize
        
        if await self._verify_traffic_switch(inactive_instance):
            # 5. Shutdown old instance
            await self._shutdown_instance(self._active_instance)
            self._active_instance = inactive_instance
            self._logger.info(f"Deployment successful, active instance: {self._active_instance}")
        else:
            # Rollback on failure
            await self._switch_traffic(self._active_instance)
            await self._shutdown_instance(inactive_instance)
            raise DeploymentError("Traffic switch verification failed, rolled back")
```

### 2. WebSocket Connection Migration

**Connection Migration Strategy**:
```python
class WebSocketConnectionMigrator(ReflectiveModule):
    """Migrates WebSocket connections during updates."""
    
    async def migrate_connections(self, old_handler, new_handler):
        """Migrate WebSocket connections from old to new handler."""
        connections = old_handler.get_active_connections()
        
        self._logger.info(f"Migrating {len(connections)} WebSocket connections")
        
        for connection in connections:
            try:
                # 1. Notify client of migration
                await connection.send(json.dumps({
                    'type': 'migration_notice',
                    'message': 'Service updating, please reconnect',
                    'reconnect_delay_ms': 5000
                }))
                
                # 2. Graceful close with reconnect code
                await connection.close(code=1012, reason='Service restart')
                
            except Exception as e:
                self._logger.warning(f"Failed to migrate connection {connection.id}: {e}")
        
        # 3. Wait for clients to reconnect to new handler
        await asyncio.sleep(10)
        
        # 4. Verify migration success
        new_connections = new_handler.get_active_connections()
        migration_success_rate = len(new_connections) / len(connections) if connections else 1.0
        
        self._logger.info(f"Migration complete: {migration_success_rate:.1%} success rate")
        
        return migration_success_rate > 0.8  # 80% success threshold
```

## Coordination with Beast Mode Components

### 1. Component Update Coordination

**Update Coordination Protocol**:
```python
class ComponentUpdateCoordinator(ReflectiveModule):
    """Coordinates updates across Beast Mode components."""
    
    def __init__(self):
        super().__init__()
        self.module_id = "ComponentUpdateCoordinator"
        self._component_registry = {}
        self._update_locks = {}
        
    async def coordinate_component_update(self, component_id: str, update_plan: Dict[str, Any]):
        """Coordinate component update with dependency management."""
        # 1. Validate update dependencies
        dependencies = await self._get_component_dependencies(component_id)
        
        for dep in dependencies:
            if dep in self._update_locks:
                raise UpdateConflictError(f"Dependency {dep} is currently updating")
        
        # 2. Acquire update lock
        self._update_locks[component_id] = {
            'start_time': datetime.now(),
            'update_plan': update_plan,
            'status': 'in_progress'
        }
        
        try:
            # 3. Notify dependent components
            await self._notify_dependents(component_id, 'update_starting')
            
            # 4. Execute update
            result = await self._execute_component_update(component_id, update_plan)
            
            # 5. Validate update success
            if await self._validate_component_health(component_id):
                self._update_locks[component_id]['status'] = 'completed'
                await self._notify_dependents(component_id, 'update_completed')
            else:
                raise UpdateValidationError(f"Health check failed for {component_id}")
                
        except Exception as e:
            # Rollback on failure
            self._update_locks[component_id]['status'] = 'failed'
            await self._rollback_component_update(component_id)
            await self._notify_dependents(component_id, 'update_failed')
            raise
            
        finally:
            # Release update lock
            del self._update_locks[component_id]
```

### 2. Service Disruption Prevention

**Graceful Degradation During Updates**:
```python
class GracefulDegradationManager(ReflectiveModule):
    """Manages graceful degradation during maintenance."""
    
    def __init__(self):
        super().__init__()
        self.module_id = "GracefulDegradationManager"
        self._degradation_levels = {
            'normal': {'rate_limit_multiplier': 1.0, 'feature_flags': {}},
            'maintenance': {'rate_limit_multiplier': 0.5, 'feature_flags': {'emoji_rain': False}},
            'emergency': {'rate_limit_multiplier': 0.1, 'feature_flags': {'emoji_rain': False, 'anomaly_detection': False}}
        }
        
    async def enable_maintenance_mode(self, component_id: str, estimated_duration: int):
        """Enable maintenance mode with graceful degradation."""
        # 1. Notify all connected clients
        await self._broadcast_maintenance_notice(component_id, estimated_duration)
        
        # 2. Reduce service capacity
        await self._apply_degradation_level('maintenance')
        
        # 3. Enable maintenance endpoints
        await self._enable_maintenance_endpoints()
        
        self._logger.info(f"Maintenance mode enabled for {component_id}")
    
    async def disable_maintenance_mode(self, component_id: str):
        """Disable maintenance mode and restore full capacity."""
        # 1. Restore normal service capacity
        await self._apply_degradation_level('normal')
        
        # 2. Disable maintenance endpoints
        await self._disable_maintenance_endpoints()
        
        # 3. Notify clients of service restoration
        await self._broadcast_service_restored(component_id)
        
        self._logger.info(f"Maintenance mode disabled for {component_id}")
```

## Monitoring and Validation

### Maintenance Metrics

```python
def get_maintenance_metrics(self) -> Dict[str, float]:
    """Get Prometheus metrics for maintenance operations."""
    return {
        "maintenance_operations_total": self._total_maintenance_operations,
        "maintenance_operation_duration_seconds": self._avg_maintenance_duration,
        "maintenance_operation_success_rate": self._maintenance_success_rate,
        "configuration_updates_total": self._total_config_updates,
        "rolling_deployment_success_rate": self._rolling_deployment_success_rate,
        "zero_downtime_deployments_total": self._zero_downtime_deployments
    }
```

### Health Monitoring During Maintenance

```python
def get_maintenance_health_status(self) -> Dict[str, Any]:
    """Get health status during maintenance operations."""
    return {
        "maintenance_mode_active": self._maintenance_mode_active,
        "degradation_level": self._current_degradation_level,
        "active_maintenance_operations": len(self._active_maintenance_ops),
        "estimated_completion_time": self._get_estimated_completion_time(),
        "service_availability_percentage": self._calculate_service_availability(),
        "client_impact_level": self._assess_client_impact()
    }
```

## Troubleshooting Maintenance Issues

### Common Maintenance Problems

**Configuration Update Failures**:
- Verify Directus CMS connectivity
- Check configuration syntax and validation
- Review fallback configuration availability

**Rolling Deployment Issues**:
- Validate health checks before and after deployment
- Check dependency compatibility
- Verify backup and rollback procedures

**WebSocket Connection Migration Problems**:
- Monitor connection migration success rates
- Check client reconnection behavior
- Validate new handler initialization

**Service Coordination Failures**:
- Review component dependency mappings
- Check update lock management
- Validate notification systems

### Recovery Procedures

1. **Rollback Failed Updates**: Use backup restoration procedures
2. **Restore Service Capacity**: Disable degradation modes and restore normal operations
3. **Clear Update Locks**: Release stuck update locks and coordination state
4. **Validate System Health**: Run comprehensive health checks after recovery
5. **Update Maintenance Procedures**: Document lessons learned and improve procedures

This comprehensive maintenance procedures documentation ensures systematic and reliable maintenance operations across the Beast Mode framework with minimal service disruption and maximum reliability.