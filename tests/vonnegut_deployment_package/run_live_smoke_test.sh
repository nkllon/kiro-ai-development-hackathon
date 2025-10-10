#!/bin/bash

# Live Smoke Test Runner
# Demonstrates how to run live smoke tests with real API credentials

echo "🔥 LIVE SMOKE TEST SETUP"
echo "=========================="

# Check if credentials are already set
if [ -n ""OPENAI_API_KE"Y" ] || [ -n ""ANTHROPIC_API_KE"Y" ]; then
	echo "✅ API credentials found in environment"
	echo "🔑 OpenAI API Key: ${OPENAI_API_KEY:+SET}"
	echo "🔑 Anthropic API Key: ${ANTHROPIC_API_KEY:+SET}"
else
	echo "❌ No API credentials found in environment"
	echo ""
	echo "To run live smoke tests, you need to set one of:"
	echo ""
	echo "Option 1: Set OpenAI API Key"
	echo "  export OPENAI_API_KEY='your-openai-api-key-here'"
	echo ""
	echo "Option 2: Set Anthropic API Key"
	echo "  export ANTHROPIC_API_KEY='your-anthropic-api-key-here'"
	echo ""
	echo "Option 3: Create a .env file with:"
	echo "  OPENAI_API_KEY=your-openai-api-key-here"
	echo "  # or"
	echo "  ANTHROPIC_API_KEY=your-anthropic-api-key-here"
	echo ""
	echo "Then source it:"
	echo "  source .env"
	echo ""
	echo "Option 4: Run with inline credentials (not recommended for production):"
	echo "  OPENAI_API_KEY='your-key' python live_smoke_test.py"
	echo ""
fi

echo ""
echo "🧪 Running tests..."

# Run the live smoke test
python live_smoke_test.py

echo ""
echo "📊 Test Results:"
echo "- If you see '✅ Live LLM generated X questions', the live test worked!"
echo "- If you see '⚠️ Live LLM failed', check your API credentials"
echo "- If you see '❌ NOT SET', you need to set API credentials"
echo ""
echo "🎯 Next Steps:"
echo "1. Set your API credentials (see options above)"
echo "2. Run: python live_smoke_test.py"
echo "3. Check the output for real LLM responses"
echo "4. Compare our orchestrator vs live LLM results"
