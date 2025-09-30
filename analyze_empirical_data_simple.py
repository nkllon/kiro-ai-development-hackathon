#!/usr/bin/env python3
"""
Simple Empirical Data Analysis (No External Dependencies)
========================================================

Analyze collected empirical data without requiring pandas or matplotlib.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import statistics


class SimpleEmpiricalAnalyzer:
    """Simple empirical data analyzer using only standard library."""
    
    def __init__(self, data_dir: str = "empirical_data"):
        self.data_dir = Path(data_dir)
        
    def load_jsonl_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load JSONL file and return list of records."""
        records = []
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    if line.strip():
                        records.append(json.loads(line))
        except Exception as e:
            print(f"❌ Error loading {file_path}: {e}")
        return records
    
    def analyze_session_data(self, session_dir: Path) -> Dict[str, Any]:
        """Analyze data from a single session."""
        print(f"📊 Analyzing session: {session_dir.name}")
        
        analysis = {
            'session_id': session_dir.name,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        # Analyze system metrics
        system_metrics_file = session_dir / "system_metrics.jsonl"
        if system_metrics_file.exists():
            system_data = self.load_jsonl_file(system_metrics_file)
            if system_data:
                cpu_values = [record['system']['cpu_percent'] for record in system_data]
                memory_values = [record['system']['memory_percent'] for record in system_data]
                kiro_processes = [record['processes']['kiro_processes'] for record in system_data]
                
                analysis['system_performance'] = {
                    'data_points': len(system_data),
                    'duration_minutes': len(system_data) * 0.5,  # 30-second intervals
                    'cpu_usage': {
                        'mean': statistics.mean(cpu_values),
                        'max': max(cpu_values),
                        'min': min(cpu_values),
                        'median': statistics.median(cpu_values)
                    },
                    'memory_usage': {
                        'mean': statistics.mean(memory_values),
                        'max': max(memory_values),
                        'min': min(memory_values),
                        'median': statistics.median(memory_values)
                    },
                    'kiro_processes': {
                        'mean': statistics.mean(kiro_processes),
                        'max': max(kiro_processes),
                        'min': min(kiro_processes)
                    }
                }
        
        # Analyze git activity
        git_activity_file = session_dir / "git_activity.jsonl"
        if git_activity_file.exists():
            git_data = self.load_jsonl_file(git_activity_file)
            if git_data:
                commits = [record['commits_last_minute'] for record in git_data]
                modifications = [record['modified_files_count'] for record in git_data]
                
                analysis['development_velocity'] = {
                    'data_points': len(git_data),
                    'total_commits_observed': sum(commits),
                    'total_file_modifications': sum(modifications),
                    'average_commits_per_observation': statistics.mean(commits),
                    'average_modifications_per_observation': statistics.mean(modifications),
                    'active_development_periods': len([c for c in commits if c > 0])
                }
        
        # Analyze agent interactions
        agent_file = session_dir / "agent_interactions.jsonl"
        if agent_file.exists():
            agent_data = self.load_jsonl_file(agent_file)
            if agent_data:
                active_agents = [record['active_agent_processes'] for record in agent_data]
                
                analysis['agent_effectiveness'] = {
                    'data_points': len(agent_data),
                    'agent_usage_frequency': len([a for a in active_agents if a > 0]) / len(active_agents),
                    'max_concurrent_agents': max(active_agents),
                    'average_active_agents': statistics.mean(active_agents)
                }
        
        # Analyze task completion
        task_file = session_dir / "task_completion.jsonl"
        if task_file.exists():
            task_data = self.load_jsonl_file(task_file)
            if task_data:
                latest_data = task_data[-1]
                
                analysis['task_completion'] = {
                    'total_tasks': latest_data['total_tasks'],
                    'completed_tasks': latest_data['completed_tasks'],
                    'in_progress_tasks': latest_data['in_progress_tasks'],
                    'completion_rate': latest_data['completion_rate'],
                    'task_files_monitored': latest_data['task_files_scanned']
                }
                
                # Calculate progress over time if multiple data points
                if len(task_data) > 1:
                    initial_completion = task_data[0]['completed_tasks']
                    final_completion = task_data[-1]['completed_tasks']
                    analysis['task_completion']['tasks_completed_during_session'] = final_completion - initial_completion
        
        # Analyze code quality
        quality_file = session_dir / "code_quality.jsonl"
        if quality_file.exists():
            quality_data = self.load_jsonl_file(quality_file)
            if quality_data:
                latest_data = quality_data[-1]
                
                analysis['code_quality'] = {
                    'python_files': latest_data['python_files_count'],
                    'lines_of_code': latest_data['total_lines_of_code'],
                    'average_file_size': latest_data['average_lines_per_file'],
                    'test_files': latest_data['test_files_count'],
                    'test_coverage_ratio': latest_data['test_to_code_ratio']
                }
        
        return analysis
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis across all sessions."""
        print("🔬 Generating Comprehensive Empirical Analysis Report")
        print("=" * 60)
        
        # Find all session directories
        session_dirs = [d for d in self.data_dir.iterdir() if d.is_dir() and d.name.startswith('session_')]
        
        if not session_dirs:
            print("❌ No session directories found")
            return {}
        
        print(f"📊 Found {len(session_dirs)} sessions to analyze")
        
        # Analyze each session
        session_analyses = {}
        for session_dir in sorted(session_dirs):
            try:
                analysis = self.analyze_session_data(session_dir)
                session_analyses[session_dir.name] = analysis
            except Exception as e:
                print(f"❌ Error analyzing {session_dir}: {e}")
        
        # Generate cross-session analysis
        cross_session_analysis = self.analyze_across_sessions(session_analyses)
        
        # Generate insights
        insights = self.generate_insights(session_analyses, cross_session_analysis)
        
        comprehensive_report = {
            'analysis_summary': {
                'total_sessions': len(session_dirs),
                'successfully_analyzed': len(session_analyses),
                'analysis_timestamp': datetime.now().isoformat(),
                'data_directory': str(self.data_dir)
            },
            'individual_sessions': session_analyses,
            'cross_session_analysis': cross_session_analysis,
            'empirical_insights': insights
        }
        
        return comprehensive_report
    
    def analyze_across_sessions(self, session_analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns across multiple sessions."""
        if not session_analyses:
            return {}
        
        # Aggregate system performance metrics
        cpu_means = []
        memory_means = []
        kiro_process_counts = []
        
        # Aggregate development metrics
        completion_rates = []
        total_tasks = []
        
        for session_name, analysis in session_analyses.items():
            if 'system_performance' in analysis:
                cpu_means.append(analysis['system_performance']['cpu_usage']['mean'])
                memory_means.append(analysis['system_performance']['memory_usage']['mean'])
                kiro_process_counts.append(analysis['system_performance']['kiro_processes']['mean'])
            
            if 'task_completion' in analysis:
                completion_rates.append(analysis['task_completion']['completion_rate'])
                total_tasks.append(analysis['task_completion']['total_tasks'])
        
        cross_analysis = {
            'system_performance_trends': {
                'average_cpu_usage': statistics.mean(cpu_means) if cpu_means else 0,
                'cpu_usage_variance': statistics.variance(cpu_means) if len(cpu_means) > 1 else 0,
                'average_memory_usage': statistics.mean(memory_means) if memory_means else 0,
                'memory_usage_variance': statistics.variance(memory_means) if len(memory_means) > 1 else 0,
                'average_kiro_processes': statistics.mean(kiro_process_counts) if kiro_process_counts else 0
            },
            'development_trends': {
                'average_completion_rate': statistics.mean(completion_rates) if completion_rates else 0,
                'completion_rate_variance': statistics.variance(completion_rates) if len(completion_rates) > 1 else 0,
                'average_total_tasks': statistics.mean(total_tasks) if total_tasks else 0
            },
            'sessions_analyzed': len(session_analyses)
        }
        
        return cross_analysis
    
    def generate_insights(self, session_analyses: Dict[str, Any], cross_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actionable insights from the analysis."""
        insights = {
            'system_performance_insights': [],
            'development_velocity_insights': [],
            'agent_effectiveness_insights': [],
            'recommendations': []
        }
        
        # System performance insights
        if 'system_performance_trends' in cross_analysis:
            perf = cross_analysis['system_performance_trends']
            avg_cpu = perf.get('average_cpu_usage', 0)
            avg_memory = perf.get('average_memory_usage', 0)
            avg_kiro_processes = perf.get('average_kiro_processes', 0)
            
            if avg_cpu > 70:
                insights['system_performance_insights'].append(f"High CPU usage detected: {avg_cpu:.1f}% average")
                insights['recommendations'].append("Consider optimizing CPU-intensive operations or reducing concurrent tasks")
            
            if avg_memory > 80:
                insights['system_performance_insights'].append(f"High memory usage detected: {avg_memory:.1f}% average")
                insights['recommendations'].append("Monitor memory usage and consider memory optimization strategies")
            
            if avg_kiro_processes > 15:
                insights['agent_effectiveness_insights'].append(f"High Kiro process count: {avg_kiro_processes:.1f} average")
                insights['recommendations'].append("Monitor Kiro process efficiency and resource usage")
        
        # Development velocity insights
        if 'development_trends' in cross_analysis:
            dev = cross_analysis['development_trends']
            avg_completion_rate = dev.get('average_completion_rate', 0)
            
            if avg_completion_rate > 0.15:
                insights['development_velocity_insights'].append(f"Good task completion rate: {avg_completion_rate:.1%}")
            elif avg_completion_rate < 0.05:
                insights['development_velocity_insights'].append(f"Low task completion rate: {avg_completion_rate:.1%}")
                insights['recommendations'].append("Review task management and completion processes")
        
        # Agent effectiveness insights
        agent_usage_rates = []
        for analysis in session_analyses.values():
            if 'agent_effectiveness' in analysis:
                agent_usage_rates.append(analysis['agent_effectiveness']['agent_usage_frequency'])
        
        if agent_usage_rates:
            avg_usage_rate = statistics.mean(agent_usage_rates)
            if avg_usage_rate > 0.8:
                insights['agent_effectiveness_insights'].append(f"High agent usage rate: {avg_usage_rate:.1%}")
            elif avg_usage_rate < 0.3:
                insights['agent_effectiveness_insights'].append(f"Low agent usage rate: {avg_usage_rate:.1%}")
                insights['recommendations'].append("Consider increasing agent utilization for development tasks")
        
        return insights
    
    def save_report(self, report: Dict[str, Any], filename: str = None) -> Path:
        """Save analysis report to file."""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"empirical_analysis_report_{timestamp}.json"
        
        output_path = self.data_dir / filename
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return output_path
    
    def print_summary(self, report: Dict[str, Any]):
        """Print a human-readable summary of the analysis."""
        print("\n📈 EMPIRICAL ANALYSIS SUMMARY")
        print("=" * 50)
        
        summary = report.get('analysis_summary', {})
        print(f"Sessions Analyzed: {summary.get('successfully_analyzed', 0)}")
        print(f"Analysis Timestamp: {summary.get('analysis_timestamp', 'Unknown')}")
        
        # Cross-session analysis
        cross_analysis = report.get('cross_session_analysis', {})
        if 'system_performance_trends' in cross_analysis:
            perf = cross_analysis['system_performance_trends']
            print(f"\n🖥️  System Performance:")
            print(f"   Average CPU Usage: {perf.get('average_cpu_usage', 0):.1f}%")
            print(f"   Average Memory Usage: {perf.get('average_memory_usage', 0):.1f}%")
            print(f"   Average Kiro Processes: {perf.get('average_kiro_processes', 0):.1f}")
        
        if 'development_trends' in cross_analysis:
            dev = cross_analysis['development_trends']
            print(f"\n📊 Development Metrics:")
            print(f"   Average Task Completion Rate: {dev.get('average_completion_rate', 0):.1%}")
            print(f"   Average Total Tasks: {dev.get('average_total_tasks', 0):.0f}")
        
        # Insights
        insights = report.get('empirical_insights', {})
        if insights:
            print(f"\n💡 Key Insights:")
            for category, insight_list in insights.items():
                if insight_list and category != 'recommendations':
                    print(f"   {category.replace('_', ' ').title()}:")
                    for insight in insight_list:
                        print(f"     • {insight}")
            
            recommendations = insights.get('recommendations', [])
            if recommendations:
                print(f"\n🎯 Recommendations:")
                for rec in recommendations:
                    print(f"   • {rec}")


def main():
    """Main execution function."""
    print("📊 Simple Empirical Data Analysis")
    print("=" * 40)
    
    analyzer = SimpleEmpiricalAnalyzer()
    
    try:
        # Generate comprehensive report
        report = analyzer.generate_comprehensive_report()
        
        if report:
            # Print summary
            analyzer.print_summary(report)
            
            # Save detailed report
            report_path = analyzer.save_report(report)
            print(f"\n📄 Detailed report saved to: {report_path}")
            
        else:
            print("❌ No data available for analysis")
    
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        raise


if __name__ == "__main__":
    main()