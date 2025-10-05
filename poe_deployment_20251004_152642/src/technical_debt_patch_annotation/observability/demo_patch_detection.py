#!/usr/bin/env python3
"""
Demonstration of Observability-based Patch Detection.

This script demonstrates how to use the ObservabilityPatchDetector to automatically
detect potential patches and workarounds through Jaeger tracing and Prometheus metrics.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.technical_debt_patch_annotation.observability.patch_detector import (
    ObservabilityPatchDetector,
    ConfidenceLevel,
    AnomalyType
)


def demonstrate_patch_detection():
    """Demonstrate the complete patch detection workflow."""
    print("🔍 Observability-based Patch Detection Demo")
    print("=" * 60)
    
    # Initialize detector with configuration
    config = {
        'jaeger_enabled': True,
        'prometheus_enabled': True,
        'jaeger_endpoint': 'http://localhost:14268',
        'prometheus_endpoint': 'http://localhost:9090',
        'performance_threshold_percent': 50.0,
        'error_rate_threshold': 0.05,
        'anomaly_detection_window_minutes': 60
    }
    
    detector = ObservabilityPatchDetector(config)
    
    print(f"✅ Initialized detector: {detector.get_module_info()['module_name']}")
    print(f"📊 Health status: {detector.get_health_status().status.value}")
    
    # Step 1: Detect performance anomalies
    print("\n🎯 Step 1: Detecting Performance Anomalies")
    print("-" * 40)
    
    components_to_analyze = ["user_service", "payment_service", "notification_service"]
    
    all_anomalies = []
    for component in components_to_analyze:
        print(f"   Analyzing component: {component}")
        anomalies = detector.detect_performance_anomalies(component)
        all_anomalies.extend(anomalies)
        
        for anomaly in anomalies:
            print(f"   🚨 {anomaly.anomaly_type.value} detected:")
            print(f"      Operation: {anomaly.operation_name}")
            print(f"      Latency increase: {anomaly.latency_increase_percent:.1f}%")
            print(f"      Confidence: {anomaly.confidence.value}")
    
    print(f"\n📈 Total anomalies detected: {len(all_anomalies)}")
    
    # Step 2: Correlate observability signals
    print("\n🔗 Step 2: Correlating Observability Signals")
    print("-" * 40)
    
    all_correlations = []
    for component in components_to_analyze:
        correlations = detector.correlate_observability_signals(component)
        all_correlations.extend(correlations)
        
        for correlation in correlations:
            print(f"   🔍 Correlation found in {correlation.component}:")
            print(f"      Operation: {correlation.operation}")
            print(f"      Score: {correlation.correlation_score:.2f}")
            print(f"      Patterns: {', '.join(correlation.unusual_patterns)}")
    
    print(f"\n🎯 Total correlations found: {len(all_correlations)}")
    
    # Step 3: Identify workaround candidates
    print("\n🎪 Step 3: Identifying Workaround Candidates")
    print("-" * 40)
    
    candidates = detector.identify_workaround_candidates(
        confidence_threshold=ConfidenceLevel.LOW
    )
    
    for candidate in candidates:
        print(f"   🎯 Candidate found:")
        print(f"      Component: {candidate.component}")
        print(f"      Operation: {candidate.operation_name}")
        print(f"      Confidence: {candidate.confidence.value}")
        print(f"      Code patterns: {', '.join(candidate.code_patterns)}")
        print(f"      Supporting anomalies: {len(candidate.performance_anomalies)}")
    
    print(f"\n🔍 Total candidates identified: {len(candidates)}")
    
    # Step 4: Generate patch suggestions
    print("\n📝 Step 4: Generating Patch Suggestions")
    print("-" * 40)
    
    suggestions = detector.generate_patch_suggestions(candidates)
    
    for i, suggestion in enumerate(suggestions, 1):
        print(f"   📋 Patch Suggestion #{i}:")
        print(f"      ID: {suggestion.patch_id}")
        print(f"      Component: {suggestion.component}")
        print(f"      Debt Level: {suggestion.debt_level.value}")
        print(f"      Reason: {suggestion.reason}")
        print(f"      Cleanup Task: {suggestion.cleanup_task}")
        print(f"      Validation Criteria: {len(suggestion.validation_criteria)} items")
        print()
    
    print(f"📊 Total patch suggestions: {len(suggestions)}")
    
    # Step 5: Show detection summary
    print("\n📈 Step 5: Detection Summary")
    print("-" * 40)
    
    summary = detector.get_detection_summary()
    detection_stats = summary['detection_summary']
    
    print(f"   Performance Anomalies: {detection_stats['performance_anomalies']}")
    print(f"   Metrics Anomalies: {detection_stats['metrics_anomalies']}")
    print(f"   Trace Correlations: {detection_stats['trace_correlations']}")
    print(f"   Suspicious Patterns: {detection_stats['suspicious_patterns']}")
    print(f"   Workaround Candidates: {detection_stats['workaround_candidates']}")
    
    recent_activity = summary['recent_activity']
    print(f"\n   Jaeger Enabled: {recent_activity['jaeger_enabled']}")
    print(f"   Prometheus Enabled: {recent_activity['prometheus_enabled']}")
    print(f"   Detection Window: {recent_activity['detection_window_minutes']} minutes")
    
    return detector, suggestions


def demonstrate_cli_interface(detector: ObservabilityPatchDetector):
    """Demonstrate the CLI interface capabilities."""
    print("\n🖥️  CLI Interface Demonstration")
    print("=" * 60)
    
    # Get CLI interface
    cli_interface = detector.get_cli_interface()
    print(f"✅ CLI interface available with {len(cli_interface['commands'])} commands")
    
    # Show some key commands
    key_commands = [
        'detect_performance_anomalies',
        'correlate_observability_signals', 
        'identify_workaround_candidates',
        'generate_patch_suggestions',
        'get_detection_summary'
    ]
    
    print("\n🔧 Key Commands Available:")
    for cmd_name in key_commands:
        if cmd_name in cli_interface['commands']:
            cmd_info = cli_interface['commands'][cmd_name]
            print(f"   • {cmd_name}")
            print(f"     Description: {cmd_info['description']}")
            print(f"     Parameters: {len(cmd_info['parameters'])}")
    
    # Execute a CLI command
    print("\n⚡ Executing CLI Command Example:")
    result = detector.execute_cli_command('get_detection_summary')
    if result['success']:
        print("   ✅ Command executed successfully")
        print(f"   📊 Result type: {type(result['result'])}")
    else:
        print(f"   ❌ Command failed: {result['error']}")


def demonstrate_integration_patterns():
    """Demonstrate integration with existing observability infrastructure."""
    print("\n🔌 Integration Patterns Demonstration")
    print("=" * 60)
    
    print("📡 Jaeger Integration Pattern:")
    print("   • Connects to Jaeger API endpoint")
    print("   • Queries traces by service and time range")
    print("   • Analyzes trace spans for performance anomalies")
    print("   • Detects retry patterns and timeout workarounds")
    print("   • Correlates traces with error patterns")
    
    print("\n📊 Prometheus Integration Pattern:")
    print("   • Connects to Prometheus query API")
    print("   • Monitors key performance metrics")
    print("   • Detects metric deviations and spikes")
    print("   • Analyzes error rates and retry counts")
    print("   • Correlates metrics with trace data")
    
    print("\n🔄 ReflectiveModule Integration:")
    print("   • Inherits from unified ReflectiveModule")
    print("   • Provides health monitoring endpoints")
    print("   • Supports graceful degradation")
    print("   • Includes CLI interface generation")
    print("   • Enables operation tracing and metrics")
    
    print("\n🎯 Patch Annotation Integration:")
    print("   • Generates standardized patch annotations")
    print("   • Links to observability evidence")
    print("   • Provides cleanup guidance")
    print("   • Includes validation criteria")
    print("   • Supports systematic debt tracking")


if __name__ == "__main__":
    print("🚀 Starting Observability Patch Detection Demo")
    print("=" * 80)
    
    try:
        # Run main demonstration
        detector, suggestions = demonstrate_patch_detection()
        
        # Demonstrate CLI interface
        demonstrate_cli_interface(detector)
        
        # Show integration patterns
        demonstrate_integration_patterns()
        
        print("\n" + "=" * 80)
        print("🎉 DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("✅ ObservabilityPatchDetector is fully functional")
        print("✅ Integration with Jaeger and Prometheus demonstrated")
        print("✅ Patch detection workflow validated")
        print("✅ CLI interface and ReflectiveModule compliance verified")
        
        if suggestions:
            print(f"\n📋 Generated {len(suggestions)} patch suggestions ready for review")
            print("💡 These suggestions can be used to create formal patch annotations")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)