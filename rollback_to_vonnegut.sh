#!/bin/bash
# Observatory Rollback Script
# Returns Observatory traffic to Vonnegut

set -e

echo "🔙 Observatory Rollback to Vonnegut"
echo "=================================="

# Restore Vonnegut config
echo "🔄 Restoring Vonnegut tunnel config..."
cp cloudflared-config-vonnegut-backup.yml cloudflared-config.yml

# Restart tunnel
echo "🔄 Restarting Cloudflare tunnel..."
python scripts/manage_tunnel.py restart

# Wait for tunnel to stabilize
echo "⏳ Waiting for tunnel to stabilize..."
sleep 10

# Test external access
echo "🔍 Testing external access..."
curl -f https://observatory.nkllon.com/health || echo "❌ Health check failed"

echo "✅ Rollback complete!"
echo "🌐 Observatory back on Vonnegut"
