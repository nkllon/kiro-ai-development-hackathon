# MCP Filesystem Server Troubleshooting Guide

## Common Issue: Read-only File System Error

### Problem Description
The MCP filesystem server fails to start with the error:
```
OSError: [Errno 30] Read-only file system: '/mcp_filesystem.log'
```

### Root Cause
The mcp-filesystem server attempts to create a log file in the root directory (`/mcp_filesystem.log`), which is read-only on most systems.

### Solution

#### Automatic Fix
Run the automated fix script:
```bash
python3 scripts/fix_mcp_filesystem_logging.py
```

#### Manual Fix

1. **Update MCP Configuration** (`.kiro/settings/mcp.json`):
```json
{
  "mcpServers": {
    "filesystem": {
      "env": {
        "MCP_FILESYSTEM_ENABLE_LOGGING": "false",
        "MCP_FILESYSTEM_LOG_LEVEL": "CRITICAL",
        "MCP_FILESYSTEM_LOG_FILE": "/tmp/mcp_filesystem.log"
      }
    }
  }
}
```

2. **Update TOML Configuration** (`mcp-filesystem-config.toml`):
```toml
[filesystem]
enable_logging = false
log_file = "/tmp/mcp_filesystem.log"
```

3. **Restart Kiro** to reload the MCP configuration.

### Verification

After applying the fix, you should see successful MCP operations in the logs:
```
[info] [filesystem] MCP Tool Call
  Tool: create_directory
  Arguments: {"path":"docs/use-cases","exist_ok":true}
  
[debug] [filesystem] MCP Tool Response (isError = false):
  目标路径: /path/to/directory
  操作状态: 成功
```

### Alternative Solutions

#### Option 1: Use Different MCP Server
If issues persist, consider using the built-in file operations or a different MCP server:
```json
{
  "mcpServers": {
    "filesystem-alt": {
      "command": "uvx",
      "args": ["mcp-server-filesystem"],
      "env": {
        "FILESYSTEM_ROOT": "."
      }
    }
  }
}
```

#### Option 2: Disable Logging Completely
Set environment variables to completely disable logging:
```bash
export MCP_FILESYSTEM_ENABLE_LOGGING=false
export MCP_FILESYSTEM_LOG_LEVEL=CRITICAL
```

### Prevention

To prevent this issue in the future:

1. **Always use writable directories** for log files (e.g., `/tmp`, `~/logs`)
2. **Set logging to false** for production environments
3. **Test MCP server configuration** before deployment
4. **Use environment variables** to override default settings

### Debugging Commands

```bash
# Test MCP server directly
uvx mcp-filesystem --config mcp-filesystem-config.toml --stdio

# Check environment variables
env | grep MCP_FILESYSTEM

# Verify log file permissions
ls -la /tmp/mcp_filesystem.log

# Test directory creation
mkdir -p test-dir && rmdir test-dir
```

### Related Issues

- **Permission denied errors**: Check file system permissions
- **Connection timeouts**: Verify server startup and stdio communication
- **Configuration not loading**: Ensure TOML file syntax is correct

### Success Indicators

✅ MCP server starts without errors  
✅ Directory creation operations succeed  
✅ File operations complete successfully  
✅ No permission-related error messages  

### Emergency Recovery

If the MCP server is completely broken:

1. **Disable the server temporarily**:
```json
{
  "mcpServers": {
    "filesystem": {
      "disabled": true
    }
  }
}
```

2. **Use built-in file operations** until the issue is resolved
3. **Restart Kiro** to apply changes
4. **Re-enable after fixing** the configuration

---

*This guide addresses the most common MCP filesystem server issues. For additional problems, check the Kiro MCP server logs and error messages.*