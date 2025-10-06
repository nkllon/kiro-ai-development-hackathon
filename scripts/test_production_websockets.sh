#!/bin/bash

# Production WebSocket Validation Script for observatory.nkllon.com
# Fibonacci iteration 5d - Production endpoint validation

echo "🚀 PRODUCTION WEBSOCKET VALIDATION MISSION"
echo "=========================================="
echo "🎯 Target: observatory.nkllon.com"
echo "📅 Timestamp: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
echo ""

# Define endpoints to test
endpoints=(
    "/ws/emoji-rain"
    "/ws/observatory"
    "/ws/anomalies"
    "/ws/doctor-status"
)

base_url="https://observatory.nkllon.com"
success_count=0
total_endpoints=${#endpoints[@]}

echo "📋 Testing Production WebSocket Endpoints:"
echo ""

# Test each endpoint
for endpoint in "${endpoints[@]}"; do
    url="${base_url}${endpoint}"
    echo "Testing: ${endpoint}"
    
    # Test WebSocket handshake
    response=$(curl -i -N --max-time 15 --connect-timeout 10 \
        -H "Connection: Upgrade" \
        -H "Upgrade: websocket" \
        -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
        -H "Sec-WebSocket-Version: 13" \
        -H "Sec-WebSocket-Protocol: chat, superchat" \
        -H "Origin: https://observatory.nkllon.com" \
        -H "User-Agent: Production-WebSocket-Validator/1.0" \
        "${url}" 2>&1)
    
    # Check for HTTP/1.1 101 Switching Protocols
    if echo "$response" | grep -q "101 Switching Protocols"; then
        echo "  ✅ Status: HTTP/1.1 101 Switching Protocols"
        echo "  ✅ WebSocket handshake successful"
        ((success_count++))
    else
        echo "  ❌ Status: WebSocket handshake failed"
        echo "  📄 Response preview:"
        echo "$response" | head -5 | sed 's/^/    /'
    fi
    
    echo ""
done

# Calculate results
success_rate=$((success_count * 100 / total_endpoints))

echo "📊 PRODUCTION VALIDATION RESULTS:"
echo "================================="
echo "🎯 Endpoints Tested: ${total_endpoints}"
echo "✅ Successful: ${success_count}"
echo "📈 Success Rate: ${success_rate}%"
echo ""

if [ $success_count -eq $total_endpoints ]; then
    echo "🎉 MISSION STATUS: PASS"
    echo "🚀 All WebSocket endpoints validated in production!"
    exit_code=0
else
    echo "⚠️  MISSION STATUS: FAIL"
    echo "❌ Some WebSocket endpoints failed validation"
    exit_code=1
fi

echo ""
echo "💡 Recommendations:"
echo "1. Review Cloudflare tunnel WebSocket configuration"
echo "2. Check Observatory server WebSocket handlers"
echo "3. Verify bot protection settings for WebSocket endpoints"
echo "4. Implement continuous WebSocket monitoring"
echo "5. Set up automated alerts for WebSocket failures"

echo ""
echo "=========================================="

exit $exit_code