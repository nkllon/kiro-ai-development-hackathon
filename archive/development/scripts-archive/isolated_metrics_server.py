#!/usr/bin/env python3
import time
from prometheus_client import start_http_server, Gauge, Counter, CollectorRegistry
import json
from pathlib import Path
from datetime import datetime

# Create custom registry
registry = CollectorRegistry()

# Create metrics
cpu_usage = Gauge('beast_mode_cpu_usage_percent', 'CPU usage', registry=registry)
memory_usage = Gauge('beast_mode_memory_usage_percent', 'Memory usage', registry=registry)
kiro_processes = Gauge('beast_mode_kiro_processes', 'Kiro processes', registry=registry)
data_collection_active = Gauge('beast_mode_data_collection_active', 'Data collection status', registry=registry)

def update_metrics():
    try:
        # Read latest empirical data
        data_dir = Path("empirical_data")
        session_dirs = [d for d in data_dir.iterdir() if d.is_dir() and d.name.startswith('session_')]
        
        if session_dirs:
            latest_session = max(session_dirs, key=lambda x: x.name)
            system_file = latest_session / "system_metrics.jsonl"
            
            if system_file.exists():
                with open(system_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        latest = json.loads(lines[-1])
                        cpu_usage.set(latest['system']['cpu_percent'])
                        memory_usage.set(latest['system']['memory_percent'])
                        kiro_processes.set(latest['processes']['kiro_processes'])
                        data_collection_active.set(1)
                        print(f"📊 Updated metrics: CPU={latest['system']['cpu_percent']:.1f}%, Memory={latest['system']['memory_percent']:.1f}%")
    except Exception as e:
        print(f"❌ Error updating metrics: {e}")
        data_collection_active.set(0)

# Start server
start_http_server(9091, registry=registry)
print(f"✅ Metrics server started on port 9091")

# Update loop
while True:
    update_metrics()
    time.sleep(30)
