#!/usr/bin/env python3
"""
HealthCheckValidator - Standardized Health Check Generation and Validation

Detects available tools in container environments and generates appropriate 
health check commands using only tools that are actually present.
"""

import os
import subprocess
import logging
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class HealthCheckTool(Enum):
    """Available health check tools."""
    WGET = "wget"
    CURL = "curl"
    NC = "nc"
    PYTHON = "python"
    PYTHON3 = "python3"
    NODE = "node"
    BASH = "bash"
    SH = "sh"


@dataclass
class HealthCheckConfig:
    """Health check configuration."""
    url: str
    timeout: int = 30
    interval: int = 30
    retries: int = 3
    start_period: int = 60
    expected_status: int = 200


class HealthCheckValidator(ReflectiveModule):
    """
    Validates and generates health checks for container environments.
    
    Automatically detects available tools and generates working health check
    commands that use only tools present in the target environment.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize HealthCheckValidator."""
        super().__init__()
        self._config = config or {}
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._tool_cache: Optional[Set[HealthCheckTool]] = None
        
        # Register metrics
        self._register_metrics()
        
        self._logger.info("HealthCheckValidator initialized")
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get HealthCheckValidator capabilities."""
        return {
            "tool_detection": True,
            "health_check_generation": True,
            "docker_integration": True,
            "multi_tool_support": True
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "name": "HealthCheckValidator",
            "version": "1.0.0",
            "description": "Health check validation and generation system",
            "author": "Beast Mode Framework"
        }
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation on errors."""
        self._logger.error(f"HealthCheckValidator degradation: {error}")
        return {
            "status": "degraded",
            "error": str(error),
            "fallback_mode": "basic_health_checks"
        }
    
    def _register_metrics(self):
        """Register Prometheus metrics."""
        try:
            from prometheus_client import Counter, Histogram, Gauge
            
            self._health_checks_generated = Counter(
                'health_checks_generated_total',
                'Total health checks generated',
                ['tool', 'service']
            )
            
            self._tool_detection_time = Histogram(
                'health_check_tool_detection_seconds',
                'Time spent detecting available tools'
            )
            
            self._validation_success_rate = Gauge(
                'health_check_validation_success_rate',
                'Success rate of health check validations',
                ['tool']
            )
            
        except ImportError:
            self._logger.warning("Prometheus client not available, metrics disabled")
    
    def detect_available_tools(self, force_refresh: bool = False) -> Set[HealthCheckTool]:
        """
        Detect which health check tools are available in the environment.
        
        Args:
            force_refresh: Force re-detection even if cached
            
        Returns:
            Set of available HealthCheckTool enums
        """
        if self._tool_cache is not None and not force_refresh:
            return self._tool_cache
        
        start_time = self._get_current_time()
        available_tools = set()
        
        # Test each tool
        tool_commands = {
            HealthCheckTool.WGET: ["wget", "--version"],
            HealthCheckTool.CURL: ["curl", "--version"],
            HealthCheckTool.NC: ["nc", "-h"],
            HealthCheckTool.PYTHON: ["python", "--version"],
            HealthCheckTool.PYTHON3: ["python3", "--version"],
            HealthCheckTool.NODE: ["node", "--version"],
            HealthCheckTool.BASH: ["bash", "--version"],
            HealthCheckTool.SH: ["sh", "--version"]
        }
        
        for tool, command in tool_commands.items():
            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    timeout=5,
                    check=False
                )
                if result.returncode == 0:
                    available_tools.add(tool)
                    self._logger.debug(f"Tool {tool.value} is available")
                else:
                    self._logger.debug(f"Tool {tool.value} not available (exit code: {result.returncode})")
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
                self._logger.debug(f"Tool {tool.value} not available: {e}")
        
        self._tool_cache = available_tools
        
        # Update metrics
        if hasattr(self, '_tool_detection_time'):
            duration = self._get_current_time() - start_time
            self._tool_detection_time.observe(duration)
        
        self._logger.info(f"Detected {len(available_tools)} available tools: {[t.value for t in available_tools]}")
        return available_tools
    
    def generate_health_check(self, config: HealthCheckConfig, service_name: str = "unknown") -> Optional[str]:
        """
        Generate a health check command using available tools.
        
        Args:
            config: Health check configuration
            service_name: Name of service for metrics
            
        Returns:
            Health check command string or None if no suitable tools
        """
        available_tools = self.detect_available_tools()
        
        if not available_tools:
            self._logger.error("No health check tools available")
            return None
        
        # Priority order for tool selection
        tool_priority = [
            HealthCheckTool.CURL,
            HealthCheckTool.WGET,
            HealthCheckTool.PYTHON3,
            HealthCheckTool.PYTHON,
            HealthCheckTool.NC,
            HealthCheckTool.NODE
        ]
        
        selected_tool = None
        for tool in tool_priority:
            if tool in available_tools:
                selected_tool = tool
                break
        
        if not selected_tool:
            self._logger.error("No suitable health check tool found")
            return None
        
        # Generate command based on selected tool
        command = self._generate_tool_command(selected_tool, config)
        
        if command:
            # Update metrics
            if hasattr(self, '_health_checks_generated'):
                self._health_checks_generated.labels(
                    tool=selected_tool.value,
                    service=service_name
                ).inc()
            
            self._logger.info(f"Generated health check using {selected_tool.value}: {command}")
        
        return command
    
    def _generate_tool_command(self, tool: HealthCheckTool, config: HealthCheckConfig) -> Optional[str]:
        """Generate health check command for specific tool."""
        
        if tool == HealthCheckTool.CURL:
            return (f"curl -f --max-time {config.timeout} "
                   f"--retry {config.retries} --retry-delay 1 "
                   f"-o /dev/null -s {config.url}")
        
        elif tool == HealthCheckTool.WGET:
            return (f"wget --timeout={config.timeout} "
                   f"--tries={config.retries} "
                   f"-q --spider {config.url}")
        
        elif tool in [HealthCheckTool.PYTHON, HealthCheckTool.PYTHON3]:
            python_cmd = "python3" if tool == HealthCheckTool.PYTHON3 else "python"
            return (f'{python_cmd} -c "import urllib.request; '
                   f'urllib.request.urlopen(\'{config.url}\', timeout={config.timeout})"')
        
        elif tool == HealthCheckTool.NC:
            # Extract host and port from URL
            if "://" in config.url:
                url_part = config.url.split("://", 1)[1]
            else:
                url_part = config.url
            
            if ":" in url_part:
                host, port = url_part.split(":", 1)
                port = port.split("/")[0]  # Remove path
                return f"nc -z -w {config.timeout} {host} {port}"
        
        elif tool == HealthCheckTool.NODE:
            return (f'node -e "const http = require(\'http\'); '
                   f'http.get(\'{config.url}\', (res) => {{ '
                   f'process.exit(res.statusCode === {config.expected_status} ? 0 : 1); }}) '
                   f'.on(\'error\', () => process.exit(1));"')
        
        return None
    
    def validate_health_check(self, command: str, config: HealthCheckConfig) -> bool:
        """
        Test a health check command in the current environment.
        
        Args:
            command: Health check command to test
            config: Health check configuration
            
        Returns:
            True if health check works, False otherwise
        """
        try:
            self._logger.info(f"Validating health check: {command}")
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                timeout=config.timeout + 5,  # Add buffer
                check=False
            )
            
            success = result.returncode == 0
            
            if success:
                self._logger.info("Health check validation successful")
            else:
                self._logger.warning(f"Health check validation failed: {result.stderr.decode()}")
            
            return success
            
        except subprocess.TimeoutExpired:
            self._logger.error("Health check validation timed out")
            return False
        except Exception as e:
            self._logger.error(f"Health check validation error: {e}")
            return False
    
    def generate_docker_healthcheck(self, config: HealthCheckConfig, service_name: str = "unknown") -> Optional[Dict[str, Any]]:
        """
        Generate Docker Compose healthcheck configuration.
        
        Args:
            config: Health check configuration
            service_name: Name of service
            
        Returns:
            Docker Compose healthcheck dict or None
        """
        command = self.generate_health_check(config, service_name)
        if not command:
            return None
        
        return {
            "test": ["CMD-SHELL", command],
            "interval": f"{config.interval}s",
            "timeout": f"{config.timeout}s",
            "retries": config.retries,
            "start_period": f"{config.start_period}s"
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for observability."""
        available_tools = self.detect_available_tools()
        
        return {
            "status": "healthy",
            "available_tools": [tool.value for tool in available_tools],
            "tool_count": len(available_tools),
            "preferred_tool": available_tools and min(available_tools, key=lambda t: t.value)
        }
    
    def _get_current_time(self) -> float:
        """Get current time for metrics."""
        import time
        return time.time()