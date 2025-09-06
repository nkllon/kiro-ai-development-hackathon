#!/bin/bash
# Cloud Run Local Development - Google's Official Local Emulator
# Uses Functions Framework to run Cloud Run services locally

set -e

echo "🌩️  Cloud Run Local Development Mode"
echo "Using Google Functions Framework for identical Cloud Run behavior"
echo "================================================================"

# Check if Functions Framework is installed
if ! python -c "import functions_framework" &>/dev/null; then
    echo "📦 Installing Functions Framework..."
    pip install functions-framework[gcp]
fi

# Check if we have the required files
if [[ ! -f "src/beast_mode/api/main.py" ]]; then
    echo "❌ FastAPI app not found. Run from project root."
    exit 1
fi

# Create Cloud Run compatible entry point
echo "🔧 Creating Cloud Run compatible entry point..."
cat > /tmp/cloud_run_main.py << 'EOF'
"""
Cloud Run Local Development Entry Point

Wraps FastAPI app for Functions Framework compatibility.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from beast_mode.api.main import app

# Functions Framework expects this signature
def main(request):
    """Cloud Run entry point"""
    return app

# For local development
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
EOF

# Set environment variables (same as Cloud Run)
export PYTHONPATH=$(pwd)
export ENVIRONMENT=development
export LOG_LEVEL=DEBUG
export PORT=8080

echo "🚀 Starting Cloud Run local emulator..."
echo "   URL: http://localhost:8080"
echo "   Behavior: Identical to Cloud Run"
echo "   Scaling: Disabled (single instance)"
echo "   Hot Reload: Enabled"
echo ""
echo "🧪 Test endpoints:"
echo "   curl http://localhost:8080/health"
echo "   curl http://localhost:8080/domains"
echo "   curl http://localhost:8080/intelligence/ghostbusters"
echo ""
echo "Press Ctrl+C to stop"

# Start with Functions Framework (Cloud Run compatible)
functions-framework --target=main --source=/tmp/cloud_run_main.py --port=8080 --debug