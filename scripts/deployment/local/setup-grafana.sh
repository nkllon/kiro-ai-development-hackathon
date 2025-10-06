#!/bin/bash
# Setup Grafana with Prometheus data source and Beast Mode dashboard

set -e

echo "Setting up Grafana for Beast Mode monitoring..."

# Wait for Grafana to be ready
echo "Waiting for Grafana to start..."
until curl -s http://localhost:3000/api/health > /dev/null; do
    echo "Waiting for Grafana..."
    sleep 2
done

echo "Grafana is ready!"

# Get Grafana admin password
GRAFANA_PASSWORD=$(docker exec local-grafana-1 cat /etc/grafana/grafana.ini | grep admin_password | cut -d'=' -f2 | tr -d ' ')
if [ -z "$GRAFANA_PASSWORD" ]; then
    GRAFANA_PASSWORD="admin"
fi

echo "Grafana admin password: $GRAFANA_PASSWORD"

# Create Prometheus data source
echo "Creating Prometheus data source..."
curl -X POST \
  -H "Content-Type: application/json" \
  -u "admin:$GRAFANA_PASSWORD" \
  -d '{
    "name": "Prometheus",
    "type": "prometheus",
    "url": "http://prometheus:9090",
    "access": "proxy",
    "isDefault": true
  }' \
  http://localhost:3000/api/datasources

echo "Prometheus data source created!"

# Import Beast Mode dashboard
echo "Importing Beast Mode dashboard..."
curl -X POST \
  -H "Content-Type: application/json" \
  -u "admin:$GRAFANA_PASSWORD" \
  -d @grafana/beast-mode-dashboard.json \
  http://localhost:3000/api/dashboards/db

echo "Beast Mode dashboard imported!"

echo ""
echo "🎉 Grafana setup complete!"
echo ""
echo "Access your dashboards at:"
echo "  http://localhost:3000"
echo "  Username: admin"
echo "  Password: $GRAFANA_PASSWORD"
echo ""
echo "Beast Mode Dashboard: http://localhost:3000/d/beast-mode-dashboard"
