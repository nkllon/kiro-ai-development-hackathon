#!/usr/bin/env python3
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
        
        return "\n".join(output)

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
