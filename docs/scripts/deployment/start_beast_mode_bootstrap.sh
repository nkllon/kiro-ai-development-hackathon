set -euo pipefail#!/bin/bash
# Beast Mode Network Bootstrap - Single macOS Box Deployment

echo "🧬 Beast Mode Network Bootstrap"
echo "Single Machine Deployment (macOS)"
echo "=================================="

# Check if Redis is running
echo "🔍 Checking Redis status..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is running"
else
    echo "🔧 Starting Redis..."
    brew services start redis
    sleep 2
    
    if redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis started successfully"
    else
        echo "❌ Failed to start Redis"
        exit 1
    fi
fi

# Check Python dependencies
echo "📦 Checking Python dependencies..."
python3 -c "import redis, pydantic" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Python dependencies available"
else
    echo "⚠️  Python dependencies missing"
    echo "   Run: pip install 'redis[hiredis]' pydantic"
fi

echo ""
echo "🧬 Beast Mode Bootstrap Configuration"
echo "===================================="
echo "Redis URL: redis://localhost:6379"
echo "Network Channel: beast_mode_network"
echo "Deployment: Single Machine (macOS)"
echo "Max Agents: 100+"

echo ""
echo "🚀 Ready to Start Beast Mode Network!"
echo "====================================="
echo ""
echo "1. Test the network:"
echo "   python3 simple_pubsub_test.py"
echo ""
echo "2. Start spore distributor (Terminal 1):"
echo "   python3 beast_mode_spore_distributor.py"
echo ""
echo "3. Start spore receiver (Terminal 2):"
echo "   python3 beast_mode_spore_receiver.py"
echo ""
echo "4. Monitor network activity:"
echo "   redis-cli monitor"
echo ""
echo "🧬 All Kiro instances will connect to redis://localhost:6379"
echo "🧬 Each gets unique agent ID automatically"
echo "🧬 Perfect for bootstrap development on single macOS box!"