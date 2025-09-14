"""
Handler Core

This module was extracted from handler.py
as part of RM-DDD compliance refactoring.
"""

import re
from datetime import datetime
from typing import Callable, Optional
from ..core.reflective_module import HealthIndicator, ModuleStatus, ReflectiveModule
from .models import ActionResult, CommandPattern, StructuredAction, ValidationResult
from src.rm_ddd.core.health import ModuleHealth


def __init__(self, instance_id: str):
    super().__init__('TextProtocolHandler', '1.0.0')
    self.instance_id = instance_id
    self.command_patterns: dict[str, CommandPattern] = {}
    self.action_handlers: dict[str, Callable[[StructuredAction], ActionResult]] = {}
    self.command_history: list[StructuredAction] = []
    self.execution_stats = {'total_commands': 0, 'successful_commands': 0, 'failed_commands': 0, 'average_execution_time': 0.0}
    self._register_default_patterns()

def _register_default_patterns(self) -> None:
    """Register default command patterns."""
    patterns = [CommandPattern(verb='run', noun='task', allowed_modifiers=['beast-mode', 'parallel', 'sequential', 'debug'], required_parameters=['task_id'], optional_parameters=['timeout', 'priority', 'workspace'], description='Execute a task with specified mode', examples=['run task abc beast-mode', 'run task xyz parallel timeout=300']), CommandPattern(verb='stop', noun='instance', allowed_modifiers=['graceful', 'immediate', 'force'], required_parameters=['instance_id'], optional_parameters=['timeout', 'preserve_state'], description='Stop a running instance', examples=['stop instance kiro-3 graceful', 'stop instance kiro-1 immediate']), CommandPattern(verb='sync', noun='branch', allowed_modifiers=['upstream', 'downstream', 'bidirectional'], required_parameters=['branch_name'], optional_parameters=['conflict_strategy', 'merge_strategy'], description='Synchronize git branch', examples=['sync branch feature/task-1 upstream', 'sync branch main bidirectional']), CommandPattern(verb='status', noun='swarm', allowed_modifiers=['detailed', 'summary', 'health', 'performance'], required_parameters=[], optional_parameters=['format', 'filter'], description='Get swarm status information', examples=['status swarm detailed', 'status swarm health']), CommandPattern(verb='scale', noun='instances', allowed_modifiers=['up', 'down', 'auto'], required_parameters=['count'], optional_parameters=['resource_type', 'deployment_target'], description='Scale instance count', examples=['scale instances up count=5', 'scale instances auto count=3'])]
    for pattern in patterns:
        self.register_pattern(pattern)

def register_pattern(self, pattern: CommandPattern) -> None:
    """Register a command pattern for validation."""
    key = f'{pattern.verb}_{pattern.noun}'
    self.command_patterns[key] = pattern
    self.update_activity()

def register_handler(self, verb: str, noun: str, handler: Callable[[StructuredAction], ActionResult]) -> None:
    """Register an action handler."""
    key = f'{verb}_{noun}'
    self.action_handlers[key] = handler
    self.update_activity()

def _normalize_command_text(self, text: str) -> str:
    """Normalize command text for parsing."""
    replacements = {'\\bexecute\\b': 'run', '\\bhalt\\b': 'stop', '\\bin beast mode\\b': 'beast-mode', '\\bin parallel\\b': 'parallel', '\\ball running threads\\b': 'instances all', '\\bactive processes\\b': 'instances active', '\\bgracefully\\b': 'graceful'}
    normalized = text.lower().strip()
    for pattern, replacement in replacements.items():
        normalized = re.sub(pattern, replacement, normalized)
    return normalized

def execute_action(self, action: StructuredAction) -> ActionResult:
    """Execute structured action and return result."""
    start_time = datetime.now()
    try:
        validation = self.validate_command(action)
        if not validation.is_valid:
            return ActionResult(success=False, message=f"Invalid command: {', '.join(validation.errors)}", execution_time=datetime.now() - start_time, correlation_id=action.correlation_id)
        key = f'{action.verb}_{action.noun}'
        if key in self.action_handlers:
            handler = self.action_handlers[key]
            result = handler(action)
            self.execution_stats['total_commands'] += 1
            if result.success:
                self.execution_stats['successful_commands'] += 1
            else:
                self.execution_stats['failed_commands'] += 1
            total_time = (self.execution_stats['average_execution_time'] * (self.execution_stats['total_commands'] - 1) + result.execution_time.total_seconds()) / self.execution_stats['total_commands']
            self.execution_stats['average_execution_time'] = total_time
            self.update_activity()
            return result
        else:
            return ActionResult(success=False, message=f'No handler registered for: {action.verb} {action.noun}', execution_time=datetime.now() - start_time, correlation_id=action.correlation_id)
    except Exception as e:
        self.add_health_indicator(self.create_health_indicator('action_execution', 'critical', f'Failed to execute action: {action.to_command_string()}', {'error': str(e), 'action': action.model_dump()}))
        return ActionResult(success=False, message=f'Execution failed: {str(e)}', execution_time=datetime.now() - start_time, correlation_id=action.correlation_id)

def get_command_help(self, verb: Optional[str]=None, noun: Optional[str]=None) -> str:
    """Get help text for commands."""
    if verb and noun:
        key = f'{verb}_{noun}'
        if key in self.command_patterns:
            pattern = self.command_patterns[key]
            help_text = f'{pattern.verb} {pattern.noun} - {pattern.description}\n'
            if pattern.allowed_modifiers:
                help_text += f"Modifiers: {', '.join(pattern.allowed_modifiers)}\n"
            if pattern.required_parameters:
                help_text += f"Required: {', '.join(pattern.required_parameters)}\n"
            if pattern.optional_parameters:
                help_text += f"Optional: {', '.join(pattern.optional_parameters)}\n"
            if pattern.examples:
                help_text += 'Examples:\n'
                for example in pattern.examples:
                    help_text += f'  {example}\n'
            return help_text
        else:
            return f'No help available for: {verb} {noun}'
    else:
        help_text = 'Available commands:\n'
        for _key, pattern in self.command_patterns.items():
            help_text += f'  {pattern.verb} {pattern.noun} - {pattern.description}\n'
        return help_text

def get_module_status(self) -> ModuleStatus:
    """Get current module status with health indicators."""
    return ModuleStatus(module_name=self.name, version=self.version, status='active' if self.is_healthy() else 'error', uptime=self.get_uptime(), last_activity=self.last_activity, health_indicators=self.get_health_indicators(), performance_metrics={'execution_stats': self.execution_stats, 'command_history_size': len(self.command_history), 'registered_patterns': len(self.command_patterns), 'registered_handlers': len(self.action_handlers)})

def is_healthy(self) -> bool:
    """Check if module is in healthy state."""
    recent_indicators = [indicator for indicator in self._health_indicators if (datetime.now() - indicator.timestamp).total_seconds() < 300]
    critical_count = sum((1 for indicator in recent_indicators if indicator.status == 'critical'))
    return critical_count == 0

def get_health_indicators(self) -> list[HealthIndicator]:
    """Get current health indicators."""
    success_rate = 0.0
    if self.execution_stats['total_commands'] > 0:
        success_rate = self.execution_stats['successful_commands'] / self.execution_stats['total_commands']
    performance_indicator = self.create_health_indicator('performance', 'healthy' if success_rate >= 0.9 else 'warning' if success_rate >= 0.7 else 'critical', f'Command success rate: {success_rate:.2%}', {'success_rate': success_rate, 'total_commands': self.execution_stats['total_commands'], 'average_execution_time': self.execution_stats['average_execution_time']})
    return self._health_indicators + [performance_indicator]

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

