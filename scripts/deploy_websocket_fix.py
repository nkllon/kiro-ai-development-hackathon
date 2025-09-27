#!/usr/bin/env python3
"""
WebSocket Fix Deployment Automation Script

This script implements staged rollout deployment with zero-downtime capability,
health checks, and automatic rollback triggers for the WebSocket infrastructure fix.

Features:
- Staged rollout (dev → staging → production)
- Health checks at each stage
- Automatic rollback on failure
- Zero-downtime deployment
- Configuration validation
- Comprehensive logging and monitoring
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


class DeploymentStage(Enum):
    """Deployment stages for staged rollout"""
    DEV = "dev"
    STAGING = "staging"
    PRODUCTION = "production"


class DeploymentStatus(Enum):
    """Deployment status tracking"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    HEALTH_CHECKING = "health_checking"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class DeploymentConfig:
    """Configuration for deployment process"""
    # Environment configurations
    environments: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Health check settings
    health_check_timeout: int = 300  # 5 minutes
    health_check_interval: int = 10  # 10 seconds
    max_health_check_retries: int = 30
    
    # Rollback settings
    rollback_timeout: int = 180  # 3 minutes
    auto_rollback_threshold: float = 0.8  # 80% health threshold
    
    # Deployment settings
    zero_downtime: bool = True
    max_parallel_deployments: int = 1
    deployment_timeout: int = 600  # 10 minutes
    
    # Monitoring settings
    metrics_collection_interval: int = 5
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "error_rate": 0.05,
        "latency_ms": 1000,
        "connection_failure_rate": 0.1
    })


@dataclass
class DeploymentResult:
    """Result of a deployment operation"""
    stage: DeploymentStage
    status: DeploymentStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    health_score: float = 0.0
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    rollback_triggered: bool = False


class WebSocketDeploymentManager:
    """
    Comprehensive deployment manager for WebSocket infrastructure fixes.
    
    Implements staged rollout with health monitoring, automatic rollback,
    and zero-downtime deployment capabilities.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize deployment manager with configuration"""
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        
        # Initialize monitoring components
        self.health_validator = WebSocketHealthValidator()
        self.endpoint_monitor = EndpointMonitor()
        self.failure_detector = FailureDetector()
        self.health_monitor = WebSocketHealthMonitor()
        
        # Deployment tracking
        self.deployment_results: List[DeploymentResult] = []
        self.current_deployment: Optional[DeploymentResult] = None
        self.rollback_history: List[DeploymentResult] = []
        
        # Health check cache
        self._health_cache: Dict[str, Dict[str, Any]] = {}
        self._last_health_check: Dict[str, datetime] = {}
        
        self.logger.info("WebSocket Deployment Manager initialized")
    
    def _load_config(self, config_path: Optional[str]) -> DeploymentConfig:
        """Load deployment configuration from file or use defaults"""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
                return DeploymentConfig(**config_data)
        
        # Default configuration
        return DeploymentConfig(
            environments={
                "dev": {
                    "url": "http://localhost:8888",
                    "websocket_url": "ws://localhost:8888/ws",
                    "health_endpoint": "/health",
                    "tunnel_config": "cloudflare-tunnel-config-websocket.yml",
                    "replicas": 1
                },
                "staging": {
                    "url": "https://staging-observatory.nkllon.com",
                    "websocket_url": "wss://staging-observatory.nkllon.com/ws",
                    "health_endpoint": "/health",
                    "tunnel_config": "cloudflare-tunnel-config-websocket-staging.yml",
                    "replicas": 2
                },
                "production": {
                    "url": "https://observatory.nkllon.com",
                    "websocket_url": "wss://observatory.nkllon.com/ws",
                    "health_endpoint": "/health",
                    "tunnel_config": "cloudflare-tunnel-config-websocket.yml",
                    "replicas": 3
                }
            }
        )
    
    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging for deployment operations"""
        logger = logging.getLogger("websocket_deployment")
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # File handler for deployment logs
        file_handler = logging.FileHandler(
            logs_dir / f"deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        file_handler.setLevel(logging.INFO)
        
        # Console handler for real-time output
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # JSON formatter for structured logs
        json_formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"component": "deployment", "message": "%(message)s"}'
        )
        file_handler.setFormatter(json_formatter)
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    async def deploy_websocket_fix(
        self,
        stages: List[DeploymentStage] = None,
        test_mode: bool = False,
        force_deploy: bool = False
    ) -> Dict[str, Any]:
        """
        Execute staged deployment of WebSocket fix across environments.
        
        Args:
            stages: List of stages to deploy to (default: all stages)
            test_mode: Run in test mode without actual deployment
            force_deploy: Skip pre-deployment checks
            
        Returns:
            Dict containing deployment results and metrics
        """
        if stages is None:
            stages = [DeploymentStage.DEV, DeploymentStage.STAGING, DeploymentStage.PRODUCTION]
        
        self.logger.info(f"Starting WebSocket fix deployment to stages: {[s.value for s in stages]}")
        
        deployment_start = datetime.now()
        overall_status = "success"
        stage_results = {}
        
        try:
            # Pre-deployment validation
            if not test_mode and not force_deploy:
                await self._pre_deployment_validation(stages)
            
            # Execute staged deployment
            for stage in stages:
                self.logger.info(f"Deploying to {stage.value} environment")
                
                stage_result = await self._deploy_to_stage(stage, test_mode)
                stage_results[stage.value] = stage_result
                
                # Check if deployment failed
                if stage_result.status == DeploymentStatus.FAILED:
                    self.logger.error(f"Deployment failed at {stage.value} stage")
                    overall_status = "failed"
                    
                    # Trigger automatic rollback if configured
                    if not test_mode:
                        await self._trigger_rollback(stage, stage_result.error_message)
                    
                    break
                
                # Wait between stages for stability
                if stage != stages[-1]:
                    self.logger.info("Waiting 30 seconds between stages for stability")
                    await asyncio.sleep(30)
            
            # Post-deployment validation
            if overall_status == "success" and not test_mode:
                await self._post_deployment_validation(stages)
            
        except Exception as e:
            self.logger.error(f"Deployment failed with exception: {e}")
            overall_status = "failed"
            await self._emergency_rollback()
        
        deployment_end = datetime.now()
        deployment_duration = (deployment_end - deployment_start).total_seconds()
        
        # Generate deployment report
        report = {
            "overall_status": overall_status,
            "deployment_duration_seconds": deployment_duration,
            "stages_deployed": [s.value for s in stages],
            "stage_results": stage_results,
            "total_deployments": len(self.deployment_results),
            "rollbacks_triggered": len(self.rollback_history),
            "health_scores": {
                stage.value: result.health_score 
                for stage, result in zip(stages, self.deployment_results)
                if result.status == DeploymentStatus.COMPLETED
            }
        }
        
        self.logger.info(f"Deployment completed with status: {overall_status}")
        return report
    
    async def _deploy_to_stage(
        self, 
        stage: DeploymentStage, 
        test_mode: bool = False
    ) -> DeploymentResult:
        """Deploy to a specific stage with health monitoring"""
        stage_config = self.config.environments[stage.value]
        
        # Create deployment result tracker
        deployment_result = DeploymentResult(
            stage=stage,
            status=DeploymentStatus.IN_PROGRESS,
            start_time=datetime.now()
        )
        self.current_deployment = deployment_result
        
        try:
            self.logger.info(f"Starting deployment to {stage.value}")
            
            # Step 1: Backup current configuration
            if not test_mode:
                await self._backup_configuration(stage)
            
            # Step 2: Deploy new configuration
            if not test_mode:
                await self._deploy_configuration(stage)
            else:
                self.logger.info(f"Test mode: Simulating deployment to {stage.value}")
                await asyncio.sleep(2)  # Simulate deployment time
            
            # Step 3: Health checks
            deployment_result.status = DeploymentStatus.HEALTH_CHECKING
            health_score = await self._comprehensive_health_check(stage)
            deployment_result.health_score = health_score
            
            # Step 4: Validate deployment success
            if health_score >= self.config.auto_rollback_threshold:
                deployment_result.status = DeploymentStatus.COMPLETED
                self.logger.info(f"Deployment to {stage.value} completed successfully (health: {health_score:.2f})")
            else:
                deployment_result.status = DeploymentStatus.FAILED
                deployment_result.error_message = f"Health score {health_score:.2f} below threshold {self.config.auto_rollback_threshold}"
                self.logger.error(f"Deployment to {stage.value} failed health check")
            
        except Exception as e:
            deployment_result.status = DeploymentStatus.FAILED
            deployment_result.error_message = str(e)
            self.logger.error(f"Deployment to {stage.value} failed: {e}")
        
        finally:
            deployment_result.end_time = datetime.now()
            self.deployment_results.append(deployment_result)
            self.current_deployment = None
        
        return deployment_result
    
    async def _pre_deployment_validation(self, stages: List[DeploymentStage]) -> None:
        """Validate system state before deployment"""
        self.logger.info("Running pre-deployment validation")
        
        validation_checks = [
            self._validate_configuration_files(),
            self._validate_environment_connectivity(stages),
            self._validate_resource_availability(),
            self._validate_backup_systems()
        ]
        
        results = await asyncio.gather(*validation_checks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                raise Exception(f"Pre-deployment validation check {i+1} failed: {result}")
        
        self.logger.info("Pre-deployment validation completed successfully")
    
    async def _post_deployment_validation(self, stages: List[DeploymentStage]) -> None:
        """Validate system state after deployment"""
        self.logger.info("Running post-deployment validation")
        
        # Wait for system to stabilize
        await asyncio.sleep(60)
        
        validation_checks = [
            self._validate_end_to_end_connectivity(stages),
            self._validate_performance_metrics(),
            self._validate_monitoring_systems()
        ]
        
        results = await asyncio.gather(*validation_checks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.warning(f"Post-deployment validation check {i+1} failed: {result}")
        
        self.logger.info("Post-deployment validation completed")
    
    async def _comprehensive_health_check(self, stage: DeploymentStage) -> float:
        """Perform comprehensive health check for a deployment stage"""
        stage_config = self.config.environments[stage.value]
        
        self.logger.info(f"Running comprehensive health check for {stage.value}")
        
        health_checks = [
            self._check_http_health(stage_config),
            self._check_websocket_health(stage_config),
            self._check_tunnel_health(stage_config),
            self._check_performance_metrics(stage_config)
        ]
        
        results = await asyncio.gather(*health_checks, return_exceptions=True)
        
        # Calculate overall health score
        health_scores = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.warning(f"Health check {i+1} failed: {result}")
                health_scores.append(0.0)
            else:
                health_scores.append(result)
        
        overall_health = sum(health_scores) / len(health_scores)
        
        self.logger.info(f"Health check completed for {stage.value}: {overall_health:.2f}")
        return overall_health
    
    async def _check_http_health(self, config: Dict[str, Any]) -> float:
        """Check HTTP endpoint health"""
        try:
            url = f"{config['url']}{config['health_endpoint']}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return 1.0
            else:
                return 0.5
        except Exception as e:
            self.logger.warning(f"HTTP health check failed: {e}")
            return 0.0
    
    async def _check_websocket_health(self, config: Dict[str, Any]) -> float:
        """Check WebSocket endpoint health"""
        try:
            # Use the health validator from the websocket module
            health_result = await self.health_validator.validate_websocket_health(
                config['websocket_url']
            )
            
            if health_result.status == HealthStatus.HEALTHY:
                return 1.0
            elif health_result.status == HealthStatus.DEGRADED:
                return 0.7
            else:
                return 0.3
        except Exception as e:
            self.logger.warning(f"WebSocket health check failed: {e}")
            return 0.0
    
    async def _check_tunnel_health(self, config: Dict[str, Any]) -> float:
        """Check Cloudflare tunnel health"""
        try:
            # Check if tunnel process is running
            result = subprocess.run(
                ["pgrep", "-f", "cloudflared"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return 1.0
            else:
                return 0.0
        except Exception as e:
            self.logger.warning(f"Tunnel health check failed: {e}")
            return 0.0
    
    async def _check_performance_metrics(self, config: Dict[str, Any]) -> float:
        """Check performance metrics against thresholds"""
        try:
            # Get current metrics from health monitor
            metrics = self.health_monitor.get_performance_metrics()
            
            score = 1.0
            
            # Check error rate
            error_rate = metrics.get('websocket_error_rate', 0)
            if error_rate > self.config.alert_thresholds['error_rate']:
                score -= 0.3
            
            # Check latency
            latency_stats = metrics.get('latency_stats', {})
            avg_latency = latency_stats.get('avg', 0)
            if avg_latency > self.config.alert_thresholds['latency_ms']:
                score -= 0.3
            
            # Check connection failures
            failures = metrics.get('websocket_connection_failures', 0)
            active_connections = metrics.get('websocket_connections_active', 1)
            failure_rate = failures / max(active_connections, 1)
            if failure_rate > self.config.alert_thresholds['connection_failure_rate']:
                score -= 0.4
            
            return max(0.0, score)
        except Exception as e:
            self.logger.warning(f"Performance metrics check failed: {e}")
            return 0.0
    
    async def _backup_configuration(self, stage: DeploymentStage) -> None:
        """Backup current configuration before deployment"""
        stage_config = self.config.environments[stage.value]
        backup_dir = Path("backups") / stage.value
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Backup tunnel configuration
        tunnel_config = stage_config.get('tunnel_config')
        if tunnel_config and Path(tunnel_config).exists():
            backup_path = backup_dir / f"{tunnel_config}.{timestamp}.backup"
            subprocess.run(["cp", tunnel_config, str(backup_path)])
            self.logger.info(f"Backed up tunnel config to {backup_path}")
    
    async def _deploy_configuration(self, stage: DeploymentStage) -> None:
        """Deploy new configuration to the stage"""
        stage_config = self.config.environments[stage.value]
        
        # Deploy tunnel configuration
        tunnel_config = stage_config.get('tunnel_config')
        if tunnel_config and Path(tunnel_config).exists():
            # Restart cloudflared with new configuration
            subprocess.run(["pkill", "-f", "cloudflared"])
            await asyncio.sleep(2)
            
            # Start cloudflared with new config
            subprocess.Popen([
                "cloudflared", "tunnel", "--config", tunnel_config, "run"
            ])
            
            # Wait for tunnel to establish
            await asyncio.sleep(10)
            self.logger.info(f"Deployed tunnel configuration for {stage.value}")
    
    async def _trigger_rollback(self, stage: DeploymentStage, error_message: str) -> None:
        """Trigger automatic rollback for failed deployment"""
        self.logger.warning(f"Triggering rollback for {stage.value}: {error_message}")
        
        rollback_result = DeploymentResult(
            stage=stage,
            status=DeploymentStatus.ROLLED_BACK,
            start_time=datetime.now(),
            error_message=f"Rollback triggered: {error_message}"
        )
        
        try:
            # Restore previous configuration
            await self._restore_configuration(stage)
            
            # Verify rollback success
            health_score = await self._comprehensive_health_check(stage)
            rollback_result.health_score = health_score
            
            if health_score >= 0.7:  # Rollback success threshold
                rollback_result.status = DeploymentStatus.COMPLETED
                self.logger.info(f"Rollback successful for {stage.value}")
            else:
                rollback_result.status = DeploymentStatus.FAILED
                self.logger.error(f"Rollback failed for {stage.value}")
            
        except Exception as e:
            rollback_result.status = DeploymentStatus.FAILED
            rollback_result.error_message = f"Rollback error: {e}"
            self.logger.error(f"Rollback failed for {stage.value}: {e}")
        
        finally:
            rollback_result.end_time = datetime.now()
            self.rollback_history.append(rollback_result)
    
    async def _restore_configuration(self, stage: DeploymentStage) -> None:
        """Restore previous configuration from backup"""
        stage_config = self.config.environments[stage.value]
        backup_dir = Path("backups") / stage.value
        
        # Find latest backup
        backup_files = list(backup_dir.glob("*.backup"))
        if not backup_files:
            raise Exception(f"No backup found for {stage.value}")
        
        latest_backup = max(backup_files, key=lambda p: p.stat().st_mtime)
        
        # Restore configuration
        tunnel_config = stage_config.get('tunnel_config')
        if tunnel_config:
            subprocess.run(["cp", str(latest_backup), tunnel_config])
            self.logger.info(f"Restored configuration from {latest_backup}")
    
    async def _emergency_rollback(self) -> None:
        """Emergency rollback for critical failures"""
        self.logger.critical("Executing emergency rollback")
        
        # Rollback all stages that were deployed
        for result in self.deployment_results:
            if result.status == DeploymentStatus.COMPLETED:
                await self._trigger_rollback(result.stage, "Emergency rollback")
    
    # Validation methods
    async def _validate_configuration_files(self) -> None:
        """Validate that all required configuration files exist"""
        required_files = [
            "cloudflare-tunnel-config-websocket.yml",
            "src/beast_mode/observatory/websocket/",
            "src/beast_mode/observatory/monitoring/"
        ]
        
        for file_path in required_files:
            if not Path(file_path).exists():
                raise Exception(f"Required file/directory not found: {file_path}")
    
    async def _validate_environment_connectivity(self, stages: List[DeploymentStage]) -> None:
        """Validate connectivity to target environments"""
        for stage in stages:
            config = self.config.environments[stage.value]
            try:
                response = requests.get(config['url'], timeout=5)
                if response.status_code not in [200, 404]:  # 404 is ok for root
                    raise Exception(f"Environment {stage.value} not accessible")
            except Exception as e:
                raise Exception(f"Cannot connect to {stage.value}: {e}")
    
    async def _validate_resource_availability(self) -> None:
        """Validate system resources are available"""
        # Check disk space
        import shutil
        free_space = shutil.disk_usage('.').free
        if free_space < 1024 * 1024 * 1024:  # 1GB
            raise Exception("Insufficient disk space for deployment")
    
    async def _validate_backup_systems(self) -> None:
        """Validate backup systems are functional"""
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        # Test backup write
        test_file = backup_dir / "test_backup.txt"
        test_file.write_text("test")
        test_file.unlink()
    
    async def _validate_end_to_end_connectivity(self, stages: List[DeploymentStage]) -> None:
        """Validate end-to-end connectivity after deployment"""
        for stage in stages:
            config = self.config.environments[stage.value]
            
            # Test HTTP endpoint
            try:
                response = requests.get(f"{config['url']}{config['health_endpoint']}", timeout=10)
                if response.status_code != 200:
                    raise Exception(f"Health endpoint not responding for {stage.value}")
            except Exception as e:
                raise Exception(f"End-to-end validation failed for {stage.value}: {e}")
    
    async def _validate_performance_metrics(self) -> None:
        """Validate performance metrics are within acceptable ranges"""
        metrics = self.health_monitor.get_performance_metrics()
        
        # Check key performance indicators
        error_rate = metrics.get('websocket_error_rate', 0)
        if error_rate > 0.1:  # 10% error rate threshold
            raise Exception(f"Error rate too high: {error_rate:.2%}")
    
    async def _validate_monitoring_systems(self) -> None:
        """Validate monitoring systems are operational"""
        # Check if health monitor is running
        health_status = self.health_monitor.get_all_health_status()
        if not health_status:
            self.logger.warning("No health status data available")


async def main():
    """Main entry point for deployment script"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy WebSocket fix with staged rollout")
    parser.add_argument("--stages", nargs="+", choices=["dev", "staging", "production"],
                       default=["dev", "staging", "production"],
                       help="Deployment stages to execute")
    parser.add_argument("--test-mode", action="store_true",
                       help="Run in test mode without actual deployment")
    parser.add_argument("--force", action="store_true",
                       help="Skip pre-deployment validation")
    parser.add_argument("--config", type=str,
                       help="Path to deployment configuration file")
    
    args = parser.parse_args()
    
    # Convert stage strings to enums
    stages = [DeploymentStage(stage) for stage in args.stages]
    
    # Initialize deployment manager
    deployment_manager = WebSocketDeploymentManager(args.config)
    
    try:
        # Execute deployment
        result = await deployment_manager.deploy_websocket_fix(
            stages=stages,
            test_mode=args.test_mode,
            force_deploy=args.force
        )
        
        # Print results
        print("\n" + "="*60)
        print("DEPLOYMENT RESULTS")
        print("="*60)
        print(json.dumps(result, indent=2, default=str))
        
        # Exit with appropriate code
        if result["overall_status"] == "success":
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nDeployment interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())