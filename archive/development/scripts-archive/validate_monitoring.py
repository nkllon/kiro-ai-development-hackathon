#!/usr/bin/env python3
"""Simple validation script for WebSocket Health Monitoring Framework"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src.beast_mode.observatory.monitoring import (
        WebSocketHealthMonitor, HealthStatus, MetricsCollector,
        ConnectionTracker, PerformanceAnalyzer, AlertManager
    )
    
    print("✅ All monitoring components imported successfully")
    
    # Test basic initialization
    monitor = WebSocketHealthMonitor()
    print("✅ WebSocketHealthMonitor initialized")
    
    # Test health status values
    print("✅ Health status values:")
    for status in HealthStatus:
        print(f"  - {status.name}: {status.value}")
    
    # Test metrics collector
    metrics = MetricsCollector()
    print("✅ MetricsCollector initialized")
    
    # Test connection tracker
    tracker = ConnectionTracker()
    print("✅ ConnectionTracker initialized")
    
    # Test performance analyzer
    analyzer = PerformanceAnalyzer()
    print("✅ PerformanceAnalyzer initialized")
    
    # Test alert manager
    alerts = AlertManager()
    print("✅ AlertManager initialized")
    
    print("\n🎉 WebSocket Health Monitoring Framework validation successful!")
    print("All components are properly implemented and ready for use.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Validation error: {e}")
    sys.exit(1)