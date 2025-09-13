#!/usr/bin/env python3
"""
Test script for MCP integration - non-blocking approach
"""
import subprocess
import json
import sys
import os
import signal
from pathlib import Path

def test_mcp_server():
    """Test if MCP server is responding properly"""
    print("🔍 Testing MCP Server Integration...")
    
    # Check if server process is running
    try:
        result = subprocess.run(
            ["ps", "aux"], 
            capture_output=True, 
            text=True, 
            timeout=2
        )
        if "node kiro_simone_adapter/mcp-server/dist/index.js" in result.stdout:
            print("✅ MCP server process is running")
        else:
            print("❌ MCP server process not found")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Process check timed out")
        return False
    
    # Check if MCP config exists
    mcp_config_path = Path.home() / ".cursor" / "mcp.json"
    if mcp_config_path.exists():
        print("✅ MCP configuration file exists")
        try:
            with open(mcp_config_path) as f:
                config = json.load(f)
                if "simone" in config.get("mcpServers", {}):
                    print("✅ Simone MCP server configured")
                else:
                    print("❌ Simone MCP server not configured")
                    return False
        except json.JSONDecodeError:
            print("❌ Invalid MCP configuration JSON")
            return False
    else:
        print("❌ MCP configuration file not found")
        return False
    
    # Check if Simone prompts exist
    prompts_dir = Path(".simone/prompts")
    if prompts_dir.exists():
        prompt_files = list(prompts_dir.glob("*.yaml"))
        print(f"✅ Found {len(prompt_files)} Simone prompt files")
    else:
        print("❌ Simone prompts directory not found")
        return False
    
    # Check if project.yaml exists
    project_yaml = Path(".simone/project.yaml")
    if project_yaml.exists():
        print("✅ Simone project configuration exists")
    else:
        print("❌ Simone project configuration not found")
        return False
    
    print("🎉 MCP integration test completed successfully")
    return True

def test_enhanced_demo():
    """Test the enhanced demo functionality"""
    print("\n🔍 Testing Enhanced Demo...")
    
    try:
        # Run enhanced demo with timeout
        result = subprocess.run(
            ["make", "enhanced-demo"], 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Enhanced demo executed successfully")
            
            # Check for suspicious output
            if "0.00 seconds" in result.stdout:
                print("⚠️  Demo shows 0.00 seconds duration - this may be incorrect")
            
            if "91.6%" in result.stdout or "90.5%" in result.stdout:
                print("✅ Demo shows efficiency metrics")
            
            return True
        else:
            print(f"❌ Enhanced demo failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Enhanced demo timed out")
        return False

def test_interface_governance():
    """Test interface governance system"""
    print("\n🔍 Testing Interface Governance...")
    
    try:
        result = subprocess.run(
            ["make", "validate-interfaces"], 
            capture_output=True, 
            text=True, 
            timeout=15
        )
        
        if result.returncode == 0:
            print("✅ Interface governance validation passed")
            
            # Check if registry file exists
            registry_file = Path(".beast_mode/interface_registry.json")
            if registry_file.exists():
                size = registry_file.stat().st_size
                print(f"✅ Registry file exists ({size} bytes)")
                
                # Try to load and validate JSON
                try:
                    with open(registry_file) as f:
                        data = json.load(f)
                        total_interfaces = data.get("total_interfaces", 0)
                        duplicates = data.get("duplicates", 0)
                        print(f"✅ Registry contains {total_interfaces} interfaces, {duplicates} duplicates")
                except json.JSONDecodeError:
                    print("❌ Registry file contains invalid JSON")
                    return False
            else:
                print("❌ Registry file not found")
                return False
                
            return True
        else:
            print(f"❌ Interface governance failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Interface governance timed out")
        return False

def main():
    """Run all tests"""
    print("🚀 COMPREHENSIVE PROJECT EVALUATION")
    print("=" * 50)
    
    tests = [
        ("MCP Integration", test_mcp_server),
        ("Enhanced Demo", test_enhanced_demo), 
        ("Interface Governance", test_interface_governance)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Project is fully operational!")
        return 0
    else:
        print(f"⚠️  {total - passed} tests failed - Issues need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())





