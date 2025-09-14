from src.rm_ddd.core.health import ModuleHealth

def _validate_redis_connection(self, config: DeploymentConfig) -> List[ValidationResult]:
    """Redis connection validation"""
    results = []
    start_time = time.time()
    try:
        redis_client = redis.Redis(host=config.redis.host, port=config.redis.port, password=config.redis.password, db=config.redis.db, ssl=config.redis.ssl, socket_timeout=5)
        redis_client.ping()
        test_key = 'beast_mode_validation_test'
        redis_client.set(test_key, 'test_value', ex=60)
        value = redis_client.get(test_key)
        redis_client.delete(test_key)
        duration_ms = (time.time() - start_time) * 1000
        if value == b'test_value':
            results.append(ValidationResult(name='Redis connection and operations', passed=True, message='Redis connection successful, basic operations working', duration_ms=duration_ms, details={'host': config.redis.host, 'port': config.redis.port}))
        else:
            results.append(ValidationResult(name='Redis connection and operations', passed=False, message='Redis operations failed - value mismatch', duration_ms=duration_ms))
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        results.append(ValidationResult(name='Redis connection and operations', passed=False, message=f'Redis connection failed: {str(e)}', duration_ms=duration_ms))
    start_time = time.time()
    try:
        redis_client = redis.Redis(host=config.redis.host, port=config.redis.port, password=config.redis.password, db=config.redis.db, ssl=config.redis.ssl)
        pubsub = redis_client.pubsub()
        test_channel = 'beast_mode_validation_channel'
        pubsub.subscribe(test_channel)
        message = pubsub.get_message(timeout=5)
        if message and message['type'] == 'subscribe':
            redis_client.publish(test_channel, 'test_message')
            message = pubsub.get_message(timeout=5)
            if message and message['type'] == 'message':
                duration_ms = (time.time() - start_time) * 1000
                results.append(ValidationResult(name='Redis pub/sub functionality', passed=True, message='Redis pub/sub working correctly', duration_ms=duration_ms))
            else:
                duration_ms = (time.time() - start_time) * 1000
                results.append(ValidationResult(name='Redis pub/sub functionality', passed=False, message='Failed to receive pub/sub message', duration_ms=duration_ms))
        else:
            duration_ms = (time.time() - start_time) * 1000
            results.append(ValidationResult(name='Redis pub/sub functionality', passed=False, message='Failed to subscribe to channel', duration_ms=duration_ms))
        pubsub.close()
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        results.append(ValidationResult(name='Redis pub/sub functionality', passed=False, message=f'Redis pub/sub test failed: {str(e)}', duration_ms=duration_ms))
    return results

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

