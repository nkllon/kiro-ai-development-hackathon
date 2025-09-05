#!/usr/bin/env python3
"""
Demo script for Test RCA Integration Layer
Shows how to use the RCA integration to analyze test failures
"""

from datetime import datetime
from src.beast_mode.testing.rca_integration import TestRCAIntegrator, TestFailure


def create_sample_test_failures():
    """Create sample test failures for demonstration"""
    base_time = datetime.now()
    
    return [
        TestFailure(
            test_name="test_import_missing_module",
            test_file="tests/test_imports.py",
            failure_type="error",
            error_message="ImportError: No module named 'nonexistent_module'",
            stack_trace="Traceback (most recent call last):\n  File \"tests/test_imports.py\", line 5, in test_import_missing_module\n    import nonexistent_module\nImportError: No module named 'nonexistent_module'",
            test_function="test_import_missing_module",
            test_class="TestImports",
            failure_timestamp=base_time,
            test_context={"test_type": "unit", "test_category": "imports"},
            pytest_node_id="tests/test_imports.py::TestImports::test_import_missing_module"
        ),
        TestFailure(
            test_name="test_file_not_found",
            test_file="tests/test_files.py",
            failure_type="error",
            error_message="FileNotFoundError: No such file or directory: 'missing_config.json'",
            stack_trace="Traceback (most recent call last):\n  File \"tests/test_files.py\", line 10, in test_file_not_found\n    with open('missing_config.json') as f:\nFileNotFoundError: No such file or directory: 'missing_config.json'",
            test_function="test_file_not_found",
            test_class="TestFiles",
            failure_timestamp=base_time,
            test_context={"test_type": "integration", "test_category": "file_operations"},
            pytest_node_id="tests/test_files.py::TestFiles::test_file_not_found"
        ),
        TestFailure(
            test_name="test_assertion_failure",
            test_file="tests/test_logic.py",
            failure_type="assertion",
            error_message="AssertionError: Expected result to be 42, but got 24",
            stack_trace="Traceback (most recent call last):\n  File \"tests/test_logic.py\", line 15, in test_assertion_failure\n    assert result == 42, f\"Expected result to be 42, but got {result}\"\nAssertionError: Expected result to be 42, but got 24",
            test_function="test_assertion_failure",
            test_class="TestLogic",
            failure_timestamp=base_time,
            test_context={"test_type": "unit", "test_category": "business_logic"},
            pytest_node_id="tests/test_logic.py::TestLogic::test_assertion_failure"
        )
    ]


def demonstrate_rca_integration():
    """Demonstrate RCA integration functionality"""
    print("🔍 Test RCA Integration Demo")
    print("=" * 50)
    
    # Create RCA integrator
    print("\n1. Initializing RCA Integration Engine...")
    integrator = TestRCAIntegrator()
    print(f"   ✅ Engine initialized: {integrator.module_name}")
    print(f"   ✅ Health status: {'Healthy' if integrator.is_healthy() else 'Degraded'}")
    
    # Create sample test failures
    print("\n2. Creating sample test failures...")
    test_failures = create_sample_test_failures()
    print(f"   ✅ Created {len(test_failures)} test failures")
    
    for i, failure in enumerate(test_failures, 1):
        print(f"   {i}. {failure.test_name}: {failure.error_message[:50]}...")
    
    # Analyze test failures
    print("\n3. Analyzing test failures with RCA...")
    report = integrator.analyze_test_failures(test_failures)
    
    print(f"   ✅ Analysis complete!")
    print(f"   📊 Total failures: {report.total_failures}")
    print(f"   📊 Failures analyzed: {report.failures_analyzed}")
    print(f"   📊 Failure groups: {len(report.grouped_failures)}")
    print(f"   📊 RCA results: {len(report.rca_results)}")
    
    # Show failure grouping
    print("\n4. Failure Grouping Results:")
    for group_name, failures in report.grouped_failures.items():
        print(f"   📁 Group '{group_name}': {len(failures)} failures")
        for failure in failures:
            print(f"      - {failure.test_name}")
    
    # Show summary
    print("\n5. RCA Summary:")
    summary = report.summary
    print(f"   🎯 Confidence Score: {summary.confidence_score:.2f}")
    print(f"   🔧 Systematic Fixes Available: {summary.systematic_fixes_available}")
    print(f"   📋 Pattern Matches Found: {summary.pattern_matches_found}")
    print(f"   ⏱️  Estimated Fix Time: {summary.estimated_fix_time_minutes} minutes")
    
    if summary.most_common_root_causes:
        print(f"   🔍 Most Common Root Causes:")
        for cause_type, count in summary.most_common_root_causes[:3]:
            print(f"      - {cause_type.value}: {count} occurrences")
    
    if summary.critical_issues:
        print(f"   ⚠️  Critical Issues:")
        for issue in summary.critical_issues[:3]:
            print(f"      - {issue}")
    
    # Show recommendations
    print("\n6. Recommendations:")
    for i, recommendation in enumerate(report.recommendations[:5], 1):
        print(f"   {i}. {recommendation}")
    
    # Show next steps
    print("\n7. Next Steps:")
    for i, step in enumerate(report.next_steps[:5], 1):
        print(f"   {i}. {step}")
    
    # Show detailed RCA results
    if report.rca_results:
        print("\n8. Detailed RCA Results:")
        for i, rca_result in enumerate(report.rca_results[:2], 1):  # Show first 2
            print(f"   🔍 RCA Result {i}:")
            print(f"      Component: {rca_result.failure.component}")
            print(f"      Analysis Time: {rca_result.total_analysis_time_seconds:.2f}s")
            print(f"      Confidence: {rca_result.rca_confidence_score:.2f}")
            print(f"      Root Causes: {len(rca_result.root_causes)}")
            print(f"      Systematic Fixes: {len(rca_result.systematic_fixes)}")
            
            if rca_result.root_causes:
                print(f"      Top Root Cause: {rca_result.root_causes[0].description}")
            
            if rca_result.systematic_fixes:
                print(f"      Top Fix: {rca_result.systematic_fixes[0].fix_description}")
    
    # Show integration metrics
    print("\n9. Integration Metrics:")
    status = integrator.get_module_status()
    print(f"   📈 Test Failures Processed: {status['test_failures_processed']}")
    print(f"   📈 Successful RCA Analyses: {status['successful_rca_analyses']}")
    print(f"   📈 Pattern Matches Found: {status['pattern_matches_found']}")
    print(f"   📈 Average Analysis Time: {status['average_analysis_time']:.2f}s")
    
    print("\n✅ Demo completed successfully!")
    print("=" * 50)


def demonstrate_failure_prioritization():
    """Demonstrate failure prioritization functionality"""
    print("\n🎯 Failure Prioritization Demo")
    print("=" * 30)
    
    integrator = TestRCAIntegrator()
    test_failures = create_sample_test_failures()
    
    # Show original order
    print("\nOriginal failure order:")
    for i, failure in enumerate(test_failures, 1):
        print(f"   {i}. {failure.test_name}")
    
    # Show prioritized order
    prioritized = integrator.prioritize_failures(test_failures)
    print("\nPrioritized failure order:")
    for i, failure in enumerate(prioritized, 1):
        priority = integrator._get_failure_priority(failure)
        score = integrator._calculate_failure_priority_score(failure)
        print(f"   {i}. {failure.test_name} (Priority: {priority.value}, Score: {score:.1f})")


def demonstrate_failure_categorization():
    """Demonstrate failure categorization functionality"""
    print("\n🏷️  Failure Categorization Demo")
    print("=" * 35)
    
    integrator = TestRCAIntegrator()
    test_failures = create_sample_test_failures()
    
    print("\nFailure categorization:")
    for failure in test_failures:
        rca_failure = integrator.convert_to_rca_failure(failure)
        print(f"   {failure.test_name}:")
        print(f"      Error: {failure.error_message[:50]}...")
        print(f"      Category: {rca_failure.category.value}")
        print(f"      Component: {rca_failure.component}")
        print()


if __name__ == "__main__":
    try:
        demonstrate_rca_integration()
        demonstrate_failure_prioritization()
        demonstrate_failure_categorization()
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()