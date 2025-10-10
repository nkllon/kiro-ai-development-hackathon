# MCP Server Configuration Governance

## Core Principle

**"MCP server configurations must be systematically validated, use writable paths, and include comprehensive diagnostic tooling to prevent configuration drift and permission failures."**

## Mandatory MCP Server Configuration Standards

### Rule 1: Configuration Validation Before Deployment
**MANDATORY**: All MCP server configurations MUST be validated before deployment using automated testing tools.

#### Required Validation Steps
1. **Command-line argument validation**: Verify all arguments are supported by the target MCP server
2. **Permission validation**: Ensure all file paths are writable by the executing user
3. **Connectivity testing**: Validate server can start and respond to basic operations
4. **Integration testing**: Confirm server integrates correctly with Kiro MCP framework

### Rule 2: Writable Path Requirements
**MANDATORY**: All MCP servers that require file operations MUST use writable directories.

#### Forbidden Patterns
- ❌ **Root directory logging**: Never write logs to `/filename.log`
- ❌ **System directories**: Avoid `/var/log`, `/etc`, `/usr` without proper permissions
- ❌ **Hardcoded paths**: Never assume specific directory permissions

#### Required Patterns
- ✅ **User directories**: Use `~/.cache`, `~/.local`, or user home subdirectories
- ✅ **Temp directories**: Use system temp directories (`/tmp`, `/var/folders/...`)
- ✅ **Environment variables**: Allow path override via environment configuration
- ✅ **Graceful degradation**: Disable logging if no writable path available

### Rule 3: Systematic Diagnostic Tooling
**MANDATORY**: Every MCP server configuration MUST include diagnostic and troubleshooting tools.

#### Required Diagnostic Capabilities
1. **Configuration validation**: Scripts that test configuration before deployment
2. **Connectivity testing**: Tools that verify server startup and basic operations
3. **Error pattern recognition**: Automated detection of common configuration issues
4. **Fix suggestion system**: Actionable recommendations for identified problems

### Rule 4: Configuration Documentation Standards
**MANDATORY**: All MCP server configurations MUST be documented with working examples and troubleshooting guides.

#### Documentation Requirements
- **Working configuration examples**: Complete, tested configuration files
- **Environment variable documentation**: All configurable parameters explained
- **Troubleshooting guides**: Common issues and systematic resolution steps
- **Validation procedures**: Step-by-step testing and verification instructions

## Implementation Patterns

### Configuration File Structure
```toml
# mcp-server-config.toml - Template for MCP server configuration
[logging]
enable_logging = false  # Default to false to avoid permission issues
log_level = "CRITICAL"  # Minimal logging when enabled
log_file = "/tmp/mcp_server.log"  # Use writable temp directory

[server]
# Server-specific configuration
# Use environment variables for paths when possible
```

### Environment Variable Pattern
```json
{
  "mcpServers": {
    "server-name": {
      "command": "uvx",
      "args": ["package-name", "--config", "config.toml", "--stdio"],
      "env": {
        "MCP_SERVER_ENABLE_LOGGING": "false",
        "MCP_SERVER_LOG_LEVEL": "CRITICAL",
        "MCP_SERVER_LOG_FILE": "/tmp/mcp_server.log"
      }
    }
  }
}
```

### Diagnostic Script Template
```python
#!/usr/bin/env python3
"""
MCP Server Diagnostic Tool Template
"""

def validate_server_config(server_name: str) -> Dict[str, Any]:
    """Validate MCP server configuration systematically."""
    results = {
        "command_args": validate_command_arguments(server_name),
        "file_permissions": validate_file_permissions(server_name),
        "connectivity": test_server_connectivity(server_name),
        "integration": test_kiro_integration(server_name)
    }
    return results

def provide_fix_suggestions(validation_results: Dict[str, Any]) -> List[str]:
    """Provide specific, actionable fix suggestions."""
    suggestions = []
    # Systematic analysis of validation results
    # Specific recommendations for each failure mode
    return suggestions
```

## Lessons Learned from MCP Filesystem Server Fix

### Critical Issues Identified
1. **Command-line argument incompatibility**: `--path .` argument not supported by mcp-filesystem package
2. **Permission failures**: Attempting to write logs to read-only root directory
3. **Configuration drift**: Working configurations becoming broken over time
4. **Diagnostic gaps**: Lack of systematic troubleshooting tools

### Systematic Solutions Applied
1. **Configuration standardization**: Created proper TOML configuration files
2. **Permission remediation**: Used writable directories and environment variables
3. **Diagnostic tooling**: Built comprehensive validation and testing scripts
4. **Documentation**: Created complete troubleshooting guides and procedures

### Prevention Measures Implemented
1. **Automated validation**: Scripts that test configuration before deployment
2. **Systematic testing**: Comprehensive test suites for all MCP operations
3. **Configuration monitoring**: Tools that detect configuration drift
4. **Knowledge preservation**: Complete documentation of working configurations

## Enforcement Mechanisms

### Pre-Deployment Validation
- **MANDATORY**: Run diagnostic scripts before any MCP server configuration changes
- **REQUIRED**: Validate all file paths are writable by executing user
- **ESSENTIAL**: Test server connectivity and basic operations

### Configuration Review Process
- **Code Review Gate**: All MCP configuration changes require review
- **Testing Requirement**: New configurations must include diagnostic tools
- **Documentation Standard**: All changes must update troubleshooting guides

### Monitoring and Maintenance
- **Regular validation**: Periodic testing of all MCP server configurations
- **Configuration drift detection**: Automated monitoring for configuration changes
- **Proactive maintenance**: Regular updates to prevent compatibility issues

## Success Metrics

### Configuration Reliability
- **Zero permission failures**: No MCP servers fail due to file system permissions
- **100% startup success**: All configured MCP servers start without errors
- **Complete diagnostic coverage**: All MCP servers have validation tools
- **Comprehensive documentation**: All configurations have troubleshooting guides

### Operational Excellence
- **Fast issue resolution**: Problems identified and resolved within minutes
- **Systematic troubleshooting**: Consistent approach to all MCP server issues
- **Knowledge preservation**: All solutions documented and reusable
- **Prevention effectiveness**: Same issues don't recur after resolution

## Emergency Procedures

### When MCP Server Fails
1. **Immediate diagnosis**: Run diagnostic scripts to identify root cause
2. **Systematic resolution**: Apply documented fix procedures
3. **Validation**: Test resolution using automated validation tools
4. **Documentation update**: Capture new lessons learned in steering rules

### Configuration Recovery
1. **Identify working baseline**: Use documented working configurations
2. **Apply systematic fixes**: Use proven resolution patterns
3. **Validate thoroughly**: Ensure all functionality restored
4. **Prevent recurrence**: Update monitoring and validation tools

## The Meta-Principle

**"MCP server configurations are critical infrastructure that must be treated with the same rigor as production systems - systematic validation, comprehensive monitoring, and proactive maintenance."**

This governance ensures that MCP server configurations remain reliable, maintainable, and systematically manageable, preventing the configuration drift and permission failures that can disrupt development workflows.

---

*This steering rule is derived from the systematic resolution of MCP filesystem server configuration issues and establishes permanent governance to prevent similar failures across all MCP server configurations.*