#!/usr/bin/env python3
"""
Test Registry Lifecycle Events

Demonstrates the exact lifecycle events and when registry interrogation occurs.
"""

import sys
import os
import inspect

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from beast_mode.core.unified_reflective_module import (
    ReflectiveModule,
    registered,
    InterfaceType,
    ModuleCapability,
)
from typing import Dict, List, Any

print("🔍 Registry Lifecycle Events Demonstration")
print("=" * 60)

# Track lifecycle events
lifecycle_events = []


def track_event(event_name: str, details: str = ""):
    """Track lifecycle events for demonstration"""
    lifecycle_events.append(f"{len(lifecycle_events) + 1}. {event_name}: {details}")
    print(f"📋 {event_name}: {details}")


# 1. Class Definition Phase
print("\n🏗️  PHASE 1: Class Definition")
print("-" * 40)

track_event("Class Definition", "ServiceManager class defined")


@registered(interface_type=InterfaceType.DOMAIN_SERVICE)
class ServiceManager(ReflectiveModule):
    """Service management module with lifecycle tracking"""

    def __init__(self, service_name: str):
        track_event("__init__ called", f"Creating ServiceManager-{service_name}")
        super().__init__(module_name=f"ServiceManager-{service_name}")
        track_event("__init__ completed", f"ServiceManager-{service_name} initialized")
        self.service_name = service_name
        self.services = {}

    def get_module_info(self) -> Dict[str, Any]:
        track_event("get_module_info called", "Retrieving module information")
        info = super().get_module_info()
        info.update(
            {"service_name": self.service_name, "managed_services": len(self.services)}
        )
        return info

    def get_capabilities(self) -> List[ModuleCapability]:
        return [ModuleCapability.DEPENDENCY_MANAGEMENT, ModuleCapability.INTEGRATION]

    def get_dependencies(self) -> List[str]:
        return ["ServiceRegistry", "ConfigurationManager"]

    def check_health(self):
        track_event("check_health called", "Performing health check")
        return super().check_health()

    def get_configuration(self) -> Dict[str, Any]:
        config = super().get_configuration()
        config.update({"service_name": self.service_name, "max_services": 100})
        return config

    def get_metrics(self) -> Dict[str, Any]:
        track_event("get_metrics called", "Collecting module metrics")
        metrics = super().get_metrics()
        metrics.update({"services_managed": len(self.services)})
        return metrics


track_event("Decorator Applied", "@registered decorator configured class")

# 2. Instance Creation Phase
print("\n🚀 PHASE 2: Instance Creation")
print("-" * 40)

track_event("Instance Creation", "Creating ServiceManager instance")
service_manager = ServiceManager("UserService")

# 3. Registry Integration Verification
print("\n🔍 PHASE 3: Registry Integration Verification")
print("-" * 40)

# Check registry integration
module_info = service_manager.get_module_info()
track_event(
    "Registry Integration",
    f"Registry ID: {module_info.get('registry_id', 'Not registered')}",
)
track_event("Interface Type", f"Type: {module_info.get('interface_type', 'Unknown')}")
track_event("Domain Terms", f"Terms: {module_info.get('domain_terms', [])}")
track_event("Source Location", f"File: {module_info.get('source_file', 'Unknown')}")

# 4. Runtime Operations
print("\n⚙️  PHASE 4: Runtime Operations")
print("-" * 40)

# Health check
health = service_manager.check_health()
track_event(
    "Health Check", f"Status: {health.status.value}, Score: {health.health_score}"
)

# Metrics collection
metrics = service_manager.get_metrics()
track_event(
    "Metrics Collection",
    f"Registry Registered: {metrics.get('registry_registered', False)}",
)
track_event("Domain Terms Count", f"Count: {metrics.get('domain_terms_count', 0)}")
track_event("Methods Count", f"Count: {metrics.get('methods_count', 0)}")

# 5. Activity Tracking
print("\n📊 PHASE 5: Activity Tracking")
print("-" * 40)

track_event("Activity Update", "Incrementing error count")
service_manager.increment_error_count()

track_event("Activity Update", "Incrementing warning count")
service_manager.increment_warning_count()

# Check updated metrics
updated_metrics = service_manager.get_metrics()
track_event("Updated Metrics", f"Error Count: {updated_metrics.get('error_count', 0)}")
track_event(
    "Updated Metrics", f"Warning Count: {updated_metrics.get('warning_count', 0)}"
)

# 6. Registry Status Check
print("\n📋 PHASE 6: Registry Status Check")
print("-" * 40)

try:
    from beast_mode.interface_governance.interface_registry import (
        BeastModeInterfaceRegistry,
    )

    registry = BeastModeInterfaceRegistry()
    status = registry.get_registry_status()
    track_event(
        "Registry Status", f"Total Interfaces: {status.get('total_interfaces', 0)}"
    )
    track_event(
        "Registry Status", f"Active Interfaces: {status.get('active_interfaces', 0)}"
    )
    track_event("Registry Status", f"Duplicates: {status.get('duplicates', 0)}")
except Exception as e:
    track_event("Registry Status", f"Error: {e}")

# 7. Lifecycle Summary
print("\n📝 LIFECYCLE SUMMARY")
print("=" * 60)

print(f"Total lifecycle events tracked: {len(lifecycle_events)}")
print("\nEvent Timeline:")
for event in lifecycle_events:
    print(f"  {event}")

print(f"\n🎯 Key Registry Integration Points:")
print(f"  ✅ Class Definition: Decorator configuration")
print(f"  ✅ Instance Creation: Automatic registration")
print(f"  ✅ Runtime Operations: Health and metrics integration")
print(f"  ✅ Activity Tracking: Timestamp updates")
print(f"  ✅ Status Monitoring: Registry-wide statistics")

print(f"\n🔍 Registry Interrogation Triggers:")
print(f"  📋 __init__(): Initial registration and metadata capture")
print(f"  🏥 check_health(): Registry status validation")
print(f"  📊 get_metrics(): Registry integration metrics")
print(f"  ℹ️  get_module_info(): Comprehensive metadata retrieval")

print(f"\n🎉 Registry Lifecycle Test Complete!")
