#!/bin/bash
# Cloudflare Tunnel Switchover Script
# Switches Observatory traffic from Vonnegut to Poe

set -e

echo "🔄 Observatory Tunnel Switchover"
echo "==============================="

# Backup current config
echo "💾 Backing up current tunnel config..."
cp cloudflared-config.yml cloudflared-config-vonnegut-backup.yml

# Switch to Poe config
echo "🔄 Switching tunnel to Poe..."
cp cloudflared-config-poe.yml cloudflared-config.yml

# Restart tunnel
echo "🔄 Restarting Cloudflare tunnel..."
python scripts/manage_tunnel.py restart

# Wait for tunnel to stabilize
echo "⏳ Waiting for tunnel to stabilize..."
sleep 10

# Test external access
echo "🔍 Testing external access..."
curl -f https://observatory.nkllon.com/health || echo "❌ Health check failed"
curl -f https://grafana.observatory.nkllon.com/ || echo "❌ Grafana check failed"

echo "✅ Tunnel switchover complete!"
echo "🌐 Observatory now running on Poe"
