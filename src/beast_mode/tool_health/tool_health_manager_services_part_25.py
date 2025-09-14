
    def get_health_indicators(self) -> List[Dict[str, Any]]:
        """Get detailed health indicators"""
        indicators = []
        if self.repair_history:
            successful_repairs = len([r for r in self.repair_history if r.repair_successful])
            success_rate = successful_repairs / len(self.repair_history)
            indicators.append({'name': 'repair_performance', 'status': 'healthy' if success_rate >= 0.8 else 'degraded' if success_rate >= 0.6 else 'unhealthy', 'success_rate': success_rate, 'repairs_performed': len(self.repair_history)})
        indicators.append({'name': 'monitoring_health', 'status': 'healthy' if self.monitored_tools else 'not_monitoring', 'tools_monitored': len(self.monitored_tools)})
        indicators.append({'name': 'fix_tools_first_principle', 'status': 'active', 'principle_applied': len(self.repair_history) > 0, 'systematic_repairs': len([r for r in self.repair_history if r.repair_successful])})
        return indicators
