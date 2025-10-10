# DAG Orchestration Operations Runbook

## Overview

This runbook provides comprehensive operational procedures for deploying, monitoring, and maintaining the DAG orchestration system in production environments. It covers deployment strategies, monitoring setup, incident response, and maintenance procedures.

## Production Deployment

### 1. Pre-Deployment Checklist

Before deploying to production, ensure all prerequisites are met:

```bash
# Run comprehensive pre-deployment check
bash scripts/check_dag_orchestrated_parallel_execution_prereqs.sh --production

# Verify system requirements
python scripts/validate_production_readiness.py

# Check security compliance
python scripts/validate_security_compliance.py
```

#### System Requirements

**Minimum Production Requirements:**
- **CPU**: 4+ cores (8+ recommended)
- **Memory**: 8GB RAM (16GB+ recommended)
- **Disk**: 50GB+ free space (SSD recommended)
- **Network**: Stable internet connection for LLM providers
- **Redis**: Dedicated Redis instance with persistence enabled

**Recommended Production Setup:**
- **Load Balancer**: For high availability
- **Monitoring**: Prometheus + Grafana stack
- **Logging**: Centralized logging (ELK stack or similar)
- **Backup**: Automated backup for Redis and execution logs

### 2. Deployment Strategies

#### Strategy A: Single Machine Deployment

For smaller workloads or development environments:

```bash
# Deploy single machine setup
python scripts/deploy_single_machine.py --environment production

# Verify deployment
curl http://localhost:8888/health
curl http://localhost:8888/ready
```

**Configuration:**
```yaml
# production_config.yaml
deployment:
  type: single_machine
  max_workers: 8
  resource_limits:
    max_cpu_percent: 80
    max_memory_percent: 75
  
redis:
  host: localhost
  port: 6379
  password: ${REDIS_PASSWORD}
  persistence: true

monitoring:
  prometheus_port: 9090
  grafana_port: 3000
  log_level: INFO
```

#### Strategy B: Distributed Deployment

For high-availability and scalable workloads:

```bash
# Deploy distributed setup
python scripts/deploy_distributed.py --config distributed_config.yaml

# Verify all nodes
python scripts/verify_distributed_deployment.py
```

**Architecture:**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Orchestrator  │    │   Worker Nodes  │
│                 │    │     Nodes       │    │                 │
│  - HAProxy      │────│  - DAG Manager  │────│  - Task Exec    │
│  - Health Check │    │  - Scheduler    │    │  - LLM Engines  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Shared Storage │
                    │                 │
                    │  - Redis Cluster│
                    │  - Metrics DB   │
                    │  - Log Storage  │
                    └─────────────────┘
```

#### Strategy C: Container Deployment

Using Docker and Kubernetes:

```bash
# Build production images
docker build -t dag-orchestration:latest .

# Deploy to Kubernetes
kubectl apply -f k8s/production/

# Verify deployment
kubectl get pods -l app=dag-orchestration
kubectl get services -l app=dag-orchestration
```

**Kubernetes Manifests:**
```yaml
# k8s/production/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dag-orchestration
  labels:
    app: dag-orchestration
spec:
  replicas: 3
  selector:
    matchLabels:
      app: dag-orchestration
  template:
    metadata:
      labels:
        app: dag-orchestration
    spec:
      containers:
      - name: dag-orchestrator
        image: dag-orchestration:latest
        ports:
        - containerPort: 8888
        env:
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        - name: EXECUTION_MODE
          value: "production"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8888
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8888
          initialDelaySeconds: 5
          periodSeconds: 5
```

### 3. Environment Configuration

#### Production Environment Variables

```bash
# Core configuration
export EXECUTION_MODE=production
export LOG_LEVEL=INFO
export MAX_WORKERS=8

# Redis configuration
export REDIS_URL=redis://redis.production.local:6379
export REDIS_PASSWORD=${REDIS_PASSWORD}
export REDIS_TIMEOUT=30

# LLM configuration
export LLM_COST_BUDGET=100.0
export LLM_PREFERRED_PROVIDERS=cursor,kiro

# Monitoring configuration
export PROMETHEUS_PORT=9090
export METRICS_ENABLED=true
export HEALTH_CHECK_INTERVAL=30

# Security configuration
export ENABLE_AUTH=true
export API_KEY=${API_KEY}
export TLS_ENABLED=true
```

#### Configuration Validation

```python
#!/usr/bin/env python3
"""Production configuration validator."""

import os
import sys
from typing import Dict, List

def validate_production_config() -> bool:
    """Validate production configuration."""
    
    required_vars = [
        'EXECUTION_MODE',
        'REDIS_URL', 
        'REDIS_PASSWORD',
        'API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        return False
    
    # Validate Redis connectivity
    try:
        import redis
        r = redis.Redis.from_url(os.getenv('REDIS_URL'), password=os.getenv('REDIS_PASSWORD'))
        r.ping()
        print("✅ Redis connectivity verified")
    except Exception as e:
        print(f"❌ Redis connectivity failed: {e}")
        return False
    
    # Validate resource limits
    max_workers = int(os.getenv('MAX_WORKERS', 4))
    if max_workers > 16:
        print("⚠️  Warning: MAX_WORKERS > 16 may cause resource exhaustion")
    
    print("✅ Production configuration validated")
    return True

if __name__ == "__main__":
    success = validate_production_config()
    sys.exit(0 if success else 1)
```

## Monitoring and Observability

### 1. Health Monitoring Setup

#### Health Check Endpoints

The system provides comprehensive health endpoints:

```bash
# Basic health check
curl http://localhost:8888/health
# Response: {"status": "healthy", "timestamp": "2024-01-27T10:30:00Z"}

# Readiness check (for load balancers)
curl http://localhost:8888/ready
# Response: {"ready": true, "components": {"redis": "connected", "workers": "available"}}

# Detailed status
curl http://localhost:8888/status
# Response: Detailed system status including active tasks, resource usage, etc.

# Prometheus metrics
curl http://localhost:8888/metrics
# Response: Prometheus-formatted metrics
```

#### Health Check Script

```bash
#!/bin/bash
# health_check.sh - Comprehensive health monitoring

set -e

HEALTH_ENDPOINT="http://localhost:8888/health"
READY_ENDPOINT="http://localhost:8888/ready"
METRICS_ENDPOINT="http://localhost:8888/metrics"

echo "🏥 DAG Orchestration Health Check"
echo "================================="

# Basic health check
echo "Checking basic health..."
if curl -s -f "$HEALTH_ENDPOINT" > /dev/null; then
    echo "✅ Health endpoint responding"
else
    echo "❌ Health endpoint not responding"
    exit 1
fi

# Readiness check
echo "Checking readiness..."
READY_RESPONSE=$(curl -s "$READY_ENDPOINT")
if echo "$READY_RESPONSE" | grep -q '"ready": true'; then
    echo "✅ System ready"
else
    echo "❌ System not ready: $READY_RESPONSE"
    exit 1
fi

# Metrics check
echo "Checking metrics..."
if curl -s -f "$METRICS_ENDPOINT" | grep -q "dag_orchestration"; then
    echo "✅ Metrics available"
else
    echo "❌ Metrics not available"
    exit 1
fi

# Resource check
echo "Checking system resources..."
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')

echo "CPU Usage: ${CPU_USAGE}%"
echo "Memory Usage: ${MEMORY_USAGE}%"

if (( $(echo "$CPU_USAGE > 90" | bc -l) )); then
    echo "⚠️  High CPU usage detected"
fi

if (( $(echo "$MEMORY_USAGE > 85" | bc -l) )); then
    echo "⚠️  High memory usage detected"
fi

echo "✅ Health check completed successfully"
```

### 2. Prometheus Metrics Configuration

#### Metrics Collection Setup

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "dag_orchestration_rules.yml"

scrape_configs:
  - job_name: 'dag-orchestration'
    static_configs:
      - targets: ['localhost:8888']
    metrics_path: '/metrics'
    scrape_interval: 10s
    
  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:9121']  # Redis exporter
    
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

#### Key Metrics to Monitor

```yaml
# dag_orchestration_rules.yml
groups:
- name: dag_orchestration
  rules:
  
  # Task execution metrics
  - alert: HighTaskFailureRate
    expr: rate(dag_orchestration_tasks_total{status="failed"}[5m]) > 0.1
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High task failure rate detected"
      description: "Task failure rate is {{ $value }} failures/second"
  
  # Execution duration alerts
  - alert: SlowDAGExecution
    expr: dag_orchestration_execution_duration_seconds > 3600
    for: 1m
    labels:
      severity: warning
    annotations:
      summary: "DAG execution taking too long"
      description: "DAG execution duration is {{ $value }} seconds"
  
  # Resource usage alerts
  - alert: HighResourceUsage
    expr: dag_orchestration_resource_usage_percent{resource_type="cpu"} > 90
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High CPU usage in DAG orchestration"
      description: "CPU usage is {{ $value }}%"
  
  # Cost monitoring
  - alert: HighLLMCost
    expr: increase(dag_orchestration_llm_cost_total[1h]) > 50
    for: 1m
    labels:
      severity: warning
    annotations:
      summary: "High LLM costs detected"
      description: "LLM costs increased by ${{ $value }} in the last hour"
```

### 3. Grafana Dashboard Setup

#### Dashboard Configuration

```json
{
  "dashboard": {
    "title": "DAG Orchestration Monitoring",
    "panels": [
      {
        "title": "Task Execution Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(dag_orchestration_tasks_total[5m])",
            "legendFormat": "{{status}}"
          }
        ]
      },
      {
        "title": "Active Tasks",
        "type": "singlestat",
        "targets": [
          {
            "expr": "dag_orchestration_active_tasks"
          }
        ]
      },
      {
        "title": "Resource Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "dag_orchestration_resource_usage_percent",
            "legendFormat": "{{resource_type}}"
          }
        ]
      },
      {
        "title": "LLM Cost Tracking",
        "type": "graph",
        "targets": [
          {
            "expr": "increase(dag_orchestration_llm_cost_total[1h])",
            "legendFormat": "{{provider}}"
          }
        ]
      }
    ]
  }
}
```

## Incident Response

### 1. Common Incident Types

#### High Priority Incidents

**P1 - System Down**
- All DAG executions failing
- Health endpoints not responding
- Complete system unavailability

**P2 - Degraded Performance**
- High task failure rates (>10%)
- Slow execution times (>2x normal)
- Resource exhaustion warnings

**P3 - Partial Issues**
- Individual task failures
- LLM provider issues
- Non-critical component failures

### 2. Incident Response Procedures

#### P1 Incident Response

```bash
#!/bin/bash
# p1_incident_response.sh

echo "🚨 P1 INCIDENT RESPONSE - SYSTEM DOWN"
echo "===================================="

# 1. Immediate assessment
echo "Step 1: System Assessment"
echo "Checking system status..."

# Check if processes are running
if pgrep -f "dag_orchestration" > /dev/null; then
    echo "✅ DAG orchestration processes running"
else
    echo "❌ DAG orchestration processes not running"
    echo "🔧 Attempting to restart..."
    python scripts/start_dag_orchestration.py --emergency
fi

# Check Redis connectivity
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis responding"
else
    echo "❌ Redis not responding"
    echo "🔧 Checking Redis status..."
    systemctl status redis-server
fi

# 2. Check system resources
echo "Step 2: Resource Check"
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')"
echo "Memory Usage: $(free -h | grep Mem | awk '{print $3 "/" $2}')"
echo "Disk Usage: $(df -h / | tail -1 | awk '{print $5}')"

# 3. Check logs for errors
echo "Step 3: Log Analysis"
echo "Recent errors:"
tail -50 /var/log/dag_orchestration/error.log | grep ERROR

# 4. Attempt recovery
echo "Step 4: Recovery Actions"
echo "Killing any stuck processes..."
pkill -f "dag_orchestration"

echo "Clearing Redis locks..."
redis-cli --scan --pattern "dag_lock:*" | xargs redis-cli del

echo "Restarting system..."
python scripts/start_dag_orchestration.py --clean-start

# 5. Verify recovery
echo "Step 5: Verification"
sleep 10
if curl -s http://localhost:8888/health > /dev/null; then
    echo "✅ System recovered successfully"
else
    echo "❌ Recovery failed - escalating to on-call engineer"
    # Send alert to on-call
    python scripts/send_alert.py --severity critical --message "P1 incident: System recovery failed"
fi
```

#### P2 Incident Response

```bash
#!/bin/bash
# p2_incident_response.sh

echo "⚠️  P2 INCIDENT RESPONSE - DEGRADED PERFORMANCE"
echo "=============================================="

# 1. Performance analysis
echo "Step 1: Performance Analysis"
python scripts/analyze_performance_degradation.py --last-hour

# 2. Resource optimization
echo "Step 2: Resource Optimization"
echo "Adjusting worker count based on load..."
python scripts/adjust_worker_count.py --auto-optimize

echo "Clearing completed task results..."
python scripts/cleanup_task_results.py --older-than 1h

# 3. Check for resource leaks
echo "Step 3: Resource Leak Detection"
python scripts/detect_resource_leaks.py

# 4. LLM provider health check
echo "Step 4: LLM Provider Check"
python scripts/check_llm_providers.py --health-check

# 5. Gradual recovery
echo "Step 5: Gradual Recovery"
echo "Implementing gradual load increase..."
python scripts/gradual_load_recovery.py
```

### 3. Escalation Procedures

#### Escalation Matrix

| Incident Type | Response Time | Escalation Path |
|---------------|---------------|-----------------|
| P1 - System Down | 5 minutes | On-call Engineer → Team Lead → Manager |
| P2 - Degraded | 15 minutes | On-call Engineer → Team Lead |
| P3 - Partial | 1 hour | Assigned Engineer |

#### Escalation Script

```python
#!/usr/bin/env python3
"""Incident escalation automation."""

import os
import time
from datetime import datetime
from typing import Dict, List

class IncidentEscalation:
    """Automated incident escalation system."""
    
    def __init__(self):
        self.escalation_config = {
            'P1': {'response_time': 300, 'contacts': ['oncall', 'lead', 'manager']},
            'P2': {'response_time': 900, 'contacts': ['oncall', 'lead']},
            'P3': {'response_time': 3600, 'contacts': ['assigned']}
        }
        
    def create_incident(self, severity: str, description: str) -> str:
        """Create new incident and start escalation timer."""
        
        incident_id = f"INC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        incident_data = {
            'id': incident_id,
            'severity': severity,
            'description': description,
            'created_at': datetime.now(),
            'status': 'OPEN',
            'assigned_to': None,
            'escalation_level': 0
        }
        
        # Store incident data
        self.store_incident(incident_data)
        
        # Send initial alert
        self.send_alert(incident_data, 'created')
        
        # Start escalation timer
        self.start_escalation_timer(incident_id)
        
        return incident_id
    
    def send_alert(self, incident: Dict, alert_type: str):
        """Send alert to appropriate contacts."""
        
        severity = incident['severity']
        contacts = self.escalation_config[severity]['contacts']
        
        message = f"""
🚨 INCIDENT ALERT - {alert_type.upper()}

Incident ID: {incident['id']}
Severity: {severity}
Description: {incident['description']}
Created: {incident['created_at']}
Status: {incident['status']}

Dashboard: http://grafana.local/d/dag-orchestration
Runbook: https://docs.local/dag-orchestration/operations-runbook
        """
        
        for contact in contacts:
            self.notify_contact(contact, message, severity)
    
    def notify_contact(self, contact: str, message: str, severity: str):
        """Send notification to specific contact."""
        
        # Implementation would integrate with:
        # - Slack/Teams for chat notifications
        # - PagerDuty for on-call alerts
        # - Email for non-urgent notifications
        # - SMS for critical alerts
        
        print(f"📱 Notifying {contact}: {severity} incident")
        
        # Example integrations:
        if contact == 'oncall':
            self.send_pagerduty_alert(message, severity)
        elif contact in ['lead', 'manager']:
            self.send_slack_message(message, severity)
        else:
            self.send_email(contact, message, severity)
```

## Maintenance Procedures

### 1. Regular Maintenance Tasks

#### Daily Maintenance

```bash
#!/bin/bash
# daily_maintenance.sh

echo "📅 Daily DAG Orchestration Maintenance"
echo "====================================="

# 1. Health check
echo "Running health check..."
bash scripts/health_check.sh

# 2. Log rotation
echo "Rotating logs..."
logrotate /etc/logrotate.d/dag_orchestration

# 3. Cleanup old execution data
echo "Cleaning up old execution data..."
python scripts/cleanup_execution_data.py --older-than 7d

# 4. Redis maintenance
echo "Redis maintenance..."
redis-cli BGREWRITEAOF  # Rewrite AOF file
redis-cli MEMORY PURGE  # Free unused memory

# 5. Performance metrics collection
echo "Collecting performance metrics..."
python scripts/collect_daily_metrics.py

# 6. Backup critical data
echo "Backing up critical data..."
python scripts/backup_dag_data.py --daily

echo "✅ Daily maintenance completed"
```

#### Weekly Maintenance

```bash
#!/bin/bash
# weekly_maintenance.sh

echo "📅 Weekly DAG Orchestration Maintenance"
echo "======================================"

# 1. Performance analysis
echo "Analyzing weekly performance..."
python scripts/analyze_weekly_performance.py

# 2. Capacity planning
echo "Updating capacity planning..."
python scripts/update_capacity_planning.py

# 3. Security updates
echo "Checking for security updates..."
python scripts/check_security_updates.py

# 4. Configuration validation
echo "Validating configuration..."
python scripts/validate_production_config.py

# 5. Disaster recovery test
echo "Testing disaster recovery procedures..."
python scripts/test_disaster_recovery.py --dry-run

echo "✅ Weekly maintenance completed"
```

### 2. Backup and Recovery

#### Backup Strategy

```python
#!/usr/bin/env python3
"""Comprehensive backup system for DAG orchestration."""

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

class DAGBackupManager:
    """Manages backups for DAG orchestration system."""
    
    def __init__(self, backup_dir: str = "/backups/dag_orchestration"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def create_full_backup(self) -> str:
        """Create full system backup."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"full_backup_{timestamp}"
        backup_path.mkdir()
        
        print(f"🔄 Creating full backup: {backup_path}")
        
        # 1. Backup Redis data
        self.backup_redis(backup_path / "redis")
        
        # 2. Backup execution logs
        self.backup_logs(backup_path / "logs")
        
        # 3. Backup configuration
        self.backup_configuration(backup_path / "config")
        
        # 4. Backup database (if using SQLite)
        self.backup_database(backup_path / "database")
        
        # 5. Create backup manifest
        self.create_backup_manifest(backup_path)
        
        # 6. Compress backup
        compressed_backup = self.compress_backup(backup_path)
        
        print(f"✅ Full backup completed: {compressed_backup}")
        return str(compressed_backup)
    
    def backup_redis(self, backup_path: Path):
        """Backup Redis data."""
        
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Create Redis snapshot
        subprocess.run(["redis-cli", "BGSAVE"], check=True)
        
        # Wait for snapshot to complete
        import time
        while True:
            result = subprocess.run(
                ["redis-cli", "LASTSAVE"], 
                capture_output=True, 
                text=True
            )
            if "OK" in result.stdout:
                break
            time.sleep(1)
        
        # Copy Redis dump file
        redis_dump = Path("/var/lib/redis/dump.rdb")
        if redis_dump.exists():
            shutil.copy2(redis_dump, backup_path / "dump.rdb")
            print("✅ Redis data backed up")
    
    def restore_from_backup(self, backup_file: str):
        """Restore system from backup."""
        
        print(f"🔄 Restoring from backup: {backup_file}")
        
        # 1. Stop DAG orchestration services
        subprocess.run(["systemctl", "stop", "dag-orchestration"], check=True)
        
        # 2. Extract backup
        backup_path = self.extract_backup(backup_file)
        
        # 3. Restore Redis data
        self.restore_redis(backup_path / "redis")
        
        # 4. Restore configuration
        self.restore_configuration(backup_path / "config")
        
        # 5. Restore database
        self.restore_database(backup_path / "database")
        
        # 6. Start services
        subprocess.run(["systemctl", "start", "dag-orchestration"], check=True)
        
        # 7. Verify restoration
        if self.verify_restoration():
            print("✅ System restored successfully")
        else:
            print("❌ Restoration verification failed")
            raise RuntimeError("System restoration failed")
```

### 3. Performance Optimization

#### Regular Performance Tuning

```python
#!/usr/bin/env python3
"""Automated performance optimization."""

import psutil
import time
from typing import Dict, Any

class PerformanceOptimizer:
    """Automated performance optimization system."""
    
    def __init__(self):
        self.optimization_history = []
        self.current_config = self.load_current_config()
        
    def analyze_system_performance(self) -> Dict[str, Any]:
        """Analyze current system performance."""
        
        # Collect system metrics
        cpu_percent = psutil.cpu_percent(interval=5)
        memory = psutil.virtual_memory()
        disk_io = psutil.disk_io_counters()
        
        # Analyze DAG execution metrics
        dag_metrics = self.get_dag_execution_metrics()
        
        analysis = {
            'cpu_utilization': cpu_percent,
            'memory_utilization': memory.percent,
            'memory_available_gb': memory.available / (1024**3),
            'disk_io_read_mb_s': disk_io.read_bytes / (1024**2),
            'disk_io_write_mb_s': disk_io.write_bytes / (1024**2),
            'avg_task_duration': dag_metrics.get('avg_task_duration', 0),
            'task_failure_rate': dag_metrics.get('failure_rate', 0),
            'queue_length': dag_metrics.get('queue_length', 0),
            'parallelization_efficiency': dag_metrics.get('parallelization_efficiency', 0)
        }
        
        return analysis
    
    def generate_optimization_recommendations(self, analysis: Dict[str, Any]) -> List[Dict]:
        """Generate optimization recommendations based on analysis."""
        
        recommendations = []
        
        # CPU optimization
        if analysis['cpu_utilization'] < 40:
            recommendations.append({
                'type': 'increase_workers',
                'current_workers': self.current_config.get('max_workers', 4),
                'recommended_workers': min(12, self.current_config.get('max_workers', 4) + 2),
                'reason': 'Low CPU utilization indicates capacity for more parallel tasks'
            })
        elif analysis['cpu_utilization'] > 85:
            recommendations.append({
                'type': 'decrease_workers',
                'current_workers': self.current_config.get('max_workers', 4),
                'recommended_workers': max(1, self.current_config.get('max_workers', 4) - 1),
                'reason': 'High CPU utilization may cause performance degradation'
            })
        
        # Memory optimization
        if analysis['memory_utilization'] > 80:
            recommendations.append({
                'type': 'enable_memory_cleanup',
                'action': 'Implement aggressive memory cleanup',
                'reason': 'High memory usage detected'
            })
        
        # Task execution optimization
        if analysis['task_failure_rate'] > 0.05:  # 5% failure rate
            recommendations.append({
                'type': 'increase_timeouts',
                'action': 'Increase task timeouts by 50%',
                'reason': f"High failure rate: {analysis['task_failure_rate']*100:.1f}%"
            })
        
        # Queue optimization
        if analysis['queue_length'] > 20:
            recommendations.append({
                'type': 'scale_workers',
                'action': 'Increase worker count to handle queue backlog',
                'reason': f"Long queue detected: {analysis['queue_length']} tasks"
            })
        
        return recommendations
    
    def apply_optimizations(self, recommendations: List[Dict]) -> bool:
        """Apply optimization recommendations."""
        
        print("🔧 Applying performance optimizations...")
        
        for rec in recommendations:
            try:
                if rec['type'] == 'increase_workers':
                    self.update_worker_count(rec['recommended_workers'])
                elif rec['type'] == 'decrease_workers':
                    self.update_worker_count(rec['recommended_workers'])
                elif rec['type'] == 'enable_memory_cleanup':
                    self.enable_aggressive_memory_cleanup()
                elif rec['type'] == 'increase_timeouts':
                    self.increase_task_timeouts()
                elif rec['type'] == 'scale_workers':
                    self.scale_workers_for_queue()
                
                print(f"✅ Applied: {rec['type']}")
                
            except Exception as e:
                print(f"❌ Failed to apply {rec['type']}: {e}")
                return False
        
        return True
```

## Security Procedures

### 1. Security Monitoring

```bash
#!/bin/bash
# security_monitoring.sh

echo "🔒 DAG Orchestration Security Monitoring"
echo "======================================="

# 1. Check for hardcoded credentials
echo "Scanning for hardcoded credentials..."
python scripts/scan_for_hardcoded_credentials.py --all-files

# 2. Validate TLS configuration
echo "Validating TLS configuration..."
python scripts/validate_tls_configuration.py

# 3. Check access logs for suspicious activity
echo "Analyzing access logs..."
python scripts/analyze_access_logs.py --suspicious-patterns

# 4. Verify API authentication
echo "Testing API authentication..."
python scripts/test_api_authentication.py

# 5. Check Redis security
echo "Validating Redis security..."
redis-cli CONFIG GET requirepass
redis-cli CONFIG GET protected-mode

echo "✅ Security monitoring completed"
```

### 2. Security Incident Response

```python
#!/usr/bin/env python3
"""Security incident response procedures."""

class SecurityIncidentResponse:
    """Handles security incidents in DAG orchestration system."""
    
    def __init__(self):
        self.incident_log = []
        
    def handle_credential_exposure(self, credential_type: str, exposure_details: Dict):
        """Handle exposed credential incident."""
        
        print(f"🚨 SECURITY INCIDENT: {credential_type} credential exposure")
        
        # 1. Immediate containment
        self.rotate_credentials(credential_type)
        
        # 2. Assess impact
        impact = self.assess_credential_exposure_impact(credential_type, exposure_details)
        
        # 3. Notify security team
        self.notify_security_team(credential_type, impact)
        
        # 4. Update security measures
        self.enhance_credential_security()
        
    def handle_unauthorized_access(self, access_details: Dict):
        """Handle unauthorized access attempt."""
        
        print("🚨 SECURITY INCIDENT: Unauthorized access detected")
        
        # 1. Block suspicious IP
        self.block_ip_address(access_details.get('source_ip'))
        
        # 2. Audit access logs
        self.audit_access_logs(access_details.get('timeframe'))
        
        # 3. Reset affected sessions
        self.reset_user_sessions()
        
        # 4. Strengthen access controls
        self.strengthen_access_controls()
```

This operations runbook provides comprehensive procedures for deploying, monitoring, and maintaining the DAG orchestration system in production environments. It covers all aspects from deployment strategies to incident response and security procedures.