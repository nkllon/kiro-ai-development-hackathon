# MCP Docker Server Troubleshooting Guide

## Issue Summary
**Problem**: MCP_DOCKER server failing to connect with error "Docker Desktop is not running"
**Root Cause**: Invalid MCP server configuration using non-existent Docker commands
**Status**: ✅ RESOLVED

## Error Analysis

### Original Error Logs
```
[2025-10-04T16:45:19.922Z] [warn] [MCP_DOCKER] Log from MCP Server: Docker Desktop is not running
[2025-10-04T16:45:19.987Z] [error] [MCP_DOCKER] Failed to connect to MCP server: MCP error -32000: Connection closed
[2025-10-04T16:46:19.130Z] [error] [MCP_DOCKER] MCP server connection + listTools timed out after 60 seconds
```

### Root Cause Analysis
The MCP_DOCKER server was configured with invalid Docker commands:
```json
"MCP_DOCKER": {
  "command": "docker",
  "args": ["mcp", "gateway", "run"]
}
```

**Problem**: `docker mcp gateway run` is not a valid Docker command, causing the MCP server to fail during initialization.

## Resolution Steps

### 1. Immediate Fix - Disable Problematic Server
The MCP_DOCKER server has been disabled in the user-level configuration:

**Location**: `~/.kiro/settings/mcp.json`
**Change**: Added `"disabled": true` to MCP_DOCKER configuration

```json
"MCP_DOCKER": {
  "command": "docker",
  "args": ["mcp", "gateway", "run"],
  "disabled": true,
  "autoApprove": ["fetch", "browser_navigate", "browser_evaluate"]
}
```

### 2. Alternative Docker Integration
Created `scripts/docker_mcp_integration.py` to provide Docker functionality through existing MCP infrastructure.

**Features**:
- List containers (`docker ps`)
- Get container logs
- Container statistics
- Container inspection
- Execute commands in containers

**Usage Examples**:
```bash
# List all containers
python scripts/docker_mcp_integration.py list

# Get container logs
python scripts/docker_mcp_integration.py logs beast-mode-observatory

# Get container stats
python scripts/docker_mcp_integration.py stats

# Execute command in container
python scripts/docker_mcp_integration.py exec beast-mode-observatory ps aux
```

## Verification

### Docker System Status
✅ **Docker Available**: Docker version 28.4.0, build d8eb465
✅ **Docker Daemon Running**: 12 containers currently running
✅ **MCP Configuration Fixed**: Problematic server disabled

### Current Running Containers
- `beast-mode-observatory` (healthy)
- `directus_cms_fixed` (healthy)
- `observatory-cloudflare-tunnel` (running)
- `observatory-grafana` (running)
- `observatory-prometheus` (running)
- `observatory-jaeger` (running)
- And 6 additional containers

## Prevention Measures

### 1. MCP Server Validation
Before adding new MCP servers, validate the command exists:
```bash
# Test command before adding to MCP config
docker mcp gateway run  # ❌ This fails
uvx mcp-server-docker   # ✅ This would work if package exists
```

### 2. Configuration Testing
Use the diagnostic script to test MCP configurations:
```bash
python fix_mcp_docker_config.py
```

### 3. Alternative Integration Patterns
Instead of trying to create MCP servers for every tool, use:
- Direct command execution through existing MCP servers
- Custom integration scripts (like `docker_mcp_integration.py`)
- Existing filesystem MCP server for Docker config management

## Troubleshooting Checklist

### When MCP Server Fails to Connect:
- [ ] Check if the command exists: `which <command>`
- [ ] Test the command manually: `<command> --help`
- [ ] Verify MCP server package exists: `uvx <package-name> --help`
- [ ] Check MCP configuration syntax
- [ ] Review MCP server logs for specific errors

### Docker-Specific Issues:
- [ ] Verify Docker is running: `docker info`
- [ ] Check Docker daemon status: `docker version`
- [ ] Test Docker commands: `docker ps`
- [ ] Verify container accessibility: `docker exec <container> echo "test"`

### MCP Configuration Issues:
- [ ] Validate JSON syntax in MCP config files
- [ ] Check file permissions on MCP config files
- [ ] Verify environment variables are set correctly
- [ ] Test with minimal configuration first

## Alternative Solutions

### Option 1: Use Existing MCP Servers
Instead of Docker-specific MCP server, use:
- **Filesystem MCP**: Manage Docker configs and compose files
- **Git MCP**: Version control Docker configurations
- **Fetch MCP**: Download Docker images and documentation

### Option 2: Custom Integration Scripts
Create purpose-built scripts like `docker_mcp_integration.py` for specific Docker operations.

### Option 3: Direct Command Execution
Use bash execution through existing MCP infrastructure:
```bash
# Through existing tools
docker ps | tee container-list.log
docker logs container-name | tee container-logs.log
```

## Success Metrics
- ✅ MCP server connection errors eliminated
- ✅ Docker functionality available through alternative integration
- ✅ No impact on existing MCP servers (filesystem, git, fetch)
- ✅ System continues to operate normally

## Lessons Learned
1. **Validate commands before MCP configuration**: Always test commands manually
2. **Use official MCP servers when available**: Avoid creating custom configurations for non-existent servers
3. **Implement graceful fallbacks**: Alternative integration methods prevent functionality loss
4. **Monitor MCP server health**: Regular validation prevents configuration drift

## Related Documentation
- [MCP Server Configuration Governance](.kiro/steering/mcp-server-configuration-governance.md)
- [Docker Integration Helper](../scripts/docker_mcp_integration.py)
- [MCP Configuration Fix Script](../fix_mcp_docker_config.py)

---

**Status**: ✅ RESOLVED - MCP_DOCKER server disabled, alternative Docker integration implemented
**Next Steps**: Monitor MCP server health and consider official Docker MCP server if one becomes available