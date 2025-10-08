# Option 3: Comprehensive System Health Check

## Mission
Perform a complete diagnostic assessment of all running systems, services, and components to identify what's working, what's broken, and what needs immediate attention.

## Context
Multiple systems have been running with various DAG executions, deployments, and implementations. We need a clear picture of the current operational state before proceeding with any development work.

## Current Running Processes
Based on recent process scan:
- ✅ Kiro with multiple MCP servers running
- ✅ Docker services available
- ✅ Various Python processes and utilities
- ❓ Observatory/Prometheus/Grafana status unknown
- ❓ Redis/WebSocket services status unknown

## Task: Comprehensive Health Assessment

### Phase 1: Infrastructure Health Check

1. **Docker Services Status**
   ```bash
   # Check all Docker containers
   docker ps -a | tee docker-status-health-check.log
   
   # Check Docker Compose services
   docker-compose ps | tee docker-compose-status.log
   
   # Check specific monitoring stack
   docker-compose -f docker-compose.yml ps prometheus grafana redis
   ```

2. **Port and Service Availability**
   ```bash
   # Check critical ports
   lsof -i :8888  # Observatory
   lsof -i :3000  # Grafana  
   lsof -i :9090  # Prometheus
   lsof -i :6379  # Redis
   
   # Test HTTP endpoints
   curl -s http://localhost:8888/health || echo "Observatory DOWN"
   curl -s http://localhost:3000/api/health || echo "Grafana DOWN"
   curl -s http://localhost:9090/-/healthy || echo "Prometheus DOWN"
   ```

3. **Network Connectivity**
   ```bash
   # Test external connectivity
   ping -c 3 observatory.nkllon.com
   curl -s https://observatory.nkllon.com/health || echo "External Observatory DOWN"
   
   # Check Cloudflare tunnel status
   pgrep -f cloudflared && echo "Cloudflare tunnel running" || echo "Cloudflare tunnel DOWN"
   ```

### Phase 2: Application Health Assessment

1. **Observatory Platform Status**
   ```bash
   # Check Observatory processes
   pgrep -f observatory
   
   # Test Observatory endpoints
   curl -s http://localhost:8888/health
   curl -s http://localhost:8888/metrics
   curl -s http://localhost:8888/ws/test
   
   # Check Observatory logs
   tail -50 observatory.log 2>/dev/null || echo "No Observatory logs found"
   ```

2. **Monitoring Stack Health**
   ```bash
   # Prometheus health and targets
   curl -s http://localhost:9090/-/healthy
   curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'
   
   # Grafana health and datasources
   curl -s http://localhost:3000/api/health
   curl -s http://localhost:3000/api/datasources | jq '.[].name'
   
   # Redis connectivity
   redis-cli ping 2>/dev/null || echo "Redis not accessible"
   ```

3. **WebSocket Infrastructure**
   ```bash
   # Test WebSocket endpoints
   wscat -c ws://localhost:8888/ws/coordination --timeout 5 || echo "WebSocket connection failed"
   
   # Check WebSocket proxy configuration
   grep -r "websocket" nginx/ cloudflare/ 2>/dev/null || echo "No WebSocket config found"
   ```

### Phase 3: Development Environment Health

1. **Python Environment Status**
   ```bash
   # Check virtual environment
   which python
   python --version
   pip list | grep -E "(kiro|beast|observatory)" || echo "No project packages found"
   
   # Test critical imports
   python -c "from src.rm_ddd.core.unified_reflective_module import ReflectiveModule; print('ReflectiveModule OK')" || echo "ReflectiveModule BROKEN"
   python -c "from src.deployment_auditor.auditor import DeploymentDataAuditor; print('DeploymentAuditor OK')" || echo "DeploymentAuditor BROKEN"
   ```

2. **MCP Server Health**
   ```bash
   # Check MCP server processes
   pgrep -f "mcp-server" | wc -l
   
   # Test MCP functionality (if available)
   # This would require Kiro-specific testing
   ```

3. **File System Health**
   ```bash
   # Check disk space
   df -h . | tail -1
   
   # Check for large log files
   find . -name "*.log" -size +100M 2>/dev/null
   
   # Check for stuck processes
   ps aux | awk '$8 ~ /^D/ {print $2, $11}' | head -10
   ```

### Phase 4: Recent Activity Analysis

1. **Recent Changes Assessment**
   ```bash
   # Check recent file modifications
   find . -type f -mtime -1 -not -path "./.git/*" | head -20
   
   # Check recent git activity
   git log --oneline -10
   git status --porcelain
   
   # Check recent process activity
   ps -eo pid,ppid,cmd,etime | grep -E "(python|docker|redis|prometheus|grafana)" | head -10
   ```

2. **Log Analysis**
   ```bash
   # Check for recent errors
   find . -name "*.log" -mtime -1 -exec grep -l "ERROR\|FAIL\|Exception" {} \; | head -10
   
   # Check system logs (if accessible)
   dmesg | tail -20 2>/dev/null || echo "System logs not accessible"
   ```

### Phase 5: Configuration Validation

1. **Critical Configuration Files**
   ```bash
   # Check Docker Compose configuration
   docker-compose config --quiet && echo "Docker Compose config OK" || echo "Docker Compose config BROKEN"
   
   # Check Nginx configuration (if present)
   nginx -t 2>/dev/null && echo "Nginx config OK" || echo "Nginx config BROKEN or not installed"
   
   # Check Cloudflare tunnel configuration
   test -f cloudflared-config.yml && echo "Cloudflare config present" || echo "Cloudflare config missing"
   ```

2. **Environment Variables**
   ```bash
   # Check critical environment variables
   echo "REDIS_PASSWORD: ${REDIS_PASSWORD:+SET}" || echo "REDIS_PASSWORD: NOT SET"
   echo "ENVIRONMENT: ${ENVIRONMENT:-not set}"
   
   # Check .env files
   test -f .env && echo ".env file present" || echo ".env file missing"
   ```

## Expected Health Report Format

### System Status Summary
```
🟢 HEALTHY: Services running normally
🟡 WARNING: Services running with issues  
🔴 CRITICAL: Services down or broken
⚪ UNKNOWN: Status cannot be determined
```

### Detailed Component Status
- **Infrastructure**: Docker, networking, storage
- **Applications**: Observatory, monitoring stack, WebSocket services
- **Development**: Python environment, MCP servers, build tools
- **Configuration**: Docker Compose, Nginx, Cloudflare, environment variables

### Immediate Action Items
- **Critical Issues**: Services that must be fixed immediately
- **Warnings**: Issues that should be addressed soon
- **Optimizations**: Performance or configuration improvements
- **Monitoring**: Items that need ongoing observation

## Success Criteria
- [ ] Complete inventory of all running services
- [ ] Health status for each critical component
- [ ] Identification of any broken or failing services
- [ ] Clear prioritization of issues needing attention
- [ ] Baseline established for ongoing monitoring

## Deliverables
1. **System Health Report**: Comprehensive status of all components
2. **Issue Priority Matrix**: Critical, warning, and optimization items
3. **Service Inventory**: Complete list of running services and their status
4. **Action Plan**: Immediate steps needed to address any issues
5. **Monitoring Baseline**: Current performance and availability metrics

## Files to Create/Update
- `system-health-report-$(date +%Y%m%d).md`
- `service-inventory.json`
- `critical-issues.md`
- `monitoring-baseline.json`

## Expected Outcome
A clear, comprehensive understanding of the current system state that enables informed decisions about:
- **What's working** and can be relied upon
- **What's broken** and needs immediate fixing
- **What's at risk** and needs monitoring
- **What's optimal** and performing well

This health check provides the foundation for all subsequent development and operational decisions.

**Estimated Time**: 15-30 minutes
**Priority**: High - Essential for informed decision making
**Risk**: Low - Pure diagnostic, no changes made