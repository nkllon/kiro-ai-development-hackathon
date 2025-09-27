#!/usr/bin/env python3
"""
Cloudflare WebSocket Support Enabler
Fibonacci Iteration 1 - Single Agent Deployment

This script enables WebSocket support in Cloudflare Dashboard for observatory.nkllon.com
and validates the configuration.
"""

import json
import subprocess
import time
import sys
import requests
from datetime import datetime, timezone
from typing import Dict, List, Any
from pathlib import Path

def log_action(task: str, action: str, status: str, details: Dict[str, Any] = None):
    """Log action in JSON format to stdout"""
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task": task,
        "action": action,
        "status": status,
        "details": details or {}
    }
    print(json.dumps(log_entry))

def test_current_websocket_status() -> Dict[str, Any]:
    """Test current WebSocket status before enabling"""
    log_action("websocket-enable", "Testing current WebSocket status", "in_progress")
    
    endpoint = "/ws/emoji-rain"
    url = f"https://observatory.nkllon.com{endpoint}"
    
    # Test with proper WebSocket headers
    headers = [
        "-H", "Connection: Upgrade",
        "-H", "Upgrade: websocket", 
        "-H", "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==",
        "-H", "Sec-WebSocket-Version: 13",
        "-H", "Origin: https://observatory.nkllon.com"
    ]
    
    cmd = ["curl", "-i", "-N", "--max-time", "10"] + headers + [url]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        response_lines = result.stdout.split('\n')
        status_line = response_lines[0] if response_lines else ""
        
        # Check for current status
        has_404 = "404" in status_line
        has_101 = "101 Switching Protocols" in status_line
        has_http2 = "HTTP/2" in status_line
        
        current_status = {
            "endpoint": endpoint,
            "url": url,
            "status_line": status_line.strip(),
            "has_404_error": has_404,
            "has_101_switching": has_101,
            "has_http2": has_http2,
            "websocket_supported": has_101,
            "response_preview": "\n".join(response_lines[:5])
        }
        
        log_action("websocket-enable", "Current WebSocket status tested", "completed", current_status)
        return current_status
        
    except Exception as e:
        error_status = {
            "endpoint": endpoint,
            "url": url,
            "error": str(e),
            "websocket_supported": False
        }
        log_action("websocket-enable", "WebSocket status test failed", "error", error_status)
        return error_status

def generate_cloudflare_dashboard_instructions() -> Dict[str, Any]:
    """Generate step-by-step instructions for enabling WebSocket support"""
    
    instructions = {
        "title": "Enable WebSocket Support in Cloudflare Dashboard",
        "target": "observatory.nkllon.com",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "steps": [
            {
                "step": 1,
                "title": "Access Cloudflare Dashboard",
                "description": "Navigate to the Cloudflare dashboard",
                "url": "https://dash.cloudflare.com",
                "action": "Login to your Cloudflare account",
                "verification": "Ensure you can see your domains"
            },
            {
                "step": 2,
                "title": "Select Observatory Domain",
                "description": "Navigate to observatory.nkllon.com domain settings",
                "action": "Click on 'observatory.nkllon.com' from your domain list",
                "verification": "Domain overview page loads"
            },
            {
                "step": 3,
                "title": "Navigate to Network Settings",
                "description": "Go to Network → WebSockets section",
                "action": "Click on 'Network' tab, then 'WebSockets'",
                "verification": "WebSockets settings page loads"
            },
            {
                "step": 4,
                "title": "Enable WebSocket Support",
                "description": "Toggle WebSocket support to ON",
                "action": "Toggle the WebSockets switch to 'ON'",
                "verification": "Switch shows 'ON' state",
                "expected_result": "WebSocket connections will work through tunnel"
            },
            {
                "step": 5,
                "title": "Save Configuration",
                "description": "Save the WebSocket configuration",
                "action": "Click 'Save' or wait for auto-save",
                "verification": "Configuration is saved successfully"
            },
            {
                "step": 6,
                "title": "Verify Setting",
                "description": "Confirm WebSocket support is enabled",
                "action": "Refresh page and verify switch is still ON",
                "verification": "WebSocket support remains enabled"
            }
        ],
        "troubleshooting": {
            "websocket_not_found": {
                "symptom": "Cannot find WebSockets section in Network tab",
                "solution": "Ensure you're on the correct domain and have proper permissions",
                "alternative": "Check if WebSockets are already enabled or disabled by default"
            },
            "toggle_not_working": {
                "symptom": "WebSocket toggle switch doesn't respond",
                "solution": "Refresh the page and try again, check browser console for errors",
                "alternative": "Try using a different browser or incognito mode"
            },
            "setting_not_saving": {
                "symptom": "WebSocket setting reverts after saving",
                "solution": "Check if there are conflicting rules or policies",
                "alternative": "Contact Cloudflare support if issue persists"
            }
        },
        "expected_results": {
            "before_enabling": "HTTP/2 404 errors on WebSocket endpoints",
            "after_enabling": "HTTP/1.1 101 Switching Protocols for WebSocket connections",
            "test_endpoint": "wss://observatory.nkllon.com/ws/emoji-rain"
        }
    }
    
    return instructions

def test_websocket_after_enabling() -> Dict[str, Any]:
    """Test WebSocket connection after enabling support"""
    log_action("websocket-enable", "Testing WebSocket after enabling", "in_progress")
    
    endpoints = [
        "/ws/emoji-rain",
        "/ws/observatory", 
        "/ws/anomalies",
        "/ws/doctor-status"
    ]
    
    results = []
    success_count = 0
    
    for endpoint in endpoints:
        url = f"https://observatory.nkllon.com{endpoint}"
        
        # WebSocket handshake headers
        headers = [
            "-H", "Connection: Upgrade",
            "-H", "Upgrade: websocket", 
            "-H", "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==",
            "-H", "Sec-WebSocket-Version: 13",
            "-H", "Origin: https://observatory.nkllon.com"
        ]
        
        cmd = ["curl", "-i", "-N", "--max-time", "10"] + headers + [url]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            response_lines = result.stdout.split('\n')
            status_line = response_lines[0] if response_lines else ""
            
            # Check for HTTP/1.1 101 Switching Protocols
            handshake_successful = "101 Switching Protocols" in status_line
            connection_established = "101" in status_line
            
            test_result = {
                "endpoint": endpoint,
                "url": url,
                "status_code": status_line.strip(),
                "handshake_successful": handshake_successful,
                "connection_established": connection_established,
                "success": handshake_successful,
                "response_preview": "\n".join(response_lines[:5])
            }
            
            if handshake_successful:
                success_count += 1
            
            results.append(test_result)
            
        except Exception as e:
            test_result = {
                "endpoint": endpoint,
                "url": url,
                "error": str(e),
                "success": False
            }
            results.append(test_result)
    
    test_summary = {
        "total_endpoints": len(endpoints),
        "successful_endpoints": success_count,
        "success_rate": success_count / len(endpoints),
        "all_endpoints_working": success_count == len(endpoints),
        "results": results
    }
    
    log_action("websocket-enable", "WebSocket testing completed", "completed", test_summary)
    return test_summary

def main():
    """Main function - Execute WebSocket enablement mission"""
    log_action("websocket-enable", "WebSocket enablement mission started", "in_progress", {
        "target": "observatory.nkllon.com",
        "objective": "Enable WebSocket support in Cloudflare Dashboard",
        "expected_result": "HTTP/1.1 101 Switching Protocols for WebSocket connections"
    })
    
    # Step 1: Test current status
    log_action("websocket-enable", "Step 1: Testing current WebSocket status", "in_progress")
    current_status = test_current_websocket_status()
    
    # Step 2: Generate instructions
    log_action("websocket-enable", "Step 2: Generating Cloudflare Dashboard instructions", "in_progress")
    instructions = generate_cloudflare_dashboard_instructions()
    
    # Save instructions to file
    instructions_file = Path("logs/cloudflare_websocket_instructions.json")
    instructions_file.parent.mkdir(exist_ok=True)
    with open(instructions_file, "w") as f:
        json.dump(instructions, f, indent=2)
    
    log_action("websocket-enable", "Cloudflare Dashboard instructions generated", "completed", {
        "instructions_file": str(instructions_file),
        "total_steps": len(instructions["steps"])
    })
    
    # Step 3: Display instructions
    print("\n" + "="*80)
    print("🔧 CLOUDFLARE WEBSOCKET ENABLEMENT INSTRUCTIONS")
    print("="*80)
    print(f"🎯 Target: {instructions['target']}")
    print(f"📅 Generated: {instructions['timestamp']}")
    
    print("\n📋 Step-by-Step Instructions:")
    for step in instructions["steps"]:
        print(f"\n{step['step']}. {step['title']}")
        print(f"   📝 {step['description']}")
        print(f"   🎯 Action: {step['action']}")
        print(f"   ✅ Verification: {step['verification']}")
        if 'expected_result' in step:
            print(f"   🎉 Expected: {step['expected_result']}")
    
    print("\n🔍 Current Status:")
    print(f"   WebSocket Supported: {'✅ Yes' if current_status.get('websocket_supported') else '❌ No'}")
    print(f"   Current Status: {current_status.get('status_line', 'Unknown')}")
    if current_status.get('has_404_error'):
        print("   ⚠️  Currently getting 404 errors - WebSocket support needs to be enabled")
    
    print("\n🎯 Expected Results After Enabling:")
    print(f"   Before: {instructions['expected_results']['before_enabling']}")
    print(f"   After:  {instructions['expected_results']['after_enabling']}")
    print(f"   Test:   {instructions['expected_results']['test_endpoint']}")
    
    print("\n🚀 Next Steps:")
    print("   1. Follow the step-by-step instructions above")
    print("   2. Enable WebSocket support in Cloudflare Dashboard")
    print("   3. Run the test script to verify the changes")
    print("   4. Monitor WebSocket connections")
    
    print("\n💡 Troubleshooting:")
    for issue, details in instructions["troubleshooting"].items():
        print(f"   • {details['symptom']}: {details['solution']}")
    
    print("\n" + "="*80)
    
    # Step 4: Wait for user to complete dashboard changes
    print("\n⏳ Waiting for you to complete the Cloudflare Dashboard changes...")
    print("   Press Enter when you've enabled WebSocket support in the dashboard...")
    input()
    
    # Step 5: Test after enabling
    log_action("websocket-enable", "Step 3: Testing WebSocket after enabling", "in_progress")
    print("\n🧪 Testing WebSocket endpoints after enabling...")
    
    # Wait a moment for changes to propagate
    print("⏳ Waiting 30 seconds for changes to propagate...")
    time.sleep(30)
    
    test_results = test_websocket_after_enabling()
    
    # Step 6: Generate final report
    final_report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mission": "WebSocket Enablement",
        "target": "observatory.nkllon.com",
        "current_status": current_status,
        "test_results": test_results,
        "instructions": instructions,
        "success": test_results["all_endpoints_working"]
    }
    
    # Save final report
    report_file = Path("logs/websocket_enablement_report.json")
    with open(report_file, "w") as f:
        json.dump(final_report, f, indent=2)
    
    # Display final results
    print("\n" + "="*80)
    print("🎉 WEBSOCKET ENABLEMENT MISSION RESULTS")
    print("="*80)
    print(f"📊 Mission Status: {'✅ SUCCESS' if final_report['success'] else '❌ FAILED'}")
    print(f"🌐 Success Rate: {test_results['success_rate']:.1%}")
    print(f"🔗 Endpoints Working: {test_results['successful_endpoints']}/{test_results['total_endpoints']}")
    
    print("\n📋 Endpoint Results:")
    for result in test_results["results"]:
        emoji = "✅" if result["success"] else "❌"
        print(f"  {emoji} {result['endpoint']}: {result.get('status_code', 'ERROR')}")
        if result.get('error'):
            print(f"    Error: {result['error']}")
    
    if final_report['success']:
        print("\n🎯 SUCCESS CRITERIA MET:")
        print("   ✅ WebSocket support enabled in Cloudflare Dashboard")
        print("   ✅ HTTP/1.1 101 Switching Protocols working")
        print("   ✅ No more HTTP/2 404 errors on WebSocket endpoints")
        print("   ✅ All WebSocket endpoints accessible through tunnel")
    else:
        print("\n⚠️  ISSUES DETECTED:")
        print("   • Some WebSocket endpoints still not working")
        print("   • Check Cloudflare Dashboard settings")
        print("   • Verify tunnel configuration")
        print("   • Check Observatory server WebSocket handlers")
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    print("="*80)
    
    return 0 if final_report['success'] else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Mission interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Mission failed with error: {e}")
        sys.exit(1)