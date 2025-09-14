from src.rm_ddd.core.health import ModuleHealth

def _validate_message_flow(self, config: DeploymentConfig) -> List[ValidationResult]:
    """Message flow validation"""
    results = []
    start_time = time.time()
    try:
        redis_client = redis.Redis(host=config.redis.host, port=config.redis.port, password=config.redis.password, db=config.redis.db, ssl=config.redis.ssl)
        test_message = {'id': 'validation_test', 'type': 'simple_message', 'source': 'validator', 'payload': {'test': True}, 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')}
        result = redis_client.publish('beast_mode_network', json.dumps(test_message))
        duration_ms = (time.time() - start_time) * 1000
        if result > 0:
            results.append(ValidationResult(name='Message publishing', passed=True, message=f'Successfully published message to {result} subscribers', duration_ms=duration_ms))
        else:
            results.append(ValidationResult(name='Message publishing', passed=True, message='Message published successfully (no active subscribers)', duration_ms=duration_ms))
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        results.append(ValidationResult(name='Message publishing', passed=False, message=f'Message publishing failed: {str(e)}', duration_ms=duration_ms))
    return results
