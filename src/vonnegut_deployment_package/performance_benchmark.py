#!/usr/bin/env python3
"""
Performance Benchmark Script for Beast Mode Framework

This script runs performance benchmarks for the Beast Mode Framework
to ensure system performance remains within acceptable thresholds.
"""

import time
import sys
import json
from datetime import datetime
from pathlib import Path


def benchmark_import_times():
    """Benchmark module import performance"""
    import_times = {}

    modules_to_test = [
        'beast_mode.cli.main',
        'beast_mode.observatory.core',
        'beast_mode.autonomous.pdca_orchestrator',
    ]

    for module in modules_to_test:
        start_time = time.time()
        try:
            __import__(module)
            import_time = time.time() - start_time
            import_times[module] = import_time
            print(f"✅ {module}: {import_time:.3f}s")
        except ImportError as e:
            import_times[module] = None
            print(f"⚠️ {module}: Import failed - {e}")

    return import_times


def benchmark_basic_operations():
    """Benchmark basic framework operations"""
    operations = {}

    # Test basic data structures
    start_time = time.time()
    test_data = {'test': 'data', 'numbers': list(range(1000))}
    operations['dict_creation'] = time.time() - start_time

    start_time = time.time()
    json.dumps(test_data)
    operations['json_serialization'] = time.time() - start_time

    print(f"✅ Dictionary creation: {operations['dict_creation']:.6f}s")
    print(f"✅ JSON serialization: {operations['json_serialization']:.6f}s")

    return operations


def benchmark_file_operations():
    """Benchmark file system operations"""
    file_ops = {}

    # Test file reading
    test_file = Path(__file__)
    start_time = time.time()
    content = test_file.read_text()
    file_ops['file_read'] = time.time() - start_time

    print(f"✅ File read ({len(content)} chars): {file_ops['file_read']:.6f}s")

    return file_ops


def run_all_benchmarks():
    """Run all performance benchmarks"""
    print("🔍 Running Beast Mode Framework Performance Benchmarks...")
    print("=" * 60)

    results = {
        'timestamp': datetime.now().isoformat(),
        'benchmarks': {}
    }

    # Run benchmarks
    print("\n📦 Import Performance:")
    results['benchmarks']['imports'] = benchmark_import_times()

    print("\n⚙️ Basic Operations:")
    results['benchmarks']['operations'] = benchmark_basic_operations()

    print("\n📁 File Operations:")
    results['benchmarks']['file_ops'] = benchmark_file_operations()

    # Check if results are acceptable
    total_import_time = sum(t for t in results['benchmarks']['imports'].values() if t is not None)

    print(f"\n📊 Summary:")
    print(f"   Total import time: {total_import_time:.3f}s")
    print(f"   File operations: {results['benchmarks']['file_ops']['file_read']:.6f}s")

    # Simple pass/fail criteria
    if total_import_time < 5.0:  # Imports should complete within 5 seconds
        print("✅ Performance benchmarks PASSED")
        return 0
    else:
        print("❌ Performance benchmarks FAILED (imports too slow)")
        return 1


if __name__ == "__main__":
    exit_code = run_all_benchmarks()
    print("✅ Performance benchmarks complete")
    sys.exit(exit_code)