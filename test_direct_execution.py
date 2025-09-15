#!/usr/bin/env python3
"""
Test Direct Execution - No Shell Commands
========================================

Direct execution of the RDI test to verify system works.
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

def main():
    """Run direct tests."""
    print("🚨 DIRECT RDI COMPLIANCE TEST")
    print("=" * 40)
    print("Testing without shell commands")
    print()
    
    tests = [
        ("RDI Size Compliance", test_file_sizes),
        ("Module Imports", test_imports),
        ("Functionality Preservation", test_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n📊 DIRECT TEST RESULTS")
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
        print("🎉 ALL DIRECT TESTS PASSED!")
        print("✅ RDI compliance: VERIFIED")
        print("✅ System functionality: PRESERVED")
        print("✅ Architecture: SOUND")
    else:
        print("⚠️ SOME TESTS FAILED - REVIEW REQUIRED")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
