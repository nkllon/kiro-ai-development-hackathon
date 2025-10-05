#!/usr/bin/env python3
"""
AI Memory Palace Analytics CLI.

Command-line interface for context analytics, optimization recommendations,
and performance monitoring.
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from beast_mode.ai_memory_palace.analytics import (
    ContextAnalyzer, ContextOptimizer, AnalyticsOptimizationCLI
)
from beast_mode.ai_memory_palace.context_registry import ContextRegistry
from beast_mode.ai_memory_palace.storage import ContextStorage


def create_analytics_system() -> tuple:
    """Create analytics system with dependencies"""
    # Initialize storage and registry
    storage_dir = Path.home() / ".kiro" / "context_storage"
    storage = ContextStorage(storage_dir)
    registry = ContextRegistry(storage)
    
    # Create analyzer and optimizer
    analyzer = ContextAnalyzer(registry)
    optimizer = ContextOptimizer(registry, analyzer)
    
    return analyzer, optimizer


def format_bytes(bytes_value: float) -> str:
    """Format bytes as human-readable string"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} TB"


def format_percentage(value: float) -> str:
    """Format percentage with color coding"""
    if value >= 80:
        return f"🟢 {value:.1f}%"
    elif value >= 60:
        return f"🟡 {value:.1f}%"
    else:
        return f"🔴 {value:.1f}%"


def print_usage_analysis(analysis: Dict[str, Any]):
    """Print formatted usage analysis"""
    if "error" in analysis:
        print(f"❌ Error: {analysis['error']}")
        return
    
    print("📊 Context Usage Analysis")
    print("=" * 50)
    
    # Basic statistics
    usage_stats = analysis.get("usage_statistics", {})
    if usage_stats:
        print(f"Total Contexts: {usage_stats.get('total_contexts', 0)}")
        print(f"Total Size: {format_bytes(usage_stats.get('total_size_mb', 0) * 1024 * 1024)}")
        print(f"Average Size: {format_bytes(usage_stats.get('average_size_mb', 0) * 1024 * 1024)}")
        print()
        
        # Conversation statistics
        conv_stats = usage_stats.get("conversation_events", {})
        print(f"Conversation Events:")
        print(f"  Total: {conv_stats.get('total', 0)}")
        print(f"  Average per Context: {conv_stats.get('average_per_context', 0):.1f}")
        print(f"  Max per Context: {conv_stats.get('max_per_context', 0)}")
        print()
        
        # Age distribution
        age_dist = usage_stats.get("age_distribution", {})
        if age_dist:
            print("Age Distribution:")
            print(f"  < 1 day: {age_dist.get('less_than_1_day', 0)}")
            print(f"  1-7 days: {age_dist.get('1_to_7_days', 0)}")
            print(f"  1-4 weeks: {age_dist.get('1_to_4_weeks', 0)}")
            print(f"  1-3 months: {age_dist.get('1_to_3_months', 0)}")
            print(f"  > 3 months: {age_dist.get('older_than_3_months', 0)}")
            print()
    
    # Quality metrics
    quality_metrics = analysis.get("quality_metrics", {})
    if quality_metrics:
        print("Quality Metrics:")
        print(f"  Completeness: {format_percentage(quality_metrics.get('completeness_score', 0))}")
        print(f"  Consistency: {format_percentage(quality_metrics.get('consistency_score', 0))}")
        print(f"  Freshness: {format_percentage(quality_metrics.get('freshness_score', 0))}")
        print(f"  Overall Quality: {format_percentage(quality_metrics.get('overall_quality_score', 0))}")
        
        issues = quality_metrics.get("quality_issues", [])
        if issues:
            print("  Quality Issues:")
            for issue in issues:
                print(f"    ⚠️ {issue}")
        print()
    
    # Detected patterns
    patterns = analysis.get("patterns_detected", [])
    if patterns:
        print(f"Detected Patterns ({len(patterns)}):")
        for pattern in patterns:
            confidence_icon = "🔴" if pattern['confidence'] < 0.5 else "🟡" if pattern['confidence'] < 0.8 else "🟢"
            print(f"  {confidence_icon} {pattern['description']}")
            print(f"    Type: {pattern['pattern_type']}")
            print(f"    Frequency: {pattern['frequency']}")
            print(f"    Confidence: {pattern['confidence']:.1%}")
            if pattern.get('examples'):
                print(f"    Example: {pattern['examples'][0]}")
            print()


def print_dashboard(dashboard: Dict[str, Any]):
    """Print formatted analytics dashboard"""
    if "error" in dashboard:
        print(f"❌ Error: {dashboard['error']}")
        return
    
    print("📈 Analytics Dashboard")
    print("=" * 50)
    
    print(f"Period: {dashboard.get('period_days', 0)} days")
    print(f"Project: {dashboard.get('project_id', 'All projects')}")
    print(f"Metrics Collected: {dashboard.get('metrics_count', 0)}")
    print()
    
    # Summary
    summary = dashboard.get("summary", {})
    if summary:
        print("Metrics Summary:")
        for metric_type, stats in summary.items():
            print(f"  {metric_type.title()}:")
            print(f"    Count: {stats.get('count', 0)}")
            print(f"    Average: {stats.get('average', 0):.2f}")
            print(f"    Range: {stats.get('min', 0):.2f} - {stats.get('max', 0):.2f}")
        print()
    
    # Trends
    trends = dashboard.get("trends", {})
    if trends:
        print("Trends:")
        for metric_name, trend in trends.items():
            direction_icon = "📈" if trend['direction'] == 'increasing' else "📉" if trend['direction'] == 'decreasing' else "➡️"
            print(f"  {direction_icon} {metric_name}: {trend['direction']}")
            if trend['change_percent'] != 0:
                print(f"    Change: {trend['change_percent']:+.1f}%")
        print()
    
    # Performance insights
    perf_insights = dashboard.get("performance_insights", [])
    if perf_insights:
        print("Performance Insights:")
        for insight in perf_insights:
            print(f"  💡 {insight}")
        print()
    
    # Usage insights
    usage_insights = dashboard.get("usage_insights", [])
    if usage_insights:
        print("Usage Insights:")
        for insight in usage_insights:
            print(f"  💡 {insight}")
        print()


def print_recommendations(recommendations: List[Dict[str, Any]]):
    """Print formatted optimization recommendations"""
    if not recommendations:
        print("✅ No optimization recommendations at this time")
        return
    
    print(f"⚡ Optimization Recommendations ({len(recommendations)})")
    print("=" * 50)
    
    for i, rec in enumerate(recommendations, 1):
        priority_icon = "🔴" if rec['priority'] == 'high' else "🟡" if rec['priority'] == 'medium' else "🟢"
        complexity_icon = "🟢" if rec['implementation_complexity'] == 'simple' else "🟡" if rec['implementation_complexity'] == 'moderate' else "🔴"
        
        print(f"{i}. {priority_icon} {rec['title']}")
        print(f"   Strategy: {rec['strategy']}")
        print(f"   Priority: {rec['priority']}")
        print(f"   Complexity: {complexity_icon} {rec['implementation_complexity']}")
        print(f"   Description: {rec['description']}")
        print(f"   Estimated Savings: {format_bytes(rec['estimated_savings_mb'] * 1024 * 1024)}")
        print(f"   Performance Gain: {rec['estimated_performance_gain']:.1f}%")
        print(f"   ID: {rec['recommendation_id']}")
        print()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="AI Memory Palace Analytics CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze context usage for all projects
  python ai_memory_palace_analytics.py analyze

  # Analyze specific project
  python ai_memory_palace_analytics.py analyze --project my-project

  # Show analytics dashboard
  python ai_memory_palace_analytics.py dashboard --days 30

  # Get optimization recommendations
  python ai_memory_palace_analytics.py optimize

  # Show analytics statistics
  python ai_memory_palace_analytics.py stats

  # Export analytics data
  python ai_memory_palace_analytics.py export --format json --output analytics.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze context usage')
    analyze_parser.add_argument('--project', type=str,
                               help='Project ID to analyze (default: all projects)')
    analyze_parser.add_argument('--format', choices=['text', 'json'], default='text',
                               help='Output format')
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Show analytics dashboard')
    dashboard_parser.add_argument('--project', type=str,
                                 help='Project ID (default: all projects)')
    dashboard_parser.add_argument('--days', type=int, default=7,
                                 help='Number of days to analyze (default: 7)')
    dashboard_parser.add_argument('--format', choices=['text', 'json'], default='text',
                                 help='Output format')
    
    # Optimize command
    optimize_parser = subparsers.add_parser('optimize', help='Get optimization recommendations')
    optimize_parser.add_argument('--project', type=str,
                                help='Project ID (default: all projects)')
    optimize_parser.add_argument('--format', choices=['text', 'json'], default='text',
                                help='Output format')
    optimize_parser.add_argument('--apply', type=str,
                                help='Apply optimization by recommendation ID')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show analytics statistics')
    stats_parser.add_argument('--format', choices=['text', 'json'], default='text',
                             help='Output format')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export analytics data')
    export_parser.add_argument('--project', type=str,
                              help='Project ID (default: all projects)')
    export_parser.add_argument('--days', type=int, default=30,
                              help='Number of days to export (default: 30)')
    export_parser.add_argument('--format', choices=['json', 'csv'], default='json',
                              help='Export format')
    export_parser.add_argument('--output', type=str, required=True,
                              help='Output file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        analyzer, optimizer = create_analytics_system()
        cli = AnalyticsOptimizationCLI(analyzer, optimizer)
        
        if args.command == 'analyze':
            print("📊 Analyzing context usage...")
            analysis = cli.analyze_usage(args.project)
            
            if args.format == 'json':
                print(json.dumps(analysis, indent=2))
            else:
                print_usage_analysis(analysis)
        
        elif args.command == 'dashboard':
            print("📈 Generating analytics dashboard...")
            dashboard = cli.get_dashboard(args.project, args.days)
            
            if args.format == 'json':
                print(json.dumps(dashboard, indent=2))
            else:
                print_dashboard(dashboard)
        
        elif args.command == 'optimize':
            if args.apply:
                print(f"⚡ Applying optimization: {args.apply}")
                result = cli.apply_optimization(args.apply, args.project)
                
                if args.format == 'json':
                    print(json.dumps(result, indent=2))
                else:
                    if result.get('success'):
                        print("✅ Optimization applied successfully")
                        print(f"Space Saved: {format_bytes(result.get('actual_savings_mb', 0) * 1024 * 1024)}")
                        print(f"Performance Gain: {result.get('actual_performance_gain', 0):.1f}%")
                        print(f"Execution Time: {result.get('execution_time_ms', 0):.0f}ms")
                    else:
                        print("❌ Optimization failed")
                        if 'error' in result:
                            print(f"Error: {result['error']}")
            else:
                print("⚡ Generating optimization recommendations...")
                recommendations = cli.get_recommendations(args.project)
                
                if args.format == 'json':
                    print(json.dumps(recommendations, indent=2))
                else:
                    print_recommendations(recommendations)
        
        elif args.command == 'stats':
            print("📊 Getting analytics statistics...")
            
            analytics_stats = cli.get_analytics_stats()
            optimization_stats = cli.get_optimization_stats()
            
            stats = {
                "analytics": analytics_stats,
                "optimization": optimization_stats
            }
            
            if args.format == 'json':
                print(json.dumps(stats, indent=2))
            else:
                print("Analytics Statistics:")
                print(f"  Analyses Performed: {analytics_stats['analyses_performed']}")
                print(f"  Patterns Detected: {analytics_stats['patterns_detected']}")
                print(f"  Metrics Collected: {analytics_stats['metrics_collected']}")
                print()
                
                print("Optimization Statistics:")
                print(f"  Optimizations Performed: {optimization_stats['optimizations_performed']}")
                print(f"  Total Space Saved: {format_bytes(optimization_stats['total_space_saved_mb'] * 1024 * 1024)}")
                print(f"  Performance Improvements: {optimization_stats['performance_improvements']}")
                print(f"  Average Savings per Optimization: {format_bytes(optimization_stats['average_savings_per_optimization'] * 1024 * 1024)}")
        
        elif args.command == 'export':
            print(f"📤 Exporting analytics data to {args.output}...")
            
            # Get dashboard data for export
            dashboard = cli.get_dashboard(args.project, args.days)
            
            if "error" in dashboard:
                print(f"❌ Error: {dashboard['error']}")
                return 1
            
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if args.format == 'json':
                with open(output_path, 'w') as f:
                    json.dump(dashboard, f, indent=2)
            
            elif args.format == 'csv':
                # Simplified CSV export
                import csv
                
                with open(output_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    
                    # Write header
                    writer.writerow(['Metric Type', 'Count', 'Average', 'Min', 'Max'])
                    
                    # Write summary data
                    summary = dashboard.get('summary', {})
                    for metric_type, stats in summary.items():
                        writer.writerow([
                            metric_type,
                            stats.get('count', 0),
                            stats.get('average', 0),
                            stats.get('min', 0),
                            stats.get('max', 0)
                        ])
            
            print(f"✅ Analytics data exported to {output_path}")
            print(f"Format: {args.format}")
            print(f"Period: {args.days} days")
            if args.project:
                print(f"Project: {args.project}")
        
        return 0
    
    except KeyboardInterrupt:
        print("\n⏹️ Operation cancelled by user")
        return 1
    
    except Exception as e:
        print(f"💥 Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())