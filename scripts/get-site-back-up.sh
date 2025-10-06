#!/bin/bash
echo "🚨 Getting Beast Mode Observatory back online..."

# Kill all tunnel processes
pkill -f cloudflared
sleep 2

# Start a new quick tunnel and capture the URL
echo "🚀 Starting emergency tunnel..."
cloudflared tunnel --url localhost:8888 2>&1 | tee tunnel_output.log &

# Wait for tunnel to establish and show URL
sleep 10
echo "📋 Tunnel output:"
grep -E "https://.*\.trycloudflare\.com" tunnel_output.log | tail -1

echo ""
echo "✅ Emergency tunnel is running"
echo "🔗 Use the URL above to access the Observatory"
echo "🛑 Press Ctrl+C to stop when ready"

# Keep running
wait