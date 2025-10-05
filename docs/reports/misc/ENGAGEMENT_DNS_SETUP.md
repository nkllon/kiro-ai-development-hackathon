# Engagement Server DNS Setup Guide

## Quick Answer: No Certificate Regeneration Needed! ✅

**Cloudflare tunnels use wildcard certificates that automatically cover all subdomains.** You just need to add a DNS record.

## Option 1: Cloudflare API (Automated) 🤖

### Prerequisites
You'll need:
- **Cloudflare API Token** with Zone:Edit permissions for nkllon.com
- **Zone ID** for nkllon.com (found in Cloudflare dashboard)

### Setup API Credentials
```bash
# Get API token from: https://dash.cloudflare.com/profile/api-tokens
export CLOUDFLARE_API_TOKEN="your_token_here"

# Get Zone ID from Cloudflare dashboard for nkllon.com
export CLOUDFLARE_ZONE_ID="your_zone_id_here"
```

### Run the Script
```bash
python scripts/add_engagement_dns.py
```

The script will:
1. ✅ Copy the target from existing `observatory.nkllon.com` record
2. ✅ Create `engagement.observatory.nkllon.com` CNAME record
3. ✅ Enable Cloudflare proxy (orange cloud)
4. ✅ Test DNS propagation
5. ✅ Verify endpoint accessibility

## Option 2: Cloudflare Dashboard (Manual) 🖱️

### Steps
1. **Go to Cloudflare Dashboard**: https://dash.cloudflare.com/
2. **Select nkllon.com domain**
3. **Go to DNS > Records**
4. **Click "Add record"**
5. **Configure the record**:
   - **Type**: CNAME
   - **Name**: `engagement.observatory`
   - **Target**: `observatory.nkllon.com` (or copy from existing record)
   - **Proxy status**: ✅ Proxied (orange cloud)
   - **TTL**: Auto
6. **Click "Save"**

## Current DNS Records (for reference)

```bash
# Existing working records:
observatory.nkllon.com          -> 104.26.3.137, 172.67.69.149, 104.26.2.137
prometheus.observatory.nkllon.com -> 104.26.3.137, 172.67.69.149, 104.26.2.137
grafana.observatory.nkllon.com    -> 104.26.3.137, 172.67.69.149, 104.26.2.137

# Need to add:
engagement.observatory.nkllon.com -> (same IPs as above)
```

## Why No Certificate Regeneration? 🔒

**Cloudflare Tunnel Certificates are Wildcard**:
- Your tunnel certificate covers `*.observatory.nkllon.com`
- Adding `engagement.observatory.nkllon.com` is automatically covered
- No certificate changes needed in tunnel configuration
- Cloudflare handles SSL termination at the edge

## Verification Steps

### 1. DNS Propagation Check
```bash
dig +short engagement.observatory.nkllon.com
# Should return: 104.26.3.137, 172.67.69.149, 104.26.2.137
```

### 2. Endpoint Health Check
```bash
curl -s https://engagement.observatory.nkllon.com/health
# Should return: {"status":"healthy","service":"engagement-manager","mode":"minimal"}
```

### 3. Tunnel Configuration Check
The engagement server is already configured in `deployment/observatory/cloudflared-config.yml`:
```yaml
- hostname: engagement.observatory.nkllon.com
  service: http://observatory-engagement-manager:8891
```

## Current Status

### ✅ What's Working
- Engagement server container running and healthy
- Cloudflare tunnel configuration includes engagement routing
- Local health endpoint responding: `http://localhost:8891/health`

### ⏳ What's Needed
- DNS record for `engagement.observatory.nkllon.com`
- 2-5 minutes for DNS propagation

### 🎯 Expected Result
After DNS setup:
- `https://engagement.observatory.nkllon.com/health` will work
- Engagement server accessible through Cloudflare tunnel
- No certificate or tunnel configuration changes needed

## Troubleshooting

### If DNS doesn't propagate:
```bash
# Check DNS servers
nslookup engagement.observatory.nkllon.com 8.8.8.8
nslookup engagement.observatory.nkllon.com 1.1.1.1
```

### If endpoint doesn't respond:
```bash
# Check tunnel logs
docker logs observatory-cloudflare-tunnel --tail 20

# Check engagement server logs  
docker logs observatory-engagement-manager --tail 20
```

### If SSL errors occur:
- Cloudflare handles SSL automatically
- Wildcard certificate covers all subdomains
- No manual certificate management needed

---

**Bottom Line**: Just add the DNS record - everything else is already configured! 🚀