from src.rm_ddd.core.health import ModuleHealth

def _handle_pdca_cycle_service(self, request: ServiceRequest) -> Dict[str, Any]:
    """
        Handle PDCA cycle service for systematic development workflow
        Implements UC-07: PDCA cycle service for GKE systematic development workflow
        """
    self.logger.info(f'Processing PDCA cycle service for team {request.gke_team_id}')
    task_description = request.parameters.get('task_description', '')
    project_context = request.project_context
    systematic_constraints = request.parameters.get('constraints', [])
    pdca_result = self.pdca_orchestrator.execute_pdca_cycle(task_description=task_description, project_context=project_context, constraints=systematic_constraints)
    gke_insights = self._generate_gke_insights(pdca_result, request)
    return {'pdca_execution': pdca_result, 'gke_insights': gke_insights, 'systematic_approach_validated': True, 'development_velocity_improvement': self._calculate_pdca_velocity_improvement(pdca_result), 'next_recommended_actions': self._generate_next_actions(pdca_result), 'service_type': 'pdca_cycle', 'team_id': request.gke_team_id}
