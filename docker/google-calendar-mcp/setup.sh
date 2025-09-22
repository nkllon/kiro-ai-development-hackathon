#!/bin/bash

# Google Calendar MCP Setup Script
# Beast Mode compliant setup using existing proven MCP server

set -e

echo "🚀 Google Calendar MCP Setup (Beast Mode)"
echo "=========================================="
echo "Using: @cocal/google-calendar-mcp@1.4.9"
echo "Wall Clock: $(date)"
echo ""

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p credentials
mkdir -p monitoring/prometheus
mkdir -p monitoring/grafana/provisioning/datasources
mkdir -p monitoring/grafana/provisioning/dashboards
mkdir -p monitoring/grafana/dashboards

# Create Prometheus configuration
echo "📊 Setting up Prometheus configuration..."
cat > monitoring/prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'google-calendar-mcp'
    static_configs:
      - targets: ['google-calendar-mcp:8080']
    scrape_interval: 5s
    metrics_path: /metrics
EOF

# Create Grafana datasource
echo "📈 Setting up Grafana datasource..."
cat > monitoring/grafana/provisioning/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

# Create Grafana dashboard provisioning
cat > monitoring/grafana/provisioning/dashboards/dashboard.yml << 'EOF'
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
EOF

# Create basic dashboard
echo "📊 Creating basic dashboard..."
cat > monitoring/grafana/dashboards/google-calendar-mcp.json << 'EOF'
{
  "dashboard": {
    "id": null,
    "title": "Google Calendar MCP - Beast Mode",
    "tags": ["mcp", "google-calendar", "beast-mode"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "MCP Server Status",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=\"google-calendar-mcp\"}",
            "refId": "A"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
      }
    ],
    "time": {"from": "now-1h", "to": "now"},
    "refresh": "5s"
  }
}
EOF

# Check for credentials
echo "🔐 Checking credentials..."
if [ ! -f "credentials/gcp-oauth.keys.json" ]; then
    echo "⚠️  WARNING: No Google OAuth credentials found!"
    echo ""
    echo "To complete setup:"
    echo "1. Go to Google Cloud Console: https://console.cloud.google.com/"
    echo "2. Create a new project or select existing"
    echo "3. Enable Google Calendar API"
    echo "4. Create OAuth 2.0 credentials (Desktop application)"
    echo "5. Download the JSON file as 'credentials/gcp-oauth.keys.json'"
    echo ""
    echo "Example credentials structure:"
    cat << 'EXAMPLE'
{
  "installed": {
    "client_id": "your-client-id.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_secret": "your-client-secret"
  }
}
EXAMPLE
    echo ""
else
    echo "✅ Credentials found: credentials/gcp-oauth.keys.json"
fi

# Build and start
echo "🐳 Building Docker container..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "✅ Setup complete!"
echo ""
echo "Services:"
echo "- Google Calendar MCP: http://localhost:3000"
echo "- Prometheus: http://localhost:9090"
echo "- Grafana: http://localhost:3001 (admin/admin)"
echo ""
echo "Claude Desktop Configuration:"
echo "Add this to your Claude Desktop config:"
echo ""
cat claude_desktop_config.json
echo ""
echo "Next steps:"
echo "1. Add your Google OAuth credentials to credentials/gcp-oauth.keys.json"
echo "2. Restart the container: docker-compose restart"
echo "3. Configure Claude Desktop with the MCP server"
echo "4. Test the integration!"
echo ""
echo "Beast Mode compliance: ✅"
echo "- Containerized deployment"
echo "- Prometheus metrics"
echo "- Grafana dashboards"
echo "- Systematic observability"