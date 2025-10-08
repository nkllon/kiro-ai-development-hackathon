#!/usr/bin/env python3
"""
Test Jaeger tracing connectivity and functionality.
"""

import sys
import os
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_jaeger_connectivity():
    """Test if Jaeger is accessible."""
    print("🔍 Testing Jaeger connectivity...")
    
    jaeger_endpoint = os.getenv('JAEGER_ENDPOINT', 'http://observatory-jaeger:14268/api/traces')
    print(f"📡 Jaeger endpoint: {jaeger_endpoint}")
    
    try:
        import requests
        # Test Jaeger health
        health_url = jaeger_endpoint.replace('/api/traces', '/health')
        response = requests.get(health_url, timeout=5)
        print(f"✅ Jaeger health check: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Jaeger connectivity failed: {e}")
        return False

def test_tracing_imports():
    """Test if tracing modules can be imported."""
    print("🔍 Testing tracing imports...")
    
    try:
        from src.beast_mode.tracing.tracer import get_tracer
        print("✅ Tracer module imported successfully")
        
        tracer = get_tracer("test-service")
        print("✅ Tracer instance created")
        
        if hasattr(tracer, 'is_available') and tracer.is_available():
            print("✅ Tracer is available and ready")
        else:
            print("⚠️ Tracer created but may not be fully configured")
            
        return True
        
    except ImportError as e:
        print(f"❌ Tracing import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Tracing setup failed: {e}")
        return False

def create_test_trace():
    """Create a test trace to verify Jaeger is working."""
    print("🔍 Creating test trace...")
    
    try:
        from src.beast_mode.tracing.tracer import get_tracer
        tracer = get_tracer("observatory-diagnostic")
        
        with tracer.start_span("diagnostic_test") as span:
            span.set_attribute("test.type", "connectivity")
            span.set_attribute("test.timestamp", time.time())
            
            # Simulate some work
            time.sleep(0.1)
            
            span.set_attribute("test.result", "success")
            print("✅ Test trace created successfully")
            
        return True
        
    except Exception as e:
        print(f"❌ Test trace creation failed: {e}")
        return False

def main():
    """Run all Jaeger diagnostic tests."""
    print("🚀 Starting Jaeger diagnostic tests...")
    print("=" * 50)
    
    results = {
        "connectivity": test_jaeger_connectivity(),
        "imports": test_tracing_imports(),
        "tracing": create_test_trace()
    }
    
    print("\n📊 Diagnostic Results:")
    print("=" * 30)
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test.upper()}: {status}")
    
    all_passed = all(results.values())
    print(f"\n🎯 Overall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if not all_passed:
        print("\n💡 Recommendations:")
        if not results["connectivity"]:
            print("  - Check if Jaeger container is running")
            print("  - Verify network connectivity to Jaeger")
        if not results["imports"]:
            print("  - Install OpenTelemetry dependencies")
            print("  - Check tracing module implementation")
        if not results["tracing"]:
            print("  - Verify Jaeger configuration")
            print("  - Check trace export settings")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)