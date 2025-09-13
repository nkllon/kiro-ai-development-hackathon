#!/usr/bin/env python3
"""
Test MCP server stdio communication without blocking
"""
import subprocess
import json
import sys
import os
import time
from pathlib import Path

def test_mcp_stdio_communication():
    """Test MCP server stdio communication"""
    print("🔍 Testing MCP Server Stdio Communication...")
    
    mcp_server_path = Path("kiro_simone_adapter/mcp-server/dist/index.js")
    if not mcp_server_path.exists():
        print("❌ MCP server binary not found")
        return False
    
    env = os.environ.copy()
    env["PROJECT_PATH"] = "/Users/lou/kiro-2/kiro-ai-development-hackathon"
    
    try:
        # Start server process
        process = subprocess.Popen(
            ["node", str(mcp_server_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True
        )
        
        # Send MCP initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("📤 Sending initialization request...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Read response with timeout
        try:
            response_line = process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                print(f"📥 Received response: {response.get('result', {}).get('capabilities', {})}")
                
                # Send tools list request
                tools_request = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list",
                    "params": {}
                }
                
                print("📤 Requesting tools list...")
                process.stdin.write(json.dumps(tools_request) + "\n")
                process.stdin.flush()
                
                # Read tools response
                tools_response_line = process.stdout.readline()
                if tools_response_line:
                    tools_response = json.loads(tools_response_line.strip())
                    tools = tools_response.get('result', {}).get('tools', [])
                    print(f"📥 Found {len(tools)} tools: {[t.get('name') for t in tools]}")
                    
                    # Check for expected tools
                    expected_tools = ['log_activity']
                    found_tools = [t.get('name') for t in tools]
                    
                    if any(tool in found_tools for tool in expected_tools):
                        print("✅ Expected tools found")
                        success = True
                    else:
                        print(f"❌ Expected tools not found. Found: {found_tools}")
                        success = False
                else:
                    print("❌ No response to tools request")
                    success = False
            else:
                print("❌ No response to initialization request")
                success = False
                
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response: {e}")
            success = False
        except Exception as e:
            print(f"❌ Error reading response: {e}")
            success = False
        
        # Cleanup
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        
        return success
        
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        return False

def main():
    """Test MCP server stdio communication"""
    print("🚀 MCP SERVER STDIO COMMUNICATION TEST")
    print("=" * 45)
    
    success = test_mcp_stdio_communication()
    
    print("\n" + "=" * 45)
    if success:
        print("✅ MCP SERVER STDIO COMMUNICATION WORKING!")
        print("💡 The server should work through Claude Desktop MCP integration")
        return 0
    else:
        print("❌ MCP SERVER STDIO COMMUNICATION FAILED")
        print("💡 Need to debug the server startup or configuration")
        return 1

if __name__ == "__main__":
    sys.exit(main())





