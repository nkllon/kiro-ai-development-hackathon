#!/usr/bin/env python3
"""Demo script for Multi-Instance Kiro Orchestration System."""

from datetime import timedelta
from src.multi_instance_orchestration.protocol.handler import TextProtocolHandler
from src.multi_instance_orchestration.protocol.models import StructuredAction, ActionResult


def demo_handler(action: StructuredAction) -> ActionResult:
    """Demo action handler."""
    return ActionResult(
        success=True,
        message=f"Successfully executed {action.verb} {action.noun}",
        execution_time=timedelta(seconds=1.2),
        correlation_id=action.correlation_id,
        data={"task_id": action.parameters.get("task_id", "unknown")},
        side_effects=["logged action", "updated metrics"]
    )


def main():
    """Run the demo."""
    print("🚀 Multi-Instance Kiro Orchestration System Demo")
    print("=" * 50)
    
    # Create protocol handler
    handler = TextProtocolHandler("demo-instance")
    
    # Register demo handler
    handler.register_handler("run", "task", demo_handler)
    
    # Demo commands
    commands = [
        "run task user-auth beast-mode task_id=auth-123",
        "execute task payment-system in parallel",
        "halt instance kiro-3 gracefully",
        "check swarm status",
        "scale instances up count=5"
    ]
    
    print("\n📝 Parsing and executing commands:")
    print("-" * 40)
    
    for cmd in commands:
        print(f"\n💬 Command: '{cmd}'")
        
        try:
            # Parse command
            action = handler.parse_command(cmd)
            print(f"   ✅ Parsed: {action.verb} {action.noun} {action.modifiers}")
            
            # Validate command
            validation = handler.validate_command(action)
            if validation.is_valid:
                print("   ✅ Valid command")
            else:
                print(f"   ❌ Invalid: {validation.errors}")
                continue
            
            # Execute if handler exists
            if f"{action.verb}_{action.noun}" in handler.action_handlers:
                result = handler.execute_action(action)
                print(f"   🎯 Result: {result.message}")
                if result.data:
                    print(f"   📊 Data: {result.data}")
            else:
                print("   ⚠️  No handler registered")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Show system status
    print("\n📊 System Status:")
    print("-" * 20)
    status = handler.get_module_status()
    print(f"Module: {status.module_name} v{status.version}")
    print(f"Status: {status.status}")
    print(f"Uptime: {status.uptime:.2f}s")
    print(f"Commands processed: {handler.execution_stats['total_commands']}")
    print(f"Success rate: {handler.execution_stats['successful_commands']}/{handler.execution_stats['total_commands']}")
    
    # Show health indicators
    print("\n🏥 Health Indicators:")
    print("-" * 20)
    indicators = handler.get_health_indicators()
    for indicator in indicators[-3:]:  # Show last 3
        print(f"• {indicator.name}: {indicator.status} - {indicator.message}")
    
    # Show command help
    print("\n📚 Available Commands:")
    print("-" * 20)
    help_text = handler.get_command_help()
    print(help_text)
    
    print("\n✨ Demo completed successfully!")


if __name__ == "__main__":
    main()