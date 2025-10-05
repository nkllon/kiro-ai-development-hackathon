#!/usr/bin/env python3
"""
Fix MCP_DOCKER Configuration Issue

This script fixes the problematic MCP_DOCKER server configuration that's causing
connection failures due to invalid Docker commands.
"""

import json
import os
from pathlib import Path

def fix_mcp_docker_config():
    """Fix the MCP_DOCKER configuration in user-level MCP settings."""
    
    # Path to user-level MCP config
    config_path = Path.home() / ".kiro" / "settings" / "mcp.json"
    
    if not config_path.exists():
        print(f"❌ MCP config not found at {config_path}")
        return False
    
    try:
        # Read current config
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print("📋 Current MCP configuration:")
        print(json.dumps(config, indent=2))
        
        # Check if MCP_DOCKER exists and is problematic
        if "MCP_DOCKER" in config.get("mcpServers", {}):
            docker_config = config["mcpServers"]["MCP_DOCKER"]
            
            # Check if it's the problematic configuration
            if (docker_config.get("command") == "docker" and 
                docker_config.get("args") == ["mcp", "gateway", "run"]):
                
                print("\n🔍 Found problematic MCP_DOCKER configuration")
                print("❌ Invalid command: docker mcp gateway run")
                
                # Option 1: Disable the server
                print("\n🔧 Fixing by disabling MCP_DOCKER server...")
                config["mcpServers"]["MCP_DOCKER"]["disabled"] = True
                
                # Write fixed config
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
                
                print("✅ MCP_DOCKER server disabled successfully")
                print("📝 The server will no longer attempt to connect")
                
                return True
            else:
                print("ℹ️  MCP_DOCKER configuration appears to be different than expected")
                return False
        else:
            print("ℹ️  No MCP_DOCKER server found in configuration")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing MCP config: {e}")
        return False

def validate_docker_availability():
    """Check if Docker is actually available."""
    try:
        import subprocess
        result = subprocess.run(["docker", "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Docker is available: {result.stdout.strip()}")
            
            # Check if Docker daemon is running
            result = subprocess.run(["docker", "info"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Docker daemon is running")
                return True
            else:
                print("❌ Docker daemon is not running")
                print("💡 Start Docker Desktop to enable Docker functionality")
                return False
        else:
            print("❌ Docker command not available")
            return False
    except Exception as e:
        print(f"❌ Error checking Docker: {e}")
        return False

def suggest_alternative_docker_integration():
    """Suggest alternative ways to integrate Docker functionality."""
    print("\n💡 Alternative Docker Integration Options:")
    print("1. Use direct Docker commands via bash execution")
    print("2. Create a custom Docker MCP server")
    print("3. Use existing filesystem MCP server to manage Docker configs")
    print("4. Integrate Docker functionality into existing Python scripts")
    
    print("\n📝 Example direct Docker usage:")
    print("   docker ps")
    print("   docker logs <container_name>")
    print("   docker exec -it <container> /bin/bash")

if __name__ == "__main__":
    print("🔧 MCP_DOCKER Configuration Fix")
    print("=" * 50)
    
    # Check Docker availability first
    docker_available = validate_docker_availability()
    
    # Fix the MCP configuration
    config_fixed = fix_mcp_docker_config()
    
    if config_fixed:
        print("\n🎉 Configuration fixed successfully!")
        print("🔄 Restart Kiro to apply the changes")
    
    if not docker_available:
        print("\n⚠️  Docker issues detected")
        suggest_alternative_docker_integration()
    
    print("\n📊 Summary:")
    print(f"   Docker Available: {'✅' if docker_available else '❌'}")
    print(f"   Config Fixed: {'✅' if config_fixed else '❌'}")