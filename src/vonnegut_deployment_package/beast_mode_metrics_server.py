#!/usr/bin/env python3
"""
Beast Mode Metrics Server for Prometheus
========================================

Serves historical Beast Mode performance data as Prometheus metrics.
"""

import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime

class BeastModeMetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            
            # Load and serve metrics
            metrics = self.generate_metrics()
            self.wfile.write(metrics.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def generate_metrics(self):
        """Generate Prometheus metrics from historical data."""
        
        # Read historical data
        data_file = Path("metrics_data/gke_velocity_measurements.jsonl")
        
        if not data_file.exists():
            return "# No historical data available\n"
        
        metrics_data = []
        with open(data_file, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    metrics_data.append(data)
                except json.JSONDecodeError:
                    continue
        
        # Group by measurement type
        before_beast_mode = [d for d in metrics_data if d.get('measurement_type') == 'before_beast_mode']
        after_beast_mode = [d for d in metrics_data if d.get('measurement_type') == 'after_beast_mode']
        
        if not before_beast_mode or not after_beast_mode:
            return "# No valid measurement data\n"
        
        # Calculate averages
        before_avg = {
            'features_per_day': sum(d['features_completed_per_day'] for d in before_beast_mode) / len(before_beast_mode),
            'bugs_per_day': sum(d['bugs_fixed_per_day'] for d in before_beast_mode) / len(before_beast_mode),
            'code_quality': sum(d['code_quality_score'] for d in before_beast_mode) / len(before_beast_mode),
            'rework_pct': sum(d['rework_percentage'] for d in before_beast_mode) / len(before_beast_mode),
            'resolution_hours': sum(d['time_to_resolution_hours'] for d in before_beast_mode) / len(before_beast_mode)
        }
        
        after_avg = {
            'features_per_day': sum(d['features_completed_per_day'] for d in after_beast_mode) / len(after_beast_mode),
            'bugs_per_day': sum(d['bugs_fixed_per_day'] for d in after_beast_mode) / len(after_beast_mode),
            'code_quality': sum(d['code_quality_score'] for d in after_beast_mode) / len(after_beast_mode),
            'rework_pct': sum(d['rework_percentage'] for d in after_beast_mode) / len(after_beast_mode),
            'resolution_hours': sum(d['time_to_resolution_hours'] for d in after_beast_mode) / len(after_beast_mode)
        }
        
        # Generate Prometheus metrics
        timestamp = int(time.time() * 1000)
        
        metrics = f"""# HELP beast_mode_features_completed_per_day Features completed per day
# TYPE beast_mode_features_completed_per_day gauge
beast_mode_features_completed_per_day{{phase="before"}} {before_avg['features_per_day']} {timestamp}
beast_mode_features_completed_per_day{{phase="after"}} {after_avg['features_per_day']} {timestamp}

# HELP beast_mode_bugs_fixed_per_day Bugs fixed per day
# TYPE beast_mode_bugs_fixed_per_day gauge
beast_mode_bugs_fixed_per_day{{phase="before"}} {before_avg['bugs_per_day']} {timestamp}
beast_mode_bugs_fixed_per_day{{phase="after"}} {after_avg['bugs_per_day']} {timestamp}

# HELP beast_mode_code_quality_score Code quality score (0-10)
# TYPE beast_mode_code_quality_score gauge
beast_mode_code_quality_score{{phase="before"}} {before_avg['code_quality']} {timestamp}
beast_mode_code_quality_score{{phase="after"}} {after_avg['code_quality']} {timestamp}

# HELP beast_mode_rework_percentage Percentage of work requiring rework
# TYPE beast_mode_rework_percentage gauge
beast_mode_rework_percentage{{phase="before"}} {before_avg['rework_pct']} {timestamp}
beast_mode_rework_percentage{{phase="after"}} {after_avg['rework_pct']} {timestamp}

# HELP beast_mode_time_to_resolution_hours Average time to resolve issues in hours
# TYPE beast_mode_time_to_resolution_hours gauge
beast_mode_time_to_resolution_hours{{phase="before"}} {before_avg['resolution_hours']} {timestamp}
beast_mode_time_to_resolution_hours{{phase="after"}} {after_avg['resolution_hours']} {timestamp}

# HELP beast_mode_improvement_factor Overall improvement factor
# TYPE beast_mode_improvement_factor gauge
beast_mode_improvement_factor{{}} {after_avg['features_per_day']/before_avg['features_per_day']:.3f} {timestamp}

# HELP beast_mode_total_measurements Total number of measurements collected
# TYPE beast_mode_total_measurements counter
beast_mode_total_measurements{{phase="before"}} {len(before_beast_mode)} {timestamp}
beast_mode_total_measurements{{phase="after"}} {len(after_beast_mode)} {timestamp}

# HELP beast_mode_data_collection_active Data collection status
# TYPE beast_mode_data_collection_active gauge
beast_mode_data_collection_active{{}} 1 {timestamp}
"""
        
        return metrics

def run_server(port=8001):
    """Run the Beast Mode metrics server."""
    server = HTTPServer(('0.0.0.0', port), BeastModeMetricsHandler)
    print(f"🚀 Beast Mode Metrics Server starting on port {port}")
    print(f"📊 Metrics endpoint: http://localhost:{port}/metrics")
    print(f"🔗 Add to Prometheus: localhost:{port}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Beast Mode Metrics Server")
        server.shutdown()

if __name__ == "__main__":
    run_server()