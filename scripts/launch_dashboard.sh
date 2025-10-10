#!/bin/bash
#
# Launch Kiro Admin Dashboard
# ==========================
#
# Starts the modern web-based admin dashboard to replace make target chaos

echo "🚀 Launching Kiro Admin Dashboard..."
echo "📱 Mobile-responsive design included"
echo "🔄 Real-time updates via WebSocket"
echo "🌐 Access at: http://localhost:8889"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the dashboard
python scripts/admin_dashboard.py --host 0.0.0.0 --port 8889