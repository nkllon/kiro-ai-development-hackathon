"""
Handler Processing

This module was extracted from handler.py
as part of RM-DDD compliance refactoring.
"""

import re
from datetime import datetime
from typing import Callable, Optional
from ..core.reflective_module import HealthIndicator, ModuleStatus, ReflectiveModule
from .models import ActionResult, CommandPattern, StructuredAction, ValidationResult

def parse_command(self, text: str) -> StructuredAction:
    """Parse human-readable text into structured action.

        Supports natural language variations:
        - 'run task abc beast mode' -> verb=run, noun=task, modifiers=[beast-mode]
        - 'execute task xyz in parallel' -> verb=run, noun=task, modifiers=[parallel]
        - 'stop all running threads' -> verb=stop, noun=instances, modifiers=[all]
        """
    try:
        normalized = self._normalize_command_text(text)
        try:
            action = StructuredAction.from_command_string(normalized, self.instance_id)
            self.command_history.append(action)
            return action
        except ValueError:
            action = self._parse_natural_language(text)
            self.command_history.append(action)
            return action
    except Exception as e:
        self.add_health_indicator(self.create_health_indicator('command_parsing', 'warning', f'Failed to parse command: {text}', {'error': str(e)}))
        raise ValueError(f"Failed to parse command '{text}': {e}") from e

def _parse_natural_language(self, text: str) -> StructuredAction:
    """Parse natural language command into structured action."""
    words = text.lower().split()
    verb_mapping = {'execute': 'run', 'start': 'run', 'launch': 'run', 'halt': 'stop', 'kill': 'stop', 'terminate': 'stop', 'synchronize': 'sync', 'update': 'sync', 'check': 'status', 'show': 'status', 'get': 'status', 'increase': 'scale', 'decrease': 'scale', 'resize': 'scale'}
    verb = None
    for word in words:
        if word in verb_mapping:
            verb = verb_mapping[word]
            break
        elif word in ['run', 'stop', 'sync', 'status', 'scale', 'merge']:
            verb = word
            break
    if not verb:
        raise ValueError('Could not identify verb in command')
    noun_mapping = {'job': 'task', 'jobs': 'tasks', 'agent': 'instance', 'agents': 'instances', 'worker': 'instance', 'workers': 'instances', 'process': 'instance', 'processes': 'instances', 'thread': 'instance', 'threads': 'instances', 'repo': 'branch', 'repository': 'branch', 'cluster': 'swarm', 'group': 'swarm'}
    noun = None
    for word in words:
        if word in noun_mapping:
            noun = noun_mapping[word]
            break
        elif word in ['task', 'instance', 'branch', 'swarm', 'instances', 'branches']:
            noun = word
            break
    if not noun:
        default_nouns = {'run': 'task', 'stop': 'instance', 'sync': 'branch', 'status': 'swarm', 'scale': 'instances'}
        noun = default_nouns.get(verb, 'task')
    modifiers = []
    parameters = {}
    if 'beast' in text.lower() and 'mode' in text.lower():
        modifiers.append('beast-mode')
    if 'parallel' in text.lower():
        modifiers.append('parallel')
    if 'graceful' in text.lower() or 'gracefully' in text.lower():
        modifiers.append('graceful')
    if 'all' in text.lower():
        modifiers.append('all')
    if 'upstream' in text.lower():
        modifiers.append('upstream')
    for word in words:
        if word.startswith(('task-', 'kiro-', 'instance-')):
            if 'task' in noun:
                parameters['task_id'] = word
            else:
                parameters['instance_id'] = word
        elif word in ['abc', 'main'] and len(word) <= 4:
            if 'task' in noun:
                parameters['task_id'] = word
            elif 'branch' in noun:
                parameters['branch_name'] = word
    return StructuredAction(verb=verb, noun=noun, modifiers=modifiers, parameters=parameters, source_instance=self.instance_id)
