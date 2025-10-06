# Observatory Deployment Guide

## Overview

This guide documents the Observatory deployment recovery process and operational procedures for the vonnegut server. The deployment has been transitioned from a complex Docker Compose setup to a simplified monolithic approach.

## Deployment Architecture

### Current State: Monolithic Deployment
- **Single Python Process**: Observatory runs as a single `start_observatory.py` process
- **Local Data Storage**: Data persisted to `observatory_data/` directory structure
- **Cloudflare Tunnel**: External access via `https://observatory.nkllon.com`
- **Process Management**: Managed via custom monitoring scripts

### Previous State: Docker Compose (Rollback Available)
- **Multi-Container**: Separate containers for Observatory, Grafana, Prometheus, Redis
- **Docker Volumes**: Data stored in Docker-managed volumes
- **Container Orchestration**: Managed via docker-compose.yml

## Directory Structure

```
kiro-ai-development-hackathon/
├── observatory_data/           # Data persistence directory
│   ├── metrics/               # Prometheus-style metrics
│   ├── dashboards/            # Dashboard configurations
│   ├── logs/                  # Application logs
│   ├── config/                # Runtime configuration
│   ├── cache/                 # Temporary cache files
│   ├── uploads/               # User uploaded files
│   └── exports/               # Data export files
├── scripts/                   # Management and deployment scripts
│   ├── backup_observatory_data.py
│   ├── cleanup_observatory_containers.py
│   ├── configure_cloudflare_tunnel.py
│   ├── deploy_monolithic_observatory.py
│   ├── monitor_observatory_health.py
│   ├── rollback_to_docker_deployment.py
│   ├── setup_data_persistence.py
│   └── validate_observatory_deployment.py
├── docs/                      # Documentation
│   ├── data_recovery_procedures.md
│   └── observatory_deployment_guide.md
└── deployment/observatory/    # Docker Compose files (for rollback)
    └── docker-compose.yml
```

## Operational Procedures

### Starting Observatory

#### Method 1: Direct Start
```bash
python start_observatory.py
```

#### Method 2: Using Monitor Script
```bash
python scripts/monitor_observatory_health.py start
```

#### Method 3: Background Start
```bash
python scripts/start_observatory_background.py
```

### Stopping Observatory

```bash
python scripts/monitor_observatory_health.py stop
```

### Checking Status

```bash
python scripts/monitor_observatory_health.py status
```

### Restarting Observatory

```bash
python scripts/monitor_observatory_health.py restart
```

### Continuous Monitoring

```bash
# Monitor every 30 seconds
python scripts/monitor_observatory_health.py monitor

# Monitor every 60 seconds
python scripts/monitor_observatory_health.py monitor 60
```

## Cloudflare Tunnel Management

### Starting Tunnel

```bash
python scripts/manage_tunnel.py start
```

### Stopping Tunnel

```bash
python scripts/manage_tunnel.py stop
```

### Checking Tunnel Status

```bash
python scripts/manage_tunnel.py status
```

### Tunnel Configuration

The tunnel is configured in `cloudflared-config.yml` to route:
- `https://observatory.nkllon.com` → `http://localhost:8888`

## Data Management

### Creating Backups

```bash
# Manual backup
python scripts/backup_observatory_data.py backup

# Automated backup (add to crontab)
./scripts/schedule_backup.sh
```

### Restoring from Backup

```bash
python scripts/backup_observatory_data.py restore observatory_data_backup_YYYYMMDD_HHMMSS.tar.gz
```

### Data Recovery

See `docs/data_recovery_procedures.md` for detailed recovery procedures.

## Validation and Testing

### Comprehensive Validation

```bash
python scripts/validate_observatory_deployment.py
```

This validates:
- Local endpoint accessibility
- External access via tunnel
- WebSocket connections
- Data persistence
- Process health
- Performance benchmarks

### Manual Health Checks

```bash
# Local health check
curl http://localhost:8888/health

# External health check
curl https://observatory.nkllon.com/health

# Metrics endpoint
curl http://localhost:8888/metrics
```

## Troubleshooting

### Common Issues

#### Observatory Not Starting
1. Check if port 8888 is available: `lsof -i :8888`
2. Review Observatory logs: `tail -f observatory.log`
3. Check process status: `python scripts/monitor_observatory_health.py status`

#### External Access Not Working
1. Check tunnel status: `python scripts/manage_tunnel.py status`
2. Verify tunnel process: `pgrep -f cloudflared`
3. Test local access first: `curl http://localhost:8888/health`

#### Data Persistence Issues
1. Check directory permissions: `ls -la observatory_data/`
2. Verify disk space: `df -h`
3. Review data recovery procedures

#### Performance Issues
1. Check resource usage: `python scripts/monitor_observatory_health.py status`
2. Review application logs: `tail -f observatory_data/logs/*.log`
3. Run performance validation: `python scripts/validate_observatory_deployment.py`

### Log Locations

- **Observatory Application**: `observatory.log`
- **Monitor Script**: `observatory_monitor.log`
- **Data Directory Logs**: `observatory_data/logs/`
- **Validation Reports**: `observatory_validation_*.json`

## Rollback Procedures

### Emergency Rollback to Docker

If the monolithic deployment fails completely:

```bash
python scripts/rollback_to_docker_deployment.py --confirm
```

This will:
1. Stop monolithic services
2. Restore Docker volumes from backups
3. Start Docker Compose services
4. Validate rollback success

### Emergency Recovery Script

For quick recovery without Python:

```bash
./scripts/emergency_recovery.sh
```

## Maintenance Tasks

### Daily
- Check Observatory status
- Review application logs
- Verify external accessibility

### Weekly
- Create data backup
- Review performance metrics
- Update documentation if needed

### Monthly
- Full system validation
- Review and rotate log files
- Update backup retention policy

## Security Considerations

### Access Control
- Observatory runs on localhost:8888 (not directly exposed)
- External access only via Cloudflare tunnel with TLS termination
- No hardcoded credentials in configuration files

### Data Protection
- Regular backups with integrity validation
- Data stored in protected directory structure
- Secure tunnel configuration for external access

### Monitoring
- Process health monitoring
- Resource usage tracking
- Automated alerting for failures

## Performance Expectations

### Response Time Targets
- Health endpoint: < 1 second
- Metrics endpoint: < 2 seconds
- Dashboard: < 3 seconds

### Resource Usage
- Memory: < 512MB under normal load
- CPU: < 50% under normal load
- Disk: Grows with metrics data, monitor regularly

## Contact Information

### System Administration
- **Primary**: System Administrator
- **Backup**: Observatory Maintainer
- **Emergency**: On-call rotation

### Documentation Updates
- Update this guide when procedures change
- Version control all configuration changes
- Document all troubleshooting solutions

---

**Last Updated**: {datetime.now().isoformat()}
**Version**: 1.0
**Status**: Active Deployment Guide