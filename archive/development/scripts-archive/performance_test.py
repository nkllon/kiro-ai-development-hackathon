#!/usr/bin/env python3
"""
Performance test for WebSocket validation framework.
"""

import time
import sys
sys.path.append('src')

def test_import_performance():
    """Test import performance."""
    start_time = time.time()
    
    try:
        from websocket_validation import ValidationEngine
        import_time = time.time() - start_time
        
        print(f"✓ Import time: {import_time:.3f} seconds")
        
        if import_time < 1.0:
            print("✓ Import performance: EXCELLENT (<1s)")
            return True
        elif import_time < 3.0:
            print("✓ Import performance: GOOD (<3s)")
            return True
        else:
            print("✗ Import performance: POOR (>3s)")
            return False
            
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_initialization_performance():
    """Test initialization performance."""
    start_time = time.time()
    
    try:
        from websocket_validation import ValidationEngine
        engine = ValidationEngine()
        init_time = time.time() - start_time
        
        print(f"✓ Initialization time: {init_time:.3f} seconds")
        
        if init_time < 2.0:
            print("✓ Initialization performance: EXCELLENT (<2s)")
            return True
        elif init_time < 5.0:
            print("✓ Initialization performance: GOOD (<5s)")
            return True
        else:
            print("✗ Initialization performance: POOR (>5s)")
            return False
            
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return False

def test_basic_operations_performance():
    """Test basic operations performance."""
    start_time = time.time()
    
    try:
        from websocket_validation import ValidationEngine
        engine = ValidationEngine()
        
        # Test status method
        status_start = time.time()
        status = engine.get_validation_status()
        status_time = time.time() - status_start
        
        # Test evidence report
        evidence_start = time.time()
        evidence = engine.generate_evidence_report()
        evidence_time = time.time() - evidence_start
        
        total_time = time.time() - start_time
        
        print(f"✓ Status method time: {status_time:.3f} seconds")
        print(f"✓ Evidence report time: {evidence_time:.3f} seconds")
        print(f"✓ Total operations time: {total_time:.3f} seconds")
        
        if total_time < 1.0:
            print("✓ Operations performance: EXCELLENT (<1s)")
            return True
        elif total_time < 3.0:
            print("✓ Operations performance: GOOD (<3s)")
            return True
        else:
            print("✗ Operations performance: POOR (>3s)")
            return False
            
    except Exception as e:
        print(f"✗ Operations test failed: {e}")
        return False

if __name__ == "__main__":
    print("WebSocket Validation Framework Performance Test")
    print("=" * 60)
    
    tests = [
        ("Import Performance", test_import_performance),
        ("Initialization Performance", test_initialization_performance),
        ("Basic Operations Performance", test_basic_operations_performance)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        if test_func():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"Performance Tests: {passed}/{total} passed")
    
    if passed == total:
        print("✓ All performance tests passed!")
        sys.exit(0)
    else:
        print("✗ Some performance tests failed!")
        sys.exit(1)