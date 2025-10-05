# MCP Filesystem Server Troubleshooting Guide

## Overview

This guide provides comprehensive troubleshooting procedures for the MCP filesystem server, including common issues, diagnostic steps, and recovery procedures.

## Quick Diagnostic Commands

```bash
# Test all MCP servers
python scripts/debug_mcp_servers.py

# Test filesystem operations specifically
python scripts/test_mcp_filesystem_operations.py

# Validate configuration
python scripts/validate_mcp_configuration.py

# Monitor server health
python scripts/monitor_mcp_server_health.py
```

## Common Issues and Solutions

### Issue 1: "unrecognized arguments" Error

**Symptoms:**
- MCP server fails to start
- Error message contains "unrecognized arguments: --path"

**Root Cause:**
The `mcp-filesystem` package doesn't support the `--path` argument directly.

**Solution:**
1. Remove `--path` argument from `.kiro/settings/mcp.json`
2. Use environment variables instead:
   ```json
   "env": {
     "MCP_FILESYSTEM_ROOT": ".",
     "MCP_FILESYSTEM_LOG_LEVEL": "ERROR"
   }
   ```

**Validation:**
```bash
python scripts/validate_mcp_configuration.py
```

### Issue 2: File System Permission Errors

**Symptoms:**
- Server crashes with "Read-only file system" errors
- Log files cannot be created

**Root Cause:**
Server attempting to write logs to read-only locations.

**Solution:**
1. Configure logging to writable directory in `mcp-filesystem-config.toml`:
   ```toml
   [filesystem]
   enable_logging = false
   log_file = "/tmp/mcp_filesystem.log"
   ```

2. Set environment variables to disable problematic logging:
   ```json
   "env": {
     "MCP_FILESYSTEM_ENABLE_LOGGING": "false"
   }
   ```

**Validation:**
```bash
python scripts/test_mcp_filesystem_operations.py
```

### Issue 3: Server Connection Failures

**Symptoms:**
- MCP server appears to start but doesn't respond
- Connection timeouts in Kiro

**Root Cause:**
Configuration issues or server startup problems.

**Diagnostic Steps:**
1. Test server manually:
   ```bash
   uvx mcp-filesystem --help
   ```

2. Check configuration:
   ```bash
   python scripts/validate_mcp_configuration.py
   ```

3. Test with specific config:
   ```bash
   uvx mcp-filesystem --config mcp-filesystem-config.toml --stdio
   ```

**Solution:**
1. Verify uvx installation: `uvx --version`
2. Check mcp-filesystem package: `uvx list`
3. Reinstall if needed: `uvx install mcp-filesystem`

### Issue 4: Environment Variable Problems

**Symptoms:**
- Server starts but doesn't respect configuration
- Filesystem operations fail

**Root Cause:**
Missing or incorrect environment variables.

**Solution:**
Ensure all required environment variables are set in `.kiro/settings/mcp.json`:
```json
"env": {
  "PYTHONPATH": ".",
  "MCP_FILESYSTEM_ROOT": ".",
  "MCP_FILESYSTEM_LOG_LEVEL": "ERROR",
  "MCP_FILESYSTEM_ENABLE_LOGGING": "false"
}
```

**Validation:**
```bash
python scripts/test_mcp_filesystem_operations.py
```

## Diagnostic Procedures

### Step 1: Basic System Check

```bash
# Check if uvx is installed
uvx --version

# Check if mcp-filesystem is available
uvx list | grep filesystem

# Test basic server functionality
uvx mcp-filesystem --help
```

### Step 2: Configuration Validation

```bash
# Validate MCP configuration
python scripts/validate_mcp_configuration.py

# Check configuration file exists
ls -la mcp-filesystem-config.toml

# Validate JSON syntax
python -m json.tool .kiro/settings/mcp.json
```

### Step 3: Permission Testing

```bash
# Test write access to temp directory
touch /tmp/test_mcp_write && rm /tmp/test_mcp_write

# Test current directory access
ls -la .

# Check file permissions
python scripts/test_mcp_filesystem_operations.py
```

### Step 4: Server Health Monitoring

```bash
# Single health check
python scripts/monitor_mcp_server_health.py

# Continuous monitoring
python scripts/monitor_mcp_server_health.py --continuous 60

# JSON output for automation
python scripts/monitor_mcp_server_health.py --json
```

## Recovery Procedures

### Complete Server Reset

1. **Stop all MCP processes:**
   ```bash
   pkill -f mcp-filesystem
   ```

2. **Backup current configuration:**
   ```bash
   cp .kiro/settings/mcp.json .kiro/settings/mcp.json.backup
   ```

3. **Validate configuration:**
   ```bash
   python scripts/validate_mcp_configuration.py
   ```

4. **Test server startup:**
   ```bash
   python scripts/debug_mcp_servers.py
   ```

5. **Run comprehensive tests:**
   ```bash
   python scripts/test_mcp_filesystem_operations.py
   ```

### Emergency Fallback

If the filesystem server cannot be fixed:

1. **Disable filesystem server temporarily:**
   ```json
   "filesystem": {
     "disabled": true,
     ...
   }
   ```

2. **Use alternative file access methods:**
   - Direct file operations through other tools
   - Manual file reading/writing
   - Alternative MCP servers

3. **Monitor other servers:**
   ```bash
   python scripts/monitor_mcp_server_health.py
   ```

## Configuration Examples

### Working Configuration (mcp.json)

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "uvx",
      "args": [
        "mcp-filesystem",
        "--config",
        "mcp-filesystem-config.toml",
        "--stdio"
      ],
      "env": {
        "PYTHONPATH": ".",
        "MCP_FILESYSTEM_ROOT": ".",
        "MCP_FILESYSTEM_LOG_LEVEL": "ERROR",
        "MCP_FILESYSTEM_ENABLE_LOGGING": "false"
      },
      "disabled": false,
      "autoApprove": [
        "read_file",
        "list_directory"
      ],
      "disabledTools": []
    }
  }
}
```

### Working Configuration (mcp-filesystem-config.toml)

```toml
[filesystem]
# Root directory for filesystem access
root_path = "."

# Allowed file extensions (empty means all)
allowed_extensions = []

# Maximum file size in bytes (0 means no limit)
max_file_size = 10485760  # 10MB

# Disable logging to avoid permission issues
enable_logging = false

# Log file location (use writable directory)
log_file = "/tmp/mcp_filesystem.log"

[server]
# Server configuration
host = "127.0.0.1"
port = 8001
```

## Monitoring and Maintenance

### Regular Health Checks

Set up periodic health monitoring:

```bash
# Add to crontab for hourly checks
0 * * * * /path/to/python scripts/monitor_mcp_server_health.py --json >> logs/mcp_health_cron.log
```

### Log Monitoring

Monitor MCP health logs:

```bash
# View recent health events
tail -f logs/mcp_health.log

# Search for errors
grep -i error logs/mcp_health.log

# Count health check results
grep "Health check complete" logs/mcp_health.log | tail -10
```

### Performance Monitoring

Track server response times:

```bash
# Get performance metrics
python scripts/monitor_mcp_server_health.py --json | jq '.servers[].response_time'
```

## Getting Help

### Recovery Procedures by Server

```bash
# Get specific recovery procedures
python scripts/monitor_mcp_server_health.py --recovery filesystem
```

### Debug Information Collection

When reporting issues, collect this information:

```bash
# System information
uname -a
python --version
uvx --version

# MCP configuration
python scripts/validate_mcp_configuration.py

# Server health
python scripts/monitor_mcp_server_health.py --json

# Recent logs
tail -50 logs/mcp_health.log
```

## Success Metrics

- **Zero "unrecognized arguments" errors**
- **Zero file system permission errors**
- **100% server connection success rate**
- **All filesystem MCP operations working correctly**
- **Stable configuration over time**

## Maintenance Schedule

- **Daily:** Monitor server health logs
- **Weekly:** Run comprehensive diagnostic tests
- **Monthly:** Review and update configuration
- **Quarterly:** Update MCP packages and dependencies

---

*This troubleshooting guide ensures systematic resolution of MCP filesystem server issues and provides clear procedures for maintaining stable operation.*