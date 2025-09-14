from src.rm_ddd.core.registry import register_module
class EnhancedInterfaceRegistry(InterfaceRegistry, ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """Enhanced Interface Registry with advanced features"""
    
    def __init__(self, registry_file: str = "enhanced_interface_registry.json"):
        super().__init__(registry_file)
        self.metrics: Dict[str, InterfaceMetrics] = {}
        self.cache: Dict[str, Any] = {}
        self.load_metrics()
    
    def load_metrics(self):
        """Load interface metrics from storage"""
        metrics_file = self.registry_file.replace('.json', '_metrics.json')
        if os.path.exists(metrics_file):
            try:
                with open(metrics_file, 'r') as f:
                    data = json.load(f)
                for interface_id, metrics_data in data.items():
                    self.metrics[interface_id] = InterfaceMetrics(**metrics_data)
            except Exception as e:
                print(f"Warning: Could not load metrics: {e}")
    
    def save_metrics(self):
        """Save interface metrics to storage"""
        metrics_file = self.registry_file.replace('.json', '_metrics.json')
        try:
            data = {
                interface_id: {
                    'interface_id': metrics.interface_id,
                    'usage_count': metrics.usage_count,
                    'last_accessed': metrics.last_accessed.isoformat(),
                    'performance_score': metrics.performance_score,
                    'error_count': metrics.error_count,
                    'success_rate': metrics.success_rate
                }
                for interface_id, metrics in self.metrics.items()
            }
            with open(metrics_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving metrics: {e}")
    
    def register_interface(self, interface: InterfaceMetadata) -> bool:
        """Enhanced interface registration with metrics"""
        success = super().register_interface(interface)
        if success:
            # Initialize metrics for new interface
            self.metrics[interface.interface_id] = InterfaceMetrics(
                interface_id=interface.interface_id,
                usage_count=0,
                last_accessed=datetime.now(),
                performance_score=1.0,
                error_count=0,
                success_rate=1.0
            )
            self.save_metrics()
        return success
    
    def track_interface_usage(self, interface_id: str, success: bool = True):
        """Track interface usage for metrics"""
        if interface_id in self.metrics:
            metrics = self.metrics[interface_id]
            metrics.usage_count += 1
            metrics.last_accessed = datetime.now()
            
            if success:
                metrics.success_rate = (metrics.success_rate * (metrics.usage_count - 1) + 1.0) / metrics.usage_count
            else:
                metrics.error_count += 1
                metrics.success_rate = (metrics.success_rate * (metrics.usage_count - 1) + 0.0) / metrics.usage_count
            
            self.save_metrics()
    
    def get_interface_performance_report(self) -> Dict[str, Any]:
        """Generate interface performance report"""
        if not self.metrics:
            return {"message": "No metrics available"}
        
        total_interfaces = len(self.metrics)
        total_usage = sum(metrics.usage_count for metrics in self.metrics.values())
        avg_success_rate = sum(metrics.success_rate for metrics in self.metrics.values()) / total_interfaces
        
        # Top performing interfaces
        top_performers = sorted(
            self.metrics.values(),
            key=lambda x: x.performance_score * x.success_rate,
            reverse=True
        )[:5]
        
        # Most used interfaces
        most_used = sorted(
            self.metrics.values(),
            key=lambda x: x.usage_count,
            reverse=True
        )[:5]
        
        return {
            'total_interfaces': total_interfaces,
            'total_usage': total_usage,
            'average_success_rate': round(avg_success_rate, 3),
            'top_performers': [
                {
                    'interface_id': metrics.interface_id,
                    'performance_score': metrics.performance_score,
                    'success_rate': metrics.success_rate,
                    'usage_count': metrics.usage_count
                }
                for metrics in top_performers
            ],
            'most_used': [
                {
                    'interface_id': metrics.interface_id,
                    'usage_count': metrics.usage_count,
                    'last_accessed': metrics.last_accessed.isoformat()
                }
                for metrics in most_used
            ]
        }
    
    def optimize_interface_cache(self):
        """Optimize interface cache based on usage patterns"""
        # Clear cache for unused interfaces
        current_time = datetime.now()
        for interface_id, metrics in self.metrics.items():
            # Remove from cache if not used in last 24 hours
            time_diff = (current_time - metrics.last_accessed).total_seconds()
            if time_diff > 86400 and interface_id in self.cache:
                del self.cache[interface_id]
        
        # Pre-load cache for frequently used interfaces
        for interface_id, metrics in self.metrics.items():
            if metrics.usage_count > 10 and interface_id not in self.cache:
                if interface_id in self.interfaces:
                    self.cache[interface_id] = self.interfaces[interface_id]
    
    def get_interface_recommendations(self, context: str) -> List[Dict[str, Any]]:
        """Get interface recommendations based on context and usage patterns"""
        recommendations = []
        
        # Find interfaces with high success rates and good performance
        for interface_id, metrics in self.metrics.items():
            if metrics.success_rate > 0.9 and metrics.performance_score > 0.8:
                if interface_id in self.interfaces:
                    interface = self.interfaces[interface_id]
                    recommendations.append({
                        'interface_id': interface_id,
                        'interface_name': interface.interface_name,
                        'interface_type': interface.interface_type.value,
                        'description': interface.description,
                        'success_rate': metrics.success_rate,
                        'usage_count': metrics.usage_count,
                        'recommendation_score': metrics.performance_score * metrics.success_rate
                    })
        
        # Sort by recommendation score
        recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
        return recommendations[:10]

        register_module(self.__class__.__name__, self)
# Global enhanced registry instance
enhanced_registry = EnhancedInterfaceRegistry()
