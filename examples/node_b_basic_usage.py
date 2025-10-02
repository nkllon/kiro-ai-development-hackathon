#!/usr/bin/env python3
"""
Basic usage example for Node B Management System

Demonstrates how to use the core interfaces and components.
"""

import asyncio
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from node_b_management import (
    NodeBComponent,
    NodeState,
    INodeLifecycle,
    IHealthMonitoring,
    INetworkCommunication
)


class ExampleNodeBManager(NodeBComponent):
    """Example Node B manager implementation"""
    
    def __init__(self):
        super().__init__("example_manager", "example_node_1")
    
    async def demonstrate_functionality(self):
        """Demonstrate basic Node B management functionality"""
        print(f"Node B Manager: {self.component_name}")
        print(f"Node ID: {self.node_id}")
        print(f"Module ID: {self.module_id}")
        
        # Show module info
        print("\n--- Module Information ---")
        module_info = self.get_module_info()
        for key, value in module_info.items():
            print(f"{key}: {value}")
        
        # Show health status
        print("\n--- Health Status ---")
        health = self.get_health_status()
        print(f"Status: {health.status.value}")
        print(f"Health Score: {health.health_score}")
        print(f"Issues: {health.issues}")
        print(f"Uptime: {health.uptime_seconds:.2f} seconds")
        
        # Show capabilities
        print("\n--- Capabilities ---")
        capabilities = self.get_capabilities()
        for cap in capabilities:
            print(f"- {cap.value}")
        
        # Demonstrate metrics
        print("\n--- Node B Metrics ---")
        metrics = self.get_node_b_metrics()
        print(f"Messages processed: {metrics['node_b_specific']['messages_processed']}")
        print(f"Messages sent: {metrics['node_b_specific']['messages_sent']}")
        print(f"Network events: {metrics['node_b_specific']['network_events']}")
        
        # Simulate some activity
        print("\n--- Simulating Activity ---")
        self.increment_message_count("processed")
        self.increment_message_count("sent")
        self.increment_network_events()
        self.increment_health_checks()
        
        updated_metrics = self.get_node_b_metrics()
        print(f"Updated messages processed: {updated_metrics['node_b_specific']['messages_processed']}")
        print(f"Updated messages sent: {updated_metrics['node_b_specific']['messages_sent']}")
        print(f"Updated network events: {updated_metrics['node_b_specific']['network_events']}")
        
        # Test Beast Mode compliance
        print("\n--- Beast Mode Compliance ---")
        compliance = await self.validate_beast_mode_compliance()
        for check, result in compliance.items():
            status = "✅" if result else "❌"
            print(f"{status} {check}: {result}")


async def main():
    """Main example function"""
    print("Node B Management System - Basic Usage Example")
    print("=" * 50)
    
    # Create example manager
    manager = ExampleNodeBManager()
    
    # Demonstrate functionality
    await manager.demonstrate_functionality()
    
    print("\n" + "=" * 50)
    print("Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())