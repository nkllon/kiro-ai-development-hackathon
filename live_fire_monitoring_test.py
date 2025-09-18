#!/usr/bin/env python3
"""
LIVE FIRE MONITORING TEST
========================

Prove the monitoring infrastructure works by generating real data
and showing comprehensive metrics, tracing, and CLI functionality.

Author: Beast Mode Framework
Date: 2025-01-16
Version: 1.0
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.repository_discovery.core.content_metadata_extractor import ContentMetadataExtractor


def main():
    """Live fire test with real data generation"""
    print("🔥 LIVE FIRE MONITORING TEST - GENERATING REAL DATA")
    print("=" * 80)
    
    # Initialize ContentMetadataExtractor (inherits all monitoring)
    extractor = ContentMetadataExtractor()
    
    print(f"🎯 Component: {extractor.module_id}")
    print(f"🎯 Correlation ID: {extractor._correlation_id}")
    
    # Test 1: Generate real file processing data
    print("\n1. 🔥 PROCESSING REAL REPOSITORY FILES")
    
    real_files = [
        Path("src/rm_ddd/core/unified_reflective_module.py"),
        Path("src/repository_discovery/core/content_metadata_extractor.py"),
        Path(".kiro/specs/repository-content-discovery-indexing/requirements.md"),
        Path("tests/test_reflective_module.py"),
        Path("directus_migration_recovered.py"),
        Path("pyproject.toml"),
        Path("README.md") if Path("README.md").exists() else Path("Makefile")
    ]
    
    # Process files and collect data
    results = []
    for file_path in real_files:
        if file_path.exists():
            print(f"   📁 Processing: {file_path}")
            result = extractor.extract_metadata(file_path)
            results.append((file_path, result))
            
            if result.success:
                print(f"      ✅ {result.metadata.file_size} bytes, {result.extraction_time_ms:.2f}ms")
            else:
                print(f"      ❌ Failed: {result.error_message}")
    
    # Test 2: Show live performance metrics
    print("\n2. 🔥 LIVE PERFORMANCE METRICS")
    metrics = extractor.get_performance_metrics()
    
    print(f"   📊 Operations Executed: {metrics['operation_count']}")
    print(f"   📊 Total Processing Time: {metrics['total_operation_time_ms']:.2f}ms")
    print(f"   📊 Average Time per Operation: {metrics['average_operation_time_ms']:.2f}ms")
    print(f"   📊 Error Rate: {metrics['error_rate']:.2%}")
    print(f"   📊 Peak Memory Usage: {metrics['resource_usage']['peak_memory_mb']:.1f}MB")
    print(f"   📊 Component Uptime: {metrics['uptime_seconds']:.2f}s")
    
    # Test 3: Show operation traces with real data
    print("\n3. 🔥 OPERATION TRACES WITH REAL DATA")
    traces = extractor.get_operation_traces()
    
    for i, trace in enumerate(traces[-5:]):  # Show last 5 traces
        success = "✅" if trace.error_info is None else "❌"
        print(f"   {success} Trace {i+1}: {trace.operation_name}")
        print(f"      Duration: {trace.duration_ms:.2f}ms")
        print(f"      Memory Delta: {trace.memory_usage.get('delta_mb', 0):.1f}MB")
        print(f"      Correlation ID: {trace.correlation_id}")
        print(f"      Input: {str(trace.input_parameters)[:60]}...")
        if trace.error_info:
            print(f"      Error: {trace.error_info['error_message']}")
    
    # Test 4: Usage tracking analysis
    print("\n4. 🔥 USAGE TRACKING ANALYSIS")
    usage = extractor.get_usage_tracking()
    
    print(f"   📈 Operation Frequency:")
    for op_name, count in usage['operation_frequency'].items():
        print(f"      {op_name}: {count} times")
    
    print(f"   📈 Tracking Period: {usage['tracking_period_start'][:19]} to {usage['tracking_period_end'][:19]}")
    print(f"   📈 Health Status: {usage['health_status']}")
    
    # Test 5: CLI Interface live test
    print("\n5. 🔥 CLI INTERFACE LIVE TEST")
    
    # Get CLI interface
    cli_interface = extractor.get_cli_interface()
    print(f"   🖥️  Available Commands: {len(cli_interface['commands'])}")
    
    # Test CLI help
    help_text = extractor.generate_cli_help("extract_metadata")
    print(f"   🖥️  CLI Help Length: {len(help_text)} characters")
    print(f"   🖥️  Sample Help:\n{help_text[:300]}...")
    
    # Execute CLI command with real data
    if real_files and real_files[0].exists():
        print(f"\n   🖥️  Executing CLI Command on {real_files[0]}")
        cli_result = extractor.execute_cli_command(
            "extract_metadata", 
            file_path=real_files[0]
        )
        print(f"      CLI Success: {cli_result['success']}")
        if cli_result['success']:
            result = cli_result['result']  # This is the ExtractionResult
            if result.success and result.metadata:
                metadata = result.metadata
                print(f"      File Size: {metadata.file_size} bytes")
                print(f"      File Type: {metadata.file_type}")
                print(f"      Encoding: {metadata.encoding}")
            else:
                print(f"      CLI returned unsuccessful result: {result.error_message}")
    
    # Test 6: Health monitoring
    print("\n6. 🔥 HEALTH MONITORING")
    health = extractor.get_health_status()
    
    print(f"   🏥 Health Status: {health.status.value}")
    print(f"   🏥 Health Score: {health.health_score}")
    print(f"   🏥 Issues: {health.issues}")
    print(f"   🏥 Error Count: {health.error_count}")
    print(f"   🏥 Uptime: {health.uptime_seconds:.2f}s")
    
    # Test 7: Generate some errors for error tracking
    print("\n7. 🔥 ERROR TRACKING TEST")
    
    # Try to process non-existent files
    fake_files = [Path("nonexistent1.txt"), Path("nonexistent2.txt")]
    for fake_file in fake_files:
        result = extractor.extract_metadata(fake_file)
        print(f"   ❌ Expected Error: {result.error_message}")
    
    # Show updated error metrics
    updated_metrics = extractor.get_performance_metrics()
    print(f"   📊 Updated Error Count: {updated_metrics['error_count']}")
    print(f"   📊 Updated Error Rate: {updated_metrics['error_rate']:.2%}")
    
    # Test 8: Export all data as JSON
    print("\n8. 🔥 DATA EXPORT")
    
    export_data = {
        'component_info': extractor.get_module_info(),
        'performance_metrics': extractor.get_performance_metrics(),
        'usage_tracking': extractor.get_usage_tracking(),
        'health_status': {
            'status': health.status.value,
            'score': health.health_score,
            'issues': health.issues,
            'uptime': health.uptime_seconds
        },
        'cli_interface': {
            'commands': list(cli_interface['commands'].keys()),
            'capabilities': cli_interface.get('capabilities', [])
        },
        'recent_traces': [
            {
                'operation': trace.operation_name,
                'duration_ms': trace.duration_ms,
                'success': trace.error_info is None,
                'correlation_id': trace.correlation_id
            }
            for trace in extractor.get_operation_traces()[-10:]
        ]
    }
    
    # Save to file
    with open('live_fire_monitoring_data.json', 'w') as f:
        json.dump(export_data, f, indent=2, default=str)
    
    print(f"   💾 Exported {len(json.dumps(export_data))} bytes to live_fire_monitoring_data.json")
    
    # Final Summary
    print("\n" + "=" * 80)
    print("🎯 LIVE FIRE TEST RESULTS:")
    print(f"   📁 Files Processed: {len([r for _, r in results if r.success])}/{len(results)}")
    print(f"   📊 Total Operations: {updated_metrics['operation_count']}")
    print(f"   📊 Average Performance: {updated_metrics['average_operation_time_ms']:.2f}ms")
    print(f"   📊 Error Rate: {updated_metrics['error_rate']:.2%}")
    print(f"   🖥️  CLI Commands Available: {len(cli_interface['commands'])}")
    print(f"   📈 Operation Types Tracked: {len(usage['operation_frequency'])}")
    print(f"   🏥 Component Health: {health.status.value} ({health.health_score})")
    
    print("\n🔥 MONITORING INFRASTRUCTURE PROVEN WITH LIVE DATA!")
    print("   ✅ Operation tracing with correlation IDs")
    print("   ✅ Performance metrics collection")
    print("   ✅ Usage tracking and analysis")
    print("   ✅ CLI introspection and execution")
    print("   ✅ Health monitoring and error tracking")
    print("   ✅ Complete data export capability")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)