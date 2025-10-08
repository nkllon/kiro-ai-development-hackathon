#!/usr/bin/env python3
"""
Simple test script for WebSocket validation framework.
"""

import sys
import os
sys.path.append('src')

def test_imports():
    """Test basic imports."""
    try:
        from websocket_validation import ValidationEngine
        print("✓ Import successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_initialization():
    """Test ValidationEngine initialization."""
    try:
        from websocket_validation import ValidationEngine
        engine = ValidationEngine()
        print("✓ ValidationEngine initialization successful")
        return True
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return False

def test_configuration():
    """Test configuration loading."""
    try:
        from websocket_validation import ValidationEngine
        engine = ValidationEngine()
        config = engine.config
        print(f"✓ Configuration loaded: {config.production_base_url}")
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality."""
    try:
        from websocket_validation import ValidationEngine
        engine = ValidationEngine()
        
        # Test status method
        status = engine.get_validation_status()
        print(f"✓ Status method works: {status['execution_id']}")
        
        # Test evidence collector
        evidence_summary = engine.generate_evidence_report()
        print(f"✓ Evidence collector works: {evidence_summary}")
        
        return True
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing WebSocket Validation Framework...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_initialization,
        test_configuration,
        test_basic_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed!")
        sys.exit(1)