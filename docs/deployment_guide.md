# Beast Mode Deployment Guide

This guide covers the complete deployment and configuration management system for the Beast Mode Agent Collaboration Network.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Configuration Management](#configuration-management)
4. [Deployment Types](#deployment-types)
5. [Service Monitoring](#service-monitoring)
6. [Validation and Testing](#validation-and-testing)
7. [Production Deployment](#production-deployment)
8. [Troubleshooting](#troubleshooting)

## Overview

The Beast Mode deployment system provides:

- **Configuration Management**: Environment-specific configurations with validation
- **Multiple Deployment Types**: Single machine, distributed, Docker, and Kubernetes
- **Service Monitoring**: Process monitoring, health checks, and automatic restart
- **Deployment Validation**: Comprehensive testing and smoke tests
- **Production Ready**: Security, monitoring, and operational best practices

### Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Config Manager  │    │ Deployment Mgr  │    │ Service Monitor │
│                 │    │                 │    │                 │
│ - Environments  │    │ - Single Machine│    │ - Health Checks │
│ - Validation    │    │ - Distributed   │    │ - Auto Restart  │
│ - Env Variables │    │ - Docker        │    │ - Metrics       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Validator       │
                    │                 │
                    │ - Connectivity  │
                    │ - Performance   │
                    │ - Security      │
                    └─────────────────┘
```

## Quick Start

### Prerequisites

```bash
# Install Python dependencies
pip install redis pyyaml psutil

# Install Redis server
# macOS:
brew install redis

# Ubuntu:
sudo apt-get install redis-server

# Start Redis
redis-server
```

### Basic Deployment

```bash
# Single machine deployment
python scripts/deploy_single_machine.py \
  --environment development \
  --agent-id my_agent \
  --capabilities "python_coding,system_admin"

# Docker deployment
python scripts/deploy_docker.py \
  --environment docker \
  --agent-id docker_agent

# Distributed deployment
python scripts/deploy_distributed.py \
  --environment distributed \
  --nodes node1 node2 node3
```

### Demo

```bash
# Run the complete demo
python examples/deployment_demo.py
```

## Configuration Management

### Environment Types

The system supports multiple deployment environments:

- **development**: Local development with debug logging
- **staging**: Pre-production testing environment
- **production**: Production deployment with security enabled
- **single_machine**: All services on one machine
- **distributed**: Services distributed across multiple nodes

### Configuration Structure

```python
from beast_mode.deployment.config_manager import (
    ConfigManager, DeploymentConfig, RedisConfig, 
    AgentConfig, MonitoringConfig
)

# Create configuration
config = DeploymentConfig(
    environment=DeploymentEnvironment.PRODUCTION,
    redis=RedisConfig(
        host="redis.example.com",
        port=6379,
        password="secure_password",
        ssl=True
    ),
    agent=AgentConfig(
        agent_id="prod_agent_01",
        capabilities=["production", "monitoring"],
        log_level="INFO"
    ),
    monitoring=MonitoringConfig(
        health_check_interval=30,
        enable_performance_monitoring=True
    )
)
```

### Managing Configurations

```python
# Initialize config manager
config_manager = ConfigManager("./config")

# Save custom configuration
config_manager.save_config("my_env", config)

# Load configuration
config = config_manager.load_config("my_env")

# Validate configuration
issues = config_manager.validate_config(config)
if issues:
    print("Configuration issues:", issues)

# Generate environment variables
env_vars = config_manager.get_environment_variables("my_env")

# Create Docker environment file
config_manager.create_docker_env_file("my_env", ".env")
```

### Configuration Files

Configurations are stored as YAML files:

```yaml
# config/production.yaml
environment: production
redis:
  host: redis.example.com
  port: 6379
  password: secure_password
  ssl: true
  connection_pool_size: 20
agent:
  agent_id: prod_agent
  capabilities:
    - production
    - monitoring
  log_level: INFO
  heartbeat_interval: 60
monitoring:
  health_check_interval: 30
  metrics_collection_interval: 30
  enable_performance_monitoring: true
```

## Deployment Types

### Single Machine Deployment

Deploy all services on a single machine:

```python
from beast_mode.deployment.deployment_manager import DeploymentManager

deployment_manager = DeploymentManager(config_manager)

# Create deployment
deployment_id = deployment_manager.create_single_machine_deployment("development")

# Check status
status = deployment_manager.get_deployment_status(deployment_id)
print(f"Status: {status.status}")

# Health check
health = deployment_manager.health_check_deployment(deployment_id)
print(f"Health: {health['overall_status']}")

# Stop deployment
deployment_manager.stop_deployment(deployment_id)
```

**Services Created:**
- Redis server
- Mailbox logger
- Beast Mode agent

### Distributed Deployment

Deploy services across multiple nodes:

```python
nodes = ["node1.example.com", "node2.example.com", "node3.example.com"]
deployment_id = deployment_manager.create_distributed_deployment("distributed", nodes)
```

This creates:
- Deployment manifest (`deployment_{id}.json`)
- Node-specific deployment scripts
- Service distribution across nodes

**Manual Execution:**
```bash
# Copy scripts to nodes
scp deploy_node1.sh node1.example.com:~/
scp deploy_node2.sh node2.example.com:~/

# Execute on each node
ssh node1.example.com "./deploy_node1.sh"
ssh node2.example.com "./deploy_node2.sh"
```

### Docker Deployment

Deploy using Docker Compose:

```python
deployment_id = deployment_manager.create_docker_deployment("docker")
```

This creates:
- `docker-compose-{id}.yml`
- `.env-{id}` environment file
- Management scripts

**Docker Commands:**
```bash
# Start services
docker-compose -f docker-compose-{id}.yml --env-file .env-{id} up -d

# View logs
docker-compose -f docker-compose-{id}.yml logs -f

# Stop services
docker-compose -f docker-compose-{id}.yml down
```

### Kubernetes Deployment

For Kubernetes deployments, use the distributed deployment with `--kubernetes` flag:

```bash
python scripts/deploy_distributed.py \
  --environment production \
  --nodes k8s-cluster \
  --kubernetes
```

This creates:
- Kubernetes manifests in `kubernetes/` directory
- Redis deployment and service
- Agent deployment with replicas
- Persistent volume claims

**Kubernetes Commands:**
```bash
cd kubernetes/
./deploy.sh

# Or manually:
kubectl apply -f redis-pvc.yaml
kubectl apply -f redis-deployment.yaml
kubectl apply -f redis-service.yaml
kubectl apply -f agent-deployment.yaml
```

## Service Monitoring

### Service Monitor

The service monitor provides:
- Process health monitoring
- Automatic restart on failure
- Performance metrics collection
- Custom health checks

```python
from beast_mode.deployment.service_monitor import ServiceMonitor, MonitoredService

# Create monitor
config = config_manager.get_config("production")
monitor = ServiceMonitor(config)

# Add service
service = MonitoredService(
    name="my_service",
    command=["python", "-m", "my_module"],
    working_directory="/app",
    environment={"ENV": "production"},
    auto_restart=True,
    max_restarts=5,
    health_check_command=["curl", "-f", "http://localhost:8080/health"]
)

monitor.add_service(service)

# Start monitoring
monitor.start_monitoring()

# Start service
monitor.start_service("my_service")

# Check status
status = monitor.get_service_status("my_service")
print(f"Status: {status.status}")
print(f"CPU: {status.metrics.cpu_percent}%")
print(f"Memory: {status.metrics.memory_mb}MB")

# Export metrics
monitor.export_metrics("metrics.json")
```

### Health Checks

Services can have custom health checks:

```python
# HTTP health check
health_check_command=["curl", "-f", "http://localhost:8080/health"]

# Redis health check
health_check_command=["redis-cli", "-h", "localhost", "ping"]

# Custom script
health_check_command=["./scripts/health_check.sh"]
```

### Metrics Collection

The monitor collects:
- CPU usage percentage
- Memory usage (MB and percentage)
- Open file descriptors
- Network connections
- Uptime
- Restart count

### Event Callbacks

Register callbacks for service events:

```python
def on_service_failed(service):
    print(f"Service {service.name} failed!")
    # Send alert, log to external system, etc.

monitor.add_callback('service_failed', on_service_failed)
monitor.add_callback('service_restarted', on_service_restarted)
```

## Validation and Testing

### Deployment Validator

The validator performs comprehensive checks:

```python
from beast_mode.deployment.validator import DeploymentValidator, ValidationLevel

validator = DeploymentValidator(config_manager)

# Run validation
report = validator.validate_deployment(
    deployment_id="my_deployment",
    environment="production",
    level=ValidationLevel.COMPREHENSIVE
)

print(f"Overall: {'PASSED' if report.overall_passed else 'FAILED'}")
print(f"Checks: {report.passed_checks}/{report.total_checks}")

# Generate HTML report
validator.generate_report_html(report, "validation_report.html")
```

### Validation Levels

**Basic:**
- Port connectivity
- DNS resolution
- Redis connection

**Standard:**
- Basic checks
- Service health
- Message flow
- Configuration validation

**Comprehensive:**
- Standard checks
- Performance testing
- Security validation
- Monitoring verification

### Validation Checks

**Connectivity:**
- Redis port accessibility
- DNS resolution
- Network connectivity

**Redis:**
- Connection and authentication
- Basic operations (get/set/delete)
- Pub/sub functionality
- Performance benchmarks

**Services:**
- Process existence
- Log file activity
- Health check responses

**Configuration:**
- Configuration completeness
- Required directories
- Environment variables

**Security:**
- Authentication enabled (production)
- SSL/TLS configuration
- Password protection

**Performance:**
- Redis operation speed
- Message throughput
- Resource usage

## Production Deployment

### Security Checklist

**Redis Security:**
```yaml
redis:
  password: "strong_random_password"
  ssl: true
  bind: "0.0.0.0"  # Only if needed
```

**Network Security:**
- Use VPC/private networks
- Configure firewalls
- Enable SSL/TLS for Redis
- Use strong passwords

**Access Control:**
- Limit SSH access
- Use key-based authentication
- Regular security updates
- Monitor access logs

### Monitoring Setup

**System Monitoring:**
```yaml
monitoring:
  health_check_interval: 30
  metrics_collection_interval: 60
  alert_thresholds:
    cpu_usage: 80.0
    memory_usage: 85.0
    disk_usage: 90.0
    message_latency: 1000.0
  log_retention_days: 30
```

**External Monitoring:**
- Integrate with Prometheus/Grafana
- Set up alerting (PagerDuty, Slack)
- Log aggregation (ELK stack)
- APM tools (New Relic, DataDog)

### Backup and Recovery

**Redis Backup:**
```bash
# Enable AOF persistence
redis-server --appendonly yes

# Regular backups
redis-cli BGSAVE
cp /var/lib/redis/dump.rdb /backup/redis-$(date +%Y%m%d).rdb
```

**Configuration Backup:**
```bash
# Backup configurations
tar -czf config-backup-$(date +%Y%m%d).tar.gz config/
```

### Scaling Considerations

**Horizontal Scaling:**
- Use Redis Cluster for high availability
- Deploy agents across multiple nodes
- Load balance with HAProxy/nginx

**Vertical Scaling:**
- Monitor resource usage
- Scale Redis memory/CPU
- Optimize connection pools

### Deployment Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy Beast Mode
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Validate configuration
        run: python scripts/validate_config.py --env production
      
      - name: Deploy to staging
        run: python scripts/deploy_docker.py --env staging
      
      - name: Run validation tests
        run: python scripts/validate_deployment.py --env staging
      
      - name: Deploy to production
        if: success()
        run: python scripts/deploy_distributed.py --env production
```

## Troubleshooting

### Common Issues

**Redis Connection Failed:**
```bash
# Check Redis is running
redis-cli ping

# Check port accessibility
telnet localhost 6379

# Check Redis logs
tail -f /var/log/redis/redis-server.log
```

**Service Won't Start:**
```bash
# Check service logs
tail -f logs/service_name.log

# Check process status
ps aux | grep service_name

# Check system resources
df -h
free -m
```

**Deployment Validation Fails:**
```bash
# Run validation with debug logging
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from beast_mode.deployment.validator import DeploymentValidator
# ... run validation
"

# Check specific validation results
python scripts/validate_deployment.py --level comprehensive --verbose
```

### Log Analysis

**Service Logs:**
```bash
# View real-time logs
tail -f logs/*.log

# Search for errors
grep -i error logs/*.log

# Check log rotation
ls -la logs/
```

**System Logs:**
```bash
# System messages
journalctl -u redis-server
journalctl -f

# Docker logs
docker-compose logs -f
docker logs container_name
```

### Performance Issues

**Redis Performance:**
```bash
# Redis info
redis-cli info

# Monitor Redis operations
redis-cli monitor

# Check slow queries
redis-cli slowlog get 10
```

**System Performance:**
```bash
# CPU and memory usage
top
htop

# Disk I/O
iotop

# Network connections
netstat -tulpn
ss -tulpn
```

### Recovery Procedures

**Service Recovery:**
```bash
# Restart failed service
python -c "
from beast_mode.deployment.service_monitor import ServiceMonitor
monitor = ServiceMonitor(config)
monitor.restart_service('service_name')
"

# Full deployment restart
python scripts/deploy_single_machine.py --restart
```

**Data Recovery:**
```bash
# Restore Redis from backup
redis-cli FLUSHALL
redis-cli --rdb /backup/redis-backup.rdb

# Restore configuration
tar -xzf config-backup.tar.gz
```

### Getting Help

**Debug Information:**
```bash
# System information
python scripts/system_info.py

# Configuration dump
python scripts/dump_config.py --env production

# Health check report
python scripts/health_check.py --comprehensive
```

**Support Channels:**
- Check logs first: `logs/*.log`
- Run validation: `python scripts/validate_deployment.py`
- Review configuration: `config/*.yaml`
- System resources: `df -h && free -m`

For additional help, include:
- Deployment ID
- Environment name
- Error messages
- System information
- Configuration (sanitized)