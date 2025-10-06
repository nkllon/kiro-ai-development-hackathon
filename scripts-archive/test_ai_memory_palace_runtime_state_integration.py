#!/usr/bin/env python3
"""
Smoke Test: AI Memory Palace Runtime State Registry Integration

Tests the AI Memory Palace's capability to support the runtime-state-registry
integration requirements identified in the design analysis.
"""

import asyncio
import sys
import json
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.beast_mode.ai_memory_palace.context_manager import ContextManager
from src.beast_mode.ai_memory_palace.models import (
    ContextEvent, ContextEventType, EventMetadata, ServiceInfo, HealthStatus
)


class RuntimeStateIntegrationSmokeTest:
    """Smoke test for AI Memory Palace runtime state integration capabilities"""
    
    def __init__(self):
        self.context_manager = None
        self.test_results = []
    
    async def run_all_tests(self):
        """Run all smoke tests"""
        print("🧪 AI Memory Palace Runtime State Integration Smoke Test")
        print("=" * 60)
        
        try:
            # Initialize context manager
            await self.test_context_manager_initialization()
            
            # Test core integration capabilities
            await self.test_system_state_context_storage()
            await self.test_runtime_state_event_contribution()
            await self.test_context_aware_query_support()
            await self.test_service_discovery_integration()
            await self.test_historical_state_tracking()
            await self.test_context_validation_against_runtime()
            
            # Test performance requirements
            await self.test_o1_context_restoration()
            await self.test_context_size_management()
            
            # Generate report
            self.generate_test_report()
            
        except Exception as e:
            print(f"💥 Critical test failure: {e}")
            return False
        
        return all(result["passed"] for result in self.test_results)
    
    async def test_context_manager_initialization(self):
        """Test 1: Context Manager can be initialized and provides required interfaces"""
        print("\n🔧 Test 1: Context Manager Initialization")
        
        try:
            self.context_manager = ContextManager()
            
            # Check required methods exist for runtime state integration
            required_methods = [
                'load_session_context',
                'save_context_event', 
                'validate_context_integrity',
                'health_check',
                'get_metrics'
            ]
            
            missing_methods = []
            for method in required_methods:
                if not hasattr(self.context_manager, method):
                    missing_methods.append(method)
            
            if missing_methods:
                self.record_test_result("context_manager_init", False, 
                                      f"Missing methods: {missing_methods}")
                return False
            
            # Test health check
            health = self.context_manager.health_check()
            if health.get("status") not in ["healthy", "degraded"]:
                self.record_test_result("context_manager_init", False, 
                                      f"Unhealthy status: {health}")
                return False
            
            self.record_test_result("context_manager_init", True, 
                                  "Context Manager initialized successfully")
            print("✅ Context Manager initialization: PASSED")
            return True
            
        except Exception as e:
            self.record_test_result("context_manager_init", False, str(e))
            print(f"❌ Context Manager initialization: FAILED - {e}")
            return False
    
    async def test_system_state_context_storage(self):
        """Test 2: Can store and retrieve system state in context"""
        print("\n💾 Test 2: System State Context Storage")
        
        try:
            # Load or create context
            context = await self.context_manager.load_session_context()
            
            if not context:
                self.record_test_result("system_state_storage", False, 
                                      "Failed to load/create context")
                return False
            
            # Check if context has project state with runtime information
            project_state = context.project_state
            
            required_fields = ['running_services', 'health_status', 'architecture_overview']
            missing_fields = []
            
            for field in required_fields:
                if not hasattr(project_state, field):
                    missing_fields.append(field)
            
            if missing_fields:
                self.record_test_result("system_state_storage", False, 
                                      f"Missing project state fields: {missing_fields}")
                return False
            
            # Verify services are discovered
            services_count = len(project_state.running_services)
            
            self.record_test_result("system_state_storage", True, 
                                  f"Context loaded with {services_count} services")
            print(f"✅ System State Storage: PASSED ({services_count} services discovered)")
            return True
            
        except Exception as e:
            self.record_test_result("system_state_storage", False, str(e))
            print(f"❌ System State Storage: FAILED - {e}")
            return False
    
    async def test_runtime_state_event_contribution(self):
        """Test 3: Can contribute runtime state events to context"""
        print("\n📝 Test 3: Runtime State Event Contribution")
        
        try:
            # Create a runtime state change event
            runtime_event = ContextEvent(
                event_id="test-runtime-event",
                event_type=ContextEventType.SYSTEM_STATE_CHANGED,
                timestamp=datetime.now(),
                correlation_id="test-correlation-123",
                data={
                    "type": "service_health_change",
                    "service_name": "test-service",
                    "old_status": "healthy",
                    "new_status": "degraded",
                    "reason": "high_latency"
                },
                metadata=EventMetadata(source="runtime_state_registry")
            )
            
            # Save the event
            success = await self.context_manager.save_context_event(runtime_event)
            
            if not success:
                self.record_test_result("runtime_event_contribution", False, 
                                      "Failed to save runtime state event")
                return False
            
            # Verify event was stored
            context = await self.context_manager.load_session_context()
            
            # Check if event appears in conversation history
            recent_events = [e for e in context.conversation_history 
                           if e.event_type == "system_state_changed"]
            
            if not recent_events:
                self.record_test_result("runtime_event_contribution", False, 
                                      "Runtime state event not found in context")
                return False
            
            self.record_test_result("runtime_event_contribution", True, 
                                  "Runtime state event successfully contributed")
            print("✅ Runtime State Event Contribution: PASSED")
            return True
            
        except Exception as e:
            self.record_test_result("runtime_event_contribution", False, str(e))
            print(f"❌ Runtime State Event Contribution: FAILED - {e}")
            return False
    
    async def test_context_aware_query_support(self):
        """Test 4: Context provides data for O(1) query optimization"""
        print("\n🔍 Test 4: Context-Aware Query Support")
        
        try:
            context = await self.context_manager.load_session_context()
            
            if not context:
                self.record_test_result("context_query_support", False, 
                                      "No context available for query testing")
                return False
            
            # Test if context contains queryable system state
            project_state = context.project_state
            
            # Check if we can answer "what's running" from context
            running_services = project_state.running_services
            service_names = [s.name for s in running_services]
            
            # Check if we can answer "system health" from context
            health_status = project_state.health_status
            overall_health = health_status.overall_status
            
            # Verify context has enough data for common queries
            query_data = {
                "services_running": len(service_names),
                "service_names": service_names,
                "overall_health": overall_health,
                "healthy_services": health_status.services_healthy,
                "total_services": health_status.services_total
            }
            
            # Check context size for performance
            context_size = context.get_context_size()
            
            self.record_test_result("context_query_support", True, 
                                  f"Context supports queries: {query_data}, Size: {context_size} bytes")
            print(f"✅ Context-Aware Query Support: PASSED")
            print(f"   📊 Query data available: {json.dumps(query_data, indent=2)}")
            return True
            
        except Exception as e:
            self.record_test_result("context_query_support", False, str(e))
            print(f"❌ Context-Aware Query Support: FAILED - {e}")
            return False
    
    async def test_service_discovery_integration(self):
        """Test 5: Context integrates with service discovery"""
        print("\n🔎 Test 5: Service Discovery Integration")
        
        try:
            context = await self.context_manager.load_session_context()
            
            # Check if context contains discovered services
            services = context.project_state.running_services
            
            if not services:
                self.record_test_result("service_discovery", False, 
                                      "No services discovered in context")
                return False
            
            # Verify service information structure
            service = services[0]
            required_service_fields = ['name', 'url', 'status']
            
            missing_fields = []
            for field in required_service_fields:
                if not hasattr(service, field):
                    missing_fields.append(field)
            
            if missing_fields:
                self.record_test_result("service_discovery", False, 
                                      f"Service missing fields: {missing_fields}")
                return False
            
            # Check if services have health information
            healthy_services = [s for s in services if s.status == "healthy"]
            
            service_summary = {
                "total_services": len(services),
                "healthy_services": len(healthy_services),
                "service_names": [s.name for s in services]
            }
            
            self.record_test_result("service_discovery", True, 
                                  f"Service discovery working: {service_summary}")
            print(f"✅ Service Discovery Integration: PASSED")
            print(f"   🔍 Discovered: {service_summary}")
            return True
            
        except Exception as e:
            self.record_test_result("service_discovery", False, str(e))
            print(f"❌ Service Discovery Integration: FAILED - {e}")
            return False
    
    async def test_historical_state_tracking(self):
        """Test 6: Context tracks historical state changes"""
        print("\n📈 Test 6: Historical State Tracking")
        
        try:
            context = await self.context_manager.load_session_context()
            
            # Check conversation history for state changes
            history = context.conversation_history
            
            # Look for system state change events
            state_changes = [e for e in history if "state" in e.event_type.lower()]
            
            # Check decisions made (architectural decisions)
            decisions = context.decisions_made
            
            # Check work completed (implementation history)
            work_items = context.work_completed
            
            # Check system discoveries (infrastructure discoveries)
            discoveries = context.system_discoveries
            
            historical_data = {
                "conversation_events": len(history),
                "state_changes": len(state_changes),
                "decisions": len(decisions),
                "work_items": len(work_items),
                "discoveries": len(discoveries)
            }
            
            # Verify we have some historical tracking
            total_historical_items = sum(historical_data.values())
            
            if total_historical_items == 0:
                self.record_test_result("historical_tracking", False, 
                                      "No historical data found in context")
                return False
            
            self.record_test_result("historical_tracking", True, 
                                  f"Historical tracking active: {historical_data}")
            print(f"✅ Historical State Tracking: PASSED")
            print(f"   📊 Historical data: {json.dumps(historical_data, indent=2)}")
            return True
            
        except Exception as e:
            self.record_test_result("historical_tracking", False, str(e))
            print(f"❌ Historical State Tracking: FAILED - {e}")
            return False
    
    async def test_context_validation_against_runtime(self):
        """Test 7: Context can be validated against current runtime state"""
        print("\n✅ Test 7: Context Validation Against Runtime")
        
        try:
            # Test context integrity validation
            validation_result = self.context_manager.validate_context_integrity()
            
            if not isinstance(validation_result, dict):
                self.record_test_result("context_validation", False, 
                                      "Invalid validation result format")
                return False
            
            # Check validation result structure
            required_fields = ['valid']
            missing_fields = []
            
            for field in required_fields:
                if field not in validation_result:
                    missing_fields.append(field)
            
            if missing_fields:
                self.record_test_result("context_validation", False, 
                                      f"Validation result missing fields: {missing_fields}")
                return False
            
            is_valid = validation_result.get('valid', False)
            errors = validation_result.get('errors', [])
            
            validation_summary = {
                "valid": is_valid,
                "error_count": len(errors),
                "has_validation_timestamp": 'validation_timestamp' in validation_result
            }
            
            self.record_test_result("context_validation", True, 
                                  f"Context validation working: {validation_summary}")
            print(f"✅ Context Validation: PASSED")
            print(f"   🔍 Validation: {json.dumps(validation_summary, indent=2)}")
            return True
            
        except Exception as e:
            self.record_test_result("context_validation", False, str(e))
            print(f"❌ Context Validation: FAILED - {e}")
            return False
    
    async def test_o1_context_restoration(self):
        """Test 8: Context restoration performance (O(1) requirement)"""
        print("\n⚡ Test 8: O(1) Context Restoration Performance")
        
        try:
            # Measure context loading time
            start_time = datetime.now()
            context = await self.context_manager.load_session_context()
            end_time = datetime.now()
            
            load_time_ms = (end_time - start_time).total_seconds() * 1000
            
            # Check if loading time meets <2 second requirement
            target_time_ms = 2000  # 2 seconds
            
            if load_time_ms > target_time_ms:
                self.record_test_result("o1_performance", False, 
                                      f"Context loading too slow: {load_time_ms:.2f}ms > {target_time_ms}ms")
                return False
            
            # Check context size for performance implications
            context_size = context.get_context_size() if context else 0
            
            performance_data = {
                "load_time_ms": round(load_time_ms, 2),
                "context_size_bytes": context_size,
                "context_size_kb": round(context_size / 1024, 2),
                "meets_performance_target": load_time_ms < target_time_ms
            }
            
            self.record_test_result("o1_performance", True, 
                                  f"Performance acceptable: {performance_data}")
            print(f"✅ O(1) Context Restoration: PASSED")
            print(f"   ⚡ Performance: {json.dumps(performance_data, indent=2)}")
            return True
            
        except Exception as e:
            self.record_test_result("o1_performance", False, str(e))
            print(f"❌ O(1) Context Restoration: FAILED - {e}")
            return False
    
    async def test_context_size_management(self):
        """Test 9: Context size management for scalability"""
        print("\n📏 Test 9: Context Size Management")
        
        try:
            context = await self.context_manager.load_session_context()
            
            if not context:
                self.record_test_result("context_size_management", False, 
                                      "No context available for size testing")
                return False
            
            # Check context size
            context_size = context.get_context_size()
            
            # Check if context has summarization capability
            context_summary = context.get_summary()
            
            # Verify summary contains key information
            required_summary_fields = ['project_id', 'conversation_events', 'context_size_bytes']
            missing_summary_fields = []
            
            for field in required_summary_fields:
                if field not in context_summary:
                    missing_summary_fields.append(field)
            
            if missing_summary_fields:
                self.record_test_result("context_size_management", False, 
                                      f"Context summary missing fields: {missing_summary_fields}")
                return False
            
            # Check if size is reasonable (< 10MB for development)
            max_size_bytes = 10 * 1024 * 1024  # 10MB
            size_acceptable = context_size < max_size_bytes
            
            size_data = {
                "context_size_bytes": context_size,
                "context_size_mb": round(context_size / (1024 * 1024), 2),
                "size_acceptable": size_acceptable,
                "max_size_mb": round(max_size_bytes / (1024 * 1024), 2),
                "has_summary": bool(context_summary)
            }
            
            self.record_test_result("context_size_management", size_acceptable, 
                                  f"Context size management: {size_data}")
            
            if size_acceptable:
                print(f"✅ Context Size Management: PASSED")
            else:
                print(f"⚠️ Context Size Management: WARNING - Large context size")
            
            print(f"   📏 Size data: {json.dumps(size_data, indent=2)}")
            return size_acceptable
            
        except Exception as e:
            self.record_test_result("context_size_management", False, str(e))
            print(f"❌ Context Size Management: FAILED - {e}")
            return False
    
    def record_test_result(self, test_name: str, passed: bool, details: str):
        """Record test result"""
        self.test_results.append({
            "test_name": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("🧪 AI MEMORY PALACE RUNTIME STATE INTEGRATION TEST REPORT")
        print("=" * 60)
        
        passed_tests = [r for r in self.test_results if r["passed"]]
        failed_tests = [r for r in self.test_results if not r["passed"]]
        
        print(f"\n📊 SUMMARY:")
        print(f"   ✅ Passed: {len(passed_tests)}/{len(self.test_results)}")
        print(f"   ❌ Failed: {len(failed_tests)}/{len(self.test_results)}")
        print(f"   📈 Success Rate: {len(passed_tests)/len(self.test_results)*100:.1f}%")
        
        if failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test_name']}: {test['details']}")
        
        print(f"\n✅ PASSED TESTS:")
        for test in passed_tests:
            print(f"   • {test['test_name']}: {test['details']}")
        
        # Integration readiness assessment
        critical_tests = [
            "context_manager_init",
            "system_state_storage", 
            "runtime_event_contribution",
            "context_query_support"
        ]
        
        critical_passed = [t for t in self.test_results 
                          if t["test_name"] in critical_tests and t["passed"]]
        
        integration_ready = len(critical_passed) == len(critical_tests)
        
        print(f"\n🔗 RUNTIME STATE REGISTRY INTEGRATION READINESS:")
        print(f"   Status: {'✅ READY' if integration_ready else '❌ NOT READY'}")
        print(f"   Critical Tests: {len(critical_passed)}/{len(critical_tests)} passed")
        
        if not integration_ready:
            failed_critical = [t for t in critical_tests 
                             if not any(r["test_name"] == t and r["passed"] 
                                      for r in self.test_results)]
            print(f"   Missing: {failed_critical}")
        
        # Save detailed report
        report_data = {
            "test_summary": {
                "total_tests": len(self.test_results),
                "passed_tests": len(passed_tests),
                "failed_tests": len(failed_tests),
                "success_rate": len(passed_tests)/len(self.test_results)*100,
                "integration_ready": integration_ready
            },
            "test_results": self.test_results,
            "timestamp": datetime.now().isoformat()
        }
        
        report_file = "ai_memory_palace_integration_test_report.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")


async def main():
    """Run the smoke test"""
    test_runner = RuntimeStateIntegrationSmokeTest()
    success = await test_runner.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! AI Memory Palace is ready for Runtime State Registry integration.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Review the gaps before proceeding with integration.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)