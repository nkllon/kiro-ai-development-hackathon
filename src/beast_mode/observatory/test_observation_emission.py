#!/usr/bin/env python3
"""
Test script to demonstrate Beastly Module observation emission
"""

import asyncio
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability

class TestObservationModule(ReflectiveModule):
    """Test module that emits various observations"""
    
    def __init__(self):
        super().__init__()
        self.module_id = "test_observation_module"
        self.operation_count = 0
    
    def get_module_info(self):
        return {
            "module_id": self.module_id,
            "name": "Test Observation Module",
            "version": "1.0.0",
            "description": "Demonstrates observation emission from Beastly Modules"
        }
    
    def get_capabilities(self):
        return [ModuleCapability.MONITORING, ModuleCapability.CORE_FUNCTIONALITY]
    
    def get_health_status(self):
        return ModuleHealth(
            module_id=self.module_id,
            status=ModuleStatus.HEALTHY,
            health_score=0.95,
            issues=[],
            last_check=self._last_activity,
            uptime_seconds=(self._last_activity - self._start_time).total_seconds(),
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self):
        from src.rm_ddd.core.unified_reflective_module import GracefulDegradationResult
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=[],
            remaining_capabilities=self.get_capabilities()
        )
    
    def perform_test_operations(self):
        """Perform various test operations that emit observations"""
        
        # Test basic info observation
        self.emit_observation(
            message="Starting test operations sequence",
            event_type="deployment",
            context={"operation": "test_start"},
            emoji="🚀"
        )
        
        time.sleep(1)
        
        # Test certificate operation (interesting)
        self.emit_observation(
            message="Locked 3 SSL certificates for processing",
            event_type="certificate_lock",
            context={"certificates_locked": 3, "operation": "ssl_processing"}
        )
        
        time.sleep(1)
        
        # Test database operation (interesting)
        self.emit_observation(
            message="Executed complex database query in 45ms",
            event_type="database_query",
            context={"query_time_ms": 45, "rows_affected": 12, "query_type": "complex_join"}
        )
        
        time.sleep(1)
        
        # Test performance observation (interesting)
        self.emit_observation(
            message="Response time improved by 15% after optimization",
            event_type="performance",
            context={"improvement_percent": 15, "avg_response_time_ms": 120, "optimization": "cache_tuning"}
        )
        
        time.sleep(1)
        
        # Test warning (interesting)
        self.emit_observation(
            message="Memory usage approaching 80% threshold",
            event_type="warning",
            context={"memory_usage_percent": 78, "threshold": 80, "action_required": True}
        )
        
        time.sleep(1)
        
        # Test security event (interesting)
        self.emit_observation(
            message="Detected and blocked suspicious API request",
            event_type="security",
            context={"blocked_requests": 1, "threat_level": "medium", "source_ip": "192.168.1.100"}
        )
        
        time.sleep(1)
        
        # Test success
        self.emit_observation(
            message="All test operations completed successfully",
            event_type="success",
            context={"operations_completed": 6, "duration_seconds": 6}
        )
        
        self.operation_count += 1

def main():
    """Run the observation emission test"""
    print("🎬 Testing Beastly Module Observation Emission")
    print("=" * 50)
    
    # Create test module
    test_module = TestObservationModule()
    
    print(f"✅ Created test module: {test_module.get_module_info()['name']}")
    print(f"📊 Module health: {test_module.get_health_status().health_score}")
    print()
    
    # Perform test operations
    print("🔄 Performing test operations (emitting observations)...")
    test_module.perform_test_operations()
    
    print()
    print("✅ Test completed!")
    print("📰 Check the Observatory Activity Feed to see the emitted observations")
    print("🌐 Visit http://localhost:8000 to view the dashboard")
    print()
    print("💡 The observations should appear in:")
    print("   - WebSocket stream at ws://localhost:8000/ws/observations")
    print("   - HTTP API at http://localhost:8000/api/observations/recent")

if __name__ == "__main__":
    main()