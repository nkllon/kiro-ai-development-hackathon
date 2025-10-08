# Development Infrastructure Status

## Currently Running Services

**Last checked:** 2025-10-08

### ✅ Core Services (Running)

| Service | Container | Status | Port | UI/API |
|---------|-----------|--------|------|--------|
| **Jaeger** | local-jaeger | ✅ Up 18h | 16686 | http://localhost:16686 |
| **Grafana** | local-grafana | ✅ Up 18h | 3000 | http://localhost:3000 |
| **Directus CMS** | local-directus-1 | ⚠️ Unhealthy | 8055 | http://localhost:8055 |
| **Directus DB** | local-directus-db-1 | ✅ Healthy | 5432 | (internal) |
| **Redis** | (host process) | ✅ Running | 6379 | 127.0.0.1:6379 |
| **Ollama** | awesome_jemison | ✅ Up 18h | 11434 | http://localhost:11434 |
| **OpenWebUI** | openwebui-extension-service | ✅ Healthy | 8090 | http://localhost:8090 |

### ⚠️ Services with Issues

| Service | Container | Issue | Action Needed |
|---------|-----------|-------|---------------|
| **Directus CMS** | local-directus-1 | Unhealthy status | Check logs: `docker logs local-directus-1` |
| **Monitoring Daemon** | beast-mode-monitoring-daemon | Restarting loop | Check configuration and logs |

## Required for Development Mode

### OpenTelemetry Tracing (Jaeger)
- ✅ **Status**: Running and accessible
- ✅ **UI**: http://localhost:16686
- ✅ **Purpose**: Local distributed tracing for all services
- 📝 **Note**: Required for debugging LangGraph, microservices, and async workflows

### LangSmith (LangChain Tracing)
- ❌ **Status**: Not configured yet
- 📝 **Setup needed**:
  ```bash
  pip install langsmith
  export LANGCHAIN_TRACING_V2=true
  export LANGCHAIN_API_KEY=<your_key>
  export LANGCHAIN_PROJECT=kiro-development
  ```
- 📝 **Purpose**: LangChain/LangGraph specific debugging

### CMS (Directus)
- ⚠️ **Status**: Running but unhealthy
- 📝 **Action**: Investigate and fix health check
- 📝 **Purpose**: Content management for specs, documentation, knowledge base

### Monitoring Stack
- ✅ **Grafana**: Running at http://localhost:3000
- ❌ **Prometheus**: Not visible in docker ps (may need separate compose file)
- ⚠️ **Monitoring Daemon**: Restarting (needs fix)

## Required Environment Variables

**Current .env should include:**
```bash
# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=

# Jaeger (OpenTelemetry)
OTEL_EXPORTER_JAEGER_ENDPOINT=http://localhost:14268/api/traces
JAEGER_AGENT_HOST=localhost
JAEGER_AGENT_PORT=6831

# LangSmith (LangChain Tracing)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=<your_key>
LANGCHAIN_PROJECT=kiro-development

# Directus CMS
DIRECTUS_URL=http://localhost:8055
DIRECTUS_EMAIL=admin@kiro.local
DIRECTUS_PASSWORD=<set_in_env>

# Grafana
GRAFANA_URL=http://localhost:3000
GF_SECURITY_ADMIN_PASSWORD=admin
```

## Commands

### Start All Development Services
```bash
# Start main services
docker-compose -f docker-compose.dev.yml up -d

# Verify status
make observatory-status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Check Service Health
```bash
# Jaeger
curl http://localhost:16686/api/services

# Directus
curl http://localhost:8055/server/health

# Grafana
curl http://localhost:3000/api/health

# Redis
redis-cli ping
```

### Debug Issues
```bash
# Check Directus logs
docker logs local-directus-1 --tail 50

# Check monitoring daemon
docker logs beast-mode-monitoring-daemon --tail 50

# Restart unhealthy services
docker restart local-directus-1
```

## Next Actions

1. ✅ **Jaeger**: Already running, ready to use
2. ⚠️ **Fix Directus**: Investigate unhealthy status
3. ❌ **Set up LangSmith**: Create account and configure
4. ⚠️ **Fix Monitoring Daemon**: Investigate restart loop
5. ❌ **Verify Prometheus**: Check if running or needs separate start

## References

- Jaeger UI: http://localhost:16686
- Grafana: http://localhost:3000 (admin/admin)
- Directus: http://localhost:8055
- OpenWebUI: http://localhost:8090
- Makefile: See `make help` for all commands
