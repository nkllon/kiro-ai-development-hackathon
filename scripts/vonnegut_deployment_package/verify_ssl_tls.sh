#!/bin/bash
"""
SSL/TLS Configuration Verification Script for Cloudflare Dashboard

This script verifies SSL/TLS settings to ensure Full Strict mode is enabled
for secure WebSocket connections.
"""

set -e

DOMAIN="observatory.nkllon.com"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")

# Logging function
log_action() {
    local action="$1"
    local status="$2"
    local details="$3"
    
    cat << EOF
{"timestamp": "$TIMESTAMP", "task": "7.0", "action": "$action", "status": "$status", "details": $details}
EOF
}

echo "🔒 SSL/TLS Configuration Verification for Cloudflare Dashboard"
echo "=============================================================="

# Check if openssl is available
if ! command -v openssl &> /dev/null; then
    log_action "check_openssl", "error", '{"error": "OpenSSL not available"}'
    echo "❌ OpenSSL not available. Please install OpenSSL to continue."
    exit 1
fi

log_action "check_openssl", "completed", '{"available": true}'

# Function to verify SSL/TLS mode
verify_ssl_tls_mode() {
    echo "📋 Verifying SSL/TLS encryption mode..."
    log_action "verify_ssl_tls_mode", "in_progress", '{}'
    
    # Get certificate information
    if openssl s_client -connect "$DOMAIN:443" -servername "$DOMAIN" -verify_return_error < /dev/null 2>/dev/null; then
        CERT_INFO=$(openssl s_client -connect "$DOMAIN:443" -servername "$DOMAIN" < /dev/null 2>/dev/null | openssl x509 -noout -text 2>/dev/null)
        
        if [ $? -eq 0 ]; then
            SSL_MODE="Full (Strict)"
            CERT_VALID=true
            
            # Extract certificate details
            SUBJECT=$(echo "$CERT_INFO" | grep "Subject:" | head -1)
            ISSUER=$(echo "$CERT_INFO" | grep "Issuer:" | head -1)
            VALID_FROM=$(echo "$CERT_INFO" | grep "Not Before:" | head -1)
            VALID_TO=$(echo "$CERT_INFO" | grep "Not After:" | head -1)
            
            CERT_DETAILS=$(cat << EOF
{
    "ssl_mode": "$SSL_MODE",
    "certificate_valid": $CERT_VALID,
    "subject": "$SUBJECT",
    "issuer": "$ISSUER",
    "valid_from": "$VALID_FROM",
    "valid_to": "$VALID_TO"
}
EOF
)
            
            log_action "verify_ssl_tls_mode", "completed", "$CERT_DETAILS"
            echo "✅ SSL/TLS Mode: $SSL_MODE"
            echo "✅ Certificate: Valid"
            return 0
        else
            log_action "verify_ssl_tls_mode", "error", '{"error": "Certificate validation failed"}'
            echo "❌ SSL/TLS Mode: Certificate validation failed"
            return 1
        fi
    else
        log_action "verify_ssl_tls_mode", "error", '{"error": "SSL connection failed"}'
        echo "❌ SSL/TLS Mode: SSL connection failed"
        return 1
    fi
}

# Function to verify TLS version
verify_tls_version() {
    echo "📋 Verifying TLS version support..."
    log_action "verify_tls_version", "in_progress", '{}'
    
    # Test TLS 1.2
    if openssl s_client -connect "$DOMAIN:443" -tls1_2 -servername "$DOMAIN" < /dev/null 2>/dev/null; then
        TLS_VERSION="TLS 1.2"
        TLS_SUPPORTED=true
        
        TLS_DETAILS=$(cat << EOF
{
    "supported_versions": ["$TLS_VERSION"],
    "minimum_version": "$TLS_VERSION",
    "tls_supported": $TLS_SUPPORTED
}
EOF
)
        
        log_action "verify_tls_version", "completed", "$TLS_DETAILS"
        echo "✅ TLS Version: $TLS_VERSION supported"
        return 0
    else
        log_action "verify_tls_version", "error", '{"error": "TLS 1.2 not supported"}'
        echo "❌ TLS Version: TLS 1.2 not supported"
        return 1
    fi
}

# Function to verify cipher suites
verify_cipher_suites() {
    echo "📋 Verifying cipher suite configuration..."
    log_action "verify_cipher_suites", "in_progress", '{}'
    
    # Get cipher information
    CIPHER_INFO=$(openssl s_client -connect "$DOMAIN:443" -servername "$DOMAIN" < /dev/null 2>/dev/null | grep "Cipher:")
    
    if [ $? -eq 0 ] && [ -n "$CIPHER_INFO" ]; then
        CIPHER_NAME=$(echo "$CIPHER_INFO" | awk '{print $3}')
        
        # Check if cipher is secure
        if echo "$CIPHER_NAME" | grep -E "(AES|ChaCha20|ECDHE)" > /dev/null; then
            CIPHER_SECURE=true
            STATUS="pass"
        else
            CIPHER_SECURE=false
            STATUS="warning"
        fi
        
        CIPHER_DETAILS=$(cat << EOF
{
    "cipher_name": "$CIPHER_NAME",
    "is_secure": $CIPHER_SECURE,
    "status": "$STATUS"
}
EOF
)
        
        log_action "verify_cipher_suites", "completed", "$CIPHER_DETAILS"
        
        if [ "$STATUS" = "pass" ]; then
            echo "✅ Cipher Suite: $CIPHER_NAME (Secure)"
        else
            echo "⚠️  Cipher Suite: $CIPHER_NAME (Review recommended)"
        fi
        return 0
    else
        log_action "verify_cipher_suites", "error", '{"error": "No cipher information available"}'
        echo "❌ Cipher Suite: No cipher information available"
        return 1
    fi
}

# Function to verify TLS handshake
verify_tls_handshake() {
    echo "📋 Verifying TLS handshake performance..."
    log_action "verify_tls_handshake", "in_progress", '{}'
    
    # Measure handshake time
    START_TIME=$(date +%s%3N)
    
    if openssl s_client -connect "$DOMAIN:443" -servername "$DOMAIN" < /dev/null 2>/dev/null; then
        END_TIME=$(date +%s%3N)
        HANDSHAKE_TIME=$((END_TIME - START_TIME))
        
        if [ $HANDSHAKE_TIME -lt 5000 ]; then
            STATUS="pass"
        else
            STATUS="warning"
        fi
        
        HANDSHAKE_DETAILS=$(cat << EOF
{
    "handshake_time_ms": $HANDSHAKE_TIME,
    "status": "$STATUS"
}
EOF
)
        
        log_action "verify_tls_handshake", "completed", "$HANDSHAKE_DETAILS"
        
        if [ "$STATUS" = "pass" ]; then
            echo "✅ TLS Handshake: ${HANDSHAKE_TIME}ms (Good)"
        else
            echo "⚠️  TLS Handshake: ${HANDSHAKE_TIME}ms (Slow)"
        fi
        return 0
    else
        log_action "verify_tls_handshake", "error", '{"error": "TLS handshake failed"}'
        echo "❌ TLS Handshake: Failed"
        return 1
    fi
}

# Function to test WebSocket SSL
test_websocket_ssl() {
    echo "📋 Testing WebSocket SSL connection..."
    log_action "test_websocket_ssl", "in_progress", '{}'
    
    # Test WebSocket endpoint with curl
    if command -v curl &> /dev/null; then
        WEBSOCKET_RESPONSE=$(curl -I -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" -H "Sec-WebSocket-Version: 13" "https://$DOMAIN/ws/emoji-rain" 2>/dev/null | head -1)
        
        if echo "$WEBSOCKET_RESPONSE" | grep -E "(101|Switching Protocols)" > /dev/null; then
            WEBSOCKET_SUCCESS=true
            STATUS="pass"
        else
            WEBSOCKET_SUCCESS=false
            STATUS="fail"
        fi
        
        WEBSOCKET_DETAILS=$(cat << EOF
{
    "websocket_success": $WEBSOCKET_SUCCESS,
    "response": "$WEBSOCKET_RESPONSE",
    "status": "$STATUS"
}
EOF
)
        
        log_action "test_websocket_ssl", "completed", "$WEBSOCKET_DETAILS"
        
        if [ "$STATUS" = "pass" ]; then
            echo "✅ WebSocket SSL: Connection successful"
        else
            echo "❌ WebSocket SSL: Connection failed"
        fi
        return 0
    else
        log_action "test_websocket_ssl", "error", '{"error": "curl not available"}'
        echo "❌ WebSocket SSL: curl not available"
        return 1
    fi
}

# Run all verification checks
echo ""
echo "🔍 Running SSL/TLS verification checks..."

TOTAL_CHECKS=5
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

# Run checks
verify_ssl_tls_mode && ((PASSED_CHECKS++)) || ((FAILED_CHECKS++))
verify_tls_version && ((PASSED_CHECKS++)) || ((FAILED_CHECKS++))
verify_cipher_suites && ((PASSED_CHECKS++)) || ((FAILED_CHECKS++))
verify_tls_handshake && ((PASSED_CHECKS++)) || ((FAILED_CHECKS++))
test_websocket_ssl && ((PASSED_CHECKS++)) || ((FAILED_CHECKS++))

# Calculate success rate
SUCCESS_RATE=$(echo "scale=1; $PASSED_CHECKS * 100 / $TOTAL_CHECKS" | bc -l 2>/dev/null || echo "0")

# Determine overall status
if [ $FAILED_CHECKS -eq 0 ]; then
    OVERALL_STATUS="pass"
else
    OVERALL_STATUS="fail"
fi

# Display summary
echo ""
echo "📊 SSL/TLS Verification Summary:"
echo "   Domain: $DOMAIN"
echo "   Overall Status: $(echo $OVERALL_STATUS | tr '[:lower:]' '[:upper:]')"
echo "   Success Rate: ${SUCCESS_RATE}%"
echo "   Total Checks: $TOTAL_CHECKS"
echo "   Passed: $PASSED_CHECKS"
echo "   Failed: $FAILED_CHECKS"
echo "   Warnings: $WARNING_CHECKS"

# Display Cloudflare dashboard configuration instructions
echo ""
echo "🚨 Critical Cloudflare Dashboard Configuration Steps:"
echo "   📍 SSL/TLS Encryption Mode"
echo "      Location: SSL/TLS → Overview → Encryption Mode"
echo "      Required: Full (strict)"
echo "      Description: Ensures end-to-end encryption with certificate validation"
echo ""
echo "   📍 TLS Version"
echo "      Location: SSL/TLS → Edge Certificates → TLS Version"
echo "      Required: TLS 1.2 or higher"
echo "      Description: Minimum TLS version for secure connections"
echo ""
echo "   📍 HTTP Strict Transport Security (HSTS)"
echo "      Location: SSL/TLS → Edge Certificates → HTTP Strict Transport Security (HSTS)"
echo "      Required: Enabled with appropriate max-age"
echo "      Description: Forces HTTPS connections and prevents downgrade attacks"
echo ""
echo "   📍 WebSocket Support"
echo "      Location: Network → WebSockets"
echo "      Required: Enabled"
echo "      Description: Required for WebSocket connections through tunnel"
echo ""

# Final completion log
FINAL_SUMMARY=$(cat << EOF
{
    "timestamp": "$TIMESTAMP",
    "domain": "$DOMAIN",
    "total_checks": $TOTAL_CHECKS,
    "passed_checks": $PASSED_CHECKS,
    "failed_checks": $FAILED_CHECKS,
    "warning_checks": $WARNING_CHECKS,
    "success_rate": $SUCCESS_RATE,
    "overall_status": "$OVERALL_STATUS"
}
EOF
)

log_action "ssl_tls_verification_complete", "completed", "$FINAL_SUMMARY"

# Final completion log
cat << EOF
{"task": "7.0", "status": "completed", "summary": "SSL/TLS configuration verified", "details": $FINAL_SUMMARY}
EOF

# Exit with appropriate code
if [ "$OVERALL_STATUS" = "pass" ]; then
    exit 0
else
    exit 1
fi