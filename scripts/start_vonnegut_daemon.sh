#!/bin/bash
# Script to start monitoring daemon on Vonnegut

echo "🚀 Starting monitoring daemon on Vonnegut..."

# Start the daemon in the background on Vonnegut
ssh vonnegut "cd /home/lou/beast-mode/monitoring-daemon && nohup python3 -m src.beast_mode.monitoring.daemon --start --port 8000 > daemon.log 2>&1 &"

echo "✅ Daemon started on Vonnegut"
echo "📊 Metrics should be available at: http://vonnegut:8000/metrics"
echo ""
echo "To check status:"
echo "  ssh vonnegut 'ps aux | grep daemon'"
echo ""
echo "To view logs:"
echo "  ssh vonnegut 'tail -f /home/lou/beast-mode/monitoring-daemon/daemon.log'"
echo ""
echo "To test metrics:"
echo "  curl http://vonnegut:8000/metrics"