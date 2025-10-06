# MCP Filesystem Server Fix Design

## Overview

This design addresses the systematic resolution of MCP filesystem server configuration issues, focusing on command-line argument compatibility and file system permission handling. The solution ensures full compliance with all four requirements while maintaining compatibility with existing Kiro MCP infrastructure.

## Requirements Alignment

### Requirement 1: Fix Command Line Arguments
**Design Response**: Configuration Resolver component removes unsupported `--path` argument and implements environment variable-based configuration (MCP_FILESYSTEM_ROOT) to maintain functionality while using supported CLI interface.

### Requirement 2: Resolve File System Permission Issues  
**Design Response**: Permission Handler component implements multi-tier logging strategy: writable directory locations (/tmp, ~/.cache), graceful degradation to disable file logging, and fallback mechanisms to ensure server functionality regardless of permission constraints.

### Requirement 3: Validate MCP Server Functionality
**Design Response**: Validation System component provides comprehensive testing of Kiro integration, filesystem operations (list_directory, read_file), and auto-approved tool compatibility through systematic validation procedures.

### Requirement 4: Prevent Configuration Regression
**Design Response**: Configuration Regression Prevention framework includes documentation templates, compatibility monitoring, diagnostic procedures, and pre-deployment validation to ensure long-term stability and maintainability.

## Root Cause Analysis

### Issue 1: Command Line Arguments
- **Error**: `unrecognized arguments: --path .`
- **Cause**: The mcp-filesystem package doesn't support the `--path` argument in the current version
- **Impact**: Server fails to start, preventing filesystem MCP operations

### Issue 2: File System Permissions
- **Error**: `OSError: [Errno 30] Read-only file system: '/mcp_filesystem.log'`
- **Cause**: Server attempts to write log file to root directory which is read-only
- **Impact**: Server crashes during initialization due to logging setup failure

## Architecture

### Configuration Strategy
```
MCP Configuration → uvx Execution → mcp-filesystem Server
                 ↓
            Environment Variables → Working Directory Setup
                 ↓
            Logging Configuration → Writable Directory
```

### Component Design

#### 1. Configuration Resolver
- **Purpose**: Determine correct mcp-filesystem arguments
- **Method**: Check package documentation and test valid arguments
- **Output**: Working MCP server configuration

#### 2. Permission Handler
- **Purpose**: Ensure logging works within file system constraints
- **Method**: Use environment variables to control logging location
- **Output**: Server starts without permission errors

#### 3. Validation System (Requirement 3)
- **Purpose**: Verify MCP server functionality after fixes and ensure Kiro integration
- **Method**: Test basic filesystem operations (list_directory, read_file) through MCP interface
- **Validation Points**: 
  - Server connection and registration with Kiro (Requirement 3.1)
  - Filesystem operations execute without connection errors (Requirement 3.2)
  - Auto-approved tools maintain compatibility (Requirement 3.4)
- **Output**: Confirmed working filesystem MCP tools with full Kiro integration

## Implementation Strategy

### Phase 1: Research and Fix Arguments
1. **Investigate mcp-filesystem CLI**: Determine supported arguments
2. **Test configurations**: Validate working argument combinations
3. **Update configuration**: Apply correct arguments to mcp.json

### Phase 2: Resolve Permission Issues
1. **Environment variable approach**: Use env vars to control logging
2. **Alternative logging setup**: Disable file logging if necessary
3. **Test permission handling**: Verify no more permission errors

### Phase 3: Validation and Documentation
1. **Functional testing**: Verify MCP filesystem operations work
2. **Configuration documentation**: Document working setup
3. **Troubleshooting guide**: Create diagnostic procedures

## Technical Solutions

**Design Rationale**: These solutions address the core requirements while maintaining compatibility with existing uvx-based execution and preserving auto-approved tools (Requirement 1.4, Technical Constraints).

### Solution 1: Remove Unsupported Arguments (Requirement 1.1, 1.2)
```json
{
  "filesystem": {
    "command": "uvx",
    "args": ["mcp-filesystem"],  // Remove --path argument
    "env": {
      "MCP_FILESYSTEM_ROOT": "."  // Use environment variable instead
    }
  }
}
```
**Rationale**: Eliminates "unrecognized arguments" errors by using supported CLI interface while maintaining functionality through environment variables.

### Solution 2: Control Logging Location (Requirement 2.1, 2.4)
```json
{
  "filesystem": {
    "command": "uvx",
    "args": ["mcp-filesystem"],
    "env": {
      "MCP_FILESYSTEM_ROOT": ".",
      "MCP_FILESYSTEM_LOG_FILE": "/tmp/mcp_filesystem.log"  // Writable location
    }
  }
}
```
**Rationale**: Uses user-writable directories (/tmp, ~/.cache) to prevent permission errors while maintaining logging functionality.

### Solution 3: Graceful Logging Degradation (Requirement 2.2, 2.3)
```json
{
  "filesystem": {
    "command": "uvx",
    "args": ["mcp-filesystem"],
    "env": {
      "MCP_FILESYSTEM_ROOT": ".",
      "MCP_FILESYSTEM_NO_LOG_FILE": "true"  // Disable file logging
    }
  }
}
```
**Rationale**: Ensures server functionality even when file logging is impossible, maintaining core MCP operations without permission dependencies.

### Solution 4: Configuration Validation (Requirement 4.4)
**Pre-deployment validation script** that:
- Tests mcp-filesystem CLI arguments before applying
- Validates environment variable recognition
- Confirms server startup without errors
- Verifies filesystem operations work correctly

## Error Handling

### Configuration Validation
- Validate MCP server arguments before applying
- Test server startup in isolation
- Provide clear error messages for configuration issues

### Permission Fallbacks
- Try multiple logging locations in order of preference
- Gracefully disable file logging if all locations fail
- Maintain server functionality even without file logging

### Connection Recovery
- Implement retry logic for MCP server connections
- Provide diagnostic information for connection failures
- Enable manual server restart without full Kiro restart

## Testing Strategy

### Unit Testing
- Test configuration parsing and validation
- Test environment variable handling
- Test permission checking logic

### Integration Testing
- Test MCP server startup with new configuration
- Test filesystem operations through MCP interface
- Test error handling and recovery scenarios

### System Testing
- Verify full Kiro integration with fixed MCP server
- Test auto-approved operations work correctly
- Validate no regression in existing functionality

## Monitoring and Observability

### Success Metrics
**Aligned with Requirements Success Criteria:**
- MCP filesystem server starts without errors (Requirement 1)
- No "unrecognized arguments" messages in logs (Requirement 1)
- No file system permission errors in logs (Requirement 2)
- Filesystem MCP tools function correctly in Kiro (Requirement 3)
- Configuration is documented and maintainable (Requirement 4)
- MCP server connection success rate: 100%
- Filesystem operation success rate: >95%
- Configuration stability over time

### Diagnostic Tools
**Comprehensive Diagnostic Suite (Requirement 4.3):**
- **MCP Server Health Check Script**: Automated connectivity and functionality validation
- **Configuration Validation Tool**: Pre-deployment configuration testing
- **Filesystem Operation Tester**: Validates read_file and list_directory operations
- **Environment Variable Validator**: Ensures proper environment setup
- **Log Analysis Tools**: Automated error pattern detection and troubleshooting guidance
- **Regression Detection**: Monitors for configuration drift over time

## Deployment Strategy

### Rollout Plan
1. **Development testing**: Validate fixes in development environment
2. **Configuration backup**: Save current configuration before changes
3. **Incremental deployment**: Apply fixes one at a time
4. **Validation testing**: Verify each fix before proceeding
5. **Documentation update**: Update troubleshooting guides

### Rollback Plan
- Restore previous mcp.json configuration
- Clear any problematic environment variables
- Restart MCP server connections
- Validate rollback success

## Configuration Regression Prevention (Requirement 4)

### Documentation Strategy
**Working Configuration Examples (Requirement 4.1):**
- Complete mcp.json configuration templates
- Environment variable setup guides
- Step-by-step troubleshooting procedures
- Common error patterns and solutions

### Compatibility Monitoring (Requirement 4.2)
**Package Update Validation:**
- Automated testing of configuration with new mcp-filesystem versions
- CLI argument compatibility checks
- Environment variable behavior validation
- Regression test suite for core functionality

### Diagnostic Procedures (Requirement 4.3)
**Systematic Troubleshooting Guide:**
1. **Connection Issues**: MCP server registration problems
2. **Permission Errors**: File system access and logging issues
3. **Argument Errors**: CLI compatibility problems
4. **Performance Issues**: Slow or failing filesystem operations

### Validation Framework (Requirement 4.4)
**Pre-deployment Configuration Testing:**
- Configuration syntax validation
- Environment variable completeness checks
- Server startup simulation
- Filesystem operation testing

## Future Considerations

### Package Updates
- Monitor mcp-filesystem package for argument changes
- Test configuration compatibility with new versions
- Update documentation as package evolves
- Maintain backward compatibility where possible

### Alternative Solutions
- Consider alternative filesystem MCP servers if issues persist
- Evaluate custom MCP server implementation if needed
- Plan for migration to different MCP architectures
- Document migration paths for future flexibility

## Technical Constraints Compliance

**Existing System Compatibility:**
- ✅ Maintains uvx-based MCP server execution
- ✅ Preserves auto-approved tools (read_file, list_directory)
- ✅ Works within macOS file system permission constraints
- ✅ Requires no root privileges or system-level changes

**Implementation Boundaries:**
- Must not break existing Kiro MCP integration
- Must maintain current security model
- Must work with existing .kiro/settings/mcp.json structure
- Must support existing auto-approval mechanisms

## Dependencies

- uvx package manager for MCP server execution
- mcp-filesystem package (current version compatibility)
- Kiro MCP integration system
- macOS file system permissions and constraints
- Environment variable support in mcp-filesystem package