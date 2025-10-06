#!/bin/bash
# SSL/TLS Full Strict Mode Deployment Script for Observatory
# Target: observatory.nkllon.com
# Mission: Configure SSL/TLS to Full Strict mode for secure WebSocket connections
# Fibonacci Iteration 2 - Single Agent Deployment

set -e

echo "🔒 SSL/TLS Full Strict Mode Deployment for Observatory"
echo "====================================================="
echo "Target: observatory.nkllon.com"
echo "Mission: Configure SSL/TLS to Full Strict mode"
echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo ""

# Create logs directory
mkdir -p logs/ssl_tls_deployment

# Log function for JSON format
log_action() {
    local action="$1"
    local status="$2"
    local details="$3"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    cat << EOF
{
  "timestamp": "$timestamp",
  "task": "ssl_tls_deployment",
  "action": "$action",
  "status": "$status",
  "details": $details
}
EOF
}

# Test 1: Current SSL/TLS configuration
echo "📋 Test 1: Current SSL/TLS configuration"
log_action "test_current_ssl_configuration" "in_progress" '{"domain": "observatory.nkllon.com"}'

if openssl s_client -connect observatory.nkllon.com:443 -servername observatory.nkllon.com < /dev/null 2>/dev/null | grep -q "Verify return code: 0"; then
    echo "✅ SSL/TLS connection: PASS"
    log_action "test_current_ssl_configuration" "completed" '{"ssl_connection": "pass", "verify_return_code": "0"}'
else
    echo "❌ SSL/TLS connection: FAIL"
    echo "   Action required: Configure SSL/TLS in Cloudflare dashboard"
    log_action "test_current_ssl_configuration" "error" '{"ssl_connection": "fail", "action_required": "configure_cloudflare_ssl_tls"}'
fi

# Test 2: Certificate validation
echo "📋 Test 2: Certificate validation"
log_action "test_certificate_validation" "in_progress" '{"domain": "observatory.nkllon.com"}'

if openssl s_client -connect observatory.nkllon.com:443 -servername observatory.nkllon.com < /dev/null 2>/dev/null | grep -q "Verify return code: 0"; then
    echo "✅ Certificate validation: PASS"
    log_action "test_certificate_validation" "completed" '{"certificate_validation": "pass"}'
else
    echo "❌ Certificate validation: FAIL"
    echo "   Action required: Verify certificate configuration"
    log_action "test_certificate_validation" "error" '{"certificate_validation": "fail", "action_required": "verify_certificate_config"}'
fi

# Test 3: TLS version support
echo "📋 Test 3: TLS version support"
log_action "test_tls_version_support" "in_progress" '{"domain": "observatory.nkllon.com"}'

if openssl s_client -connect observatory.nkllon.com:443 -tls1_2 < /dev/null 2>/dev/null | grep -q "Protocol.*TLSv1.2"; then
    echo "✅ TLS 1.2 support: PASS"
    log_action "test_tls_version_support" "completed" '{"tls_1_2_support": "pass"}'
else
    echo "❌ TLS 1.2 support: FAIL"
    echo "   Action required: Enable TLS 1.2 in Cloudflare dashboard"
    log_action "test_tls_version_support" "error" '{"tls_1_2_support": "fail", "action_required": "enable_tls_1_2"}'
fi

# Test 4: WebSocket SSL connection
echo "📋 Test 4: WebSocket SSL connection"
log_action "test_websocket_ssl" "in_progress" '{"websocket_url": "wss://observatory.nkllon.com/ws/emoji-rain"}'

if curl -s -I -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" -H "Sec-WebSocket-Version: 13" https://observatory.nkllon.com/ws/emoji-rain | grep -q "HTTP/2 101"; then
    echo "✅ WebSocket SSL: PASS"
    log_action "test_websocket_ssl" "completed" '{"websocket_ssl": "pass", "upgrade_successful": true}'
else
    echo "❌ WebSocket SSL: FAIL"
    echo "   Action required: Enable WebSocket support in Cloudflare dashboard"
    log_action "test_websocket_ssl" "error" '{"websocket_ssl": "fail", "action_required": "enable_websocket_support"}'
fi

# Test 5: HSTS header
echo "📋 Test 5: HSTS header"
log_action "test_hsts_header" "in_progress" '{"domain": "observatory.nkllon.com"}'

if curl -s -I https://observatory.nkllon.com | grep -qi "strict-transport-security"; then
    echo "✅ HSTS header: PASS"
    log_action "test_hsts_header" "completed" '{"hsts_header": "present"}'
else
    echo "❌ HSTS header: FAIL"
    echo "   Action required: Enable HSTS in Cloudflare dashboard"
    log_action "test_hsts_header" "error" '{"hsts_header": "missing", "action_required": "enable_hsts"}'
fi

echo ""
echo "🚨 CRITICAL CLOUDFLARE DASHBOARD CONFIGURATION STEPS:"
echo "   1. Navigate to: https://dash.cloudflare.com"
echo "   2. Select domain: observatory.nkllon.com"
echo "   3. Go to: SSL/TLS → Overview → Encryption Mode"
echo "   4. Set to: Full (strict)"
echo "   5. Go to: SSL/TLS → Edge Certificates → TLS Version"
echo "   6. Set to: TLS 1.2 or higher"
echo "   7. Go to: SSL/TLS → Edge Certificates → HTTP Strict Transport Security (HSTS)"
echo "   8. Enable HSTS with max-age: 31536000"
echo "   9. Go to: Network → WebSockets"
echo "   10. Toggle WebSockets to: ON"
echo ""

# Generate detailed certificate information
echo "📋 Certificate Information:"
log_action "get_certificate_info" "in_progress" '{"domain": "observatory.nkllon.com"}'

echo "Certificate details:"
openssl s_client -connect observatory.nkllon.com:443 -servername observatory.nkllon.com < /dev/null 2>/dev/null | grep -E "(subject=|issuer=|notBefore=|notAfter=|Protocol:|Cipher:|Verify return code:)"

log_action "get_certificate_info" "completed" '{"certificate_info_extracted": true}'

echo ""
echo "🎯 SUCCESS CRITERIA:"
echo "   • SSL/TLS mode set to Full (strict)"
echo "   • Certificate validation working"
echo "   • No SSL/TLS warnings or errors"
echo "   • Secure WebSocket connections (wss://) functional"
echo "   • HSTS header present in responses"
echo "   • TLS 1.2 or higher supported"
echo ""

# Final completion log
log_action "ssl_tls_deployment_complete" "completed" '{"summary": "SSL/TLS Full Strict mode deployment ready", "next_steps": "configure_cloudflare_dashboard"}'

echo "✅ SSL/TLS deployment script completed!"
echo ""
echo "🚀 EXECUTION INSTRUCTIONS:"
echo "   1. Follow the Cloudflare dashboard configuration steps above"
echo "   2. Run verification commands after configuration"
echo "   3. Test WebSocket connections with wss:// protocol"
echo "   4. Verify all success criteria are met"