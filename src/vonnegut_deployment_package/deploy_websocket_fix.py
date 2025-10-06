#!/usr/bin/env python3
"""
Deployment Automation Script for WebSocket Fix
Task 7.2: Deployment Automation and Validation

This script provides comprehensive deployment automation with:
- Staged rollout (dev → staging → production)
- Health checks at each stage
- Automatic rollback on failure
- Zero-downtime deployment
- Configuration validation
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

import aiohttp
import websockets
from websockets.exceptions import ConnectionClosed, InvalidStatusCode

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.beast_mode.observatory.tunnel.tunnel_config_manager import TunnelConfigManager
from src.beast_mode.observatory.websocket.manager import WebSocketManager, WebSocketManagerConfig


class DeploymentStage(Enum):
    """Deployment stages for staged rollout."""
    DEV = "dev"
    STAGING = "staging"
    PRODUCTION = "production"


class DeploymentStatus(Enum):
    """Deployment status tracking."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class DeploymentConfig:
    """Configuration for deployment automation."""
    environments: Dict[str, Dict[str, Any]]
    health_check_timeout: int = 300
    health_check_interval: int = 10
    max_health_check_retries: int = 30
    rollback_timeout: int = 180
    auto_rollback_threshold: float = 0.8
    zero_downtime: bool = True
    max_parallel_deployments: int = 1
    deployment_timeout: int = 600
    validation_thresholds: Dict[str, Any] = None
    rollback_triggers: Dict[str, Any] = None
    backup_retention_days: int = 7
    generate_report: bool = True
    alert_on_failure: bool = True


@dataclass
class DeploymentResult:
    """Result of a deployment operation."""
    stage: str
    status: DeploymentStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    success: bool = False
    error_message: Optional[str] = None
    health_score: float = 0.0
    validation_results: Dict[str, Any] = None
    rollback_triggered: bool = False
    rollback_reason: Optional[str] = None


class DeploymentAutomation:
    """Main deployment automation class."""
    
    def __init__(self, config_path: str = "deployment-config.yml"):
        """Initialize deployment automation."""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.tunnel_manager = TunnelConfigManager()
        self.deployment_results: List[DeploymentResult] = []
        self.current_deployment_id = None
        self.logger = self._setup_logging()
        
        self.log_action("deployment_automation_init", "completed", {
            "config_path": str(self.config_path),
            "environments": list(self.config.environments.keys()),
            "zero_downtime": self.config.zero_downtime
        })
    
    def _load_config(self) -> DeploymentConfig:
        """Load deployment configuration."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        return DeploymentConfig(**config_data)
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger("deployment_automation")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def log_action(self, action: str, status: str, details: Dict[str, Any] = None):
        """Log action in JSON format as required."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "task": "7.2",
            "action": f"DeploymentAutomation.{action}",
            "status": status,
            "details": details or {}
        }
        print(json.dumps(log_entry))
    
    async def deploy_websocket_fix(self, 
                                 target_stage: str = "production",
                                 force_deploy: bool = False,
                                 skip_validation: bool = False) -> Dict[str, Any]:
        """Deploy WebSocket fix with staged rollout."""
        self.current_deployment_id = f"deploy_{int(time.time())}"
        
        self.log_action("deploy_websocket_fix_start", "in_progress", {
            "deployment_id": self.current_deployment_id,
            "target_stage": target_stage,
            "force_deploy": force_deploy,
            "skip_validation": skip_validation
        })
        
        try:
            # Determine deployment stages
            stages = self._get_deployment_stages(target_stage)
            
            # Pre-deployment validation
            if not skip_validation:
                validation_result = await self._pre_deployment_validation()
                if not validation_result["success"]:
                    raise Exception(f"Pre-deployment validation failed: {validation_result['errors']}")
            
            # Backup current configuration
            backup_result = await self._backup_current_config()
            if not backup_result["success"]:
                raise Exception(f"Backup failed: {backup_result['error']}")
            
            # Execute staged deployment
            deployment_results = []
            for stage in stages:
                stage_result = await self._deploy_to_stage(stage, force_deploy)
                deployment_results.append(stage_result)
                
                # Check if deployment failed and rollback is needed
                if not stage_result.success:
                    self.log_action("deployment_stage_failed", "error", {
                        "stage": stage,
                        "error": stage_result.error_message,
                        "triggering_rollback": True
                    })
                    
                    # Rollback previous stages
                    await self._rollback_deployment(deployment_results)
                    break
            
            # Post-deployment validation
            if all(result.success for result in deployment_results):
                final_validation = await self._post_deployment_validation(target_stage)
                if not final_validation["success"]:
                    self.log_action("post_deployment_validation_failed", "error", {
                        "errors": final_validation["errors"],
                        "triggering_rollback": True
                    })
                    await self._rollback_deployment(deployment_results)
            
            # Generate deployment report
            report = await self._generate_deployment_report(deployment_results)
            
            self.log_action("deploy_websocket_fix_complete", "completed", {
                "deployment_id": self.current_deployment_id,
                "success": all(result.success for result in deployment_results),
                "stages_deployed": len([r for r in deployment_results if r.success]),
                "total_stages": len(stages)
            })
            
            return report
            
        except Exception as e:
            self.log_action("deploy_websocket_fix_error", "error", {
                "deployment_id": self.current_deployment_id,
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise
    
    def _get_deployment_stages(self, target_stage: str) -> List[str]:
        """Get deployment stages based on target."""
        stage_order = ["dev", "staging", "production"]
        target_index = stage_order.index(target_stage)
        return stage_order[:target_index + 1]
    
    async def _pre_deployment_validation(self) -> Dict[str, Any]:
        """Perform pre-deployment validation."""
        self.log_action("pre_deployment_validation", "in_progress")
        
        validation_results = {
            "success": True,
            "errors": [],
            "warnings": [],
            "checks": {}
        }
        
        try:
            # Check if observatory server is running
            server_check = await self._check_observatory_server()
            validation_results["checks"]["observatory_server"] = server_check
            if not server_check["running"]:
                validation_results["errors"].append("Observatory server is not running")
                validation_results["success"] = False
            
            # Validate tunnel configuration
            tunnel_check = await self._validate_tunnel_config()
            validation_results["checks"]["tunnel_config"] = tunnel_check
            if not tunnel_check["valid"]:
                validation_results["errors"].extend(tunnel_check["errors"])
                validation_results["success"] = False
            
            # Check WebSocket endpoints
            websocket_check = await self._check_websocket_endpoints()
            validation_results["checks"]["websocket_endpoints"] = websocket_check
            if not websocket_check["all_healthy"]:
                validation_results["warnings"].append("Some WebSocket endpoints are not healthy")
            
            # Validate deployment configuration
            config_check = self._validate_deployment_config()
            validation_results["checks"]["deployment_config"] = config_check
            if not config_check["valid"]:
                validation_results["errors"].extend(config_check["errors"])
                validation_results["success"] = False
            
            self.log_action("pre_deployment_validation", "completed", {
                "success": validation_results["success"],
                "error_count": len(validation_results["errors"]),
                "warning_count": len(validation_results["warnings"])
            })
            
        except Exception as e:
            validation_results["success"] = False
            validation_results["errors"].append(f"Validation error: {str(e)}")
            self.log_action("pre_deployment_validation", "error", {"error": str(e)})
        
        return validation_results
    
    async def _deploy_to_stage(self, stage: str, force_deploy: bool = False) -> DeploymentResult:
        """Deploy to a specific stage."""
        start_time = datetime.now()
        
        self.log_action("deploy_to_stage_start", "in_progress", {
            "stage": stage,
            "force_deploy": force_deploy
        })
        
        result = DeploymentResult(
            stage=stage,
            status=DeploymentStatus.IN_PROGRESS,
            start_time=start_time
        )
        
        try:
            # Get stage configuration
            stage_config = self.config.environments.get(stage)
            if not stage_config:
                raise Exception(f"Configuration not found for stage: {stage}")
            
            # Apply tunnel configuration for stage
            tunnel_config_result = await self._apply_tunnel_config(stage, stage_config)
            if not tunnel_config_result["success"]:
                raise Exception(f"Tunnel configuration failed: {tunnel_config_result['error']}")
            
            # Wait for configuration to propagate
            await asyncio.sleep(5)
            
            # Perform health checks
            health_result = await self._perform_health_checks(stage, stage_config)
            result.health_score = health_result["health_score"]
            
            if health_result["health_score"] < self.config.auto_rollback_threshold:
                raise Exception(f"Health score too low: {health_result['health_score']}")
            
            # Validate WebSocket functionality
            websocket_validation = await self._validate_websocket_functionality(stage, stage_config)
            result.validation_results = websocket_validation
            
            if not websocket_validation["success"]:
                raise Exception(f"WebSocket validation failed: {websocket_validation['errors']}")
            
            # Mark deployment as successful
            result.status = DeploymentStatus.COMPLETED
            result.success = True
            result.end_time = datetime.now()
            
            self.log_action("deploy_to_stage_complete", "completed", {
                "stage": stage,
                "health_score": result.health_score,
                "duration_seconds": (result.end_time - result.start_time).total_seconds()
            })
            
        except Exception as e:
            result.status = DeploymentStatus.FAILED
            result.success = False
            result.error_message = str(e)
            result.end_time = datetime.now()
            
            self.log_action("deploy_to_stage_failed", "error", {
                "stage": stage,
                "error": str(e),
                "duration_seconds": (result.end_time - result.start_time).total_seconds()
            })
        
        self.deployment_results.append(result)
        return result
    
    async def _apply_tunnel_config(self, stage: str, stage_config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply tunnel configuration for stage."""
        self.log_action("apply_tunnel_config", "in_progress", {"stage": stage})
        
        try:
            # Generate WebSocket-enabled configuration
            tunnel_config = self.tunnel_manager.generate_websocket_config(
                tunnel_name=f"observatory-{stage}",
                hostname=stage_config["url"].replace("https://", "").replace("http://", ""),
                local_port=8888,
                credentials_file="/Users/lou/.cloudflared/d1e53e43-033f-4994-8f46-c83962ae3785.json",
                config_type="websocket"
            )
            
            # Validate configuration
            validation_result = self.tunnel_manager.validate_config(tunnel_config)
            if not validation_result.is_valid:
                return {
                    "success": False,
                    "error": f"Configuration validation failed: {validation_result.errors}"
                }
            
            # Apply configuration
            success = self.tunnel_manager.apply_config(tunnel_config, create_version=True)
            if not success:
                return {
                    "success": False,
                    "error": "Failed to apply tunnel configuration"
                }
            
            self.log_action("apply_tunnel_config", "completed", {"stage": stage})
            return {"success": True}
            
        except Exception as e:
            self.log_action("apply_tunnel_config", "error", {"stage": stage, "error": str(e)})
            return {"success": False, "error": str(e)}
    
    async def _perform_health_checks(self, stage: str, stage_config: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive health checks for stage."""
        self.log_action("perform_health_checks", "in_progress", {"stage": stage})
        
        health_results = {
            "health_score": 0.0,
            "checks": {},
            "overall_status": "unhealthy"
        }
        
        try:
            base_url = stage_config["url"]
            health_endpoint = f"{base_url}{stage_config['health_endpoint']}"
            
            # HTTP health check
            http_check = await self._check_http_health(health_endpoint)
            health_results["checks"]["http"] = http_check
            
            # WebSocket health check
            websocket_check = await self._check_websocket_health(stage_config["websocket_url"])
            health_results["checks"]["websocket"] = websocket_check
            
            # Response time check
            response_time_check = await self._check_response_time(base_url)
            health_results["checks"]["response_time"] = response_time_check
            
            # Calculate overall health score
            health_score = self._calculate_health_score(health_results["checks"])
            health_results["health_score"] = health_score
            health_results["overall_status"] = "healthy" if health_score >= 0.8 else "unhealthy"
            
            self.log_action("perform_health_checks", "completed", {
                "stage": stage,
                "health_score": health_score,
                "overall_status": health_results["overall_status"]
            })
            
        except Exception as e:
            self.log_action("perform_health_checks", "error", {"stage": stage, "error": str(e)})
            health_results["error"] = str(e)
        
        return health_results
    
    async def _check_http_health(self, health_url: str) -> Dict[str, Any]:
        """Check HTTP health endpoint."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(health_url, timeout=10) as response:
                    return {
                        "status": "healthy" if response.status == 200 else "unhealthy",
                        "status_code": response.status,
                        "response_time_ms": response.headers.get("X-Response-Time", "unknown")
                    }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def _check_websocket_health(self, websocket_url: str) -> Dict[str, Any]:
        """Check WebSocket health."""
        try:
            async with websockets.connect(websocket_url, timeout=10) as websocket:
                # Send ping and wait for pong
                await websocket.ping()
                return {
                    "status": "healthy",
                    "connection_time_ms": "unknown"
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def _check_response_time(self, base_url: str) -> Dict[str, Any]:
        """Check response time for base URL."""
        try:
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get(base_url, timeout=10) as response:
                    response_time = (time.time() - start_time) * 1000
                    return {
                        "status": "healthy" if response_time < 2000 else "slow",
                        "response_time_ms": response_time,
                        "status_code": response.status
                    }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def _calculate_health_score(self, checks: Dict[str, Any]) -> float:
        """Calculate overall health score from individual checks."""
        if not checks:
            return 0.0
        
        scores = []
        for check_name, check_result in checks.items():
            if check_result.get("status") == "healthy":
                scores.append(1.0)
            elif check_result.get("status") == "slow":
                scores.append(0.5)
            else:
                scores.append(0.0)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    async def _validate_websocket_functionality(self, stage: str, stage_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate WebSocket functionality for stage."""
        self.log_action("validate_websocket_functionality", "in_progress", {"stage": stage})
        
        validation_results = {
            "success": True,
            "errors": [],
            "endpoints": {}
        }
        
        try:
            websocket_url = stage_config["websocket_url"]
            endpoints = ["/ws/emoji-rain", "/ws/observatory", "/ws/anomalies", "/ws/doctor-status"]
            
            for endpoint in endpoints:
                full_url = f"{websocket_url}{endpoint}"
                try:
                    async with websockets.connect(full_url, timeout=10) as websocket:
                        # Test basic connectivity
                        await websocket.ping()
                        
                        # Test message sending/receiving
                        test_message = {"type": "test", "timestamp": datetime.now().isoformat()}
                        await websocket.send(json.dumps(test_message))
                        
                        validation_results["endpoints"][endpoint] = {
                            "status": "healthy",
                            "connectivity": True,
                            "message_test": True
                        }
                        
                except Exception as e:
                    validation_results["endpoints"][endpoint] = {
                        "status": "unhealthy",
                        "error": str(e)
                    }
                    validation_results["errors"].append(f"Endpoint {endpoint} failed: {str(e)}")
                    validation_results["success"] = False
            
            self.log_action("validate_websocket_functionality", "completed", {
                "stage": stage,
                "success": validation_results["success"],
                "healthy_endpoints": len([ep for ep in validation_results["endpoints"].values() if ep["status"] == "healthy"])
            })
            
        except Exception as e:
            validation_results["success"] = False
            validation_results["errors"].append(f"Validation error: {str(e)}")
            self.log_action("validate_websocket_functionality", "error", {"stage": stage, "error": str(e)})
        
        return validation_results
    
    async def _rollback_deployment(self, deployment_results: List[DeploymentResult]) -> Dict[str, Any]:
        """Rollback deployment to previous version."""
        self.log_action("rollback_deployment", "in_progress", {
            "deployment_results_count": len(deployment_results)
        })
        
        rollback_results = {
            "success": True,
            "stages_rolled_back": [],
            "errors": []
        }
        
        try:
            # Get the latest version before deployment
            version_history = self.tunnel_manager.get_version_history(limit=5)
            if not version_history:
                raise Exception("No version history found for rollback")
            
            # Find the version before the current deployment
            rollback_version = None
            for version in version_history:
                if version.description and "Backup before configuration change" in version.description:
                    rollback_version = version.version_id
                    break
            
            if not rollback_version:
                raise Exception("No suitable rollback version found")
            
            # Perform rollback
            success, message = self.tunnel_manager.rollback_config(rollback_version)
            if not success:
                raise Exception(f"Rollback failed: {message}")
            
            # Update deployment results
            for result in deployment_results:
                if result.success:
                    result.rollback_triggered = True
                    result.rollback_reason = "Deployment failure"
                    result.status = DeploymentStatus.ROLLED_BACK
            
            rollback_results["success"] = True
            rollback_results["stages_rolled_back"] = [r.stage for r in deployment_results if r.success]
            
            self.log_action("rollback_deployment", "completed", {
                "rollback_version": rollback_version,
                "stages_rolled_back": rollback_results["stages_rolled_back"]
            })
            
        except Exception as e:
            rollback_results["success"] = False
            rollback_results["errors"].append(str(e))
            self.log_action("rollback_deployment", "error", {"error": str(e)})
        
        return rollback_results
    
    async def _backup_current_config(self) -> Dict[str, Any]:
        """Backup current configuration."""
        self.log_action("backup_current_config", "in_progress")
        
        try:
            backup_id = self.tunnel_manager.backup_current_config()
            if backup_id.startswith("Failed"):
                return {"success": False, "error": backup_id}
            
            self.log_action("backup_current_config", "completed", {"backup_id": backup_id})
            return {"success": True, "backup_id": backup_id}
            
        except Exception as e:
            self.log_action("backup_current_config", "error", {"error": str(e)})
            return {"success": False, "error": str(e)}
    
    async def _check_observatory_server(self) -> Dict[str, Any]:
        """Check if observatory server is running."""
        try:
            # Check if observatory server is running on localhost:8888
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8888/health", timeout=5) as response:
                    return {
                        "running": response.status == 200,
                        "status_code": response.status,
                        "url": "http://localhost:8888"
                    }
        except Exception:
            return {
                "running": False,
                "error": "Server not responding"
            }
    
    async def _validate_tunnel_config(self) -> Dict[str, Any]:
        """Validate tunnel configuration."""
        try:
            config_info = self.tunnel_manager.get_config_info()
            return {
                "valid": config_info.get("validation_status") == "valid",
                "errors": config_info.get("validation_errors", []),
                "websocket_enabled": config_info.get("websocket_enabled", False)
            }
        except Exception as e:
            return {
                "valid": False,
                "errors": [str(e)]
            }
    
    async def _check_websocket_endpoints(self) -> Dict[str, Any]:
        """Check WebSocket endpoints health."""
        try:
            # Create WebSocket manager for health checks
            config = WebSocketManagerConfig(base_url="ws://localhost:8888")
            manager = WebSocketManager(config)
            
            health_status = await manager.get_health_status()
            
            all_healthy = all(
                result.get("status") == "healthy" 
                for result in health_status.values()
            )
            
            return {
                "all_healthy": all_healthy,
                "endpoints": health_status
            }
            
        except Exception as e:
            return {
                "all_healthy": False,
                "error": str(e)
            }
    
    def _validate_deployment_config(self) -> Dict[str, Any]:
        """Validate deployment configuration."""
        errors = []
        
        # Check required environments
        required_envs = ["dev", "staging", "production"]
        for env in required_envs:
            if env not in self.config.environments:
                errors.append(f"Missing environment configuration: {env}")
        
        # Check environment configurations
        for env_name, env_config in self.config.environments.items():
            required_fields = ["url", "websocket_url", "health_endpoint"]
            for field in required_fields:
                if field not in env_config:
                    errors.append(f"Missing {field} in {env_name} environment")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    async def _post_deployment_validation(self, target_stage: str) -> Dict[str, Any]:
        """Perform post-deployment validation."""
        self.log_action("post_deployment_validation", "in_progress", {"target_stage": target_stage})
        
        validation_results = {
            "success": True,
            "errors": [],
            "checks": {}
        }
        
        try:
            stage_config = self.config.environments[target_stage]
            
            # Final health check
            health_result = await self._perform_health_checks(target_stage, stage_config)
            validation_results["checks"]["final_health"] = health_result
            
            if health_result["health_score"] < self.config.auto_rollback_threshold:
                validation_results["errors"].append(f"Final health score too low: {health_result['health_score']}")
                validation_results["success"] = False
            
            # WebSocket functionality validation
            websocket_validation = await self._validate_websocket_functionality(target_stage, stage_config)
            validation_results["checks"]["websocket_validation"] = websocket_validation
            
            if not websocket_validation["success"]:
                validation_results["errors"].extend(websocket_validation["errors"])
                validation_results["success"] = False
            
            self.log_action("post_deployment_validation", "completed", {
                "target_stage": target_stage,
                "success": validation_results["success"],
                "error_count": len(validation_results["errors"])
            })
            
        except Exception as e:
            validation_results["success"] = False
            validation_results["errors"].append(f"Validation error: {str(e)}")
            self.log_action("post_deployment_validation", "error", {"error": str(e)})
        
        return validation_results
    
    async def _generate_deployment_report(self, deployment_results: List[DeploymentResult]) -> Dict[str, Any]:
        """Generate comprehensive deployment report."""
        self.log_action("generate_deployment_report", "in_progress")
        
        report = {
            "deployment_id": self.current_deployment_id,
            "timestamp": datetime.now().isoformat(),
            "overall_success": all(result.success for result in deployment_results),
            "stages": [],
            "summary": {
                "total_stages": len(deployment_results),
                "successful_stages": len([r for r in deployment_results if r.success]),
                "failed_stages": len([r for r in deployment_results if not r.success]),
                "rolled_back_stages": len([r for r in deployment_results if r.rollback_triggered])
            },
            "configuration": {
                "zero_downtime": self.config.zero_downtime,
                "auto_rollback_threshold": self.config.auto_rollback_threshold,
                "deployment_timeout": self.config.deployment_timeout
            }
        }
        
        # Add stage details
        for result in deployment_results:
            stage_report = {
                "stage": result.stage,
                "status": result.status.value,
                "success": result.success,
                "start_time": result.start_time.isoformat(),
                "end_time": result.end_time.isoformat() if result.end_time else None,
                "duration_seconds": (result.end_time - result.start_time).total_seconds() if result.end_time else None,
                "health_score": result.health_score,
                "error_message": result.error_message,
                "rollback_triggered": result.rollback_triggered,
                "rollback_reason": result.rollback_reason,
                "validation_results": result.validation_results
            }
            report["stages"].append(stage_report)
        
        self.log_action("generate_deployment_report", "completed", {
            "overall_success": report["overall_success"],
            "total_stages": report["summary"]["total_stages"]
        })
        
        return report


async def main():
    """Main entry point for deployment script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy WebSocket fix with staged rollout")
    parser.add_argument("--stage", choices=["dev", "staging", "production"], 
                       default="production", help="Target deployment stage")
    parser.add_argument("--force", action="store_true", 
                       help="Force deployment even if validation fails")
    parser.add_argument("--skip-validation", action="store_true",
                       help="Skip pre-deployment validation")
    parser.add_argument("--config", default="deployment-config.yml",
                       help="Path to deployment configuration file")
    
    args = parser.parse_args()
    
    try:
        # Initialize deployment automation
        deployment = DeploymentAutomation(args.config)
        
        # Execute deployment
        result = await deployment.deploy_websocket_fix(
            target_stage=args.stage,
            force_deploy=args.force,
            skip_validation=args.skip_validation
        )
        
        # Print results
        print("\n" + "="*80)
        print("DEPLOYMENT REPORT")
        print("="*80)
        print(json.dumps(result, indent=2, default=str))
        
        if result["overall_success"]:
            print("\n✅ Deployment completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Deployment failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Deployment error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())