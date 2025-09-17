from src.rm_ddd.core.registry import register_module
class OperatorSafetyManager(ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """Main safety management system - Coordinates all safety measures"""

    def __init__(self, limits: Optional[ResourceLimits]=None):
        register_module(self.__class__.__name__, self)
        self.limits = limits or ResourceLimits()
        self.kill_switch = KillSwitch()
        self.resource_monitor = ResourceMonitor(self.limits)
        self.safety_validator = SafetyValidator()
        self.logger = logging.getLogger('rm_rdi_analysis.safety_manager')
        self.is_safe_mode = True
        self.analysis_allowed = True
        self.emergency_shutdown_triggered = False
        self.kill_switch.register_shutdown_callback(self._emergency_shutdown_callback)
        self.resource_monitor.register_violation_callback(self._resource_violation_callback)

    def initialize_safety_systems(self) -> bool:
        """Initialize all safety systems"""
        try:
            self.logger.info('Initializing operator safety systems...')
            self.resource_monitor.start_monitoring()
            if not self._validate_initial_safety():
                self.logger.error('Initial safety validation failed')
                return False
            self.logger.info('Safety systems initialized successfully')
            return True
        except Exception as e:
            self.logger.error(f'Failed to initialize safety systems: {e}')
            return False

    def shutdown_safety_systems(self) -> None:
        """Shutdown all safety systems"""
        self.logger.info('Shutting down safety systems...')
        self.resource_monitor.stop_monitoring()
        self.logger.info('Safety systems shutdown complete')

    def get_safety_status(self) -> SafetyStatus:
        """Get current safety status"""
        violations = self.resource_monitor.check_limits()
        usage = self.resource_monitor.get_current_usage()
        return SafetyStatus(is_safe=len(violations) == 0 and (not self.emergency_shutdown_triggered), resource_usage=usage, violations=violations, last_check=datetime.now(), kill_switch_armed=self.kill_switch.is_armed)

    def is_operation_safe(self, operation_name: str) -> bool:
        """Check if an operation is safe to perform"""
        if self.emergency_shutdown_triggered:
            self.logger.warning(f'Operation {operation_name} blocked - emergency shutdown active')
            return False
        if not self.analysis_allowed:
            self.logger.warning(f'Operation {operation_name} blocked - analysis disabled')
            return False
        violations = self.resource_monitor.check_limits()
        if violations:
            self.logger.warning(f'Operation {operation_name} blocked - resource violations: {violations}')
            return False
        return True

    def emergency_shutdown(self, reason: str='Operator request') -> None:
        """Trigger emergency shutdown"""
        self.emergency_shutdown_triggered = True
        self.analysis_allowed = False
        self.kill_switch.emergency_shutdown(reason)

    def _validate_initial_safety(self) -> bool:
        """Validate initial safety conditions"""
        if os.getuid() == 0:
            self.logger.error('SAFETY VIOLATION: Running as root user')
            return False
        if self.limits.max_cpu_percent > 50:
            self.logger.warning('CPU limit >50% may impact system performance')
        return True

    def _emergency_shutdown_callback(self) -> None:
        """Callback for emergency shutdown"""
        self.emergency_shutdown_triggered = True
        self.analysis_allowed = False
        self.logger.critical('Emergency shutdown callback executed')

    def _resource_violation_callback(self, violations: List[str]) -> None:
        """Callback for resource violations"""
        self.logger.warning(f'Resource violations detected: {violations}')
        for violation in violations:
            if 'CPU usage' in violation and 'exceeds limit' in violation:
                try:
                    cpu_str = violation.split('CPU usage ')[1].split('%')[0]
                    cpu_percent = float(cpu_str)
                    if cpu_percent > self.limits.max_cpu_percent * 2:
                        self.emergency_shutdown('Severe CPU usage violation')
                        return
                except:
                    pass
            if 'Memory usage' in violation and 'exceeds limit' in violation:
                try:
                    mem_str = violation.split('Memory usage ')[1].split('MB')[0]
                    mem_mb = float(mem_str)
                    if mem_mb > self.limits.max_memory_mb * 2:
                        self.emergency_shutdown('Severe memory usage violation')
                        return
                except:
                    pass

    def validate_workflow_safety(self, workflow_id: str, workflow_config: Dict[str, Any]=None) -> bool:
        """Validate that a workflow is safe to execute"""
        if workflow_config is None:
            workflow_config = {}
        self.logger.info(f'Validating workflow safety: {workflow_id}')
        if self.emergency_shutdown_triggered:
            self.logger.warning(f'Workflow {workflow_id} blocked - emergency shutdown active')
            return False
        if not self.analysis_allowed:
            self.logger.warning(f'Workflow {workflow_id} blocked - analysis disabled')
            return False
        try:
            max_memory = workflow_config.get('max_memory_mb', 0)
            max_cpu = workflow_config.get('max_cpu_percent', 0)
            timeout = workflow_config.get('timeout_seconds', 300)
            if max_memory > self.limits.max_memory_mb:
                self.logger.warning(f'Workflow {workflow_id} memory requirement ({max_memory}MB) exceeds limit ({self.limits.max_memory_mb}MB)')
                return False
            if max_cpu > self.limits.max_cpu_percent:
                self.logger.warning(f'Workflow {workflow_id} CPU requirement ({max_cpu}%) exceeds limit ({self.limits.max_cpu_percent}%)')
                return False
            if timeout > self.limits.max_analysis_time_seconds:
                self.logger.warning(f'Workflow {workflow_id} timeout ({timeout}s) exceeds limit ({self.limits.max_analysis_time_seconds}s)')
                return False
            current_usage = self.resource_monitor.get_current_usage()
            if current_usage.get('cpu_percent', 0) + max_cpu > self.limits.max_cpu_percent:
                self.logger.warning(f'Workflow {workflow_id} would exceed CPU limits with current usage')
                return False
            if current_usage.get('memory_mb', 0) + max_memory > self.limits.max_memory_mb:
                self.logger.warning(f'Workflow {workflow_id} would exceed memory limits with current usage')
                return False
            workflow_type = workflow_config.get('type', 'analysis')
            if workflow_type not in ['analysis', 'validation', 'monitoring']:
                self.logger.warning(f'Workflow {workflow_id} has unsafe type: {workflow_type}')
                return False
            read_only = workflow_config.get('read_only', True)
            if not read_only:
                self.logger.warning(f'Workflow {workflow_id} is not read-only - safety violation')
                return False
            self.logger.info(f'Workflow {workflow_id} passed safety validation')
            return True
        except Exception as e:
            self.logger.error(f'Workflow safety validation failed for {workflow_id}: {e}')
            return False

    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }
        
    def register_module(self, registry):
        """Register module with registry."""
        if hasattr(registry, 'register'):
            registry.register(self.get_interface_metadata())
            
    def health_check(self):
        """Perform health check."""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'module_id': getattr(self, 'module_id', self.__class__.__name__)
        }
        
    def get_health_status(self):
        """Get current health status."""
        return self.health_check()

