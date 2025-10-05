# Phase 2: Cloudflare WebSocket Configuration

## Overview
This document provides comprehensive instructions for enabling WebSocket support in Cloudflare Dashboard for `observatory.nkllon.com` and verifying SSL/TLS configuration.

## Objective
- Enable WebSocket support in Cloudflare Dashboard
- Verify SSL/TLS configuration is set to Full (strict) mode
- Test WebSocket endpoints through Cloudflare using curl commands
- Document configuration changes and test results

## Expected Result
**HTTP/1.1 101 Switching Protocols** through Cloudflare for WebSocket connections

---

## Step-by-Step Cloudflare Dashboard Configuration

### Step 1: Enable WebSocket Support
**Location:** Network → WebSockets
**Action:** Toggle WebSocket support to ON
**Description:** Enable WebSocket connections through Cloudflare tunnel
**Verification:** WebSocket connections will work through tunnel
**Expected Result:** HTTP/1.1 101 Switching Protocols for WebSocket endpoints

### Step 2: Verify SSL/TLS Configuration
**Location:** SSL/TLS → Overview → Encryption Mode
**Action:** Ensure SSL/TLS encryption mode is set to 'Full (strict)'
**Description:** End-to-end encryption with certificate validation
**Verification:** Certificate validation enabled
**Expected Result:** Secure WebSocket connections (wss://) with valid certificates

### Step 3: Configure TLS Version
**Location:** SSL/TLS → Edge Certificates → TLS Version
**Action:** Set minimum TLS version to TLS 1.2 or higher
**Description:** Modern TLS version for secure connections
**Verification:** TLS handshake successful with modern protocols
**Expected Result:** TLS 1.2+ connections supported

### Step 4: Enable HSTS
**Location:** SSL/TLS → Edge Certificates → HTTP Strict Transport Security (HSTS)
**Action:** Enable HSTS with appropriate max-age
**Description:** Force HTTPS connections and prevent downgrade attacks
**Verification:** Strict-Transport-Security header present
**Expected Result:** HTTPS-only connections enforced

---

## Testing Commands

### WebSocket Endpoint Tests
```bash
# Test emoji-rain WebSocket endpoint
curl -I -N -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' -H 'Sec-WebSocket-Version: 13' https://observatory.nkllon.com/ws/emoji-rain

# Test observatory WebSocket endpoint
curl -I -N -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' -H 'Sec-WebSocket-Version: 13' https://observatory.nkllon.com/ws/observatory

# Test anomalies WebSocket endpoint
curl -I -N -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' -H 'Sec-WebSocket-Version: 13' https://observatory.nkllon.com/ws/anomalies

# Test doctor-status WebSocket endpoint
curl -I -N -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' -H 'Sec-WebSocket-Version: 13' https://observatory.nkllon.com/ws/doctor-status
```

### SSL/TLS Verification Tests
```bash
# Test SSL mode
curl -I https://observatory.nkllon.com

# Test TLS version
openssl s_client -connect observatory.nkllon.com:443 -tls1_2

# Test certificate
openssl s_client -connect observatory.nkllon.com:443 -servername observatory.nkllon.com
```

---

## Expected Results

### Before Configuration
- **WebSocket Endpoints:** HTTP/2 404 errors
- **SSL Mode:** May be set to Flexible or Full (not strict)
- **HSTS:** May not be enabled

### After Configuration
- **WebSocket Endpoints:** HTTP/1.1 101 Switching Protocols
- **SSL Mode:** Full (strict) - end-to-end encryption with certificate validation
- **HSTS:** Strict-Transport-Security header present
- **TLS Version:** TLS 1.2 or higher supported

---

## WebSocket Endpoints

The following WebSocket endpoints should be accessible after configuration:

1. **wss://observatory.nkllon.com/ws/emoji-rain**
2. **wss://observatory.nkllon.com/ws/observatory**
3. **wss://observatory.nkllon.com/ws/anomalies**
4. **wss://observatory.nkllon.com/ws/doctor-status**

---

## Troubleshooting

### WebSocket Connection Issues
**Symptom:** WebSocket connections return HTTP/2 404
**Cause:** WebSockets not enabled in Cloudflare dashboard
**Solution:** Enable WebSockets in Network → WebSockets
**Verification:** Test WebSocket connection after enabling

### SSL/TLS Issues
**Symptom:** Certificate validation errors
**Cause:** SSL/TLS mode not set to Full (strict)
**Solution:** Set SSL/TLS encryption mode to Full (strict)
**Verification:** Check certificate validation

### HSTS Issues
**Symptom:** No Strict-Transport-Security header
**Cause:** HSTS not enabled
**Solution:** Enable HSTS in SSL/TLS → Edge Certificates
**Verification:** Check for Strict-Transport-Security header

---

## Configuration Validation

### Success Criteria
- ✅ WebSocket support enabled in Cloudflare Dashboard
- ✅ SSL/TLS mode set to Full (strict)
- ✅ HSTS enabled with appropriate max-age
- ✅ TLS 1.2 or higher supported
- ✅ HTTP/1.1 101 Switching Protocols for WebSocket connections
- ✅ All WebSocket endpoints accessible through tunnel

### Monitoring
- Monitor WebSocket connection success rates
- Track SSL/TLS certificate validity
- Verify HSTS header presence
- Test WebSocket endpoints regularly

---

## Documentation

### Configuration Changes
All configuration changes should be documented with:
- Timestamp of changes
- Specific settings modified
- Before/after values
- Test results
- Verification commands used

### Test Results
Document test results including:
- WebSocket endpoint test results
- SSL/TLS verification results
- Certificate information
- Performance metrics
- Error logs (if any)

---

## Automation Script

The Phase 2 configuration can be automated using:
```bash
python scripts/phase2_cloudflare_websocket_configuration.py
```

This script will:
1. Generate Cloudflare Dashboard instructions
2. Test current WebSocket status
3. Verify SSL/TLS configuration
4. Generate test commands
5. Create comprehensive documentation

---

## Next Steps

After completing Phase 2 configuration:

1. **Verify Configuration:** Run all test commands to ensure proper setup
2. **Monitor Performance:** Track WebSocket connection success rates
3. **Document Results:** Record all configuration changes and test results
4. **Set Up Alerts:** Configure monitoring for WebSocket endpoint health
5. **Regular Testing:** Implement automated testing for WebSocket endpoints

---

## Support

For issues or questions regarding Phase 2 configuration:
- Check Cloudflare Dashboard settings
- Verify tunnel configuration
- Review Observatory server WebSocket handlers
- Consult Cloudflare documentation for WebSocket support