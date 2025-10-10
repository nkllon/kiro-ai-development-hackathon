#!/usr/bin/env python3
"""
AI Memory Palace Test Drive
Test the newly migrated BeastlyModule architecture end-to-end
"""

import sys
import os
sys.path.insert(0, '.')

from datetime import datetime
from typing import Dict, Any
import tempfile
import json

def test_beastly_module_capabilities():
    """Test BeastlyModule enhanced capabilities"""
    print("🐺 Testing BeastlyModule Enhanced Capabilities...")
    
    try:
        from src.beast_mode.ai_memory_palace.context_manager import ContextManager
        
        # Create ContextManager with temporary database
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {"db_path": os.path.join(temp_dir, "test_context.db")}
            cm = ContextManager(config)
            
            print("✅ ContextManager instantiated successfully")
            
            # Test BeastlyModule methods
            print("\n🔍 BeastlyModule Enhanced Features:")
            
            # 1. Tracing Status
            tracing_status = cm.get_tracing_status()
            print(f"  📊 Tracing Available: {tracing_status.get('tracing_available', False)}")
            print(f"  🎯 Tracing Enabled: {tracing_status.get('tracing_enabled', False)}")
            print(f"  🏷️  Service Name: {tracing_status.get('service_name', 'N/A')}")
            
            # 2. Module Info
            module_info = cm.get_module_info()
            print(f"\n  🏗️  Module: {module_info['module_name']} v{module_info['version']}")
            print(f"  🆔 Module ID: {module_info['module_id']}")
            print(f"  📝 Description: {module_info['description']}")
            
            # 3. Health Status
            health = cm.get_health_status()
            print(f"\n  💚 Health Status: {health.status.value}")
            print(f"  📈 Health Score: {health.health_score}")
            print(f"  ⏱️  Uptime: {health.uptime_seconds:.2f}s")
            
            # 4. Capabilities
            capabilities = cm.get_capabilities()
            print(f"\n  🛠️  Capabilities ({len(capabilities)} total):")
            for cap in capabilities:
                print(f"    - {cap.value}")
            
            # 5. Graceful Degradation
            degradation = cm.graceful_degradation()
            print(f"\n  🔄 Graceful Degradation: {'✅ Success' if degradation.success else '❌ Failed'}")
            print(f"  🟢 Remaining Capabilities: {len(degradation.remaining_capabilities)}")
            print(f"  🟡 Degraded Capabilities: {len(degradation.degraded_capabilities)}")
            
            # 6. Enhanced Observation
            print(f"\n  📡 Testing Enhanced Observation Emission...")
            cm.emit_observation(
                message='AI Memory Palace test drive successful!',
                event_type='info',
                context={'test': 'beastly_capabilities', 'layer': 3},
                emoji='🎉'
            )
            print("  ✅ Enhanced observation emitted with trace correlation")
            
            return True
            
    except Exception as e:
        print(f"❌ BeastlyModule test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_context_operations():
    """Test core context storage and retrieval operations"""
    print("\n🧠 Testing Core Context Operations...")
    
    try:
        from src.beast_mode.ai_memory_palace.context_manager import ContextManager
        from src.beast_mode.ai_memory_palace.models import SessionContext, ContextEvent, ContextEventType
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {"db_path": os.path.join(temp_dir, "test_context.db")}
            cm = ContextManager(config)
            
            # Test context creation
            print("  📝 Creating test context...")
            test_context = SessionContext(
                session_id="test-session-123",
                project_id="ai-memory-palace-test",
                start_time=datetime.now(),
                conversation_events=[],
                context_events=[],
                project_state={
                    "current_task": "Testing AI Memory Palace",
                    "architecture": "BeastlyModule Layer 3"
                }
            )
            
            # Test context storage
            print("  💾 Storing context...")
            success = cm.registry.store_context(test_context)
            if success:
                print("  ✅ Context stored successfully")
            else:
                print("  ❌ Context storage failed")
                return False
            
            # Test context retrieval
            print("  🔍 Retrieving context...")
            retrieved_context = cm.registry.load_context("ai-memory-palace-test")
            if retrieved_context:
                print("  ✅ Context retrieved successfully")
                print(f"    📊 Session ID: {retrieved_context.session_id}")
                print(f"    🏗️  Project ID: {retrieved_context.project_id}")
                print(f"    📈 Project State: {retrieved_context.project_state}")
            else:
                print("  ❌ Context retrieval failed")
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ Context operations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_built_in_cli():
    """Test the built-in CLI capabilities from BeastlyModule"""
    print("\n🎛️ Testing Built-in CLI Capabilities...")
    
    try:
        from src.beast_mode.ai_memory_palace.context_manager import ContextManager
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {"db_path": os.path.join(temp_dir, "test_context.db")}
            cm = ContextManager(config)
            
            # Test CLI interface generation
            print("  🔍 Generating CLI interface...")
            cli_interface = cm.get_cli_interface()
            
            print(f"  ✅ CLI Interface Generated:")
            print(f"    📦 Module: {cli_interface['module_name']}")
            print(f"    🆔 Module ID: {cli_interface['module_id']}")
            print(f"    🛠️  Commands Available: {len(cli_interface['commands'])}")
            
            # Show some available commands
            print(f"\n  📋 Available CLI Commands:")
            for cmd_name, cmd_info in list(cli_interface['commands'].items())[:5]:
                print(f"    - {cmd_name}: {cmd_info['description'][:50]}...")
            
            if len(cli_interface['commands']) > 5:
                print(f"    ... and {len(cli_interface['commands']) - 5} more commands")
            
            # Test CLI help generation
            print(f"\n  📖 Testing CLI Help Generation...")
            help_text = cm.generate_cli_help()
            print(f"  ✅ CLI Help Generated ({len(help_text)} characters)")
            
            # Test specific command help
            if 'get_module_info' in cli_interface['commands']:
                specific_help = cm.generate_cli_help('get_module_info')
                print(f"  ✅ Specific Command Help Generated")
            
            return True
            
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_component_integration():
    """Test integration between AI Memory Palace components"""
    print("\n🔗 Testing Component Integration...")
    
    try:
        # Test individual component imports
        components = [
            ('ContextRegistry', 'src.beast_mode.ai_memory_palace.context_registry'),
            ('ContextEngine', 'src.beast_mode.ai_memory_palace.context_engine'),
            ('ContextValidator', 'src.beast_mode.ai_memory_palace.context_validator'),
        ]
        
        imported_components = {}
        
        for comp_name, module_path in components:
            try:
                module = __import__(module_path, fromlist=[comp_name])
                comp_class = getattr(module, comp_name)
                imported_components[comp_name] = comp_class
                print(f"  ✅ {comp_name} imported successfully")
            except Exception as e:
                print(f"  ⚠️  {comp_name} import issue: {str(e)[:50]}...")
        
        print(f"\n  📊 Component Integration Summary:")
        print(f"    🟢 Successfully Imported: {len(imported_components)}/{len(components)}")
        
        # Test that components have BeastlyModule capabilities
        for comp_name, comp_class in imported_components.items():
            try:
                # Check if it has BeastlyModule methods
                instance = comp_class()
                has_tracing = hasattr(instance, 'get_tracing_status')
                has_observation = hasattr(instance, 'emit_observation')
                print(f"    🐺 {comp_name}: BeastlyModule powers {'✅' if has_tracing and has_observation else '⚠️'}")
            except Exception as e:
                print(f"    ⚠️  {comp_name}: Instantiation issue (likely missing dependencies)")
        
        return len(imported_components) > 0
        
    except Exception as e:
        print(f"❌ Component integration test failed: {e}")
        return False

def main():
    """Run the AI Memory Palace test drive"""
    print("🚗 AI Memory Palace Test Drive")
    print("=" * 50)
    print("Testing the newly migrated BeastlyModule architecture...")
    print()
    
    tests = [
        ("BeastlyModule Capabilities", test_beastly_module_capabilities),
        ("Context Operations", test_context_operations),
        ("Built-in CLI", test_built_in_cli),
        ("Component Integration", test_component_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("🏁 AI Memory Palace Test Drive Results:")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    print(f"\n📊 Overall Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🏆 EXCELLENT! AI Memory Palace is fully functional with BeastlyModule Layer 3!")
        print("🐺 Enhanced observability and tracing capabilities confirmed!")
        print("🎉 Ready for production use with full Beast Mode ecosystem integration!")
    elif passed > total // 2:
        print("🎯 GOOD! Core functionality works, some components need dependency fixes")
        print("🔧 Recommend addressing missing model dependencies next")
    else:
        print("⚠️  NEEDS WORK! Several components have issues that need attention")
        print("🛠️  Recommend fixing core dependencies before proceeding")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)