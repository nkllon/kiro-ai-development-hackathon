#!/usr/bin/env python3
"""
Beast Mode Framework - Tool Orchestration Engine Demo
Demonstrates UC-03: Model-Driven Decision Making vs Guesswork

This example shows:
- Tool orchestration with comprehensive health monitoring
- Confidence-based decision framework (80%+ Model, 50-80% Multi-Perspective, <50% Full Analysis)
- Tool hierarchy and systematic repair system
- Decision documentation for manual analysis fallback
- Integration with RCA engine for systematic tool problem resolution
"""

import time
from datetime import datetime
from pathlib import Path

# Import Tool Orchestration components
from src.beast_mode.orchestration.tool_orchestration_engine import (
    ToolOrchestrationEngine,
    DecisionContext,
    ToolDefinition,
    ToolPriority,
    DecisionConfidenceLevel
)

def main():
    """Demonstrate Tool Orchestration Engine capabilities"""
    print("🚀 Beast Mode Framework - Tool Orchestration Engine Demo")
    print("=" * 70)
    
    # Demo 1: Tool Registration and Health Monitoring
    print("\n🔧 Demo 1: Tool Registration and Health Monitoring")
    print("-" * 55)
    
    orchestration_engine = ToolOrchestrationEngine(".")
    print(f"✅ Tool Orchestration Engine initialized")
    print(f"   Status: {orchestration_engine.get_module_status()['status']}")
    
    # Register additional custom tools
    custom_tools = [
        ToolDefinition(
            tool_id="project_structure",
            name="Project Structure Analysis",
            description="Analyze project directory structure",
            command="find . -type f -name '*.py' | head -10",
            health_check_command="find --version",
            priority=ToolPriority.HIGH,
            timeout_seconds=30,
            repair_procedures=["which find", "find --help"]
        ),
        ToolDefinition(
            tool_id="code_quality_check",
            name="Code Quality Check",
            description="Basic code quality analysis",
            command="wc -l src/beast_mode/**/*.py",
            health_check_command="wc --version",
            priority=ToolPriority.MEDIUM,
            timeout_seconds=60,
            repair_procedures=["which wc", "wc --help"]
        ),
        ToolDefinition(
            tool_id="dependency_check",
            name="Dependency Check",
            description="Check project dependencies",
            command="pip freeze | grep -E '(pytest|mock)'",
            health_check_command="pip --version",
            priority=ToolPriority.CRITICAL,
            timeout_seconds=45,
            repair_procedures=["python -m pip --version", "which pip"]
        )
    ]
    
    print("\n   Registering Custom Tools:")
    for tool in custom_tools:
        result = orchestration_engine.register_tool(tool)
        if result.get("success"):
            print(f"      ✅ {result['name']} ({result['tool_id']})")
            print(f"         Priority: {result['priority']}")
            print(f"         Initial Health: {result['initial_health']}")
        else:
            print(f"      ❌ Failed to register {tool.name}: {result.get('error')}")
    
    # Show all registered tools
    all_tools = orchestration_engine.get_registered_tools()
    print(f"\n   📋 Total Registered Tools: {len(all_tools)}")
    
    for tool_id, tool_info in all_tools.items():
        health_icon = "🟢" if tool_info["health_status"] == "healthy" else "🔴" if tool_info["health_status"] == "failed" else "🟡"
        print(f"      {health_icon} {tool_info['name']} ({tool_info['priority']} priority)")
    
    # Demo 2: High Confidence Decision Making (80%+ Model Registry)
    print("\n🎯 Demo 2: High Confidence Decision Making (Model Registry)")
    print("-" * 62)
    
    high_confidence_context = DecisionContext(
        decision_id="HC-001",
        problem_statement="Need to analyze project structure for development planning",
        available_options=["project_structure", "git_status", "python_version"],
        constraints=["Must complete within 60 seconds", "Prefer file system analysis"],
        stakeholder_requirements={
            "accuracy": "high",
            "completeness": "medium",
            "speed": "high"
        },
        time_pressure="normal",
        risk_tolerance="medium",
        domain="development_tools"
    )
    
    print(f"   Decision Context: {high_confidence_context.problem_statement}")
    print(f"   Domain: {high_confidence_context.domain}")
    print(f"   Available Options: {', '.join(high_confidence_context.available_options)}")
    
    # Execute high confidence orchestration
    print("\n   Executing High Confidence Orchestration...")
    start_time = time.time()
    
    hc_result = orchestration_engine.orchestrate_tool_execution(
        high_confidence_context,
        preferred_tools=["project_structure", "git_status"]
    )
    
    execution_time = time.time() - start_time
    
    print(f"   ✅ Orchestration Complete (Time: {execution_time:.2f}s)")
    print(f"      Operation ID: {hc_result.operation_id}")
    print(f"      Success: {hc_result.success}")
    print(f"      Decision Confidence: {hc_result.decision_confidence.value}")
    print(f"      Decision Rationale: {hc_result.decision_rationale}")
    print(f"      Tools Attempted: {', '.join(hc_result.tools_attempted)}")
    
    if hc_result.primary_result:
        print(f"      Primary Result:")
        print(f"         Tool: {hc_result.primary_result.tool_id}")
        print(f"         Success: {hc_result.primary_result.success}")
        print(f"         Execution Time: {hc_result.primary_result.execution_time_ms}ms")
        if hc_result.primary_result.output:
            output_preview = hc_result.primary_result.output[:100] + "..." if len(hc_result.primary_result.output) > 100 else hc_result.primary_result.output
            print(f"         Output Preview: {output_preview}")
    
    if hc_result.recommendations:
        print(f"      Recommendations:")
        for rec in hc_result.recommendations:
            print(f"         💡 {rec}")
    
    # Demo 3: Medium Confidence Decision Making (Registry + Multi-Perspective)
    print("\n🤔 Demo 3: Medium Confidence Decision Making (Registry + Multi-Perspective)")
    print("-" * 78)
    
    medium_confidence_context = DecisionContext(
        decision_id="MC-002",
        problem_statement="Need to assess code quality for deployment readiness",
        available_options=["code_quality_check", "dependency_check", "git_status"],
        constraints=["Must be thorough", "Time sensitive"],
        stakeholder_requirements={
            "quality_assurance": "critical",
            "deployment_readiness": "high",
            "risk_mitigation": "high"
        },
        time_pressure="urgent",
        risk_tolerance="low",
        domain="quality_assurance",
        previous_decisions=[
            {"decision_id": "HC-001", "outcome": "successful", "tools_used": ["project_structure"]}
        ]
    )
    
    print(f"   Decision Context: {medium_confidence_context.problem_statement}")
    print(f"   Domain: {medium_confidence_context.domain}")
    print(f"   Time Pressure: {medium_confidence_context.time_pressure}")
    print(f"   Risk Tolerance: {medium_confidence_context.risk_tolerance}")
    
    # Execute medium confidence orchestration
    print("\n   Executing Medium Confidence Orchestration...")
    start_time = time.time()
    
    mc_result = orchestration_engine.orchestrate_tool_execution(
        medium_confidence_context,
        preferred_tools=["code_quality_check", "dependency_check"]
    )
    
    execution_time = time.time() - start_time
    
    print(f"   ✅ Orchestration Complete (Time: {execution_time:.2f}s)")
    print(f"      Operation ID: {mc_result.operation_id}")
    print(f"      Success: {mc_result.success}")
    print(f"      Decision Confidence: {mc_result.decision_confidence.value}")
    print(f"      Decision Method: Registry + Basic Multi-Perspective Analysis")
    
    if mc_result.primary_result:
        print(f"      Primary Tool Executed: {mc_result.primary_result.tool_id}")
        print(f"      Health Status: {mc_result.primary_result.health_status.value}")
    
    # Demo 4: Low Confidence Decision Making (Full Multi-Stakeholder Analysis)
    print("\n🔍 Demo 4: Low Confidence Decision Making (Full Multi-Stakeholder Analysis)")
    print("-" * 80)
    
    low_confidence_context = DecisionContext(
        decision_id="LC-003",
        problem_statement="Need to choose optimal tool for complex system integration task",
        available_options=["make_help", "git_status", "python_version", "pip_list"],
        constraints=["Unknown system state", "Multiple stakeholder requirements", "High complexity"],
        stakeholder_requirements={
            "beast_mode_perspective": "systematic_superiority",
            "gke_consumer_perspective": "integration_ease",
            "devops_perspective": "reliability",
            "development_perspective": "maintainability",
            "evaluator_perspective": "measurable_results"
        },
        time_pressure="flexible",
        risk_tolerance="very_low",
        domain="system_integration"
    )
    
    print(f"   Decision Context: {low_confidence_context.problem_statement}")
    print(f"   Domain: {low_confidence_context.domain}")
    print(f"   Stakeholder Requirements: {len(low_confidence_context.stakeholder_requirements)} perspectives")
    print(f"   Complexity: High (Unknown system state)")
    
    # Execute low confidence orchestration
    print("\n   Executing Low Confidence Orchestration...")
    print("   (Performing Full Multi-Stakeholder Analysis...)")
    start_time = time.time()
    
    lc_result = orchestration_engine.orchestrate_tool_execution(
        low_confidence_context
    )
    
    execution_time = time.time() - start_time
    
    print(f"   ✅ Orchestration Complete (Time: {execution_time:.2f}s)")
    print(f"      Operation ID: {lc_result.operation_id}")
    print(f"      Success: {lc_result.success}")
    print(f"      Decision Confidence: {lc_result.decision_confidence.value}")
    print(f"      Decision Method: Full Multi-Stakeholder Analysis")
    print(f"      Risk Reduction: Applied comprehensive stakeholder validation")
    
    # Demo 5: Tool Health Monitoring and Systematic Repair
    print("\n🔧 Demo 5: Tool Health Monitoring and Systematic Repair")
    print("-" * 58)
    
    print("   Current Tool Health Status:")
    
    # Force health refresh to get current status
    health_refresh = orchestration_engine.force_tool_health_refresh()
    print(f"      Refreshed {health_refresh['refreshed_tools']} tools")
    
    for tool_id, health_status in health_refresh["health_status"].items():
        health_icon = "🟢" if health_status == "healthy" else "🔴" if health_status == "failed" else "🟡"
        print(f"      {health_icon} {tool_id}: {health_status}")
    
    # Simulate tool failure and repair
    print("\n   Simulating Tool Failure and Systematic Repair:")
    
    # Create a tool that will fail
    failing_tool = ToolDefinition(
        tool_id="failing_tool",
        name="Intentionally Failing Tool",
        description="Tool designed to fail for repair demonstration",
        command="nonexistent_command_that_will_fail",
        health_check_command="nonexistent_command_that_will_fail",
        priority=ToolPriority.HIGH,
        repair_procedures=[
            "echo 'Attempting repair procedure 1'",
            "echo 'Attempting repair procedure 2'"
        ]
    )
    
    orchestration_engine.register_tool(failing_tool)
    print(f"      ✅ Registered failing tool for demonstration")
    
    # Create context that will use the failing tool
    repair_context = DecisionContext(
        decision_id="REPAIR-001",
        problem_statement="Test systematic repair capabilities",
        available_options=["failing_tool"],
        constraints=["Must demonstrate repair process"],
        stakeholder_requirements={"repair_validation": "required"},
        time_pressure="normal",
        risk_tolerance="medium",
        domain="tool_repair_testing"
    )
    
    # Execute orchestration that will trigger repair
    print("      Executing orchestration with failing tool...")
    repair_result = orchestration_engine.orchestrate_tool_execution(
        repair_context,
        preferred_tools=["failing_tool"]
    )
    
    print(f"      Repair Orchestration Result:")
    print(f"         Success: {repair_result.success}")
    print(f"         Tools Attempted: {', '.join(repair_result.tools_attempted)}")
    
    if repair_result.recommendations:
        print(f"         Repair Recommendations:")
        for rec in repair_result.recommendations:
            print(f"            🔧 {rec}")
    
    # Demo 6: Decision Analytics and Performance Metrics
    print("\n📊 Demo 6: Decision Analytics and Performance Metrics")
    print("-" * 56)
    
    # Get comprehensive analytics
    decision_analytics = orchestration_engine.get_decision_analytics()
    
    print(f"   Decision Analytics Summary:")
    print(f"      Total Decisions Made: {decision_analytics.get('total_decisions', 0)}")
    print(f"      Overall Success Rate: {decision_analytics.get('overall_success_rate', 0):.1%}")
    print(f"      Average Execution Time: {decision_analytics.get('average_execution_time_ms', 0):.0f}ms")
    print(f"      Tools Repaired: {decision_analytics.get('tools_repaired', 0)}")
    print(f"      Fallbacks Used: {decision_analytics.get('fallbacks_used', 0)}")
    
    # Confidence distribution
    confidence_dist = decision_analytics.get('confidence_distribution', {})
    print(f"\n   Decision Confidence Distribution:")
    for level, count in confidence_dist.items():
        percentage = (count / max(1, decision_analytics.get('total_decisions', 1))) * 100
        print(f"      {level.capitalize()}: {count} decisions ({percentage:.1f}%)")
    
    # Success rates by confidence level
    success_rates = decision_analytics.get('success_rates_by_confidence', {})
    print(f"\n   Success Rates by Confidence Level:")
    for level, rate in success_rates.items():
        print(f"      {level.capitalize()}: {rate:.1%}")
    
    # Module health indicators
    health_indicators = orchestration_engine.get_health_indicators()
    print(f"\n   System Health Indicators:")
    
    orch_status = health_indicators.get('orchestration_status', {})
    print(f"      Total Tools: {orch_status.get('total_tools', 0)}")
    print(f"      Healthy Tools: {orch_status.get('healthy_tools', 0)}")
    print(f"      Failed Tools: {orch_status.get('failed_tools', 0)}")
    print(f"      Success Rate: {orch_status.get('success_rate', 0):.1%}")
    
    decision_framework = health_indicators.get('decision_framework', {})
    print(f"\n   Decision Framework Health:")
    print(f"      Intelligence Engine: {'🟢 Healthy' if decision_framework.get('intelligence_engine_healthy') else '🔴 Unhealthy'}")
    print(f"      RCA Engine: {'🟢 Healthy' if decision_framework.get('rca_engine_healthy') else '🔴 Unhealthy'}")
    print(f"      Multi-Perspective Engine: {'🟢 Healthy' if decision_framework.get('multi_perspective_engine_healthy') else '🔴 Unhealthy'}")
    
    # Demo 7: Integration with Beast Mode Framework
    print("\n🔗 Demo 7: Integration with Beast Mode Framework")
    print("-" * 50)
    
    print("   Tool Orchestration Engine Integration Benefits:")
    print("      ✅ Model-driven decision making vs guesswork")
    print("      ✅ Confidence-based routing for optimal tool selection")
    print("      ✅ Systematic tool repair with RCA integration")
    print("      ✅ Comprehensive health monitoring and status reporting")
    print("      ✅ Multi-stakeholder perspective analysis for complex decisions")
    print("      ✅ Performance metrics and decision analytics")
    
    print("\n   UC-03 Implementation Highlights:")
    print("      • High Confidence (80%+): Uses Model Registry + Domain Intelligence")
    print("      • Medium Confidence (50-80%): Registry + Basic Multi-Perspective Check")
    print("      • Low Confidence (<50%): Full Multi-Stakeholder Analysis")
    print("      • Systematic tool repair with root cause analysis")
    print("      • Decision documentation for manual analysis fallback")
    
    # Final summary
    print("\n" + "=" * 70)
    print("🎉 Tool Orchestration Engine Demo Complete!")
    print("=" * 70)
    
    print("\nKey Capabilities Demonstrated:")
    print("• UC-03: Model-Driven Decision Making with confidence-based routing")
    print("• Tool orchestration with comprehensive health monitoring")
    print("• Systematic repair system with RCA integration")
    print("• Multi-stakeholder perspective analysis for risk reduction")
    print("• Performance metrics and decision analytics")
    
    print("\nDecision Framework Summary:")
    print("• Eliminates guesswork through systematic intelligence consultation")
    print("• Routes decisions based on confidence levels for optimal outcomes")
    print("• Provides fallback mechanisms and systematic repair capabilities")
    print("• Tracks decision patterns and success rates for continuous improvement")
    
    print("\nNext Steps:")
    print("• Integrate with project registry for domain-specific intelligence")
    print("• Expand tool library with domain-specific tools")
    print("• Configure multi-stakeholder perspectives for your organization")
    print("• Set up monitoring dashboards for operational visibility")
    print("• Train team on confidence-based decision framework")

if __name__ == "__main__":
    main()