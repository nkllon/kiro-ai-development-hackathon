"""
Service Monitor Validation

This module was extracted from service_monitor.py
as part of RM-DDD compliance refactoring.
"""

import time
import threading
import logging
import psutil
import subprocess
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path
from .config_manager import DeploymentConfig

def _check_service_health(self, service: MonitoredService):
    """Check health of a single service"""
    if service.status != ServiceStatus.RUNNING:
        return
    if service.process and service.process.poll() is not None:
        exit_code = service.process.returncode
        self.logger.warning(f'Service {service.name} terminated with exit code {exit_code}')
        service.status = ServiceStatus.FAILED
        service.process = None
        service.pid = None
        self._trigger_callbacks('service_failed', service)
        if service.auto_restart and service.metrics.restart_count < service.max_restarts:
            self.logger.info(f'Auto-restarting service {service.name}')
            threading.Thread(target=self.restart_service, args=(service.name,), daemon=True).start()
        return
    if service.pid:
        try:
            process = psutil.Process(service.pid)
            if not process.is_running():
                self.logger.warning(f'Service {service.name} process is not running')
                service.status = ServiceStatus.FAILED
                self._trigger_callbacks('service_failed', service)
                if service.auto_restart and service.metrics.restart_count < service.max_restarts:
                    threading.Thread(target=self.restart_service, args=(service.name,), daemon=True).start()
        except psutil.NoSuchProcess:
            self.logger.warning(f'Service {service.name} process not found')
            service.status = ServiceStatus.FAILED
            service.pid = None
            self._trigger_callbacks('service_failed', service)
    if service.health_check_command:
        self._run_health_check_command(service)
    service.last_health_check = time.time()

def _run_health_check_command(self, service: MonitoredService):
    """Run custom health check command"""
    try:
        result = subprocess.run(service.health_check_command, capture_output=True, timeout=10, cwd=service.working_directory)
        if result.returncode != 0:
            service.health_check_failures += 1
            self.logger.warning(f'Health check failed for {service.name}: {result.stderr.decode()}')
            if service.health_check_failures >= 3:
                self.logger.error(f'Multiple health check failures for {service.name}, restarting')
                service.health_check_failures = 0
                self._trigger_callbacks('health_check_failed', service)
                if service.auto_restart:
                    threading.Thread(target=self.restart_service, args=(service.name,), daemon=True).start()
        else:
            service.health_check_failures = 0
    except subprocess.TimeoutExpired:
        service.health_check_failures += 1
        self.logger.warning(f'Health check timeout for {service.name}')
    except Exception as e:
        service.health_check_failures += 1
        self.logger.error(f'Health check error for {service.name}: {e}')
