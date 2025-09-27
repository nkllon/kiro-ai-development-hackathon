#!/bin/bash
# WebSocket Connectivity Test Commands for Observatory
# Run these commands to verify WebSocket support is working

echo "🔍 WebSocket Connectivity Test Suite"
echo "=================================="

# Test 1: Basic WebSocket handshake test
echo "📡 Test 1: WebSocket Handshake Test"
echo "Testing WebSocket upgrade request to observatory.nkllon.com..."
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" -H "Sec-WebSocket-Version: 13" https://observatory.nkllon.com/ws/observatory

echo -e "\n"

# Test 2: Test all WebSocket endpoints
echo "📡 Test 2: All WebSocket Endpoints"
endpoints=("/ws/emoji-rain" "/ws/observatory" "/ws/anomalies" "/ws/doctor-status")

for endpoint in "${endpoints[@]}"; do
    echo "Testing $endpoint..."
    curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" -H "Sec-WebSocket-Version: 13" "https://observatory.nkllon.com$endpoint"
    echo -e "\n---\n"
done

# Test 3: Direct localhost test (should work)
echo "📡 Test 3: Localhost Direct Test (Control)"
echo "Testing direct localhost connection..."
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" -H "Sec-WebSocket-Version: 13" http://localhost:8888/ws/observatory

echo -e "\n"

# Test 4: SSL/TLS verification
echo "📡 Test 4: SSL/TLS Certificate Check"
echo "Checking SSL certificate for observatory.nkllon.com..."
openssl s_client -connect observatory.nkllon.com:443 -servername observatory.nkllon.com < /dev/null 2>/dev/null | openssl x509 -noout -dates

echo -e "\n"

# Test 5: HTTP/2 support check
echo "📡 Test 5: HTTP/2 Support Check"
echo "Checking if HTTP/2 is supported..."
curl -I --http2 https://observatory.nkllon.com/ 2>/dev/null | grep -i "HTTP/"

echo -e "\n"

# Test 6: WebSocket with proper headers
echo "📡 Test 6: Full WebSocket Headers Test"
echo "Testing with complete WebSocket headers..."
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Protocol: chat, superchat" \
  -H "Origin: https://observatory.nkllon.com" \
  https://observatory.nkllon.com/ws/observatory

echo -e "\n"

echo "✅ Test suite complete!"
echo ""
echo "Expected Results:"
echo "- Tests 1-2,6: Should return 'HTTP/1.1 101 Switching Protocols'"
echo "- Test 3: Should return 'HTTP/1.1 101 Switching Protocols' (control)"
echo "- Test 4: Should show valid SSL certificate dates"
echo "- Test 5: Should show 'HTTP/2' in response"
echo ""
echo "If any test fails, check:"
echo "1. WebSocket enabled in Cloudflare Dashboard"
echo "2. SSL/TLS mode set to 'Full (strict)'"
echo "3. Updated tunnel configuration applied"
echo "4. Tunnel restarted with new configuration"