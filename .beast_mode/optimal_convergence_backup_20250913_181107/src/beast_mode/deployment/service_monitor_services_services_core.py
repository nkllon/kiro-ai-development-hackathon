"""
Service Monitor Services Services Core

This module was extracted from service_monitor_services_services.py
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

def __init__(self, config: DeploymentConfig):
    self.config = config
    self.logger = logging.getLogger(__name__)
    self.services: Dict[str, MonitoredService] = {}
    self.monitoring_thread: Optional[threading.Thread] = None
    self.running = False
    self.callbacks: Dict[str, List[Callable]] = {'service_started': [], 'service_stopped': [], 'service_failed': [], 'service_restarted': [], 'health_check_failed': []}

def add_service(self, service: MonitoredService):
    """Add a service to monitor"""
    self.services[service.name] = service
    self.logger.info(f'Added service to monitor: {service.name}')

def remove_service(self, service_name: str):
    """Remove a service from monitoring"""
    if service_name in self.services:
        service = self.services[service_name]
        if service.status == ServiceStatus.RUNNING:
            self.stop_service(service_name)
        del self.services[service_name]
        self.logger.info(f'Removed service from monitor: {service_name}')

def start_service(self, service_name: str) -> bool:
    """Start a monitored service"""
    if service_name not in self.services:
        self.logger.error(f'Service not found: {service_name}')
        return False
    service = self.services[service_name]
    if service.status == ServiceStatus.RUNNING:
        self.logger.warning(f'Service {service_name} is already running')
        return True
    try:
        service.status = ServiceStatus.STARTING
        self.logger.info(f'Starting service: {service_name}')
        env = service.environment.copy()
        process = subprocess.Popen(service.command, cwd=service.working_directory, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=None if hasattr(subprocess, 'CREATE_NEW_PROCESS_GROUP') else lambda: None)
        service.process = process
        service.pid = process.pid
        service.status = ServiceStatus.RUNNING
        service.started_at = time.time()
        service.metrics.restart_count += 1
        service.metrics.last_restart = time.strftime('%Y-%m-%d %H:%M:%S')
        self.logger.info(f'Service {service_name} started with PID {service.pid}')
        self._trigger_callbacks('service_started', service)
        return True
    except Exception as e:
        service.status = ServiceStatus.FAILED
        self.logger.error(f'Failed to start service {service_name}: {e}')
        self._trigger_callbacks('service_failed', service)
        return False

def stop_service(self, service_name: str, graceful: bool=True) -> bool:
    """Stop a monitored service"""
    if service_name not in self.services:
        self.logger.error(f'Service not found: {service_name}')
        return False
    service = self.services[service_name]
    if service.status != ServiceStatus.RUNNING:
        self.logger.warning(f'Service {service_name} is not running')
        return True
    try:
        service.status = ServiceStatus.STOPPING
        self.logger.info(f'Stopping service: {service_name}')
        if service.process:
            if graceful:
                service.process.terminate()
                try:
                    service.process.wait(timeout=self.config.service_management.get('graceful_shutdown_timeout', 30))
                except subprocess.TimeoutExpired:
                    self.logger.warning(f'Service {service_name} did not stop gracefully, forcing shutdown')
                    service.process.kill()
                    service.process.wait()
            else:
                service.process.kill()
                service.process.wait()
            service.process = None
        service.pid = None
        service.status = ServiceStatus.STOPPED
        self.logger.info(f'Service {service_name} stopped')
        self._trigger_callbacks('service_stopped', service)
        return True
    except Exception as e:
        self.logger.error(f'Failed to stop service {service_name}: {e}')
        return False

def restart_service(self, service_name: str) -> bool:
    """Restart a monitored service"""
    if service_name not in self.services:
        self.logger.error(f'Service not found: {service_name}')
        return False
    service = self.services[service_name]
    if service.metrics.restart_count >= service.max_restarts:
        self.logger.error(f'Service {service_name} has exceeded max restarts ({service.max_restarts})')
        service.status = ServiceStatus.FAILED
        return False
    service.status = ServiceStatus.RESTARTING
    self.logger.info(f'Restarting service: {service_name}')
    if not self.stop_service(service_name):
        return False
    time.sleep(service.restart_delay)
    success = self.start_service(service_name)
    if success:
        self._trigger_callbacks('service_restarted', service)
    return success

def start_monitoring(self):
    """Start the monitoring thread"""
    if self.running:
        self.logger.warning('Monitoring is already running')
        return
    self.running = True
    self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
    self.monitoring_thread.start()
    self.logger.info('Service monitoring started')

def stop_monitoring(self):
    """Stop the monitoring thread"""
    if not self.running:
        return
    self.running = False
    if self.monitoring_thread:
        self.monitoring_thread.join(timeout=5)
    self.logger.info('Service monitoring stopped')

def _monitoring_loop(self):
    """Main monitoring loop"""
    while self.running:
        try:
            for service_name, service in self.services.items():
                self._check_service_health(service)
                self._update_service_metrics(service)
            time.sleep(self.config.monitoring.health_check_interval)
        except Exception as e:
            self.logger.error(f'Error in monitoring loop: {e}')
            time.sleep(5)

def _update_service_metrics(self, service: MonitoredService):
    """Update metrics for a service"""
    if service.status != ServiceStatus.RUNNING or not service.pid:
        return
    try:
        process = psutil.Process(service.pid)
        service.metrics.cpu_percent = process.cpu_percent()
        memory_info = process.memory_info()
        service.metrics.memory_mb = memory_info.rss / 1024 / 1024
        service.metrics.memory_percent = process.memory_percent()
        try:
            service.metrics.open_files = len(process.open_files())
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
        try:
            service.metrics.connections = len(process.connections())
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
        if service.started_at:
            service.metrics.uptime_seconds = time.time() - service.started_at
    except psutil.NoSuchProcess:
        service.status = ServiceStatus.FAILED
        service.pid = None
    except Exception as e:
        self.logger.error(f'Error updating metrics for {service.name}: {e}')

def get_service_status(self, service_name: str) -> Optional[MonitoredService]:
    """Get status of a specific service"""
    return self.services.get(service_name)

def get_all_services_status(self) -> Dict[str, MonitoredService]:
    """Get status of all services"""
    return self.services.copy()

def add_callback(self, event: str, callback: Callable):
    """Add callback for service events"""
    if event in self.callbacks:
        self.callbacks[event].append(callback)

def _trigger_callbacks(self, event: str, service: MonitoredService):
    """Trigger callbacks for an event"""
    for callback in self.callbacks.get(event, []):
        try:
            callback(service)
        except Exception as e:
            self.logger.error(f'Error in callback for {event}: {e}')

def export_metrics(self, output_file: str):
    """Export service metrics to file"""
    metrics_data = {'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'), 'services': {}}
    for service_name, service in self.services.items():
        metrics_data['services'][service_name] = {'status': service.status.value, 'metrics': {'cpu_percent': service.metrics.cpu_percent, 'memory_percent': service.metrics.memory_percent, 'memory_mb': service.metrics.memory_mb, 'uptime_seconds': service.metrics.uptime_seconds, 'restart_count': service.metrics.restart_count, 'open_files': service.metrics.open_files, 'connections': service.metrics.connections}}
    with open(output_file, 'w') as f:
        json.dump(metrics_data, f, indent=2)
    self.logger.info(f'Metrics exported to {output_file}')

def cleanup(self):
    """Cleanup resources and stop all services"""
    self.stop_monitoring()
    for service_name in list(self.services.keys()):
        self.stop_service(service_name)
    self.logger.info('Service monitor cleanup completed')
