#!/usr/bin/env python3
"""
Demo Prometheus Monitoring
==========================

Demonstrates real-time monitoring with Prometheus integration for the
Beast Mode framework. Shows how metrics are exported and can be scraped.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Demo Prometheus monitoring capabilities
"""

import sys
import os
import time
import requests
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from beast_mode.monitoring.prometheus_exporter import PrometheusExporter
from beast_mode.performance.performance_monitoring_system import PerformanceMonitoringSystem


def print_banner(title, width=80):
    """Print a formatted banner."""
    print("\n" + "=" * width)
    print(f"📊 {title}")
    print("=" * width)


def demo_prometheus_monitoring():
    """Demo Prometheus monitoring capabilities."""
    print_banner("BEAST MODE PROMETHEUS MONITORING DEMO")
    
    print("🚀 Initializing Prometheus metrics exporter...")
    
    # Initialize Prometheus exporter
    exporter = PrometheusExporter(port=8000, monitoring_interval=2.0)
    
    print("✅ Prometheus exporter initialized")
    print(f"📡 Metrics endpoint: http://localhost:8000/metrics")
    print(f"⏱️  Monitoring interval: 2 seconds")
    
    # Initialize performance monitor
    print("\n🔧 Initializing performance monitoring...")
    monitor = PerformanceMonitoringSystem(monitoring_interval=1.0, enable_alerts=True)
    
    print("✅ Performance monitoring initialized")
    
    # Simulate some activity
    print("\n📈 Simulating application activity...")
    
    for i in range(10):
        # Record some metrics
        monitor.record_metric(f'demo_metric_{i}', i * 10.5, tags={'demo': 'true'})
        monitor.record_timing(f'demo_timing_{i}', i * 50.0, tags={'operation': 'demo'})
        monitor.increment_counter('demo_counter', 1.0, tags={'event': 'demo'})
        
        print(f"   Recorded metrics batch {i+1}/10")
        time.sleep(1)
    
    # Wait for metrics to be collected and exported
    print("\n⏳ Waiting for metrics collection and export...")
    time.sleep(5)
    
    # Check metrics endpoint
    print("\n🔍 Checking Prometheus metrics endpoint...")
    
    try:
        response = requests.get("http://localhost:8000/metrics", timeout=10)
        if response.status_code == 200:
            metrics_content = response.text
            print(f"✅ Metrics endpoint accessible")
            print(f"📊 Metrics content length: {len(metrics_content)} characters")
            
            # Count different metric types
            beast_mode_metrics = metrics_content.count('beast_mode_')
            print(f"🏷️  Beast Mode metrics: {beast_mode_metrics}")
            
            # Show some key metrics
            key_metrics = [
                'beast_mode_system_cpu_percent',
                'beast_mode_app_operations_total',
                'beast_mode_component_health_status',
                'beast_mode_framework_info'
            ]
            
            print("\n📋 Key metrics found:")
            for metric in key_metrics:
                if metric in metrics_content:
                    print(f"   ✅ {metric}")
                else:
                    print(f"   ❌ {metric}")
            
            # Show sample metrics
            print("\n📄 Sample metrics (first 20 lines):")
            lines = metrics_content.split('\n')[:20]
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    print(f"   {line}")
            
        else:
            print(f"❌ Metrics endpoint returned HTTP {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to access metrics endpoint: {e}")
    
    # Get performance summary
    print("\n📊 Performance Summary:")
    current_metrics = monitor.get_current_metrics()
    
    system_usage = current_metrics.get('system_usage', {})
    app_metrics = current_metrics.get('application_metrics', {})
    
    print(f"   💻 CPU Usage: {system_usage.get('cpu_percent', 0):.1f}%")
    print(f"   🧠 Memory Usage: {system_usage.get('memory_percent', 0):.1f}%")
    print(f"   ⚡ Active Operations: {app_metrics.get('active_operations', 0)}")
    print(f"   📈 Throughput: {app_metrics.get('throughput_ops_per_second', 0):.1f} ops/sec")
    print(f"   🎯 Cache Hit Rate: {app_metrics.get('cache_hit_rate', 0):.1f}%")
    print(f"   🚨 Active Alerts: {current_metrics.get('active_alerts_count', 0)}")
    
    # Generate Prometheus report
    print("\n📋 Prometheus Integration Report:")
    report = exporter.generate_prometheus_report()
    print(report)
    
    print("\n🎉 DEMO COMPLETE!")
    print("\n📋 NEXT STEPS:")
    print("   1. Install Prometheus: brew install prometheus (or download from https://prometheus.io)")
    print("   2. Configure prometheus.yml to scrape Beast Mode metrics")
    print("   3. Start Prometheus: prometheus --config.file=prometheus.yml")
    print("   4. Access Prometheus UI: http://localhost:9090")
    print("   5. Query metrics like: beast_mode_system_cpu_percent")
    print("   6. Set up Grafana dashboards for visualization")
    print("   7. Configure alerting rules for Beast Mode metrics")
    
    # Cleanup
    monitor.stop_monitoring()
    print("\n🧹 Cleanup complete")


if __name__ == "__main__":
    demo_prometheus_monitoring()
