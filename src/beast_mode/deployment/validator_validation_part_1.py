
def validate_deployment(self, deployment_id: str, environment: str, level: ValidationLevel=ValidationLevel.STANDARD) -> ValidationReport:
    """Validate a deployment"""
    start_time = time.time()
    started_at = time.strftime('%Y-%m-%d %H:%M:%S')
    self.logger.info(f'Starting {level.value} validation for deployment {deployment_id}')
    config = self.config_manager.get_config(environment)
    results = []
    results.extend(self._validate_basic_connectivity(config))
    results.extend(self._validate_redis_connection(config))
    if level in [ValidationLevel.STANDARD, ValidationLevel.COMPREHENSIVE]:
        results.extend(self._validate_service_health(config))
        results.extend(self._validate_message_flow(config))
        results.extend(self._validate_configuration(config))
    if level == ValidationLevel.COMPREHENSIVE:
        results.extend(self._validate_performance(config))
        results.extend(self._validate_security(config))
        results.extend(self._validate_monitoring(config))
    end_time = time.time()
    completed_at = time.strftime('%Y-%m-%d %H:%M:%S')
    total_duration_ms = (end_time - start_time) * 1000
    passed_checks = sum((1 for r in results if r.passed))
    failed_checks = len(results) - passed_checks
    overall_passed = failed_checks == 0
    report = ValidationReport(deployment_id=deployment_id, environment=environment, validation_level=level, overall_passed=overall_passed, total_checks=len(results), passed_checks=passed_checks, failed_checks=failed_checks, results=results, started_at=started_at, completed_at=completed_at, total_duration_ms=total_duration_ms)
    self.logger.info(f'Validation completed: {passed_checks}/{len(results)} checks passed')
    return report
