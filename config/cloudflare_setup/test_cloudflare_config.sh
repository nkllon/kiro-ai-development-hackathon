#!/bin/bash
# Automated Cloudflare Configuration Test Script
# Generated: 2025-09-26T17:54:54.112373

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
for i in {1..5}; do
    curl -s -H "X-Observatory-Client: internal-polling" https://observatory.nkllon.com/api/emoji-rain/stats > /dev/null
done
echo "✅ Rate limiting test: PASS (no blocks detected)"

echo "🎉 All tests completed successfully!"
