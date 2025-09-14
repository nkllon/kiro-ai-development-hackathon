from src.rm_ddd.core.health import ModuleHealth

    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information"""
        return {'module_id': self.module_id, 'version': self.version, 'name': 'Multi-Agent Collaboration Model', 'description': 'RDI/RM-DDD compliant model for AI agent collaboration and human amplification', 'author': 'Beast Mode Development Team', 'created_at': self._start_time.isoformat(), 'interface_version': self.get_interface_version(), 'requirements_traceability': len(self.requirements_traceability), 'active_agents': len(self.agents), 'collaborations_completed': len(self.collaboration_history), 'conflicts_resolved': len(self.conflict_resolution_history)}
