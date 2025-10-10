#!/bin/bash

# Deploy Beast Mode Framework in Production Mode
# This mode is for developers USING the Beast Mode framework

set -e

echo "🚀 Deploying Beast Mode Framework - Production Mode"
echo "=================================================="

# Set environment
export BEAST_MODE_ENV=production
export KIRO_STEERING_MODE=production

echo "📋 Production Mode Configuration:"
echo "   - Target Audience: Framework Users"
echo "   - Steering Files: .kiro/steering/ only"
echo "   - Purpose: Guide AI assistants to use Beast Mode correctly"
echo ""

# Validate production steering files exist
echo "✅ Validating production steering files..."

required_files=(
    ".kiro/steering/security-credentials-governance.md"
    ".kiro/steering/beast-mode-framework-patterns.md"
    ".kiro/steering/mathematical-governance-principle.md"
    ".kiro/steering/quality-first-development.md"
    ".kiro/steering/ai-memory-palace-usage.md"
)

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "   ✅ $file"
    else
        echo "   ❌ Missing: $file"
        exit 1
    fi
done

echo ""
echo "📊 Production Steering Files Summary:"
echo "   - Security: Credentials governance and best practices"
echo "   - Framework: ReflectiveModule patterns and Beast Mode usage"
echo "   - Mathematics: DAG orchestration and constraint validation"
echo "   - Quality: Testing patterns and systematic validation"
echo "   - AI Memory: Persistent context management patterns"

echo ""
echo "🎯 Production Mode Active!"
echo ""
echo "Framework users will receive guidance on:"
echo "   • How to use ReflectiveModule for instant production readiness"
echo "   • DAG orchestration for mathematical task dependencies"
echo "   • AI Memory Palace for persistent context across sessions"
echo "   • Quality-first development with >90% test coverage"
echo "   • Security best practices with zero hardcoded credentials"

echo ""
echo "📚 Next Steps for Framework Users:"
echo "   1. Read the README.md for quick start guide"
echo "   2. Try examples/simple_beast_agent.py"
echo "   3. Explore Jupyter notebooks in examples/notebooks/"
echo "   4. Follow the systematic patterns in steering files"

echo ""
echo "✅ Production deployment complete!"
echo "   Environment: $BEAST_MODE_ENV"
echo "   Steering Mode: $KIRO_STEERING_MODE"