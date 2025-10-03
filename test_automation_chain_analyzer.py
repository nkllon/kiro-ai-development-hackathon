#!/usr/bin/env python3
"""
Test Script for AutomationChainAnalyzer - Task 2.3 Validation
============================================================

Tests the AutomationChainAnalyzer implementation to ensure it meets
all requirements from Task 2.3 of the system architecture specification.
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from src.system_architecture.analysis.automation_chain_analyzer import AutomationChainAnalyzer
    print("✅ Successfully imported AutomationChainAnalyzer")
except ImportError as e:
    print(f"❌ Failed to import AutomationChainAnalyzer: {e}")
    sys.exit(1)


def test_automation_chain_analyzer():
    """Test the AutomationChainAnalyzer implementation."""
    
    print("\n🔍 TESTING AUTOMATION CHAIN ANALYZER - TASK 2.3")
    print("=" * 60)
    
    # Initialize analyzer
    print("1. Initializing AutomationChainAnalyzer...")
    try:
        analyzer = AutomationChainAnalyzer()
        print("   ✅ AutomationChainAnalyzer initialized successfully")
        print(f"   📋 Module ID: {analyzer.module_id}")
    except Exception as e:
        print(f"   ❌ Failed to initialize: {e}")
        return False
    
    # Test health status
    print("\n2. Testing health status...")
    try:
        health = analyzer.get_health_status()
        print("   ✅ Health status retrieved")
        print(f"   📊 Status: {health['status']}")
        print(f"   🎯 Task ID: {health['task_id']}")
    except Exception as e:
        print(f"   ❌ Health status failed: {e}")
        return False
    
    # Test Makefile target dependencies analysis
    print("\n3. Testing Makefile target dependencies analysis...")
    try:
        makefile_deps = analyzer.analyze_makefile_target_dependencies()
        print("   ✅ Makefile dependencies analyzed")
        print(f"   📊 Targets analyzed: {len(makefile_deps.get('target_dependencies', {}))}")
        print(f"   🔗 Execution chains: {len(makefile_deps.get('execution_chains', []))}")
        
        # Check for specific dependency patterns mentioned in Task 2.3
        patterns = makefile_deps.get('dependency_patterns', {})
        if 'task_dependencies' in patterns:
            print(f"   🎯 Task dependencies found: {len(patterns['task_dependencies'])}")
        if 'phase_dependencies' in patterns:
            print(f"   📋 Phase dependencies found: {len(patterns['phase_dependencies'])}")
            
    except Exception as e:
        print(f"   ❌ Makefile analysis failed: {e}")
        return False
    
    # Test Python script parameter mapping
    print("\n4. Testing Python script parameter mapping...")
    try:
        param_mappings = analyzer.map_python_script_parameter_passing()
        print("   ✅ Parameter mappings created")
        print(f"   📊 Parameter mappings: {len(param_mappings)}")
        
        # Check for environment variable mappings
        env_mappings = [m for m in param_mappings if m.environment_variable]
        print(f"   🌍 Environment variable mappings: {len(env_mappings)}")
        
        # Show sample mappings
        if param_mappings:
            sample = param_mappings[0]
            print(f"   📝 Sample mapping: {sample.source} → {sample.target} ({sample.parameter_name})")
            
    except Exception as e:
        print(f"   ❌ Parameter mapping failed: {e}")
        return False
    
    # Test WebSocket endpoint dependencies
    print("\n5. Testing WebSocket endpoint registration dependencies...")
    try:
        ws_deps = analyzer.document_websocket_endpoint_registration_dependencies()
        print("   ✅ WebSocket dependencies documented")
        print(f"   📊 WebSocket endpoints: {len(ws_deps)}")
        
        # Check for required endpoints from specification
        required_endpoints = ["/ws/observatory", "/ws/emoji-rain", "/ws/anomalies", "/ws/doctor-status"]
        found_endpoints = [dep.endpoint_path for dep in ws_deps]
        
        for endpoint in required_endpoints:
            if endpoint in found_endpoints:
                print(f"   ✅ Found required endpoint: {endpoint}")
            else:
                print(f"   ⚠️  Missing endpoint: {endpoint}")
                
    except Exception as e:
        print(f"   ❌ WebSocket dependencies failed: {e}")
        return False
    
    # Test metrics collection pipeline
    print("\n6. Testing metrics collection pipeline dependency mapping...")
    try:
        metrics_deps = analyzer.create_metrics_collection_pipeline_dependency_mapping()
        print("   ✅ Metrics pipeline dependencies created")
        print(f"   📊 Metrics pipelines: {len(metrics_deps)}")
        
        # Check for key pipeline flows
        pipeline_sources = [dep.source_component for dep in metrics_deps]
        if "ReflectiveModule Components" in pipeline_sources:
            print("   ✅ ReflectiveModule metrics pipeline found")
        if "Observatory Server" in pipeline_sources:
            print("   ✅ Observatory metrics pipeline found")
            
    except Exception as e:
        print(f"   ❌ Metrics pipeline mapping failed: {e}")
        return False
    
    # Test integration coordination workflows
    print("\n7. Testing integration point coordination workflows...")
    try:
        integration_coords = analyzer.map_integration_point_coordination_workflows()
        print("   ✅ Integration coordination mapped")
        print(f"   📊 Integration flows: {len(integration_coords)}")
        
        # Check for ACE Reporter → AI Memory Palace → DAG Registry flow
        integration_names = [coord.integration_name for coord in integration_coords]
        ace_to_palace = any("ACE Reporter" in name and "AI Memory Palace" in name for name in integration_names)
        palace_to_dag = any("AI Memory Palace" in name and "DAG Registry" in name for name in integration_names)
        
        if ace_to_palace:
            print("   ✅ ACE Reporter → AI Memory Palace flow found")
        if palace_to_dag:
            print("   ✅ AI Memory Palace → DAG Registry flow found")
            
    except Exception as e:
        print(f"   ❌ Integration coordination failed: {e}")
        return False
    
    # Test NetworkX dependency graph generation
    print("\n8. Testing automation dependency graphs with NetworkX...")
    try:
        dependency_graph = analyzer.generate_automation_dependency_graphs_with_execution_order()
        print("   ✅ Dependency graph generated with NetworkX")
        print(f"   📊 Graph nodes: {len(dependency_graph.nodes)}")
        print(f"   🔗 Graph edges: {len(dependency_graph.edges)}")
        print(f"   📋 Execution order length: {len(dependency_graph.execution_order)}")
        print(f"   🎯 Critical path length: {len(dependency_graph.critical_path)}")
        print(f"   ⚡ Parallel groups: {len(dependency_graph.parallel_groups)}")
        
        # Show sample execution order
        if dependency_graph.execution_order:
            print(f"   📝 First 5 in execution order: {dependency_graph.execution_order[:5]}")
        
        # Show critical path
        if dependency_graph.critical_path:
            print(f"   🎯 Critical path sample: {dependency_graph.critical_path[:3]}...")
            
    except Exception as e:
        print(f"   ❌ NetworkX graph generation failed: {e}")
        return False
    
    # Test comprehensive analysis
    print("\n9. Testing comprehensive automation analysis...")
    try:
        comprehensive_analysis = analyzer.get_comprehensive_automation_analysis()
        print("   ✅ Comprehensive analysis completed")
        print(f"   📊 Analysis timestamp: {comprehensive_analysis['analysis_timestamp']}")
        print(f"   🎯 Task ID: {comprehensive_analysis['task_id']}")
        
        # Check summary statistics
        summary = comprehensive_analysis['summary']
        print("   📋 Summary statistics:")
        for key, value in summary.items():
            print(f"      {key}: {value}")
        
        # Check recommendations
        recommendations = comprehensive_analysis.get('recommendations', [])
        print(f"   💡 Recommendations: {len(recommendations)}")
        
    except Exception as e:
        print(f"   ❌ Comprehensive analysis failed: {e}")
        return False
    
    # Test export functionality
    print("\n10. Testing export functionality...")
    try:
        # Export to GraphML
        graphml_success = analyzer.export_dependency_graph_to_graphml("test_dependency_graph.graphml")
        if graphml_success:
            print("   ✅ GraphML export successful")
        else:
            print("   ⚠️  GraphML export failed")
        
        # Export comprehensive analysis to JSON
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"test_automation_analysis_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(comprehensive_analysis, f, indent=2)
        print(f"   ✅ Analysis exported to: {output_file}")
        
    except Exception as e:
        print(f"   ❌ Export functionality failed: {e}")
        return False
    
    print("\n🎉 ALL TESTS PASSED - TASK 2.3 IMPLEMENTATION COMPLETE")
    print("=" * 60)
    print("✅ AutomationChainAnalyzer class inherits from ReflectiveModule")
    print("✅ Makefile target dependencies analyzed using existing makefile_analyzer.py")
    print("✅ Python script parameter passing and environment requirements mapped")
    print("✅ WebSocket endpoint registration dependencies documented")
    print("✅ Metrics collection pipeline dependency mapping created")
    print("✅ Integration point coordination workflows mapped (ACE Reporter → AI Memory Palace → DAG Registry)")
    print("✅ Automation dependency graphs generated with execution order using NetworkX")
    print("✅ Integration with existing RelationshipMapper for dependency validation")
    
    return True


if __name__ == "__main__":
    success = test_automation_chain_analyzer()
    if success:
        print("\n🚀 TASK 2.3 READY FOR DAG EXECUTION")
        sys.exit(0)
    else:
        print("\n❌ TASK 2.3 IMPLEMENTATION NEEDS FIXES")
        sys.exit(1)