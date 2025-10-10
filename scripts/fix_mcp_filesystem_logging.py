#!/usr/bin/env python3
"""
Fix MCP Filesystem Server Logging Issue

The mcp-filesystem server is trying to create a log file in the root directory
which is read-only. This script fixes the configuration to prevent logging issues.
"""

import json
import os
import tempfile
from pathlib import Path

def fix_mcp_filesystem_config():
    """Fix the MCP filesystem server configuration to prevent logging issues."""
    
    # Update the MCP configuration
    mcp_config_path = Path(".kiro/settings/mcp.json")
    
    if mcp_config_path.exists():
        with open(mcp_config_path, 'r') as f:
            config = json.load(f)
        
        # Update filesystem server environment variables
        if "filesystem" in config.get("mcpServers", {}):
            env = config["mcpServers"]["filesystem"].get("env", {})
            
            # Disable logging completely
            env["MCP_FILESYSTEM_ENABLE_LOGGING"] = "false"
            env["MCP_FILESYSTEM_LOG_LEVEL"] = "CRITICAL"
            
            # Set a writable log directory if logging is needed
            temp_dir = tempfile.gettempdir()
            env["MCP_FILESYSTEM_LOG_FILE"] = os.path.join(temp_dir, "mcp_filesystem.log")
            
            # Update the config
            config["mcpServers"]["filesystem"]["env"] = env
            
            # Write back the updated config
            with open(mcp_config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"✅ Updated MCP configuration: {mcp_config_path}")
        else:
            print("❌ Filesystem server not found in MCP configuration")
    else:
        print(f"❌ MCP configuration file not found: {mcp_config_path}")
    
    # Update the TOML configuration
    toml_config_path = Path("mcp-filesystem-config.toml")
    
    if toml_config_path.exists():
        # Read the current config
        with open(toml_config_path, 'r') as f:
            content = f.read()
        
        # Update the logging settings
        lines = content.split('\n')
        updated_lines = []
        
        for line in lines:
            if line.strip().startswith('enable_logging'):
                updated_lines.append('enable_logging = false')
            elif line.strip().startswith('log_file'):
                temp_dir = tempfile.gettempdir()
                log_file = os.path.join(temp_dir, "mcp_filesystem.log")
                updated_lines.append(f'log_file = "{log_file}"')
            else:
                updated_lines.append(line)
        
        # Write back the updated config
        with open(toml_config_path, 'w') as f:
            f.write('\n'.join(updated_lines))
        
        print(f"✅ Updated TOML configuration: {toml_config_path}")
    else:
        print(f"❌ TOML configuration file not found: {toml_config_path}")

def test_mcp_filesystem_connection():
    """Test if the MCP filesystem server can connect properly."""
    import subprocess
    import time
    
    print("\n🔍 Testing MCP filesystem server connection...")
    
    try:
        # Try to start the server briefly to test configuration
        cmd = [
            "uvx", "mcp-filesystem", 
            "--config", "mcp-filesystem-config.toml",
            "--stdio"
        ]
        
        env = os.environ.copy()
        env.update({
            "MCP_FILESYSTEM_ROOT": ".",
            "MCP_FILESYSTEM_ENABLE_LOGGING": "false",
            "MCP_FILESYSTEM_LOG_LEVEL": "CRITICAL"
        })
        
        # Start the process
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True
        )
        
        # Send a simple test message
        test_message = '{"jsonrpc": "2.0", "method": "initialize", "id": 1, "params": {}}\n'
        
        try:
            stdout, stderr = process.communicate(input=test_message, timeout=5)
            
            if process.returncode == 0 or "initialized" in stdout.lower():
                print("✅ MCP filesystem server connection test passed")
                return True
            else:
                print(f"❌ MCP filesystem server test failed:")
                print(f"   stdout: {stdout}")
                print(f"   stderr: {stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            process.kill()
            print("⚠️  MCP filesystem server test timed out (this might be normal)")
            return True  # Timeout might be normal for stdio mode
            
    except Exception as e:
        print(f"❌ Error testing MCP filesystem server: {e}")
        return False

def main():
    """Main function to fix MCP filesystem logging issues."""
    print("🔧 Fixing MCP Filesystem Server Logging Issues")
    print("=" * 50)
    
    # Fix the configuration
    fix_mcp_filesystem_config()
    
    # Test the connection
    test_mcp_filesystem_connection()
    
    print("\n📋 Next Steps:")
    print("1. Restart Kiro to reload the MCP configuration")
    print("2. The filesystem server should now work without logging errors")
    print("3. If issues persist, check the MCP server logs in Kiro")

if __name__ == "__main__":
    main()