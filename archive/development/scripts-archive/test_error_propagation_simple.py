#!/usr/bin/env python3
"""
Simple test script for Error Propagation Analysis implementation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all imports work correctly."""
    try:
        from src.system_architecture.models.error_propagation import (
            ErrorPropagationGraph, ErrorPropagationPath, CorrelationIDMapping,
            ErrorRecoveryProcedure, FallbackMechanism, EmergencyProtocol,
            ErrorClassification, ErrorSeverity, ErrorCategory, FallbackType
        )
        print("✅ Error propagation models imported successfully")
        
        from src.system_architecture.analysis.error_propagation_analyzer import (
            ErrorPropagationAnalyzer, ErrorPropagationConfig
        )
        print("✅ Error propagation analyzer imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_models():
    """Test error propagation models."""
    try:
        from src.system_architecture.models.error_propagation import (
            ErrorPropagationGraph, ErrorPropagationPath, ErrorSeverity, ErrorCategory
        )
        
        # Test ErrorPropagationPath creation
        path = ErrorPropagationPath(
            path_id="test_path",
            source_component="test_source",
            target_components=["target1"],
            propagation_steps=["step1"],
            error_types=["error1"],
            severity_levels=[ErrorSeverity.ERROR]
        )
        print("✅ ErrorPropagationPath created successfully")
        
        # Test ErrorPropagationGraph creation
        graph = ErrorPropagationGraph(
            graph_id="test_graph",
            graph_name="Test Graph"
        )
        graph.add_propagation_path(path)
        print("✅ ErrorPropagationGraph created and path added successfully")
        
        # Test graph validation
        validation = graph.validate_graph()
        print(f"✅ Graph validation: {validation['is_valid']}")
        
        return True
    except Exception as e:
        print(f"❌ Model test error: {e}")
        return False

def test_analyzer():
    """Test error propagation analyzer."""
    try:
        from src.system_architecture.analysis.error_propagation_analyzer import (
            ErrorPropagationAnalyzer, ErrorPropagationConfig
        )
        
        # Test configuration
        config = ErrorPropagationConfig(
            enable_real_time_analysis=False,
            analysis_interval_seconds=1
        )
        print("✅ ErrorPropagationConfig created successfully")
        
        # Test analyzer creation
        analyzer = ErrorPropagationAnalyzer(config)
        print("✅ ErrorPropagationAnalyzer created successfully")
        
        # Test module info
        info = analyzer.get_module_info()
        print(f"✅ Module info: {info['name']}")
        
        # Test capabilities
        capabilities = analyzer.get_capabilities()
        print(f"✅ Capabilities: {[cap.value for cap in capabilities]}")
        
        # Test health status
        health = analyzer.get_health_status()
        print(f"✅ Health status: {health.status.value}")
        
        return True
    except Exception as e:
        print(f"❌ Analyzer test error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Error Propagation Analysis Implementation")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("Model Tests", test_models),
        ("Analyzer Tests", test_analyzer),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Error Propagation Analysis implementation is working correctly.")
        return 0
    else:
        print("💥 Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())