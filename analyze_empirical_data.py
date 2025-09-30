#!/usr/bin/env python3
"""
Empirical Data Analysis System
Comprehensive analysis of collected Kiro agent effectiveness data
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timezone
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any
import statistics

class EmpiricalDataAnalyzer:
    """Comprehensive analysis of empirical data collected during Kiro agent usage"""
    
    def __init__(self, data_dir: str = "empirical_data"):
        self.data_dir = Path(data_dir)
        self.analysis_results = {}
        
        print(f"📊 Empirical Data Analyzer Initialized")
        print(f"📂 Data Directory: {self.data_dir}")
        
    def load_session_data(self, session_dir: Path) -> Dict[str, pd.DataFrame]:
        """Load all data files from a session directory"""
        data = {}
        
        # Load each JSONL file
        jsonl_files = list(session_dir.glob('*.jsonl'))
        
        for file_path in jsonl_files:
            try:
                records = []
                with open(file_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            records.append(json.loads(line))
                
                if records:
                    df = pd.json_normalize(records)
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    data[file_path.stem] = df
                    print(f"✅ Loaded {len(records)} records from {file_path.name}")
                
            except Exception as e:
                print(f"❌ Error loading {file_path}: {e}")
        
        return data
    
    def analyze_system_performance(self, system_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze system performance metrics"""
        if system_data.empty:
            return {}
        
        analysis = {
            'duration_minutes': (system_data['timestamp'].max() - system_data['timestamp'].min()).total_seconds() / 60,
            'data_points': len(system_data),
            'cpu_usage': {
                'mean': system_data['system.cpu_percent'].mean(),
                'max': system_data['system.cpu_percent'].max(),
                'min': system_data['system.cpu_percent'].min(),
                'std': system_data['system.cpu_percent'].std()
            },
            'memory_usage': {
                'mean': system_data['system.memory_percent'].mean(),
                'max': system_data['system.memory_percent'].max(),
                'min': system_data['system.memory_percent'].min(),
                'std': system_data['system.memory_percent'].std()
            },
            'kiro_processes': {
                'mean': system_data['processes.kiro_processes'].mean(),
                'max': system_data['processes.kiro_processes'].max(),
                'total_observations': len(system_data[system_data['processes.kiro_processes'] > 0])
            }
        }
        
        return analysis
    
    def analyze_development_velocity(self, git_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze development velocity and git activity"""
        if git_data.empty:
            return {}
        
        # Calculate commits per hour
        git_data['hour'] = git_data['timestamp'].dt.floor('H')
        commits_per_hour = git_data.groupby('hour')['commits_last_minute'].sum()
        
        # Calculate file modification patterns
        total_modifications = git_data['modified_files_count'].sum()
        
        analysis = {
            'total_commits_observed': git_data['commits_last_minute'].sum(),
            'commits_per_hour': {
                'mean': commits_per_hour.mean(),
                'max': commits_per_hour.max(),
                'total_active_hours': len(commits_per_hour[commits_per_hour > 0])
            },
            'file_modifications': {
                'total': total_modifications,
                'average_per_observation': git_data['modified_files_count'].mean(),
                'max_simultaneous': git_data['modified_files_count'].max()
            },
            'development_activity_periods': len(git_data[git_data['commits_last_minute'] > 0])
        }
        
        return analysis
    
    def analyze_agent_effectiveness(self, agent_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze Kiro agent effectiveness and usage patterns"""
        if agent_data.empty:
            return {}
        
        # Agent activity analysis
        active_periods = agent_data[agent_data['active_agent_processes'] > 0]
        
        analysis = {
            'agent_usage_frequency': {
                'total_observations': len(agent_data),
                'active_periods': len(active_periods),
                'usage_rate': len(active_periods) / len(agent_data) if len(agent_data) > 0 else 0
            },
            'concurrent_agents': {
                'max_concurrent': agent_data['active_agent_processes'].max(),
                'mean_concurrent': active_periods['active_agent_processes'].mean() if len(active_periods) > 0 else 0
            },
            'agent_session_duration': {
                'observations_with_agents': len(active_periods)
            }
        }
        
        return analysis
    
    def analyze_task_completion(self, task_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze task completion rates and progress"""
        if task_data.empty:
            return {}
        
        # Task completion progress over time
        latest_data = task_data.iloc[-1] if len(task_data) > 0 else None
        
        if latest_data is None:
            return {}
        
        analysis = {
            'current_status': {
                'total_tasks': latest_data['total_tasks'],
                'completed_tasks': latest_data['completed_tasks'],
                'in_progress_tasks': latest_data['in_progress_tasks'],
                'completion_rate': latest_data['completion_rate']
            },
            'progress_trend': {
                'completion_rate_change': (task_data['completion_rate'].iloc[-1] - task_data['completion_rate'].iloc[0]) if len(task_data) > 1 else 0,
                'tasks_completed_during_session': task_data['completed_tasks'].iloc[-1] - task_data['completed_tasks'].iloc[0] if len(task_data) > 1 else 0
            }
        }
        
        return analysis
    
    def analyze_code_quality_evolution(self, quality_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze code quality metrics evolution"""
        if quality_data.empty:
            return {}
        
        latest_data = quality_data.iloc[-1] if len(quality_data) > 0 else None
        
        if latest_data is None:
            return {}
        
        analysis = {
            'current_metrics': {
                'python_files': latest_data['python_files_count'],
                'lines_of_code': latest_data['total_lines_of_code'],
                'average_file_size': latest_data['average_lines_per_file'],
                'test_files': latest_data['test_files_count'],
                'test_coverage_ratio': latest_data['test_to_code_ratio']
            },
            'evolution': {
                'files_added': quality_data['python_files_count'].iloc[-1] - quality_data['python_files_count'].iloc[0] if len(quality_data) > 1 else 0,
                'lines_added': quality_data['total_lines_of_code'].iloc[-1] - quality_data['total_lines_of_code'].iloc[0] if len(quality_data) > 1 else 0,
                'tests_added': quality_data['test_files_count'].iloc[-1] - quality_data['test_files_count'].iloc[0] if len(quality_data) > 1 else 0
            }
        }
        
        return analysis
    
    def generate_correlation_analysis(self, session_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Generate correlation analysis between different metrics"""
        correlations = {}
        
        try:
            # Merge datasets on timestamp for correlation analysis
            if 'system_metrics' in session_data and 'git_activity' in session_data:
                system_df = session_data['system_metrics'].set_index('timestamp')
                git_df = session_data['git_activity'].set_index('timestamp')
                
                # Resample to common frequency (hourly)
                system_hourly = system_df.resample('H').mean()
                git_hourly = git_df.resample('H').sum()
                
                # Merge and calculate correlations
                merged = pd.merge(system_hourly, git_hourly, left_index=True, right_index=True, how='inner')
                
                if not merged.empty:
                    correlations['cpu_vs_commits'] = merged['system.cpu_percent'].corr(merged['commits_last_minute'])
                    correlations['memory_vs_modifications'] = merged['system.memory_percent'].corr(merged['modified_files_count'])
                    correlations['kiro_processes_vs_activity'] = merged['processes.kiro_processes'].corr(merged['commits_last_minute'])
        
        except Exception as e:
            print(f"❌ Error in correlation analysis: {e}")
        
        return correlations
    
    def generate_comprehensive_report(self, session_dir: Path) -> Dict[str, Any]:
        """Generate comprehensive analysis report for a session"""
        print(f"\n📊 Analyzing session: {session_dir.name}")
        
        # Load session data
        session_data = self.load_session_data(session_dir)
        
        if not session_data:
            print(f"❌ No data found in {session_dir}")
            return {}
        
        # Perform individual analyses
        report = {
            'session_info': {
                'session_id': session_dir.name,
                'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
                'data_files_analyzed': list(session_data.keys())
            }
        }
        
        # System performance analysis
        if 'system_metrics' in session_data:
            report['system_performance'] = self.analyze_system_performance(session_data['system_metrics'])
        
        # Development velocity analysis
        if 'git_activity' in session_data:
            report['development_velocity'] = self.analyze_development_velocity(session_data['git_activity'])
        
        # Agent effectiveness analysis
        if 'agent_interactions' in session_data:
            report['agent_effectiveness'] = self.analyze_agent_effectiveness(session_data['agent_interactions'])
        
        # Task completion analysis
        if 'task_completion' in session_data:
            report['task_completion'] = self.analyze_task_completion(session_data['task_completion'])
        
        # Code quality analysis
        if 'code_quality' in session_data:
            report['code_quality'] = self.analyze_code_quality_evolution(session_data['code_quality'])
        
        # Correlation analysis
        report['correlations'] = self.generate_correlation_analysis(session_data)
        
        return report
    
    def analyze_all_sessions(self) -> Dict[str, Any]:
        """Analyze all available sessions"""
        session_dirs = [d for d in self.data_dir.iterdir() if d.is_dir() and d.name.startswith('session_')]
        
        if not session_dirs:
            print("❌ No session directories found")
            return {}
        
        print(f"📊 Found {len(session_dirs)} sessions to analyze")
        
        all_reports = {}
        summary_stats = {
            'total_sessions': len(session_dirs),
            'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
            'sessions_analyzed': []
        }
        
        for session_dir in sorted(session_dirs):
            try:
                report = self.generate_comprehensive_report(session_dir)
                if report:
                    all_reports[session_dir.name] = report
                    summary_stats['sessions_analyzed'].append(session_dir.name)
            except Exception as e:
                print(f"❌ Error analyzing {session_dir}: {e}")
        
        # Generate cross-session analysis
        cross_session_analysis = self.generate_cross_session_analysis(all_reports)
        
        final_report = {
            'summary': summary_stats,
            'individual_sessions': all_reports,
            'cross_session_analysis': cross_session_analysis
        }
        
        return final_report
    
    def generate_cross_session_analysis(self, all_reports: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analysis across multiple sessions"""
        if not all_reports:
            return {}
        
        # Aggregate metrics across sessions
        cpu_means = []
        memory_means = []
        completion_rates = []
        commits_per_hour = []
        
        for session_name, report in all_reports.items():
            if 'system_performance' in report:
                cpu_means.append(report['system_performance'].get('cpu_usage', {}).get('mean', 0))
                memory_means.append(report['system_performance'].get('memory_usage', {}).get('mean', 0))
            
            if 'task_completion' in report:
                completion_rates.append(report['task_completion'].get('current_status', {}).get('completion_rate', 0))
            
            if 'development_velocity' in report:
                commits_per_hour.append(report['development_velocity'].get('commits_per_hour', {}).get('mean', 0))
        
        cross_analysis = {
            'aggregate_metrics': {
                'average_cpu_usage': statistics.mean(cpu_means) if cpu_means else 0,
                'average_memory_usage': statistics.mean(memory_means) if memory_means else 0,
                'average_completion_rate': statistics.mean(completion_rates) if completion_rates else 0,
                'average_commits_per_hour': statistics.mean(commits_per_hour) if commits_per_hour else 0
            },
            'performance_trends': {
                'cpu_usage_variance': statistics.variance(cpu_means) if len(cpu_means) > 1 else 0,
                'memory_usage_variance': statistics.variance(memory_means) if len(memory_means) > 1 else 0,
                'completion_rate_variance': statistics.variance(completion_rates) if len(completion_rates) > 1 else 0
            },
            'sessions_compared': len(all_reports)
        }
        
        return cross_analysis
    
    def save_analysis_report(self, report: Dict[str, Any], filename: str = None):
        """Save analysis report to file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"empirical_analysis_report_{timestamp}.json"
        
        output_path = self.data_dir / filename
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📄 Analysis report saved to: {output_path}")
        return output_path

def main():
    """Main execution function"""
    print("📊 Starting Empirical Data Analysis")
    print("=" * 50)
    
    analyzer = EmpiricalDataAnalyzer()
    
    try:
        # Analyze all available sessions
        comprehensive_report = analyzer.analyze_all_sessions()
        
        if comprehensive_report:
            # Save the report
            report_path = analyzer.save_analysis_report(comprehensive_report)
            
            # Print summary
            print("\n📈 Analysis Summary:")
            print(f"Sessions Analyzed: {comprehensive_report['summary']['total_sessions']}")
            
            if 'cross_session_analysis' in comprehensive_report:
                cross_analysis = comprehensive_report['cross_session_analysis']
                if 'aggregate_metrics' in cross_analysis:
                    metrics = cross_analysis['aggregate_metrics']
                    print(f"Average CPU Usage: {metrics.get('average_cpu_usage', 0):.2f}%")
                    print(f"Average Memory Usage: {metrics.get('average_memory_usage', 0):.2f}%")
                    print(f"Average Task Completion Rate: {metrics.get('average_completion_rate', 0):.2%}")
                    print(f"Average Commits per Hour: {metrics.get('average_commits_per_hour', 0):.2f}")
            
            print(f"\n✅ Complete analysis report available at: {report_path}")
        else:
            print("❌ No data available for analysis")
    
    except Exception as e:
        print(f"❌ Error during analysis: {e}")

if __name__ == "__main__":
    main()