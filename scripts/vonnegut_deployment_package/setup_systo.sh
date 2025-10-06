#!/bin/bash
# Systo Generator Setup Script

echo "🦾 SYSTO GENERATOR SETUP"
echo "========================"

# Install requirements
echo "📦 Installing Python requirements..."
pip install -r requirements-systo.txt

# Create asset directories
echo "📁 Creating asset directories..."
mkdir -p assets/systo/{source,processed,vectors,exports,brand}

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OpenAI API key not set!"
    echo "Please set your API key:"
    echo "export OPENAI_API_KEY='your-key-here'"
    echo ""
    echo "Then run: python scripts/systo_generator.py"
else
    echo "✅ OpenAI API key found"
    echo "Ready to generate Systo!"
    echo ""
    echo "Run: python scripts/systo_generator.py"
fi

echo ""
echo "🎯 SYSTEMATIC SUPERIORITY AWAITS"