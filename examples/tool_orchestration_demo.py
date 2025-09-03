#!/usr/bin/env python3
"""
Beast Mode Framework - Tool Orchestration Demo
Demonstrates UC-12, UC-13, UC-14, UC-15 implementation

This example shows how to use the Tool Orchestrator for:
- Intelligent tool selection with decision framework
- Systematic tool execution with constraint compliance
- Tool health monitoring with systematic diagnostics
- Tool performance optimization with systematic approach
"""

import time
import uuid
from datetime import datetime
from pathlib import Path

from src.beast_mode.orchestration.tool_orchestrator import (
    ToolOrchestrator, ToolDefinition, ToolExecutionRequest,
    ToolType, ExecutionStrategy
)

def main():
    """Demonstrate tool orchestration capabilities"""
    print("🔧 Beast Mode Framework - Tool Orchestration Demo")
    print("=" * 60)
    
    # Initialize orchestrator
    orchestrator = ToolOrchestrator()
    print(f"✅ Tool Orchestrator initialized")
    print(f"   Status: {orchestrator.get_module_status()['status']}")
    print()
    
    # Demo 1: Register custom tools
    print("📋 Demo 1: Tool Registration")
    print("-" * 30)
    
    # Register a custom build tool
    custom_build_tool = ToolDefinition(
        tool_id="custom_build",
        name="Custom Build System",
        tool_type=ToolType.BUILD_TOOL,
        command_template="echo 'Building {project} with {config} configuration'",
        systematic_constraints={
            "no_ad_hoc_commands": True,
            "systematic_error_handling": True,
            "requires_project_file": True
        },
        performance_profile={
            "typical_execution_time_ms": 3000,
            "memory_usage_mb": 150,
            "cpu_utilization": 0.4
        },
        health_check_command="echo 'Custom build system ready'",
        timeout_seconds=120
    )
    
    registration_result = orchestrator.register_tool(custom_build_tool)
    print(f"   ✅ Registered: {custom_build_tool.name}")
    print(f"   Tool ID: {registration_result['tool_id']}")
    print(f"   Systematic Constraints Validated: {registration_result['systematic_constraints_validated']}")
    print()
    
    # Register a test tool
    test_tool = ToolDefinition(
        tool_id="advanced_test",
        name="Advanced Test Runner",
        tool_type=ToolType.TEST_TOOL,
        command_template="echo 'Running {test_suite} tests with {coverage} coverage'",
        systematic_constraints={
            "no_ad_hoc_commands": True,
            "systematic_error_handling": True,
            "coverage_reporting": True
        },
        performance_profile={
            "typical_execution_time_ms": 8000,
            "memory_usage_mb": 300,
            "cpu_utilization": 0.6
        },
        health_check_command="echo 'Test runner operational'",
        timeout_seconds=300
    )
    
    orchestrator.register_tool(test_tool)
    print(f"   ✅ Registered: {test_tool.name}")
    print()
    
    # Demo 2: Intelligent Tool Selection (UC-12)
    print("🧠 Demo 2: Intelligent Tool Selection (UC-12)")
    print("-" * 45)
    
    # Test different selection scenarios
    scenarios = [
        {
            "name": "Build Task - Systematic Only",
            "context": {
                "task_type": "build",
                "tool_types": ["build_tool"],
                "systematic_only": True,
                "priority": "high"
            },
            "strategy": ExecutionStrategy.SYSTEMATIC_ONLY
        },
        {
            "name": "Test Task - Performance Optimized", 
            "context": {
                "task_type": "test",
                "tool_types": ["test_tool"],
                "performance": {"priority": "speed"},
                "priority": "normal"
            },
            "strategy": ExecutionStrategy.PERFORMANCE_OPTIMIZED
        },
        {
            "name": "Multi-Tool Task - Reliability First",
            "context": {
                "task_type": "ci_pipeline",
                "tool_types": ["build_tool", "test_tool"],
                "reliability_required": True
            },
            "strategy": ExecutionStrategy.RELIABILITY_FIRST
        }
    ]
    
    for scenario in scenarios:
        print(f"   Scenario: {scenario['name']}")
        
        selection_result = orchestrator.intelligent_tool_selection(
            scenario["context"], scenario["strategy"]
        )
        
        if "selected_tool_id" in selection_result:
            print(f"   ✅ Selected Tool: {selection_result['tool_name']}")
            print(f"      Tool ID: {selection_result['selected_tool_id']}")
            print(f"      Confidence: {selection_result['decision_confidence']:.2f}")
            print(f"      Systematic Compliance: {selection_result['systematic_compliance']}")
            print(f"      Rationale: {selection_result['decision_rationale']}")
            if selection_result['alternative_tools']:
                print(f"      Alternatives: {', '.join(selection_result['alternative_tools'])}")
        else:
            print(f"   ❌ Selection Failed: {selection_result.get('error', 'Unknown error')}")
            
        print()
    
    # Demo 3: Systematic Tool Execution (UC-13)
    print("⚙️  Demo 3: Systematic Tool Execution (UC-13)")
    print("-" * 45)
    
    # Execute build task
    build_request = ToolExecutionRequest(
        request_id=str(uuid.uuid4()),
        tool_id="custom_build",
        parameters={
            "project": "beast-mode-framework",
            "config": "production"
        },
        execution_strategy=ExecutionStrategy.SYSTEMATIC_ONLY,
        context={
            "task_type": "build",
            "environment": "ci"
        },
        priority="high"
    )
    
    print(f"   Executing Build Task...")
    print(f"   Request ID: {build_request.request_id}")
    print(f"   Tool: {build_request.tool_id}")
    print(f"   Strategy: {build_request.execution_strategy.value}")
    
    build_result = orchestrator.execute_tool_systematically(build_request)
    
    print(f"   ✅ Execution Result:")
    print(f"      Status: {build_result.status}")
    print(f"      Output: {build_result.output}")
    print(f"      Execution Time: {build_result.execution_time_ms}ms")
    print(f"      Systematic Compliance: {build_result.systematic_compliance}")
    print(f"      Exit Code: {build_result.exit_code}")
    
    if build_result.recommendations:
        print(f"      Recommendations:")
        for rec in build_result.recommendations:
            print(f"        - {rec}")
    print()
    
    # Execute test task
    test_request = ToolExecutionRequest(
        request_id=str(uuid.uuid4()),
        tool_id="advanced_test",
        parameters={
            "test_suite": "integration",
            "coverage": "90%"
        },
        execution_strategy=ExecutionStrategy.PERFORMANCE_OPTIMIZED,
        context={"task_type": "test"}
    )
    
    print(f"   Executing Test Task...")
    test_result = orchestrator.execute_tool_systematically(test_request)
    
    print(f"   ✅ Test Execution:")
    print(f"      Status: {test_result.status}")
    print(f"      Output: {test_result.output}")
    print(f"      Execution Time: {test_result.execution_time_ms}ms")
    print()
    
    # Demo 4: Tool Health Monitoring (UC-14)
    print("🏥 Demo 4: Tool Health Monitoring (UC-14)")
    print("-" * 42)
    
    # Monitor individual tool health
    print("   Individual Tool Health Checks:")
    for tool_id in ["custom_build", "advanced_test"]:
        health_result = orchestrator.monitor_tool_health(tool_id)
        
        print(f"   Tool: {tool_id}")
        print(f"      Status: {health_result['health_status']['status']}")
        print(f"      Systematic Compliance: {health_result['systematic_compliance']}")
        
        metrics = health_result['health_metrics']
        print(f"      Success Rate: {metrics['success_rate']:.2f}")
        print(f"      Avg Execution Time: {metrics['average_execution_time_ms']:.0f}ms")
        print(f"      Availability: {metrics['availability_percentage']:.1f}%")
        print(f"      Performance Trend: {metrics['performance_trend']}")
        
        if health_result['recommendations']:
            print(f"      Recommendations:")
            for rec in health_result['recommendations']:
                print(f"        - {rec}")
        print()
    
    # Overall health monitoring
    print("   Overall Health Monitoring:")
    overall_health = orchestrator.monitor_tool_health()
    
    print(f"   Health Summary:")
    health_summary = overall_health['health_summary']
    print(f"      Total Tools: {health_summary['total_tools']}")
    print(f"      Health Score: {health_summary['overall_health_score']:.2f}")
    print(f"      Health Status: {health_summary['health_status']}")
    
    compliance_overview = overall_health['systematic_compliance_overview']
    print(f"   Systematic Compliance:")
    print(f"      Overall Rate: {compliance_overview['overall_compliance_rate']:.2f}")
    print(f"      Compliant Tools: {compliance_overview['compliant_tools']}/{compliance_overview['total_tools']}")
    
    print(f"   Monitoring Recommendations:")
    for rec in overall_health['monitoring_recommendations']:
        print(f"      - {rec}")
    print()
    
    # Demo 5: Tool Performance Optimization (UC-15)
    print("🚀 Demo 5: Tool Performance Optimization (UC-15)")
    print("-" * 50)
    
    # Simulate some performance issues for demonstration
    print("   Simulating performance optimization scenario...")
    
    # Modify tool metrics to show optimization opportunities
    custom_build_metrics = orchestrator.tool_metrics["custom_build"]
    custom_build_metrics.average_execution_time_ms = 12000  # Slow
    custom_build_metrics.systematic_compliance_rate = 0.75  # Low compliance
    
    test_metrics = orchestrator.tool_metrics["advanced_test"]
    test_metrics.average_execution_time_ms = 15000  # Very slow
    test_metrics.performance_trend = "degrading"
    
    optimization_context = {
        "target_performance_improvement": 25,  # 25% improvement target
        "maintain_systematic_compliance": True,
        "focus_areas": ["execution_time", "compliance"],
        "optimization_budget": "medium"
    }
    
    print(f"   Running Performance Optimization...")
    optimization_result = orchestrator.optimize_tool_performance(optimization_context)
    
    print(f"   ✅ Optimization Results:")
    print(f"      Optimizations Applied: {optimization_result['optimization_applied']}")
    print(f"      Systematic Compliance Maintained: {optimization_result['systematic_compliance_maintained']}")
    
    improvements = optimization_result['performance_improvements']
    print(f"      Performance Improvements:")
    print(f"        - Performance: {improvements['performance']:.1f}%")
    print(f"        - Compliance: {improvements['compliance']:.1f}%")
    
    bottleneck_analysis = optimization_result['bottleneck_analysis']
    print(f"      Bottleneck Analysis:")
    print(f"        - Primary Bottlenecks: {len(bottleneck_analysis.get('bottlenecks', []))}")
    print(f"        - Systematic Issues: {bottleneck_analysis.get('systematic_issues', 0)}")
    
    print(f"      Optimization Recommendations:")
    for rec in optimization_result['optimization_recommendations']:
        print(f"        - {rec}")
    
    next_cycle = optimization_result['next_optimization_cycle']
    print(f"      Next Optimization: {next_cycle['next_optimization_time']}")
    print()
    
    # Demo 6: Orchestration Analytics
    print("📊 Demo 6: Orchestration Analytics")
    print("-" * 35)
    
    analytics = orchestrator.get_orchestration_analytics()
    
    # Execution Analytics
    exec_analytics = analytics['execution_analytics']
    print(f"   Execution Analytics:")
    print(f"      Total Executions: {exec_analytics['total_executions']}")
    print(f"      Success Rate: {exec_analytics['success_rate']:.2f}")
    print(f"      Avg Execution Time: {exec_analytics['average_execution_time']:.0f}ms")
    print(f"      Systematic Compliance Rate: {exec_analytics['systematic_compliance_rate']:.2f}")
    
    # Decision Framework Effectiveness
    decision_analytics = analytics['decision_framework_effectiveness']
    print(f"   Decision Framework:")
    print(f"      Avg Decision Time: {decision_analytics['average_decision_time']:.0f}ms")
    print(f"      Decision Accuracy: {decision_analytics['decision_accuracy']:.2f}")
    
    # Tool Usage Patterns
    usage_patterns = analytics['tool_usage_patterns']
    print(f"   Tool Usage Patterns:")
    most_used = usage_patterns['most_used_tools']
    if most_used:
        print(f"      Most Used Tool: {most_used[0]['tool_name']} ({most_used[0]['usage_count']} uses)")
    
    performance_ranking = usage_patterns['tool_performance_ranking']
    if performance_ranking:
        print(f"      Best Performing: {performance_ranking[0]['tool_name']} (score: {performance_ranking[0]['performance_score']:.2f})")
    
    # Health Monitoring Insights
    health_insights = analytics['health_monitoring_insights']
    print(f"   Health Monitoring Insights:")
    maintenance_recs = health_insights['preventive_maintenance_recommendations']
    print(f"      Maintenance Recommendations: {len(maintenance_recs)}")
    for rec in maintenance_recs[:3]:  # Show first 3
        print(f"        - {rec}")
    
    print()
    
    # Final Status
    print("🎯 Final Orchestrator Status")
    print("-" * 30)
    
    final_status = orchestrator.get_module_status()
    print(f"   Module Status: {final_status['status']}")
    print(f"   Registered Tools: {final_status['registered_tools']}")
    print(f"   Total Executions: {final_status['total_executions']}")
    print(f"   Success Rate: {final_status['success_rate']:.2f}")
    print(f"   Systematic Compliance: {final_status['systematic_compliance_rate']:.2f}")
    print(f"   Health Monitoring: {'Active' if final_status['health_monitoring_active'] else 'Inactive'}")
    
    print()
    print("✅ Tool Orchestration Demo Complete!")
    print("   All UC-12, UC-13, UC-14, UC-15 capabilities demonstrated")

if __name__ == "__main__":
    main()