#!/usr/bin/env python3
"""
Empirical Data Collection System for Kiro Agent Analysis
Comprehensive monitoring and data gathering for agent effectiveness research
"""

import json
import time
import subprocess
import psutil
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List
import uuid

class EmpiricalDataCollector:
    """Comprehensive data collection system for Kiro agent analysis"""
    
    def __init__(self, data_dir: str = "empirical_data"):
        self.data_dir = Path(data_dir)
        self.session_id = str(uuid.uuid4())
        self.start_time = datetime.now(timezone.utc)
        
        # Create timestamped data directory
        self.session_dir = self.data_dir / f"session_{self.start_time.strftime('%Y%m%d_%H%M%S')}"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # Data collection flags
        self.collecting = True
        self.threads = []
        
        print(f"🔬 Empirical Data Collection Started")
        print(f"📁 Session ID: {self.session_id}")
        print(f"📂 Data Directory: {self.session_dir}")
        
    def collect_system_metrics(self):
        """Continuous system metrics collection"""
        metrics_file = self.session_dir / "system_metrics.jsonl"
        
        while self.collecting:
            try:
                # System metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # Process metrics
                kiro_processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                    if 'kiro' in proc.info['name'].lower():
                        kiro_processes.append(proc.info)
                
                # Network metrics
                network = psutil.net_io_counters()
                
                metrics = {
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'session_id': self.session_id,
                    'system': {
                        'cpu_percent': cpu_percent,
                        'memory_percent': memory.percent,
                        'memory_available_gb': memory.available / (1024**3),
                        'disk_percent': (disk.used / disk.total) * 100,
                        'disk_free_gb': disk.free / (1024**3)
                    },
                    'processes': {
                        'total_processes': len(list(psutil.process_iter())),
                        'kiro_processes': len(kiro_processes),
                        'kiro_process_details': kiro_processes
                    },
                    'network': {
                        'bytes_sent': network.bytes_sent,
                        'bytes_recv': network.bytes_recv,
                        'packets_sent': network.packets_sent,
                        'packets_recv': network.packets_recv
                    }
                }
                
                # Write metrics
                with open(metrics_file, 'a') as f:
                    f.write(json.dumps(metrics) + '\n')
                
                time.sleep(30)  # Collect every 30 seconds
                
            except Exception as e:
                print(f"❌ Error collecting system metrics: {e}")
                time.sleep(60)
    
    def collect_git_activity(self):
        """Monitor git activity and development velocity"""
        git_file = self.session_dir / "git_activity.jsonl"
        
        while self.collecting:
            try:
                # Recent commits
                result = subprocess.run(
                    ['git', 'log', '--oneline', '--since=1 minute ago'],
                    capture_output=True, text=True, cwd='.'
                )
                
                commits = result.stdout.strip().split('\n') if result.stdout.strip() else []
                
                # Git status
                status_result = subprocess.run(
                    ['git', 'status', '--porcelain'],
                    capture_output=True, text=True, cwd='.'
                )
                
                modified_files = status_result.stdout.strip().split('\n') if status_result.stdout.strip() else []
                
                # Branch info
                branch_result = subprocess.run(
                    ['git', 'branch', '--show-current'],
                    capture_output=True, text=True, cwd='.'
                )
                
                current_branch = branch_result.stdout.strip()
                
                git_data = {
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'session_id': self.session_id,
                    'commits_last_minute': len([c for c in commits if c]),
                    'recent_commits': commits[:10],  # Last 10 commits
                    'modified_files_count': len([f for f in modified_files if f]),
                    'modified_files': modified_files,
                    'current_branch': current_branch
                }
                
                with open(git_file, 'a') as f:
                    f.write(json.dumps(git_data) + '\n')
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"❌ Error collecting git activity: {e}")
                time.sleep(120)
    
    def collect_agent_interactions(self):
        """Monitor Kiro agent interactions and performance"""
        agent_file = self.session_dir / "agent_interactions.jsonl"
        
        # This would be enhanced to hook into actual Kiro agent calls
        # For now, we'll monitor process activity and log files
        
        while self.collecting:
            try:
                # Monitor for kiro chat processes
                kiro_processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time', 'cpu_percent', 'memory_percent']):
                    try:
                        if proc.info['name'] and 'kiro' in proc.info['name'].lower():
                            if proc.info['cmdline'] and 'chat' in ' '.join(proc.info['cmdline']):
                                kiro_processes.append({
                                    'pid': proc.info['pid'],
                                    'cmdline': proc.info['cmdline'],
                                    'create_time': proc.info['create_time'],
                                    'cpu_percent': proc.info['cpu_percent'],
                                    'memory_percent': proc.info['memory_percent'],
                                    'duration': time.time() - proc.info['create_time']
                                })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                agent_data = {
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'session_id': self.session_id,
                    'active_agent_processes': len(kiro_processes),
                    'agent_process_details': kiro_processes
                }
                
                with open(agent_file, 'a') as f:
                    f.write(json.dumps(agent_data) + '\n')
                
                time.sleep(15)  # Check every 15 seconds
                
            except Exception as e:
                print(f"❌ Error collecting agent interactions: {e}")
                time.sleep(30)
    
    def collect_task_completion_data(self):
        """Monitor task completion and development progress"""
        task_file = self.session_dir / "task_completion.jsonl"
        
        while self.collecting:
            try:
                # Scan for task files and completion status
                task_files = list(Path('.kiro/specs').glob('*/tasks.md'))
                
                total_tasks = 0
                completed_tasks = 0
                in_progress_tasks = 0
                
                for task_file_path in task_files:
                    try:
                        with open(task_file_path, 'r') as f:
                            content = f.read()
                            
                        # Count task checkboxes
                        lines = content.split('\n')
                        for line in lines:
                            if '- [ ]' in line:
                                total_tasks += 1
                            elif '- [x]' in line or '- [X]' in line:
                                completed_tasks += 1
                                total_tasks += 1
                            elif '- [-]' in line:
                                in_progress_tasks += 1
                                total_tasks += 1
                                
                    except Exception as e:
                        print(f"❌ Error reading task file {task_file_path}: {e}")
                
                completion_data = {
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'session_id': self.session_id,
                    'total_tasks': total_tasks,
                    'completed_tasks': completed_tasks,
                    'in_progress_tasks': in_progress_tasks,
                    'completion_rate': completed_tasks / total_tasks if total_tasks > 0 else 0,
                    'task_files_scanned': len(task_files)
                }
                
                with open(task_file, 'a') as f:
                    f.write(json.dumps(completion_data) + '\n')
                
                time.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                print(f"❌ Error collecting task completion data: {e}")
                time.sleep(600)
    
    def collect_code_quality_metrics(self):
        """Analyze code quality evolution"""
        quality_file = self.session_dir / "code_quality.jsonl"
        
        while self.collecting:
            try:
                # Count Python files and lines of code
                python_files = list(Path('src').glob('**/*.py'))
                total_lines = 0
                total_files = len(python_files)
                
                for py_file in python_files[:50]:  # Sample first 50 files
                    try:
                        with open(py_file, 'r') as f:
                            lines = len(f.readlines())
                            total_lines += lines
                    except Exception:
                        continue
                
                # Test files
                test_files = list(Path('.').glob('**/test_*.py')) + list(Path('.').glob('**/*_test.py'))
                
                quality_data = {
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'session_id': self.session_id,
                    'python_files_count': total_files,
                    'total_lines_of_code': total_lines,
                    'average_lines_per_file': total_lines / total_files if total_files > 0 else 0,
                    'test_files_count': len(test_files),
                    'test_to_code_ratio': len(test_files) / total_files if total_files > 0 else 0
                }
                
                with open(quality_file, 'a') as f:
                    f.write(json.dumps(quality_data) + '\n')
                
                time.sleep(600)  # Check every 10 minutes
                
            except Exception as e:
                print(f"❌ Error collecting code quality metrics: {e}")
                time.sleep(1200)
    
    def start_collection(self):
        """Start all data collection threads"""
        collectors = [
            ('System Metrics', self.collect_system_metrics),
            ('Git Activity', self.collect_git_activity),
            ('Agent Interactions', self.collect_agent_interactions),
            ('Task Completion', self.collect_task_completion_data),
            ('Code Quality', self.collect_code_quality_metrics)
        ]
        
        for name, collector_func in collectors:
            thread = threading.Thread(target=collector_func, name=name, daemon=True)
            thread.start()
            self.threads.append(thread)
            print(f"✅ Started {name} collection")
        
        # Create session metadata
        metadata = {
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat(),
            'data_directory': str(self.session_dir),
            'collectors_active': len(collectors),
            'collection_interval_seconds': {
                'system_metrics': 30,
                'git_activity': 60,
                'agent_interactions': 15,
                'task_completion': 300,
                'code_quality': 600
            }
        }
        
        with open(self.session_dir / 'session_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"🚀 All data collectors started successfully")
        print(f"📊 Data collection active for session: {self.session_id}")
        
    def stop_collection(self):
        """Stop all data collection"""
        self.collecting = False
        
        # Create session summary
        end_time = datetime.now(timezone.utc)
        duration = end_time - self.start_time
        
        summary = {
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration.total_seconds(),
            'data_files_created': len(list(self.session_dir.glob('*.jsonl'))),
            'session_directory': str(self.session_dir)
        }
        
        with open(self.session_dir / 'session_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"🛑 Data collection stopped")
        print(f"📈 Session duration: {duration}")
        print(f"📁 Data saved to: {self.session_dir}")

def main():
    """Main execution function"""
    print("🔬 Starting Empirical Data Collection System")
    print("=" * 50)
    
    collector = EmpiricalDataCollector()
    
    try:
        collector.start_collection()
        
        print("\n📊 Data collection is now active")
        print("Press Ctrl+C to stop collection and generate summary")
        
        # Keep main thread alive
        while True:
            time.sleep(60)
            print(f"📈 Data collection active... (Session: {collector.session_id[:8]})")
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping data collection...")
        collector.stop_collection()
        print("✅ Data collection completed successfully")
        
    except Exception as e:
        print(f"❌ Error in data collection: {e}")
        collector.stop_collection()

if __name__ == "__main__":
    main()