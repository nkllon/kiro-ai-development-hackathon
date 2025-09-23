# Google Calendar MCP Integration - Beast Mode

A Beast Mode compliant Google Calendar integration using a proven, existing MCP server instead of reinventing the wheel.

## Overview

This integration uses `@cocal/google-calendar-mcp@1.4.9` - a mature, well-tested Google Calendar MCP server - containerized with Beast Mode systematic observability and monitoring.

**Why this approach?**
- ✅ **Proven solution**: Uses existing, battle-tested MCP server with 13 versions and active maintenance
- ✅ **Beast Mode compliant**: Adds systematic monitoring, observability, and containerization
- ✅ **No reinventing**: Leverages community expertise instead of building from scratch
- ✅ **Production ready**: Mature OAuth handling, error recovery, and feature completeness

## Features

- **Mature MCP Server**: @cocal/google-calendar-mcp with extensive calendar management support
- **Complete OAuth 2.0**: Secure Google Calendar API access with automatic token management
- **Full Calendar Operations**: Create, read, update, delete events, availability checking
- **Beast Mode Monitoring**: Prometheus metrics + Grafana dashboards (MANDATORY)
- **Docker Deployment**: Secure containerization with health checks
- **Claude Desktop Ready**: Direct MCP protocol integration

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Google Cloud Project with Calendar API enabled
- OAuth 2.0 credentials (Desktop application type)

### Setup

1. **Run the setup script**:
   ```bash
   cd docker/google-calendar-mcp
   ./setup.sh
   ```

2. **Add your Google OAuth credentials**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create/select project and enable Google Calendar API
   - Create OAuth 2.0 credentials (Desktop application)
   - Download JSON as `credentials/gcp-oauth.keys.json`

3. **Restart to apply credentials**:
   ```bash
   docker-compose restart
   ```

4. **Configure Claude Desktop**:
   ```json
   {
     "mcpServers": {
       "google-calendar": {
         "command": "docker",
         "args": ["exec", "google_calendar_mcp", "google-calendar-mcp"],
         "env": {
           "GOOGLE_APPLICATION_CREDENTIALS": "/app/credentials/gcp-oauth.keys.json"
         }
       }
     }
   }
   ```

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Claude        │    │   Docker         │    │   Google        │
│   Desktop       │◄──►│   Container      │◄──►│   Calendar API  │
│                 │    │   (@cocal/mcp)   │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   Beast Mode     │
                       │   Monitoring     │
                       │   (Prometheus +  │
                       │    Grafana)      │
                       └──────────────────┘
```

## Beast Mode Compliance

- ✅ **Proven MCP Server**: Uses community-tested @cocal/google-calendar-mcp
- ✅ **Systematic Monitoring**: Prometheus metrics + Grafana dashboards (MANDATORY)
- ✅ **Docker Security**: Non-root execution, proper permissions, health checks
- ✅ **Observability**: Structured logging and systematic error handling
- ✅ **Network Integration**: Beast Mode network topology compliance

## Services

After running `./setup.sh`:

- **Google Calendar MCP**: http://localhost:3000
- **Prometheus**: http://localhost:9090  
- **Grafana**: http://localhost:3001 (admin/admin)

## MCP Server Features (@cocal/google-calendar-mcp)

The underlying MCP server provides:
- Complete Google Calendar API v3 integration
- OAuth 2.0 with automatic token refresh
- Event CRUD operations (create, read, update, delete)
- Calendar availability checking
- Recurring event support
- Multi-calendar support
- Attendee management
- Error handling and retry logic

## Security

- OAuth credentials stored with 600 permissions
- Container runs as non-root user
- HTTPS-only API communication
- Secure token storage and automatic refresh
- Credential validation and error recovery

## Troubleshooting

**Check container status**:
```bash
docker-compose ps
```

**View logs**:
```bash
docker-compose logs google-calendar-mcp
```

**Test MCP connection**:
```bash
docker exec google_calendar_mcp google-calendar-mcp --help
```

**Verify credentials**:
```bash
ls -la credentials/
# Should show: -rw------- gcp-oauth.keys.json
```

## Why This Approach Works

1. **Community Proven**: @cocal/google-calendar-mcp has 13 versions, active maintenance, and real-world usage
2. **Feature Complete**: Extensive calendar management without custom development
3. **Beast Mode Enhanced**: Adds systematic monitoring without reinventing core functionality  
4. **Production Ready**: Mature error handling, OAuth flows, and edge case management
5. **Maintainable**: Updates come from the community, not custom code maintenance

This is exactly what you should do - use proven solutions and enhance them systematically rather than building from scratch.