#!/bin/bash

# Live Smoke Test with 1Password Integration
# Pulls API credentials from 1Password and runs live smoke tests

echo "🔐 LIVE SMOKE TEST WITH 1PASSWORD"
echo "=================================="

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

# Function to get credential from 1Password
get_1password_credential() {
	local item_name="$1"
	local field_name="$2"

	echo "🔍 Looking for '"item_name"' in 1Password..."

	# Try to get the item
	if op item get ""item_nam"e" --fields ""field_nam"e" 2>/dev/null; then
		return 0
	else
		echo "❌ Could not find '"item_name"' with field '"field_name"'"
		return 1
	fi
}

# Try to get OpenAI API key
echo ""
echo "🔑 Attempting to get OpenAI API key from 1Password..."
OPENAI_API_KEY=$(get_1password_credential "OpenAI API Key" "credential")
if [ $? -eq 0 ]; then
	echo "✅ Found OpenAI API key in 1Password"
	export OPENAI_API_KEY
else
	echo "⚠️ OpenAI API key not found in 1Password"
	echo "   Looking for item named 'OpenAI API Key' with field 'credential'"
fi

# Try to get Anthropic API key
echo ""
echo "🔑 Attempting to get Anthropic API key from 1Password..."
ANTHROPIC_API_KEY=$(get_1password_credential "Anthropic API Key" "credential")
if [ $? -eq 0 ]; then
	echo "✅ Found Anthropic API key in 1Password"
	export ANTHROPIC_API_KEY
else
	echo "⚠️ Anthropic API key not found in 1Password"
	echo "   Looking for item named 'Anthropic API Key' with field 'credential'"
fi

# Check if we have any credentials
if [ -z ""OPENAI_API_KE"Y" ] && [ -z ""ANTHROPIC_API_KE"Y" ]; then
	echo ""
	echo "❌ No API credentials found in 1Password"
	echo ""
	echo "Expected 1Password items:"
	echo "  - Item: 'OpenAI API Key' with field: 'credential'"
	echo "  - Item: 'Anthropic API Key' with field: 'credential'"
	echo ""
	echo "Alternative field names to try:"
	echo "  - 'password'"
	echo "  - 'api_key'"
	echo "  - 'key'"
	echo ""
	echo "To list available items:"
	echo "  op item list"
	echo ""
	echo "To see item details:"
	echo "  op item get 'Item Name'"
	exit 1
fi

echo ""
echo "🎯 Credentials Status:"
echo "   OpenAI API Key: ${OPENAI_API_KEY:+✅ SET}"
echo "   Anthropic API Key: ${ANTHROPIC_API_KEY:+✅ SET}"

echo ""
echo "🧪 Running live smoke test with 1Password credentials..."
echo ""

# Run the live smoke test
python live_smoke_test.py

echo ""
echo "📊 Test completed!"
echo ""
echo "💡 Tips:"
echo "  - If credentials are in different field names, update the script"
echo "  - If items have different names, update the script"
echo "  - Run 'op item list' to see available items"
echo "  - Run 'op item get \"Item Name\"' to see item structure"
