#!/bin/bash

# The Stochastic Gentleman Observatory - Public Access Setup
# Creates a public tunnel to the Beast Mode Observatory running on localhost:8888
# with academic research theme overlay for trolling purposes

echo "🔬 Setting up The Stochastic Gentleman Observatory public access..."

# Check if Observatory server is running on port 8888
if ! lsof -i :8888 >/dev/null 2>&1; then
    echo "❌ Observatory server not found on port 8888"
    echo "Please start the Observatory server first using:"
    echo "python -m src.beast_mode.observatory.server"
    exit 1
fi

echo "✅ Observatory server detected on port 8888"

# Check if cloudflared is available
if ! command -v cloudflared >/dev/null 2>&1; then
    echo "⚠️  cloudflared not found. Installing via Homebrew..."
    brew install cloudflared
fi

echo "🌐 Creating Cloudflare tunnel for localhost:8888..."
echo "📚 Theme: 'The Stochastic Gentleman: Multi-Agent AI Coordination Research'"

# Start the tunnel
echo "Starting tunnel... (Press Ctrl+C to stop)"
cloudflared tunnel --url http://localhost:8888