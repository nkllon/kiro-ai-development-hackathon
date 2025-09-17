#!/bin/bash
"""
Beast Mode Setup Script
Creates user-friendly CLI access for Beast Mode system.

TRACE: REQ-RC1-RMDDD-016, REQ-RC1-RDI-016
TEST: tests/rc1/test_setup_script.py
IMPLEMENTATION: User-friendly setup script
"""

set -e

echo "🚀 Setting up Beast Mode CLI..."

# Make the main CLI executable
chmod +x beast-mode

# Create symlink in /usr/local/bin if possible
if command -v sudo >/dev/null 2>&1; then
    echo "📁 Creating system-wide CLI access..."
    if sudo ln -sf "$(pwd)/beast-mode" /usr/local/bin/beast-mode 2>/dev/null; then
        echo "✅ Beast Mode CLI installed system-wide!"
        echo "💡 You can now run 'beast-mode' from anywhere"
    else
        echo "⚠️  Could not install system-wide (permission denied)"
        echo "💡 You can still run './beast-mode' from this directory"
    fi
else
    echo "⚠️  sudo not available, skipping system-wide installation"
    echo "💡 You can run './beast-mode' from this directory"
fi

# Test the CLI
echo "🧪 Testing Beast Mode CLI..."
if ./beast-mode --version >/dev/null 2>&1; then
    echo "✅ Beast Mode CLI is working correctly!"
else
    echo "❌ Beast Mode CLI test failed"
    exit 1
fi

echo ""
echo "🎯 Beast Mode Setup Complete!"
echo ""
echo "Usage:"
echo "  ./beast-mode --help          # Show help"
echo "  ./beast-mode status          # Show system status"
echo "  ./beast-mode diagnose all    # Diagnose system health"
echo "  ./beast-mode report          # Generate health report"
echo ""
echo "For system-wide access, run: sudo ./setup-beast-mode.sh"
