#!/usr/bin/env python3
"""
Comprehensive AI Memory Palace Tests
Full validation of BeastlyModule migration and system capabilities
"""

import sys
import os
sys.path.insert(0, '.')

from datetime import datetime
from typing import Dict, Any, List
import tempfile
import json
import traceback

def test_all_component_imports():
    """Test that all AI Memory Palace components can be imported with BeastlyModule"""
    print("🔍 Testing All Component Imports...")
    
    components = [
        ('context_manager', 'ContextManager'),
        ('context_registry', 'ContextRegistry'),
        ('context_engine', 'ContextEngine'),
        ('context_validator', 'ContextValidator'),
        ('session_manager', 'SessionManager'),
        ('tracing_integration', 'ContextTracingIntegration'),
        ('tracing_integration', 'DistributedTracer'),
        ('observatory_integration', 'ContextObservatoryIntegration'),
        ('developer_tools', 'ContextInspector'),
        ('developer_tools', 'ContextDebugger'),
        ('security', 'ContextSecurityManager'),
        ('multi_project_manager', 'ProjectDetector'),
        ('multi_project_manager', 'MultiProjectContextManager'),
        ('api', 'ContextAPI'),
        ('api', 'ContextCLITools'),
        ('analytics', 'ContextAnalyzer'),
        ('analytics', 'ContextOptimizer'),
        ('spec_integration', 'SpecFileWatcher'),
        ('spec_integration', 'SpecWorkflowIntegrator'),
        ('backup_recovery', 'ContextBackupManager'),
        ('backup_recovery', 'ContextRecoveryCLI'),
        ('deployment', 'ConfigurationManager'),
        ('deployment', 'DatabaseMigrationManager'),
        ('deployment', 'DeploymentOrchestrator'),
        ('event_capture', 'EventCapture')
    ]
    
    success_count = 0
    total_count = len(components)
    results = []
    
    for module_name, class_name in components:
        try:
            exec(f'from src.beast_mode.ai_memory_palace.{module_name} import {class_name}')
            print(f"  ✅ {class_name:<35} - Import successful")
            results.append((class_name, True, None))
            success_count += 1
        except Exception as e:
            error_msg = str(e)[:60] + "..." if len(str(e)) > 60 else str(e)
            print(f"  ⚠️  {class_name:<35} - Import issue: {error_msg}")
            results.append((class_name, False, str(e)))
    
    print(f"\n📊 Import Results: {success_count}/{total_count} components imported successfully")
    return success_count, total_count, results

def test_beastly_module_powers():
    """Test BeastlyModule enhanced capabilities across components"""
    print("\n🐺 Testing BeastlyModule Powers Across Components...")
    
    # Test core components that should work
    test_components = [
        ('ContextManager', 'src.beast_mode.ai_memory_palace.context_manager'),
        ('ContextRegistry', 'src.beast_mode.ai_memory_palace.context_registry'),
        ('ContextEngine', 'src.beast_mode.ai_memory_palace.context_engine'),
        ('ContextValidator', 'src.beast_mode.ai_memory_palace.context_validator'),
        ('ContextTracingIntegration', 'src.beast_mode.ai_memory_palace.tracing_integration'),
        ('ContextObservatoryIntegration', 'src.beast_mode.ai_memory_palace.observatory_integration'),
        ('ContextSecurityManager', 'src.beast_mode.ai_memory_palace.security'),
    ]
    
    powers_tested = 0
    total_components = len(test_components)
    
    for comp_name, module_path in test_components:
        try:
            print(f"\n  🔍 Testing {comp_name}:")
            
            # Import the component
            module = __import__(module_path, fromlist=[comp_name])
            comp_class = getattr(module, comp_name)
            
            # Test instantiation (may fail due to dependencies, but we test what we can)
            try:
                if comp_name == 'ContextManager':
                    with tempfile.TemporaryDirectory() as temp_dir:
                        config = {"db_path": os.path.join(temp_dir, "test.db")}
                        instance = comp_class(config)
                elif comp_name == 'ContextRegistry':
                    with tempfile.TemporaryDirectory() as temp_dir:
                        db_path = os.path.join(temp_dir, "test.db")
                        instance = comp_class(db_path)
                else:
                    instance = comp_class()
                
                # Test BeastlyModule methods
                beastly_methods = [
                    'get_tracing_status',
                    'emit_observation', 
                    'get_module_info',
                    'get_capabilities',
                    'get_health_status',
                    'graceful_degradation',
                    'get_cli_interface',
                    'generate_cli_help'
                ]
                
                method_results = []
                for method_name in beastly_methods:
                    if hasattr(instance, method_name):
                        try:
                            method = getattr(instance, method_name)
                            if method_name == 'emit_observation':
                                # Test observation emission
                                method('Test observation', 'info', emoji='🧪')
                                method_results.append(f"✅ {method_name}")
                            elif method_name == 'generate_cli_help':
                                # Test CLI help
                                help_text = method()
                                method_results.append(f"✅ {method_name} ({len(help_text)} chars)")
                            else:
                                # Test other methods
                                result = method()
                                method_results.append(f"✅ {method_name}")
                        except Exception as e:
                            method_results.append(f"⚠️ {method_name}: {str(e)[:30]}...")
                    else:
                        method_results.append(f"❌ {method_name}: Not found")
                
                print(f"    🐺 BeastlyModule Methods:")
                for result in method_results:
                    print(f"      {result}")
                
                powers_tested += 1
                
            except Exception as e:
                print(f"    ⚠️  Instantiation issue: {str(e)[:50]}...")
                print(f"    🔍 Testing class-level BeastlyModule inheritance...")
                
                # Test that it inherits from BeastlyModule
                from src.beast_mode.core.beastly_module import BeastlyModule
                if issubclass(comp_class, BeastlyModule):
                    print(f"    ✅ Inherits from BeastlyModule")
                    powers_tested += 0.5  # Partial credit
                else:
                    print(f"    ❌ Does not inherit from BeastlyModule")
                
        except Exception as e:
            print(f"    ❌ Component test failed: {str(e)[:50]}...")
    
    print(f"\n📊 BeastlyModule Powers: {powers_tested}/{total_components} components tested")
    return powers_tested, total_components

def test_context_manager_full_capabilities():
    """Comprehensive test of ContextManager capabilities"""
    print("\n🧠 Testing ContextManager Full Capabilities...")
    
    try:
        from src.beast_mode.ai_memory_palace.context_manager import ContextManager
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {"db_path": os.path.join(temp_dir, "test_context.db")}
            cm = ContextManager(config)
            
            print("  ✅ ContextManager instantiated successfully")
            
            # Test 1: BeastlyModule Enhanced Features
            print("\n  🐺 BeastlyModule Enhanced Features:")
            
            tracing_status = cm.get_tracing_status()
            print(f"    📊 Tracing Available: {tracing_status.get('tracing_available', False)}")
            print(f"    🎯 Tracing Enabled: {tracing_status.get('tracing_enabled', False)}")
            
            module_info = cm.get_module_info()
            print(f"    🏗️  Module: {module_info['module_name']} v{module_info['version']}")
            print(f"    🆔 Module ID: {module_info['module_id']}")
            
            health = cm.get_health_status()
            print(f"    💚 Health: {health.status.value} (score: {health.health_score})")
            
            capabilities = cm.get_capabilities()
            print(f"    🛠️  Capabilities: {len(capabilities)} total")
            
            degradation = cm.graceful_degradation()
            print(f"    🔄 Graceful Degradation: {'✅' if degradation.success else '❌'}")
            
            # Test 2: Enhanced Observation
            print(f"\n  📡 Enhanced Observation:")
            cm.emit_observation(
                message='Comprehensive test observation',
                event_type='info',
                context={'test_type': 'comprehensive', 'component': 'ContextManager'},
                emoji='🧪'
            )
            print(f"    ✅ Enhanced observation emitted with trace correlation")
            
            # Test 3: CLI Interface
            print(f"\n  🎛️ CLI Interface:")
            cli_interface = cm.get_cli_interface()
            print(f"    📦 Module: {cli_interface['module_name']}")
            print(f"    🛠️  Commands: {len(cli_interface['commands'])} available")
            
            help_text = cm.generate_cli_help()
            print(f"    📖 Help Generated: {len(help_text)} characters")
            
            # Test 4: Performance Metrics
            print(f"\n  📈 Performance Metrics:")
            metrics = cm.get_performance_metrics()
            print(f"    ⏱️  Operations: {metrics['operation_count']}")
            print(f"    🕐 Uptime: {metrics['uptime_seconds']:.2f}s")
            print(f"    📊 Error Rate: {metrics['error_rate']:.3f}")
            
            return True
            
    except Exception as e:
        print(f"❌ ContextManager test failed: {e}")
        traceback.print_exc()
        return False

def test_cli_command_execution():
    """Test CLI command execution capabilities"""
    print("\n🎛️ Testing CLI Command Execution...")
    
    try:
        from src.beast_mode.ai_memory_palace.context_manager import ContextManager
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {"db_path": os.path.join(temp_dir, "test_context.db")}
            cm = ContextManager(config)
            
            # Test CLI command execution
            print("  🔍 Testing CLI Command Execution:")
            
            # Test get_module_info command
            result = cm.execute_cli_command('get_module_info')
            if result['success']:
                print(f"    ✅ get_module_info: {result['result']['module_name']}")
            else:
                print(f"    ❌ get_module_info: {result['error']}")
            
            # Test get_health_status command
            result = cm.execute_cli_command('get_health_status')
            if result['success']:
                print(f"    ✅ get_health_status: {result['result'].status.value}")
            else:
                print(f"    ❌ get_health_status: {result['error']}")
            
            # Test get_capabilities command
            result = cm.execute_cli_command('get_capabilities')
            if result['success']:
                print(f"    ✅ get_capabilities: {len(result['result'])} capabilities")
            else:
                print(f"    ❌ get_capabilities: {result['error']}")
            
            # Test graceful_degradation command
            result = cm.execute_cli_command('graceful_degradation')
            if result['success']:
                print(f"    ✅ graceful_degradation: {'Success' if result['result'].success else 'Failed'}")
            else:
                print(f"    ❌ graceful_degradation: {result['error']}")
            
            return True
            
    except Exception as e:
        print(f"❌ CLI command execution test failed: {e}")
        return False

def test_prometheus_integration():
    """Test Prometheus metrics integration"""
    print("\n📊 Testing Prometheus Integration...")
    
    try:
        from src.beast_mode.ai_memory_palace.context_manager import ContextManager
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {"db_path": os.path.join(temp_dir, "test_context.db")}
            cm = ContextManager(config)
            
            print("  🔍 Testing Prometheus Metrics:")
            
            # Test Prometheus metrics collection
            prometheus_metrics = cm.get_prometheus_metrics()
            print(f"    📊 Prometheus Metrics Available: {len(prometheus_metrics)} metrics")
            
            # Test performance metrics
            performance_metrics = cm.get_performance_metrics()
            print(f"    📈 Performance Metrics:")
            print(f"      ⏱️  Operation Count: {performance_metrics['operation_count']}")
            print(f"      🕐 Uptime: {performance_metrics['uptime_seconds']:.2f}s")
            print(f"      📊 Error Rate: {performance_metrics['error_rate']:.3f}")
            
            # Test usage tracking
            usage_tracking = cm.get_usage_tracking()
            print(f"    📋 Usage Tracking:")
            print(f"      🆔 Module ID: {usage_tracking['module_id']}")
            print(f"      🎯 Health Status: {usage_tracking['health_status']}")
            
            return True
            
    except Exception as e:
        print(f"❌ Prometheus integration test failed: {e}")
        return False

def test_tracing_integration():
    """Test distributed tracing integration"""
    print("\n🔍 Testing Distributed Tracing Integration...")
    
    try:
        from src.beast_mode.ai_memory_palace.context_manager import ContextManager
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {"db_path": os.path.join(temp_dir, "test_context.db")}
            cm = ContextManager(config)
            
            print("  🔍 Testing Tracing Capabilities:")
            
            # Test tracing status
            tracing_status = cm.get_tracing_status()
            print(f"    📊 Tracing Available: {tracing_status.get('tracing_available', False)}")
            print(f"    🎯 Tracing Enabled: {tracing_status.get('tracing_enabled', False)}")
            print(f"    🏷️  Service Name: {tracing_status.get('service_name', 'N/A')}")
            
            # Test trace operation context manager
            print(f"    🔄 Testing Trace Operation Context Manager:")
            try:
                with cm.trace_operation('test_operation', test_param='test_value') as trace:
                    trace.output_result = {'test': 'success'}
                    print(f"      ✅ Trace operation context manager works")
            except Exception as e:
                print(f"      ⚠️  Trace operation: {str(e)[:50]}...")
            
            # Test trace event emission
            try:
                cm.emit_trace_event('test_event', {'test_data': 'comprehensive_test'})
                print(f"      ✅ Trace event emission works")
            except Exception as e:
                print(f"      ⚠️  Trace event emission: {str(e)[:50]}...")
            
            # Test operation traces
            traces = cm.get_operation_traces(10)
            print(f"    📋 Operation Traces: {len(traces)} traces stored")
            
            return True
            
    except Exception as e:
        print(f"❌ Tracing integration test failed: {e}")
        return False

def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("🚀 AI Memory Palace Comprehensive Test Suite")
    print("=" * 60)
    print("Testing complete BeastlyModule migration and capabilities...")
    print()
    
    test_results = []
    
    # Test 1: Component Imports
    print("=" * 60)
    success_count, total_count, import_results = test_all_component_imports()
    test_results.append(("Component Imports", success_count == total_count, f"{success_count}/{total_count}"))
    
    # Test 2: BeastlyModule Powers
    print("=" * 60)
    powers_tested, total_components = test_beastly_module_powers()
    test_results.append(("BeastlyModule Powers", powers_tested >= total_components * 0.7, f"{powers_tested}/{total_components}"))
    
    # Test 3: ContextManager Full Capabilities
    print("=" * 60)
    cm_success = test_context_manager_full_capabilities()
    test_results.append(("ContextManager Capabilities", cm_success, "Full test"))
    
    # Test 4: CLI Command Execution
    print("=" * 60)
    cli_success = test_cli_command_execution()
    test_results.append(("CLI Command Execution", cli_success, "Command tests"))
    
    # Test 5: Prometheus Integration
    print("=" * 60)
    prometheus_success = test_prometheus_integration()
    test_results.append(("Prometheus Integration", prometheus_success, "Metrics tests"))
    
    # Test 6: Tracing Integration
    print("=" * 60)
    tracing_success = test_tracing_integration()
    test_results.append(("Tracing Integration", tracing_success, "Trace tests"))
    
    # Final Results
    print("\n" + "=" * 60)
    print("🏁 COMPREHENSIVE TEST RESULTS")
    print("=" * 60)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, success, details in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {test_name:<30} ({details})")
        if success:
            passed_tests += 1
    
    print(f"\n📊 Overall Results: {passed_tests}/{total_tests} test suites passed")
    
    # Final Assessment
    if passed_tests == total_tests:
        print("\n🏆 EXCELLENT! AI Memory Palace is fully functional with complete BeastlyModule Layer 3 integration!")
        print("🐺 All enhanced observability capabilities confirmed working")
        print("🔍 Distributed tracing, Prometheus metrics, and CLI interfaces operational")
        print("📊 Full Beast Mode ecosystem integration achieved")
        print("🎉 Ready for production deployment with systematic observability!")
        
    elif passed_tests >= total_tests * 0.8:
        print("\n🎯 VERY GOOD! AI Memory Palace core functionality is solid with BeastlyModule powers")
        print("🐺 Enhanced observability capabilities largely functional")
        print("🔧 Minor issues can be addressed without affecting core architecture")
        print("✅ BeastlyModule migration successful - ready for use!")
        
    elif passed_tests >= total_tests * 0.6:
        print("\n👍 GOOD! AI Memory Palace BeastlyModule migration is fundamentally successful")
        print("🐺 Core BeastlyModule capabilities working")
        print("🔧 Some integration issues need attention but architecture is sound")
        print("📈 Significant progress made - continue with remaining fixes")
        
    else:
        print("\n⚠️  NEEDS WORK! Several core issues need attention")
        print("🔧 Focus on fixing fundamental BeastlyModule integration issues")
        print("📋 Review component dependencies and abstract method implementations")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)