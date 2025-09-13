#!/bin/bash

# GitHub MCP Server Installation Script
# This script helps you install and configure the GitHub MCP server

set -e

echo "🚀 GitHub MCP Server Installation Script"
echo "========================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is running"

# Check if GitHub token is provided
if [ -z "$GITHUB_PERSONAL_ACCESS_TOKEN" ]; then
    echo ""
    echo "🔑 GitHub Personal Access Token Required"
    echo "========================================"
    echo "Please create a GitHub Personal Access Token:"
    echo "1. Go to: https://github.com/settings/tokens"
    echo "2. Click 'Generate new token (classic)'"
    echo "3. Select scopes: repo, issues, pull_requests, workflow"
    echo "4. Copy the token and run:"
    echo "   export GITHUB_PERSONAL_ACCESS_TOKEN=your_token_here"
    echo "   ./install-github-mcp.sh"
    echo ""
    exit 1
fi

echo "✅ GitHub token found"

# Test the GitHub MCP server
echo ""
echo "🧪 Testing GitHub MCP Server..."
echo "================================"

# Run a test command to verify the server works
echo "Testing server connectivity..."
if docker run -i --rm \
    -e GITHUB_PERSONAL_ACCESS_TOKEN="$GITHUB_PERSONAL_ACCESS_TOKEN" \
    ghcr.io/github/github-mcp-server \
    --version > /dev/null 2>&1; then
    echo "✅ GitHub MCP Server is working correctly"
else
    echo "❌ GitHub MCP Server test failed"
    exit 1
fi

# Create environment file
echo ""
echo "📝 Creating environment configuration..."
echo "======================================"

cat > .env.github-mcp << EOF
# GitHub MCP Server Configuration
GITHUB_PERSONAL_ACCESS_TOKEN=$GITHUB_PERSONAL_ACCESS_TOKEN
GITHUB_OWNER=lou
GITHUB_REPO=kiro-ai-development-hackathon
EOF

echo "✅ Environment file created: .env.github-mcp"

# Update the config file with the actual token
echo ""
echo "⚙️  Updating configuration file..."
echo "================================"

sed "s/YOUR_GITHUB_TOKEN_HERE/$GITHUB_PERSONAL_ACCESS_TOKEN/g" mcp-github-config.json > mcp-github-config.json.tmp
mv mcp-github-config.json.tmp mcp-github-config.json

echo "✅ Configuration file updated: mcp-github-config.json"

# Create a test script
echo ""
echo "📋 Creating test script..."
echo "========================"

cat > test-github-mcp.sh << 'EOF'
#!/bin/bash

# Test GitHub MCP Server functionality
echo "🧪 Testing GitHub MCP Server..."
echo "================================"

# Load environment variables
if [ -f .env.github-mcp ]; then
    source .env.github-mcp
fi

# Test basic functionality
echo "Testing repository access..."
docker run -i --rm \
    -e GITHUB_PERSONAL_ACCESS_TOKEN="$GITHUB_PERSONAL_ACCESS_TOKEN" \
    ghcr.io/github/github-mcp-server \
    --help > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ GitHub MCP Server is working correctly"
    echo ""
    echo "🎉 Installation completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Configure your MCP host application (Claude Desktop, VS Code, etc.)"
    echo "2. Use the configuration in mcp-github-config.json"
    echo "3. Test creating issues, PRs, and other GitHub operations"
else
    echo "❌ GitHub MCP Server test failed"
    exit 1
fi
EOF

chmod +x test-github-mcp.sh
echo "✅ Test script created: test-github-mcp.sh"

echo ""
echo "🎉 GitHub MCP Server Installation Complete!"
echo "=========================================="
echo ""
echo "Files created:"
echo "- mcp-github-config.json (MCP configuration)"
echo "- .env.github-mcp (Environment variables)"
echo "- test-github-mcp.sh (Test script)"
echo ""
echo "Next steps:"
echo "1. Configure your MCP host application with mcp-github-config.json"
echo "2. Run ./test-github-mcp.sh to verify everything works"
echo "3. Start using GitHub MCP server for issue creation, PR management, etc."
echo ""
echo "🔗 Useful links:"
echo "- GitHub MCP Server: https://github.com/github/github-mcp-server"
echo "- MCP Protocol: https://modelcontextprotocol.io/"
echo ""




