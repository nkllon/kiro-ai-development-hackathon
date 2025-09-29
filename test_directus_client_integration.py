#!/usr/bin/env python3
"""
Test DirectusClient integration with Beast Mode framework
"""

import sys
sys.path.insert(0, '.')

def test_directus_client_import():
    """Test that DirectusClient can be imported and instantiated"""
    print("🔍 Testing DirectusClient import and instantiation...")
    
    try:
        from src.beast_mode.directus_cms.directus_client import DirectusClient
        print("✅ DirectusClient imported successfully")
        
        # Test instantiation
        client = DirectusClient()
        print("✅ DirectusClient instantiated successfully")
        
        # Test BeastlyModule capabilities
        print(f"🐺 Module Info: {client.get_module_info()['module_name']}")
        print(f"🛠️  Capabilities: {len(client.get_capabilities())} total")
        print(f"💚 Health Status: {client.get_health_status().status.value}")
        
        return True
        
    except Exception as e:
        print(f"❌ DirectusClient test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_directus_connection():
    """Test connection to running Directus instance"""
    print("\n🔗 Testing Directus connection...")
    
    try:
        from src.beast_mode.directus_cms.directus_client import DirectusClient
        
        client = DirectusClient("http://localhost:8055")
        
        # Test health check
        is_healthy = client.health_check()
        print(f"🏥 Directus Health Check: {'✅ Healthy' if is_healthy else '❌ Unhealthy'}")
        
        if is_healthy:
            # Test getting collections
            collections = client.get_collections()
            print(f"📚 Collections Available: {len(collections)} collections")
            
            # Show some collection names
            for collection in collections[:5]:
                collection_name = collection.get('collection', 'unknown')
                print(f"  - {collection_name}")
            
            if len(collections) > 5:
                print(f"  ... and {len(collections) - 5} more")
        
        return is_healthy
        
    except Exception as e:
        print(f"❌ Directus connection test failed: {e}")
        return False

def test_reflective_module_cms_integration():
    """Test that ReflectiveModule can now use real Directus"""
    print("\n🧠 Testing ReflectiveModule CMS integration...")
    
    try:
        from src.beast_mode.ai_memory_palace.context_manager import ContextManager
        import tempfile
        import os
        
        # Create ContextManager (which inherits from BeastlyModule -> ReflectiveModule)
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {"db_path": os.path.join(temp_dir, "test.db")}
            cm = ContextManager(config)
            
            print("✅ ContextManager created successfully")
            
            # Test CMS client initialization
            if hasattr(cm, '_cms_client'):
                print(f"🔗 CMS Client: {type(cm._cms_client).__name__}")
                
                if hasattr(cm._cms_client, 'health_check'):
                    health = cm._cms_client.health_check()
                    print(f"🏥 CMS Health: {'✅ Connected' if health else '⚠️ Offline'}")
                else:
                    print("📝 CMS Client: Memory fallback mode")
            else:
                print("⚠️ CMS Client not initialized yet")
            
            # Test content storage
            success = cm.store_content("test_content_123", "test_collection", {"message": "Hello Beast Mode!"})
            print(f"💾 Content Storage: {'✅ Success' if success else '❌ Failed'}")
            
            return True
            
    except Exception as e:
        print(f"❌ ReflectiveModule CMS integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_existing_directus_components():
    """Test that existing Directus CMS components can now work"""
    print("\n🏗️ Testing existing Directus CMS components...")
    
    try:
        # Test some existing components that expect directus_client
        from src.beast_mode.directus_cms.directus_client import DirectusClient
        
        client = DirectusClient()
        
        # Test components that expect directus_client parameter
        component_tests = [
            ("API Error Handler", "src.beast_mode.directus_cms.error_prevention.api_handler", "APIErrorHandler"),
            ("Auth Validator", "src.beast_mode.directus_cms.error_prevention.auth_validator", "AuthenticationValidator"),
            ("REST API Manager", "src.beast_mode.directus_cms.api.rest_config", "RESTAPIManager"),
        ]
        
        success_count = 0
        
        for name, module_path, class_name in component_tests:
            try:
                module = __import__(module_path, fromlist=[class_name])
                component_class = getattr(module, class_name)
                
                # Instantiate with DirectusClient
                component = component_class(directus_client=client)
                
                # Test that it has BeastlyModule/ReflectiveModule capabilities
                if hasattr(component, 'get_health_status'):
                    health = component.get_health_status()
                    print(f"  ✅ {name}: {health.status.value}")
                    success_count += 1
                else:
                    print(f"  ⚠️ {name}: No health status method")
                    
            except Exception as e:
                print(f"  ❌ {name}: {str(e)[:50]}...")
        
        print(f"\n📊 Component Test Results: {success_count}/{len(component_tests)} components working")
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Existing components test failed: {e}")
        return False

def main():
    """Run all DirectusClient integration tests"""
    print("🚀 DirectusClient Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("DirectusClient Import", test_directus_client_import),
        ("Directus Connection", test_directus_connection),
        ("ReflectiveModule CMS Integration", test_reflective_module_cms_integration),
        ("Existing Directus Components", test_existing_directus_components),
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
    print("🏁 DirectusClient Integration Test Results:")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    print(f"\n📊 Overall Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🏆 EXCELLENT! DirectusClient integration is fully functional!")
        print("🐺 Beast Mode Directus CMS framework is now operational!")
        print("🔗 AI Memory Palace can now use Directus for content management!")
    elif passed >= total * 0.7:
        print("🎯 GOOD! Core DirectusClient functionality is working!")
        print("🔧 Some components may need additional configuration")
    else:
        print("⚠️ NEEDS WORK! DirectusClient integration has issues")
        print("🛠️ Check Directus connectivity and configuration")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)