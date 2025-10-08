#!/usr/bin/env python3
"""
Test Phase 2 WebSocket Configuration
Quick test script to verify WebSocket endpoints and SSL/TLS configuration
"""

import json
import subprocess
import time
import sys
from datetime import datetime, timezone
from typing import Dict, List, Any
from pathlib import Path

def log_action(action: str, status: str, details: Dict[str, Any] = None):
    """Log action in JSON format"""
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task": "phase2-websocket-test",
        "action": action,
        "status": status,
        "details": details or {}
    }
    print(json.dumps(log_entry))

def test_websocket_endpoint(endpoint: str, domain: str = "observatory.nkllon.com") -> Dict[str, Any]:
    """Test a single WebSocket endpoint"""
    url = f"https://{domain}{endpoint}"
    
    # WebSocket handshake headers
    headers = [
        "-H", "Connection: Upgrade",
        "-H", "Upgrade: websocket",
        "-H", "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==",
        "-H", "Sec-WebSocket-Version: 13",
        "-H", f"Origin: https://{domain}"
    ]
    
    cmd = ["curl", "-i", "-N", "--max-time", "10"] + headers + [url]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        response_lines = result.stdout.split('\n')
        status_line = response_lines[0] if response_lines else ""
        
        # Check for success indicators
        has_101 = "101 Switching Protocols" in status_line
        has_http1 = "HTTP/1.1" in status_line
        has_http2 = "HTTP/2" in status_line
        has_404 = "404" in status_line
        
        return {
            "endpoint": endpoint,
            "url": url,
            "status_line": status_line.strip(),
            "success": has_101,
            "is_http1": has_http1,
            "is_http2": has_http2,
            "has_404": has_404,
            "response_preview": "\n".join(response_lines[:5])
        }
        
    except Exception as e:
        return {
            "endpoint": endpoint,
            "url": url,
            "error": str(e),
            "success": False
        }

def test_ssl_configuration(domain: str = "observatory.nkllon.com") -> Dict[str, Any]:
    """Test SSL/TLS configuration"""
    try:
        # Test HTTPS connection
        cmd = ["curl", "-I", f"https://{domain}"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        response_lines = result.stdout.split('\n')
        status_line = response_lines[0] if response_lines else ""
        
        # Check for SSL headers
        headers = {}
        for line in response_lines:
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip().lower()] = value.strip()
        
        return {
            "domain": domain,
            "status_line": status_line.strip(),
            "hsts_header": headers.get('strict-transport-security'),
            "hsts_enabled": bool(headers.get('strict-transport-security')),
            "response_preview": "\n".join(response_lines[:5])
        }
        
    except Exception as e:
        return {
            "domain": domain,
            "error": str(e),
            "hsts_enabled": False
        }

def main():
    """Main test function"""
    print("🧪 Phase 2 WebSocket Configuration Test")
    print("=" * 50)
    
    domain = "observatory.nkllon.com"
    endpoints = [
        "/ws/emoji-rain",
        "/ws/observatory",
        "/ws/anomalies",
        "/ws/doctor-status"
    ]
    
    log_action("test_start", "Starting Phase 2 WebSocket configuration test", "in_progress", {
        "domain": domain,
        "endpoints": endpoints
    })
    
    # Test WebSocket endpoints
    websocket_results = []
    success_count = 0
    
    print(f"\n🔌 Testing WebSocket Endpoints:")
    for endpoint in endpoints:
        result = test_websocket_endpoint(endpoint, domain)
        websocket_results.append(result)
        
        if result["success"]:
            success_count += 1
            print(f"  ✅ {endpoint}: {result['status_line']}")
        else:
            print(f"  ❌ {endpoint}: {result.get('status_line', 'ERROR')}")
            if result.get('error'):
                print(f"      Error: {result['error']}")
        
        log_action("websocket_test", f"Tested {endpoint}", "completed", result)
    
    # Test SSL configuration
    print(f"\n🔒 Testing SSL/TLS Configuration:")
    ssl_result = test_ssl_configuration(domain)
    
    if ssl_result.get('hsts_enabled'):
        print(f"  ✅ HSTS Enabled: {ssl_result['hsts_header']}")
    else:
        print(f"  ❌ HSTS Not Enabled")
    
    print(f"  📋 Status: {ssl_result.get('status_line', 'Unknown')}")
    
    log_action("ssl_test", "SSL/TLS configuration tested", "completed", ssl_result)
    
    # Generate summary
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "domain": domain,
        "websocket_results": websocket_results,
        "ssl_result": ssl_result,
        "total_endpoints": len(endpoints),
        "successful_endpoints": success_count,
        "success_rate": success_count / len(endpoints),
        "websocket_support_enabled": success_count > 0,
        "hsts_enabled": ssl_result.get('hsts_enabled', False)
    }
    
    print(f"\n📊 Test Summary:")
    print(f"  WebSocket Support: {'✅ Enabled' if summary['websocket_support_enabled'] else '❌ Disabled'}")
    print(f"  Success Rate: {summary['success_rate']:.1%}")
    print(f"  Endpoints Working: {summary['successful_endpoints']}/{summary['total_endpoints']}")
    print(f"  HSTS Enabled: {'✅ Yes' if summary['hsts_enabled'] else '❌ No'}")
    
    # Determine overall status
    if summary['websocket_support_enabled'] and summary['hsts_enabled']:
        overall_status = "✅ PASS - Configuration Complete"
    elif summary['websocket_support_enabled']:
        overall_status = "⚠️  PARTIAL - WebSocket enabled, HSTS needs configuration"
    else:
        overall_status = "❌ FAIL - WebSocket support not enabled"
    
    print(f"\n🎯 Overall Status: {overall_status}")
    
    # Save results
    results_file = Path("logs/phase2_websocket_test_results.json")
    results_file.parent.mkdir(exist_ok=True)
    with open(results_file, "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📄 Results saved to: {results_file}")
    
    log_action("test_complete", "Phase 2 WebSocket configuration test completed", "completed", {
        "overall_status": overall_status,
        "success_rate": summary['success_rate']
    })
    
    return 0 if summary['websocket_support_enabled'] else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)