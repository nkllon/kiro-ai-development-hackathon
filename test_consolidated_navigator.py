#!/usr/bin/env python3
"""
Test Consolidated Navigator System
=================================

Comprehensive test of the refactored smart_devpost_navigator_v2.py
and its consolidated modules for RDI and RM-DDD compliance.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test all consolidated module imports."""
    print("🧪 TESTING CONSOLIDATED NAVIGATOR IMPORTS")
    print("=" * 50)
    
    try:
        # Test main wrapper
        from smart_devpost_navigator_v2 import SmartDevPostNavigatorV2
        print("✅ Main wrapper import: SUCCESS")
        
        # Test consolidated modules
        from src.navigator_consolidated.core_navigator import SmartDevPostNavigatorV2 as CoreNavigator
        print("✅ Core navigator import: SUCCESS")
        
        from src.navigator_consolidated.event_handler import EventHandler
        print("✅ Event handler import: SUCCESS")
        
        from src.navigator_consolidated.step_detector import StepDetector
        print("✅ Step detector import: SUCCESS")
        
        from src.navigator_consolidated.form_processor import FormProcessor
        print("✅ Form processor import: SUCCESS")
        
        from src.navigator_consolidated.interactive_mode import InteractiveMode
        print("✅ Interactive mode import: SUCCESS")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_rdi_compliance():
    """Test RDI compliance - size limits and structure."""
    print("\n🔍 TESTING RDI COMPLIANCE")
    print("=" * 30)
    
    # Check file sizes
    files_to_check = [
        "smart_devpost_navigator_v2.py",
        "src/navigator_consolidated/core_navigator.py",
        "src/navigator_consolidated/event_handler.py", 
        "src/navigator_consolidated/step_detector.py",
        "src/navigator_consolidated/form_processor.py",
        "src/navigator_consolidated/interactive_mode.py"
    ]
    
    rdi_compliant = True
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                lines = f.readlines()
                line_count = len(lines)
                
                if line_count <= 200:
                    print(f"✅ {file_path}: {line_count} lines (RDI compliant)")
                else:
                    print(f"❌ {file_path}: {line_count} lines (RDI violation)")
                    rdi_compliant = False
        else:
            print(f"⚠️ {file_path}: File not found")
            rdi_compliant = False
    
    return rdi_compliant

def test_rm_ddd_compliance():
    """Test RM-DDD compliance - reflective module patterns."""
    print("\n🧬 TESTING RM-DDD COMPLIANCE")
    print("=" * 35)
    
    try:
        # Test if modules can be instantiated
        from smart_devpost_navigator_v2 import SmartDevPostNavigatorV2
        
        navigator = SmartDevPostNavigatorV2()
        print("✅ Navigator instantiation: SUCCESS")
        
        # Test delegation pattern
        core_navigator = navigator.core_navigator
        print("✅ Core navigator delegation: SUCCESS")
        
        # Test component initialization
        event_handler = core_navigator.event_handler
        step_detector = core_navigator.step_detector
        form_processor = core_navigator.form_processor
        interactive_mode = core_navigator.interactive_mode
        
        print("✅ Component initialization: SUCCESS")
        print("✅ Event handler component: SUCCESS")
        print("✅ Step detector component: SUCCESS")
        print("✅ Form processor component: SUCCESS")
        print("✅ Interactive mode component: SUCCESS")
        
        return True
        
    except Exception as e:
        print(f"❌ RM-DDD compliance test failed: {e}")
        return False

def test_functionality():
    """Test basic functionality preservation."""
    print("\n⚙️ TESTING FUNCTIONALITY PRESERVATION")
    print("=" * 40)
    
    try:
        from smart_devpost_navigator_v2 import SmartDevPostNavigatorV2
        
        navigator = SmartDevPostNavigatorV2()
        
        # Test that main interface is preserved
        assert hasattr(navigator, 'start_navigation'), "Missing start_navigation method"
        print("✅ Main interface preserved: SUCCESS")
        
        # Test delegation works
        assert hasattr(navigator.core_navigator, 'start_navigation'), "Core navigator missing start_navigation"
        print("✅ Delegation pattern: SUCCESS")
        
        # Test component access
        assert hasattr(navigator.core_navigator, 'event_handler'), "Missing event_handler"
        assert hasattr(navigator.core_navigator, 'step_detector'), "Missing step_detector"
        assert hasattr(navigator.core_navigator, 'form_processor'), "Missing form_processor"
        assert hasattr(navigator.core_navigator, 'interactive_mode'), "Missing interactive_mode"
        print("✅ Component access: SUCCESS")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def test_architecture_compliance():
    """Test architectural compliance patterns."""
    print("\n🏗️ TESTING ARCHITECTURAL COMPLIANCE")
    print("=" * 40)
    
    try:
        # Test separation of concerns
        from src.navigator_consolidated.event_handler import EventHandler
        from src.navigator_consolidated.step_detector import StepDetector
        from src.navigator_consolidated.form_processor import FormProcessor
        from src.navigator_consolidated.interactive_mode import InteractiveMode
        
        # Each component should have focused responsibilities
        event_handler_methods = [method for method in dir(EventHandler) if not method.startswith('_')]
        step_detector_methods = [method for method in dir(StepDetector) if not method.startswith('_')]
        form_processor_methods = [method for method in dir(FormProcessor) if not method.startswith('_')]
        interactive_mode_methods = [method for method in dir(InteractiveMode) if not method.startswith('_')]
        
        print(f"✅ Event handler methods: {len(event_handler_methods)}")
        print(f"✅ Step detector methods: {len(step_detector_methods)}")
        print(f"✅ Form processor methods: {len(form_processor_methods)}")
        print(f"✅ Interactive mode methods: {len(interactive_mode_methods)}")
        
        # Test that components are focused (not too many methods)
        max_methods_per_component = 15
        if len(event_handler_methods) <= max_methods_per_component:
            print("✅ Event handler focused: SUCCESS")
        else:
            print(f"⚠️ Event handler has {len(event_handler_methods)} methods (may be too broad)")
            
        if len(step_detector_methods) <= max_methods_per_component:
            print("✅ Step detector focused: SUCCESS")
        else:
            print(f"⚠️ Step detector has {len(step_detector_methods)} methods (may be too broad)")
            
        if len(form_processor_methods) <= max_methods_per_component:
            print("✅ Form processor focused: SUCCESS")
        else:
            print(f"⚠️ Form processor has {len(form_processor_methods)} methods (may be too broad)")
            
        if len(interactive_mode_methods) <= max_methods_per_component:
            print("✅ Interactive mode focused: SUCCESS")
        else:
            print(f"⚠️ Interactive mode has {len(interactive_mode_methods)} methods (may be too broad)")
        
        return True
        
    except Exception as e:
        print(f"❌ Architecture compliance test failed: {e}")
        return False

def main():
    """Run comprehensive tests."""
    print("🚨 CONSOLIDATED NAVIGATOR SYSTEM TEST")
    print("=" * 50)
    print("Testing RDI and RM-DDD compliance for refactored system")
    print()
    
    tests = [
        ("Import Test", test_imports),
        ("RDI Compliance", test_rdi_compliance),
        ("RM-DDD Compliance", test_rm_ddd_compliance),
        ("Functionality Preservation", test_functionality),
        ("Architecture Compliance", test_architecture_compliance)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n📊 TEST RESULTS SUMMARY")
    print("=" * 30)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 OVERALL RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - SYSTEM IS RDI AND RM-DDD COMPLIANT!")
    else:
        print("⚠️ SOME TESTS FAILED - SYSTEM NEEDS ATTENTION")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

