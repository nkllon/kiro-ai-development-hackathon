# Cloudflare Dashboard WebSocket Configuration Guide

**Date**: 2025-01-27  
**Domain**: observatory.nkllon.com  
**Purpose**: Enable WebSocket support for WebSocket remediation  
**Priority**: CRITICAL  

---

## 🎯 Executive Summary

This guide provides step-by-step instructions to configure Cloudflare Dashboard for WebSocket support on `observatory.nkllon.com`. The current status shows **HTTP/2 404** errors for all WebSocket endpoints, indicating that WebSocket support is not enabled in the Cloudflare Dashboard.

**Current Status**: ❌ **WebSocket endpoints returning HTTP/2 404**  
**Target Status**: ✅ **WebSocket endpoints returning HTTP/1.1 101 Switching Protocols**

---

## 📋 Prerequisites

- Access to Cloudflare Dashboard for `observatory.nkllon.com`
- Admin privileges for the domain
- Understanding of WebSocket protocols and SSL/TLS configuration

---

## 🔧 Step-by-Step Configuration

### **Step 1: Enable WebSocket Support**

**Location**: Cloudflare Dashboard → Network → WebSockets

**Action**:
1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Select domain: `observatory.nkllon.com`
3. Navigate to **Network** → **WebSockets**
4. Toggle **WebSocket support** to **ON**

**Expected Result**: WebSocket upgrade requests will be proxied correctly through Cloudflare

**Verification Command**:
```bash
curl -I -N -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' -H 'Sec-WebSocket-Version: 13' https://observatory.nkllon.com/ws/emoji-rain
```

**Expected Response**: `HTTP/1.1 101 Switching Protocols`

---

### **Step 2: Configure SSL/TLS Mode**

**Location**: Cloudflare Dashboard → SSL/TLS → Overview

**Action**:
1. Navigate to **SSL/TLS** → **Overview**
2. Set **Encryption mode** to **Full (strict)**

**Expected Result**: End-to-end encryption with proper certificate validation

**Verification Command**:
```bash
curl -I https://observatory.nkllon.com
```

**Expected Response**: `HTTP/2 200` with secure connection

---

### **Step 3: Set Minimum TLS Version**

**Location**: Cloudflare Dashboard → SSL/TLS → Edge Certificates

**Action**:
1. Navigate to **SSL/TLS** → **Edge Certificates**
2. Scroll to **TLS Version**
3. Set **Minimum TLS version** to **TLS 1.2** or higher

**Expected Result**: Only secure TLS versions are accepted for connections

**Verification Command**:
```bash
openssl s_client -connect observatory.nkllon.com:443 -tls1_2
```

**Expected Response**: `Verify return code: 0 (ok)`

---

### **Step 4: Enable HTTP Strict Transport Security (HSTS)**

**Location**: Cloudflare Dashboard → SSL/TLS → Edge Certificates

**Action**:
1. Navigate to **SSL/TLS** → **Edge Certificates**
2. Scroll to **HTTP Strict Transport Security (HSTS)**
3. Click **Enable HSTS**
4. Set **Max Age** to `31536000` (1 year)
5. Enable **Include SubDomains** (recommended)
6. Enable **Preload** (recommended)

**Expected Result**: Browser will enforce HTTPS connections for the domain

**Verification**: Check browser developer tools for HSTS headers

---

### **Step 5: Configure Bot Protection**

**Location**: Cloudflare Dashboard → Security → Bot Fight Mode

**Action**:
1. Navigate to **Security** → **Bot Fight Mode**
2. Ensure bot protection is configured to allow WebSocket connections
3. Review any custom rules that might block WebSocket upgrade requests

**Expected Result**: Bot protection without blocking legitimate WebSocket connections

**Verification**: WebSocket connections should not be blocked by bot protection

---

## 🧪 Comprehensive Testing

### **Test All WebSocket Endpoints**

After completing the configuration, test all 4 WebSocket endpoints:

```bash
# Test emoji-rain endpoint
curl -I -N -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' -H 'Sec-WebSocket-Version: 13' https://observatory.nkllon.com/ws/emoji-rain

# Test observatory endpoint
curl -I -N -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' -H 'Sec-WebSocket-Version: 13' https://observatory.nkllon.com/ws/observatory

# Test anomalies endpoint
curl -I -N -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' -H 'Sec-WebSocket-Version: 13' https://observatory.nkllon.com/ws/anomalies

# Test doctor-status endpoint
curl -I -N -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' -H 'Sec-WebSocket-Version: 13' https://observatory.nkllon.com/ws/doctor-status
```

### **Expected Results**

All endpoints should return:
```
HTTP/1.1 101 Switching Protocols
```

### **Automated Testing Script**

Run the comprehensive test script:
```bash
python3 scripts/cloudflare_dashboard_websocket_configuration.py
```

---

## 📊 Success Criteria

### **Primary Success Criteria**
- [ ] All 4 WebSocket endpoints return `HTTP/1.1 101 Switching Protocols`
- [ ] WebSocket connections establish successfully
- [ ] SSL/TLS mode set to Full (strict)
- [ ] HSTS enabled with appropriate max-age
- [ ] TLS 1.2+ supported

### **Secondary Success Criteria**
- [ ] Bot protection configured correctly
- [ ] Performance metrics within acceptable ranges
- [ ] No security warnings or errors
- [ ] Monitoring and alerting configured

---

## 🚨 Troubleshooting

### **Common Issues**

**Issue**: WebSocket endpoints still returning HTTP/2 404
**Solution**: 
1. Verify WebSocket support is enabled in Network → WebSockets
2. Check for any custom Page Rules blocking WebSocket traffic
3. Ensure tunnel configuration is correct

**Issue**: SSL/TLS errors
**Solution**:
1. Verify SSL/TLS mode is set to Full (strict)
2. Check certificate validity and chain
3. Ensure minimum TLS version is 1.2+

**Issue**: Bot protection blocking WebSocket connections
**Solution**:
1. Review Bot Fight Mode settings
2. Create custom rules to allow WebSocket upgrade requests
3. Whitelist WebSocket endpoints if necessary

### **Verification Commands**

```bash
# Test WebSocket upgrade
curl -I -N -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' -H 'Sec-WebSocket-Version: 13' https://observatory.nkllon.com/ws/emoji-rain

# Test SSL/TLS
curl -I https://observatory.nkllon.com
openssl s_client -connect observatory.nkllon.com:443 -tls1_2

# Test tunnel connectivity
curl -I http://localhost:8888/health
```

---

## 📋 Configuration Checklist

- [ ] **Step 1**: Enable WebSocket support (Network → WebSockets)
- [ ] **Step 2**: Set SSL/TLS mode to Full (strict)
- [ ] **Step 3**: Set minimum TLS version to 1.2+
- [ ] **Step 4**: Enable HSTS with appropriate settings
- [ ] **Step 5**: Configure bot protection
- [ ] **Testing**: Verify all 4 WebSocket endpoints
- [ ] **Validation**: Run comprehensive test script
- [ ] **Documentation**: Update configuration records

---

## 🎯 Next Steps

After successful configuration:

1. **Monitor Performance**: Track WebSocket connection success rates
2. **Set Up Alerts**: Configure monitoring for WebSocket endpoint health
3. **Document Results**: Record all configuration changes and test results
4. **Schedule Regular Reviews**: Plan periodic configuration audits

---

## 📞 Support

If you encounter issues during configuration:

1. Check Cloudflare documentation for WebSocket support
2. Review tunnel configuration and logs
3. Test with simplified WebSocket clients
4. Contact Cloudflare support if needed

---

**Configuration Status**: ⏳ **PENDING IMPLEMENTATION**  
**Target Completion**: Immediate  
**Success Criteria**: All WebSocket endpoints returning HTTP/1.1 101 Switching Protocols