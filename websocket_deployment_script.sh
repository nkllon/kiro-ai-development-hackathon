#!/bin/bash
# WebSocket Fix Deployment Script
# Target: observatory.nkllon.com
# Mission: Enable WebSocket support in Cloudflare Dashboard

set -e

echo "🚀 WebSocket Fix Deployment Script"
echo "=================================="
echo "Target: observatory.nkllon.com"
echo "Mission: Enable WebSocket support in Cloudflare Dashboard"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Step 1: Check current tunnel configuration
print_status "Checking current tunnel configuration..."
if [ -f ~/.cloudflared/config.yml ]; then
    print_success "Tunnel configuration file found"
    if grep -q "connectTimeout: 30s" ~/.cloudflared/config.yml; then
        print_success "WebSocket support already configured in tunnel"
    else
        print_warning "WebSocket support may not be fully configured in tunnel"
    fi
else
    print_error "Tunnel configuration file not found at ~/.cloudflared/config.yml"
    exit 1
fi

# Step 2: Test current WebSocket connectivity
print_status "Testing current WebSocket connectivity..."

# Test WebSocket upgrade
print_status "Testing WebSocket upgrade to /ws/emoji-rain..."
WEBSOCKET_TEST=$(curl -s -I -N -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' -H 'Sec-WebSocket-Version: 13' https://observatory.nkllon.com/ws/emoji-rain 2>/dev/null | head -1)

if echo "$WEBSOCKET_TEST" | grep -q "101 Switching Protocols"; then
    print_success "WebSocket upgrade successful: HTTP/1.1 101 Switching Protocols"
    WEBSOCKET_WORKING=true
elif echo "$WEBSOCKET_TEST" | grep -q "404"; then
    print_warning "WebSocket upgrade failed: HTTP/2 404 (WebSocket support not enabled)"
    WEBSOCKET_WORKING=false
else
    print_warning "WebSocket upgrade returned: $WEBSOCKET_TEST"
    WEBSOCKET_WORKING=false
fi

# Test health endpoint
print_status "Testing health endpoint..."
HEALTH_TEST=$(curl -s -I https://observatory.nkllon.com/health 2>/dev/null | head -1)
if echo "$HEALTH_TEST" | grep -q "405\|200"; then
    print_success "Health endpoint accessible: $HEALTH_TEST"
else
    print_error "Health endpoint not accessible: $HEALTH_TEST"
fi

# Step 3: Provide Cloudflare Dashboard instructions
echo ""
print_status "CLOUDFLARE DASHBOARD CONFIGURATION REQUIRED"
echo "=================================================="
echo ""
echo "Manual action required: Enable WebSocket support in Cloudflare Dashboard"
echo ""
echo "Steps:"
echo "1. Go to: https://dash.cloudflare.com/"
echo "2. Select domain: observatory.nkllon.com"
echo "3. Navigate to: Network → WebSockets"
echo "4. Toggle 'WebSocket support' to ON"
echo "5. Click Save"
echo ""
echo "After enabling WebSocket support, wait 2-3 minutes for changes to propagate."
echo ""

# Step 4: Test all WebSocket endpoints
print_status "Testing all WebSocket endpoints..."

ENDPOINTS=("emoji-rain" "observatory" "anomalies" "doctor-status")
for endpoint in "${ENDPOINTS[@]}"; do
    print_status "Testing /ws/$endpoint..."
    TEST_RESULT=$(curl -s -I -N -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' -H 'Sec-WebSocket-Version: 13' https://observatory.nkllon.com/ws/$endpoint 2>/dev/null | head -1)
    
    if echo "$TEST_RESULT" | grep -q "101 Switching Protocols"; then
        print_success "/ws/$endpoint: HTTP/1.1 101 Switching Protocols ✅"
    elif echo "$TEST_RESULT" | grep -q "404"; then
        print_warning "/ws/$endpoint: HTTP/2 404 (WebSocket support needed) ❌"
    else
        print_warning "/ws/$endpoint: $TEST_RESULT"
    fi
done

# Step 5: Provide verification commands
echo ""
print_status "VERIFICATION COMMANDS"
echo "========================"
echo ""
echo "After enabling WebSocket support in Cloudflare Dashboard, run these commands:"
echo ""
echo "# Test WebSocket upgrade"
echo "curl -I -N -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' -H 'Sec-WebSocket-Version: 13' https://observatory.nkllon.com/ws/emoji-rain"
echo ""
echo "# Test all endpoints"
echo "for endpoint in emoji-rain observatory anomalies doctor-status; do"
echo "  echo \"Testing \$endpoint...\""
echo "  curl -I -N -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' -H 'Sec-WebSocket-Version: 13' https://observatory.nkllon.com/ws/\$endpoint"
echo "done"
echo ""
echo "# Browser console test"
echo "const ws = new WebSocket('wss://observatory.nkllon.com/ws/emoji-rain');"
echo "ws.onopen = () => console.log('✅ WebSocket connected');"
echo "ws.onerror = (e) => console.log('❌ WebSocket failed:', e);"
echo ""

# Step 6: Summary
echo ""
print_status "DEPLOYMENT SUMMARY"
echo "==================="
echo ""
if [ "$WEBSOCKET_WORKING" = true ]; then
    print_success "WebSocket support appears to be working!"
    echo "✅ WebSocket connections return HTTP/1.1 101 Switching Protocols"
    echo "✅ Real-time features should be functional"
    echo "✅ No HTTP polling fallback needed"
else
    print_warning "WebSocket support needs to be enabled in Cloudflare Dashboard"
    echo "❌ WebSocket connections return HTTP/2 404"
    echo "❌ HTTP polling fallback may be active"
    echo "❌ Bot protection may trigger Error 1033"
fi

echo ""
echo "Next steps:"
echo "1. Enable WebSocket support in Cloudflare Dashboard (if not already done)"
echo "2. Wait 2-3 minutes for changes to propagate"
echo "3. Re-run this script to verify WebSocket connectivity"
echo "4. Test Observatory dashboard for real-time updates"
echo ""

print_status "Deployment script completed!"
echo "Check the results above and follow the next steps as needed."