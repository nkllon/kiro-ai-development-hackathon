#!/bin/bash

echo "🔐 Google Calendar MCP - Credential Setup"
echo "========================================"

echo "1. In Google Cloud Console (opening now):"
echo "   - Create a new project or select existing"
echo "   - Go to 'APIs & Services' > 'Library'"
echo "   - Search for 'Google Calendar API' and enable it"
echo ""

echo "2. Create OAuth credentials:"
echo "   - Go to 'APIs & Services' > 'Credentials'"
echo "   - Click '+ CREATE CREDENTIALS' > 'OAuth client ID'"
echo "   - Choose 'Desktop application'"
echo "   - Name it 'Kiro Calendar MCP'"
echo "   - Download the JSON file"
echo ""

echo "3. Save the downloaded file as:"
echo "   docker/google-calendar-mcp/credentials/gcp-oauth.keys.json"
echo ""

echo "4. Then run: docker-compose restart"
echo ""

read -p "Press Enter when you've downloaded the credentials file..."

if [ -f "credentials/gcp-oauth.keys.json" ]; then
    echo "✅ Credentials file found!"
    chmod 600 credentials/gcp-oauth.keys.json
    echo "✅ Permissions set to 600"
    
    echo "🚀 Restarting MCP server with real credentials..."
    docker-compose restart google-calendar-mcp
    
    echo "✅ Done! The MCP server should now authenticate with your Google Calendar."
    echo "Visit http://localhost:3003 to complete OAuth flow."
else
    echo "❌ Credentials file not found. Please download it to credentials/gcp-oauth.keys.json"
fi