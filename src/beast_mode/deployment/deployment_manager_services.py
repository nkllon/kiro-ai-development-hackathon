"""
Deployment Manager Services

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

@dataclass
class ServiceDefinition:
    """Definition of a service to deploy"""
    name: str
    command: List[str]
    working_directory: str
    environment: Dict[str, str]
    dependencies: List[str] = None
    health_check_url: Optional[str] = None
    restart_policy: str = 'always'

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

class DeploymentManager:
    """Manages deployment of Beast Mode services"""

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self.deployments: Dict[str, DeploymentStatus] = {}
        self.processes: Dict[str, subprocess.Popen] = {}
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f'Received signal {signum}, shutting down gracefully...')
        self.stop_all_deployments()
        sys.exit(0)

    def create_single_machine_deployment(self, environment: str) -> str:
        """Create single machine deployment"""
        config = self.config_manager.get_config(environment)
        deployment_id = f'single_{environment}_{int(time.time())}'
        services = {'redis': ServiceDefinition(name='redis', command=['redis-server', '--port', str(config.redis.port)], working_directory='.', environment={}, health_check_url=f'redis://{config.redis.host}:{config.redis.port}'), 'mailbox_logger': ServiceDefinition(name='mailbox_logger', command=[sys.executable, '-m', 'beast_mode.messaging.mailbox_logger', '--redis-url', f'redis://{config.redis.host}:{config.redis.port}', '--log-file', config.agent.mailbox_log_file], working_directory='.', environment=self.config_manager.get_environment_variables(environment), dependencies=['redis']), 'agent': ServiceDefinition(name='agent', command=[sys.executable, '-m', 'beast_mode.messaging.bus_client', '--agent-id', config.agent.agent_id, '--capabilities', ','.join(config.agent.capabilities), '--redis-url', f'redis://{config.redis.host}:{config.redis.port}'], working_directory='.', environment=self.config_manager.get_environment_variables(environment), dependencies=['redis', 'mailbox_logger'])}
        deployment_status = DeploymentStatus(deployment_id=deployment_id, type=DeploymentType.SINGLE_MACHINE, environment=environment, services={name: {'status': 'pending', 'pid': None} for name in services.keys()}, started_at=time.strftime('%Y-%m-%d %H:%M:%S'), status='starting')
        self.deployments[deployment_id] = deployment_status
        self._start_services_in_order(services, deployment_id)
        return deployment_id

    def create_distributed_deployment(self, environment: str, nodes: List[str]) -> str:
        """Create distributed deployment across multiple nodes"""
        config = self.config_manager.get_config(environment)
        deployment_id = f'distributed_{environment}_{int(time.time())}'
        deployment_manifest = {'deployment_id': deployment_id, 'environment': environment, 'nodes': nodes, 'services': {}}
        if len(nodes) > 0:
            redis_node = nodes[0]
            deployment_manifest['services']['redis'] = {'node': redis_node, 'service': ServiceDefinition(name='redis', command=['redis-server', '--port', str(config.redis.port), '--bind', '0.0.0.0'], working_directory='.', environment={}).__dict__}
        for i, node in enumerate(nodes):
            agent_id = f'{config.agent.agent_id}_node_{i}'
            deployment_manifest['services'][f'agent_{i}'] = {'node': node, 'service': ServiceDefinition(name=f'agent_{i}', command=[sys.executable, '-m', 'beast_mode.messaging.bus_client', '--agent-id', agent_id, '--capabilities', ','.join(config.agent.capabilities), '--redis-url', f'redis://{config.redis.host}:{config.redis.port}'], working_directory='.', environment=self.config_manager.get_environment_variables(environment), dependencies=['redis']).__dict__}
            deployment_manifest['services'][f'mailbox_logger_{i}'] = {'node': node, 'service': ServiceDefinition(name=f'mailbox_logger_{i}', command=[sys.executable, '-m', 'beast_mode.messaging.mailbox_logger', '--redis-url', f'redis://{config.redis.host}:{config.redis.port}', '--log-file', f'mailbox_{node}.log'], working_directory='.', environment=self.config_manager.get_environment_variables(environment), dependencies=['redis']).__dict__}
        manifest_path = Path(f'deployment_{deployment_id}.json')
        with open(manifest_path, 'w') as f:
            json.dump(deployment_manifest, f, indent=2)
        deployment_status = DeploymentStatus(deployment_id=deployment_id, type=DeploymentType.DISTRIBUTED, environment=environment, services={name: {'status': 'pending', 'node': service['node']} for name, service in deployment_manifest['services'].items()}, started_at=time.strftime('%Y-%m-%d %H:%M:%S'), status='manifest_created')
        self.deployments[deployment_id] = deployment_status
        self.logger.info(f'Distributed deployment manifest created: {manifest_path}')
        self.logger.info('Execute the manifest on each node to start the deployment')
        return deployment_id

    def create_docker_deployment(self, environment: str) -> str:
        """Create Docker-based deployment"""
        config = self.config_manager.get_config(environment)
        deployment_id = f'docker_{environment}_{int(time.time())}'
        docker_compose = {'version': '3.8', 'services': {'redis': {'image': 'redis:7-alpine', 'ports': [f'{config.redis.port}:6379'], 'command': ['redis-server', '--appendonly', 'yes'], 'volumes': ['redis_data:/data'], 'healthcheck': {'test': ['CMD', 'redis-cli', 'ping'], 'interval': '30s', 'timeout': '10s', 'retries': 3}}, 'mailbox_logger': {'build': '.', 'command': ['python', '-m', 'beast_mode.messaging.mailbox_logger', '--redis-url', 'redis://redis:6379', '--log-file', '/app/logs/mailbox.log'], 'depends_on': ['redis'], 'volumes': ['./logs:/app/logs'], 'environment': self.config_manager.get_environment_variables(environment), 'restart': 'unless-stopped'}, 'agent': {'build': '.', 'command': ['python', '-m', 'beast_mode.messaging.bus_client', '--agent-id', config.agent.agent_id, '--capabilities', ','.join(config.agent.capabilities), '--redis-url', 'redis://redis:6379'], 'depends_on': ['redis', 'mailbox_logger'], 'volumes': ['./spores:/app/spores', './logs:/app/logs'], 'environment': self.config_manager.get_environment_variables(environment), 'restart': 'unless-stopped'}}, 'volumes': {'redis_data': {}}}
        compose_path = Path(f'docker-compose-{deployment_id}.yml')
        with open(compose_path, 'w') as f:
            import yaml
            yaml.dump(docker_compose, f, default_flow_style=False)
        self.config_manager.create_docker_env_file(environment, f'.env-{deployment_id}')
        deployment_status = DeploymentStatus(deployment_id=deployment_id, type=DeploymentType.DOCKER, environment=environment, services={name: {'status': 'pending'} for name in docker_compose['services'].keys()}, started_at=time.strftime('%Y-%m-%d %H:%M:%S'), status='compose_created')
        self.deployments[deployment_id] = deployment_status
        self.logger.info(f'Docker Compose file created: {compose_path}')
        self.logger.info(f'Environment file created: .env-{deployment_id}')
        self.logger.info(f'Start with: docker-compose -f {compose_path} --env-file .env-{deployment_id} up -d')
        return deployment_id

    def _start_services_in_order(self, services: Dict[str, ServiceDefinition], deployment_id: str):
        """Start services respecting dependencies"""
        started = set()
        remaining = set(services.keys())
        while remaining:
            ready_to_start = []
            for service_name in remaining:
                service = services[service_name]
                if all((dep in started for dep in service.dependencies)):
                    ready_to_start.append(service_name)
            if not ready_to_start:
                self.logger.error('Circular dependency detected or missing dependencies')
                break
            for service_name in ready_to_start:
                service = services[service_name]
                self._start_service(service, deployment_id)
                started.add(service_name)
                remaining.remove(service_name)
                time.sleep(2)
        if deployment_id in self.deployments:
            self.deployments[deployment_id].status = 'running'

    def _start_service(self, service: ServiceDefinition, deployment_id: str):
        """Start a single service"""
        try:
            self.logger.info(f'Starting service: {service.name}')
            env = os.environ.copy()
            env.update(service.environment)
            process = subprocess.Popen(service.command, cwd=service.working_directory, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes[f'{deployment_id}_{service.name}'] = process
            if deployment_id in self.deployments:
                self.deployments[deployment_id].services[service.name] = {'status': 'running', 'pid': process.pid, 'started_at': time.strftime('%Y-%m-%d %H:%M:%S')}
            self.logger.info(f'Service {service.name} started with PID {process.pid}')
        except Exception as e:
            self.logger.error(f'Failed to start service {service.name}: {e}')
            if deployment_id in self.deployments:
                self.deployments[deployment_id].services[service.name] = {'status': 'failed', 'error': str(e)}

    def stop_deployment(self, deployment_id: str):
        """Stop a deployment"""
        if deployment_id not in self.deployments:
            raise ValueError(f'Deployment not found: {deployment_id}')
        deployment = self.deployments[deployment_id]
        deployment.status = 'stopping'
        for process_key in list(self.processes.keys()):
            if process_key.startswith(deployment_id):
                process = self.processes[process_key]
                try:
                    process.terminate()
                    process.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                del self.processes[process_key]
                service_name = process_key.split('_', 1)[1]
                if service_name in deployment.services:
                    deployment.services[service_name]['status'] = 'stopped'
        deployment.status = 'stopped'
        self.logger.info(f'Deployment {deployment_id} stopped')

    def stop_all_deployments(self):
        """Stop all running deployments"""
        for deployment_id in list(self.deployments.keys()):
            if self.deployments[deployment_id].status in ['running', 'starting']:
                self.stop_deployment(deployment_id)

    def get_deployment_status(self, deployment_id: str) -> DeploymentStatus:
        """Get status of a deployment"""
        if deployment_id not in self.deployments:
            raise ValueError(f'Deployment not found: {deployment_id}')
        deployment = self.deployments[deployment_id]
        for process_key, process in self.processes.items():
            if process_key.startswith(deployment_id):
                service_name = process_key.split('_', 1)[1]
                if service_name in deployment.services:
                    if process.poll() is None:
                        deployment.services[service_name]['status'] = 'running'
                    else:
                        deployment.services[service_name]['status'] = 'stopped'
                        deployment.services[service_name]['exit_code'] = process.returncode
        return deployment

    def list_deployments(self) -> List[DeploymentStatus]:
        """List all deployments"""
        return list(self.deployments.values())

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
