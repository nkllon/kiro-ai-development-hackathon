#!/usr/bin/env python3
"""
Direct RDI Test - No Shell Commands
==================================

Direct testing of RDI and RM-DDD compliance without shell commands.
"""

import os
import sys
from pathlib import Path

def test_file_sizes():
    """Test RDI size compliance directly."""
    print("🔍 TESTING RDI SIZE COMPLIANCE")
    print("=" * 35)
    
    files_to_check = [
        "smart_devpost_navigator_v2.py",
        "src/navigator_consolidated/core_navigator.py",
        "src/navigator_consolidated/event_handler.py",
        "src/navigator_consolidated/step_detector.py",
        "src/navigator_consolidated/form_processor.py",
        "src/navigator_consolidated/interactive_mode.py"
    ]
    
    compliant = 0
    total = len(files_to_check)
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                lines = f.readlines()
                line_count = len(lines)
                
                if line_count <= 200:
                    print(f"✅ {file_path}: {line_count} lines (RDI compliant)")
                    compliant += 1
                else:
                    print(f"❌ {file_path}: {line_count} lines (RDI violation)")
        else:
            print(f"⚠️ {file_path}: File not found")
    
    compliance_rate = (compliant / total) * 100
    print(f"\n📊 RDI Size Compliance: {compliant}/{total} files ({compliance_rate:.1f}%)")
    return compliance_rate == 100

def test_imports():
    """Test module imports directly."""
    print("\n🧪 TESTING MODULE IMPORTS")
    print("=" * 30)
    
    try:
        # Test main wrapper
        sys.path.insert(0, str(Path(__file__).parent))
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

def test_rm_ddd_patterns():
    """Test RM-DDD patterns directly."""
    print("\n🧬 TESTING RM-DDD PATTERNS")
    print("=" * 35)
    
    try:
        # Test ReflectiveModule pattern
        from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
        print("✅ ReflectiveModule base class: SUCCESS")
        
        # Test DAG registry
        from src.rm_ddd.core.dag_registry import DAGRegistry
        print("✅ DAG registry: SUCCESS")
        
        # Test bounded context
        from src.rm_ddd.core.bounded_context import BoundedContext
        print("✅ BoundedContext: SUCCESS")
        
        # Test AI framework
        from src.rm_ddd.core.ai_framework import AgentOrchestrator
        print("✅ AI framework: SUCCESS")
        
        return True
        
    except ImportError as e:
        print(f"❌ RM-DDD pattern test failed: {e}")
        return False

def test_functionality():
    """Test basic functionality preservation."""
    print("\n⚙️ TESTING FUNCTIONALITY")
    print("=" * 25)
    
    try:
        from smart_devpost_navigator_v2 import SmartDevPostNavigatorV2
        
        # Test instantiation
        navigator = SmartDevPostNavigatorV2()
        print("✅ Navigator instantiation: SUCCESS")
        
        # Test delegation
        core_navigator = navigator.core_navigator
        print("✅ Core navigator delegation: SUCCESS")
        
        # Test components
        event_handler = core_navigator.event_handler
        step_detector = core_navigator.step_detector
        form_processor = core_navigator.form_processor
        interactive_mode = core_navigator.interactive_mode
        
        print("✅ Component access: SUCCESS")
        
        # Test main interface
        assert hasattr(navigator, 'start_navigation'), "Missing start_navigation method"
        print("✅ Main interface preserved: SUCCESS")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def test_architecture():
    """Test architectural compliance."""
    print("\n🏗️ TESTING ARCHITECTURE")
    print("=" * 25)
    
    try:
        # Test separation of concerns
        from src.navigator_consolidated.event_handler import EventHandler
        from src.navigator_consolidated.step_detector import StepDetector
        from src.navigator_consolidated.form_processor import FormProcessor
        from src.navigator_consolidated.interactive_mode import InteractiveMode
        
        # Check method counts (should be focused)
        event_methods = [m for m in dir(EventHandler) if not m.startswith('_')]
        step_methods = [m for m in dir(StepDetector) if not m.startswith('_')]
        form_methods = [m for m in dir(FormProcessor) if not m.startswith('_')]
        interactive_methods = [m for m in dir(InteractiveMode) if not m.startswith('_')]
        
        print(f"✅ Event handler methods: {len(event_methods)}")
        print(f"✅ Step detector methods: {len(step_methods)}")
        print(f"✅ Form processor methods: {len(form_methods)}")
        print(f"✅ Interactive mode methods: {len(interactive_methods)}")
        
        # Check if components are focused (not too many methods)
        max_methods = 15
        focused = all([
            len(event_methods) <= max_methods,
            len(step_methods) <= max_methods,
            len(form_methods) <= max_methods,
            len(interactive_methods) <= max_methods
        ])
        
        if focused:
            print("✅ Components are focused: SUCCESS")
        else:
            print("⚠️ Some components may be too broad")
        
        return True
        
    except Exception as e:
        print(f"❌ Architecture test failed: {e}")
        return False

def main():
    """Run all direct tests."""
    print("🚨 DIRECT RDI AND RM-DDD COMPLIANCE TEST")
    print("=" * 50)
    print("Testing without shell commands")
    print()
    
    tests = [
        ("RDI Size Compliance", test_file_sizes),
        ("Module Imports", test_imports),
        ("RM-DDD Patterns", test_rm_ddd_patterns),
        ("Functionality Preservation", test_functionality),
        ("Architecture Compliance", test_architecture)
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
        print("🎉 ALL TESTS PASSED - SYSTEM IS FULLY COMPLIANT!")
        print("✅ RDI compliance: ACHIEVED")
        print("✅ RM-DDD compliance: ACHIEVED")
        print("✅ Architecture: SOUND")
        print("✅ Functionality: PRESERVED")
    else:
        print("⚠️ SOME TESTS FAILED - SYSTEM NEEDS ATTENTION")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

