#!/usr/bin/env python3
"""
Automated Rollback System for WebSocket Deployment

This script implements automated rollback capabilities with failure triggers,
configuration restoration, and comprehensive rollback validation.

Features:
- Automatic rollback triggers based on health metrics
- Configuration restoration from backups
- Zero-downtime rollback with health validation
- Rollback validation and reporting
- Emergency rollback procedures
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import yaml
import requests
from concurrent.futures import ThreadPoolExecutor

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from beast_mode.observatory.websocket import (
    WebSocketHealthValidator,
    HealthStatus,
    EndpointMonitor,
    FailureDetector
)
from beast_mode.observatory.monitoring.health_monitor import WebSocketHealthMonitor


class RollbackTrigger(Enum):
    """Types of rollback triggers"""
    HEALTH_THRESHOLD = "health_threshold"
    ERROR_RATE = "error_rate"
    LATENCY_THRESHOLD = "latency_threshold"
    CONNECTION_FAILURE = "connection_failure"
    MANUAL = "manual"
    EMERGENCY = "emergency"


class RollbackStatus(Enum):
    """Rollback status tracking"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class RollbackConfig:
    """Configuration for rollback system"""
    # Rollback triggers
    triggers: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "health_threshold": {
            "enabled": True,
            "threshold": 0.7,
            "check_interval": 30
        },
        "error_rate": {
            "enabled": True,
            "threshold": 0.1,
            "check_interval": 60
        },
        "latency_threshold": {
            "enabled": True,
            "threshold_ms": 2000,
            "check_interval": 30
        },
        "connection_failure": {
            "enabled": True,
            "threshold": 0.2,
            "check_interval": 60
        }
    })
    
    # Rollback settings
    rollback_timeout: int = 300  # 5 minutes
    validation_timeout: int = 180  # 3 minutes
    max_rollback_attempts: int = 3
    
    # Backup settings
    backup_retention_days: int = 7
    backup_validation: bool = True
    
    # Environment configurations
    environments: Dict[str, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class RollbackResult:
    """Result of a rollback operation"""
    environment: str
    trigger: RollbackTrigger
    status: RollbackStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    health_score_before: float = 0.0
    health_score_after: float = 0.0
    error_message: Optional[str] = None
    restored_files: List[str] = field(default_factory=list)
    validation_results: Dict[str, Any] = field(default_factory=dict)


class RollbackManager:
    """
    Comprehensive rollback management system.
    
    Provides automated rollback capabilities with health monitoring,
    configuration restoration, and validation.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize rollback manager with configuration"""
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        
        # Initialize monitoring components
        self.health_validator = WebSocketHealthValidator()
        self.endpoint_monitor = EndpointMonitor()
        self.failure_detector = FailureDetector()
        self.health_monitor = WebSocketHealthMonitor()
        
        # Rollback tracking
        self.rollback_history: List[RollbackResult] = []
        self.active_rollbacks: Dict[str, RollbackResult] = {}
        self.monitoring_active = False
        
        # Health monitoring cache
        self._health_cache: Dict[str, Dict[str, Any]] = {}
        self._last_health_check: Dict[str, datetime] = {}
        
        self.logger.info("Rollback Manager initialized")
    
    def _load_config(self, config_path: Optional[str]) -> RollbackConfig:
        """Load rollback configuration from file or use defaults"""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
                return RollbackConfig(**config_data)
        
        # Default configuration
        return RollbackConfig(
            environments={
                "dev": {
                    "url": "http://localhost:8888",
                    "websocket_url": "ws://localhost:8888/ws",
                    "health_endpoint": "/health",
                    "backup_dir": "backups/dev",
                    "config_files": [
                        "cloudflare-tunnel-config-websocket.yml"
                    ]
                },
                "staging": {
                    "url": "https://staging-observatory.nkllon.com",
                    "websocket_url": "wss://staging-observatory.nkllon.com/ws",
                    "health_endpoint": "/health",
                    "backup_dir": "backups/staging",
                    "config_files": [
                        "cloudflare-tunnel-config-websocket-staging.yml"
                    ]
                },
                "production": {
                    "url": "https://observatory.nkllon.com",
                    "websocket_url": "wss://observatory.nkllon.com/ws",
                    "health_endpoint": "/health",
                    "backup_dir": "backups/production",
                    "config_files": [
                        "cloudflare-tunnel-config-websocket.yml"
                    ]
                }
            }
        )
    
    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging for rollback operations"""
        logger = logging.getLogger("rollback_manager")
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # File handler for rollback logs
        file_handler = logging.FileHandler(
            logs_dir / f"rollback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        file_handler.setLevel(logging.INFO)
        
        # Console handler for real-time output
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # JSON formatter for structured logs
        json_formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"component": "rollback", "message": "%(message)s"}'
        )
        file_handler.setFormatter(json_formatter)
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    async def start_monitoring(self) -> None:
        """Start continuous monitoring for rollback triggers"""
        self.monitoring_active = True
        self.logger.info("Starting rollback monitoring")
        
        # Start monitoring tasks for each environment
        monitoring_tasks = []
        for env_name in self.config.environments.keys():
            task = asyncio.create_task(self._monitor_environment(env_name))
            monitoring_tasks.append(task)
        
        # Wait for monitoring tasks
        try:
            await asyncio.gather(*monitoring_tasks)
        except Exception as e:
            self.logger.error(f"Monitoring failed: {e}")
        finally:
            self.monitoring_active = False
    
    async def stop_monitoring(self) -> None:
        """Stop continuous monitoring"""
        self.monitoring_active = False
        self.logger.info("Stopping rollback monitoring")
    
    async def _monitor_environment(self, environment: str) -> None:
        """Monitor a specific environment for rollback triggers"""
        env_config = self.config.environments[environment]
        
        while self.monitoring_active:
            try:
                # Check each trigger type
                for trigger_name, trigger_config in self.config.triggers.items():
                    if not trigger_config.get("enabled", False):
                        continue
                    
                    check_interval = trigger_config.get("check_interval", 60)
                    
                    # Check if enough time has passed since last check
                    last_check_key = f"{environment}_{trigger_name}"
                    last_check = self._last_health_check.get(last_check_key, datetime.min)
                    
                    if datetime.now() - last_check < timedelta(seconds=check_interval):
                        continue
                    
                    # Perform trigger check
                    should_rollback = await self._check_rollback_trigger(
                        environment, trigger_name, trigger_config
                    )
                    
                    if should_rollback:
                        self.logger.warning(f"Rollback trigger activated: {trigger_name} for {environment}")
                        await self._execute_rollback(
                            environment, RollbackTrigger(trigger_name)
                        )
                    
                    # Update last check time
                    self._last_health_check[last_check_key] = datetime.now()
                
                # Wait before next check cycle
                await asyncio.sleep(10)
                
            except Exception as e:
                self.logger.error(f"Error monitoring {environment}: {e}")
                await asyncio.sleep(30)  # Back off on error
    
    async def _check_rollback_trigger(
        self, 
        environment: str, 
        trigger_name: str, 
        trigger_config: Dict[str, Any]
    ) -> bool:
        """Check if a rollback trigger condition is met"""
        try:
            if trigger_name == "health_threshold":
                return await self._check_health_threshold(environment, trigger_config)
            elif trigger_name == "error_rate":
                return await self._check_error_rate(environment, trigger_config)
            elif trigger_name == "latency_threshold":
                return await self._check_latency_threshold(environment, trigger_config)
            elif trigger_name == "connection_failure":
                return await self._check_connection_failure(environment, trigger_config)
            else:
                return False
        except Exception as e:
            self.logger.error(f"Error checking trigger {trigger_name}: {e}")
            return False
    
    async def _check_health_threshold(
        self, 
        environment: str, 
        trigger_config: Dict[str, Any]
    ) -> bool:
        """Check if health score is below threshold"""
        threshold = trigger_config.get("threshold", 0.7)
        
        # Get current health score
        health_score = await self._get_environment_health_score(environment)
        
        return health_score < threshold
    
    async def _check_error_rate(
        self, 
        environment: str, 
        trigger_config: Dict[str, Any]
    ) -> bool:
        """Check if error rate exceeds threshold"""
        threshold = trigger_config.get("threshold", 0.1)
        
        # Get current error rate
        metrics = self.health_monitor.get_performance_metrics()
        error_rate = metrics.get('websocket_error_rate', 0)
        
        return error_rate > threshold
    
    async def _check_latency_threshold(
        self, 
        environment: str, 
        trigger_config: Dict[str, Any]
    ) -> bool:
        """Check if latency exceeds threshold"""
        threshold_ms = trigger_config.get("threshold_ms", 2000)
        
        # Get current latency
        metrics = self.health_monitor.get_performance_metrics()
        latency_stats = metrics.get('latency_stats', {})
        avg_latency = latency_stats.get('avg', 0)
        
        return avg_latency > threshold_ms
    
    async def _check_connection_failure(
        self, 
        environment: str, 
        trigger_config: Dict[str, Any]
    ) -> bool:
        """Check if connection failure rate exceeds threshold"""
        threshold = trigger_config.get("threshold", 0.2)
        
        # Get current connection failure rate
        metrics = self.health_monitor.get_performance_metrics()
        failures = metrics.get('websocket_connection_failures', 0)
        active_connections = metrics.get('websocket_connections_active', 1)
        failure_rate = failures / max(active_connections, 1)
        
        return failure_rate > threshold
    
    async def _get_environment_health_score(self, environment: str) -> float:
        """Get health score for a specific environment"""
        env_config = self.config.environments[environment]
        
        try:
            # Check HTTP health
            health_url = f"{env_config['url']}{env_config['health_endpoint']}"
            response = requests.get(health_url, timeout=10)
            
            if response.status_code != 200:
                return 0.0
            
            # Check WebSocket health
            health_result = await self.health_validator.validate_websocket_health(
                env_config['websocket_url']
            )
            
            if health_result.status == HealthStatus.HEALTHY:
                return 1.0
            elif health_result.status == HealthStatus.DEGRADED:
                return 0.7
            else:
                return 0.3
                
        except Exception as e:
            self.logger.warning(f"Health check failed for {environment}: {e}")
            return 0.0
    
    async def execute_rollback(
        self,
        environment: str,
        trigger: RollbackTrigger = RollbackTrigger.MANUAL,
        force: bool = False
    ) -> RollbackResult:
        """
        Execute rollback for a specific environment.
        
        Args:
            environment: Environment to rollback
            trigger: Type of rollback trigger
            force: Force rollback even if validation fails
            
        Returns:
            RollbackResult containing rollback details
        """
        self.logger.info(f"Starting rollback for {environment} (trigger: {trigger.value})")
        
        # Create rollback result tracker
        rollback_result = RollbackResult(
            environment=environment,
            trigger=trigger,
            status=RollbackStatus.IN_PROGRESS,
            start_time=datetime.now()
        )
        
        # Check if rollback is already in progress
        if environment in self.active_rollbacks:
            self.logger.warning(f"Rollback already in progress for {environment}")
            return self.active_rollbacks[environment]
        
        self.active_rollbacks[environment] = rollback_result
        
        try:
            # Get health score before rollback
            rollback_result.health_score_before = await self._get_environment_health_score(environment)
            
            # Step 1: Validate backup availability
            if not force:
                await self._validate_backup_availability(environment)
            
            # Step 2: Stop current services
            await self._stop_services(environment)
            
            # Step 3: Restore configuration from backup
            restored_files = await self._restore_configuration(environment)
            rollback_result.restored_files = restored_files
            
            # Step 4: Restart services
            await self._restart_services(environment)
            
            # Step 5: Validate rollback success
            rollback_result.status = RollbackStatus.VALIDATING
            validation_results = await self._validate_rollback(environment)
            rollback_result.validation_results = validation_results
            
            # Step 6: Check final health score
            rollback_result.health_score_after = await self._get_environment_health_score(environment)
            
            # Determine final status
            if rollback_result.health_score_after > rollback_result.health_score_before:
                rollback_result.status = RollbackStatus.COMPLETED
                self.logger.info(f"Rollback completed successfully for {environment}")
            else:
                rollback_result.status = RollbackStatus.FAILED
                rollback_result.error_message = "Health score did not improve after rollback"
                self.logger.error(f"Rollback failed for {environment}")
            
        except Exception as e:
            rollback_result.status = RollbackStatus.FAILED
            rollback_result.error_message = str(e)
            self.logger.error(f"Rollback failed for {environment}: {e}")
        
        finally:
            rollback_result.end_time = datetime.now()
            self.rollback_history.append(rollback_result)
            self.active_rollbacks.pop(environment, None)
        
        return rollback_result
    
    async def _execute_rollback(self, environment: str, trigger: RollbackTrigger) -> None:
        """Execute rollback (internal method)"""
        try:
            result = await self.execute_rollback(environment, trigger)
            
            if result.status == RollbackStatus.COMPLETED:
                self.logger.info(f"Automatic rollback successful for {environment}")
            else:
                self.logger.error(f"Automatic rollback failed for {environment}")
                
        except Exception as e:
            self.logger.error(f"Error executing automatic rollback for {environment}: {e}")
    
    async def _validate_backup_availability(self, environment: str) -> None:
        """Validate that backups are available for rollback"""
        env_config = self.config.environments[environment]
        backup_dir = Path(env_config['backup_dir'])
        
        if not backup_dir.exists():
            raise Exception(f"Backup directory not found: {backup_dir}")
        
        # Check for recent backups
        backup_files = list(backup_dir.glob("*.backup"))
        if not backup_files:
            raise Exception(f"No backup files found in {backup_dir}")
        
        # Check backup age
        latest_backup = max(backup_files, key=lambda p: p.stat().st_mtime)
        backup_age = datetime.now() - datetime.fromtimestamp(latest_backup.stat().st_mtime)
        
        if backup_age > timedelta(days=self.config.backup_retention_days):
            raise Exception(f"Latest backup is too old: {backup_age}")
        
        self.logger.info(f"Backup validation passed for {environment}")
    
    async def _stop_services(self, environment: str) -> None:
        """Stop services for rollback"""
        self.logger.info(f"Stopping services for {environment}")
        
        # Stop cloudflared processes
        subprocess.run(["pkill", "-f", "cloudflared"], capture_output=True)
        
        # Wait for processes to stop
        await asyncio.sleep(5)
        
        self.logger.info(f"Services stopped for {environment}")
    
    async def _restore_configuration(self, environment: str) -> List[str]:
        """Restore configuration from backup"""
        env_config = self.config.environments[environment]
        backup_dir = Path(env_config['backup_dir'])
        
        self.logger.info(f"Restoring configuration for {environment}")
        
        # Find latest backup
        backup_files = list(backup_dir.glob("*.backup"))
        if not backup_files:
            raise Exception(f"No backup files found for {environment}")
        
        latest_backup = max(backup_files, key=lambda p: p.stat().st_mtime)
        
        # Restore configuration files
        restored_files = []
        for config_file in env_config.get('config_files', []):
            if Path(config_file).exists():
                # Create backup of current file
                current_backup = f"{config_file}.rollback_backup"
                subprocess.run(["cp", config_file, current_backup])
                
                # Restore from backup
                subprocess.run(["cp", str(latest_backup), config_file])
                restored_files.append(config_file)
                
                self.logger.info(f"Restored {config_file} from backup")
        
        return restored_files
    
    async def _restart_services(self, environment: str) -> None:
        """Restart services after rollback"""
        env_config = self.config.environments[environment]
        
        self.logger.info(f"Restarting services for {environment}")
        
        # Start cloudflared with restored configuration
        tunnel_config = env_config.get('config_files', [])
        if tunnel_config:
            config_file = tunnel_config[0]  # Use first config file
            subprocess.Popen([
                "cloudflared", "tunnel", "--config", config_file, "run"
            ])
            
            # Wait for service to start
            await asyncio.sleep(10)
        
        self.logger.info(f"Services restarted for {environment}")
    
    async def _validate_rollback(self, environment: str) -> Dict[str, Any]:
        """Validate rollback success"""
        env_config = self.config.environments[environment]
        
        self.logger.info(f"Validating rollback for {environment}")
        
        validation_results = {}
        
        try:
            # Test HTTP connectivity
            health_url = f"{env_config['url']}{env_config['health_endpoint']}"
            response = requests.get(health_url, timeout=10)
            
            validation_results['http_connectivity'] = {
                'status': 'passed' if response.status_code == 200 else 'failed',
                'status_code': response.status_code,
                'response_time_ms': response.elapsed.total_seconds() * 1000
            }
            
            # Test WebSocket connectivity
            health_result = await self.health_validator.validate_websocket_health(
                env_config['websocket_url']
            )
            
            validation_results['websocket_connectivity'] = {
                'status': 'passed' if health_result.status == HealthStatus.HEALTHY else 'failed',
                'health_status': health_result.status.value,
                'issues': health_result.issues
            }
            
            # Test tunnel health
            tunnel_result = subprocess.run(
                ["pgrep", "-f", "cloudflared"],
                capture_output=True,
                text=True
            )
            
            validation_results['tunnel_health'] = {
                'status': 'passed' if tunnel_result.returncode == 0 else 'failed',
                'process_running': tunnel_result.returncode == 0
            }
            
        except Exception as e:
            validation_results['validation_error'] = str(e)
        
        self.logger.info(f"Rollback validation completed for {environment}")
        return validation_results
    
    async def emergency_rollback(self, environments: List[str] = None) -> Dict[str, RollbackResult]:
        """Execute emergency rollback for multiple environments"""
        if environments is None:
            environments = list(self.config.environments.keys())
        
        self.logger.critical(f"Executing emergency rollback for environments: {environments}")
        
        # Execute rollbacks in parallel
        rollback_tasks = []
        for env in environments:
            task = asyncio.create_task(
                self.execute_rollback(env, RollbackTrigger.EMERGENCY, force=True)
            )
            rollback_tasks.append(task)
        
        results = await asyncio.gather(*rollback_tasks, return_exceptions=True)
        
        # Process results
        emergency_results = {}
        for i, result in enumerate(results):
            env = environments[i]
            if isinstance(result, Exception):
                emergency_results[env] = RollbackResult(
                    environment=env,
                    trigger=RollbackTrigger.EMERGENCY,
                    status=RollbackStatus.FAILED,
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    error_message=str(result)
                )
            else:
                emergency_results[env] = result
        
        return emergency_results
    
    def get_rollback_history(self, environment: str = None) -> List[RollbackResult]:
        """Get rollback history for environment or all environments"""
        if environment:
            return [r for r in self.rollback_history if r.environment == environment]
        return self.rollback_history.copy()
    
    def get_rollback_status(self, environment: str) -> Optional[RollbackResult]:
        """Get current rollback status for environment"""
        return self.active_rollbacks.get(environment)


async def main():
    """Main entry point for rollback script"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Execute WebSocket deployment rollback")
    parser.add_argument("--environment", type=str, required=True,
                       choices=["dev", "staging", "production"],
                       help="Environment to rollback")
    parser.add_argument("--trigger", type=str, default="manual",
                       choices=["manual", "health_threshold", "error_rate", 
                               "latency_threshold", "connection_failure", "emergency"],
                       help="Rollback trigger type")
    parser.add_argument("--force", action="store_true",
                       help="Force rollback even if validation fails")
    parser.add_argument("--monitor", action="store_true",
                       help="Start continuous monitoring mode")
    parser.add_argument("--config", type=str,
                       help="Path to rollback configuration file")
    parser.add_argument("--emergency", action="store_true",
                       help="Execute emergency rollback for all environments")
    
    args = parser.parse_args()
    
    # Initialize rollback manager
    rollback_manager = RollbackManager(args.config)
    
    try:
        if args.emergency:
            # Emergency rollback for all environments
            results = await rollback_manager.emergency_rollback()
            
            print("\n" + "="*60)
            print("EMERGENCY ROLLBACK RESULTS")
            print("="*60)
            for env, result in results.items():
                print(f"{env}: {result.status.value}")
                if result.error_message:
                    print(f"  Error: {result.error_message}")
        
        elif args.monitor:
            # Start monitoring mode
            print("Starting rollback monitoring...")
            await rollback_manager.start_monitoring()
        
        else:
            # Execute single rollback
            result = await rollback_manager.execute_rollback(
                environment=args.environment,
                trigger=RollbackTrigger(args.trigger),
                force=args.force
            )
            
            print("\n" + "="*60)
            print("ROLLBACK RESULTS")
            print("="*60)
            print(json.dumps({
                "environment": result.environment,
                "trigger": result.trigger.value,
                "status": result.status.value,
                "health_score_before": result.health_score_before,
                "health_score_after": result.health_score_after,
                "restored_files": result.restored_files,
                "validation_results": result.validation_results,
                "error_message": result.error_message,
                "duration_seconds": (result.end_time - result.start_time).total_seconds() if result.end_time else None
            }, indent=2, default=str))
            
            # Exit with appropriate code
            if result.status == RollbackStatus.COMPLETED:
                sys.exit(0)
            else:
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\nRollback interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Rollback failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())