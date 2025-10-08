#!/usr/bin/env python3
"""
ReflectiveModule Interactive Demo
================================

An interactive command-line interface for exploring ReflectiveModule capabilities.
This demo allows users to experiment with health monitoring, metrics collection,
and observability features in real-time.

Usage:
    python examples/demos/reflective_module_interactive.py

Author: Beast Mode Framework
Date: 2025-01-27
"""

import os
import sys
import time
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import ReflectiveModule components
try:
    from src.rm_ddd.core.unified_reflective_module import (
        ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability,
        GracefulDegradationResult
    )
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  ReflectiveModule not available: {e}")
    IMPORTS_AVAILABLE = False


class InteractiveReflectiveModule(ReflectiveModule):
    """Interactive ReflectiveModule for demonstration purposes."""
    
    def __init__(self, module_name: str = "InteractiveDemo"):
        super().__init__()
        self.module_id = module_name
        self._custom_data = {}
        self._operation_count = 0
        self._simulated_load = 0.0
        self._is_degraded = False
        self._custom_capabilities = [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.MONITORING
        ]
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": self.module_id,
            "name": f"Interactive {self.module_id}",
            "version": "1.0.0",
            "description": "Interactive ReflectiveModule for demonstration",
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "statistics": {
                "operation_count": self._operation_count,
                "simulated_load": self._simulated_load,
                "custom_data_items": len(self._custom_data),
                "is_degraded": self._is_degraded,
                "uptime_seconds": (datetime.now() - self._start_time).total_seconds()
            }
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        return self._custom_capabilities
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        try:
            issues = []
            health_score = 1.0
            
            # Check simulated load
            if self._simulated_load > 0.8:
                issues.append(f"High simulated load: {self._simulated_load:.1%}")
                health_score *= 0.6
            elif self._simulated_load > 0.6:
                issues.append(f"Moderate simulated load: {self._simulated_load:.1%}")
                health_score *= 0.8
            
            # Check degradation status
            if self._is_degraded:
                issues.append("Module is in degraded mode")
                health_score *= 0.7
            
            # Check operation count (simulate wear)
            if self._operation_count > 100:
                issues.append(f"High operation count: {self._operation_count}")
                health_score *= 0.9
            
            # Determine overall status
            if health_score >= 0.9:
                status = ModuleStatus.HEALTHY
            elif health_score >= 0.7:
                status = ModuleStatus.WARNING
            elif health_score >= 0.5:
                status = ModuleStatus.DEGRADED
            else:
                status = ModuleStatus.ERROR
                
        except Exception as e:
            status = ModuleStatus.ERROR
            health_score = 0.0
            issues = [f"Health check failed: {str(e)}"]
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds(),
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - RDI Compliant"""
        try:
            # In degraded mode, reduce capabilities
            remaining_capabilities = [
                ModuleCapability.CORE_FUNCTIONALITY,
                ModuleCapability.MONITORING
            ]
            
            degraded_capabilities = [
                ModuleCapability.DATA_PROCESSING
            ]
            
            # Enable degraded mode
            self._is_degraded = True
            self._custom_capabilities = remaining_capabilities
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=degraded_capabilities,
                remaining_capabilities=remaining_capabilities
            )
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=[ModuleCapability.CORE_FUNCTIONALITY],
                remaining_capabilities=[],
                error_message=str(e)
            )
    
    def perform_operation(self, operation_type: str = "default") -> Dict[str, Any]:
        """Perform a custom operation with tracing."""
        with self.trace_operation("perform_operation", operation_type=operation_type) as trace:
            self._operation_count += 1
            
            # Simulate operation time
            operation_time = random.uniform(0.1, 1.0)
            time.sleep(operation_time)
            
            # Simulate occasional failures
            if random.random() < 0.1:  # 10% failure rate
                self._increment_error_count()
                raise Exception(f"Simulated failure in {operation_type} operation")
            
            result = {
                "operation_type": operation_type,
                "operation_count": self._operation_count,
                "execution_time": operation_time,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
            trace.output_result = result
            return result
    
    def set_simulated_load(self, load_percentage: float) -> Dict[str, Any]:
        """Set simulated system load."""
        self._simulated_load = max(0.0, min(1.0, load_percentage))
        return {
            "simulated_load": self._simulated_load,
            "load_percentage": f"{self._simulated_load:.1%}",
            "timestamp": datetime.now().isoformat()
        }
    
    def store_custom_data(self, key: str, value: Any) -> Dict[str, Any]:
        """Store custom data in the module."""
        with self.trace_operation("store_custom_data", key=key) as trace:
            self._custom_data[key] = {
                "value": value,
                "stored_at": datetime.now().isoformat()
            }
            
            result = {
                "key": key,
                "stored": True,
                "total_items": len(self._custom_data)
            }
            
            trace.output_result = result
            return result
    
    def get_custom_data(self, key: Optional[str] = None) -> Dict[str, Any]:
        """Get custom data from the module."""
        if key:
            return self._custom_data.get(key, {"error": "Key not found"})
        else:
            return dict(self._custom_data)
    
    def reset_module(self) -> Dict[str, Any]:
        """Reset module to initial state."""
        self._operation_count = 0
        self._simulated_load = 0.0
        self._is_degraded = False
        self._custom_data.clear()
        self._error_count = 0
        self._warning_count = 0
        self._custom_capabilities = [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.MONITORING
        ]
        
        return {
            "status": "reset",
            "timestamp": datetime.now().isoformat(),
            "message": "Module reset to initial state"
        }
class In
teractiveReflectiveModuleDemo:
    """Interactive ReflectiveModule demonstration."""
    
    def __init__(self):
        if IMPORTS_AVAILABLE:
            self.module = InteractiveReflectiveModule("DemoModule")
        else:
            self.module = None
    
    def display_banner(self):
        """Display the demo banner."""
        print("\n" + "=" * 70)
        print("🔧 ReflectiveModule Pattern - Interactive Demo")
        print("🐺 Beast Mode Framework")
        print("Explore health monitoring, metrics, and observability!")
        print("=" * 70)
        
        if not IMPORTS_AVAILABLE:
            print("\n⚠️  Note: ReflectiveModule not available.")
            print("This demo will run in simulation mode.")
        
        print("\nWelcome to the ReflectiveModule interactive demo!")
        print("Experiment with health monitoring, metrics, and observability features.")
    
    def display_menu(self):
        """Display the main menu."""
        print("\n📋 Available Commands:")
        print("  1. 📊 View Module Information")
        print("  2. 🏥 Check Health Status")
        print("  3. 🎯 View Capabilities")
        print("  4. 🚀 Perform Operation")
        print("  5. 📈 Set Simulated Load")
        print("  6. 💾 Store Custom Data")
        print("  7. 📖 View Custom Data")
        print("  8. 🛡️  Test Graceful Degradation")
        print("  9. 💻 Generate CLI Interface")
        print(" 10. 📋 Execute CLI Command")
        print(" 11. 🔄 Reset Module")
        print(" 12. 📖 Show Help")
        print("  0. 🚪 Exit")
        print("\n" + "-" * 50)
    
    def view_module_information(self):
        """View comprehensive module information."""
        print("\n📊 Module Information")
        print("-" * 30)
        
        if not IMPORTS_AVAILABLE:
            print("📝 Module information (simulated):")
            print("   🆔 Module ID: DemoModule")
            print("   📝 Name: Interactive DemoModule")
            print("   🔢 Version: 1.0.0")
            return
        
        info = self.module.get_module_info()
        
        print(f"🆔 Module ID: {info['module_id']}")
        print(f"📝 Name: {info['name']}")
        print(f"🔢 Version: {info['version']}")
        print(f"📄 Description: {info['description']}")
        print(f"🎯 Capabilities: {', '.join(info['capabilities'])}")
        
        print(f"\n📊 Statistics:")
        stats = info['statistics']
        for key, value in stats.items():
            if isinstance(value, float):
                if 'percentage' in key or 'load' in key:
                    print(f"   {key}: {value:.1%}")
                else:
                    print(f"   {key}: {value:.2f}")
            else:
                print(f"   {key}: {value}")
    
    def check_health_status(self):
        """Check and display health status."""
        print("\n🏥 Health Status Check")
        print("-" * 30)
        
        if not IMPORTS_AVAILABLE:
            print("📝 Health status (simulated):")
            print("   ✅ Status: healthy")
            print("   💯 Health Score: 1.00")
            return
        
        health = self.module.get_health_status()
        
        # Status with emoji
        status_emoji = {
            ModuleStatus.HEALTHY: "✅",
            ModuleStatus.WARNING: "⚠️",
            ModuleStatus.DEGRADED: "🔶",
            ModuleStatus.ERROR: "❌",
            ModuleStatus.UNKNOWN: "❓"
        }.get(health.status, "❓")
        
        print(f"{status_emoji} Status: {health.status.value}")
        print(f"💯 Health Score: {health.health_score:.2f}")
        print(f"⏱️  Uptime: {health.uptime_seconds:.1f}s")
        print(f"❌ Error Count: {health.error_count}")
        print(f"⚠️  Warning Count: {health.warning_count}")
        print(f"🕐 Last Check: {health.last_check.strftime('%H:%M:%S')}")
        
        if health.issues:
            print(f"\n🔍 Issues Detected:")
            for issue in health.issues:
                print(f"   • {issue}")
        else:
            print(f"\n✅ No issues detected")
    
    def view_capabilities(self):
        """View module capabilities."""
        print("\n🎯 Module Capabilities")
        print("-" * 30)
        
        if not IMPORTS_AVAILABLE:
            print("📝 Capabilities (simulated):")
            print("   • core_functionality")
            print("   • data_processing")
            print("   • monitoring")
            return
        
        capabilities = self.module.get_capabilities()
        
        print(f"📋 Total Capabilities: {len(capabilities)}")
        for cap in capabilities:
            print(f"   • {cap.value}")
        
        # Show capability descriptions
        capability_descriptions = {
            ModuleCapability.CORE_FUNCTIONALITY: "Essential module operations",
            ModuleCapability.DATA_PROCESSING: "Data manipulation and transformation",
            ModuleCapability.API_INTEGRATION: "External API communication",
            ModuleCapability.VALIDATION: "Data and operation validation",
            ModuleCapability.MONITORING: "Health and performance monitoring"
        }
        
        print(f"\n📖 Capability Descriptions:")
        for cap in capabilities:
            desc = capability_descriptions.get(cap, "No description available")
            print(f"   🔧 {cap.value}: {desc}")
    
    def perform_operation(self):
        """Perform a custom operation."""
        print("\n🚀 Perform Operation")
        print("-" * 30)
        
        if not IMPORTS_AVAILABLE:
            print("📝 Performing operation (simulated)...")
            print("✅ Operation completed successfully")
            return
        
        # Get operation type from user
        operation_types = [
            "data_processing",
            "validation",
            "computation",
            "file_operation",
            "network_request"
        ]
        
        print("Available operation types:")
        for i, op_type in enumerate(operation_types, 1):
            print(f"  {i}. {op_type}")
        
        try:
            choice = input("Select operation type (1-5, or press Enter for default): ").strip()
            if choice:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(operation_types):
                    operation_type = operation_types[choice_idx]
                else:
                    operation_type = "default"
            else:
                operation_type = "default"
        except ValueError:
            operation_type = "default"
        
        print(f"\n🔄 Executing {operation_type} operation...")
        
        try:
            result = self.module.perform_operation(operation_type)
            print(f"✅ Operation completed successfully!")
            print(f"   ⏱️  Execution Time: {result['execution_time']:.2f}s")
            print(f"   🔢 Operation Count: {result['operation_count']}")
            print(f"   🕐 Timestamp: {result['timestamp']}")
            
        except Exception as e:
            print(f"❌ Operation failed: {e}")
    
    def set_simulated_load(self):
        """Set simulated system load."""
        print("\n📈 Set Simulated Load")
        print("-" * 30)
        
        if not IMPORTS_AVAILABLE:
            print("📝 Setting simulated load (simulated)...")
            print("✅ Load set to 50%")
            return
        
        try:
            load_input = input("Enter load percentage (0-100): ").strip()
            load_percentage = float(load_input) / 100.0
            
            result = self.module.set_simulated_load(load_percentage)
            print(f"✅ Simulated load set to {result['load_percentage']}")
            
            # Show impact on health
            health = self.module.get_health_status()
            print(f"🏥 Health impact: {health.status.value} (Score: {health.health_score:.2f})")
            
        except ValueError:
            print("❌ Invalid input. Please enter a number between 0 and 100.")
        except Exception as e:
            print(f"❌ Failed to set load: {e}")
    
    def store_custom_data(self):
        """Store custom data in the module."""
        print("\n💾 Store Custom Data")
        print("-" * 30)
        
        if not IMPORTS_AVAILABLE:
            print("📝 Storing custom data (simulated)...")
            print("✅ Data stored successfully")
            return
        
        key = input("Enter data key: ").strip()
        if not key:
            print("❌ Key cannot be empty")
            return
        
        value = input("Enter data value: ").strip()
        
        try:
            result = self.module.store_custom_data(key, value)
            print(f"✅ Data stored successfully!")
            print(f"   🔑 Key: {result['key']}")
            print(f"   📊 Total Items: {result['total_items']}")
            
        except Exception as e:
            print(f"❌ Failed to store data: {e}")
    
    def view_custom_data(self):
        """View stored custom data."""
        print("\n📖 View Custom Data")
        print("-" * 30)
        
        if not IMPORTS_AVAILABLE:
            print("📝 Custom data (simulated):")
            print("   🔑 sample_key: sample_value")
            return
        
        data = self.module.get_custom_data()
        
        if not data:
            print("📝 No custom data stored")
            return
        
        print(f"📊 Total Items: {len(data)}")
        
        for key, item in data.items():
            print(f"\n🔑 Key: {key}")
            print(f"   📄 Value: {item['value']}")
            print(f"   🕐 Stored At: {item['stored_at']}")
    
    def test_graceful_degradation(self):
        """Test graceful degradation."""
        print("\n🛡️  Test Graceful Degradation")
        print("-" * 30)
        
        if not IMPORTS_AVAILABLE:
            print("📝 Testing graceful degradation (simulated)...")
            print("✅ Graceful degradation successful")
            return
        
        print("🔄 Testing graceful degradation...")
        
        # Show initial state
        initial_capabilities = self.module.get_capabilities()
        initial_health = self.module.get_health_status()
        
        print(f"📊 Initial State:")
        print(f"   🎯 Capabilities: {[cap.value for cap in initial_capabilities]}")
        print(f"   🏥 Health: {initial_health.status.value} ({initial_health.health_score:.2f})")
        
        # Perform graceful degradation
        degradation_result = self.module.graceful_degradation()
        
        if degradation_result.success:
            print(f"\n✅ Graceful degradation successful!")
            print(f"   📉 Degraded: {[cap.value for cap in degradation_result.degraded_capabilities]}")
            print(f"   📊 Remaining: {[cap.value for cap in degradation_result.remaining_capabilities]}")
            
            # Show post-degradation state
            post_health = self.module.get_health_status()
            print(f"\n🏥 Post-Degradation Health:")
            print(f"   📊 Status: {post_health.status.value}")
            print(f"   💯 Score: {post_health.health_score:.2f}")
            
            if post_health.issues:
                print(f"   ⚠️  Issues: {', '.join(post_health.issues)}")
            
        else:
            print(f"❌ Graceful degradation failed: {degradation_result.error_message}")
    
    def generate_cli_interface(self):
        """Generate and display CLI interface."""
        print("\n💻 Generate CLI Interface")
        print("-" * 30)
        
        if not IMPORTS_AVAILABLE:
            print("📝 CLI interface (simulated):")
            print("   📋 Available commands: get_health_status, perform_operation")
            return
        
        cli_interface = self.module.get_cli_interface()
        
        print(f"🆔 Module: {cli_interface['module_id']}")
        print(f"🏥 Health: {cli_interface['health_status']}")
        print(f"📋 Available Commands ({len(cli_interface['commands'])}):")
        
        for cmd_name, cmd_info in cli_interface['commands'].items():
            print(f"\n   🔧 {cmd_name}")
            print(f"      📝 Description: {cmd_info['docstring']}")
            print(f"      📋 Signature: {cmd_info['signature']}")
            
            if cmd_info['parameters']:
                print(f"      🎯 Parameters:")
                for param in cmd_info['parameters']:
                    required = "required" if param['required'] else "optional"
                    default = f" (default: {param['default']})" if param['default'] else ""
                    print(f"         • {param['name']} ({param['type']}) - {required}{default}")
    
    def execute_cli_command(self):
        """Execute a CLI command."""
        print("\n📋 Execute CLI Command")
        print("-" * 30)
        
        if not IMPORTS_AVAILABLE:
            print("📝 Executing CLI command (simulated)...")
            print("✅ Command executed successfully")
            return
        
        # Get available commands
        cli_interface = self.module.get_cli_interface()
        commands = list(cli_interface['commands'].keys())
        
        if not commands:
            print("❌ No CLI commands available")
            return
        
        print("Available commands:")
        for i, cmd in enumerate(commands, 1):
            print(f"  {i}. {cmd}")
        
        try:
            choice = input("Select command (number): ").strip()
            choice_idx = int(choice) - 1
            
            if 0 <= choice_idx < len(commands):
                command_name = commands[choice_idx]
                
                print(f"\n🚀 Executing {command_name}...")
                
                # Execute command (no parameters for simplicity)
                result = self.module.execute_cli_command(command_name)
                
                if result['success']:
                    print(f"✅ Command executed successfully!")
                    print(f"   📊 Result: {result['result']}")
                    print(f"   🕐 Executed At: {result['executed_at']}")
                else:
                    print(f"❌ Command failed: {result['error']}")
            else:
                print("❌ Invalid command selection")
                
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
        except Exception as e:
            print(f"❌ Command execution failed: {e}")
    
    def reset_module(self):
        """Reset module to initial state."""
        print("\n🔄 Reset Module")
        print("-" * 30)
        
        if not IMPORTS_AVAILABLE:
            print("📝 Resetting module (simulated)...")
            print("✅ Module reset successfully")
            return
        
        confirm = input("Are you sure you want to reset the module? (y/n): ").strip().lower()
        
        if confirm == 'y':
            result = self.module.reset_module()
            print(f"✅ {result['message']}")
            print(f"🕐 Reset At: {result['timestamp']}")
        else:
            print("❌ Reset cancelled")
    
    def show_help(self):
        """Display help information."""
        print("\n📖 ReflectiveModule Help")
        print("-" * 30)
        
        print("🔧 What is ReflectiveModule?")
        print("   ReflectiveModule is a pattern that provides comprehensive")
        print("   observability, health monitoring, and systematic error handling")
        print("   for all components in the Beast Mode Framework.")
        
        print("\n🎯 Key Features:")
        print("   • Health monitoring with status and scores")
        print("   • Performance metrics and operation tracing")
        print("   • Graceful degradation capabilities")
        print("   • Dynamic CLI interface generation")
        print("   • Systematic error handling and recovery")
        
        print("\n🚀 Getting Started:")
        print("   1. View module information (option 1)")
        print("   2. Check health status regularly (option 2)")
        print("   3. Perform operations and monitor impact (option 4)")
        print("   4. Experiment with simulated load (option 5)")
        print("   5. Test graceful degradation (option 8)")
        
        print("\n💡 Tips:")
        print("   • Monitor health scores - below 0.7 indicates issues")
        print("   • Use graceful degradation to handle failures")
        print("   • CLI interfaces are generated automatically from methods")
        print("   • Custom data storage demonstrates module state management")
        print("   • Reset the module to start fresh experiments")
        
        print("\n🔗 Health Status Meanings:")
        print("   ✅ HEALTHY (0.9-1.0): All systems operating normally")
        print("   ⚠️  WARNING (0.7-0.9): Minor issues detected")
        print("   🔶 DEGRADED (0.5-0.7): Reduced functionality")
        print("   ❌ ERROR (0.0-0.5): Significant problems")
    
    def run_interactive_demo(self):
        """Run the interactive demo."""
        self.display_banner()
        
        while True:
            self.display_menu()
            
            try:
                choice = input("Enter your choice (0-12): ").strip()
                
                if choice == "0":
                    print("\n👋 Thanks for exploring ReflectiveModule!")
                    print("🔧 Remember: Observability is the key to reliable systems!")
                    break
                elif choice == "1":
                    self.view_module_information()
                elif choice == "2":
                    self.check_health_status()
                elif choice == "3":
                    self.view_capabilities()
                elif choice == "4":
                    self.perform_operation()
                elif choice == "5":
                    self.set_simulated_load()
                elif choice == "6":
                    self.store_custom_data()
                elif choice == "7":
                    self.view_custom_data()
                elif choice == "8":
                    self.test_graceful_degradation()
                elif choice == "9":
                    self.generate_cli_interface()
                elif choice == "10":
                    self.execute_cli_command()
                elif choice == "11":
                    self.reset_module()
                elif choice == "12":
                    self.show_help()
                else:
                    print("❌ Invalid choice. Please enter a number from 0-12.")
                
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Demo interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                input("Press Enter to continue...")


def main():
    """Main entry point."""
    demo = InteractiveReflectiveModuleDemo()
    demo.run_interactive_demo()


if __name__ == "__main__":
    main()