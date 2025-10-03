#!/usr/bin/env python3
"""
MCP Filesystem Operations Test Script
Tests basic filesystem operations and integration with Kiro.
"""

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any, List


def test_mcp_server_connection() -> Dict[str, Any]:
    """Test if MCP filesystem server can be started and connected to."""
    result = {
        "test": "mcp_server_connection",
        "status": "unknown",
        "details": {}
    }
    
    try:
        # Test server startup with help command
        proc = subprocess.run(
            ["uvx", "mcp-filesystem", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if proc.returncode == 0:
            result["status"] = "success"
            result["details"]["help_output"] = proc.stdout[:200]
        else:
            result["status"] = "error"
            result["details"]["error"] = proc.stderr
            
    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["details"]["error"] = "Server startup timed out"
    except Exception as e:
        result["status"] = "error"
        result["details"]["error"] = str(e)
    
    return result


def test_configuration_validation() -> Dict[str, Any]:
    """Test if the MCP configuration is valid."""
    result = {
        "test": "configuration_validation",
        "status": "unknown",
        "details": {}
    }
    
    try:
        # Check if config file exists
        config_path = Path("mcp-filesystem-config.toml")
        if not config_path.exists():
            result["status"] = "error"
            result["details"]["error"] = "Configuration file not found"
            return result
        
        # Check if mcp.json exists and is valid
        mcp_config_path = Path(".kiro/settings/mcp.json")
        if not mcp_config_path.exists():
            result["status"] = "error"
            result["details"]["error"] = "MCP settings file not found"
            return result
        
        with open(mcp_config_path, 'r') as f:
            mcp_config = json.load(f)
        
        filesystem_config = mcp_config.get("mcpServers", {}).get("filesystem", {})
        if not filesystem_config:
            result["status"] = "error"
            result["details"]["error"] = "Filesystem server not configured"
            return result
        
        result["status"] = "success"
        result["details"]["config"] = {
            "disabled": filesystem_config.get("disabled", True),
            "command": filesystem_config.get("command"),
            "args": filesystem_config.get("args", []),
            "env_vars": list(filesystem_config.get("env", {}).keys())
        }
        
    except Exception as e:
        result["status"] = "error"
        result["details"]["error"] = str(e)
    
    return result


def test_environment_variables() -> Dict[str, Any]:
    """Test if environment variables are properly configured."""
    result = {
        "test": "environment_variables",
        "status": "unknown",
        "details": {}
    }
    
    try:
        # Load MCP config to check environment variables
        with open(".kiro/settings/mcp.json", 'r') as f:
            mcp_config = json.load(f)
        
        filesystem_config = mcp_config.get("mcpServers", {}).get("filesystem", {})
        env_vars = filesystem_config.get("env", {})
        
        expected_vars = [
            "MCP_FILESYSTEM_ROOT",
            "MCP_FILESYSTEM_LOG_LEVEL", 
            "MCP_FILESYSTEM_ENABLE_LOGGING"
        ]
        
        missing_vars = [var for var in expected_vars if var not in env_vars]
        
        if missing_vars:
            result["status"] = "warning"
            result["details"]["missing_vars"] = missing_vars
        else:
            result["status"] = "success"
        
        result["details"]["configured_vars"] = env_vars
        
    except Exception as e:
        result["status"] = "error"
        result["details"]["error"] = str(e)
    
    return result


def test_file_permissions() -> Dict[str, Any]:
    """Test if file permissions are properly configured."""
    result = {
        "test": "file_permissions",
        "status": "unknown",
        "details": {}
    }
    
    try:
        # Test write access to /tmp directory
        test_file = Path("/tmp/mcp_filesystem_test.log")
        test_file.write_text("test")
        test_file.unlink()
        
        # Test current directory access
        current_dir = Path(".")
        if not current_dir.is_dir():
            result["status"] = "error"
            result["details"]["error"] = "Current directory not accessible"
            return result
        
        result["status"] = "success"
        result["details"]["writable_locations"] = ["/tmp", str(current_dir.absolute())]
        
    except Exception as e:
        result["status"] = "error"
        result["details"]["error"] = str(e)
    
    return result


def run_diagnostic_tests() -> Dict[str, Any]:
    """Run all diagnostic tests for MCP filesystem server."""
    print("🔍 MCP Filesystem Operations Test Suite")
    print("=" * 50)
    
    tests = [
        test_mcp_server_connection,
        test_configuration_validation,
        test_environment_variables,
        test_file_permissions
    ]
    
    results = {}
    
    for test_func in tests:
        print(f"\n🧪 Running: {test_func.__name__}")
        result = test_func()
        results[result["test"]] = result
        
        status_emoji = {
            "success": "✅",
            "warning": "⚠️", 
            "error": "❌",
            "timeout": "⏱️",
            "unknown": "❓"
        }
        
        print(f"  Status: {status_emoji.get(result['status'], '❓')} {result['status']}")
        
        if result.get("details", {}).get("error"):
            print(f"  Error: {result['details']['error']}")
        
        if result["status"] == "success" and result["details"]:
            for key, value in result["details"].items():
                if key != "error":
                    print(f"  {key}: {value}")
    
    # Summary
    print(f"\n" + "=" * 50)
    success_count = sum(1 for r in results.values() if r["status"] == "success")
    total_count = len(results)
    print(f"✨ Tests completed: {success_count}/{total_count} successful")
    
    return results


def main():
    """Main function to run MCP filesystem tests."""
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        # Output JSON for programmatic use
        results = {}
        for test_func in [test_mcp_server_connection, test_configuration_validation, 
                         test_environment_variables, test_file_permissions]:
            result = test_func()
            results[result["test"]] = result
        print(json.dumps(results, indent=2))
    else:
        # Interactive output
        run_diagnostic_tests()


if __name__ == "__main__":
    main()