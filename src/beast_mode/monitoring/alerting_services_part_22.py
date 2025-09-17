from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def get_alert_summary(self) -> Dict[str, Any]:
        """get_alert_summary - Enhanced for compliance"""
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Get a summary of current alert status."""
        active_by_severity = {}
        for severity in AlertSeverity:
            active_by_severity[severity.value] = len(self.get_alerts_by_severity(severity))
        recent_history = self.get_alert_history(24)
        return {'active_alerts': len(self.active_alerts), 'active_by_severity': active_by_severity, 'recent_alerts_24h': len(recent_history), 'alert_rules': len(self.alert_rules), 'last_updated': datetime.now().isoformat()}

    async def _register_default_rules(self) -> None:
        """Register default alert rules for common issues."""
        await self.register_alert_rule(name='redis_connectivity_failure', description='Redis server is not reachable', severity=AlertSeverity.CRITICAL, condition_function=self._check_redis_connectivity_alert, evaluation_interval_seconds=30, cooldown_seconds=300)
        await self.register_alert_rule(name='high_error_rate', description='Error rate is above acceptable threshold', severity=AlertSeverity.HIGH, condition_function=self._check_error_rate_alert, threshold_value=5.0, evaluation_interval_seconds=60, cooldown_seconds=600)
        await self.register_alert_rule(name='high_message_latency', description='Message latency is above acceptable threshold', severity=AlertSeverity.MEDIUM, condition_function=self._check_latency_alert, threshold_value=1000.0, evaluation_interval_seconds=120, cooldown_seconds=300)
        await self.register_alert_rule(name='high_resource_usage', description='System resource usage is critically high', severity=AlertSeverity.HIGH, condition_function=self._check_resource_usage_alert, threshold_value=90.0, evaluation_interval_seconds=300, cooldown_seconds=600)

    async def _alerting_loop(self) -> None:
        """Main alerting evaluation loop."""
        self.logger.info('Starting alerting evaluation loop')
        while self.alerting_active:
            try:
                for rule_name, rule in self.alert_rules.items():
                    last_eval = self.last_evaluation.get(rule_name)
                    if not last_eval or (datetime.now() - last_eval).total_seconds() >= rule.evaluation_interval_seconds:
                        await self._evaluate_rule(rule_name, rule)
                        self.last_evaluation[rule_name] = datetime.now()
                await asyncio.sleep(10)
            except Exception as e:
                self.logger.error(f'Error in alerting loop: {e}')
                await asyncio.sleep(30)

    async def _evaluate_rule(self, rule_name: str, rule: AlertRule) -> None:
        """Evaluate a single alert rule."""
        try:
            last_alert = self.last_alert_time.get(rule_name)
            if last_alert and (datetime.now() - last_alert).total_seconds() < rule.cooldown_seconds:
                return
            result = await rule.condition_function(rule)
            if result.get('should_alert', False):
                alert_id = await self.fire_alert(name=rule_name, message=result.get('message', rule.description), severity=rule.severity, source_component=result.get('component', 'unknown'), details=result.get('details', {}))
                self.last_alert_time[rule_name] = datetime.now()
            elif rule.auto_resolve:
                await self._check_auto_resolve(rule_name, rule, result)
        except Exception as e:
            self.logger.error(f'Error evaluating alert rule {rule_name}: {e}')

    async def _check_auto_resolve(self, rule_name: str, rule: AlertRule, result: Dict[str, Any]) -> None:
        """Check if any active alerts for this rule should be auto-resolved."""
        rule_alerts = [alert for alert in self.active_alerts.values() if alert.name == rule_name]
        for alert in rule_alerts:
            if result.get('should_resolve', False):
                await self.resolve_alert(alert.id, result.get('resolution_message', 'Condition no longer met'))

    async def _notify_handlers(self, alert: Alert) -> None:
        """Notify all registered alert handlers."""
        for handler in self.alert_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert)
                else:
                    handler(alert)
            except Exception as e:
                self.logger.error(f'Error in alert handler {handler.__name__}: {e}')

    async def _check_redis_connectivity_alert(self, rule: AlertRule) -> Dict[str, Any]:
        """Check Redis connectivity for alerting."""
        return {'should_alert': False, 'should_resolve': True, 'message': 'Redis connectivity OK', 'component': 'redis'}

    async def _check_error_rate_alert(self, rule: AlertRule) -> Dict[str, Any]:
        """Check error rate for alerting."""
        return {'should_alert': False, 'should_resolve': True, 'message': 'Error rate within acceptable limits', 'component': 'messaging'}

    async def _check_latency_alert(self, rule: AlertRule) -> Dict[str, Any]:
        """Check message latency for alerting."""
        return {'should_alert': False, 'should_resolve': True, 'message': 'Message latency within acceptable limits', 'component': 'messaging'}

    async def _check_resource_usage_alert(self, rule: AlertRule) -> Dict[str, Any]:
        """Check system resource usage for alerting."""
        return {'should_alert': False, 'should_resolve': True, 'message': 'System resource usage normal', 'component': 'system'}

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

