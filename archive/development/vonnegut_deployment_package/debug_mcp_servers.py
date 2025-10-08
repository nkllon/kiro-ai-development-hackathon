#!/usr/bin/env python3
"""
MCP Server Debug Tool
Helps diagnose and fix MCP server configuration issues.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List


def load_mcp_config(config_path: str) -> Dict[str, Any]:
    """Load MCP configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading MCP config from {config_path}: {e}")
        return {}


def test_server_command(server_name: str, server_config: Dict[str, Any]) -> Dict[str, Any]:
    """Test if an MCP server command can be executed."""
    result = {
        "server": server_name,
        "status": "unknown",
        "error": None,
        "help_output": None
    }
    
    if server_config.get("disabled", False):
        result["status"] = "disabled"
        return result
    
    command = server_config.get("command", "")
    args = server_config.get("args", [])
    
    if not command:
        result["status"] = "error"
        result["error"] = "No command specified"
        return result
    
    # Try to get help output
    try:
        help_cmd = [command] + args + ["--help"]
        proc = subprocess.run(
            help_cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if proc.returncode == 0:
            result["status"] = "ok"
            result["help_output"] = proc.stdout[:500]  # First 500 chars
        else:
            result["status"] = "error"
            result["error"] = proc.stderr[:500]
            
    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["error"] = "Command timed out"
    except FileNotFoundError:
        result["status"] = "not_found"
        result["error"] = f"Command '{command}' not found"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    return result


def suggest_fixes(server_name: str, test_result: Dict[str, Any]) -> List[str]:
    """Suggest fixes based on test results."""
    suggestions = []
    
    if test_result["status"] == "not_found":
        suggestions.append(f"Install the server: uvx install {server_name}")
        suggestions.append("Check if uvx is installed and in PATH")
    
    elif test_result["status"] == "error":
        error = test_result.get("error", "")
        
        if "unrecognized arguments" in error:
            suggestions.append("Check server documentation for correct arguments")
            suggestions.append("Try removing problematic arguments from config")
        
        if "Read-only file system" in error:
            suggestions.append("Change log file location to writable directory")
            suggestions.append("Disable logging in server configuration")
        
        if "permission" in error.lower():
            suggestions.append("Check file/directory permissions")
            suggestions.append("Run with appropriate user permissions")
    
    elif test_result["status"] == "timeout":
        suggestions.append("Server may be hanging - check configuration")
        suggestions.append("Try simpler configuration options")
    
    return suggestions


def main():
    """Main diagnostic function."""
    print("🔍 MCP Server Diagnostic Tool")
    print("=" * 40)
    
    # Check workspace and user configs
    configs_to_check = [
        ".kiro/settings/mcp.json",
        "~/.kiro/settings/mcp.json"
    ]
    
    all_servers = {}
    
    for config_path in configs_to_check:
        expanded_path = Path(config_path).expanduser()
        if expanded_path.exists():
            print(f"\n📁 Checking config: {config_path}")
            config = load_mcp_config(str(expanded_path))
            servers = config.get("mcpServers", {})
            
            for server_name, server_config in servers.items():
                if server_name not in all_servers:
                    all_servers[server_name] = server_config
                    print(f"  Found server: {server_name}")
    
    if not all_servers:
        print("❌ No MCP servers found in configuration files")
        return
    
    print(f"\n🧪 Testing {len(all_servers)} MCP servers...")
    print("-" * 40)
    
    for server_name, server_config in all_servers.items():
        print(f"\n🔧 Testing: {server_name}")
        
        result = test_server_command(server_name, server_config)
        
        status_emoji = {
            "ok": "✅",
            "disabled": "⏸️",
            "error": "❌",
            "not_found": "🚫",
            "timeout": "⏱️",
            "unknown": "❓"
        }
        
        print(f"  Status: {status_emoji.get(result['status'], '❓')} {result['status']}")
        
        if result.get("error"):
            print(f"  Error: {result['error']}")
        
        if result["status"] not in ["ok", "disabled"]:
            suggestions = suggest_fixes(server_name, result)
            if suggestions:
                print("  💡 Suggestions:")
                for suggestion in suggestions:
                    print(f"    • {suggestion}")
    
    print("\n" + "=" * 40)
    print("✨ Diagnostic complete!")


if __name__ == "__main__":
    main()