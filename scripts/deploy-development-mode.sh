#!/bin/bash

# Deploy Beast Mode Framework in Development Mode
# This mode is for developers WORKING ON the Beast Mode framework itself

set -e

echo "🔧 Deploying Beast Mode Framework - Development Mode"
echo "===================================================="

# Set environment
export BEAST_MODE_ENV=development
export KIRO_STEERING_MODE=development

echo "📋 Development Mode Configuration:"
echo "   - Target Audience: Framework Developers"
echo "   - Steering Files: .kiro/steering/ + .kiro/steering-dev/"
echo "   - Purpose: Guide development OF the Beast Mode framework"
echo ""

# Validate development steering directory exists
if [[ ! -d ".kiro/steering-dev" ]]; then
    echo "📁 Creating development steering directory..."
    mkdir -p .kiro/steering-dev
fi

# Check if we need to recover archived development steering files
echo "🔍 Checking for archived development steering files..."

archived_steering_dir="archive/development/vonnegut_deployment_package/steering"
if [[ -d "$archived_steering_dir" ]]; then
    echo "   📦 Found archived steering files"
    
    # List available archived files
    echo "   Available archived files:"
    for file in "$archived_steering_dir"/*.md; do
        if [[ -f "$file" ]]; then
            basename_file=$(basename "$file")
            echo "      - $basename_file"
        fi
    done
    
    echo ""
    read -p "   🤔 Copy archived development steering files? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "   📋 Copying archived development steering files..."
        cp "$archived_steering_dir"/*.md .kiro/steering-dev/ 2>/dev/null || true
        echo "   ✅ Archived files copied to .kiro/steering-dev/"
    fi
else
    echo "   ℹ️  No archived steering files found"
fi

# Create essential development steering files if they don't exist
echo ""
echo "📝 Ensuring essential development steering files exist..."

dev_files=(
    "systematic-development-governance.md"
    "hounds-protocol-implementation.md"
    "infrastructure-first-implementation.md"
)

for file in "${dev_files[@]}"; do
    if [[ ! -f ".kiro/steering-dev/$file" ]]; then
        echo "   📄 Creating template: $file"
        cat > ".kiro/steering-dev/$file" << EOF
---
inclusion: manual
---

# $(echo "$file" | sed 's/-/ /g' | sed 's/.md//' | sed 's/\b\w/\U&/g')

## Core Principle

**"This is a development steering file for Beast Mode framework development."**

## Purpose

This file guides development of the Beast Mode framework itself, not usage of the framework.

## TODO

- Define specific development patterns
- Add implementation guidelines
- Include quality standards
- Document architecture decisions

---

**This is a development steering file - edit as needed for framework development.**
EOF
    else
        echo "   ✅ $file exists"
    fi
done

echo ""
echo "📊 Development Mode Steering Summary:"
echo ""
echo "Production Steering (.kiro/steering/):"
echo "   - For framework USERS"
echo "   - Guides how to USE Beast Mode patterns"
echo "   - Always active in both modes"
echo ""
echo "Development Steering (.kiro/steering-dev/):"
echo "   - For framework DEVELOPERS"
echo "   - Guides how to BUILD Beast Mode framework"
echo "   - Only active in development mode"

echo ""
echo "🎯 Development Mode Active!"
echo ""
echo "Framework developers will receive guidance on:"
echo "   • Systematic development methodology"
echo "   • Hounds protocol implementation patterns"
echo "   • Infrastructure-first architecture"
echo "   • Internal quality standards"
echo "   • Development observability patterns"

echo ""
echo "🔧 Development Tools Available:"
echo "   • All production steering (for testing framework usage)"
echo "   • Development-specific steering files"
echo "   • Access to archived development patterns"
echo "   • Internal development workflows"

echo ""
echo "📚 Next Steps for Framework Developers:"
echo "   1. Review .kiro/steering-dev/README.md"
echo "   2. Check development steering files in .kiro/steering-dev/"
echo "   3. Use both production and dev steering for comprehensive guidance"
echo "   4. Follow systematic development patterns"

echo ""
echo "✅ Development deployment complete!"
echo "   Environment: $BEAST_MODE_ENV"
echo "   Steering Mode: $KIRO_STEERING_MODE"
echo "   Production Steering: Active"
echo "   Development Steering: Active"