#!/bin/bash

# Claude-Simone Framework Launch Script
# This script launches Claude Code in IDE mode with the Simone framework configuration

set -e

echo "🚀 Claude-Simone Framework Launch Script"
echo "======================================="

# Check if Claude Code is installed
if ! command -v claude &> /dev/null; then
    echo "❌ Claude Code CLI is not installed."
    echo "Please run: npm install -g @anthropic-ai/claude-code"
    exit 1
fi

echo "✅ Claude Code CLI found: $(claude --version)"

# Check if we're in the right directory
if [ ! -f "simone-interface-consolidation.md" ]; then
    echo "❌ Simone framework configuration not found."
    echo "Please run this script from the project root directory."
    exit 1
fi

echo "✅ Simone framework configuration found"

# Check if Cursor is running
if ! pgrep -f "Cursor" > /dev/null; then
    echo "⚠️  Cursor is not running. Please start Cursor and open this project."
    echo "Then run this script again."
    exit 1
fi

echo "✅ Cursor is running"

# Create the Claude terminal launch command
echo ""
echo "🎯 Launching Claude Code in IDE mode..."
echo "======================================"
echo ""
echo "Instructions:"
echo "1. Claude will start in IDE mode and connect to your Cursor workspace"
echo "2. You'll be prompted to authorize with your Anthropic API key"
echo "3. Once connected, provide the Simone framework specification as context"
echo "4. Use the following prompt to start the interface consolidation work:"
echo ""
echo "--- COPY THIS PROMPT ---"
echo ""
cat << 'EOF'
I'm working on resolving a critical interface duplication crisis in this codebase. Please review the Simone framework specification in `simone-interface-consolidation.md` and begin with Task 1: Interface Audit and Inventory.

The project has:
- 48+ duplicate interface classes across 11+ files
- 0.00 consistency score indicating complete conflicts
- Multiple "authoritative" sources claiming single source of truth

Please start by:
1. Reading the Simone framework specification
2. Analyzing the current interface duplication situation
3. Running the existing consolidation tools
4. Creating a comprehensive interface inventory

Use the existing tools in `src/rm_ddd/core/` for analysis and consolidation.
EOF
echo ""
echo "--- END PROMPT ---"
echo ""
echo "Press Enter to launch Claude Code in IDE mode..."
read -r

# Launch Claude Code in IDE mode
echo "🚀 Starting Claude Code in IDE mode..."
claude /ide




