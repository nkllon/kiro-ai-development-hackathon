#!/usr/bin/env python3
"""
WebSocket Fix Monitoring Agent

Monitors the execution status of the three WebSocket fix agents (Phase 1, Phase 2, Phase 3).
Checks agent outputs, detects stuck processes, and provides regular status updates.
Implements timeout detection and auto-remediation if agents become unresponsive.
Collects and summarizes results from all agents.
Generates comprehensive status report every 5 minutes until all phases complete.
"""

import asyncio
import json
import logging
import os
import psutil
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
import signal
import threading

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from beast_mode.observatory.websocket import (
    WebSocketHealthValidator,
    HealthStatus,
    EndpointMonitor,
    FailureDetector
)
from beast_mode.observatory.monitoring.health_monitor import WebSocketHealthMonitor


class AgentPhase(Enum):
    """WebSocket fix agent phases"""
    PHASE_1 = "phase_1"
    PHASE_2 = "phase_2"
    PHASE_3 = "phase_3"


class AgentStatus(Enum):
    """Agent execution status"""
    NOT_STARTED = "not_started"
    STARTING = "starting"
    RUNNING = "running"
    HEALTH_CHECKING = "health_checking"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    STUCK = "stuck"
    TERMINATED = "terminated"


class RemediationAction(Enum):
    """Auto-remediation actions"""
    RESTART_AGENT = "restart_agent"
    KILL_AND_RESTART = "kill_and_restart"
    SKIP_PHASE = "skip_phase"
    ESCALATE = "escalate"
    NO_ACTION = "no_action"


@dataclass
class AgentConfig:
    """Configuration for a WebSocket fix agent"""
    phase: AgentPhase
    script_path: str
    timeout_minutes: int = 30
    health_check_interval: int = 60  # seconds
    stuck_threshold_minutes: int = 10
    max_restart_attempts: int = 3
    dependencies: List[AgentPhase] = field(default_factory=list)
    auto_remediation: bool = True
    critical: bool = True


@dataclass
class AgentProcess:
    """Information about a running agent process"""
    phase: AgentPhase
    pid: Optional[int] = None
    start_time: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    status: AgentStatus = AgentStatus.NOT_STARTED
    restart_count: int = 0
    output_file: Optional[str] = None
    error_file: Optional[str] = None
    health_score: float = 0.0
    last_health_check: Optional[datetime] = None
    stuck_detection_count: int = 0
    remediation_actions: List[RemediationAction] = field(default_factory=list)


@dataclass
class MonitoringReport:
    """Comprehensive monitoring report"""
    timestamp: datetime
    overall_status: str
    phases_status: Dict[str, Dict[str, Any]]
    health_metrics: Dict[str, Any]
    remediation_actions: List[Dict[str, Any]]
    recommendations: List[str]
    next_check_time: datetime


class WebSocketFixMonitoringAgent:
    """
    Comprehensive monitoring agent for WebSocket fix deployment phases.
    
    Monitors Phase 1, Phase 2, and Phase 3 WebSocket fix agents with:
    - Real-time process monitoring
    - Timeout detection and auto-remediation
    - Health check validation
    - Comprehensive status reporting
    - Automatic escalation and recovery
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize monitoring agent with configuration"""
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        
        # Initialize monitoring components
        self.health_validator = WebSocketHealthValidator()
        self.endpoint_monitor = EndpointMonitor()
        self.failure_detector = FailureDetector()
        self.health_monitor = WebSocketHealthMonitor()
        
        # Agent tracking
        self.agents: Dict[AgentPhase, AgentProcess] = {}
        self.monitoring_active = False
        self.report_history: List[MonitoringReport] = []
        
        # Monitoring threads
        self.monitoring_thread: Optional[threading.Thread] = None
        self.reporting_thread: Optional[threading.Thread] = None
        
        # Signal handling
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info("WebSocket Fix Monitoring Agent initialized")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, AgentConfig]:
        """Load monitoring configuration"""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
                return {
                    AgentPhase(phase): AgentConfig(**config) 
                    for phase, config in config_data.get('agents', {}).items()
                }
        
        # Default configuration for WebSocket fix agents
        return {
            AgentPhase.PHASE_1: AgentConfig(
                phase=AgentPhase.PHASE_1,
                script_path="scripts/deploy_websocket_fix.py",
                timeout_minutes=30,
                health_check_interval=60,
                stuck_threshold_minutes=10,
                max_restart_attempts=3,
                dependencies=[],
                auto_remediation=True,
                critical=True
            ),
            AgentPhase.PHASE_2: AgentConfig(
                phase=AgentPhase.PHASE_2,
                script_path="scripts/ssl_tls_full_strict_deployment.sh",
                timeout_minutes=45,
                health_check_interval=90,
                stuck_threshold_minutes=15,
                max_restart_attempts=3,
                dependencies=[AgentPhase.PHASE_1],
                auto_remediation=True,
                critical=True
            ),
            AgentPhase.PHASE_3: AgentConfig(
                phase=AgentPhase.PHASE_3,
                script_path="scripts/production_websocket_tester.py",
                timeout_minutes=60,
                health_check_interval=120,
                stuck_threshold_minutes=20,
                max_restart_attempts=2,
                dependencies=[AgentPhase.PHASE_1, AgentPhase.PHASE_2],
                auto_remediation=True,
                critical=True
            )
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging for monitoring operations"""
        logger = logging.getLogger("websocket_fix_monitoring")
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # File handler for monitoring logs
        file_handler = logging.FileHandler(
            logs_dir / f"websocket_fix_monitoring_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        file_handler.setLevel(logging.INFO)
        
        # Console handler for real-time output
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # JSON formatter for structured logs
        json_formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"component": "monitoring", "message": "%(message)s"}'
        )
        file_handler.setFormatter(json_formatter)
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    async def start_monitoring(self) -> None:
        """Start monitoring all WebSocket fix agents"""
        self.logger.info("Starting WebSocket Fix Monitoring Agent")
        
        # Initialize agent tracking
        for phase, config in self.config.items():
            self.agents[phase] = AgentProcess(phase=phase)
        
        self.monitoring_active = True
        
        # Start monitoring threads
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.reporting_thread = threading.Thread(target=self._reporting_loop)
        
        self.monitoring_thread.start()
        self.reporting_thread.start()
        
        self.logger.info("Monitoring threads started")
        
        # Wait for monitoring to complete
        try:
            while self.monitoring_active:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Monitoring interrupted by user")
        finally:
            await self.stop_monitoring()
    
    async def stop_monitoring(self) -> None:
        """Stop monitoring and cleanup resources"""
        self.logger.info("Stopping WebSocket Fix Monitoring Agent")
        
        self.monitoring_active = False
        
        # Terminate all running agents
        for agent in self.agents.values():
            if agent.pid and agent.status == AgentStatus.RUNNING:
                await self._terminate_agent(agent)
        
        # Wait for threads to finish
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        if self.reporting_thread and self.reporting_thread.is_alive():
            self.reporting_thread.join(timeout=5)
        
        # Generate final report
        await self._generate_final_report()
        
        self.logger.info("WebSocket Fix Monitoring Agent stopped")
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop running in separate thread"""
        while self.monitoring_active:
            try:
                # Check each agent
                for phase, agent in self.agents.items():
                    self._check_agent_status(agent)
                    self._detect_stuck_processes(agent)
                    self._perform_health_checks(agent)
                    self._apply_auto_remediation(agent)
                
                # Check if all phases are complete
                if self._all_phases_complete():
                    self.logger.info("All WebSocket fix phases completed")
                    self.monitoring_active = False
                    break
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)  # Wait longer on error
    
    def _reporting_loop(self) -> None:
        """Reporting loop running in separate thread"""
        while self.monitoring_active:
            try:
                # Generate status report every 5 minutes
                report = self._generate_status_report()
                self.report_history.append(report)
                
                # Print report to console
                self._print_status_report(report)
                
                # Save report to file
                self._save_report_to_file(report)
                
                # Wait 5 minutes
                time.sleep(300)
                
            except Exception as e:
                self.logger.error(f"Error in reporting loop: {e}")
                time.sleep(60)  # Wait 1 minute on error
    
    def _check_agent_status(self, agent: AgentProcess) -> None:
        """Check the current status of an agent"""
        if agent.status in [AgentStatus.COMPLETED, AgentStatus.FAILED, AgentStatus.TERMINATED]:
            return
        
        if agent.pid is None:
            # Agent not started yet
            if self._can_start_agent(agent):
                self._start_agent(agent)
        else:
            # Check if process is still running
            try:
                process = psutil.Process(agent.pid)
                if not process.is_running():
                    agent.status = AgentStatus.TERMINATED
                    self.logger.warning(f"Agent {agent.phase.value} terminated unexpectedly")
                else:
                    # Update last activity
                    agent.last_activity = datetime.now()
                    
                    # Check for timeout
                    if self._is_agent_timeout(agent):
                        agent.status = AgentStatus.TIMEOUT
                        self.logger.warning(f"Agent {agent.phase.value} timed out")
                        
            except psutil.NoSuchProcess:
                agent.status = AgentStatus.TERMINATED
                self.logger.warning(f"Agent {agent.phase.value} process not found")
    
    def _can_start_agent(self, agent: AgentProcess) -> bool:
        """Check if agent can be started based on dependencies"""
        config = self.config[agent.phase]
        
        # Check dependencies
        for dep_phase in config.dependencies:
            dep_agent = self.agents[dep_phase]
            if dep_agent.status != AgentStatus.COMPLETED:
                return False
        
        # Check if already started
        if agent.status != AgentStatus.NOT_STARTED:
            return False
        
        return True
    
    def _start_agent(self, agent: AgentProcess) -> None:
        """Start a WebSocket fix agent"""
        config = self.config[agent.phase]
        
        try:
            self.logger.info(f"Starting agent {agent.phase.value}")
            
            # Prepare output files
            logs_dir = Path("logs")
            logs_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            agent.output_file = str(logs_dir / f"{agent.phase.value}_output_{timestamp}.log")
            agent.error_file = str(logs_dir / f"{agent.phase.value}_error_{timestamp}.log")
            
            # Start the agent process
            with open(agent.output_file, 'w') as out_file, open(agent.error_file, 'w') as err_file:
                process = subprocess.Popen(
                    [sys.executable, config.script_path],
                    stdout=out_file,
                    stderr=err_file,
                    cwd=Path.cwd()
                )
            
            agent.pid = process.pid
            agent.start_time = datetime.now()
            agent.last_activity = datetime.now()
            agent.status = AgentStatus.RUNNING
            
            self.logger.info(f"Agent {agent.phase.value} started with PID {agent.pid}")
            
        except Exception as e:
            agent.status = AgentStatus.FAILED
            self.logger.error(f"Failed to start agent {agent.phase.value}: {e}")
    
    def _is_agent_timeout(self, agent: AgentProcess) -> bool:
        """Check if agent has timed out"""
        if agent.start_time is None:
            return False
        
        config = self.config[agent.phase]
        timeout_duration = timedelta(minutes=config.timeout_minutes)
        
        return datetime.now() - agent.start_time > timeout_duration
    
    def _detect_stuck_processes(self, agent: AgentProcess) -> None:
        """Detect if agent process is stuck"""
        if agent.status != AgentStatus.RUNNING or agent.last_activity is None:
            return
        
        config = self.config[agent.phase]
        stuck_threshold = timedelta(minutes=config.stuck_threshold_minutes)
        
        if datetime.now() - agent.last_activity > stuck_threshold:
            agent.stuck_detection_count += 1
            
            if agent.stuck_detection_count >= 3:  # Confirm stuck after 3 detections
                agent.status = AgentStatus.STUCK
                self.logger.warning(f"Agent {agent.phase.value} detected as stuck")
    
    def _perform_health_checks(self, agent: AgentProcess) -> None:
        """Perform health checks on agent"""
        if agent.status != AgentStatus.RUNNING:
            return
        
        config = self.config[agent.phase]
        
        # Check if it's time for health check
        if (agent.last_health_check is None or 
            datetime.now() - agent.last_health_check > timedelta(seconds=config.health_check_interval)):
            
            try:
                # Perform health check based on agent phase
                health_score = self._check_agent_health(agent)
                agent.health_score = health_score
                agent.last_health_check = datetime.now()
                
                if health_score < 0.5:
                    self.logger.warning(f"Agent {agent.phase.value} health score low: {health_score:.2f}")
                
            except Exception as e:
                self.logger.error(f"Health check failed for agent {agent.phase.value}: {e}")
    
    def _check_agent_health(self, agent: AgentProcess) -> float:
        """Check health of a specific agent based on its phase"""
        if agent.pid is None:
            return 0.0
        
        try:
            process = psutil.Process(agent.pid)
            
            # Basic process health
            health_score = 1.0
            
            # Check CPU usage
            cpu_percent = process.cpu_percent()
            if cpu_percent > 90:
                health_score -= 0.3
            elif cpu_percent > 70:
                health_score -= 0.1
            
            # Check memory usage
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            if memory_mb > 1000:  # 1GB
                health_score -= 0.2
            elif memory_mb > 500:  # 500MB
                health_score -= 0.1
            
            # Check if process is responsive
            try:
                process.status()
            except psutil.NoSuchProcess:
                health_score = 0.0
            
            # Phase-specific health checks
            if agent.phase == AgentPhase.PHASE_1:
                # Check WebSocket deployment health
                health_score = min(health_score, self._check_websocket_deployment_health())
            elif agent.phase == AgentPhase.PHASE_2:
                # Check SSL/TLS configuration health
                health_score = min(health_score, self._check_ssl_tls_health())
            elif agent.phase == AgentPhase.PHASE_3:
                # Check production WebSocket health
                health_score = min(health_score, self._check_production_websocket_health())
            
            return max(0.0, health_score)
            
        except Exception as e:
            self.logger.error(f"Error checking agent health: {e}")
            return 0.0
    
    def _check_websocket_deployment_health(self) -> float:
        """Check WebSocket deployment health for Phase 1"""
        try:
            # Check if cloudflared is running
            result = subprocess.run(["pgrep", "-f", "cloudflared"], capture_output=True, text=True)
            if result.returncode != 0:
                return 0.3
            
            # Check WebSocket endpoint
            health_result = asyncio.run(self.health_validator.validate_websocket_health(
                "ws://localhost:8888/ws"
            ))
            
            if health_result.status == HealthStatus.HEALTHY:
                return 1.0
            elif health_result.status == HealthStatus.DEGRADED:
                return 0.7
            else:
                return 0.3
                
        except Exception as e:
            self.logger.error(f"WebSocket deployment health check failed: {e}")
            return 0.0
    
    def _check_ssl_tls_health(self) -> float:
        """Check SSL/TLS configuration health for Phase 2"""
        try:
            # Check SSL certificate validity
            result = subprocess.run([
                "openssl", "s_client", "-connect", "observatory.nkllon.com:443", 
                "-servername", "observatory.nkllon.com", "-verify_return_error"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return 1.0
            else:
                return 0.5
                
        except Exception as e:
            self.logger.error(f"SSL/TLS health check failed: {e}")
            return 0.0
    
    def _check_production_websocket_health(self) -> float:
        """Check production WebSocket health for Phase 3"""
        try:
            # Check production WebSocket endpoint
            health_result = asyncio.run(self.health_validator.validate_websocket_health(
                "wss://observatory.nkllon.com/ws"
            ))
            
            if health_result.status == HealthStatus.HEALTHY:
                return 1.0
            elif health_result.status == HealthStatus.DEGRADED:
                return 0.7
            else:
                return 0.3
                
        except Exception as e:
            self.logger.error(f"Production WebSocket health check failed: {e}")
            return 0.0
    
    def _apply_auto_remediation(self, agent: AgentProcess) -> None:
        """Apply auto-remediation actions for problematic agents"""
        if not self.config[agent.phase].auto_remediation:
            return
        
        remediation_action = None
        
        if agent.status == AgentStatus.TIMEOUT:
            remediation_action = RemediationAction.KILL_AND_RESTART
        elif agent.status == AgentStatus.STUCK:
            remediation_action = RemediationAction.RESTART_AGENT
        elif agent.status == AgentStatus.FAILED:
            remediation_action = RemediationAction.RESTART_AGENT
        elif agent.health_score < 0.3:
            remediation_action = RemediationAction.RESTART_AGENT
        
        if remediation_action:
            await self._execute_remediation(agent, remediation_action)
    
    async def _execute_remediation(self, agent: AgentProcess, action: RemediationAction) -> None:
        """Execute remediation action for an agent"""
        config = self.config[agent.phase]
        
        if agent.restart_count >= config.max_restart_attempts:
            self.logger.error(f"Agent {agent.phase.value} exceeded max restart attempts")
            agent.status = AgentStatus.FAILED
            return
        
        self.logger.info(f"Executing remediation action {action.value} for agent {agent.phase.value}")
        
        if action == RemediationAction.RESTART_AGENT:
            await self._restart_agent(agent)
        elif action == RemediationAction.KILL_AND_RESTART:
            await self._terminate_agent(agent)
            await self._restart_agent(agent)
        elif action == RemediationAction.SKIP_PHASE:
            agent.status = AgentStatus.COMPLETED
            self.logger.warning(f"Skipping phase {agent.phase.value}")
        elif action == RemediationAction.ESCALATE:
            self.logger.critical(f"Escalating issue with agent {agent.phase.value}")
            # Could send alerts, notifications, etc.
        
        agent.remediation_actions.append(action)
    
    async def _restart_agent(self, agent: AgentProcess) -> None:
        """Restart an agent"""
        self.logger.info(f"Restarting agent {agent.phase.value}")
        
        # Terminate current process
        if agent.pid:
            await self._terminate_agent(agent)
        
        # Reset agent state
        agent.pid = None
        agent.start_time = None
        agent.last_activity = None
        agent.status = AgentStatus.NOT_STARTED
        agent.restart_count += 1
        agent.stuck_detection_count = 0
        
        # Start agent again
        self._start_agent(agent)
    
    async def _terminate_agent(self, agent: AgentProcess) -> None:
        """Terminate an agent process"""
        if agent.pid is None:
            return
        
        try:
            process = psutil.Process(agent.pid)
            process.terminate()
            
            # Wait for graceful termination
            try:
                process.wait(timeout=10)
            except psutil.TimeoutExpired:
                # Force kill if graceful termination fails
                process.kill()
                process.wait(timeout=5)
            
            self.logger.info(f"Agent {agent.phase.value} terminated")
            
        except psutil.NoSuchProcess:
            self.logger.warning(f"Agent {agent.phase.value} process not found")
        except Exception as e:
            self.logger.error(f"Error terminating agent {agent.phase.value}: {e}")
        finally:
            agent.pid = None
            agent.status = AgentStatus.TERMINATED
    
    def _all_phases_complete(self) -> bool:
        """Check if all phases are complete"""
        for agent in self.agents.values():
            if agent.status not in [AgentStatus.COMPLETED, AgentStatus.FAILED]:
                return False
        return True
    
    def _generate_status_report(self) -> MonitoringReport:
        """Generate comprehensive status report"""
        timestamp = datetime.now()
        
        # Calculate overall status
        completed_count = sum(1 for agent in self.agents.values() if agent.status == AgentStatus.COMPLETED)
        failed_count = sum(1 for agent in self.agents.values() if agent.status == AgentStatus.FAILED)
        total_count = len(self.agents)
        
        if completed_count == total_count:
            overall_status = "ALL_PHASES_COMPLETE"
        elif failed_count > 0:
            overall_status = "PHASES_FAILED"
        elif completed_count > 0:
            overall_status = "PHASES_IN_PROGRESS"
        else:
            overall_status = "PHASES_NOT_STARTED"
        
        # Generate phase status
        phases_status = {}
        for phase, agent in self.agents.items():
            phases_status[phase.value] = {
                "status": agent.status.value,
                "pid": agent.pid,
                "start_time": agent.start_time.isoformat() if agent.start_time else None,
                "last_activity": agent.last_activity.isoformat() if agent.last_activity else None,
                "health_score": agent.health_score,
                "restart_count": agent.restart_count,
                "stuck_detection_count": agent.stuck_detection_count,
                "remediation_actions": [action.value for action in agent.remediation_actions],
                "output_file": agent.output_file,
                "error_file": agent.error_file
            }
        
        # Generate health metrics
        health_metrics = {
            "overall_health_score": sum(agent.health_score for agent in self.agents.values()) / len(self.agents),
            "agents_running": sum(1 for agent in self.agents.values() if agent.status == AgentStatus.RUNNING),
            "agents_completed": completed_count,
            "agents_failed": failed_count,
            "total_restarts": sum(agent.restart_count for agent in self.agents.values()),
            "total_remediation_actions": sum(len(agent.remediation_actions) for agent in self.agents.values())
        }
        
        # Generate remediation actions summary
        remediation_actions = []
        for agent in self.agents.values():
            for action in agent.remediation_actions:
                remediation_actions.append({
                    "phase": agent.phase.value,
                    "action": action.value,
                    "timestamp": timestamp.isoformat()
                })
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        
        return MonitoringReport(
            timestamp=timestamp,
            overall_status=overall_status,
            phases_status=phases_status,
            health_metrics=health_metrics,
            remediation_actions=remediation_actions,
            recommendations=recommendations,
            next_check_time=timestamp + timedelta(minutes=5)
        )
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on current status"""
        recommendations = []
        
        for phase, agent in self.agents.items():
            if agent.status == AgentStatus.STUCK:
                recommendations.append(f"Consider restarting {phase.value} agent - appears to be stuck")
            elif agent.status == AgentStatus.TIMEOUT:
                recommendations.append(f"Investigate {phase.value} agent timeout - may need configuration adjustment")
            elif agent.status == AgentStatus.FAILED:
                recommendations.append(f"Review {phase.value} agent failure - check logs for errors")
            elif agent.health_score < 0.5:
                recommendations.append(f"Monitor {phase.value} agent health - score is low")
            elif agent.restart_count >= 2:
                recommendations.append(f"Investigate {phase.value} agent stability - multiple restarts required")
        
        if not recommendations:
            recommendations.append("All agents operating normally")
        
        return recommendations
    
    def _print_status_report(self, report: MonitoringReport) -> None:
        """Print status report to console"""
        print("\n" + "="*80)
        print("WEBSOCKET FIX MONITORING AGENT - STATUS REPORT")
        print("="*80)
        print(f"Timestamp: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Overall Status: {report.overall_status}")
        print()
        
        print("PHASE STATUS:")
        print("-" * 40)
        for phase, status in report.phases_status.items():
            print(f"  {phase.upper()}:")
            print(f"    Status: {status['status']}")
            print(f"    PID: {status['pid']}")
            print(f"    Health Score: {status['health_score']:.2f}")
            print(f"    Restart Count: {status['restart_count']}")
            if status['remediation_actions']:
                print(f"    Remediation Actions: {', '.join(status['remediation_actions'])}")
            print()
        
        print("HEALTH METRICS:")
        print("-" * 40)
        for metric, value in report.health_metrics.items():
            print(f"  {metric.replace('_', ' ').title()}: {value}")
        print()
        
        if report.remediation_actions:
            print("RECENT REMEDIATION ACTIONS:")
            print("-" * 40)
            for action in report.remediation_actions[-5:]:  # Show last 5 actions
                print(f"  {action['timestamp']}: {action['phase']} - {action['action']}")
            print()
        
        print("RECOMMENDATIONS:")
        print("-" * 40)
        for recommendation in report.recommendations:
            print(f"  • {recommendation}")
        print()
        
        print(f"Next Report: {report.next_check_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
    
    def _save_report_to_file(self, report: MonitoringReport) -> None:
        """Save report to file"""
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        report_file = logs_dir / f"websocket_fix_monitoring_report_{report.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        
        report_data = {
            "timestamp": report.timestamp.isoformat(),
            "overall_status": report.overall_status,
            "phases_status": report.phases_status,
            "health_metrics": report.health_metrics,
            "remediation_actions": report.remediation_actions,
            "recommendations": report.recommendations,
            "next_check_time": report.next_check_time.isoformat()
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        self.logger.info(f"Status report saved to {report_file}")
    
    async def _generate_final_report(self) -> None:
        """Generate final comprehensive report"""
        self.logger.info("Generating final comprehensive report")
        
        final_report = {
            "monitoring_session": {
                "start_time": self.report_history[0].timestamp.isoformat() if self.report_history else None,
                "end_time": datetime.now().isoformat(),
                "total_reports": len(self.report_history),
                "monitoring_duration_minutes": (
                    (datetime.now() - self.report_history[0].timestamp).total_seconds() / 60
                    if self.report_history else 0
                )
            },
            "final_status": {
                "overall_status": self.report_history[-1].overall_status if self.report_history else "UNKNOWN",
                "phases_completed": sum(1 for agent in self.agents.values() if agent.status == AgentStatus.COMPLETED),
                "phases_failed": sum(1 for agent in self.agents.values() if agent.status == AgentStatus.FAILED),
                "total_phases": len(self.agents)
            },
            "agent_summary": {
                phase.value: {
                    "final_status": agent.status.value,
                    "total_restarts": agent.restart_count,
                    "final_health_score": agent.health_score,
                    "remediation_actions_count": len(agent.remediation_actions),
                    "output_file": agent.output_file,
                    "error_file": agent.error_file
                }
                for phase, agent in self.agents.items()
            },
            "health_metrics_summary": {
                "average_health_score": sum(agent.health_score for agent in self.agents.values()) / len(self.agents),
                "total_restarts": sum(agent.restart_count for agent in self.agents.values()),
                "total_remediation_actions": sum(len(agent.remediation_actions) for agent in self.agents.values())
            },
            "report_history": [
                {
                    "timestamp": report.timestamp.isoformat(),
                    "overall_status": report.overall_status,
                    "health_metrics": report.health_metrics
                }
                for report in self.report_history
            ]
        }
        
        # Save final report
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        final_report_file = logs_dir / f"websocket_fix_monitoring_final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(final_report_file, 'w') as f:
            json.dump(final_report, f, indent=2)
        
        self.logger.info(f"Final comprehensive report saved to {final_report_file}")
        
        # Print final summary
        print("\n" + "="*80)
        print("WEBSOCKET FIX MONITORING AGENT - FINAL REPORT")
        print("="*80)
        print(f"Monitoring Duration: {final_report['monitoring_session']['monitoring_duration_minutes']:.1f} minutes")
        print(f"Total Reports Generated: {final_report['monitoring_session']['total_reports']}")
        print(f"Final Status: {final_report['final_status']['overall_status']}")
        print(f"Phases Completed: {final_report['final_status']['phases_completed']}/{final_report['final_status']['total_phases']}")
        print(f"Phases Failed: {final_report['final_status']['phases_failed']}")
        print(f"Average Health Score: {final_report['health_metrics_summary']['average_health_score']:.2f}")
        print(f"Total Restarts: {final_report['health_metrics_summary']['total_restarts']}")
        print(f"Total Remediation Actions: {final_report['health_metrics_summary']['total_remediation_actions']}")
        print("="*80)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, initiating shutdown")
        self.monitoring_active = False


async def main():
    """Main entry point for WebSocket Fix Monitoring Agent"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor WebSocket fix agents execution")
    parser.add_argument("--config", type=str, help="Path to monitoring configuration file")
    parser.add_argument("--phases", nargs="+", choices=["phase_1", "phase_2", "phase_3"],
                       default=["phase_1", "phase_2", "phase_3"],
                       help="Phases to monitor")
    parser.add_argument("--test-mode", action="store_true",
                       help="Run in test mode without starting actual agents")
    
    args = parser.parse_args()
    
    # Initialize monitoring agent
    monitoring_agent = WebSocketFixMonitoringAgent(args.config)
    
    try:
        # Start monitoring
        await monitoring_agent.start_monitoring()
        
    except KeyboardInterrupt:
        print("\nMonitoring interrupted by user")
    except Exception as e:
        print(f"Monitoring failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())