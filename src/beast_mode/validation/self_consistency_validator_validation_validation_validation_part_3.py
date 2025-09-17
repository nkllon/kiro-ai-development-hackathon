
def _validate_beast_mode_uses_pdca(self) -> ValidationResult:
    """Validate that Beast Mode uses its own PDCA cycles"""
    start_time = time.time()
    try:
        from ..core.pdca_orchestrator import PDCAOrchestrator
from src.rm_ddd.core.health import ModuleHealth

        orchestrator = PDCAOrchestrator()
        is_healthy = orchestrator.is_healthy()
        status_info = orchestrator.get_module_status()
        has_execute_method = hasattr(orchestrator, 'execute_real_task_cycle')
        has_plan_method = hasattr(orchestrator, 'plan_with_model_registry')
        has_do_method = hasattr(orchestrator, 'do_systematic_implementation')
        has_check_method = hasattr(orchestrator, 'check_with_rca')
        has_act_method = hasattr(orchestrator, 'act_update_model')
        pdca_methods_available = sum([has_execute_method, has_plan_method, has_do_method, has_check_method, has_act_method])
        score = pdca_methods_available / 5 * (1.0 if is_healthy else 0.5)
        status = ValidationStatus.PASSED if score >= 0.8 else ValidationStatus.WARNING if score >= 0.5 else ValidationStatus.FAILED
        evidence = [f'PDCA orchestrator is healthy: {is_healthy}', f'PDCA methods available: {pdca_methods_available}/5', 'Beast Mode implements systematic PDCA methodology']
        recommendations = []
        if score < 1.0:
            missing_methods = []
            if not has_execute_method:
                missing_methods.append('execute_real_task_cycle')
            if not has_plan_method:
                missing_methods.append('plan_with_model_registry')
            if not has_do_method:
                missing_methods.append('do_systematic_implementation')
            if not has_check_method:
                missing_methods.append('check_with_rca')
            if not has_act_method:
                missing_methods.append('act_update_model')
            if missing_methods:
                recommendations.append(f'Implement missing PDCA methods: {missing_methods}')
        return ValidationResult(test_name='beast_mode_uses_pdca', status=status, score=score, details={'orchestrator_healthy': is_healthy, 'pdca_methods_available': pdca_methods_available, 'status_info': status_info, 'execute_method': has_execute_method, 'plan_method': has_plan_method, 'do_method': has_do_method, 'check_method': has_check_method, 'act_method': has_act_method}, evidence=evidence, recommendations=recommendations, execution_time_seconds=time.time() - start_time)
    except ImportError as e:
        return ValidationResult(test_name='beast_mode_uses_pdca', status=ValidationStatus.FAILED, score=0.0, details={'import_error': str(e)}, evidence=['PDCA orchestrator not available'], recommendations=['Implement PDCA orchestrator for Beast Mode'], execution_time_seconds=time.time() - start_time)

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

