#!/usr/bin/env python3
"""
Automated Rollback System for WebSocket Deployment
Task 7.2: Deployment Automation and Validation

This script provides comprehensive rollback capabilities including:
- Automatic rollback triggers based on health metrics
- Manual rollback to specific versions
- Emergency rollback procedures
- Rollback validation and verification
- Rollback reporting and logging
"""

import asyncio
import json
import logging
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
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.beast_mode.observatory.tunnel.tunnel_config_manager import TunnelConfigManager
from src.beast_mode.observatory.websocket.manager import WebSocketManager, WebSocketManagerConfig


class RollbackTrigger(Enum):
    """Rollback trigger types."""
    MANUAL = "manual"
    HEALTH_THRESHOLD = "health_threshold"
    ERROR_RATE = "error_rate"
    LATENCY_THRESHOLD = "latency_threshold"
    CONNECTION_FAILURE = "connection_failure"
    VALIDATION_FAILURE = "validation_failure"
    EMERGENCY = "emergency"


class RollbackStatus(Enum):
    """Rollback status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"


@dataclass
class RollbackTriggerConfig:
    """Configuration for rollback triggers."""
    enabled: bool
    threshold: float
    check_interval: int  # seconds
    cooldown_period: int = 300  # 5 minutes default
    last_triggered: Optional[datetime] = None


@dataclass
class RollbackPlan:
    """Rollback plan with execution details."""
    rollback_id: str
    trigger: RollbackTrigger
    target_version: str
    current_version: str
    environment: str
    reason: str
    created_at: datetime
    status: RollbackStatus = RollbackStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    verification_results: Dict[str, Any] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.verification_results is None:
            self.verification_results = {}


@dataclass
class RollbackMetrics:
    """Metrics for rollback decision making."""
    health_score: float
    error_rate: float
    latency_ms: float
    connection_failure_rate: float
    timestamp: datetime
    environment: str


class RollbackAutomation:
    """Automated rollback system with monitoring and triggers."""
    
    def __init__(self, config_path: str = "deployment-config.yml"):
        """Initialize rollback automation."""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.tunnel_manager = TunnelConfigManager()
        self.logger = self._setup_logging()
        
        # Rollback state
        self.active_rollbacks: Dict[str, RollbackPlan] = {}
        self.rollback_history: List[RollbackPlan] = []
        self.monitoring_active = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # Trigger configurations
        self.trigger_configs = self._load_trigger_configs()
        
        self.log_action("rollback_automation_init", "completed", {
            "config_path": str(self.config_path),
            "environments": list(self.config["environments"].keys()),
            "triggers_enabled": len([t for t in self.trigger_configs.values() if t.enabled])
        })
    
    def _load_config(self) -> Dict[str, Any]:
        """Load deployment configuration."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _load_trigger_configs(self) -> Dict[str, RollbackTriggerConfig]:
        """Load rollback trigger configurations."""
        rollback_triggers = self.config.get("rollback_triggers", {})
        
        configs = {}
        for trigger_name, config in rollback_triggers.items():
            configs[trigger_name] = RollbackTriggerConfig(
                enabled=config.get("enabled", False),
                threshold=config.get("threshold", 0.0),
                check_interval=config.get("check_interval", 60),
                cooldown_period=config.get("cooldown_period", 300)
            )
        
        return configs
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger("rollback_automation")
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
            "action": f"RollbackAutomation.{action}",
            "status": status,
            "details": details or {}
        }
        print(json.dumps(log_entry))
    
    async def start_monitoring(self) -> None:
        """Start continuous monitoring for rollback triggers."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        self.log_action("start_monitoring", "completed", {
            "monitoring_active": True,
            "triggers_monitored": len([t for t in self.trigger_configs.values() if t.enabled])
        })
    
    async def stop_monitoring(self) -> None:
        """Stop continuous monitoring."""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        self.log_action("stop_monitoring", "completed", {
            "monitoring_active": False
        })
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop for rollback triggers."""
        while self.monitoring_active:
            try:
                self.log_action("monitoring_cycle_start", "in_progress")
                
                # Check each environment for rollback triggers
                for environment in self.config["environments"].keys():
                    await self._check_rollback_triggers(environment)
                
                self.log_action("monitoring_cycle_complete", "completed")
                
                # Wait for next check cycle
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.log_action("monitoring_cycle_error", "error", {"error": str(e)})
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _check_rollback_triggers(self, environment: str) -> None:
        """Check rollback triggers for a specific environment."""
        try:
            # Collect current metrics
            metrics = await self._collect_metrics(environment)
            
            # Check each trigger
            for trigger_name, trigger_config in self.trigger_configs.items():
                if not trigger_config.enabled:
                    continue
                
                # Check cooldown period
                if trigger_config.last_triggered:
                    time_since_last = datetime.now() - trigger_config.last_triggered
                    if time_since_last.total_seconds() < trigger_config.cooldown_period:
                        continue
                
                # Check trigger condition
                should_rollback, reason = await self._evaluate_trigger(
                    trigger_name, trigger_config, metrics
                )
                
                if should_rollback:
                    await self._trigger_rollback(
                        environment, trigger_name, reason, metrics
                    )
                    trigger_config.last_triggered = datetime.now()
                    
        except Exception as e:
            self.log_action("check_rollback_triggers_error", "error", {
                "environment": environment,
                "error": str(e)
            })
    
    async def _collect_metrics(self, environment: str) -> RollbackMetrics:
        """Collect current metrics for environment."""
        env_config = self.config["environments"][environment]
        
        try:
            # Health score
            health_score = await self._calculate_health_score(environment, env_config)
            
            # Error rate
            error_rate = await self._calculate_error_rate(environment, env_config)
            
            # Latency
            latency_ms = await self._calculate_latency(environment, env_config)
            
            # Connection failure rate
            connection_failure_rate = await self._calculate_connection_failure_rate(environment, env_config)
            
            return RollbackMetrics(
                health_score=health_score,
                error_rate=error_rate,
                latency_ms=latency_ms,
                connection_failure_rate=connection_failure_rate,
                timestamp=datetime.now(),
                environment=environment
            )
            
        except Exception as e:
            self.log_action("collect_metrics_error", "error", {
                "environment": environment,
                "error": str(e)
            })
            # Return default metrics on error
            return RollbackMetrics(
                health_score=0.0,
                error_rate=1.0,
                latency_ms=9999.0,
                connection_failure_rate=1.0,
                timestamp=datetime.now(),
                environment=environment
            )
    
    async def _calculate_health_score(self, environment: str, env_config: Dict[str, Any]) -> float:
        """Calculate health score for environment."""
        try:
            health_url = f"{env_config['url']}{env_config['health_endpoint']}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(health_url, timeout=10) as response:
                    if response.status == 200:
                        return 1.0
                    else:
                        return 0.0
                        
        except Exception:
            return 0.0
    
    async def _calculate_error_rate(self, environment: str, env_config: Dict[str, Any]) -> float:
        """Calculate error rate for environment."""
        try:
            base_url = env_config["url"]
            error_count = 0
            total_requests = 10
            
            async with aiohttp.ClientSession() as session:
                for _ in range(total_requests):
                    try:
                        async with session.get(base_url, timeout=5) as response:
                            if response.status >= 400:
                                error_count += 1
                    except Exception:
                        error_count += 1
            
            return error_count / total_requests if total_requests > 0 else 0.0
            
        except Exception:
            return 1.0
    
    async def _calculate_latency(self, environment: str, env_config: Dict[str, Any]) -> float:
        """Calculate average latency for environment."""
        try:
            base_url = env_config["url"]
            latencies = []
            
            async with aiohttp.ClientSession() as session:
                for _ in range(5):
                    start_time = time.time()
                    try:
                        async with session.get(base_url, timeout=10) as response:
                            latency = (time.time() - start_time) * 1000
                            latencies.append(latency)
                    except Exception:
                        latencies.append(9999.0)
            
            return sum(latencies) / len(latencies) if latencies else 9999.0
            
        except Exception:
            return 9999.0
    
    async def _calculate_connection_failure_rate(self, environment: str, env_config: Dict[str, Any]) -> float:
        """Calculate WebSocket connection failure rate."""
        try:
            websocket_url = env_config["websocket_url"]
            failed_connections = 0
            total_attempts = 5
            
            for _ in range(total_attempts):
                try:
                    async with websockets.connect(websocket_url, timeout=5) as websocket:
                        await websocket.ping()
                except Exception:
                    failed_connections += 1
            
            return failed_connections / total_attempts if total_attempts > 0 else 0.0
            
        except Exception:
            return 1.0
    
    async def _evaluate_trigger(self, trigger_name: str, trigger_config: RollbackTriggerConfig, 
                              metrics: RollbackMetrics) -> Tuple[bool, str]:
        """Evaluate if a trigger condition is met."""
        try:
            if trigger_name == "health_threshold":
                if metrics.health_score < trigger_config.threshold:
                    return True, f"Health score {metrics.health_score:.2f} below threshold {trigger_config.threshold}"
            
            elif trigger_name == "error_rate":
                if metrics.error_rate > trigger_config.threshold:
                    return True, f"Error rate {metrics.error_rate:.2f} above threshold {trigger_config.threshold}"
            
            elif trigger_name == "latency_threshold":
                if metrics.latency_ms > trigger_config.threshold:
                    return True, f"Latency {metrics.latency_ms:.1f}ms above threshold {trigger_config.threshold}ms"
            
            elif trigger_name == "connection_failure":
                if metrics.connection_failure_rate > trigger_config.threshold:
                    return True, f"Connection failure rate {metrics.connection_failure_rate:.2f} above threshold {trigger_config.threshold}"
            
            return False, "Trigger condition not met"
            
        except Exception as e:
            return False, f"Error evaluating trigger: {str(e)}"
    
    async def _trigger_rollback(self, environment: str, trigger_name: str, 
                               reason: str, metrics: RollbackMetrics) -> None:
        """Trigger automatic rollback."""
        self.log_action("trigger_rollback", "in_progress", {
            "environment": environment,
            "trigger": trigger_name,
            "reason": reason
        })
        
        try:
            # Create rollback plan
            rollback_id = f"auto_{trigger_name}_{int(time.time())}"
            
            # Get current and target versions
            version_history = self.tunnel_manager.get_version_history(limit=5)
            if not version_history:
                raise Exception("No version history available for rollback")
            
            current_version = version_history[0].version_id if version_history else "unknown"
            target_version = None
            
            # Find a suitable rollback version
            for version in version_history[1:]:
                if version.description and "Backup before configuration change" in version.description:
                    target_version = version.version_id
                    break
            
            if not target_version:
                raise Exception("No suitable rollback version found")
            
            # Create rollback plan
            plan = RollbackPlan(
                rollback_id=rollback_id,
                trigger=RollbackTrigger(trigger_name),
                target_version=target_version,
                current_version=current_version,
                environment=environment,
                reason=reason,
                created_at=datetime.now()
            )
            
            # Execute rollback
            await self._execute_rollback(plan)
            
        except Exception as e:
            self.log_action("trigger_rollback_error", "error", {
                "environment": environment,
                "trigger": trigger_name,
                "error": str(e)
            })
    
    async def manual_rollback(self, environment: str, target_version: str, 
                            reason: str = "Manual rollback") -> Dict[str, Any]:
        """Execute manual rollback to specific version."""
        self.log_action("manual_rollback", "in_progress", {
            "environment": environment,
            "target_version": target_version,
            "reason": reason
        })
        
        try:
            # Get current version
            version_history = self.tunnel_manager.get_version_history(limit=1)
            current_version = version_history[0].version_id if version_history else "unknown"
            
            # Create rollback plan
            rollback_id = f"manual_{int(time.time())}"
            plan = RollbackPlan(
                rollback_id=rollback_id,
                trigger=RollbackTrigger.MANUAL,
                target_version=target_version,
                current_version=current_version,
                environment=environment,
                reason=reason,
                created_at=datetime.now()
            )
            
            # Execute rollback
            result = await self._execute_rollback(plan)
            
            self.log_action("manual_rollback", "completed", {
                "rollback_id": rollback_id,
                "success": result["success"]
            })
            
            return result
            
        except Exception as e:
            self.log_action("manual_rollback_error", "error", {
                "environment": environment,
                "target_version": target_version,
                "error": str(e)
            })
            return {
                "success": False,
                "error": str(e),
                "rollback_id": None
            }
    
    async def emergency_rollback(self, environment: str, reason: str = "Emergency rollback") -> Dict[str, Any]:
        """Execute emergency rollback to latest stable version."""
        self.log_action("emergency_rollback", "in_progress", {
            "environment": environment,
            "reason": reason
        })
        
        try:
            # Find the most recent stable version
            version_history = self.tunnel_manager.get_version_history(limit=10)
            target_version = None
            
            for version in version_history:
                if version.description and "Backup before configuration change" in version.description:
                    target_version = version.version_id
                    break
            
            if not target_version:
                raise Exception("No stable version found for emergency rollback")
            
            # Get current version
            current_version = version_history[0].version_id if version_history else "unknown"
            
            # Create emergency rollback plan
            rollback_id = f"emergency_{int(time.time())}"
            plan = RollbackPlan(
                rollback_id=rollback_id,
                trigger=RollbackTrigger.EMERGENCY,
                target_version=target_version,
                current_version=current_version,
                environment=environment,
                reason=reason,
                created_at=datetime.now()
            )
            
            # Execute rollback immediately
            result = await self._execute_rollback(plan)
            
            self.log_action("emergency_rollback", "completed", {
                "rollback_id": rollback_id,
                "success": result["success"]
            })
            
            return result
            
        except Exception as e:
            self.log_action("emergency_rollback_error", "error", {
                "environment": environment,
                "error": str(e)
            })
            return {
                "success": False,
                "error": str(e),
                "rollback_id": None
            }
    
    async def _execute_rollback(self, plan: RollbackPlan) -> Dict[str, Any]:
        """Execute rollback plan."""
        plan.status = RollbackStatus.IN_PROGRESS
        plan.started_at = datetime.now()
        
        self.active_rollbacks[plan.rollback_id] = plan
        
        self.log_action("execute_rollback", "in_progress", {
            "rollback_id": plan.rollback_id,
            "target_version": plan.target_version,
            "environment": plan.environment
        })
        
        try:
            # Perform rollback
            success, message = self.tunnel_manager.rollback_config(plan.target_version)
            
            if success:
                plan.status = RollbackStatus.COMPLETED
                plan.completed_at = datetime.now()
                
                # Verify rollback
                verification_results = await self._verify_rollback(plan)
                plan.verification_results = verification_results
                
                if verification_results["success"]:
                    plan.status = RollbackStatus.VERIFIED
                
                self.log_action("execute_rollback", "completed", {
                    "rollback_id": plan.rollback_id,
                    "success": True,
                    "verification_success": verification_results["success"]
                })
                
                result = {
                    "success": True,
                    "rollback_id": plan.rollback_id,
                    "target_version": plan.target_version,
                    "verification_results": verification_results
                }
                
            else:
                plan.status = RollbackStatus.FAILED
                plan.error_message = message
                plan.completed_at = datetime.now()
                
                self.log_action("execute_rollback", "error", {
                    "rollback_id": plan.rollback_id,
                    "error": message
                })
                
                result = {
                    "success": False,
                    "rollback_id": plan.rollback_id,
                    "error": message
                }
            
            # Move to history
            self.rollback_history.append(plan)
            if plan.rollback_id in self.active_rollbacks:
                del self.active_rollbacks[plan.rollback_id]
            
            return result
            
        except Exception as e:
            plan.status = RollbackStatus.FAILED
            plan.error_message = str(e)
            plan.completed_at = datetime.now()
            
            self.log_action("execute_rollback_error", "error", {
                "rollback_id": plan.rollback_id,
                "error": str(e)
            })
            
            # Move to history
            self.rollback_history.append(plan)
            if plan.rollback_id in self.active_rollbacks:
                del self.active_rollbacks[plan.rollback_id]
            
            return {
                "success": False,
                "rollback_id": plan.rollback_id,
                "error": str(e)
            }
    
    async def _verify_rollback(self, plan: RollbackPlan) -> Dict[str, Any]:
        """Verify rollback was successful."""
        self.log_action("verify_rollback", "in_progress", {
            "rollback_id": plan.rollback_id,
            "environment": plan.environment
        })
        
        verification_results = {
            "success": True,
            "checks": {},
            "errors": []
        }
        
        try:
            env_config = self.config["environments"][plan.environment]
            
            # Wait for configuration to propagate
            await asyncio.sleep(10)
            
            # Check HTTP health
            health_check = await self._verify_http_health(plan.environment, env_config)
            verification_results["checks"]["http_health"] = health_check
            if not health_check["success"]:
                verification_results["errors"].append("HTTP health check failed")
                verification_results["success"] = False
            
            # Check WebSocket health
            websocket_check = await self._verify_websocket_health(plan.environment, env_config)
            verification_results["checks"]["websocket_health"] = websocket_check
            if not websocket_check["success"]:
                verification_results["errors"].append("WebSocket health check failed")
                verification_results["success"] = False
            
            # Check tunnel configuration
            tunnel_check = await self._verify_tunnel_config()
            verification_results["checks"]["tunnel_config"] = tunnel_check
            if not tunnel_check["success"]:
                verification_results["errors"].append("Tunnel configuration check failed")
                verification_results["success"] = False
            
            self.log_action("verify_rollback", "completed", {
                "rollback_id": plan.rollback_id,
                "success": verification_results["success"],
                "checks_performed": len(verification_results["checks"])
            })
            
        except Exception as e:
            verification_results["success"] = False
            verification_results["errors"].append(f"Verification error: {str(e)}")
            self.log_action("verify_rollback_error", "error", {
                "rollback_id": plan.rollback_id,
                "error": str(e)
            })
        
        return verification_results
    
    async def _verify_http_health(self, environment: str, env_config: Dict[str, Any]) -> Dict[str, Any]:
        """Verify HTTP health after rollback."""
        try:
            health_url = f"{env_config['url']}{env_config['health_endpoint']}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(health_url, timeout=10) as response:
                    return {
                        "success": response.status == 200,
                        "status_code": response.status,
                        "url": health_url
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _verify_websocket_health(self, environment: str, env_config: Dict[str, Any]) -> Dict[str, Any]:
        """Verify WebSocket health after rollback."""
        try:
            websocket_url = env_config["websocket_url"]
            
            async with websockets.connect(websocket_url, timeout=10) as websocket:
                await websocket.ping()
                
                return {
                    "success": True,
                    "url": websocket_url
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _verify_tunnel_config(self) -> Dict[str, Any]:
        """Verify tunnel configuration after rollback."""
        try:
            config_info = self.tunnel_manager.get_config_info()
            
            return {
                "success": config_info.get("validation_status") == "valid",
                "validation_status": config_info.get("validation_status"),
                "websocket_enabled": config_info.get("websocket_enabled", False)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_rollback_status(self, rollback_id: Optional[str] = None) -> Dict[str, Any]:
        """Get rollback status."""
        if rollback_id:
            # Get specific rollback status
            for rollback in self.rollback_history:
                if rollback.rollback_id == rollback_id:
                    return {
                        "rollback_id": rollback.rollback_id,
                        "status": rollback.status.value,
                        "trigger": rollback.trigger.value,
                        "environment": rollback.environment,
                        "reason": rollback.reason,
                        "created_at": rollback.created_at.isoformat(),
                        "started_at": rollback.started_at.isoformat() if rollback.started_at else None,
                        "completed_at": rollback.completed_at.isoformat() if rollback.completed_at else None,
                        "verification_results": rollback.verification_results,
                        "error_message": rollback.error_message
                    }
            
            # Check active rollbacks
            if rollback_id in self.active_rollbacks:
                rollback = self.active_rollbacks[rollback_id]
                return {
                    "rollback_id": rollback.rollback_id,
                    "status": rollback.status.value,
                    "trigger": rollback.trigger.value,
                    "environment": rollback.environment,
                    "reason": rollback.reason,
                    "created_at": rollback.created_at.isoformat(),
                    "started_at": rollback.started_at.isoformat() if rollback.started_at else None,
                    "completed_at": rollback.completed_at.isoformat() if rollback.completed_at else None,
                    "verification_results": rollback.verification_results,
                    "error_message": rollback.error_message
                }
            
            return {"error": f"Rollback {rollback_id} not found"}
        
        else:
            # Get all rollback status
            return {
                "active_rollbacks": len(self.active_rollbacks),
                "total_rollbacks": len(self.rollback_history),
                "recent_rollbacks": [
                    {
                        "rollback_id": r.rollback_id,
                        "status": r.status.value,
                        "trigger": r.trigger.value,
                        "environment": r.environment,
                        "created_at": r.created_at.isoformat(),
                        "success": r.status in [RollbackStatus.COMPLETED, RollbackStatus.VERIFIED]
                    }
                    for r in self.rollback_history[-10:]  # Last 10 rollbacks
                ],
                "monitoring_active": self.monitoring_active,
                "triggers_enabled": len([t for t in self.trigger_configs.values() if t.enabled])
            }
    
    def get_rollback_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get rollback history."""
        return [
            {
                "rollback_id": r.rollback_id,
                "status": r.status.value,
                "trigger": r.trigger.value,
                "target_version": r.target_version,
                "current_version": r.current_version,
                "environment": r.environment,
                "reason": r.reason,
                "created_at": r.created_at.isoformat(),
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                "verification_results": r.verification_results,
                "error_message": r.error_message
            }
            for r in self.rollback_history[-limit:]
        ]
    
    def get_available_versions(self) -> List[Dict[str, Any]]:
        """Get available rollback versions."""
        try:
            versions = self.tunnel_manager.get_version_history(limit=20)
            return [
                {
                    "version_id": v.version_id,
                    "description": v.description,
                    "created_at": v.created_at.isoformat(),
                    "is_stable": "Backup before configuration change" in (v.description or "")
                }
                for v in versions
            ]
        except Exception as e:
            return [{"error": str(e)}]


async def main():
    """Main entry point for rollback script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Rollback deployment")
    parser.add_argument("--action", choices=["manual", "emergency", "status", "history", "versions", "monitor"], 
                       required=True, help="Action to perform")
    parser.add_argument("--environment", choices=["dev", "staging", "production"], 
                       default="production", help="Environment to rollback")
    parser.add_argument("--version", help="Target version for manual rollback")
    parser.add_argument("--reason", default="Manual rollback", help="Reason for rollback")
    parser.add_argument("--rollback-id", help="Rollback ID for status check")
    parser.add_argument("--config", default="deployment-config.yml",
                       help="Path to deployment configuration file")
    parser.add_argument("--output", choices=["json", "text"], default="json",
                       help="Output format")
    
    args = parser.parse_args()
    
    try:
        # Initialize rollback automation
        rollback = RollbackAutomation(args.config)
        
        if args.action == "monitor":
            # Start monitoring
            await rollback.start_monitoring()
            print("Rollback monitoring started. Press Ctrl+C to stop.")
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                await rollback.stop_monitoring()
                print("\nRollback monitoring stopped.")
        
        elif args.action == "manual":
            if not args.version:
                print("Error: --version is required for manual rollback")
                sys.exit(1)
            
            result = await rollback.manual_rollback(
                environment=args.environment,
                target_version=args.version,
                reason=args.reason
            )
            
            if args.output == "json":
                print(json.dumps(result, indent=2, default=str))
            else:
                if result["success"]:
                    print(f"✅ Manual rollback completed successfully!")
                    print(f"Rollback ID: {result['rollback_id']}")
                else:
                    print(f"❌ Manual rollback failed: {result['error']}")
        
        elif args.action == "emergency":
            result = await rollback.emergency_rollback(
                environment=args.environment,
                reason=args.reason
            )
            
            if args.output == "json":
                print(json.dumps(result, indent=2, default=str))
            else:
                if result["success"]:
                    print(f"✅ Emergency rollback completed successfully!")
                    print(f"Rollback ID: {result['rollback_id']}")
                else:
                    print(f"❌ Emergency rollback failed: {result['error']}")
        
        elif args.action == "status":
            status = rollback.get_rollback_status(args.rollback_id)
            
            if args.output == "json":
                print(json.dumps(status, indent=2, default=str))
            else:
                if "error" in status:
                    print(f"❌ {status['error']}")
                else:
                    print(f"\n{'='*80}")
                    print(f"ROLLBACK STATUS")
                    print(f"{'='*80}")
                    if args.rollback_id:
                        print(f"Rollback ID: {status['rollback_id']}")
                        print(f"Status: {status['status']}")
                        print(f"Trigger: {status['trigger']}")
                        print(f"Environment: {status['environment']}")
                        print(f"Reason: {status['reason']}")
                        print(f"Created: {status['created_at']}")
                        if status['started_at']:
                            print(f"Started: {status['started_at']}")
                        if status['completed_at']:
                            print(f"Completed: {status['completed_at']}")
                        if status['error_message']:
                            print(f"Error: {status['error_message']}")
                    else:
                        print(f"Active Rollbacks: {status['active_rollbacks']}")
                        print(f"Total Rollbacks: {status['total_rollbacks']}")
                        print(f"Monitoring Active: {status['monitoring_active']}")
                        print(f"Triggers Enabled: {status['triggers_enabled']}")
        
        elif args.action == "history":
            history = rollback.get_rollback_history()
            
            if args.output == "json":
                print(json.dumps(history, indent=2, default=str))
            else:
                print(f"\n{'='*80}")
                print(f"ROLLBACK HISTORY")
                print(f"{'='*80}")
                for rollback_info in history:
                    status_icon = "✅" if rollback_info["success"] else "❌"
                    print(f"{status_icon} {rollback_info['rollback_id']} ({rollback_info['status']})")
                    print(f"   Trigger: {rollback_info['trigger']}")
                    print(f"   Environment: {rollback_info['environment']}")
                    print(f"   Created: {rollback_info['created_at']}")
                    print()
        
        elif args.action == "versions":
            versions = rollback.get_available_versions()
            
            if args.output == "json":
                print(json.dumps(versions, indent=2, default=str))
            else:
                print(f"\n{'='*80}")
                print(f"AVAILABLE ROLLBACK VERSIONS")
                print(f"{'='*80}")
                for version in versions:
                    if "error" in version:
                        print(f"❌ {version['error']}")
                        break
                    
                    stable_icon = "🔒" if version["is_stable"] else "📝"
                    print(f"{stable_icon} {version['version_id']}")
                    print(f"   Description: {version['description']}")
                    print(f"   Created: {version['created_at']}")
                    print(f"   Stable: {version['is_stable']}")
                    print()
        
        # Exit with appropriate code
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Rollback error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())