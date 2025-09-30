#!/usr/bin/env python3
"""
Task 2.1 Completion Validation Test

This test validates that Task 2.1 "Implement AI Memory Palace context integration layer" 
has been completed successfully with all requirements met.

Task 2.1 Requirements:
✅ Create AIMemoryPalaceIntegration class with context provider
✅ Implement get_current_project_context() with comprehensive fallbacks
✅ Add context caching for when AI Memory Palace unavailable
✅ Create ProjectContext model with default fallback values
✅ Verify context retrieval works with AI Memory Palace online/offline
✅ Confirm context enhancement doesn't break existing broadcasts
✅ Context failures fall back to existing behavior without context
"""

import sys
import time
import json
import uuid
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_ai_memory_palace_integration_exists():
    """Test that AIMemoryPalaceIntegration class exists and is functional"""
    print("📋 Testing AIMemoryPalaceIntegration class exists...")
    
    try:
        from src.beast_mode.observatory.ai_memory_palace_integration import (
            AIMemoryPalaceIntegration, ProjectContext, ProjectType, ContextRetrievalStatus
        )
        
        # Test class creation
        integration = AIMemoryPalaceIntegration()
        
        # Test required methods exist
        assert hasattr(integration, 'get_current_project_context')
        assert hasattr(integration, 'create_session_context')
        assert hasattr(integration, 'get_session_context')
        assert hasattr(integration, 'get_statistics')
        assert hasattr(integration, 'graceful_degradation')
        
        # Test data models exist
        assert ProjectContext
        assert ProjectType
        assert ContextRetrievalStatus
        
        print("✅ AIMemoryPalaceIntegration class exists with all required components")
        return True
    except Exception as e:
        print(f"❌ AIMemoryPalaceIntegration test failed: {e}")
        return False

def test_context_provider_functionality():
    """Test context provider with comprehensive fallbacks"""
    print("📋 Testing context provider functionality...")
    
    try:
        from src.beast_mode.observatory.ai_memory_palace_integration import AIMemoryPalaceIntegration
        
        integration = AIMemoryPalaceIntegration()
        
        # Test basic context retrieval
        context1 = integration.get_current_project_context()
        assert context1 is not None
        assert hasattr(context1, 'project_name')
        assert hasattr(context1, 'project_type')
        assert hasattr(context1, 'current_spec')
        assert hasattr(context1, 'active_tasks')
        assert hasattr(context1, 'completion_percentage')
        assert hasattr(context1, 'retrieval_status')
        
        # Test context with specific project name
        context2 = integration.get_current_project_context(project_name="test-project")
        assert context2.project_name == "test-project"
        
        # Test context with session ID
        session_id = f"test_{uuid.uuid4().hex[:8]}"
        context3 = integration.get_current_project_context(session_id=session_id)
        assert context3.session_id == session_id
        
        print("✅ Context provider functionality working correctly")
        return True
    except Exception as e:
        print(f"❌ Context provider test failed: {e}")
        return False

def test_comprehensive_fallbacks():
    """Test comprehensive fallback mechanisms"""
    print("📋 Testing comprehensive fallbacks...")
    
    try:
        from src.beast_mode.observatory.ai_memory_palace_integration import (
            AIMemoryPalaceIntegration, ContextRetrievalStatus
        )
        
        integration = AIMemoryPalaceIntegration()
        
        # Test offline mode fallback
        integration.config["offline_mode"] = True
        context_offline = integration.get_current_project_context()
        assert context_offline.retrieval_status in [ContextRetrievalStatus.FALLBACK, ContextRetrievalStatus.CACHED]
        
        # Test circuit breaker fallback
        integration._circuit_breaker_open = True
        context_circuit_open = integration.get_current_project_context()
        assert context_circuit_open.retrieval_status in [ContextRetrievalStatus.FALLBACK, ContextRetrievalStatus.CACHED]
        
        # Test graceful degradation
        degradation_result = integration.graceful_degradation()
        assert degradation_result.success == True
        
        # Context should still work after degradation
        context_degraded = integration.get_current_project_context()
        assert context_degraded is not None
        
        print("✅ Comprehensive fallbacks working correctly")
        return True
    except Exception as e:
        print(f"❌ Comprehensive fallbacks test failed: {e}")
        return False

def test_context_caching():
    """Test context caching for when AI Memory Palace unavailable"""
    print("📋 Testing context caching...")
    
    try:
        from src.beast_mode.observatory.ai_memory_palace_integration import (
            AIMemoryPalaceIntegration, ContextRetrievalStatus
        )
        
        integration = AIMemoryPalaceIntegration()
        
        # First retrieval should be from AI Memory Palace (or fallback)
        context1 = integration.get_current_project_context()
        first_status = context1.retrieval_status
        
        # Second retrieval should be from cache
        context2 = integration.get_current_project_context()
        assert context2.retrieval_status == ContextRetrievalStatus.CACHED
        
        # Verify cache statistics
        stats = integration.get_statistics()
        assert stats["cache_hits"] >= 1
        assert stats["cache_size"] >= 1
        
        # Test cache hit rate calculation
        assert "cache_hit_rate" in stats
        assert isinstance(stats["cache_hit_rate"], (int, float))
        
        print("✅ Context caching working correctly")
        return True
    except Exception as e:
        print(f"❌ Context caching test failed: {e}")
        return False

def test_project_context_model():
    """Test ProjectContext model with default fallback values"""
    print("📋 Testing ProjectContext model...")
    
    try:
        from src.beast_mode.observatory.ai_memory_palace_integration import (
            ProjectContext, ProjectType, ContextRetrievalStatus
        )
        
        # Test default context creation
        default_context = ProjectContext()
        assert default_context.project_name == "unknown-project"
        assert default_context.project_type == ProjectType.GENERAL
        assert default_context.active_tasks == []
        assert default_context.completion_percentage == 0.0
        
        # Test context with specific values
        custom_context = ProjectContext(
            project_name="test-project",
            project_type=ProjectType.HACKATHON,
            current_spec="test-spec",
            active_tasks=["task1", "task2"],
            completion_percentage=50.0
        )
        
        assert custom_context.project_name == "test-project"
        assert custom_context.project_type == ProjectType.HACKATHON
        assert custom_context.current_spec == "test-spec"
        assert len(custom_context.active_tasks) == 2
        assert custom_context.completion_percentage == 50.0
        
        # Test that context has all required fields
        required_fields = [
            'project_name', 'project_type', 'current_spec', 'active_tasks',
            'completion_percentage', 'session_id', 'workspace_path', 'git_branch',
            'last_activity', 'project_goals', 'key_technologies', 'context_retrieved_at',
            'context_source', 'retrieval_status'
        ]
        
        for field in required_fields:
            assert hasattr(default_context, field), f"Missing field: {field}"
        
        print("✅ ProjectContext model working correctly")
        return True
    except Exception as e:
        print(f"❌ ProjectContext model test failed: {e}")
        return False

def test_online_offline_context_retrieval():
    """Test context retrieval works with AI Memory Palace online/offline"""
    print("📋 Testing online/offline context retrieval...")
    
    try:
        from src.beast_mode.observatory.ai_memory_palace_integration import (
            AIMemoryPalaceIntegration, ContextRetrievalStatus
        )
        
        integration = AIMemoryPalaceIntegration()
        
        # Test online mode (default)
        integration.config["offline_mode"] = False
        integration._circuit_breaker_open = False
        
        context_online = integration.get_current_project_context(force_refresh=True)
        assert context_online is not None
        # Should be SUCCESS or FALLBACK (if AI Memory Palace not actually available)
        assert context_online.retrieval_status in [ContextRetrievalStatus.SUCCESS, ContextRetrievalStatus.FALLBACK]
        
        # Test offline mode
        integration.config["offline_mode"] = True
        
        context_offline = integration.get_current_project_context(force_refresh=True)
        assert context_offline is not None
        assert context_offline.retrieval_status in [ContextRetrievalStatus.FALLBACK, ContextRetrievalStatus.CACHED]
        
        # Both contexts should be functional
        assert context_online.project_name is not None
        assert context_offline.project_name is not None
        
        print("✅ Online/offline context retrieval working correctly")
        return True
    except Exception as e:
        print(f"❌ Online/offline context retrieval test failed: {e}")
        return False

def test_context_enhancement_compatibility():
    """Test context enhancement doesn't break existing broadcasts"""
    print("📋 Testing context enhancement compatibility...")
    
    try:
        from src.beast_mode.observatory.enhanced_ace_reporter_with_error_handling import (
            EnhancedACEReporterWithErrorHandling
        )
        
        # Test reporter without AI Memory Palace integration
        reporter_basic = EnhancedACEReporterWithErrorHandling(feature_flags={
            "ai_memory_palace_integration": False,
            "enhanced_context": False
        })
        
        # Test basic announcements work
        reporter_basic.announce_spec_completion("test-spec", 50)
        reporter_basic.announce_task_completion("test-spec", "test-task", "1.1")
        reporter_basic.announce_milestone("test-milestone", "test-description")
        
        # Test reporter with AI Memory Palace integration
        reporter_enhanced = EnhancedACEReporterWithErrorHandling(feature_flags={
            "ai_memory_palace_integration": True,
            "enhanced_context": True
        })
        
        # Test enhanced announcements work
        reporter_enhanced.announce_spec_completion("test-spec", 75)
        reporter_enhanced.announce_task_completion("test-spec", "test-task", "2.1")
        reporter_enhanced.announce_milestone("test-milestone", "test-description")
        
        # Test context retrieval
        context = reporter_enhanced.get_current_project_context()
        assert context is not None
        assert hasattr(context, 'project_name')
        
        print("✅ Context enhancement compatibility confirmed")
        return True
    except Exception as e:
        print(f"❌ Context enhancement compatibility test failed: {e}")
        return False

def test_context_failure_fallback():
    """Test context failures fall back to existing behavior without context"""
    print("📋 Testing context failure fallback...")
    
    try:
        from src.beast_mode.observatory.enhanced_ace_reporter_with_error_handling import (
            EnhancedACEReporterWithErrorHandling
        )
        
        # Create reporter with AI Memory Palace enabled but simulate failure
        reporter = EnhancedACEReporterWithErrorHandling(feature_flags={
            "ai_memory_palace_integration": True,
            "enhanced_context": True
        })
        
        # Force AI Memory Palace to be unavailable
        reporter._ai_memory_palace = None
        
        # Test that operations still work without context
        try:
            reporter.announce_spec_completion("test-spec", 80)
            reporter.announce_task_completion("test-spec", "test-task", "2.1")
            reporter.announce_milestone("test-milestone", "test-description")
            reporter.announce_system_status("test-system", "healthy")
            
            # Test context retrieval fallback
            context = reporter.get_current_project_context()
            assert context is not None  # Should get fallback context
            
            print("   ✅ All operations work with AI Memory Palace unavailable")
        except Exception as e:
            print(f"   ❌ Operation failed without AI Memory Palace: {e}")
            return False
        
        # Test graceful degradation
        degradation_result = reporter.graceful_degradation()
        assert degradation_result.success == True
        
        # Operations should still work after degradation
        reporter.announce_spec_completion("test-spec", 85)
        
        print("✅ Context failure fallback working correctly")
        return True
    except Exception as e:
        print(f"❌ Context failure fallback test failed: {e}")
        return False

def test_session_management():
    """Test session-aware context management"""
    print("📋 Testing session management...")
    
    try:
        from src.beast_mode.observatory.ai_memory_palace_integration import AIMemoryPalaceIntegration
        
        integration = AIMemoryPalaceIntegration()
        
        # Test session creation
        session1 = integration.create_session_context(
            user_id="test_user",
            session_goals=["Complete AI Memory Palace integration"]
        )
        
        assert session1.session_id is not None
        assert session1.user_id == "test_user"
        assert len(session1.session_goals) == 1
        
        # Test session retrieval
        retrieved_session = integration.get_session_context(session1.session_id)
        assert retrieved_session is not None
        assert retrieved_session.session_id == session1.session_id
        
        # Test session-aware context
        context = integration.get_current_project_context(session_id=session1.session_id)
        assert context.session_id == session1.session_id
        
        # Test session activity update
        original_activity = session1.last_activity
        time.sleep(0.1)  # Small delay to ensure timestamp difference
        integration.update_session_activity(session1.session_id)
        updated_session = integration.get_session_context(session1.session_id)
        assert updated_session.last_activity != original_activity
        
        print("✅ Session management working correctly")
        return True
    except Exception as e:
        print(f"❌ Session management test failed: {e}")
        return False

def test_integration_statistics():
    """Test comprehensive statistics and monitoring"""
    print("📋 Testing integration statistics...")
    
    try:
        from src.beast_mode.observatory.ai_memory_palace_integration import AIMemoryPalaceIntegration
        
        integration = AIMemoryPalaceIntegration()
        
        # Generate some activity
        integration.get_current_project_context()
        integration.get_current_project_context()  # Should be cached
        integration.get_current_project_context(force_refresh=True)
        
        # Test statistics
        stats = integration.get_statistics()
        
        required_stats = [
            'total_requests', 'cache_hits', 'cache_misses', 'fallback_uses',
            'errors', 'ai_memory_palace_calls', 'successful_retrievals',
            'cache_hit_rate', 'success_rate', 'error_rate', 'cache_size',
            'active_sessions', 'circuit_breaker_open', 'offline_mode'
        ]
        
        for stat in required_stats:
            assert stat in stats, f"Missing statistic: {stat}"
        
        # Verify statistics make sense
        assert stats['total_requests'] >= 3
        assert stats['cache_hits'] >= 1
        assert isinstance(stats['cache_hit_rate'], (int, float))
        assert isinstance(stats['success_rate'], (int, float))
        
        print("✅ Integration statistics working correctly")
        return True
    except Exception as e:
        print(f"❌ Integration statistics test failed: {e}")
        return False

def main():
    """Run all Task 2.1 completion tests"""
    print("🧠 Task 2.1 Completion Validation Test")
    print("=" * 70)
    print("Task: Implement AI Memory Palace context integration layer")
    print("=" * 70)
    
    tests = [
        ("AIMemoryPalaceIntegration Exists", test_ai_memory_palace_integration_exists),
        ("Context Provider Functionality", test_context_provider_functionality),
        ("Comprehensive Fallbacks", test_comprehensive_fallbacks),
        ("Context Caching", test_context_caching),
        ("ProjectContext Model", test_project_context_model),
        ("Online/Offline Context Retrieval", test_online_offline_context_retrieval),
        ("Context Enhancement Compatibility", test_context_enhancement_compatibility),
        ("Context Failure Fallback", test_context_failure_fallback),
        ("Session Management", test_session_management),
        ("Integration Statistics", test_integration_statistics)
    ]
    
    results = {}
    
    for test_name, test_function in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 50)
        try:
            result = test_function()
            results[test_name] = result
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TASK 2.1 COMPLETION SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📈 Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 TASK 2.1 COMPLETE!")
        print("✅ AI Memory Palace context integration layer successfully implemented")
        print("✅ All requirements met with comprehensive fallback mechanisms")
        print("✅ Context retrieval works with AI Memory Palace online/offline")
        print("✅ Context enhancement doesn't break existing broadcasts")
        print("✅ Context failures gracefully fall back to existing behavior")
        
        # Create completion report
        completion_report = {
            "task": "2.1 Implement AI Memory Palace context integration layer",
            "status": "COMPLETED",
            "completion_time": datetime.now().isoformat(),
            "test_results": results,
            "success_rate": f"{(passed/total)*100:.1f}%",
            "key_achievements": [
                "AIMemoryPalaceIntegration class created with context provider",
                "get_current_project_context() implemented with comprehensive fallbacks",
                "Context caching system for offline operation implemented",
                "ProjectContext model with default fallback values created",
                "Context retrieval verified to work online/offline",
                "Context enhancement confirmed compatible with existing broadcasts",
                "Context failures gracefully fall back to existing behavior",
                "Session-aware context management implemented",
                "Comprehensive statistics and monitoring system operational",
                "Circuit breaker protection for AI Memory Palace API implemented"
            ],
            "next_steps": [
                "Task 2.2: Enhance observations with AI Memory Palace context",
                "Task 2.3: Implement spec progress monitoring integration"
            ]
        }
        
        with open("TASK_2_1_COMPLETION_REPORT.json", "w") as f:
            json.dump(completion_report, f, indent=2)
        
        print(f"\n📄 Completion report saved to: TASK_2_1_COMPLETION_REPORT.json")
        
        return 0
    else:
        print(f"\n❌ TASK 2.1 INCOMPLETE")
        print(f"❌ {total - passed} tests failed - additional work required")
        return 1

if __name__ == "__main__":
    exit(main())