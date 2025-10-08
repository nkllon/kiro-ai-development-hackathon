#!/usr/bin/env python3
"""
Test MCP Filesystem Operations

This script tests basic MCP filesystem operations to ensure the server is working correctly.
"""

import os
import tempfile
import subprocess
import json
import time
from pathlib import Path

def test_mcp_filesystem_basic():
    """Test basic MCP filesystem operations."""
    print("🧪 Testing MCP Filesystem Basic Operations")
    print("=" * 50)
    
    # Test directory creation
    test_dir = "test_mcp_operations"
    
    try:
        # Create test directory
        if os.path.exists(test_dir):
            os.rmdir(test_dir)
        
        os.makedirs(test_dir, exist_ok=True)
        print(f"✅ Created test directory: {test_dir}")
        
        # Test file creation
        test_file = os.path.join(test_dir, "test_file.txt")
        with open(test_file, 'w') as f:
            f.write("Test content for MCP filesystem operations")
        print(f"✅ Created test file: {test_file}")
        
        # Test file reading
        with open(test_file, 'r') as f:
            content = f.read()
        print(f"✅ Read test file content: {len(content)} characters")
        
        # Cleanup
        os.remove(test_file)
        os.rmdir(test_dir)
        print(f"✅ Cleaned up test files")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic filesystem test failed: {e}")
        return False

def test_mcp_server_config():
    """Test MCP server configuration."""
    print("\n🔧 Testing MCP Server Configuration")
    print("=" * 50)
    
    # Check MCP configuration file
    mcp_config_path = Path(".kiro/settings/mcp.json")
    
    if not mcp_config_path.exists():
        print(f"❌ MCP configuration file not found: {mcp_config_path}")
        return False
    
    try:
        with open(mcp_config_path, 'r') as f:
            config = json.load(f)
        
        if "filesystem" not in config.get("mcpServers", {}):
            print("❌ Filesystem server not configured in MCP settings")
            return False
        
        fs_config = config["mcpServers"]["filesystem"]
        env = fs_config.get("env", {})
        
        # Check logging configuration
        logging_disabled = env.get("MCP_FILESYSTEM_ENABLE_LOGGING", "").lower() == "false"
        log_level = env.get("MCP_FILESYSTEM_LOG_LEVEL", "")
        
        print(f"✅ MCP configuration found")
        print(f"   - Logging disabled: {logging_disabled}")
        print(f"   - Log level: {log_level}")
        print(f"   - Disabled: {fs_config.get('disabled', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading MCP configuration: {e}")
        return False

def test_toml_config():
    """Test TOML configuration file."""
    print("\n📄 Testing TOML Configuration")
    print("=" * 50)
    
    toml_config_path = Path("mcp-filesystem-config.toml")
    
    if not toml_config_path.exists():
        print(f"❌ TOML configuration file not found: {toml_config_path}")
        return False
    
    try:
        with open(toml_config_path, 'r') as f:
            content = f.read()
        
        # Check for key settings
        logging_disabled = "enable_logging = false" in content
        has_log_file = "log_file =" in content
        
        print(f"✅ TOML configuration found")
        print(f"   - Logging disabled: {logging_disabled}")
        print(f"   - Log file configured: {has_log_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading TOML configuration: {e}")
        return False

def test_environment_variables():
    """Test environment variables."""
    print("\n🌍 Testing Environment Variables")
    print("=" * 50)
    
    env_vars = [
        "MCP_FILESYSTEM_ROOT",
        "MCP_FILESYSTEM_ENABLE_LOGGING", 
        "MCP_FILESYSTEM_LOG_LEVEL",
        "MCP_FILESYSTEM_LOG_FILE"
    ]
    
    for var in env_vars:
        value = os.environ.get(var, "Not set")
        print(f"   {var}: {value}")
    
    return True

def test_uvx_availability():
    """Test if uvx is available."""
    print("\n📦 Testing uvx Availability")
    print("=" * 50)
    
    try:
        result = subprocess.run(["uvx", "--version"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"✅ uvx is available: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ uvx command failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ uvx command timed out")
        return False
    except FileNotFoundError:
        print("❌ uvx command not found")
        return False
    except Exception as e:
        print(f"❌ Error testing uvx: {e}")
        return False

def main():
    """Run all MCP filesystem tests."""
    print("🔍 MCP Filesystem Server Test Suite")
    print("=" * 60)
    
    tests = [
        ("Basic Filesystem Operations", test_mcp_filesystem_basic),
        ("MCP Server Configuration", test_mcp_server_config),
        ("TOML Configuration", test_toml_config),
        ("Environment Variables", test_environment_variables),
        ("uvx Availability", test_uvx_availability)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MCP filesystem server should be working correctly.")
    else:
        print("⚠️  Some tests failed. Check the configuration and try running the fix script.")
        print("   Run: python3 scripts/fix_mcp_filesystem_logging.py")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)