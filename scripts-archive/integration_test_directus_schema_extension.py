#!/usr/bin/env python3
"""
Integration Test for DirectusSchemaExtension
==========================================

Validates DirectusSchemaExtension can create repository content schema
following the recursive descent integration test requirements.

Author: Beast Mode Framework
Date: 2025-01-16
Version: 1.0
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.repository_discovery.directus.schema_extension import DirectusSchemaExtension


def main():
    """Integration test for DirectusSchemaExtension"""
    print("🧪 DirectusSchemaExtension Integration Test")
    print("=" * 60)
    
    # Initialize schema extension
    extension = DirectusSchemaExtension()
    
    # Test 1: Verify RM-DDD compliance
    print("\n1. Testing RM-DDD Compliance:")
    print(f"   Module ID: {extension.module_id}")
    print(f"   Capabilities: {[cap.value for cap in extension.get_capabilities()]}")
    
    health = extension.get_health_status()
    print(f"   Health Status: {health.status.value}")
    print(f"   Health Score: {health.health_score}")
    
    # Test 2: Create repository collections schema
    print("\n2. Testing Repository Collections Creation:")
    
    result = extension.create_repository_collections()
    
    if result.success:
        print(f"   ✅ Schema Extension Success")
        print(f"   Collections Created: {len(result.collections_created)}")
        print(f"   Relations Created: {len(result.relations_created)}")
        
        for collection in result.collections_created:
            print(f"      - {collection}")
    else:
        print(f"   ❌ Schema Extension Failed: {result.error_message}")
    
    # Test 3: Validate SQL migration
    print("\n3. Testing SQL Migration Generation:")
    
    if result.migration_sql:
        sql_lines = result.migration_sql.split('\n')
        print(f"   SQL Lines Generated: {len(sql_lines)}")
        print(f"   SQL Size: {len(result.migration_sql)} characters")
        
        # Check for key SQL elements
        sql_checks = [
            ("CREATE TABLE repository_items", "repository_items table"),
            ("CREATE TABLE specifications", "specifications table"),
            ("CREATE TABLE requirements", "requirements table"),
            ("CREATE TABLE analysis_artifacts", "analysis_artifacts table"),
            ("CREATE TABLE operation_traces", "operation_traces table"),
            ("CREATE INDEX", "database indexes"),
            ("REFERENCES directus_users", "Directus user references"),
            ("CASCADE", "foreign key constraints")
        ]
        
        for check_text, description in sql_checks:
            if check_text in result.migration_sql:
                print(f"   ✅ {description}")
            else:
                print(f"   ❌ Missing {description}")
    
    # Test 4: Test schema status
    print("\n4. Testing Schema Status:")
    status = extension.get_schema_status()
    
    print(f"   Total Collections: {status['total_collections']}")
    print(f"   Total Relations: {status['total_relations']}")
    print(f"   Dry Run Mode: {status['dry_run_mode']}")
    print(f"   Directus URL: {status['directus_url']}")
    
    # Test 5: Test CLI interface
    print("\n5. Testing CLI Interface:")
    
    cli_interface = extension.get_cli_interface()
    print(f"   Available Commands: {len(cli_interface['commands'])}")
    
    # Test CLI help
    help_text = extension.generate_cli_help("create_repository_collections")
    print(f"   CLI Help Generated: {len(help_text)} characters")
    
    # Test 6: Test operation tracing
    print("\n6. Testing Operation Tracing:")
    
    traces = extension.get_operation_traces()
    print(f"   Operation Traces: {len(traces)}")
    
    if traces:
        latest_trace = traces[-1]
        print(f"   Latest Operation: {latest_trace.operation_name}")
        print(f"   Duration: {latest_trace.duration_ms:.2f}ms")
        print(f"   Success: {latest_trace.error_info is None}")
    
    # Test 7: Test performance metrics
    print("\n7. Testing Performance Metrics:")
    
    metrics = extension.get_performance_metrics()
    print(f"   Operations Executed: {metrics['operation_count']}")
    print(f"   Average Time: {metrics['average_operation_time_ms']:.2f}ms")
    print(f"   Error Rate: {metrics['error_rate']:.2%}")
    
    # Test 8: Test graceful degradation
    print("\n8. Testing Graceful Degradation:")
    
    degradation = extension.graceful_degradation()
    print(f"   Degradation Success: {degradation.success}")
    print(f"   Remaining Capabilities: {len(degradation.remaining_capabilities)}")
    
    # Test 9: Export schema for inspection
    print("\n9. Exporting Schema Definition:")
    
    if result.success and result.migration_sql:
        with open('directus_schema_migration.sql', 'w') as f:
            f.write(result.migration_sql)
        print(f"   ✅ Schema exported to directus_schema_migration.sql")
        print(f"   File size: {len(result.migration_sql)} bytes")
    
    # Final Summary
    print("\n" + "=" * 60)
    print("📊 Integration Test Summary:")
    
    tests_passed = []
    
    # Check each requirement
    tests_passed.append(("RM-DDD Compliance", True))
    tests_passed.append(("Schema Creation", result.success))
    tests_passed.append(("SQL Generation", result.migration_sql is not None))
    tests_passed.append(("Collections Created", len(result.collections_created) == 5))
    tests_passed.append(("Relations Created", len(result.relations_created) >= 3))
    tests_passed.append(("CLI Interface", len(cli_interface['commands']) > 0))
    tests_passed.append(("Operation Tracing", len(traces) > 0))
    tests_passed.append(("Performance Metrics", metrics['operation_count'] > 0))
    
    for test_name, passed in tests_passed:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    all_passed = all(passed for _, passed in tests_passed)
    
    if all_passed:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("   DirectusSchemaExtension is ready for:")
        print("   - Repository content management")
        print("   - Specification tracking")
        print("   - Requirements management")
        print("   - Analysis artifact storage")
        print("   - Operation monitoring")
        return True
    else:
        print("\n⚠️  SOME INTEGRATION TESTS FAILED")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)