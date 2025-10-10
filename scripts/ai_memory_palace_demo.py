#!/usr/bin/env python3
"""
AI Memory Palace Demo

Demonstrates the AI Memory Palace functionality with a simple CLI interface.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from src.ai_memory_palace.manager.context_manager import ContextManager
    from src.ai_memory_palace.models.context_models import SessionContext, ProjectState
    print("✅ AI Memory Palace modules imported successfully!")
except ImportError as e:
    print(f"❌ Failed to import AI Memory Palace modules: {e}")
    sys.exit(1)


def demo_context_operations():
    """Demonstrate basic context operations."""
    print("\n🧠 AI Memory Palace Demo")
    print("=" * 50)
    
    # Initialize Context Manager
    print("🔄 Initializing Context Manager...")
    try:
        context_manager = ContextManager()
        print("✅ Context Manager initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize Context Manager: {e}")
        return False
    
    # Test context loading
    print("\n🔄 Testing context loading...")
    try:
        project_path = "."
        context = context_manager.load_session_context(project_path)
        
        if context:
            print(f"✅ Context loaded for project: {context.project_id}")
            print(f"   Session ID: {context.session_id}")
            print(f"   Timestamp: {context.timestamp}")
            print(f"   Conversation history items: {len(context.conversation_history)}")
        else:
            print("❌ Failed to load context")
            return False
            
    except Exception as e:
        print(f"❌ Context loading failed: {e}")
        return False
    
    # Test context saving
    print("\n🔄 Testing context saving...")
    try:
        # Add some test data to context
        context.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "demo_message",
            "content": "This is a test message for the AI Memory Palace demo"
        })
        
        context.decisions_made.append({
            "timestamp": datetime.now().isoformat(),
            "summary": "Decided to test the AI Memory Palace system",
            "rationale": "Testing is important for validation"
        })
        
        # Save context
        success = context_manager.save_context_event(context, {
            "type": "demo_save",
            "timestamp": datetime.now().isoformat()
        })
        
        if success:
            print("✅ Context saved successfully!")
        else:
            print("❌ Failed to save context")
            return False
            
    except Exception as e:
        print(f"❌ Context saving failed: {e}")
        return False
    
    # Test context summary
    print("\n🔄 Testing context summary...")
    try:
        summary = context_manager.get_context_summary(context.project_id)
        
        if summary:
            print(f"✅ Context summary generated:")
            print(f"   Project: {summary.project_id}")
            print(f"   Last session: {summary.last_session}")
            print(f"   Total events: {summary.total_events}")
            print(f"   System health: {summary.system_health}")
            print(f"   Context size: {summary.context_size_mb:.2f} MB")
        else:
            print("❌ Failed to generate context summary")
            return False
            
    except Exception as e:
        print(f"❌ Context summary failed: {e}")
        return False
    
    return True


def demo_health_monitoring():
    """Demonstrate health monitoring capabilities."""
    print("\n🏥 Health Monitoring Demo")
    print("=" * 50)
    
    try:
        context_manager = ContextManager()
        
        # Get module info
        module_info = context_manager.get_module_info()
        print(f"📋 Module Info:")
        for key, value in module_info.items():
            print(f"   {key}: {value}")
        
        # Get health status
        health_status = context_manager.get_health_status()
        print(f"\n🏥 Health Status:")
        for key, value in health_status.items():
            print(f"   {key}: {value}")
        
        # Get capabilities
        capabilities = context_manager.get_capabilities()
        print(f"\n🔧 Capabilities:")
        for capability in capabilities:
            print(f"   - {capability}")
        
        return True
        
    except Exception as e:
        print(f"❌ Health monitoring demo failed: {e}")
        return False


def main():
    """Main demo function."""
    print("🐺 AI Memory Palace - Beast Mode Implementation")
    print("Eliminating the '50 first dates' problem through persistent context!")
    
    # Run context operations demo
    context_success = demo_context_operations()
    
    # Run health monitoring demo
    health_success = demo_health_monitoring()
    
    # Final summary
    print("\n" + "=" * 50)
    print("📊 Demo Summary")
    print("=" * 50)
    
    if context_success and health_success:
        print("🎉 All demos completed successfully!")
        print("\n✨ The AI Memory Palace is working correctly!")
        print("\n📝 Key Features Demonstrated:")
        print("   ✅ Context loading and session restoration")
        print("   ✅ Context saving and persistence")
        print("   ✅ Context summarization")
        print("   ✅ Health monitoring and observability")
        print("   ✅ Beast Mode ReflectiveModule integration")
        print("   ✅ Graceful error handling")
        
        print("\n🚀 Next Steps:")
        print("   1. Integrate with your AI assistant workflow")
        print("   2. Configure project-specific context policies")
        print("   3. Set up monitoring and alerting")
        print("   4. Train team on context management best practices")
        
        return True
    else:
        print("❌ Some demos failed - check the error messages above")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)