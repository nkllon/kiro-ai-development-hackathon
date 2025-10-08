# Disaster Recovery Procedures and Runbooks

## Overview

This document provides comprehensive disaster recovery procedures for the Beast Mode Observatory system, including Recovery Time Objectives (RTO), Recovery Point Objectives (RPO), step-by-step recovery procedures, backup and restore processes, and emergency escalation procedures.

## Recovery Objectives

### Service-Level Recovery Targets

| Service | RTO | RPO | Criticality | Recovery Priority |
|---------|-----|-----|-------------|-------------------|
| **Observatory Server** | 5 minutes | 1 minute | Critical | P0 |
| **WebSocket Endpoints** | 5 minutes | 1 minute | Critical | P0 |
| **Cloudflare Tunnel** | 10 minutes | 5 minutes | High | P1 |
| **Redis Coordination** | 3 minutes | 30 seconds | Critical | P0 |
| **Prometheus Monitoring** | 15 minutes | 5 minutes | Medium | P2 |
| **Grafana Dashboards** | 20 minutes | 10 minutes | Medium | P2 |
| **Directus CMS** | 30 minutes | 15 minutes | Low | P3 |

### Business Impact Analysis

#### Critical Services (RTO ≤ 5 minutes):
- **Observatory Server**: Core system functionality, all WebSocket endpoints depend on it
- **WebSocket Endpoints**: Real-time communication, celebration system, anomaly alerts
- **Redis Coordination**: Service coordination, failover mechanisms, state management

#### High Priority Services (RTO ≤ 15 minutes):
- **Cloudflare Tunnel**: External access, DNS routing, SSL termination
- **Prometheus Monitoring**: System observability, alerting, metrics collection

#### Medium Priority Services (RTO ≤ 30 minutes):
- **Grafana Dashboards**: Visualization, reporting, historical analysis
- **Directus CMS**: Configuration management, content administration

## Disaster Scenarios and Recovery Procedures

### Scenario 1: Observatory Server Failure

**Symptoms:**
- Observatory server process crashed or unresponsive
- All WebSocket endpoints unavailable
- Health endpoints returning errors or timeouts

**Impact Assessment:**
- **Business Impact:** Complete system outage
- **Affected Users:** All connected clients
- **Data Loss Risk:** In-memory state, active WebSocket connections

#### Recovery Procedure:

##### Phase 1: Immediate Response (0-2 minutes)
```bash
#!/bin/bash
# observatory-recovery-phase1.sh

echo "=== OBSERVATORY SERVER RECOVERY - PHASE 1 ==="
echo "Start Time: $(date)"

# Step 1: Assess current state
echo "Step 1: Assessing current state..."
ps aux | grep observatory | grep -v grep
lsof -i :8888
curl -s --max-time 3 http://localhost:8888/health || echo "Health check failed"

# Step 2: Stop any remaining processes
echo "Step 2: Stopping remaining processes..."
pkill -f observatory
sleep 2
pkill -9 -f observatory 2>/dev/null || true

# Step 3: Verify port availability
echo "Step 3: Verifying port availability..."
if lsof -i :8888 >/dev/null 2>&1; then
    echo "ERROR: Port 8888 still in use"
    lsof -i :8888
    exit 1
else
    echo "✅ Port 8888 available"
fi

# Step 4: Check system resources
echo "Step 4: Checking system resources..."
free -h
df -h /
uptime

echo "Phase 1 complete - ready for restart"
```

##### Phase 2: Service Restart (2-4 minutes)
```bash
#!/bin/bash
# observatory-recovery-phase2.sh

echo "=== OBSERVATORY SERVER RECOVERY - PHASE 2 ==="

# Step 1: Validate prerequisites
echo "Step 1: Validating prerequisites..."

# Check Redis connectivity
if redis-cli -h 192.168.1.119 -p 6379 ping >/dev/null 2>&1; then
    echo "✅ Primary Redis available"
elif redis-cli -h localhost -p 6380 ping >/dev/null 2>&1; then
    echo "✅ Fallback Redis available"
else
    echo "❌ No Redis available - starting Redis recovery"
    ./redis-recovery.sh
fi

# Check Python environment
if python3 -c "import observatory" >/dev/null 2>&1; then
    echo "✅ Python environment ready"
else
    echo "❌ Python environment issues detected"
    source venv/bin/activate
fi

# Step 2: Start Observatory server
echo "Step 2: Starting Observatory server..."
make dashboard-up &
START_PID=$!

# Step 3: Monitor startup progress
echo "Step 3: Monitoring startup progress..."
for i in {1..60}; do
    if curl -s http://localhost:8888/health >/dev/null 2>&1; then
        echo "✅ Observatory server started successfully"
        break
    fi
    
    if ! kill -0 $START_PID 2>/dev/null; then
        echo "❌ Observatory startup failed"
        tail -20 logs/observatory.log
        exit 1
    fi
    
    echo "Waiting for startup... ($i/60)"
    sleep 1
done

echo "Phase 2 complete - service restarted"
```

##### Phase 3: Validation and Recovery (4-5 minutes)
```bash
#!/bin/bash
# observatory-recovery-phase3.sh

echo "=== OBSERVATORY SERVER RECOVERY - PHASE 3 ==="

# Step 1: Comprehensive health validation
echo "Step 1: Comprehensive health validation..."

# Health endpoints
health_status=$(curl -s http://localhost:8888/health | jq -r '.status' 2>/dev/null)
if [ "$health_status" = "healthy" ]; then
    echo "✅ Health endpoint: HEALTHY"
else
    echo "❌ Health endpoint: $health_status"
fi

ready_status=$(curl -s http://localhost:8888/ready | jq -r '.ready' 2>/dev/null)
if [ "$ready_status" = "true" ]; then
    echo "✅ Ready endpoint: READY"
else
    echo "❌ Ready endpoint: $ready_status"
fi

# WebSocket endpoints
websocket_endpoints=("observatory" "emoji-rain" "anomalies" "doctor-status")
for endpoint in "${websocket_endpoints[@]}"; do
    if timeout 5 wscat -c "ws://localhost:8888/ws/$endpoint" >/dev/null 2>&1; then
        echo "✅ WebSocket /$endpoint: AVAILABLE"
    else
        echo "❌ WebSocket /$endpoint: UNAVAILABLE"
    fi
done

# Step 2: Restore service state
echo "Step 2: Restoring service state..."

# Restore Redis coordination
curl -X POST http://localhost:8888/admin/restore-coordination-state

# Restore WebSocket subscriptions (if backup available)
if [ -f "backup/websocket-subscriptions.json" ]; then
    curl -X POST http://localhost:8888/admin/restore-subscriptions \
         -H "Content-Type: application/json" \
         -d @backup/websocket-subscriptions.json
fi

# Step 3: Notify stakeholders
echo "Step 3: Notifying stakeholders..."

# Send recovery notification
curl -X POST "https://hooks.slack.com/services/..." \
     -d "{\"text\": \"✅ Observatory server recovery complete at $(date)\"}"

echo "Phase 3 complete - recovery successful"
echo "Total Recovery Time: $(($(date +%s) - START_TIME)) seconds"
```

### Scenario 2: Complete System Failure

**Symptoms:**
- Multiple services down simultaneously
- Network connectivity issues
- Hardware or infrastructure failure

**Impact Assessment:**
- **Business Impact:** Complete system outage
- **Affected Users:** All users and external services
- **Data Loss Risk:** All in-memory state, recent transactions

#### Recovery Procedure:

##### Emergency System Recovery
```bash
#!/bin/bash
# complete-system-recovery.sh

echo "=== COMPLETE SYSTEM RECOVERY INITIATED ==="
echo "Start Time: $(date)"

# Step 1: Infrastructure assessment
echo "Step 1: Infrastructure assessment..."

# Check system basics
ping -c 3 8.8.8.8 || echo "❌ No internet connectivity"
df -h | grep -E "(/$|/var|/tmp)" || echo "❌ Disk space issues"
free -h | grep Mem || echo "❌ Memory issues"

# Check critical services
systemctl is-active docker >/dev/null 2>&1 || echo "❌ Docker not running"
systemctl is-active redis >/dev/null 2>&1 || echo "❌ Redis not running"

# Step 2: Start infrastructure services
echo "Step 2: Starting infrastructure services..."

# Start Docker if needed
if ! systemctl is-active docker >/dev/null 2>&1; then
    sudo systemctl start docker
    sleep 10
fi

# Start Redis if needed
if ! systemctl is-active redis >/dev/null 2>&1; then
    sudo systemctl start redis
    sleep 5
fi

# Step 3: Restore from backup
echo "Step 3: Restoring from backup..."

# Restore configuration files
if [ -d "backup/config" ]; then
    cp -r backup/config/* config/
    echo "✅ Configuration restored"
fi

# Restore Redis data
if [ -f "backup/redis-dump.rdb" ]; then
    sudo systemctl stop redis
    sudo cp backup/redis-dump.rdb /var/lib/redis/dump.rdb
    sudo chown redis:redis /var/lib/redis/dump.rdb
    sudo systemctl start redis
    echo "✅ Redis data restored"
fi

# Step 4: Start all services in dependency order
echo "Step 4: Starting services in dependency order..."

# Start Redis coordination first
make redis-start

# Start Observatory server
make dashboard-up

# Start tunnel connection
make tunnel-start

# Start monitoring services
make prometheus-start
make grafana-start

# Step 5: Validate complete system
echo "Step 5: Validating complete system..."
./system-validation.sh

echo "Complete system recovery finished"
```

## Backup and Restore Procedures

### Automated Backup System

#### Daily Backup Schedule:
```bash
#!/bin/bash
# daily-backup.sh

BACKUP_DATE=$(date +%Y%m%d)
BACKUP_DIR="backups/$BACKUP_DATE"
mkdir -p "$BACKUP_DIR"

echo "Starting daily backup for $BACKUP_DATE"

# Configuration backup
echo "Backing up configuration files..."
tar -czf "$BACKUP_DIR/config-backup.tar.gz" config/
echo "✅ Configuration backup complete"

# Redis data backup
echo "Backing up Redis data..."
redis-cli -h 192.168.1.119 -p 6379 BGSAVE
sleep 10
scp user@192.168.1.119:/var/lib/redis/dump.rdb "$BACKUP_DIR/redis-primary.rdb"

redis-cli -h localhost -p 6380 BGSAVE
sleep 5
cp /var/lib/redis/dump.rdb "$BACKUP_DIR/redis-fallback.rdb"
echo "✅ Redis backup complete"

# Application state backup
echo "Backing up application state..."
curl -s http://localhost:8888/admin/export-state > "$BACKUP_DIR/observatory-state.json"
echo "✅ Application state backup complete"

# Log files backup
echo "Backing up log files..."
tar -czf "$BACKUP_DIR/logs-backup.tar.gz" logs/
echo "✅ Log files backup complete"

# Tunnel configuration backup
echo "Backing up tunnel configuration..."
cp ~/.cloudflared/cert.pem "$BACKUP_DIR/tunnel-cert.pem" 2>/dev/null || true
cp ~/.cloudflared/credentials.json "$BACKUP_DIR/tunnel-credentials.json" 2>/dev/null || true
cp cloudflared-config.yml "$BACKUP_DIR/tunnel-config.yml"
echo "✅ Tunnel configuration backup complete"

# Create backup manifest
cat > "$BACKUP_DIR/backup-manifest.json" << EOF
{
  "backup_date": "$BACKUP_DATE",
  "backup_time": "$(date -Iseconds)",
  "components": [
    "configuration",
    "redis_data",
    "application_state",
    "log_files",
    "tunnel_configuration"
  ],
  "backup_size": "$(du -sh $BACKUP_DIR | cut -f1)",
  "retention_days": 30
}
EOF

echo "Daily backup complete: $BACKUP_DIR"
```

#### Backup Validation:
```bash
#!/bin/bash
# validate-backup.sh

BACKUP_DIR=$1
if [ -z "$BACKUP_DIR" ]; then
    echo "Usage: $0 <backup_directory>"
    exit 1
fi

echo "Validating backup: $BACKUP_DIR"

# Check backup manifest
if [ -f "$BACKUP_DIR/backup-manifest.json" ]; then
    echo "✅ Backup manifest found"
    jq . "$BACKUP_DIR/backup-manifest.json"
else
    echo "❌ Backup manifest missing"
    exit 1
fi

# Validate configuration backup
if tar -tzf "$BACKUP_DIR/config-backup.tar.gz" >/dev/null 2>&1; then
    echo "✅ Configuration backup valid"
else
    echo "❌ Configuration backup corrupted"
fi

# Validate Redis backups
if [ -f "$BACKUP_DIR/redis-primary.rdb" ]; then
    echo "✅ Redis primary backup found"
else
    echo "❌ Redis primary backup missing"
fi

# Validate application state
if jq . "$BACKUP_DIR/observatory-state.json" >/dev/null 2>&1; then
    echo "✅ Application state backup valid"
else
    echo "❌ Application state backup invalid"
fi

echo "Backup validation complete"
```

### Restore Procedures

#### Configuration Restore:
```bash
#!/bin/bash
# restore-configuration.sh

BACKUP_DIR=$1
if [ -z "$BACKUP_DIR" ]; then
    echo "Usage: $0 <backup_directory>"
    exit 1
fi

echo "Restoring configuration from: $BACKUP_DIR"

# Backup current configuration
cp -r config/ config-backup-$(date +%Y%m%d-%H%M%S)/

# Restore configuration files
tar -xzf "$BACKUP_DIR/config-backup.tar.gz"
echo "✅ Configuration files restored"

# Restore tunnel configuration
if [ -f "$BACKUP_DIR/tunnel-config.yml" ]; then
    cp "$BACKUP_DIR/tunnel-config.yml" cloudflared-config.yml
    echo "✅ Tunnel configuration restored"
fi

# Validate configuration
make validate-config
echo "Configuration restore complete"
```

#### Data Restore:
```bash
#!/bin/bash
# restore-data.sh

BACKUP_DIR=$1
if [ -z "$BACKUP_DIR" ]; then
    echo "Usage: $0 <backup_directory>"
    exit 1
fi

echo "Restoring data from: $BACKUP_DIR"

# Stop services
make dashboard-stop
sudo systemctl stop redis

# Restore Redis data
if [ -f "$BACKUP_DIR/redis-primary.rdb" ]; then
    sudo cp "$BACKUP_DIR/redis-primary.rdb" /var/lib/redis/dump.rdb
    sudo chown redis:redis /var/lib/redis/dump.rdb
    echo "✅ Redis data restored"
fi

# Start services
sudo systemctl start redis
sleep 5
make dashboard-up

# Restore application state
if [ -f "$BACKUP_DIR/observatory-state.json" ]; then
    curl -X POST http://localhost:8888/admin/import-state \
         -H "Content-Type: application/json" \
         -d @"$BACKUP_DIR/observatory-state.json"
    echo "✅ Application state restored"
fi

echo "Data restore complete"
```

## Emergency Escalation Procedures

### Escalation Matrix

| Incident Severity | Initial Response | Escalation Time | Escalation Target |
|-------------------|------------------|-----------------|-------------------|
| **P0 - Critical** | On-call Engineer | Immediate | Engineering Manager |
| **P1 - High** | On-call Engineer | 15 minutes | Senior Engineer |
| **P2 - Medium** | Assigned Engineer | 1 hour | Team Lead |
| **P3 - Low** | Assigned Engineer | 4 hours | Team Lead |

### Contact Information

#### Primary Contacts:
```yaml
on_call_engineer:
  name: "Primary On-Call"
  phone: "+1-555-0123"
  email: "oncall@company.com"
  slack: "@oncall-engineer"

engineering_manager:
  name: "Engineering Manager"
  phone: "+1-555-0124"
  email: "eng-manager@company.com"
  slack: "@eng-manager"

senior_engineer:
  name: "Senior Engineer"
  phone: "+1-555-0125"
  email: "senior-eng@company.com"
  slack: "@senior-engineer"

infrastructure_team:
  email: "infrastructure@company.com"
  slack: "#infrastructure-alerts"
  pagerduty: "infrastructure-team"
```

#### Emergency Notification Script:
```bash
#!/bin/bash
# emergency-notification.sh

SEVERITY=$1
INCIDENT_DESCRIPTION=$2

if [ -z "$SEVERITY" ] || [ -z "$INCIDENT_DESCRIPTION" ]; then
    echo "Usage: $0 <severity> <description>"
    echo "Severity: P0, P1, P2, P3"
    exit 1
fi

echo "Sending emergency notification - Severity: $SEVERITY"

# Slack notification
slack_message="{
    \"text\": \"🚨 $SEVERITY INCIDENT: $INCIDENT_DESCRIPTION\",
    \"channel\": \"#infrastructure-alerts\",
    \"username\": \"Observatory Alert Bot\"
}"

curl -X POST "https://hooks.slack.com/services/..." \
     -H "Content-Type: application/json" \
     -d "$slack_message"

# Email notification
case $SEVERITY in
    P0)
        # Critical - notify everyone immediately
        echo "$INCIDENT_DESCRIPTION" | mail -s "🚨 P0 CRITICAL: Observatory System" \
            oncall@company.com,eng-manager@company.com,infrastructure@company.com
        ;;
    P1)
        # High - notify on-call and senior engineer
        echo "$INCIDENT_DESCRIPTION" | mail -s "⚠️ P1 HIGH: Observatory System" \
            oncall@company.com,senior-eng@company.com
        ;;
    P2|P3)
        # Medium/Low - notify team
        echo "$INCIDENT_DESCRIPTION" | mail -s "ℹ️ $SEVERITY: Observatory System" \
            infrastructure@company.com
        ;;
esac

# PagerDuty integration (if configured)
if [ "$SEVERITY" = "P0" ] || [ "$SEVERITY" = "P1" ]; then
    curl -X POST "https://events.pagerduty.com/v2/enqueue" \
         -H "Content-Type: application/json" \
         -d "{
             \"routing_key\": \"$PAGERDUTY_ROUTING_KEY\",
             \"event_action\": \"trigger\",
             \"payload\": {
                 \"summary\": \"$SEVERITY: $INCIDENT_DESCRIPTION\",
                 \"source\": \"Observatory System\",
                 \"severity\": \"critical\"
             }
         }"
fi

echo "Emergency notifications sent for $SEVERITY incident"
```

## Fallback Mechanisms and Service Isolation

### Service Isolation Procedures

#### Observatory Server Isolation:
```bash
#!/bin/bash
# isolate-observatory.sh

echo "Isolating Observatory server..."

# Stop external access
make tunnel-stop
echo "✅ External access disabled"

# Isolate WebSocket connections
iptables -A INPUT -p tcp --dport 8888 -j DROP
echo "✅ WebSocket connections blocked"

# Preserve internal monitoring
iptables -I INPUT -s 127.0.0.1 -p tcp --dport 8888 -j ACCEPT
iptables -I INPUT -s 192.168.1.0/24 -p tcp --dport 8888 -j ACCEPT
echo "✅ Internal monitoring preserved"

# Enable maintenance mode
curl -X POST http://localhost:8888/admin/maintenance-mode
echo "✅ Maintenance mode enabled"

echo "Observatory server isolated successfully"
```

#### Service Failover:
```bash
#!/bin/bash
# service-failover.sh

SERVICE=$1
if [ -z "$SERVICE" ]; then
    echo "Usage: $0 <service>"
    echo "Services: observatory, redis, tunnel, prometheus, grafana"
    exit 1
fi

echo "Initiating failover for service: $SERVICE"

case $SERVICE in
    observatory)
        # Observatory failover to backup instance
        echo "Starting backup Observatory instance..."
        # Implementation depends on backup infrastructure
        ;;
    redis)
        # Redis failover to secondary
        echo "Switching to Redis fallback..."
        curl -X POST http://localhost:8888/admin/redis-failover
        ;;
    tunnel)
        # Tunnel failover to backup tunnel
        echo "Activating backup tunnel..."
        # Implementation depends on backup tunnel configuration
        ;;
    *)
        echo "Unknown service: $SERVICE"
        exit 1
        ;;
esac

echo "Failover complete for $SERVICE"
```

## Success Criteria

### Recovery Objectives:
- ✅ RTO/RPO defined for all critical services
- ✅ Step-by-step recovery procedures with validation checkpoints
- ✅ Automated backup system with daily execution
- ✅ Backup validation and restore procedures tested
- ✅ Emergency escalation procedures with contact information

### Operational Requirements:
- ✅ Recovery procedures tested monthly
- ✅ Backup integrity validated weekly
- ✅ Emergency contact information updated quarterly
- ✅ Disaster recovery documentation reviewed quarterly
- ✅ Service isolation procedures validated and ready

### Integration Requirements:
- ✅ Integration with monitoring and alerting systems
- ✅ Coordination with emergency protocol systems
- ✅ Automated notification and escalation procedures
- ✅ Fallback mechanisms for all critical services

This disaster recovery system provides comprehensive procedures for maintaining service continuity and rapid recovery from various failure scenarios in the Beast Mode Observatory infrastructure.