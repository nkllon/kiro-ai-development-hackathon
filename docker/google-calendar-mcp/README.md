# Google Calendar MCP Integration - Beast Mode Framework

**⚠️ IMPORTANT: This is a Beast Mode MCP, not a generic MCP implementation**

This MCP server implements the unified ReflectiveModule pattern and requires Beast Mode infrastructure components (Prometheus, Grafana, Directus CMS) to function properly.

## Beast Mode Framework Requirements

**MANDATORY Infrastructure Dependencies:**

1. **Prometheus** (port 9090): Metrics collection and alerting - NOT optional
2. **Grafana** (port 3001): Observability dashboards - NOT optional
3. **Directus CMS**: Interface registration via ReflectiveModule.register_module()
4. **Beast Mode Network**: Must use `systematic-pdca-local` Docker network

**Framework Compliance:**
- All components inherit from unified ReflectiveModule
- Prometheus metrics exposed on port 8080 (MANDATORY)
- Systematic logging with correlation IDs
- PDCA methodology for all operations
- Beast Mode error handling patterns

This directory contains the Docker deployment configuration for the Google Calendar MCP integration.

## Quick Start

### 1. Build and Run (Stub Mode - No Google Credentials)

```bash
# Build the container
docker-compose build

# First, ensure main infrastructure is running
cd ../../deployment/local && docker-compose up -d

# Then start the MCP service (uses existing network)
cd ../../docker/google-calendar-mcp && docker-compose up -d

# Check health
curl http://localhost:3000/health
```

### 2. Production Deployment (With Google Credentials)

1. **Set up Google Cloud Project:**
   - Enable Google Calendar API
   - Create OAuth 2.0 credentials
   - Download credentials as `gcp-oauth.keys.json`

2. **Add credentials:**
   ```bash
   cp /path/to/your/gcp-oauth.keys.json ./credentials/
   ```

3. **Deploy:**
   ```bash
   # Ensure main infrastructure is running first
   cd ../../deployment/local && docker-compose up -d
   
   # Then deploy MCP service
   cd ../../docker/google-calendar-mcp && docker-compose up -d
   ```

### 3. With Monitoring (Optional)

```bash
# Uses existing Prometheus and Grafana from main deployment
# Access dashboards (from main infrastructure)
# Grafana: http://localhost:3000 (admin/systematic)
# Prometheus: http://localhost:9090
```

## Configuration

### Environment Variables

- `GOOGLE_CALENDAR_PORT` - Server port (default: 3000)
- `GOOGLE_CALENDAR_LOG_LEVEL` - Log level (default: info)
- `BEAST_MODE_PROMETHEUS_ENABLED` - Enable metrics (default: true)

### Volumes

- `./credentials:/app/credentials:ro` - OAuth credentials (read-only)
- `google_calendar_logs:/app/logs` - Persistent logs
- `google_calendar_cache:/app/cache` - Performance cache

## Health Checks

The container includes comprehensive health monitoring:

```bash
# Docker health check
docker ps  # Shows health status

# Manual health check
curl http://localhost:3000/health

# Detailed metrics
curl http://localhost:3000/metrics
```

## MCP Protocol Testing

### Claude Desktop Integration

Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "google-calendar": {
      "command": "docker",
      "args": ["exec", "google_calendar_mcp", "python3", "-m", "src.beast_mode.mcp_integrations.google_calendar.main", "--health-only"],
      "env": {}
    }
  }
}
```

### Manual MCP Testing

```bash
# Test auth status
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "auth.status", "params": {}, "id": "test1"}'

# Test health status
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "health.status", "params": {}, "id": "test2"}'
```

## Troubleshooting

### Common Issues

1. **Container won't start:**
   ```bash
   docker-compose logs google-calendar-mcp
   ```

2. **Health check failing:**
   ```bash
   docker exec google_calendar_mcp curl -f http://localhost:3000/health
   ```

3. **Authentication issues:**
   - Verify credentials file exists and has correct permissions
   - Check Google Cloud Project has Calendar API enabled
   - Ensure OAuth scopes are correct

### Debug Mode

```bash
# Run with debug logging
GOOGLE_CALENDAR_LOG_LEVEL=debug docker-compose up

# Interactive debugging
docker exec -it google_calendar_mcp bash
```

## Performance Monitoring

The integration includes comprehensive profiling:

- **Request/response timing** for all operations
- **Memory usage tracking** with leak detection  
- **Performance bottleneck identification**
- **Prometheus metrics export**

Access performance data:
```bash
# Performance report
curl http://localhost:3000/health/profiling_report

# Slow operations
curl http://localhost:3000/health/slow_operations
```

## Security

The container follows security best practices:

- ✅ **Non-root user** execution
- ✅ **Read-only credentials** mount
- ✅ **Minimal base image** (Python slim)
- ✅ **Health check endpoints**
- ✅ **Encrypted credential storage**

## Development

### Local Development

```bash
# Run smoke tests
PYTHONPATH=. python3 src/beast_mode/mcp_integrations/google_calendar/smoke_test.py

# Run unit tests
python3 -m pytest tests/unit/beast_mode/mcp_integrations/google_calendar/ -v
```

### Building Custom Images

```bash
# Build with custom tag
docker build -f docker/google-calendar-mcp/Dockerfile -t my-calendar-mcp:latest .

# Push to registry
docker tag my-calendar-mcp:latest your-registry/calendar-mcp:latest
docker push your-registry/calendar-mcp:latest
```