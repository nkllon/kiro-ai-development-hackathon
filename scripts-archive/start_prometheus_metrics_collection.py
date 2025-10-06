#!/usr/bin/env python3
"""
Start Prometheus Metrics Collection
==================================

Starts the Beast Mode Prometheus exporter and DAG orchestration metrics
collection to ensure data is available for Grafana dashboards.

Author: Beast Mode Framework
Date: 2025-01-27
"""

import sys
import time
import threading
import asyncio
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.beast_mode.monitoring.prometheus_exporter import PrometheusExporter
from src.dag_orchestration.infrastructure.precondition_validator import InfrastructurePreconditionValidator
from src.dag_orchestration.core.infrastructure_validator import InfrastructureValidator
from src.dag_orchestration.execution.parallel_execution_engine import ParallelExecutionEngine, TaskDefinition


class MetricsCollectionManager:
    """Manages Prometheus metrics collection for DAG orchestration components."""
    
    def __init__(self):
        self.prometheus_exporter = None
        self.components = []
        self.metrics_active = False
        self.collection_thread = None
        
    def initialize_prometheus_exporter(self) -> bool:
        """Initialize the Prometheus exporter."""
        try:
            print("🚀 Initializing Prometheus Exporter...")
            
            # Create Prometheus exporter bound to network interface
            self.prometheus_exporter = PrometheusExporter(
                port=9090,  # Standard Prometheus port
                monitoring_interval=5.0,
                enable_http_server=True
            )
            
            print("✅ Prometheus exporter initialized")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize Prometheus exporter: {e}")
            return False
    
    def create_dag_orchestration_components(self) -> bool:
        """Create DAG orchestration components to generate metrics."""
        try:
            print("🔧 Creating DAG orchestration components...")
            
            # Create infrastructure validator
            infra_validator = InfrastructurePreconditionValidator()
            self.components.append(("InfrastructurePreconditionValidator", infra_validator))
            
            # Create infrastructure validator
            validator = InfrastructureValidator()
            self.components.append(("InfrastructureValidator", validator))
            
            # Create parallel execution engine
            engine = ParallelExecutionEngine(max_workers=4)
            self.components.append(("ParallelExecutionEngine", engine))
            
            print(f"✅ Created {len(self.components)} DAG orchestration components")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create components: {e}")
            return False
    
    async def generate_sample_metrics(self) -> bool:
        """Generate sample metrics by exercising the components."""
        try:
            print("📊 Generating sample metrics...")
            
            for name, component in self.components:
                print(f"   🔍 Exercising {name}...")
                
                # Get health status (generates health metrics)
                health = component.get_health_status()
                print(f"      Health: {health.status.value} (Score: {health.health_score})")
                
                # Get module info (generates module metrics)
                module_info = component.get_module_info()
                print(f"      Module: {module_info['name']} v{module_info['version']}")
                
                # Exercise specific component functionality
                if isinstance(component, InfrastructurePreconditionValidator):
                    # Run validation to generate metrics
                    report = await component.validate_all_preconditions()
                    print(f"      Validation: {'PASSED' if report.overall_status else 'FAILED'}")
                
                elif isinstance(component, InfrastructureValidator):
                    # Run execution validation
                    requirements = {'sample_execution': True, 'parallel_tasks': 3}
                    validation_passed, report = await component.validate_for_execution(requirements)
                    print(f"      Execution Validation: {'PASSED' if validation_passed else 'FAILED'}")
                
                elif isinstance(component, ParallelExecutionEngine):
                    # Run sample parallel execution
                    tasks = [
                        TaskDefinition(
                            task_id=f"sample_task_{i}",
                            name=f"Sample Task {i}",
                            execution_function=lambda x=i: f"Task {x} completed",
                            dependencies=set()
                        )
                        for i in range(3)
                    ]
                    
                    results = await component.execute_dag_parallel(tasks)
                    completed = sum(1 for r in results.values() if r.status.value == 'completed')
                    print(f"      Parallel Execution: {completed}/{len(tasks)} tasks completed")
                
                # Small delay between components
                await asyncio.sleep(1)
            
            print("✅ Sample metrics generated successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate sample metrics: {e}")
            return False
    
    def start_continuous_metrics_collection(self) -> bool:
        """Start continuous metrics collection."""
        try:
            print("🔄 Starting continuous metrics collection...")
            
            self.metrics_active = True
            
            def metrics_loop():
                """Continuous metrics collection loop."""
                while self.metrics_active:
                    try:
                        # Update component metrics
                        for name, component in self.components:
                            # Trigger health status update (generates metrics)
                            health = component.get_health_status()
                            
                            # Update activity timestamp
                            if hasattr(component, '_update_activity'):
                                component._update_activity()
                        
                        # Wait before next collection
                        time.sleep(10)  # Collect every 10 seconds
                        
                    except Exception as e:
                        print(f"⚠️ Metrics collection error: {e}")
                        time.sleep(5)
            
            # Start metrics collection thread
            self.collection_thread = threading.Thread(target=metrics_loop, daemon=True)
            self.collection_thread.start()
            
            print("✅ Continuous metrics collection started")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start metrics collection: {e}")
            return False
    
    def verify_metrics_endpoint(self) -> bool:
        """Verify that metrics are available at the Prometheus endpoint."""
        try:
            import requests
            
            print("🧪 Verifying metrics endpoint...")
            
            # Test local metrics endpoint
            local_url = "http://localhost:9090/metrics"
            response = requests.get(local_url, timeout=5)
            
            if response.status_code == 200:
                metrics_text = response.text
                
                # Check for Beast Mode metrics
                beast_mode_metrics = [line for line in metrics_text.split('\n') if 'beast_mode' in line]
                
                print(f"✅ Metrics endpoint accessible")
                print(f"✅ Found {len(beast_mode_metrics)} Beast Mode metrics")
                
                # Show sample metrics
                if beast_mode_metrics:
                    print("📊 Sample metrics:")
                    for metric in beast_mode_metrics[:5]:  # Show first 5
                        if not metric.startswith('#'):  # Skip comments
                            print(f"   {metric}")
                
                return True
            else:
                print(f"❌ Metrics endpoint returned: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error verifying metrics endpoint: {e}")
            return False
    
    def stop_metrics_collection(self):
        """Stop metrics collection."""
        print("🛑 Stopping metrics collection...")
        self.metrics_active = False
        
        if self.collection_thread and self.collection_thread.is_alive():
            self.collection_thread.join(timeout=5)
        
        # Shutdown components
        for name, component in self.components:
            if hasattr(component, 'shutdown'):
                component.shutdown()
        
        print("✅ Metrics collection stopped")


async def main():
    """Main execution function."""
    print("📊 Prometheus Metrics Collection Starter")
    print("=" * 50)
    print("This will start Beast Mode Prometheus metrics collection")
    print("for DAG orchestration components to populate Grafana dashboards.")
    print("=" * 50)
    
    manager = MetricsCollectionManager()
    
    try:
        # Initialize Prometheus exporter
        if not manager.initialize_prometheus_exporter():
            return False
        
        # Create components
        if not manager.create_dag_orchestration_components():
            return False
        
        # Generate initial metrics
        if not await manager.generate_sample_metrics():
            return False
        
        # Start continuous collection
        if not manager.start_continuous_metrics_collection():
            return False
        
        # Verify metrics endpoint
        time.sleep(2)  # Give metrics a moment to be collected
        if not manager.verify_metrics_endpoint():
            print("⚠️ Metrics endpoint verification failed, but continuing...")
        
        print(f"\n🚀 SUCCESS!")
        print(f"✅ Prometheus metrics collection is now active")
        print(f"✅ Metrics available at: http://localhost:9090/metrics")
        print(f"✅ Public endpoint: https://prometheus.observatory.nkllon.com/metrics")
        print(f"\n💡 Next steps:")
        print(f"   1. Check Grafana: https://grafana.observatory.nkllon.com")
        print(f"   2. Verify data sources are working")
        print(f"   3. Create/import dashboards for DAG orchestration metrics")
        print(f"\n⏳ Metrics collection will continue running...")
        print(f"   Press Ctrl+C to stop")
        
        # Keep running until interrupted
        try:
            while True:
                await asyncio.sleep(10)
                print(f"📊 Metrics collection active... ({time.strftime('%H:%M:%S')})")
        except KeyboardInterrupt:
            print(f"\n⚠️ Stopping metrics collection...")
            manager.stop_metrics_collection()
            return True
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        manager.stop_metrics_collection()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)