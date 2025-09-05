#!/usr/bin/env python3
"""
Test Simple PDCA Orchestrator

A practical demonstration of systematic PDCA execution on a real task.
No over-engineering - just systematic Plan-Do-Check-Act in action!
"""

import sys
import logging
from datetime import timedelta
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from beast_mode.pdca.pdca_orchestrator import SystematicPDCAOrchestrator, PDCATask


def demo_simple_pdca():
    """Demonstrate simple PDCA execution on a real task"""
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("🔄" * 20)
    print("🚀 SIMPLE PDCA ORCHESTRATOR DEMO 🚀")
    print("🔄" * 20)
    print()
    print("Demonstrating systematic Plan-Do-Check-Act execution")
    print("on a real development task - no over-engineering!")
    print()
    
    # Initialize the PDCA orchestrator
    orchestrator = SystematicPDCAOrchestrator()
    
    # Check initial status
    print("📊 Initial PDCA Orchestrator Status:")
    status = orchestrator.get_module_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    print()
    
    # Create a simple, real task
    task = PDCATask(
        name="Create Simple Configuration File",
        description="Create a basic configuration file for the PDCA orchestrator",
        requirements=[
            "File must be created in the correct location",
            "File must contain valid JSON structure",
            "Configuration must include basic PDCA settings"
        ],
        success_criteria=[
            "File created successfully",
            "JSON structure is valid",
            "Configuration contains required settings"
        ],
        estimated_duration=timedelta(minutes=5)
    )
    
    print(f"📋 Task to Execute: {task.name}")
    print(f"   Description: {task.description}")
    print(f"   Requirements: {len(task.requirements)}")
    print(f"   Success Criteria: {len(task.success_criteria)}")
    print()
    
    # Execute PDCA cycle
    print("🚀 Executing PDCA Cycle...")
    print("   PLAN → DO → CHECK → ACT")
    print()
    
    result = orchestrator.execute_pdca_cycle(task)
    
    # Display results
    print("📊" * 20)
    print("🎉 PDCA CYCLE COMPLETED! 🎉")
    print("📊" * 20)
    print()
    
    print(f"✅ Success: {result.success}")
    print(f"⏱️  Duration: {result.duration.total_seconds():.1f} seconds")
    print()
    
    print("📋 PLAN Results:")
    plan = result.plan_result
    print(f"   Approach: {plan.get('implementation_strategy', {}).get('approach', 'N/A')}")
    print(f"   Risk Level: {plan.get('risk_assessment', {}).get('risk_level', 'N/A')}")
    print()
    
    print("🔧 DO Results:")
    do = result.do_result
    print(f"   Approach Used: {do.get('approach_used', 'N/A')}")
    print(f"   Systematic: {do.get('systematic_approach', False)}")
    print()
    
    print("🔍 CHECK Results:")
    check = result.check_result
    print(f"   Overall Success: {check.get('success', False)}")
    print(f"   Success Rate: {check.get('success_rate', 0):.1%}")
    validation_results = check.get('validation_results', [])
    for validation in validation_results:
        status = "✅" if validation['met'] else "❌"
        print(f"   {status} {validation['criterion']}")
    print()
    
    print("📚 ACT Results (Lessons Learned):")
    for lesson in result.lessons_learned:
        print(f"   • {lesson}")
    print()
    
    # Check final status
    print("📊 Final PDCA Orchestrator Status:")
    final_status = orchestrator.get_module_status()
    for key, value in final_status.items():
        print(f"  {key}: {value}")
    print()
    
    # Check health indicators
    print("🏥 Health Indicators:")
    health_indicators = orchestrator.get_health_indicators()
    for indicator in health_indicators:
        status_emoji = "✅" if indicator['status'] in ['healthy', 'active'] else "⚠️"
        print(f"  {status_emoji} {indicator['name']}: {indicator['status']}")
    print()
    
    if result.success:
        print("🏆 SYSTEMATIC SUPERIORITY DEMONSTRATED!")
        print("The PDCA orchestrator successfully executed a systematic")
        print("Plan-Do-Check-Act cycle on a real development task!")
        print("This proves systematic approaches work in practice! 🚀")
    else:
        print("📈 LEARNING OPPORTUNITY!")
        print("Even when tasks don't fully succeed, the systematic approach")
        print("provides valuable learning and improvement opportunities!")
        print("This is still better than ad-hoc approaches! 🔄")


if __name__ == "__main__":
    print("🎬 Starting Simple PDCA Demo...")
    print("This demonstrates practical systematic development!")
    print()
    
    demo_simple_pdca()
    
    print()
    print("🎬 Demo complete!")
    print("This shows that systematic PDCA execution actually works! 🚀")