from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


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

# Global enhanced registry instance
enhanced_registry = EnhancedInterfaceRegistry()
