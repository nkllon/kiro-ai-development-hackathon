#!/usr/bin/env python3
"""
Prometheus Integration Fix for Empirical Data Collection
Ensures Prometheus is properly collecting Beast Mode metrics
"""

import requests
import time
import json
from datetime import datetime
from prometheus_client import CollectorRegistry, Gauge, Counter, push_to_gateway, start_http_server
import threading

class PrometheusIntegrationFix:
    """Fix and enhance Prometheus integration for Beast Mode metrics"""
    
    def __init__(self):
        self.registry = CollectorRegistry()
        self.metrics_port = 8888
        self.prometheus_url = "http://localhost:9090"
        
        # Create Beast Mode metrics
        self.setup_beast_mode_metrics()
        
        print(f"🔧 Prometheus Integration Fix Initialized")
        print(f"📊 Metrics will be served on port {self.metrics_port}")
        
    def setup_beast_mode_metrics(self):
        """Setup Beast Mode specific metrics"""
        
        # Data collection metrics
        self.data_collection_active = Gauge(
            'beast_mode_data_collection_active',
            'Whether Beast Mode data collection is active',
            registry=self.registry
        )
        
        self.total_measurements = Counter(
            'beast_mode_total_measurements',
            'Total number of measurements collected',
            registry=self.registry
        )
        
        # System performance metrics
        self.cpu_usage = Gauge(
            'beast_mode_cpu_usage_percent',
            'Current CPU usage percentage',
            registry=self.registry
        )
        
        self.memory_usage = Gauge(
            'beast_mode_memory_usage_percent', 
            'Current memory usage percentage',
            registry=self.registry
        )
        
        self.kiro_processes = Gauge(
            'beast_mode_kiro_processes_count',
            'Number of active Kiro processes',
            registry=self.registry
        )
        
        # Development velocity metrics
        self.commits_per_hour = Gauge(
            'beast_mode_commits_per_hour',
            'Git commits per hour',
            registry=self.registry
        )
        
        self.tasks_completed = Counter(
            'beast_mode_tasks_completed_total',
            'Total tasks completed',
            registry=self.registry
        )
        
        self.code_quality_score = Gauge(
            'beast_mode_code_quality_score',
            'Current code quality score',
            registry=self.registry
        )
        
        # Agent effectiveness metrics
        self.agent_interactions = Counter(
            'beast_mode_agent_interactions_total',
            'Total agent interactions',
            registry=self.registry
        )
        
        self.agent_response_time = Gauge(
            'beast_mode_agent_response_time_seconds',
            'Average agent response time in seconds',
            registry=self.registry
        )
        
        print("✅ Beast Mode metrics configured")
        
    def check_prometheus_status(self):
        """Check if Prometheus is accessible"""
        try:
            response = requests.get(f"{self.prometheus_url}/api/v1/status/config", timeout=5)
            if response.status_code == 200:
                print("✅ Prometheus server is accessible")
                return True
            else:
                print(f"❌ Prometheus returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot reach Prometheus: {e}")
            return False
    
    def start_metrics_server(self):
        """Start HTTP server for metrics"""
        try:
            start_http_server(self.metrics_port, registry=self.registry)
            print(f"✅ Metrics server started on port {self.metrics_port}")
            print(f"📊 Metrics available at: http://localhost:{self.metrics_port}/metrics")
            return True
        except Exception as e:
            print(f"❌ Failed to start metrics server: {e}")
            return False
    
    def update_metrics_from_empirical_data(self):
        """Update Prometheus metrics from empirical data collection"""
        try:
            # Check if empirical data exists
            from pathlib import Path
            import json
            
            data_dir = Path("empirical_data")
            if not data_dir.exists():
                print("⚠️  No empirical data directory found")
                return
            
            # Find latest session
            session_dirs = [d for d in data_dir.iterdir() if d.is_dir() and d.name.startswith('session_')]
            if not session_dirs:
                print("⚠️  No session data found")
                return
            
            latest_session = max(session_dirs, key=lambda x: x.name)
            print(f"📊 Reading data from: {latest_session.name}")
            
            # Read system metrics
            system_metrics_file = latest_session / "system_metrics.jsonl"
            if system_metrics_file.exists():
                with open(system_metrics_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        latest_data = json.loads(lines[-1])
                        
                        # Update Prometheus metrics
                        self.cpu_usage.set(latest_data['system']['cpu_percent'])
                        self.memory_usage.set(latest_data['system']['memory_percent'])
                        self.kiro_processes.set(latest_data['processes']['kiro_processes'])
                        
                        print(f"✅ Updated system metrics: CPU={latest_data['system']['cpu_percent']:.1f}%, Memory={latest_data['system']['memory_percent']:.1f}%")
            
            # Read git activity
            git_file = latest_session / "git_activity.jsonl"
            if git_file.exists():
                with open(git_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        latest_data = json.loads(lines[-1])
                        self.commits_per_hour.set(latest_data.get('commits_last_minute', 0) * 60)  # Convert to hourly
                        
                        print(f"✅ Updated git metrics: Commits={latest_data.get('commits_last_minute', 0)}")
            
            # Read task completion
            task_file = latest_session / "task_completion.jsonl"
            if task_file.exists():
                with open(task_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        latest_data = json.loads(lines[-1])
                        self.tasks_completed._value._value = latest_data.get('completed_tasks', 0)
                        
                        # Calculate code quality score (simple heuristic)
                        completion_rate = latest_data.get('completion_rate', 0)
                        self.code_quality_score.set(completion_rate * 100)
                        
                        print(f"✅ Updated task metrics: Completed={latest_data.get('completed_tasks', 0)}, Rate={completion_rate:.2%}")
            
            # Mark data collection as active
            self.data_collection_active.set(1)
            self.total_measurements.inc()
            
        except Exception as e:
            print(f"❌ Error updating metrics: {e}")
    
    def continuous_metrics_update(self):
        """Continuously update metrics from empirical data"""
        while True:
            try:
                self.update_metrics_from_empirical_data()
                time.sleep(30)  # Update every 30 seconds
            except Exception as e:
                print(f"❌ Error in continuous update: {e}")
                time.sleep(60)
    
    def verify_prometheus_scraping(self):
        """Verify that Prometheus is scraping our metrics"""
        try:
            # Check if our metrics appear in Prometheus
            response = requests.get(f"{self.prometheus_url}/api/v1/label/__name__/values")
            if response.status_code == 200:
                metrics = response.json()['data']
                beast_mode_metrics = [m for m in metrics if m.startswith('beast_mode_')]
                
                if beast_mode_metrics:
                    print(f"✅ Prometheus is scraping {len(beast_mode_metrics)} Beast Mode metrics")
                    for metric in beast_mode_metrics[:5]:  # Show first 5
                        print(f"   📊 {metric}")
                    return True
                else:
                    print("⚠️  No Beast Mode metrics found in Prometheus")
                    return False
            else:
                print(f"❌ Failed to query Prometheus labels: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error verifying Prometheus scraping: {e}")
            return False
    
    def run_integration_fix(self):
        """Run the complete integration fix"""
        print("🔧 Starting Prometheus Integration Fix")
        print("=" * 50)
        
        # Check Prometheus status
        if not self.check_prometheus_status():
            print("❌ Prometheus is not accessible. Please ensure it's running.")
            return False
        
        # Start metrics server
        if not self.start_metrics_server():
            print("❌ Failed to start metrics server")
            return False
        
        # Wait a moment for server to start
        time.sleep(2)
        
        # Start continuous metrics updates
        update_thread = threading.Thread(target=self.continuous_metrics_update, daemon=True)
        update_thread.start()
        print("✅ Started continuous metrics updates")
        
        # Initial metrics update
        self.update_metrics_from_empirical_data()
        
        # Wait and verify scraping
        print("⏳ Waiting for Prometheus to scrape metrics...")
        time.sleep(10)
        
        if self.verify_prometheus_scraping():
            print("🎉 Prometheus integration is working!")
        else:
            print("⚠️  Prometheus may not be configured to scrape our metrics")
            print("💡 Add this to prometheus.yml scrape_configs:")
            print(f"   - job_name: 'beast-mode'")
            print(f"     static_configs:")
            print(f"       - targets: ['localhost:{self.metrics_port}']")
        
        return True

def main():
    """Main execution function"""
    print("🔧 Prometheus Integration Fix for Beast Mode")
    print("=" * 50)
    
    fixer = PrometheusIntegrationFix()
    
    try:
        if fixer.run_integration_fix():
            print("\n✅ Integration fix completed successfully")
            print("📊 Metrics are now being collected and served")
            print("🔄 Continuous updates are running")
            print("\nPress Ctrl+C to stop")
            
            # Keep running
            while True:
                time.sleep(60)
                print(f"📈 Metrics collection active... ({datetime.now().strftime('%H:%M:%S')})")
        else:
            print("❌ Integration fix failed")
    
    except KeyboardInterrupt:
        print("\n🛑 Stopping Prometheus integration...")
        print("✅ Integration fix completed")
    
    except Exception as e:
        print(f"❌ Error in integration fix: {e}")

if __name__ == "__main__":
    main()