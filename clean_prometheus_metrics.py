#!/usr/bin/env python3
"""
Clean Prometheus Metrics Server
Simple, working metrics server without conflicts
"""

from prometheus_client import start_http_server, Gauge, Counter, CollectorRegistry
import time
import json
import psutil
from pathlib import Path
from datetime import datetime

class CleanMetricsServer:
    """Clean, simple metrics server"""
    
    def __init__(self, port=8889):  # Different port to avoid conflicts
        self.port = port
        self.registry = CollectorRegistry()
        self.setup_metrics()
        
    def setup_metrics(self):
        """Setup Beast Mode metrics"""
        # System metrics
        self.cpu_usage = Gauge('beast_mode_cpu_percent', 'CPU usage percentage', registry=self.registry)
        self.memory_usage = Gauge('beast_mode_memory_percent', 'Memory usage percentage', registry=self.registry)
        self.kiro_processes = Gauge('beast_mode_kiro_processes', 'Number of Kiro processes', registry=self.registry)
        
        # Development metrics
        self.data_collection_active = Gauge('beast_mode_data_collection_active', 'Data collection status', registry=self.registry)
        self.total_measurements = Counter('beast_mode_total_measurements', 'Total measurements', registry=self.registry)
        
        print("✅ Metrics configured")
    
    def update_metrics(self):
        """Update metrics from system and empirical data"""
        try:
            # System metrics
            self.cpu_usage.set(psutil.cpu_percent())
            self.memory_usage.set(psutil.virtual_memory().percent)
            
            # Count Kiro processes
            kiro_count = 0
            for proc in psutil.process_iter(['name']):
                try:
                    if 'kiro' in proc.info['name'].lower():
                        kiro_count += 1
                except:
                    pass
            self.kiro_processes.set(kiro_count)
            
            # Check empirical data
            data_dir = Path("empirical_data")
            if data_dir.exists():
                session_dirs = [d for d in data_dir.iterdir() if d.is_dir() and d.name.startswith('session_')]
                if session_dirs:
                    self.data_collection_active.set(1)
                    self.total_measurements.inc()
                else:
                    self.data_collection_active.set(0)
            else:
                self.data_collection_active.set(0)
            
            print(f"📊 Metrics updated: CPU={psutil.cpu_percent():.1f}%, Memory={psutil.virtual_memory().percent:.1f}%, Kiro={kiro_count}")
            
        except Exception as e:
            print(f"❌ Error updating metrics: {e}")
    
    def start_server(self):
        """Start the metrics server"""
        try:
            start_http_server(self.port, registry=self.registry)
            print(f"✅ Metrics server started on port {self.port}")
            print(f"📊 Metrics URL: http://localhost:{self.port}/metrics")
            return True
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
    
    def run(self):
        """Run the metrics server"""
        print("🚀 Starting Clean Prometheus Metrics Server")
        print("=" * 50)
        
        if not self.start_server():
            return False
        
        print("✅ Server running, updating metrics every 30 seconds")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                self.update_metrics()
                time.sleep(30)
        except KeyboardInterrupt:
            print("\n🛑 Stopping metrics server")
            return True

def main():
    server = CleanMetricsServer()
    server.run()

if __name__ == "__main__":
    main()