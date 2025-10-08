#!/bin/bash

# Live Smoke Test with Direct 1Password Integration
# Uses specific item IDs we found in your 1Password vault

echo "🔐 LIVE SMOKE TEST WITH DIRECT 1PASSWORD"
echo "========================================="

# Check if 1Password CLI is available
if ! command -v op &>/dev/null; then
	echo "❌ 1Password CLI not found. Please install it first:"
	echo "   https://1password.com/downloads/command-line/"
	exit 1
fi

# Check if user is signed in to 1Password
if ! op account list &>/dev/null; then
	echo "❌ Not signed in to 1Password CLI"
	echo "Please run: op signin"
	exit 1
fi

echo "✅ 1Password CLI available and signed in"

# Try to get Anthropic API key - look for standard env var names
echo ""
echo "🔑 Looking for Anthropic API key..."
ANTHROPIC_API_KEY=""

# Define a whitelist of allowed item names for security
allowed_anthropic_items=("ANTHROPIC_API_KEY" "Anthropic Cursor AI" "Anthropic API Key"
	"Anthropic" "Claude API Key")
for item_name in "${allowed_anthropic_items[@]}"; do
	echo "  Trying: "item_nam"e"
	# Try different field names (whitelist approach for security)
	for field_name in "credential" "api key" "password" "key" "secret"; do
		# Use field_name directly since it's from a hardcoded whitelist
		if
			credential=$(op item get ""item_nam"e" --fields ""field_nam"e" --reveal 2>/dev/null)
			[ -n ""credentia"l" ]
		then
			echo "  ✅ Found Anthropic API key in '"item_name"' field '"field_name"'"
			ANTHROPIC_API_KEY=""credentia"l"
			export ANTHROPIC_API_KEY
			break 2
		fi
	done
done

if [ -z ""ANTHROPIC_API_KE"Y" ]; then
	echo "❌ Could not find Anthropic API key"
fi

# Try to get OpenAI API key - look for standard env var names
echo ""
echo "🔑 Looking for OpenAI API key..."
OPENAI_API_KEY=""

# Define a whitelist of allowed item names for security
allowed_openai_items=("OPENAI_API_KEY" "OpenAI API Key" "OpenAI" "GPT API Key")
for item_name in "${allowed_openai_items[@]}"; do
	echo "  Trying: "item_nam"e"
	# Try different field names (whitelist approach for security)
	for field_name in "credential" "api key" "password" "key" "secret"; do
		# Use field_name directly since it's from a hardcoded whitelist
		if
			credential=$(op item get ""item_nam"e" --fields ""field_nam"e" --reveal 2>/dev/null)
			[ -n ""credentia"l" ]
		then
			echo "  ✅ Found OpenAI API key in '"item_name"' field '"field_name"'"
			OPENAI_API_KEY=""credentia"l"
			export OPENAI_API_KEY
			break 2
		fi
	done
done

if [ -z ""OPENAI_API_KE"Y" ]; then
	echo "❌ Could not find OpenAI API key"
fi

# Check if we have any credentials
if [ -z ""OPENAI_API_KE"Y" ] && [ -z ""ANTHROPIC_API_KE"Y" ]; then
	echo ""
	echo "❌ No API credentials found in 1Password"
	echo ""
	echo "Found items in your vault:"
	echo "  - Anthropic Cursor AI (API credential)"
	echo "  - Openai (login item)"
	echo "  - Claude (login item)"
	echo ""
	echo "To add API keys to 1Password:"
	echo "  op item create --category=api-credential --title='OpenAI API Key'"
	exit 1
fi

echo ""
echo "🎯 Credentials Status:"
echo "   OpenAI API Key: ${OPENAI_API_KEY:+✅ SET}"
echo "   Anthropic API Key: ${ANTHROPIC_API_KEY:+✅ SET}"

echo ""
echo "🧪 Running live smoke test with 1Password credentials..."
echo ""

# Run the live smoke test with LangChain
python live_smoke_test_langchain.py

echo ""
echo "📊 Test completed!"
echo ""
echo "💡 If you want to add more API keys:"
echo "  1. Create them in 1Password as API Credentials"
echo "  2. Use descriptive names like 'OpenAI API Key'"
echo "  3. Put the key in the 'credential' field"
