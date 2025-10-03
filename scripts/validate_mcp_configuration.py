#!/usr/bin/env python3
"""
MCP Configuration Validation Script
Validates mcp.json configuration before applying changes.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple


def validate_json_syntax(config_path: Path) -> Tuple[bool, str]:
    """Validate JSON syntax of configuration file."""
    try:
        with open(config_path, 'r') as f:
            json.load(f)
        return True, "Valid JSON syntax"
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON syntax: {e}"
    except Exception as e:
        return False, f"Error reading file: {e}"


def validate_server_configuration(server_name: str, server_config: Dict[str, Any]) -> List[str]:
    """Validate individual server configuration."""
    errors = []
    
    # Required fields
    if "command" not in server_config:
        errors.append(f"{server_name}: Missing 'command' field")
    
    if "args" not in server_config:
        errors.append(f"{server_name}: Missing 'args' field")
    elif not isinstance(server_config["args"], list):
        errors.append(f"{server_name}: 'args' must be a list")
    
    # Optional but recommended fields
    if "env" in server_config and not isinstance(server_config["env"], dict):
        errors.append(f"{server_name}: 'env' must be a dictionary")
    
    if "autoApprove" in server_config and not isinstance(server_config["autoApprove"], list):
        errors.append(f"{server_name}: 'autoApprove' must be a list")
    
    if "disabled" in server_config and not isinstance(server_config["disabled"], bool):
        errors.append(f"{server_name}: 'disabled' must be a boolean")
    
    return errors


def validate_filesystem_server_config(server_config: Dict[str, Any]) -> List[str]:
    """Validate filesystem-specific configuration."""
    errors = []
    
    # Check for problematic arguments
    args = server_config.get("args", [])
    if "--path" in args:
        errors.append("filesystem: '--path' argument is not supported, use environment variables instead")
    
    # Check for required configuration file
    if "--config" in args:
        config_index = args.index("--config")
        if config_index + 1 < len(args):
            config_file = args[config_index + 1]
            if not Path(config_file).exists():
                errors.append(f"filesystem: Configuration file '{config_file}' not found")
    
    # Check environment variables
    env = server_config.get("env", {})
    recommended_env_vars = [
        "MCP_FILESYSTEM_ROOT",
        "MCP_FILESYSTEM_LOG_LEVEL",
        "MCP_FILESYSTEM_ENABLE_LOGGING"
    ]
    
    missing_env_vars = [var for var in recommended_env_vars if var not in env]
    if missing_env_vars:
        errors.append(f"filesystem: Missing recommended environment variables: {missing_env_vars}")
    
    return errors


def test_server_executable(server_config: Dict[str, Any]) -> Tuple[bool, str]:
    """Test if server command is executable."""
    command = server_config.get("command")
    if not command:
        return False, "No command specified"
    
    try:
        # Test with --help to see if command exists
        proc = subprocess.run(
            [command, "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if proc.returncode == 0:
            return True, "Command executable"
        else:
            return False, f"Command failed: {proc.stderr[:200]}"
            
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except FileNotFoundError:
        return False, f"Command '{command}' not found"
    except Exception as e:
        return False, f"Error testing command: {e}"


def validate_mcp_configuration(config_path: str = ".kiro/settings/mcp.json") -> Dict[str, Any]:
    """Validate complete MCP configuration."""
    config_path = Path(config_path)
    
    result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "servers_tested": 0,
        "servers_valid": 0
    }
    
    # Check if file exists
    if not config_path.exists():
        result["valid"] = False
        result["errors"].append(f"Configuration file not found: {config_path}")
        return result
    
    # Validate JSON syntax
    json_valid, json_message = validate_json_syntax(config_path)
    if not json_valid:
        result["valid"] = False
        result["errors"].append(json_message)
        return result
    
    # Load configuration
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except Exception as e:
        result["valid"] = False
        result["errors"].append(f"Error loading configuration: {e}")
        return result
    
    # Validate structure
    if "mcpServers" not in config:
        result["valid"] = False
        result["errors"].append("Missing 'mcpServers' section")
        return result
    
    servers = config["mcpServers"]
    if not isinstance(servers, dict):
        result["valid"] = False
        result["errors"].append("'mcpServers' must be a dictionary")
        return result
    
    # Validate each server
    for server_name, server_config in servers.items():
        result["servers_tested"] += 1
        
        # Basic validation
        server_errors = validate_server_configuration(server_name, server_config)
        result["errors"].extend(server_errors)
        
        # Filesystem-specific validation
        if server_name == "filesystem":
            fs_errors = validate_filesystem_server_config(server_config)
            result["errors"].extend(fs_errors)
        
        # Test if server is executable (only if not disabled)
        if not server_config.get("disabled", False):
            executable, exec_message = test_server_executable(server_config)
            if not executable:
                result["warnings"].append(f"{server_name}: {exec_message}")
            else:
                result["servers_valid"] += 1
        else:
            result["servers_valid"] += 1  # Disabled servers are considered valid
    
    # Final validation
    if result["errors"]:
        result["valid"] = False
    
    return result


def main():
    """Main function for configuration validation."""
    config_path = ".kiro/settings/mcp.json"
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("Usage: python validate_mcp_configuration.py [config_path]")
            print("Validates MCP server configuration file.")
            return
        else:
            config_path = sys.argv[1]
    
    print("🔍 MCP Configuration Validation")
    print("=" * 40)
    print(f"📁 Validating: {config_path}")
    
    result = validate_mcp_configuration(config_path)
    
    # Display results
    if result["valid"]:
        print("✅ Configuration is valid!")
    else:
        print("❌ Configuration has errors!")
    
    print(f"\n📊 Summary:")
    print(f"  Servers tested: {result['servers_tested']}")
    print(f"  Servers valid: {result['servers_valid']}")
    
    if result["errors"]:
        print(f"\n❌ Errors ({len(result['errors'])}):")
        for error in result["errors"]:
            print(f"  • {error}")
    
    if result["warnings"]:
        print(f"\n⚠️ Warnings ({len(result['warnings'])}):")
        for warning in result["warnings"]:
            print(f"  • {warning}")
    
    if result["valid"]:
        print("\n✨ Configuration ready for use!")
    else:
        print("\n🔧 Please fix errors before using configuration.")
        sys.exit(1)


if __name__ == "__main__":
    main()