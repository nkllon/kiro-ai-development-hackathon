#!/usr/bin/env python3
"""
Create Redis Exporter Solution
Alternative approach using Prometheus Redis exporter instead of direct Redis plugin
"""

import subprocess
import time
import requests
import json

def create_redis_exporter_service():
    """Create Redis exporter service to expose Redis metrics to Prometheus."""
    
    print("🔧 Creating Redis exporter solution...")
    
    # Create a simple Redis metrics exporter script
    exporter_script = '''#!/usr/bin/env python3
"""
Simple Redis Metrics Exporter for Prometheus
Exports Redis stream data as Prometheus metrics
"""

import redis
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import json

class RedisMetricsExporter:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, password='mspssl123', decode_responses=True)
        self.metrics_cache = {}
        self.last_update = 0
        
    def get_redis_metrics(self):
        """Get Redis metrics and convert to Prometheus format."""
        if time.time() - self.last_update < 30:  # Cache for 30 seconds
            return self.metrics_cache
            
        try:
            metrics = {}
            
            # Get stream lengths
            metrics['observatory_metrics_total'] = self.redis_client.xlen('observatory_metrics')
            metrics['llm_costs_total'] = self.redis_client.xlen('observatory_metrics:llm_costs')
            metrics['analytics_total'] = self.redis_client.xlen('observatory_metrics:analytics')
            metrics['messages_total'] = self.redis_client.llen('beast_mode_messages')
            
            # Get recent health scores from observatory_metrics
            recent_entries = self.redis_client.xrevrange('observatory_metrics', count=10)
            if recent_entries:
                health_scores = []
                for entry_id, entry_data in recent_entries:
                    if 'health_score' in entry_data:
                        try:
                            health_scores.append(float(entry_data['health_score']))
                        except:
                            pass
                
                if health_scores:
                    metrics['avg_health_score'] = sum(health_scores) / len(health_scores)
                    metrics['min_health_score'] = min(health_scores)
            
            # Get recent LLM costs
            recent_costs = self.redis_client.xrevrange('observatory_metrics:llm_costs', count=10)
            if recent_costs:
                costs = []
                for entry_id, entry_data in recent_costs:
                    if 'estimated_cost' in entry_data:
                        try:
                            costs.append(float(entry_data['estimated_cost']))
                        except:
                            pass
                
                if costs:
                    metrics['avg_llm_cost'] = sum(costs) / len(costs)
                    metrics['total_recent_llm_cost'] = sum(costs)
            
            self.metrics_cache = metrics
            self.last_update = time.time()
            return metrics
            
        except Exception as e:
            print(f"Error getting Redis metrics: {e}")
            return {}
    
    def format_prometheus_metrics(self, metrics):
        """Format metrics in Prometheus exposition format."""
        output = []
        
        for metric_name, value in metrics.items():
            output.append(f"# HELP redis_{metric_name} Redis metric from Beast Mode")
            output.append(f"# TYPE redis_{metric_name} gauge")
            output.append(f"redis_{metric_name} {value}")
        
        return "\\n".join(output)

class MetricsHandler(BaseHTTPRequestHandler):
    def __init__(self, exporter, *args, **kwargs):
        self.exporter = exporter
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/metrics':
            metrics = self.exporter.get_redis_metrics()
            prometheus_output = self.exporter.format_prometheus_metrics(metrics)
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(prometheus_output.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run_exporter():
    exporter = RedisMetricsExporter()
    
    def handler(*args, **kwargs):
        return MetricsHandler(exporter, *args, **kwargs)
    
    server = HTTPServer(('0.0.0.0', 9121), handler)
    print("Redis metrics exporter running on port 9121")
    server.serve_forever()

if __name__ == "__main__":
    run_exporter()
'''
    
    # Write the exporter script
    with open('scripts/redis_metrics_exporter.py', 'w') as f:
        f.write(exporter_script)
    
    print("✅ Created Redis metrics exporter script")
    return True

def update_prometheus_config():
    """Update Prometheus configuration to scrape Redis exporter."""
    
    print("🔧 Updating Prometheus configuration...")
    
    # Read current Prometheus config
    try:
        with open('deployment/observatory/prometheus.yml', 'r') as f:
            config = f.read()
        
        # Add Redis exporter scrape config if not already present
        if 'redis-exporter' not in config:
            redis_scrape_config = '''
- job_name: redis-exporter
  metrics_path: /metrics
  scrape_interval: 30s
  static_configs:
  - targets:
    - localhost:9121
'''
            
            # Insert before the last line
            lines = config.strip().split('\n')
            lines.append('')
            lines.extend(redis_scrape_config.strip().split('\n'))
            
            with open('deployment/observatory/prometheus.yml', 'w') as f:
                f.write('\n'.join(lines))
            
            print("✅ Updated Prometheus configuration")
            return True
        else:
            print("✅ Prometheus already configured for Redis exporter")
            return True
            
    except Exception as e:
        print(f"❌ Error updating Prometheus config: {e}")
        return False

def create_simple_dashboard():
    """Create a simple dashboard using Prometheus data instead of Redis plugin."""
    
    dashboard = {
        "dashboard": {
            "title": "Beast Mode Redis Metrics (Prometheus)",
            "tags": ["beast-mode", "redis", "prometheus"],
            "timezone": "",
            "panels": [
                {
                    "id": 1,
                    "title": "Redis Stream Lengths",
                    "type": "stat",
                    "targets": [
                        {
                            "expr": "redis_observatory_metrics_total",
                            "legendFormat": "Observatory Metrics",
                            "refId": "A"
                        },
                        {
                            "expr": "redis_llm_costs_total", 
                            "legendFormat": "LLM Costs",
                            "refId": "B"
                        }
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                },
                {
                    "id": 2,
                    "title": "Average Health Score",
                    "type": "gauge",
                    "targets": [
                        {
                            "expr": "redis_avg_health_score",
                            "legendFormat": "Health Score",
                            "refId": "A"
                        }
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                },
                {
                    "id": 3,
                    "title": "LLM Costs",
                    "type": "timeseries",
                    "targets": [
                        {
                            "expr": "redis_avg_llm_cost",
                            "legendFormat": "Average Cost",
                            "refId": "A"
                        }
                    ],
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8}
                }
            ],
            "time": {"from": "now-1h", "to": "now"},
            "refresh": "30s"
        }
    }
    
    try:
        response = requests.post(
            'http://localhost:3000/api/dashboards/db',
            json=dashboard,
            auth=('admin', 'admin'),
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code in [200, 201]:
            print("✅ Created simple Redis metrics dashboard")
            return True
        else:
            print(f"❌ Failed to create dashboard: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating dashboard: {e}")
        return False

def main():
    """Main function to create Redis exporter solution."""
    
    print("🚀 Creating Redis Exporter Solution")
    print("=" * 40)
    print("Since the Redis plugin has compatibility issues,")
    print("we'll use a Prometheus-based approach instead.")
    print()
    
    # Step 1: Create Redis exporter
    if not create_redis_exporter_service():
        return False
    
    # Step 2: Update Prometheus config
    if not update_prometheus_config():
        return False
    
    # Step 3: Create simple dashboard
    time.sleep(2)  # Wait a moment
    if not create_simple_dashboard():
        print("⚠️ Dashboard creation failed, but exporter is ready")
    
    print()
    print("🎉 Redis Exporter Solution Created!")
    print("📊 Next steps:")
    print("   1. Run: python scripts/redis_metrics_exporter.py")
    print("   2. Restart Prometheus to pick up new config")
    print("   3. Check Grafana for Redis metrics from Prometheus")
    print()
    print("🌐 This approach uses Prometheus to scrape Redis data")
    print("   instead of the problematic Redis plugin.")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)