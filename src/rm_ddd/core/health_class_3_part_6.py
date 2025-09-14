
class InitClass:
    """Auto-generated class for functions."""

    def __init__(self, module: 'ReflectiveModuleBase'):
    """
    Initialize health monitor for a specific module.

    Args:
    module: The RM module to monitor
    """
    self.module = module
    self.module_id = module.module_id
    self._health_history: List[ModuleHealth] = []
    self._health_indicators: Dict[str, HealthIndicator] = {}
    self._monitoring_active = False
    self._monitoring_task: Optional[asyncio.Task] = None
    self._check_interval = timedelta(seconds=30)
    logger.info(f'HealthMonitor initialized for module: {self.module_id}')

    async def start_monitoring(self, check_interval: Optional[timedelta]=None):
    """
    Start periodic health monitoring.

    Args:
    check_interval: How often to perform health checks
    """
    if self._monitoring_active:
    logger.warning(f'Health monitoring already active for {self.module_id}')
    return
    if check_interval:
    self._check_interval = check_interval
    self._monitoring_active = True
    self._monitoring_task = asyncio.create_task(self._monitoring_loop())
    logger.info(f'Health monitoring started for {self.module_id} with {self._check_interval} interval')

    async def stop_monitoring(self):
    """Stop periodic health monitoring."""
    if not self._monitoring_active:
    return
    self._monitoring_active = False
    if self._monitoring_task:
    self._monitoring_task.cancel()
    try:
    await self._monitoring_task
    except asyncio.CancelledError:
    pass
    logger.info(f'Health monitoring stopped for {self.module_id}')

    async def _monitoring_loop(self):
    """Main monitoring loop."""
    try:
    while self._monitoring_active:
    try:
    health_status = await self.module.perform_health_check()
    await self.update_health_status(health_status)
    await asyncio.sleep(self._check_interval.total_seconds())
    except asyncio.CancelledError:
    break
    except Exception as e:
    logger.error(f'Error in health monitoring loop for {self.module_id}: {e}')
    await asyncio.sleep(5)
    except asyncio.CancelledError:
    logger.info(f'Health monitoring loop cancelled for {self.module_id}')

    async def update_health_status(self, health_status: ModuleHealth):
    """
    Update health status and maintain history.

    Args:
    health_status: New health status to record
    """
    self._health_history.append(health_status)
    if len(self._health_history) > 100:
    self._health_history = self._health_history[-100:]
    await self._update_health_indicators(health_status)
    if len(self._health_history) > 1:
    previous_status = self._health_history[-2]
    if previous_status.status != health_status.status:
    logger.info(f'Health status changed for {self.module_id}: {previous_status.status.value} -> {health_status.status.value}')

    async def _update_health_indicators(self, health_status: ModuleHealth):
    """Update health indicators based on current status."""
    timestamp = datetime.now()
    self._health_indicators['status'] = HealthIndicator(name='status', status=health_status.status.value, value=health_status.status.value, message=health_status.message, timestamp=timestamp)
    if health_status.performance_metrics:
    metrics = health_status.performance_metrics
    self._health_indicators['response_time'] = HealthIndicator(name='response_time', status='healthy' if metrics.response_time_ms < 100 else 'degraded', value=metrics.response_time_ms, threshold=100.0, message=f'Response time: {metrics.response_time_ms:.2f}ms', timestamp=timestamp)
    self._health_indicators['error_rate'] = HealthIndicator(name='error_rate', status='healthy' if metrics.error_rate < 0.01 else 'degraded', value=metrics.error_rate, threshold=0.01, message=f'Error rate: {metrics.error_rate:.2%}', timestamp=timestamp)
    self._health_indicators['cpu_usage'] = HealthIndicator(name='cpu_usage', status='healthy' if metrics.cpu_usage_percent < 80 else 'degraded', value=metrics.cpu_usage_percent, threshold=80.0, message=f'CPU usage: {metrics.cpu_usage_percent:.1f}%', timestamp=timestamp)
    self._health_indicators['memory_usage'] = HealthIndicator(name='memory_usage', status='healthy' if metrics.memory_usage_mb < 1000 else 'degraded', value=metrics.memory_usage_mb, threshold=1000.0, message=f'Memory usage: {metrics.memory_usage_mb:.1f}MB', timestamp=timestamp)
    if health_status.domain_health:
    domain_health = health_status.domain_health
    self._health_indicators['domain_boundary_integrity'] = HealthIndicator(name='domain_boundary_integrity', status='healthy' if domain_health.boundary_integrity else 'unhealthy', value=domain_health.boundary_integrity, message=f"Domain boundary integrity: {('OK' if domain_health.boundary_integrity else 'VIOLATED')}", timestamp=timestamp)
    self._health_indicators['domain_invariant_compliance'] = HealthIndicator(name='domain_invariant_compliance', status='healthy' if domain_health.invariant_compliance else 'unhealthy', value=domain_health.invariant_compliance, message=f"Domain invariant compliance: {('OK' if domain_health.invariant_compliance else 'VIOLATED')}", timestamp=timestamp)
    self._health_indicators['domain_complexity'] = HealthIndicator(name='domain_complexity', status='healthy' if domain_health.complexity_score < 0.8 else 'warning', value=domain_health.complexity_score, threshold=0.8, message=f'Domain complexity score: {domain_health.complexity_score:.2f}', timestamp=timestamp)

    async def get_current_health(self) -> Optional[ModuleHealth]:
    """Get the most recent health status."""
    if not self._health_history:
    return None
    return self._health_history[-1]

    async def get_health_history(self, limit: int=10) -> List[ModuleHealth]:
    """
    Get recent health history.

    Args:
    limit: Maximum number of health records to return

    Returns:
    List of recent health records, most recent first
    """
    return list(reversed(self._health_history[-limit:]))

    async def get_health_indicators(self) -> Dict[str, HealthIndicator]:
    """Get current health indicators."""
    return self._health_indicators.copy()

    async def get_health_summary(self) -> Dict[str, Any]:
    """Get comprehensive health summary."""
    current_health = await self.get_current_health()
    if not current_health:
    return {'module_id': self.module_id, 'status': 'unknown', 'message': 'No health data available'}
    health_trend = self._calculate_health_trend()
    return {'module_id': self.module_id, 'current_status': current_health.status.value, 'is_healthy': current_health.is_healthy, 'message': current_health.message, 'health_trend': health_trend, 'health_indicators': {name: {'status': indicator.status, 'value': indicator.value, 'message': indicator.message} for name, indicator in self._health_indicators.items()}, 'domain_health': current_health.domain_health.to_dict() if current_health.domain_health else None, 'last_check': current_health.timestamp.isoformat(), 'monitoring_active': self._monitoring_active}

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

