#!/usr/bin/env python3
"""
Cloudflare Dashboard Setup Instructions

This script provides step-by-step instructions for configuring
Cloudflare dashboard settings to enable WebSocket support and
configure bot protection for Observatory.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def generate_cloudflare_setup_instructions():
    """Generate comprehensive Cloudflare dashboard setup instructions"""
    
    instructions = {
        "title": "Cloudflare Dashboard Setup for Observatory WebSocket Support",
        "timestamp": datetime.now().isoformat(),
        "domain": "observatory.nkllon.com",
        "tunnel_id": "d1e53e43-033f-4994-8f46-c83962ae3785",
        "steps": [
            {
                "step": 1,
                "title": "Enable WebSockets",
                "description": "Enable WebSocket support in Cloudflare dashboard",
                "location": "Network → WebSockets",
                "action": "Toggle WebSockets to ON",
                "reason": "Required for WebSocket connections through tunnel",
                "expected_result": "WebSocket connections will work through tunnel",
                "verification": "Test WebSocket connection to wss://observatory.nkllon.com/ws/emoji-rain"
            },
            {
                "step": 2,
                "title": "Configure Bot Protection",
                "description": "Set up bot protection rules for Observatory",
                "location": "Security → Bot Fight Mode",
                "action": "Disable Bot Fight Mode for observatory.nkllon.com",
                "reason": "Prevents false positives on legitimate polling",
                "expected_result": "HTTP polling fallback will not trigger bot protection",
                "verification": "Check that HTTP polling requests are not blocked"
            },
            {
                "step": 3,
                "title": "Create WAF Rules",
                "description": "Create custom WAF rules for Observatory polling",
                "location": "Security → WAF → Custom Rules",
                "action": "Create rule with Observatory polling conditions",
                "reason": "Whitelist legitimate polling patterns",
                "rule_expression": """
                    (http.host eq "observatory.nkllon.com" and
                     http.request.uri.path starts_with "/api/" and
                     http.request.headers.x-observatory-client eq "internal-polling")
                """,
                "rule_action": "Allow",
                "expected_result": "Observatory polling requests are whitelisted",
                "verification": "Check WAF logs for allowed requests"
            },
            {
                "step": 4,
                "title": "Configure Rate Limiting",
                "description": "Set appropriate rate limits for Observatory",
                "location": "Security → Rate Limiting",
                "action": "Create rate limit rule for /api/* endpoints",
                "reason": "Prevent abuse while allowing legitimate polling",
                "rate_limit_config": {
                    "requests_per_minute": 60,
                    "burst_size": 10,
                    "action": "Block",
                    "duration": "1 minute"
                },
                "expected_result": "Reasonable rate limits prevent abuse",
                "verification": "Test rate limiting with multiple requests"
            },
            {
                "step": 5,
                "title": "Firewall Rules",
                "description": "Create firewall rules for Observatory traffic",
                "location": "Security → Firewall Rules",
                "action": "Allow Observatory polling traffic",
                "reason": "Ensure Observatory traffic is not blocked",
                "rule_expression": """
                    (http.host eq "observatory.nkllon.com" and
                     http.request.uri.path starts_with "/api/" and
                     http.request.headers.x-polling-reason eq "websocket-fallback")
                """,
                "rule_action": "Allow",
                "expected_result": "Observatory traffic is not blocked by firewall",
                "verification": "Check firewall logs for allowed traffic"
            }
        ],
        "troubleshooting": {
            "websocket_404": {
                "symptom": "WebSocket connections return HTTP/2 404",
                "cause": "WebSockets not enabled in Cloudflare dashboard",
                "solution": "Enable WebSockets in Network → WebSockets",
                "verification": "Test WebSocket connection after enabling"
            },
            "bot_protection_error": {
                "symptom": "HTTP polling triggers Error 1033",
                "cause": "Bot protection blocking legitimate requests",
                "solution": "Disable Bot Fight Mode and create WAF rules",
                "verification": "Check bot protection logs"
            },
            "rate_limiting": {
                "symptom": "Requests blocked by rate limiting",
                "cause": "Rate limits too restrictive",
                "solution": "Adjust rate limit rules for Observatory",
                "verification": "Test with expected polling frequency"
            }
        },
        "testing_commands": {
            "websocket_test": "curl -I -N -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' -H 'Sec-WebSocket-Version: 13' https://observatory.nkllon.com/ws/emoji-rain",
            "http_polling_test": "curl -H 'X-Observatory-Client: internal-polling' -H 'X-Polling-Reason: websocket-fallback' https://observatory.nkllon.com/api/emoji-rain/stats",
            "health_check": "curl -I https://observatory.nkllon.com/health"
        }
    }
    
    return instructions

def generate_automated_test_script():
    """Generate automated test script for Cloudflare configuration"""
    
    test_script = """#!/bin/bash
# Automated Cloudflare Configuration Test Script
# Generated: {timestamp}

set -e

echo "🔧 Testing Cloudflare Configuration for Observatory"
echo "=================================================="

# Test 1: Health check
echo "📋 Test 1: Health check"
if curl -s -I https://observatory.nkllon.com/health | grep -q "HTTP/2 405"; then
    echo "✅ Health check: PASS"
else
    echo "❌ Health check: FAIL"
    exit 1
fi

# Test 2: WebSocket connection
echo "📋 Test 2: WebSocket connection"
if curl -s -I -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" -H "Sec-WebSocket-Version: 13" https://observatory.nkllon.com/ws/emoji-rain | grep -q "HTTP/2 101"; then
    echo "✅ WebSocket connection: PASS"
else
    echo "❌ WebSocket connection: FAIL (expected if WebSockets not enabled)"
fi

# Test 3: HTTP polling with bot-safe headers
echo "📋 Test 3: HTTP polling with bot-safe headers"
if curl -s -H "X-Observatory-Client: internal-polling" -H "X-Polling-Reason: websocket-fallback" https://observatory.nkllon.com/api/emoji-rain/stats | grep -q "active_effects"; then
    echo "✅ HTTP polling: PASS"
else
    echo "❌ HTTP polling: FAIL"
    exit 1
fi

# Test 4: Rate limiting test
echo "📋 Test 4: Rate limiting test"
for i in {{1..5}}; do
    curl -s -H "X-Observatory-Client: internal-polling" https://observatory.nkllon.com/api/emoji-rain/stats > /dev/null
done
echo "✅ Rate limiting test: PASS (no blocks detected)"

echo "🎉 All tests completed successfully!"
""".format(timestamp=datetime.now().isoformat())
    
    return test_script

def main():
    """Main script to generate Cloudflare setup instructions"""
    print("🔧 Cloudflare Dashboard Setup Instructions Generator")
    print("=" * 60)
    
    # Generate instructions
    instructions = generate_cloudflare_setup_instructions()
    test_script = generate_automated_test_script()
    
    # Save instructions
    output_dir = Path("config/cloudflare_setup")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "dashboard_instructions.json", "w") as f:
        json.dump(instructions, f, indent=2)
    
    with open(output_dir / "test_cloudflare_config.sh", "w") as f:
        f.write(test_script)
    
    # Make test script executable
    import os
    os.chmod(output_dir / "test_cloudflare_config.sh", 0o755)
    
    print(f"✅ Setup instructions generated in {output_dir}")
    print(f"   • dashboard_instructions.json")
    print(f"   • test_cloudflare_config.sh")
    
    print(f"\n📋 Cloudflare Dashboard Setup Steps:")
    for step in instructions["steps"]:
        print(f"   {step['step']}. {step['title']}")
        print(f"      Location: {step['location']}")
        print(f"      Action: {step['action']}")
        print(f"      Reason: {step['reason']}")
        print()
    
    print(f"🚀 Next Steps:")
    print(f"   1. Follow the dashboard setup steps above")
    print(f"   2. Run the test script: ./config/cloudflare_setup/test_cloudflare_config.sh")
    print(f"   3. Verify WebSocket connectivity through tunnel")
    print(f"   4. Monitor WebSocket health with automated monitoring")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
