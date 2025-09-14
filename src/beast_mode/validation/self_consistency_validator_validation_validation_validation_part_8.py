
def _validate_health_monitoring(self) -> ValidationResult:
    """Validate that Beast Mode components provide health monitoring"""
    start_time = time.time()
    try:
        healthy_components = 0
        total_tested = 0
        health_details = {}
        key_components = [('core.reflective_module', 'ReflectiveModule'), ('analysis.rca_engine', 'RCAEngine'), ('tool_health.makefile_health_manager', 'MakefileHealthManager'), ('quality.automated_quality_gates', 'AutomatedQualityGates')]
        for component_path, class_name in key_components:
            try:
                module_path = f'src.beast_mode.{component_path}'
                module = __import__(module_path, fromlist=[class_name])
                component_class = getattr(module, class_name)
                if class_name == 'ReflectiveModule':
                    continue
                instance = component_class()
                total_tested += 1
                is_healthy = instance.is_healthy()
                status_info = instance.get_module_status()
                health_indicators = instance.get_health_indicators()
                if is_healthy and status_info and health_indicators:
                    healthy_components += 1
                health_details[component_path] = {'healthy': is_healthy, 'has_status': bool(status_info), 'has_indicators': bool(health_indicators), 'status_keys': list(status_info.keys()) if status_info else []}
            except Exception as e:
                health_details[component_path] = {'healthy': False, 'error': str(e)}
                total_tested += 1
        score = healthy_components / max(1, total_tested)
        status = ValidationStatus.PASSED if score >= 0.8 else ValidationStatus.WARNING if score >= 0.5 else ValidationStatus.FAILED
        evidence = [f'Healthy components: {healthy_components}/{total_tested}', 'Components provide comprehensive health monitoring', 'Health indicators available for operational visibility']
        recommendations = []
        if score < 1.0:
            unhealthy = [comp for comp, details in health_details.items() if not details.get('healthy', False)]
            recommendations.append(f'Fix health monitoring for: {unhealthy}')
        return ValidationResult(test_name='health_monitoring', status=status, score=score, details={'healthy_components': healthy_components, 'total_tested': total_tested, 'health_details': health_details}, evidence=evidence, recommendations=recommendations, execution_time_seconds=time.time() - start_time)
    except Exception as e:
        return ValidationResult(test_name='health_monitoring', status=ValidationStatus.FAILED, score=0.0, details={'validation_error': str(e)}, evidence=['Health monitoring validation failed'], recommendations=['Fix health monitoring validation'], execution_time_seconds=time.time() - start_time)
