#!/usr/bin/env python3
"""Test MCP connection to Google Calendar server."""

import json
import subprocess
import sys
from typing import Dict, Any


def send_mcp_request(method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """Send an MCP request to the Google Calendar server.
    
    Args:
        method: MCP method name
        params: Method parameters
        
    Returns:
        MCP response
    """
    if params is None:
        params = {}
    
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }
    
    try:
        # Connect to the MCP server running in Docker
        # The @cocal/google-calendar-mcp server uses stdio for MCP communication
        cmd = ["docker", "exec", "-i", "google_calendar_mcp", "google-calendar-mcp"]
        
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send the request
        request_json = json.dumps(request) + "\n"
        stdout, stderr = process.communicate(input=request_json, timeout=30)
        
        if stderr:
            print(f"MCP Server stderr: {stderr}", file=sys.stderr)
        
        if process.returncode != 0:
            return {"error": f"Process failed with code {process.returncode}"}
        
        # Parse response
        if stdout.strip():
            return json.loads(stdout.strip())
        else:
            return {"error": "No response from server"}
            
    except subprocess.TimeoutExpired:
        process.kill()
        return {"error": "Request timed out"}
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON response: {e}"}
    except Exception as e:
        return {"error": f"Connection failed: {e}"}


def test_mcp_capabilities():
    """Test MCP server capabilities."""
    print("🔍 Testing MCP server capabilities...")
    
    # Test initialize
    response = send_mcp_request("initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {
            "name": "beast-mode-test-client",
            "version": "1.0.0"
        }
    })
    
    print(f"Initialize response: {json.dumps(response, indent=2)}")
    
    if "error" in response:
        print("❌ Failed to initialize MCP connection")
        return False
    
    # Test list tools
    response = send_mcp_request("tools/list")
    print(f"Tools list response: {json.dumps(response, indent=2)}")
    
    return True


def test_calendar_operations():
    """Test calendar operations."""
    print("\n📅 Testing calendar operations...")
    
    # Test list calendars
    response = send_mcp_request("tools/call", {
        "name": "list_calendars",
        "arguments": {}
    })
    
    print(f"List calendars response: {json.dumps(response, indent=2)}")
    
    # Test get events
    response = send_mcp_request("tools/call", {
        "name": "get_events",
        "arguments": {
            "calendar_id": "primary",
            "max_results": 5
        }
    })
    
    print(f"Get events response: {json.dumps(response, indent=2)}")


def main():
    """Main test function."""
    print("🚀 Testing Google Calendar MCP Server Connection")
    print("=" * 50)
    
    # Test basic MCP capabilities
    if not test_mcp_capabilities():
        sys.exit(1)
    
    # Test calendar operations
    test_calendar_operations()
    
    print("\n✅ MCP connection test completed")


if __name__ == "__main__":
    main()