#!/usr/bin/env python3
"""
Direct test of Google Calendar MCP functionality
"""
import subprocess
import json
import os
import time

def test_mcp_server():
    """Test the MCP server directly"""
    print("🚀 Testing Google Calendar MCP Server Directly")
    print("=" * 50)
    
    # Set up environment
    env = os.environ.copy()
    env['GOOGLE_OAUTH_CREDENTIALS'] = '/Users/lou/.config/google-calendar-mcp/gcp-oauth.keys.json'
    
    print("🔍 Testing authentication...")
    try:
        result = subprocess.run([
            'npx', '@cocal/google-calendar-mcp', 'auth'
        ], env=env, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Authentication successful")
            print(f"   Output: {result.stdout.strip()}")
        else:
            print("❌ Authentication failed")
            print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False
    
    print("\n🔍 Testing MCP server startup...")
    try:
        # Start server in background and test if it responds
        server_process = subprocess.Popen([
            'npx', '@cocal/google-calendar-mcp', 'start'
        ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Give it a moment to start
        time.sleep(2)
        
        # Check if process is still running
        if server_process.poll() is None:
            print("✅ MCP server started successfully")
            server_process.terminate()
            server_process.wait()
            return True
        else:
            stdout, stderr = server_process.communicate()
            print("❌ MCP server failed to start")
            print(f"   Stdout: {stdout[:200]}")
            print(f"   Stderr: {stderr[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_mcp_server()
    if success:
        print("\n🎉 MCP server is working correctly!")
        print("📝 If calendar listing isn't working in Claude Desktop,")
        print("   the issue is likely with MCP configuration or connection.")
    else:
        print("\n💥 MCP server has issues that need to be fixed.")