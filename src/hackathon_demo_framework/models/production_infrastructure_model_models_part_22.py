from src.rm_ddd.core.health import ModuleHealth

    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information"""
        return {'module_id': self.module_id, 'version': self.version, 'name': 'Production Infrastructure Model', 'description': 'RDI/RM-DDD compliant model for enterprise-grade infrastructure demonstration', 'author': 'Beast Mode Development Team', 'created_at': self._start_time.isoformat(), 'interface_version': self.get_interface_version(), 'requirements_traceability': len(self.requirements_traceability), 'deployments_completed': len(self.deployment_history), 'cost_optimizations': len(self.cost_optimization_history), 'security_validations': len(self.security_validation_history)}
