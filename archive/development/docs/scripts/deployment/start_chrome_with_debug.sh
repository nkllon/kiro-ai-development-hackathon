set -euo pipefail#!/bin/bash
# Start Chrome with debugging enabled for automation

echo "🔧 Starting Chrome with debugging enabled..."
echo "🔐 This will preserve all your extensions including 1Password"

# Kill any existing Chrome debug instances
pkill -f "remote-debugging-port"

# Start Chrome with debugging
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/Library/Application Support/Google/Chrome" \
  --no-first-run \
  --no-default-browser-check &

echo "✅ Chrome started with debugging on port 9222"
echo "🔗 You can now run: uv run python step_navigator.py"
echo "📱 All your extensions (including 1Password) will be available"
