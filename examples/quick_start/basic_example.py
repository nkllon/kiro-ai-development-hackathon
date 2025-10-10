#!/usr/bin/env python3
"""
Beast Mode AI Development Framework - Quick Start Example

This example demonstrates the core features of the Beast Mode framework
in a simple, easy-to-understand format. Perfect for getting started!
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from beast_mode.core.reflective_module import ReflectiveModule
    from beast_mode.ai_memory_palace.context_engine import ContextEngine
except ImportError:
    print("⚠️  Beast Mode modules not found. Using mock implementation for demo.")
    
    # Mock implementation for demonstration
    class ReflectiveModule:
        def __init__(self, name):
            self.name = name
            print(f"🔧 Initialized {name}")
        
        def log_info(self, message):
            print(f"ℹ️  {message}")
        
        def log_warning(self, message):
            print(f"⚠️  {message}")
        
        def get_health_status(self):
            return {"status": "healthy", "components": ["core", "memory"]}
    
    class ContextEngine:
        def __init__(self):
            self.storage = {}
        
        def store_context(self, key, context):
            self.storage[key] = context
            return True
        
        def get_context(self, key):
            return self.storage.get(key)


class QuickStartDemo(ReflectiveModule):
    """A simple demonstration of Beast Mode capabilities."""
    
    def __init__(self):
        super().__init__("QuickStartDemo")
        self.context_engine = ContextEngine()
    
    def setup_environment(self):
        """Set up basic environment variables for demo."""
        # Set default values if not already set
        os.environ.setdefault('REDIS_HOST', 'localhost')
        os.environ.setdefault('REDIS_PORT', '6379')
        os.environ.setdefault('REDIS_PASSWORD', '')
        os.environ.setdefault('ENVIRONMENT', 'demo')
        
        self.log_info("🔧 Environment configured for demo")
    
    def demonstrate_memory_palace(self):
        """Demonstrate AI Memory Palace functionality."""
        self.log_info("📚 Testing AI Memory Palace...")
        
        # Create sample context data
        context = {
            "project": "Beast Mode Framework",
            "purpose": "AI-powered development workflows",
            "features": [
                "AI Memory Palace - Advanced context management",
                "DAG Orchestration - Complex workflow management", 
                "ReflectiveModule - Self-monitoring components",
                "Security-First - Comprehensive credential management"
            ],
            "benefits": [
                "Rapid development",
                "Intelligent automation",
                "Robust error handling",
                "Scalable architecture"
            ]
        }
        
        # Store context in Memory Palace
        success = self.context_engine.store_context("demo_project", context)
        if success:
            self.log_info("✅ Context stored in Memory Palace")
        
        # Retrieve and validate context
        retrieved = self.context_engine.get_context("demo_project")
        if retrieved and retrieved.get("project") == "Beast Mode Framework":
            self.log_info("✅ Memory Palace retrieval successful")
            self.log_info(f"   Project: {retrieved['project']}")
            self.log_info(f"   Features: {len(retrieved['features'])} available")
        else:
            self.log_warning("⚠️ Memory Palace not fully available (Redis recommended)")
        
        return retrieved is not None
    
    def demonstrate_health_monitoring(self):
        """Demonstrate ReflectiveModule health monitoring."""
        self.log_info("📊 Checking system health...")
        
        # Get health status
        health = self.get_health_status()
        status = health.get("status", "unknown")
        components = health.get("components", [])
        
        self.log_info(f"   System Status: {status.upper()}")
        self.log_info(f"   Active Components: {len(components)}")
        
        # Simulate some metrics
        metrics = {
            "memory_usage": "45%",
            "response_time": "12ms",
            "uptime": "100%",
            "error_rate": "0.01%"
        }
        
        self.log_info("📈 Performance Metrics:")
        for metric, value in metrics.items():
            self.log_info(f"   {metric.replace('_', ' ').title()}: {value}")
        
        return status == "healthy"
    
    def demonstrate_workflow_orchestration(self):
        """Demonstrate basic workflow orchestration concepts."""
        self.log_info("🔄 Demonstrating workflow orchestration...")
        
        # Simulate a simple workflow
        workflow_steps = [
            "Initialize components",
            "Load configuration", 
            "Process data",
            "Generate results",
            "Cleanup resources"
        ]
        
        self.log_info("   Workflow Steps:")
        for i, step in enumerate(workflow_steps, 1):
            self.log_info(f"   {i}. {step} ✅")
        
        self.log_info("✅ Workflow orchestration demo completed")
        return True
    
    def run_demo(self):
        """Run the complete quick start demonstration."""
        print("=" * 60)
        print("🚀 Beast Mode AI Development Framework")
        print("   Quick Start Demo")
        print("=" * 60)
        
        # Setup
        self.setup_environment()
        
        # Run demonstrations
        demos = [
            ("AI Memory Palace", self.demonstrate_memory_palace),
            ("Health Monitoring", self.demonstrate_health_monitoring),
            ("Workflow Orchestration", self.demonstrate_workflow_orchestration),
        ]
        
        results = {}
        for demo_name, demo_func in demos:
            print(f"\n📋 {demo_name} Demo")
            print("-" * 40)
            try:
                results[demo_name] = demo_func()
            except Exception as e:
                self.log_warning(f"Demo error: {e}")
                results[demo_name] = False
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Demo Summary")
        print("=" * 60)
        
        successful_demos = sum(1 for success in results.values() if success)
        total_demos = len(results)
        
        for demo_name, success in results.items():
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"   {demo_name}: {status}")
        
        print(f"\nResults: {successful_demos}/{total_demos} demos successful")
        
        if successful_demos == total_demos:
            print("\n🎉 All demos completed successfully!")
            print("   Beast Mode is ready to use!")
        else:
            print("\n⚠️  Some demos had issues. This is normal in minimal environments.")
            print("   For full functionality, ensure Redis is available.")
        
        print("\n📖 Next Steps:")
        print("   1. Explore examples/demos/ for advanced features")
        print("   2. Read docs/api/README.md for API documentation")
        print("   3. Check docs/usage/README.md for usage guides")
        print("   4. Visit docs/installation/ for setup help")
        
        return successful_demos > 0


def main():
    """Main entry point for the quick start demo."""
    try:
        demo = QuickStartDemo()
        success = demo.run_demo()
        
        if success:
            print("\n✨ Welcome to Beast Mode! Happy coding! ✨")
            sys.exit(0)
        else:
            print("\n⚠️  Demo completed with some issues.")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        print("   This might indicate a setup issue.")
        print("   Please check the installation guide.")
        sys.exit(1)


if __name__ == "__main__":
    main()