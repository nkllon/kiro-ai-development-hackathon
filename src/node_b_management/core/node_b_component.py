"""
NodeBComponent Base Class

Base class for all Node B management components that provides systematic
observability, health monitoring, and Beast Mode framework integration.
"""

import os
import logging
from typing import Dict, Any, List
from datetime import datetime

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleStatus, ModuleCapability, ModuleHealth
from .redis_connection_manager import RedisConnectionManager


class NodeBComponent(ReflectiveModule):
    """
    Base class for all Node B management components
    
    Inherits from ReflectiveModule to provide systematic observability,
    health monitoring, and Beast Mode framework integration. All Node B
    management components should inherit from this class.
    
    Requirements: 6.1, 6.2, 6.3, 6.4
    """

    def __init__(self, component_name: str, node_id: str = None):
        """
        Initialize NodeBComponent with Beast Mode compliance
        
        Args:
            component_name: Name of the component for identification
            node_id: Optional Node B instance ID this component manages
        """
        super().__init__()
        
        self.component_name = component_name
        self.node_id = node_id or f"node-b-{component_name}"
        self.module_id = f"node_b_{component_name}_{self.node_id}"
        
        # Initialize logging with correlation IDs
        self._logger = logging.getLogger(f"node_b.{component_name}")
        
        # Initialize Redis connection manager
        self._redis_manager = None
        self._redis_connected = False
        
        # Node B specific metrics
        self._node_b_metrics = {
            'messages_processed': 0,
            'messages_sent': 0,
            'network_events': 0,
            'health_checks': 0,
            'redis_operations': 0
        }
        
        # Setup Node B specific Prometheus metrics
        self._setup_node_b_metrics()
        
        # Setup health endpoints
        self._setup_node_b_health_endpoints()
        
        self._logger.info(f"NodeBComponent {component_name} initialized for node {self.node_id}")

    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - ReflectiveModule implementation"""
        return {
            "module_id": self.module_id,
            "component_name": self.component_name,
            "node_id": self.node_id,
            "version": "1.0.0",
            "framework": "Beast Mode Node B Management",
            "initialized_at": self._start_time.isoformat(),
            "redis_connected": self._redis_connected,
            "node_b_metrics": self._node_b_metrics.copy()
        }

    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - ReflectiveModule implementation"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.MONITORING,
            ModuleCapability.API_INTEGRATION
        ]

    def get_health_status(self) -> ModuleHealth:
        """Get module health status - ReflectiveModule implementation"""
        # Determine health status based on Redis connectivity and error counts
        if self._error_count > 10:
            status = ModuleStatus.ERROR
            health_score = 0.0
        elif self._error_count > 5 or not self._redis_connected:
            status = ModuleStatus.WARNING
            health_score = 0.5
        elif self._warning_count > 10:
            status = ModuleStatus.DEGRADED
            health_score = 0.7
        else:
            status = ModuleStatus.HEALTHY
            health_score = 1.0

        issues = []
        if not self._redis_connected:
            issues.append("Redis connection not established")
        if self._error_count > 0:
            issues.append(f"Error count: {self._error_count}")
        if self._warning_count > 5:
            issues.append(f"Warning count: {self._warning_count}")

        uptime = (datetime.now() - self._start_time).total_seconds()

        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=uptime,
            error_count=self._error_count,
            warning_count=self._warning_count
        )

    def graceful_degradation(self):
        """Perform graceful degradation - ReflectiveModule implementation"""
        from src.rm_ddd.core.unified_reflective_module import GracefulDegradationResult
        
        try:
            # Attempt to maintain core functionality
            degraded_capabilities = []
            remaining_capabilities = [ModuleCapability.CORE_FUNCTIONALITY]
            
            # Check if we can maintain Redis connectivity
            if not self._redis_connected:
                degraded_capabilities.append(ModuleCapability.API_INTEGRATION)
                self._logger.warning("Redis connectivity lost - degrading API integration capability")
            else:
                remaining_capabilities.append(ModuleCapability.API_INTEGRATION)
            
            # Always try to maintain monitoring
            remaining_capabilities.append(ModuleCapability.MONITORING)
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=degraded_capabilities,
                remaining_capabilities=remaining_capabilities
            )
            
        except Exception as e:
            self._logger.error(f"Graceful degradation failed: {e}")
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=[],
                remaining_capabilities=[],
                error_message=str(e)
            )

    async def get_redis_manager(self) -> RedisConnectionManager:
        """
        Get Redis connection manager with lazy initialization
        
        Returns:
            RedisConnectionManager: Configured Redis connection manager
            
        Requirements: 4.1, 4.2, 6.6
        """
        if self._redis_manager is None:
            try:
                self._redis_manager = RedisConnectionManager()
                # Test connection
                connection = await self._redis_manager.get_connection()
                await connection.ping()
                self._redis_connected = True
                self._logger.info("Redis connection established successfully")
            except Exception as e:
                self._redis_connected = False
                self._increment_error_count()
                self._logger.error(f"Failed to establish Redis connection: {e}")
                raise
        
        return self._redis_manager

    def _setup_node_b_metrics(self):
        """Setup Node B specific Prometheus metrics"""
        try:
            if hasattr(self, '_enable_prometheus') and self._enable_prometheus and hasattr(self, '_prometheus_exporter') and self._prometheus_exporter:
                # Check if the exporter has the method we need
                if hasattr(self._prometheus_exporter, 'register_node_b_metrics'):
                    self._prometheus_exporter.register_node_b_metrics(
                        component_name=self.component_name,
                        node_id=self.node_id
                    )
                    self._logger.info(f"Node B Prometheus metrics registered for {self.component_name}")
                else:
                    # Use standard metrics registration
                    self._logger.info(f"Using standard Prometheus metrics for {self.component_name}")
        except Exception as e:
            self._logger.warning(f"Failed to setup Node B Prometheus metrics: {e}")

    def _setup_node_b_health_endpoints(self):
        """Setup Node B specific health endpoints"""
        # Health endpoints are automatically provided by ReflectiveModule
        # We just need to ensure our health status includes Node B specific information
        self._logger.info(f"Node B health endpoints available at /health, /ready, /metrics")

    def increment_message_count(self, message_type: str = "processed"):
        """
        Increment message processing counters
        
        Args:
            message_type: Type of message operation ("processed" or "sent")
        """
        if message_type == "processed":
            self._node_b_metrics['messages_processed'] += 1
        elif message_type == "sent":
            self._node_b_metrics['messages_sent'] += 1
        
        self._update_activity()

    def increment_network_events(self):
        """Increment network event counter"""
        self._node_b_metrics['network_events'] += 1
        self._update_activity()

    def increment_health_checks(self):
        """Increment health check counter"""
        self._node_b_metrics['health_checks'] += 1
        self._update_activity()

    def increment_redis_operations(self):
        """Increment Redis operation counter"""
        self._node_b_metrics['redis_operations'] += 1
        self._update_activity()

    def get_node_b_metrics(self) -> Dict[str, Any]:
        """
        Get Node B specific metrics
        
        Returns:
            Dict[str, Any]: Node B performance and operational metrics
        """
        base_metrics = self.get_performance_metrics()
        
        return {
            **base_metrics,
            "node_b_specific": self._node_b_metrics.copy(),
            "component_name": self.component_name,
            "node_id": self.node_id,
            "redis_connected": self._redis_connected
        }

    async def validate_beast_mode_compliance(self) -> Dict[str, bool]:
        """
        Validate Beast Mode framework compliance
        
        Returns:
            Dict[str, bool]: Compliance validation results
            
        Requirements: 6.1, 6.2, 6.3, 6.4
        """
        compliance_results = {
            "reflective_module_inheritance": isinstance(self, ReflectiveModule),
            "health_endpoints_available": True,  # Provided by ReflectiveModule
            "prometheus_metrics_enabled": self._enable_prometheus,
            "structured_logging": self._logger is not None,
            "error_handling_patterns": hasattr(self, '_increment_error_count'),
            "redis_coordination": self._redis_manager is not None,
            "correlation_ids": hasattr(self, '_correlation_id')
        }
        
        all_compliant = all(compliance_results.values())
        
        if all_compliant:
            self._logger.info("Beast Mode compliance validation passed")
        else:
            failed_checks = [k for k, v in compliance_results.items() if not v]
            self._logger.warning(f"Beast Mode compliance issues: {failed_checks}")
        
        return compliance_results

    def __repr__(self) -> str:
        """String representation of NodeBComponent"""
        return f"NodeBComponent(component_name='{self.component_name}', node_id='{self.node_id}', redis_connected={self._redis_connected})"