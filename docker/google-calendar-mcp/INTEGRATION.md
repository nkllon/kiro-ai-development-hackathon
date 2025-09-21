# Google Calendar MCP Integration Guide

## Integration with Existing Infrastructure

This Google Calendar MCP service integrates with the existing Beast Mode infrastructure instead of creating duplicate services.

### Network Integration

- **Uses existing network**: `systematic-pdca-local`
- **No port conflicts**: Exposes internal ports only
- **Metrics integration**: Adds to existing Prometheus scraping

### Prerequisites

1. **Main infrastructure must be running first**:
   ```bash
   cd deployment/local
   docker-compose up -d
   ```

2. **Verify existing services**:
   ```bash
   docker-compose ps
   # Should show: nginx, systematic-pdca-orchestrator, prometheus, grafana, directus, etc.
   ```

### Deployment

1. **Start MCP service**:
   ```bash
   cd docker/google-calendar-mcp
   docker-compose up -d
   ```

2. **Verify integration**:
   ```bash
   # Check network connectivity
   docker network ls | grep systematic-pdca-local
   
   # Check Prometheus targets
   curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.job=="google-calendar-mcp")'
   ```

### Monitoring Integration

- **Prometheus**: Existing server at `localhost:9090` scrapes MCP metrics
- **Grafana**: Existing dashboard at `localhost:3000` (admin/systematic)
- **Logs**: Shared logs directory at `../../logs`

### Service Discovery

The MCP service is discoverable within the Docker network as:
- **Service name**: `google_calendar_mcp`
- **MCP port**: `3000`
- **Metrics port**: `8080`

### Health Checks

```bash
# Check MCP service health
docker-compose exec google_calendar_mcp python3 -c "
import sys; sys.path.insert(0, '/app')
from src.beast_mode.mcp_integrations.google_calendar import GoogleCalendarMCPServer
server = GoogleCalendarMCPServer({'host': 'localhost', 'port': 3000})
health = server.get_health_status()
print(f'Health: {health.status.name}')
"

# Check metrics endpoint
curl -s http://localhost:9090/api/v1/query?query=up{job=\"google-calendar-mcp\"}
```

### Cleanup

```bash
# Stop MCP service only
cd docker/google-calendar-mcp
docker-compose down

# Stop all services (if needed)
cd ../../deployment/local
docker-compose down
```

## Configuration Notes

- **No duplicate Prometheus/Grafana**: Uses existing monitoring stack
- **Shared logging**: Uses existing logs volume
- **Network isolation**: Proper Docker networking prevents conflicts
- **Resource sharing**: Efficient use of existing infrastructure

This approach follows the Beast Mode principle of systematic integration rather than ad-hoc duplication.