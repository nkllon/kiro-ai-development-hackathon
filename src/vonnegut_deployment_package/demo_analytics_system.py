#!/usr/bin/env python3
"""
Demo script for DAG Orchestration Analytics System

This script demonstrates the comprehensive analytics and optimization
capabilities of the DAG orchestration system.
"""

import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dag_orchestration.analytics import (
    AnalyticsOrchestrator,
    ExecutionMetrics,
    DAGNode
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_sample_execution_data(num_tasks: int = 50) -> list[ExecutionMetrics]:
    """Generate sample execution data for demonstration."""
    logger.info(f"Generating {num_tasks} sample execution metrics")
    
    metrics = []
    now = datetime.now()
    
    # Simulate different execution patterns
    providers = ["openai", "anthropic", "local", "cursor"]
    
    for i in range(num_tasks):
        # Simulate some performance degradation over time
        base_time = 10.0
        time_degradation = i * 0.2  # Gradual slowdown
        execution_time = base_time + time_degradation + (i % 5) * 2  # Some variation
        
        # Simulate resource usage patterns
        cpu_usage = min(0.9, 0.3 + (i * 0.01) + (i % 3) * 0.1)
        memory_usage = min(0.8, 0.2 + (i * 0.008) + (i % 4) * 0.1)
        
        # Simulate cost patterns
        provider = providers[i % len(providers)]
        base_cost = {"openai": 0.05, "anthropic": 0.07, "local": 0.001, "cursor": 0.03}[provider]
        cost = base_cost * (1 + execution_time / 10.0)  # Cost scales with time
        
        # Simulate some failures
        success = not (i > 40 and i % 7 == 0)  # Some failures near the end
        
        metric = ExecutionMetrics(
            task_id=f"task_{i:03d}",
            execution_time=execution_time,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            cost=cost,
            success=success,
            timestamp=now - timedelta(minutes=num_tasks*2 - i*2),  # Spread over time
            dependencies=[f"task_{i-1:03d}"] if i > 0 and i % 5 != 0 else [],
            parallel_group=f"group_{i // 10}" if i % 10 < 8 else None,
            llm_provider=provider,
            error_type="timeout" if not success else None
        )
        metrics.append(metric)
    
    logger.info(f"Generated {len(metrics)} execution metrics")
    return metrics


def create_sample_dag_structure(num_nodes: int = 20) -> dict[str, DAGNode]:
    """Create sample DAG structure for demonstration."""
    logger.info(f"Creating sample DAG structure with {num_nodes} nodes")
    
    dag_structure = {}
    
    for i in range(num_nodes):
        # Create dependencies (each task depends on 1-2 previous tasks)
        dependencies = set()
        if i > 0:
            dependencies.add(f"task_{i-1:03d}")
        if i > 2 and i % 3 == 0:
            dependencies.add(f"task_{i-2:03d}")
        
        # Create dependents (tasks that depend on this one)
        dependents = set()
        if i < num_nodes - 1:
            dependents.add(f"task_{i+1:03d}")
        if i < num_nodes - 3 and (i + 1) % 3 == 0:
            dependents.add(f"task_{i+2:03d}")
        
        node = DAGNode(
            task_id=f"task_{i:03d}",
            dependencies=dependencies,
            dependents=dependents,
            execution_time=10.0 + i * 0.5,
            resource_requirements={
                "cpu": 0.3 + (i % 5) * 0.1,
                "memory": 0.2 + (i % 4) * 0.1
            },
            parallel_group=f"group_{i // 10}" if i % 10 < 8 else None
        )
        
        dag_structure[f"task_{i:03d}"] = node
    
    logger.info(f"Created DAG structure with {len(dag_structure)} nodes")
    return dag_structure


def simulate_resource_monitoring(orchestrator: AnalyticsOrchestrator, num_snapshots: int = 10):
    """Simulate resource monitoring over time."""
    logger.info(f"Simulating {num_snapshots} resource snapshots")
    
    try:
        for i in range(num_snapshots):
            # Simulate varying workload
            active_tasks = 3 + (i % 5)
            concurrent_executions = 2 + (i % 3)
            
            snapshot = orchestrator.capture_resource_snapshot(
                active_tasks=active_tasks,
                concurrent_executions=concurrent_executions
            )
            
            logger.debug(f"Captured snapshot {i+1}: CPU={snapshot.cpu_percent:.1f}%, "
                        f"Memory={snapshot.memory_percent:.1f}%")
    
    except Exception as e:
        logger.warning(f"Resource monitoring simulation failed: {e}")
        logger.info("Continuing without resource snapshots...")


def demonstrate_analytics_system():
    """Demonstrate the complete analytics system."""
    logger.info("Starting DAG Orchestration Analytics System Demo")
    
    # Initialize analytics orchestrator
    logger.info("Initializing Analytics Orchestrator")
    orchestrator = AnalyticsOrchestrator(
        analysis_interval_minutes=30,
        budget_limit=100.0  # $100 budget limit
    )
    
    # Generate and add execution data
    logger.info("Adding execution metrics")
    execution_metrics = generate_sample_execution_data(num_tasks=50)
    orchestrator.add_execution_metrics(execution_metrics)
    
    # Create and update DAG structure
    logger.info("Updating DAG structure")
    dag_structure = create_sample_dag_structure(num_nodes=20)
    orchestrator.update_dag_structure(dag_structure)
    
    # Simulate resource monitoring
    logger.info("Simulating resource monitoring")
    simulate_resource_monitoring(orchestrator, num_snapshots=10)
    
    # Run comprehensive analysis
    logger.info("Running comprehensive analysis")
    report = orchestrator.run_comprehensive_analysis(analysis_period_days=1)
    
    # Display results
    logger.info("=" * 60)
    logger.info("ANALYTICS RESULTS SUMMARY")
    logger.info("=" * 60)
    
    logger.info(f"Overall Health Score: {report.overall_health_score:.1f}/100")
    logger.info(f"Analysis Period: {report.analysis_period_days} days")
    logger.info(f"Generated At: {report.generated_at}")
    
    # Execution insights
    logger.info(f"\nExecution Insights: {len(report.execution_insights)}")
    for insight in report.execution_insights[:3]:  # Show top 3
        logger.info(f"  - {insight.pattern_type.value}: {insight.description}")
        logger.info(f"    Impact Score: {insight.impact_score:.1f}, Confidence: {insight.confidence:.1%}")
    
    # Performance regressions
    if report.performance_regressions:
        logger.info(f"\nPerformance Regressions: {len(report.performance_regressions)}")
        for regression in report.performance_regressions[:2]:  # Show top 2
            logger.info(f"  - {regression.regression_type.value}: {regression.description}")
            logger.info(f"    Severity: {regression.severity.value}, Degradation: {regression.degradation_percent:.1f}%")
    
    # Cost optimization opportunities
    if report.cost_optimization_opportunities:
        logger.info(f"\nCost Optimization Opportunities: {len(report.cost_optimization_opportunities)}")
        total_savings = sum(opp.potential_savings for opp in report.cost_optimization_opportunities)
        logger.info(f"  Total Potential Savings: ${total_savings:.2f}")
        
        for opp in report.cost_optimization_opportunities[:3]:  # Show top 3
            logger.info(f"  - {opp.strategy.value}: {opp.description}")
            logger.info(f"    Savings: ${opp.potential_savings:.2f} ({opp.savings_percentage:.1f}%)")
    
    # Resource trends
    if report.resource_trends:
        logger.info(f"\nResource Trends: {len(report.resource_trends)}")
        for trend in report.resource_trends:
            logger.info(f"  - {trend.resource_type.value}: {trend.trend_direction} "
                       f"(strength: {trend.trend_strength:.2f})")
            logger.info(f"    Current Level: {trend.current_level.value}")
    
    # Priority recommendations
    logger.info(f"\nPriority Recommendations: {len(report.priority_recommendations)}")
    for rec in report.priority_recommendations[:5]:  # Show top 5
        logger.info(f"  - [{rec['priority']}] {rec['title']}")
        logger.info(f"    Category: {rec['category']}")
        logger.info(f"    Description: {rec['description']}")
    
    # Continuous improvement plan
    logger.info(f"\nContinuous Improvement Plan: {len(report.continuous_improvement_plan)}")
    for action in report.continuous_improvement_plan[:3]:  # Show top 3
        logger.info(f"  - [{action['priority']}] {action['title']}")
        logger.info(f"    Timeline: {action['timeline']}")
    
    # Predictive alerts
    if report.predictive_alerts:
        logger.info(f"\nPredictive Alerts: {len(report.predictive_alerts)}")
        for alert in report.predictive_alerts[:2]:  # Show top 2
            logger.info(f"  - {alert.alert_type}: {alert.description}")
            logger.info(f"    Severity: {alert.severity.value}, Confidence: {alert.confidence:.1%}")
            logger.info(f"    Predicted: {alert.predicted_occurrence_time}")
    
    # Real-time insights
    logger.info("\nReal-time Insights:")
    insights = orchestrator.get_real_time_insights()
    
    if insights['cost_alerts']:
        logger.info(f"  Active Cost Alerts: {len(insights['cost_alerts'])}")
        for alert in insights['cost_alerts'][:2]:
            logger.info(f"    - {alert.alert_type}: {alert.description}")
    
    if insights['system_recommendations']:
        logger.info(f"  Immediate Recommendations: {len(insights['system_recommendations'])}")
        for rec in insights['system_recommendations'][:2]:
            logger.info(f"    - [{rec['priority']}] {rec['title']}")
    
    # Export comprehensive report
    output_dir = Path("analytics_reports")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = output_dir / f"analytics_report_{timestamp}.json"
    
    logger.info(f"\nExporting comprehensive report to: {report_path}")
    orchestrator.export_comprehensive_report(report, report_path)
    
    # Analytics summary
    logger.info("\nAnalytics System Summary:")
    summary = orchestrator.get_analytics_summary()
    logger.info(f"  Status: {summary['analytics_status']}")
    logger.info(f"  Reports Generated: {summary['reports_generated']}")
    logger.info(f"  Analysis Interval: {summary['analysis_interval_minutes']} minutes")
    
    if 'latest_analysis' in summary:
        latest = summary['latest_analysis']
        logger.info(f"  Latest Analysis:")
        logger.info(f"    Health Score: {latest['overall_health_score']:.1f}")
        logger.info(f"    Recommendations: {latest['priority_recommendations']}")
        logger.info(f"    Regressions: {latest['performance_regressions']}")
        logger.info(f"    Cost Opportunities: {latest['cost_opportunities']}")
    
    logger.info("=" * 60)
    logger.info("DEMO COMPLETED SUCCESSFULLY")
    logger.info("=" * 60)
    
    return report


if __name__ == "__main__":
    try:
        report = demonstrate_analytics_system()
        
        print(f"\n🎉 Analytics demo completed successfully!")
        print(f"📊 Overall Health Score: {report.overall_health_score:.1f}/100")
        print(f"💡 Priority Recommendations: {len(report.priority_recommendations)}")
        print(f"💰 Cost Optimization Opportunities: {len(report.cost_optimization_opportunities)}")
        print(f"📈 Performance Insights: {len(report.execution_insights)}")
        print(f"🔮 Predictive Alerts: {len(report.predictive_alerts)}")
        
        if report.cost_optimization_opportunities:
            total_savings = sum(opp.potential_savings for opp in report.cost_optimization_opportunities)
            print(f"💵 Total Potential Savings: ${total_savings:.2f}")
        
        print(f"\n📄 Detailed report exported to: analytics_reports/")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        sys.exit(1)