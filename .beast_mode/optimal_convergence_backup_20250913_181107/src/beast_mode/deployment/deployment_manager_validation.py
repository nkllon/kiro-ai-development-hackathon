"""
Deployment Manager Validation

This module was extracted from deployment_manager.py
as part of RM-DDD compliance refactoring.
"""

import os
import sys
import json
import subprocess
import signal
import time
import psutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging
from .config_manager import ConfigManager, DeploymentConfig, DeploymentEnvironment
import yaml

def health_check_deployment(self, deployment_id: str) -> Dict[str, Any]:
    """Perform health check on deployment"""
    if deployment_id not in self.deployments:
        raise ValueError(f'Deployment not found: {deployment_id}')
    deployment = self.deployments[deployment_id]
    health_status = {'deployment_id': deployment_id, 'overall_status': 'healthy', 'services': {}, 'system_resources': {}}
    for service_name, service_info in deployment.services.items():
        service_health = {'status': service_info.get('status', 'unknown')}
        if 'pid' in service_info:
            try:
                process = psutil.Process(service_info['pid'])
                service_health.update({'cpu_percent': process.cpu_percent(), 'memory_percent': process.memory_percent(), 'status': 'running' if process.is_running() else 'stopped'})
            except psutil.NoSuchProcess:
                service_health['status'] = 'stopped'
        health_status['services'][service_name] = service_health
        if service_health['status'] != 'running':
            health_status['overall_status'] = 'unhealthy'
    health_status['system_resources'] = {'cpu_percent': psutil.cpu_percent(), 'memory_percent': psutil.virtual_memory().percent, 'disk_percent': psutil.disk_usage('/').percent}
    return health_status
