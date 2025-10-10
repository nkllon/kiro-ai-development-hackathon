#!/usr/bin/env python3
"""
AI Memory Palace Interactive Demo
================================

An interactive command-line interface for exploring AI Memory Palace capabilities.
This demo allows users to experiment with different features and see real-time results.

Usage:
    python examples/demos/ai_memory_palace_interactive.py

Author: Beast Mode Framework
Date: 2025-01-27
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import AI Memory Palace components
try:
    from src.dag_orchestration.integration.ai_memory_palace_integration import (
        AIMemoryPalaceIntegration, ExecutionPattern
    )
    from src.beast_mode.observatory.ai_memory_palace_integration import (
        AIMemoryPalaceIntegration as ObservatoryIntegration,
        ProjectContext, ContextRetrievalStatus, ProjectType
    )
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  AI Memory Palace modules not available: {e}")
    IMPORTS_AVAILABLE = False


class InteractiveDemo:
    """Interactive AI Memory Palace demonstration."""
    
    def __init__(self):
        if IMPORTS_AVAILABLE:
            self.dag_integration = AIMemoryPalaceIntegration()
            self.observatory_integration = ObservatoryIntegration()
        else:
            self.dag_integration = None
            self.observatory_integration = None
        
        self.session_data = {
            "patterns_stored": 0,
            "contexts_retrieved": 0,
            "insights_generated": 0
        }
    
    def display_banner(self):
        """Display the demo banner."""
        print("\n" + "=" * 70)
        print("🧠 AI Memory Palace - Interactive Demo")
        print("🐺 Beast Mode Framework")
        print("Eliminating the '50 first dates' problem!")
        print("=" * 70)
        
        if not IMPORTS_AVAILABLE:
            print("\n⚠️  Note: AI Memory Palace modules not available.")
            print("This demo will run in simulation mode.")
        
        print("\nWelcome to the AI Memory Palace interactive demo!")
        print("Explore the features that make AI assistants remember and learn.")
    
    def display_menu(self):
        """Display the main menu."""
        print("\n📋 Available Commands:")
        print("  1. 🧠 Store Execution Pattern")
        print("  2. 🔍 Find Similar Patterns") 
        print("  3. 💡 Generate Learning Insights")
        print("  4. 🏗️  Get Project Context")
        print("  5. 👤 Create Session")
        print("  6. 📊 View Statistics")
        print("  7. 🏥 Check Health Status")
        print("  8. 🛡️  Test Graceful Degradation")
        print("  9. 📖 Show Help")
        print("  0. 🚪 Exit")
        print("\n" + "-" * 50)
    
    async def store_execution_pattern(self):
        """Interactive execution pattern storage."""
        print("\n🧠 Store Execution Pattern")
        print("-" * 30)
        
        if not IMPORTS_AVAILABLE:
            print("📝 Simulating pattern storage...")
            self.session_data["patterns_stored"] += 1
            print("✅ Pattern stored successfully (simulated)")
            return
        
        # Get user input for pattern
        print("Enter execution pattern details:")
        
        execution_id = input("Execution ID (e.g., 'task_001'): ").strip()
        if not execution_id:
            execution_id = f"interactive_{datetime.now().strftime('%H%M%S')}"
        
        task_type = input("Task type (data_processing/ml_training/web_scraping): ").strip()
        if not task_type:
            task_type = "data_processing"
        
        try:
            workers = int(input("Number of workers (1-16): ") or "4")
            data_size = int(input("Data size in MB (1-1000): ") or "100")
            exec_time = float(input("Execution time in seconds (1-300): ") or "30.0")
            memory_mb = int(input("Memory usage in MB (100-2048): ") or "512")
        except ValueError:
            print("⚠️  Using default values for numeric inputs")
            workers, data_size, exec_time, memory_mb = 4, 100, 30.0, 512
        
        pattern_data = {
            "task_type": task_type,
            "parallel_workers": workers,
            "data_size_mb": data_size,
            "complexity": "medium"
        }
        
        performance_metrics = {
            "execution_time_seconds": exec_time,
            "memory_usage_mb": memory_mb,
            "cpu_utilization": min(0.95, workers * 0.2),
            "parallelization_efficiency": max(1.0, workers * 0.3),
            "resource_utilization": min(0.9, memory_mb / 1024)
        }
        
        # Store the pattern
        success = await self.dag_integration.store_execution_pattern(
            execution_id, pattern_data, performance_metrics
        )
        
        if success:
            print(f"✅ Pattern '{execution_id}' stored successfully!")
            self.session_data["patterns_stored"] += 1
            
            # Show stored pattern details
            print(f"\n📋 Pattern Details:")
            print(f"   🆔 ID: {execution_id}")
            print(f"   🔧 Type: {task_type}")
            print(f"   👥 Workers: {workers}")
            print(f"   📊 Data Size: {data_size} MB")
            print(f"   ⏱️  Execution Time: {exec_time}s")
            print(f"   💾 Memory Usage: {memory_mb} MB")
        else:
            print("❌ Failed to store pattern")
    
    async def find_similar_patterns(self):
        """Interactive similar pattern search."""
        print("\n🔍 Find Similar Patterns")
        print("-" * 30)
        
        if not IMPORTS_AVAILABLE:
            print("📝 Simulating pattern search...")
            print("✅ Found 2 similar patterns (simulated)")
            return
        
        # Get search criteria
        print("Enter search criteria:")
        
        task_type = input("Task type (data_processing/ml_training/web_scraping): ").strip()
        if not task_type:
            task_type = "data_processing"
        
        try:
            workers = int(input("Number of workers (1-16): ") or "4")
            data_size = int(input("Data size in MB (1-1000): ") or "100")
        except ValueError:
            workers, data_size = 4, 100
        
        query_pattern = {
            "task_type": task_type,
            "parallel_workers": workers,
            "data_size_mb": data_size,
            "complexity": "medium"
        }
        
        # Search for similar patterns
        similar_patterns = await self.dag_integration.retrieve_similar_patterns(
            query_pattern, limit=5
        )
        
        if similar_patterns:
            print(f"\n🎯 Found {len(similar_patterns)} similar patterns:")
            for i, pattern in enumerate(similar_patterns, 1):
                print(f"\n   📋 Pattern {i}: {pattern.execution_id}")
                print(f"      🎯 Similarity: {pattern.similarity_score:.2f}")
                print(f"      ⏱️  Execution Time: {pattern.performance_metrics.get('execution_time_seconds', 'N/A')}s")
                print(f"      💾 Memory: {pattern.performance_metrics.get('memory_usage_mb', 'N/A')} MB")
                print(f"      🔧 Workers: {pattern.pattern_data.get('parallel_workers', 'N/A')}")
        else:
            print("🔍 No similar patterns found. Try storing some patterns first!")
    
    async def generate_learning_insights(self):
        """Interactive learning insights generation."""
        print("\n💡 Generate Learning Insights")
        print("-" * 30)
        
        if not IMPORTS_AVAILABLE:
            print("📝 Simulating insight generation...")
            self.session_data["insights_generated"] += 1
            print("✅ Generated optimization insights (simulated)")
            return
        
        # Get execution ID to analyze
        execution_id = input("Execution ID to analyze (or press Enter for latest): ").strip()
        
        if not execution_id:
            # Use a sample execution
            execution_id = "sample_analysis"
            performance_metrics = {
                "execution_time_seconds": 45.2,
                "memory_usage_mb": 512,
                "cpu_utilization": 0.75,
                "parallelization_efficiency": 1.2,  # Low efficiency
                "resource_utilization": 0.85       # High utilization
            }
        else:
            # Get performance metrics from user
            try:
                exec_time = float(input("Execution time in seconds: ") or "30.0")
                memory_mb = int(input("Memory usage in MB: ") or "512")
                cpu_util = float(input("CPU utilization (0.0-1.0): ") or "0.75")
                parallel_eff = float(input("Parallelization efficiency: ") or "1.5")
                resource_util = float(input("Resource utilization (0.0-1.0): ") or "0.65")
                
                performance_metrics = {
                    "execution_time_seconds": exec_time,
                    "memory_usage_mb": memory_mb,
                    "cpu_utilization": cpu_util,
                    "parallelization_efficiency": parallel_eff,
                    "resource_utilization": resource_util
                }
            except ValueError:
                print("⚠️  Using default performance metrics")
                performance_metrics = {
                    "execution_time_seconds": 30.0,
                    "memory_usage_mb": 512,
                    "cpu_utilization": 0.75,
                    "parallelization_efficiency": 1.5,
                    "resource_utilization": 0.65
                }
        
        # Generate insights
        insights = await self.dag_integration.learn_from_execution(
            execution_id, performance_metrics
        )
        
        if "optimization_suggestions" in insights and insights["optimization_suggestions"]:
            print(f"\n💡 Learning Insights for '{execution_id}':")
            print(f"   📊 Confidence Score: {insights['confidence_score']:.2f}")
            print(f"   🔧 Optimization Suggestions:")
            
            for suggestion in insights["optimization_suggestions"]:
                print(f"\n      🎯 {suggestion['type'].title()}:")
                print(f"         💬 {suggestion['suggestion']}")
                print(f"         📊 Confidence: {suggestion['confidence']:.1%}")
            
            self.session_data["insights_generated"] += 1
        else:
            print("💡 No specific optimization suggestions for this execution.")
            print("   The performance metrics look good!")
    
    def get_project_context(self):
        """Interactive project context retrieval."""
        print("\n🏗️  Get Project Context")
        print("-" * 30)
        
        if not IMPORTS_AVAILABLE:
            print("📝 Simulating context retrieval...")
            self.session_data["contexts_retrieved"] += 1
            print("✅ Project context retrieved (simulated)")
            return
        
        # Get project name
        project_name = input("Project name (or press Enter for current): ").strip()
        
        # Get project context
        context = self.observatory_integration.get_current_project_context(
            project_name=project_name if project_name else None
        )
        
        print(f"\n📂 Project Context:")
        print(f"   📋 Name: {context.project_name}")
        print(f"   🏷️  Type: {context.project_type.value}")
        print(f"   📊 Completion: {context.completion_percentage:.1f}%")
        print(f"   📝 Current Spec: {context.current_spec or 'None'}")
        print(f"   🎯 Active Tasks: {len(context.active_tasks)}")
        print(f"   🔄 Retrieval Status: {context.retrieval_status.value}")
        print(f"   🌿 Git Branch: {context.git_branch or 'Unknown'}")
        print(f"   🏠 Workspace: {context.workspace_path or 'Unknown'}")
        print(f"   🆔 Session ID: {context.session_id or 'None'}")
        
        if context.active_tasks:
            print(f"\n   📋 Active Tasks:")
            for task in context.active_tasks[:3]:
                print(f"      • {task}")
        
        if context.project_goals:
            print(f"\n   🎯 Project Goals:")
            for goal in context.project_goals[:3]:
                print(f"      • {goal}")
        
        self.session_data["contexts_retrieved"] += 1
    
    def create_session(self):
        """Interactive session creation."""
        print("\n👤 Create Session")
        print("-" * 30)
        
        if not IMPORTS_AVAILABLE:
            print("📝 Simulating session creation...")
            print("✅ Session created (simulated)")
            return
        
        # Get session details
        user_id = input("User ID (or press Enter for default): ").strip()
        if not user_id:
            user_id = f"user_{datetime.now().strftime('%H%M%S')}"
        
        print("Enter session goals (one per line, empty line to finish):")
        goals = []
        while True:
            goal = input("  Goal: ").strip()
            if not goal:
                break
            goals.append(goal)
        
        if not goals:
            goals = ["Explore AI Memory Palace", "Learn context management"]
        
        # Create session
        session = self.observatory_integration.create_session_context(
            user_id=user_id,
            session_goals=goals
        )
        
        print(f"\n✅ Session Created:")
        print(f"   🆔 Session ID: {session.session_id}")
        print(f"   👤 User ID: {session.user_id}")
        print(f"   🎯 Goals: {len(session.session_goals)}")
        print(f"   📂 Active Projects: {len(session.active_projects)}")
        print(f"   ⏰ Start Time: {session.start_time}")
        
        if session.session_goals:
            print(f"\n   🎯 Session Goals:")
            for goal in session.session_goals:
                print(f"      • {goal}")
    
    def view_statistics(self):
        """Display comprehensive statistics."""
        print("\n📊 AI Memory Palace Statistics")
        print("-" * 30)
        
        if not IMPORTS_AVAILABLE:
            print("📝 Session Statistics (simulated):")
            print(f"   📦 Patterns Stored: {self.session_data['patterns_stored']}")
            print(f"   🔍 Contexts Retrieved: {self.session_data['contexts_retrieved']}")
            print(f"   💡 Insights Generated: {self.session_data['insights_generated']}")
            return
        
        # DAG Integration Statistics
        dag_stats = self.dag_integration.get_learning_statistics()
        print("🔧 DAG Integration:")
        print(f"   📦 Total Patterns Stored: {dag_stats['total_patterns_stored']}")
        print(f"   💡 Total Insights Generated: {dag_stats['total_insights_generated']}")
        print(f"   📊 Current Patterns: {dag_stats['stored_patterns']}")
        print(f"   🧠 Learning Enabled: {dag_stats['learning_enabled']}")
        
        # Observatory Integration Statistics
        obs_stats = self.observatory_integration.get_statistics()
        print(f"\n🏗️  Observatory Integration:")
        print(f"   📞 Total Requests: {obs_stats['total_requests']}")
        print(f"   🎯 Cache Hit Rate: {obs_stats['cache_hit_rate']:.1f}%")
        print(f"   ✅ Success Rate: {obs_stats['success_rate']:.1f}%")
        print(f"   ❌ Error Rate: {obs_stats['error_rate']:.1f}%")
        print(f"   💾 Cache Size: {obs_stats['cache_size']}")
        print(f"   👥 Active Sessions: {obs_stats['active_sessions']}")
        
        # Session Statistics
        print(f"\n👤 Current Session:")
        print(f"   📦 Patterns Stored: {self.session_data['patterns_stored']}")
        print(f"   🔍 Contexts Retrieved: {self.session_data['contexts_retrieved']}")
        print(f"   💡 Insights Generated: {self.session_data['insights_generated']}")
    
    def check_health_status(self):
        """Display health status."""
        print("\n🏥 Health Status")
        print("-" * 30)
        
        if not IMPORTS_AVAILABLE:
            print("📝 Health Status (simulated):")
            print("   ✅ All systems operational")
            return
        
        # DAG Integration Health
        dag_health = self.dag_integration.get_health_status()
        print("🔧 DAG Integration:")
        print(f"   📊 Status: {dag_health.status.value}")
        print(f"   💯 Health Score: {dag_health.health_score:.2f}")
        print(f"   ⏱️  Uptime: {dag_health.uptime_seconds:.1f}s")
        if dag_health.issues:
            print(f"   ⚠️  Issues: {', '.join(dag_health.issues)}")
        
        # Observatory Integration Health
        obs_health = self.observatory_integration.get_health_status()
        print(f"\n🏗️  Observatory Integration:")
        print(f"   📊 Status: {obs_health.status.value}")
        print(f"   💯 Health Score: {obs_health.health_score:.2f}")
        print(f"   ⏱️  Uptime: {obs_health.uptime_seconds:.1f}s")
        if obs_health.issues:
            print(f"   ⚠️  Issues: {', '.join(obs_health.issues)}")
    
    def test_graceful_degradation(self):
        """Test graceful degradation."""
        print("\n🛡️  Test Graceful Degradation")
        print("-" * 30)
        
        if not IMPORTS_AVAILABLE:
            print("📝 Graceful degradation test (simulated):")
            print("   ✅ Systems degraded gracefully")
            return
        
        print("🔄 Testing graceful degradation...")
        
        # Test DAG integration degradation
        dag_result = self.dag_integration.graceful_degradation()
        print(f"\n🔧 DAG Integration:")
        print(f"   ✅ Success: {dag_result.success}")
        print(f"   📉 Degraded: {[cap.value for cap in dag_result.degraded_capabilities]}")
        print(f"   📊 Remaining: {[cap.value for cap in dag_result.remaining_capabilities]}")
        
        # Test observatory integration degradation
        obs_result = self.observatory_integration.graceful_degradation()
        print(f"\n🏗️  Observatory Integration:")
        print(f"   ✅ Success: {obs_result.success}")
        print(f"   📉 Degraded: {[cap.value for cap in obs_result.degraded_capabilities]}")
        print(f"   📊 Remaining: {[cap.value for cap in obs_result.remaining_capabilities]}")
        
        print(f"\n🧪 Systems are now operating in degraded mode.")
        print(f"   Core functionality remains available with reduced features.")
    
    def show_help(self):
        """Display help information."""
        print("\n📖 AI Memory Palace Help")
        print("-" * 30)
        
        print("🧠 What is the AI Memory Palace?")
        print("   The AI Memory Palace eliminates the '50 first dates' problem")
        print("   by maintaining persistent context across AI assistant sessions.")
        
        print("\n🎯 Key Features:")
        print("   • Execution pattern storage and learning")
        print("   • Project context management")
        print("   • Session continuity")
        print("   • Performance optimization suggestions")
        print("   • Graceful error handling")
        
        print("\n🚀 Getting Started:")
        print("   1. Store some execution patterns (option 1)")
        print("   2. Retrieve project context (option 4)")
        print("   3. Generate learning insights (option 3)")
        print("   4. View statistics to see your progress (option 6)")
        
        print("\n💡 Tips:")
        print("   • Try different task types: data_processing, ml_training, web_scraping")
        print("   • Experiment with different worker counts and data sizes")
        print("   • Create sessions to track your goals")
        print("   • Check health status regularly")
        
        print("\n🔗 More Information:")
        print("   • Read examples/demos/AI_MEMORY_PALACE_README.md")
        print("   • Run examples/demos/ai_memory_palace_demo.py for full demo")
        print("   • Check the Beast Mode Framework documentation")
    
    async def run_interactive_demo(self):
        """Run the interactive demo."""
        self.display_banner()
        
        while True:
            self.display_menu()
            
            try:
                choice = input("Enter your choice (0-9): ").strip()
                
                if choice == "0":
                    print("\n👋 Thanks for exploring the AI Memory Palace!")
                    print("🧠 Remember: Your AI assistant should remember yesterday's conversation.")
                    break
                elif choice == "1":
                    await self.store_execution_pattern()
                elif choice == "2":
                    await self.find_similar_patterns()
                elif choice == "3":
                    await self.generate_learning_insights()
                elif choice == "4":
                    self.get_project_context()
                elif choice == "5":
                    self.create_session()
                elif choice == "6":
                    self.view_statistics()
                elif choice == "7":
                    self.check_health_status()
                elif choice == "8":
                    self.test_graceful_degradation()
                elif choice == "9":
                    self.show_help()
                else:
                    print("❌ Invalid choice. Please enter a number from 0-9.")
                
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Demo interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                input("Press Enter to continue...")


def main():
    """Main entry point."""
    demo = InteractiveDemo()
    asyncio.run(demo.run_interactive_demo())


if __name__ == "__main__":
    main()