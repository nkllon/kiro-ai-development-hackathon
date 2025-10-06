#!/usr/bin/env python3
"""
Vonnegut Redis Exporter
Exports Beast Mode execution data from Vonnegut Redis to Prometheus metrics
"""

import redis
import time
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from datetime import datetime

class VonnegutRedisExporter:
    def __init__(self):
        self.redis_client = redis.Redis(
            host='192.168.1.119', 
            port=6379, 
            password=os.getenv('REDIS_PASSWORD', ''), 
            decode_responses=True
        )
        self.metrics_cache = {}
        self.last_update = 0
        
    def get_beast_mode_metrics(self):
        """Get Beast Mode execution metrics from Vonnegut Redis."""
        if time.time() - self.last_update < 30:  # Cache for 30 seconds
            return self.metrics_cache
            
        try:
            metrics = {}
            
            # Get all keys and categorize them
            all_keys = self.redis_client.keys('*')
            
            # Count by category
            checkin_keys = [k for k in all_keys if k.startswith('checkin:')]
            execution_keys = [k for k in all_keys if k.startswith('execution:') and not k.endswith('_history')]
            
            metrics['beast_mode_checkins_total'] = len(checkin_keys)
            metrics['beast_mode_executions_total'] = len(execution_keys)
            metrics['beast_mode_total_keys'] = len(all_keys)
            
            # Get active executions data
            if 'active_executions' in all_keys:
                try:
                    active_data = self.redis_client.get('active_executions')
                    if active_data:
                        active_executions = json.loads(active_data)
                        metrics['beast_mode_active_executions'] = len(active_executions)
                    else:
                        metrics['beast_mode_active_executions'] = 0
                except:
                    metrics['beast_mode_active_executions'] = 0
            
            # Analyze recent checkins (last 24 hours)
            recent_checkins = 0
            current_time = time.time()
            
            for key in checkin_keys[:20]:  # Sample recent checkins
                try:
                    # Extract timestamp from key if possible
                    if ':' in key:
                        parts = key.split(':')
                        if len(parts) >= 2:
                            timestamp_part = parts[-1]
                            if '.' in timestamp_part:
                                timestamp = float(timestamp_part)
                                if current_time - timestamp < 86400:  # 24 hours
                                    recent_checkins += 1
                except:
                    pass
            
            metrics['beast_mode_recent_checkins'] = recent_checkins
            
            # Analyze execution patterns
            execution_projects = set()
            for key in execution_keys:
                try:
                    # Extract project name from execution key
                    if ':' in key:
                        project_part = key.split(':')[1]
                        if '_' in project_part:
                            project_name = project_part.split('_')[0]
                            execution_projects.add(project_name)
                except:
                    pass
            
            metrics['beast_mode_active_projects'] = len(execution_projects)
            
            # Get execution history if available
            if 'execution_history' in all_keys:
                try:
                    history_data = self.redis_client.get('execution_history')
                    if history_data:
                        history = json.loads(history_data)
                        if isinstance(history, list):
                            metrics['beast_mode_total_historical_executions'] = len(history)
                        elif isinstance(history, dict):
                            metrics['beast_mode_total_historical_executions'] = len(history.keys())
                except:
                    metrics['beast_mode_total_historical_executions'] = 0
            
            self.metrics_cache = metrics
            self.last_update = time.time()
            
            print(f"📊 Updated metrics: {metrics}")
            return metrics
            
        except Exception as e:
            print(f"❌ Error getting Beast Mode metrics: {e}")
            return {}
    
    def format_prometheus_metrics(self, metrics):
        """Format metrics in Prometheus exposition format."""
        output = []
        
        # Add metadata
        output.append("# Beast Mode Execution Metrics from Vonnegut Redis")
        output.append(f"# Last updated: {datetime.now().isoformat()}")
        output.append("")
        
        for metric_name, value in metrics.items():
            output.append(f"# HELP {metric_name} Beast Mode execution metric")
            output.append(f"# TYPE {metric_name} gauge")
            output.append(f"{metric_name} {value}")
            output.append("")
        
        return "\n".join(output)

class MetricsHandler(BaseHTTPRequestHandler):
    def __init__(self, exporter, *args, **kwargs):
        self.exporter = exporter
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/metrics':
            try:
                metrics = self.exporter.get_beast_mode_metrics()
                prometheus_output = self.exporter.format_prometheus_metrics(metrics)
                
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(prometheus_output.encode('utf-8'))
                
            except Exception as e:
                print(f"❌ Error serving metrics: {e}")
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Error: {e}".encode('utf-8'))
                
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"OK")
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def test_redis_connection():
    """Test connection to Vonnegut Redis."""
    try:
        client = redis.Redis(
            host='192.168.1.119', 
            port=6379, 
            password=os.getenv('REDIS_PASSWORD', ''), 
            decode_responses=True
        )
        
        # Test connection
        client.ping()
        
        # Get sample data
        keys = client.keys('*')
        print(f"✅ Connected to Vonnegut Redis")
        print(f"📊 Found {len(keys)} keys")
        
        # Show key categories
        categories = {}
        for key in keys:
            category = key.split(':')[0] if ':' in key else 'other'
            categories[category] = categories.get(category, 0) + 1
        
        print("📋 Key categories:")
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"   {category}: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to Vonnegut Redis: {e}")
        return False

def run_exporter():
    """Run the Redis metrics exporter."""
    print("🚀 Starting Vonnegut Redis Exporter")
    print("=" * 40)
    
    # Test connection first
    if not test_redis_connection():
        print("❌ Cannot connect to Vonnegut Redis")
        return False
    
    # Create exporter
    exporter = VonnegutRedisExporter()
    
    # Test metrics collection
    print("\n🧪 Testing metrics collection...")
    test_metrics = exporter.get_beast_mode_metrics()
    if test_metrics:
        print("✅ Metrics collection working")
        for metric, value in test_metrics.items():
            print(f"   {metric}: {value}")
    else:
        print("❌ No metrics collected")
        return False
    
    # Start HTTP server
    def handler(*args, **kwargs):
        return MetricsHandler(exporter, *args, **kwargs)
    
    try:
        server = HTTPServer(('0.0.0.0', 9122), handler)
        print(f"\n🌐 Beast Mode Redis exporter running on port 9122")
        print(f"📊 Metrics endpoint: http://localhost:9122/metrics")
        print(f"❤️  Health endpoint: http://localhost:9122/health")
        print(f"🔗 Vonnegut Redis: 192.168.1.119:6379")
        print(f"\n📈 Add this to Prometheus scrape config:")
        print(f"   - job_name: beast-mode-redis")
        print(f"     static_configs:")
        print(f"       - targets: ['localhost:9122']")
        print(f"\nPress Ctrl+C to stop...")
        
        server.serve_forever()
        
    except KeyboardInterrupt:
        print(f"\n🛑 Shutting down exporter...")
        return True
    except Exception as e:
        print(f"❌ Error running server: {e}")
        return False

if __name__ == "__main__":
    success = run_exporter()
    exit(0 if success else 1)