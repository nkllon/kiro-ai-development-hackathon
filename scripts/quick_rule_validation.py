#!/usr/bin/env python3
"""
Quick Rule Firing Validation Tool
Built in 1 hour for immediate testing!
"""

import time
from pathlib import Path

from scripts.mdc_parser import MDCParser
from scripts.rule_firing_identifier import RuleFiringIdentifier


def quick_validation():
    """Quick validation of rule firing system"""
    print("🚀 QUICK RULE VALIDATION - 1 HOUR BUILD!")
    print("=" * 50)

    # Initialize tools
    rfi = RuleFiringIdentifier()
    parser = MDCParser()

    # Test 1: Basic functionality
    print("\n🧪 Test 1: Basic Rule Firing")
    test_basic_functionality(rfi)

    # Test 2: Performance with all files
    print("\n⚡ Test 2: Performance Test")
    test_performance(rfi)

    # Test 3: Edge cases
    print("\n🎭 Test 3: Edge Cases")
    test_edge_cases(rfi)

    # Test 4: MDC parsing
    print("\n📄 Test 4: MDC Parsing")
    test_mdc_parsing(parser)

    print("\n🎉 QUICK VALIDATION COMPLETE!")


def test_basic_functionality(rfi):
    """Test basic rule firing functionality"""
    print("  Testing rule firing for deterministic-editing.mdc...")

    # Test with different operations
    operations = ["formatting", "editing", "linting", "nonexistent"]

    for op in operations:
        try:
            rfi.print_firing_rules(".cursor/rules/deterministic-editing.mdc", op)
        except Exception as e:
            print(f"    ❌ Error with operation '{op}': {e}")


def test_performance(rfi):
    """Test performance with all MDC files"""
    print("  Testing performance with all MDC files...")

    mdc_files = list(Path(".cursor/rules").glob("*.mdc"))
    print(f"    Found {len(mdc_files)} MDC files")

    start_time = time.time()

    for file_path in mdc_files[:5]:  # Test first 5 files
        try:
            rfi.identify_firing_rules(str(file_path), "testing")
        except Exception as e:
            print(f"    ❌ Error with {file_path}: {e}")

    end_time = time.time()
    print(f"    Performance: {end_time - start_time:.3f} seconds for 5 files")


def test_edge_cases(rfi):
    """Test edge cases and error handling"""
    print("  Testing edge cases...")

    # Test nonexistent file
    try:
        rfi.identify_firing_rules("nonexistent.mdc", "testing")
        print("    ✅ Handled nonexistent file gracefully")
    except Exception as e:
        print(f"    ❌ Error with nonexistent file: {e}")

    # Test weird operation
    try:
        rfi.identify_firing_rules(".cursor/rules/security.mdc", "weird_operation_123")
        print("    ✅ Handled weird operation gracefully")
    except Exception as e:
        print(f"    ❌ Error with weird operation: {e}")


def test_mdc_parsing(parser):
    """Test MDC parsing functionality"""
    print("  Testing MDC parsing...")

    mdc_files = list(Path(".cursor/rules").glob("*.mdc"))

    for file_path in mdc_files[:3]:  # Test first 3 files
        try:
            result = parser.parse_mdc(str(file_path))
            print(f"    ✅ {file_path}: {len(result[0])} YAML fields, {len(result[1])} content chars")
        except Exception as e:
            print(f"    ❌ {file_path}: {e}")


if __name__ == "__main__":
    quick_validation()
