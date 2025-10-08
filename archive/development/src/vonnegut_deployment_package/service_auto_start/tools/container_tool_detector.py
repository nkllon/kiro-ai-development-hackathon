#!/usr/bin/env python3
"""
ContainerToolDetector - Automatic Health Check Tool Detection

Automatically detects which health check tools are available in container images
and provides this information to health check generators with caching for performance.
"""

import subprocess
import logging
from typing import Dict, Any, Set, Optional, List
from dataclasses import dataclass
from enum import Enum
import json
import time

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class ToolType(Enum):
    """Types of tools that can be detected."""
    HTTP_CLIENT = "http_client"
    NETWORK_TOOL = "network_tool"
    SCRIPTING = "scripting"
    SHELL = "shell"


@dataclass
class ToolInfo:
    """Information about a detected tool."""
    name: str
    version: Optional[str]
    path: str
    tool_type: ToolType
    capabilities: List[str]
    last_detected: float


class ContainerToolDetector(ReflectiveModule):
    """
    Detects available health check tools in container environments.
    
    Uses container introspection to test tool availability and caches
    results for performance. Provides fallback strategies when preferred
    tools are not available.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize ContainerToolDetector."""
        super().__init__()
        self._config = config or {}
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Tool detection cache
        self._tool_cache: Dict[str, ToolInfo] = {}
        self._cache_ttl = self._config.get("cache_ttl", 3600)  # 1 hour default
        self._last_scan_time = 0
        
        # Tool definitions
        self._tool_definitions = self._get_tool_definitions()
        
        # Register metrics
        self._register_metrics()
        
        self._logger.info("ContainerToolDetector initialized")
    
    def _register_metrics(self):
        """Register Prometheus metrics."""
        try:
            from prometheus_client import Counter, Gauge, Histogram
            
            self._tools_detected = Counter(
                'container_tools_detected_total',
                'Total tools detected',
                ['tool_name', 'tool_type']
            )
            
            self._detection_time = Histogram(
                'container_tool_detection_seconds',
                'Time spent detecting tools'
            )
            
            self._available_tools_count = Gauge(
                'container_available_tools_count',
                'Number of available tools',
                ['tool_type']
            )
            
        except ImportError:
            self._logger.warning("Prometheus client not available, metrics disabled")
    
    def _get_tool_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Get tool definitions for detection."""
        return {
            "curl": {
                "command": ["curl", "--version"],
                "type": ToolType.HTTP_CLIENT,
                "capabilities": ["http", "https", "ftp", "timeout", "retry"],
                "priority": 1
            },
            "wget": {
                "command": ["wget", "--version"],
                "type": ToolType.HTTP_CLIENT,
                "capabilities": ["http", "https", "timeout", "retry"],
                "priority": 2
            },
            "nc": {
                "command": ["nc", "-h"],
                "type": ToolType.NETWORK_TOOL,
                "capabilities": ["tcp", "udp", "port_check"],
                "priority": 3
            },
            "netcat": {
                "command": ["netcat", "-h"],
                "type": ToolType.NETWORK_TOOL,
                "capabilities": ["tcp", "udp", "port_check"],
                "priority": 3
            },
            "python3": {
                "command": ["python3", "--version"],
                "type": ToolType.SCRIPTING,
                "capabilities": ["http", "https", "json", "scripting"],
                "priority": 4
            },
            "python": {
                "command": ["python", "--version"],
                "type": ToolType.SCRIPTING,
                "capabilities": ["http", "https", "json", "scripting"],
                "priority": 5
            },
            "node": {
                "command": ["node", "--version"],
                "type": ToolType.SCRIPTING,
                "capabilities": ["http", "https", "json", "scripting"],
                "priority": 6
            },
            "bash": {
                "command": ["bash", "--version"],
                "type": ToolType.SHELL,
                "capabilities": ["scripting", "process_control"],
                "priority": 7
            },
            "sh": {
                "command": ["sh", "--version"],
                "type": ToolType.SHELL,
                "capabilities": ["scripting", "basic_process_control"],
                "priority": 8
            }
        }
    
    def detect_available_tools(self, force_refresh: bool = False, container_name: Optional[str] = None) -> Dict[str, ToolInfo]:
        """
        Detect available tools in the current or specified container environment.
        
        Args:
            force_refresh: Force re-detection even if cached
            container_name: Specific container to check (None for current environment)
            
        Returns:
            Dictionary of available tools with their information
        """
        current_time = time.time()
        
        # Check cache validity
        if (not force_refresh and 
            self._tool_cache and 
            (current_time - self._last_scan_time) < self._cache_ttl):
            self._logger.debug("Returning cached tool detection results")
            return self._tool_cache.copy()
        
        start_time = current_time
        self._logger.info("Starting tool detection scan")
        
        detected_tools = {}
        
        for tool_name, tool_def in self._tool_definitions.items():
            try:
                tool_info = self._detect_single_tool(tool_name, tool_def, container_name)
                if tool_info:
                    detected_tools[tool_name] = tool_info
                    
                    # Update metrics
                    if hasattr(self, '_tools_detected'):
                        self._tools_detected.labels(
                            tool_name=tool_name,
                            tool_type=tool_def["type"].value
                        ).inc()
                    
            except Exception as e:
                self._logger.debug(f"Failed to detect tool {tool_name}: {e}")
        
        # Update cache
        self._tool_cache = detected_tools
        self._last_scan_time = current_time
        
        # Update metrics
        if hasattr(self, '_detection_time'):
            duration = time.time() - start_time
            self._detection_time.observe(duration)
        
        if hasattr(self, '_available_tools_count'):
            # Count tools by type
            type_counts = {}
            for tool_info in detected_tools.values():
                tool_type = tool_info.tool_type.value
                type_counts[tool_type] = type_counts.get(tool_type, 0) + 1
            
            for tool_type, count in type_counts.items():
                self._available_tools_count.labels(tool_type=tool_type).set(count)
        
        self._logger.info(f"Detected {len(detected_tools)} available tools: {list(detected_tools.keys())}")
        return detected_tools.copy()
    
    def _detect_single_tool(self, tool_name: str, tool_def: Dict[str, Any], container_name: Optional[str] = None) -> Optional[ToolInfo]:
        """Detect a single tool."""
        try:
            command = tool_def["command"]
            
            if container_name:
                # Run command in specified container
                full_command = ["docker", "exec", container_name] + command
            else:
                # Run command in current environment
                full_command = command
            
            result = subprocess.run(
                full_command,
                capture_output=True,
                timeout=5,
                text=True
            )
            
            if result.returncode == 0:
                # Extract version information
                version = self._extract_version(result.stdout + result.stderr)
                
                # Get tool path
                path = self._get_tool_path(tool_name, container_name)
                
                tool_info = ToolInfo(
                    name=tool_name,
                    version=version,
                    path=path,
                    tool_type=tool_def["type"],
                    capabilities=tool_def["capabilities"],
                    last_detected=time.time()
                )
                
                self._logger.debug(f"Detected tool: {tool_name} v{version} at {path}")
                return tool_info
            
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            self._logger.debug(f"Tool {tool_name} not available: {e}")
        
        return None
    
    def _extract_version(self, output: str) -> Optional[str]:
        """Extract version information from command output."""
        import re
        
        # Common version patterns
        patterns = [
            r'version\s+(\d+\.\d+(?:\.\d+)?)',
            r'v(\d+\.\d+(?:\.\d+)?)',
            r'(\d+\.\d+(?:\.\d+)?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _get_tool_path(self, tool_name: str, container_name: Optional[str] = None) -> str:
        """Get the full path to a tool."""
        try:
            if container_name:
                command = ["docker", "exec", container_name, "which", tool_name]
            else:
                command = ["which", tool_name]
            
            result = subprocess.run(command, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        
        return tool_name  # Fallback to tool name
    
    def get_best_tool_for_capability(self, capability: str, available_tools: Optional[Dict[str, ToolInfo]] = None) -> Optional[ToolInfo]:
        """
        Get the best available tool for a specific capability.
        
        Args:
            capability: Required capability (e.g., "http", "tcp", "scripting")
            available_tools: Pre-detected tools (None to detect automatically)
            
        Returns:
            Best tool for the capability or None if not available
        """
        if available_tools is None:
            available_tools = self.detect_available_tools()
        
        # Filter tools that have the required capability
        capable_tools = []
        for tool_info in available_tools.values():
            if capability in tool_info.capabilities:
                tool_def = self._tool_definitions.get(tool_info.name, {})
                priority = tool_def.get("priority", 999)
                capable_tools.append((priority, tool_info))
        
        if not capable_tools:
            return None
        
        # Sort by priority (lower number = higher priority)
        capable_tools.sort(key=lambda x: x[0])
        return capable_tools[0][1]
    
    def get_tools_by_type(self, tool_type: ToolType, available_tools: Optional[Dict[str, ToolInfo]] = None) -> List[ToolInfo]:
        """
        Get all available tools of a specific type.
        
        Args:
            tool_type: Type of tools to retrieve
            available_tools: Pre-detected tools (None to detect automatically)
            
        Returns:
            List of tools of the specified type
        """
        if available_tools is None:
            available_tools = self.detect_available_tools()
        
        return [tool_info for tool_info in available_tools.values() 
                if tool_info.tool_type == tool_type]
    
    def generate_fallback_strategy(self, preferred_capabilities: List[str]) -> List[ToolInfo]:
        """
        Generate a fallback strategy for health checks based on available tools.
        
        Args:
            preferred_capabilities: List of capabilities in order of preference
            
        Returns:
            Ordered list of tools to try for health checks
        """
        available_tools = self.detect_available_tools()
        strategy = []
        
        for capability in preferred_capabilities:
            tool = self.get_best_tool_for_capability(capability, available_tools)
            if tool and tool not in strategy:
                strategy.append(tool)
        
        return strategy
    
    def export_detection_results(self) -> Dict[str, Any]:
        """Export detection results for external use."""
        available_tools = self.detect_available_tools()
        
        export_data = {
            "scan_time": self._last_scan_time,
            "cache_ttl": self._cache_ttl,
            "tools": {}
        }
        
        for tool_name, tool_info in available_tools.items():
            export_data["tools"][tool_name] = {
                "name": tool_info.name,
                "version": tool_info.version,
                "path": tool_info.path,
                "type": tool_info.tool_type.value,
                "capabilities": tool_info.capabilities,
                "last_detected": tool_info.last_detected
            }
        
        return export_data
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for observability."""
        available_tools = self.detect_available_tools()
        
        # Count tools by type
        type_counts = {}
        for tool_info in available_tools.values():
            tool_type = tool_info.tool_type.value
            type_counts[tool_type] = type_counts.get(tool_type, 0) + 1
        
        return {
            "status": "healthy",
            "total_tools": len(available_tools),
            "tools_by_type": type_counts,
            "cache_age": time.time() - self._last_scan_time,
            "cache_valid": (time.time() - self._last_scan_time) < self._cache_ttl
        }