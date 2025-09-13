#!/usr/bin/env python3
"""
Test MCP server startup and functionality without blocking
"""
import subprocess
import json
import sys
import os
import signal
import time
from pathlib import Path

def test_mcp_server_startup():
    """Test MCP server can start without blocking"""
    print("🔍 Testing MCP Server Startup...")
    
    mcp_server_path = Path("kiro_simone_adapter/mcp-server/dist/index.js")
    if not mcp_server_path.exists():
        print("❌ MCP server binary not found")
        return False
    
    print("✅ MCP server binary exists")
    
    # Test if server can start (with timeout)
    env = os.environ.copy()
    env["PROJECT_PATH"] = "/Users/lou/kiro-2/kiro-ai-development-hackathon"
    
    try:
        # Start server with timeout
        process = subprocess.Popen(
            ["node", str(mcp_server_path)],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait briefly to see if it starts without immediate error
        time.sleep(2)
        
        if process.poll() is None:
            print("✅ MCP server started successfully")
            # Terminate it
            process.terminate()
            process.wait(timeout=5)
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ MCP server failed to start: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        return False

def test_mcp_config():
    """Test MCP configuration validity"""
    print("\n🔍 Testing MCP Configuration...")
    
    config_path = Path.home() / ".cursor" / "mcp.json"
    if not config_path.exists():
        print("❌ MCP config file not found")
        return False
    
    try:
        with open(config_path) as f:
            config = json.load(f)
        
        if "mcpServers" not in config:
            print("❌ No mcpServers in config")
            return False
        
        if "simone" not in config["mcpServers"]:
            print("❌ Simone server not configured")
            return False
        
        simone_config = config["mcpServers"]["simone"]
        
        # Check required fields
        if "command" not in simone_config:
            print("❌ Missing command in Simone config")
            return False
        
        if "args" not in simone_config:
            print("❌ Missing args in Simone config")
            return False
        
        if "env" not in simone_config:
            print("❌ Missing env in Simone config")
            return False
        
        # Check PROJECT_PATH is set
        if "PROJECT_PATH" not in simone_config["env"]:
            print("❌ PROJECT_PATH not set in environment")
            return False
        
        print("✅ MCP configuration is valid")
        return True
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON in MCP config")
        return False
    except Exception as e:
        print(f"❌ Error reading MCP config: {e}")
        return False

def test_simone_prompts():
    """Test Simone prompts are accessible"""
    print("\n🔍 Testing Simone Prompts...")
    
    prompts_dir = Path(".simone/prompts")
    if not prompts_dir.exists():
        print("❌ Simone prompts directory not found")
        return False
    
    prompt_files = list(prompts_dir.glob("*.yaml"))
    if not prompt_files:
        print("❌ No prompt files found")
        return False
    
    print(f"✅ Found {len(prompt_files)} prompt files")
    
    # Check for key prompts
    key_prompts = ["init_simone.yaml", "create_issue.yaml", "work_issue.yaml"]
    missing_prompts = []
    
    for prompt in key_prompts:
        if not (prompts_dir / prompt).exists():
            missing_prompts.append(prompt)
    
    if missing_prompts:
        print(f"⚠️  Missing key prompts: {missing_prompts}")
    else:
        print("✅ All key prompts present")
    
    return len(missing_prompts) == 0

def test_project_yaml():
    """Test Simone project configuration"""
    print("\n🔍 Testing Simone Project Configuration...")
    
    project_yaml = Path(".simone/project.yaml")
    if not project_yaml.exists():
        print("❌ Project YAML not found")
        return False
    
    try:
        import yaml
        with open(project_yaml) as f:
            config = yaml.safe_load(f)
        
        required_sections = ["project", "contexts", "github"]
        missing_sections = []
        
        for section in required_sections:
            if section not in config:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"❌ Missing required sections: {missing_sections}")
            return False
        
        print("✅ Project configuration is valid")
        return True
        
    except ImportError:
        print("⚠️  PyYAML not available, skipping YAML validation")
        return True
    except Exception as e:
        print(f"❌ Error reading project config: {e}")
        return False

def main():
    """Run all MCP server tests"""
    print("🚀 MCP SERVER INTEGRATION TESTS")
    print("=" * 40)
    
    tests = [
        ("MCP Configuration", test_mcp_config),
        ("Simone Prompts", test_simone_prompts),
        ("Project Configuration", test_project_yaml),
        ("MCP Server Startup", test_mcp_server_startup)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 40)
    print("📊 MCP SERVER TEST RESULTS")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 MCP SERVER READY!")
        return 0
    else:
        print(f"⚠️  {total - passed} issues need fixing")
        return 1

if __name__ == "__main__":
    sys.exit(main())





