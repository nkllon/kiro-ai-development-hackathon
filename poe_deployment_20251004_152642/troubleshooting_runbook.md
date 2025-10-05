# Observatory Troubleshooting Runbook

## Quick Reference

### Emergency Commands
```bash
# Check Observatory status
python scripts/monitor_observatory_health.py status

# Restart Observatory
python scripts/monitor_observatory_health.py restart

# Emergency rollback to Docker
python scripts/rollback_to_docker_deployment.py --confirm

# Quick recovery
./scripts/emergency_recovery.sh
```

### Health Check URLs
- **Local**: http://localhost:8888/health
- **External**: https://observatory.nkllon.com/health
- **Metrics**: http://localhost:8888/metrics

## Common Issues and Solutions

### 1. Observatory Not Responding

#### Symptoms
- `curl http://localhost:8888/health` returns connection refused
- External access returns 502/503 errors
- Process appears to be running but not serving HTTP

#### Diagnosis Steps
```bash
# Check if process is running
python scripts/monitor_observatory_health.py status

# Check process details
ps aux | grep start_observatory

# Check port usage
lsof -i :8888

# Review logs
tail -50 observatory.log
```

#### Solutions

**Solution 1: Restart Observatory**
```bash
python scripts/monitor_observatory_health.py restart
```

**Solution 2: Kill and Clean Start**
```bash
pkill -f start_observatory
rm -f observatory.pid
python scripts/monitor_observatory_health.py start
```

**Solution 3: Check Configuration**
```bash
# Verify data directories exist
ls -la observatory_data/

# Check permissions
ls -ld observatory_data/*/

# Recreate data structure if needed
python scripts/setup_data_persistence.py
```

### 2. External Access Not Working

#### Symptoms
- Local access works but https://observatory.nkllon.com fails
- Cloudflare returns 502/530 errors
- Tunnel appears disconnected

#### Diagnosis Steps
```bash
# Check tunnel process
python scripts/manage_tunnel.py status
pgrep -f cloudflared

# Test local access first
curl -v http://localhost:8888/health

# Check tunnel logs
docker logs observatory-cloudflare-tunnel 2>/dev/null || echo "No Docker tunnel"
```

#### Solutions

**Solution 1: Restart Tunnel**
```bash
python scripts/manage_tunnel.py restart
```

**Solution 2: Verify Tunnel Configuration**
```bash
# Check config file
cat cloudflared-config.yml

# Verify tunnel points to localhost:8888
grep -A 5 "observatory.nkllon.com" cloudflared-config.yml
```

**Solution 3: Manual Tunnel Start**
```bash
cloudflared tunnel --config cloudflared-config.yml run
```

### 3. Data Persistence Issues

#### Symptoms
- Observatory starts but loses data on restart
- Permission denied errors in logs
- Backup/restore operations fail

#### Diagnosis Steps
```bash
# Check data directory structure
tree observatory_data/ || ls -la observatory_data/

# Check permissions
ls -ld observatory_data/
ls -ld observatory_data/*/

# Test write permissions
touch observatory_data/logs/test.txt && rm observatory_data/logs/test.txt
```

#### Solutions

**Solution 1: Fix Permissions**
```bash
chmod 755 observatory_data/
chmod 755 observatory_data/*/
```

**Solution 2: Recreate Data Structure**
```bash
python scripts/setup_data_persistence.py
```

**Solution 3: Restore from Backup**
```bash
# List available backups
ls -la observatory_backup_*/

# Restore from most recent
python scripts/backup_observatory_data.py restore observatory_backup_YYYYMMDD_HHMMSS.tar.gz
```

### 4. Performance Issues

#### Symptoms
- Slow response times (>5 seconds)
- High CPU/memory usage
- Timeouts on health checks

#### Diagnosis Steps
```bash
# Check resource usage
python scripts/monitor_observatory_health.py status

# Check system resources
top -p $(pgrep -f start_observatory)
free -h
df -h

# Run performance validation
python scripts/validate_observatory_deployment.py
```

#### Solutions

**Solution 1: Restart Observatory**
```bash
python scripts/monitor_observatory_health.py restart
```

**Solution 2: Clear Cache**
```bash
rm -rf observatory_data/cache/*
```

**Solution 3: Check Disk Space**
```bash
# Clean up old logs
find observatory_data/logs/ -name "*.log" -mtime +7 -delete

# Clean up old backups
ls -t observatory_*backup*.tar.gz | tail -n +8 | xargs rm -f
```

### 5. WebSocket Connection Issues

#### Symptoms
- Dashboard loads but real-time features don't work
- WebSocket connection errors in browser console
- Validation shows WebSocket failures

#### Diagnosis Steps
```bash
# Test WebSocket endpoints manually
wscat -c ws://localhost:8888/ws/observatory

# Check if Observatory supports WebSockets
curl -H "Upgrade: websocket" -H "Connection: Upgrade" http://localhost:8888/ws/observatory
```

#### Solutions

**Solution 1: Restart Observatory**
```bash
python scripts/monitor_observatory_health.py restart
```

**Solution 2: Check Tunnel WebSocket Support**
```bash
# Verify tunnel config includes WebSocket settings
grep -A 10 "originRequest" cloudflared-config.yml
```

### 6. Backup and Recovery Issues

#### Symptoms
- Backup creation fails
- Restore operations don't work
- Data corruption after recovery

#### Diagnosis Steps
```bash
# Check backup directory
ls -la observatory_backup_*/

# Verify backup integrity
tar -tzf observatory_backup_YYYYMMDD_HHMMSS/observatory_prometheus_data.tar.gz | head

# Check available disk space
df -h
```

#### Solutions

**Solution 1: Manual Backup**
```bash
python scripts/backup_observatory_data.py backup
```

**Solution 2: Verify Backup Integrity**
```bash
# Test backup files
for backup in observatory_backup_*/*.tar.gz; do
    echo "Testing $backup"
    tar -tzf "$backup" >/dev/null && echo "OK" || echo "CORRUPTED"
done
```

**Solution 3: Clean Recovery**
```bash
# Stop Observatory
python scripts/monitor_observatory_health.py stop

# Remove current data
mv observatory_data observatory_data_backup_$(date +%Y%m%d_%H%M%S)

# Restore from backup
python scripts/setup_data_persistence.py
python scripts/backup_observatory_data.py restore observatory_backup_YYYYMMDD_HHMMSS.tar.gz

# Restart Observatory
python scripts/monitor_observatory_health.py start
```

## Escalation Procedures

### Level 1: Self-Service
- Use this runbook
- Check logs and status
- Try restart procedures
- Attempt rollback if needed

### Level 2: System Administrator
- Contact system administrator if:
  - Multiple restart attempts fail
  - Data corruption suspected
  - System resource issues
  - Network connectivity problems

### Level 3: Emergency Response
- Use emergency rollback if:
  - Service completely unavailable
  - Data loss suspected
  - Security incident
  - Critical business impact

## Monitoring and Alerting

### Automated Monitoring
```bash
# Set up continuous monitoring
python scripts/monitor_observatory_health.py monitor 60 &

# Enable auto-restart
export OBSERVATORY_AUTO_RESTART=true
python scripts/monitor_observatory_health.py monitor 30 &
```

### Manual Health Checks
```bash
# Quick health check
curl -f http://localhost:8888/health && echo "Local OK" || echo "Local FAIL"
curl -f https://observatory.nkllon.com/health && echo "External OK" || echo "External FAIL"

# Comprehensive validation
python scripts/validate_observatory_deployment.py
```

### Log Monitoring
```bash
# Watch Observatory logs
tail -f observatory.log

# Watch monitor logs
tail -f observatory_monitor.log

# Search for errors
grep -i error observatory.log | tail -10
```

## Prevention and Maintenance

### Daily Tasks
- Check Observatory status
- Review error logs
- Verify external access
- Monitor resource usage

### Weekly Tasks
- Create data backup
- Review performance metrics
- Clean up old logs
- Update documentation

### Monthly Tasks
- Full system validation
- Review and test rollback procedures
- Update backup retention
- Security review

## Emergency Contacts

### Primary Contacts
- **System Administrator**: [contact info]
- **Observatory Maintainer**: [contact info]
- **On-Call Engineer**: [contact info]

### Escalation Matrix
1. **Self-service** (0-15 minutes)
2. **System Admin** (15-30 minutes)
3. **Emergency Response** (30+ minutes)

### Communication Channels
- **Slack**: #observatory-alerts
- **Email**: observatory-team@company.com
- **Phone**: Emergency hotline

---

**Remember**: When in doubt, use the emergency rollback procedure to restore service quickly, then investigate the root cause.

**Last Updated**: {datetime.now().isoformat()}
**Version**: 1.0