#!/usr/bin/env python3
"""
Test ReflectiveModule Redis auto-registration from within a container
using host.docker.internal to reach Redis on the macOS host.
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, '/app')

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleCapability, ModuleHealth, ModuleStatus, GracefulDegradationResult

class ContainerizedTestModule(ReflectiveModule):
    """Test ReflectiveModule running in a container"""
    
    def get_module_info(self):
        return {
            'module_id': 'containerized_test_module', 
            'version': '1.0.0',
            'container_id': os.getenv('HOSTNAME', 'unknown'),
            'environment': 'docker_container'
        }
    
    def get_capabilities(self):
        return [ModuleCapability.CORE_FUNCTIONALITY, ModuleCapability.MONITORING]
    
    def get_health_status(self):
        return ModuleHealth(
            module_id='containerized_test_module',
            status=ModuleStatus.HEALTHY, 
            health_score=1.0, 
            issues=[],
            last_check=datetime.now(),
            uptime_seconds=30, 
            error_count=0, 
            warning_count=0
        )
    
    def graceful_degradation(self):
        return GracefulDegradationResult(
            success=True, 
            degraded_capabilities=[], 
            remaining_capabilities=self.get_capabilities()
        )

if __name__ == "__main__":
    print("🐳 Starting containerized ReflectiveModule test with smart Redis detection...")
    print(f"REDIS_HOST env var: {os.getenv('REDIS_HOST', 'NOT SET - will use smart detection')}")
    print(f"REDIS_PORT: {os.getenv('REDIS_PORT', 'not set')}")
    print(f"Container Hostname: {os.getenv('HOSTNAME', 'unknown')}")
    print(f"Docker env file exists: {os.path.exists('/.dockerenv')}")
    
    try:
        # Create the test module - should auto-detect container and use host.docker.internal
        print("🧠 Creating module with smart Redis host detection...")
        test_module = ContainerizedTestModule()
        print("✅ ContainerizedTestModule created successfully")
        print("✅ Smart detection should have resolved Redis host automatically")
        
        # Keep container alive for a bit to maintain registration
        import time
        print("⏳ Keeping container alive for 10 seconds...")
        time.sleep(10)
        print("✅ Test completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)