
def _validate_performance(self, config: DeploymentConfig) -> List[ValidationResult]:
    """Performance validation"""
    results = []
    start_time = time.time()
    try:
        redis_client = redis.Redis(host=config.redis.host, port=config.redis.port, password=config.redis.password, db=config.redis.db, ssl=config.redis.ssl)
        operations = 100
        for i in range(operations):
            redis_client.set(f'perf_test_{i}', f'value_{i}')
            redis_client.get(f'perf_test_{i}')
            redis_client.delete(f'perf_test_{i}')
        duration_ms = (time.time() - start_time) * 1000
        ops_per_second = operations * 3 / (duration_ms / 1000)
        if ops_per_second > 1000:
            results.append(ValidationResult(name='Redis performance test', passed=True, message=f'Good performance: {ops_per_second:.0f} ops/sec', duration_ms=duration_ms, details={'ops_per_second': ops_per_second}))
        else:
            results.append(ValidationResult(name='Redis performance test', passed=False, message=f'Poor performance: {ops_per_second:.0f} ops/sec (expected >1000)', duration_ms=duration_ms, details={'ops_per_second': ops_per_second}))
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        results.append(ValidationResult(name='Redis performance test', passed=False, message=f'Performance test failed: {str(e)}', duration_ms=duration_ms))
    return results
