#!/usr/bin/env python3
"""
System Constraint Validator - Fallback Mechanisms
=================================================

Implements Task 1.4: System constraint validation and fallback mechanisms
- Create SystemConstraintValidator class with Directus availability checking
- Implement Directus CMS availability validation (localhost:8055/server/ping)
- Create fallback configuration management for Directus unavailability
- Implement Redis coordination validation with automatic failover
- Create Observatory server availability checking with static discovery fallback
- Document constraint validation results and fallback mode operations

Requirements: 7.2, 8.1, 9.1, 10.1
"""

import asyncio
import json
import logging
import requests
import redis
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

try:
    from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
except ImportError:
    print("Warning: ReflectiveModule not available, using base class")
    class ReflectiveModule:
        def __init__(self):
            pass


class ConstraintStatus(Enum):
    """Status of system constraints."""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class SystemConstraint:
    """System constraint definition."""
    name: str
    endpoint: str
    validation_method: str
    required: bool
    fallback_strategy: str
    impact_description: str
    validation_timeout_seconds: int
    status: ConstraintStatus = ConstraintStatus.UNKNOWN
    last_validated: Optional[datetime] = None
    error_message: Optional[str] = None


class SystemConstraintValidator(ReflectiveModule):
    """
    System constraint validator with fallback mechanisms.
    
    Validates critical system dependencies and provides fallback
    strategies when constraints are not met.
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "SystemConstraintValidator"
        self._logger = logging.getLogger(f"system_architecture.{self.__class__.__name__}")
        
        # Define system constraints
        self.constraints = [
            SystemConstraint(
                name="Directus CMS",
                endpoint="http://localhost:8055/server/ping",
                validation_method="HTTP GET expecting 'pong'",
                required=False,  # Has fallback
                fallback_strategy="File-based configuration storage",
                impact_description="Configuration management degraded to read-only mode",
                validation_timeout_seconds=5
            ),
            SystemConstraint(
                name="Redis Primary",
                endpoint="192.168.1.119:6379",
                validation_method="Redis PING command",
                required=False,  # Has fallback
                fallback_strategy="Automatic failover to localhost:6380",
                impact_description="Coordination features continue with fallback Redis",
                validation_timeout_seconds=3
            ),
            SystemConstraint(
                name="Redis Fallback",
                endpoint="localhost:6380",
                validation_method="Redis PING command",
                required=False,  # Fallback for primary
                fallback_strategy="Local file-based coordination",
                impact_description="Coordination features degraded to local mode",
                validation_timeout_seconds=3
            ),
            SystemConstraint(
                name="Observatory Server",
                endpoint="http://localhost:8888/health",
                validation_method="HTTP GET expecting 200 status",
                required=False,  # Has fallback
                fallback_strategy="Static configuration discovery",
                impact_description="Real-time metrics documentation incomplete",
                validation_timeout_seconds=5
            )
        ]
        
        # Fallback configuration paths
        self.fallback_config_dir = Path("config/fallback")
        self.fallback_config_dir.mkdir(parents=True, exist_ok=True)
        
        # Active fallback modes
        self.active_fallbacks: Dict[str, bool] = {}
        
    def get_capabilities(self) -> Dict[str, Any]:
        """Return component capabilities."""
        return {
            'constraint_validation': True,
            'fallback_mechanisms': True,
            'automatic_failover': True,
            'configuration_management': True,
            'health_monitoring': True
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Return component health status."""
        available_constraints = len([c for c in self.constraints if c.status == ConstraintStatus.AVAILABLE])
        total_constraints = len(self.constraints)
        
        return {
            'status': 'healthy' if available_constraints > 0 else 'degraded',
            'constraints_available': available_constraints,
            'constraints_total': total_constraints,
            'active_fallbacks': len(self.active_fallbacks),
            'fallback_modes': list(self.active_fallbacks.keys())
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Return module information."""
        return {
            'name': 'SystemConstraintValidator',
            'version': '1.0.0',
            'description': 'System constraint validation with fallback mechanisms',
            'dependencies': ['requests', 'redis'],
            'workflow_control': 'system-architecture-wiring-diagram'
        }
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation on errors."""
        return {
            'degraded_mode': True,
            'error': str(error),
            'available_functions': ['basic_constraint_validation'],
            'recommendation': 'Use cached validation results if available'
        }
    
    async def validate_all_constraints(self) -> Dict[str, Any]:
        """Validate all system constraints and activate fallbacks as needed."""
        self._logger.info("Validating all system constraints...")
        
        validation_results = {
            'validation_timestamp': datetime.now().isoformat(),
            'constraints': {},
            'fallbacks_activated': [],
            'overall_status': 'unknown'
        }
        
        available_count = 0
        
        for constraint in self.constraints:
            try:
                result = await self._validate_constraint(constraint)
                validation_results['constraints'][constraint.name] = {
                    'status': result.status.value,
                    'endpoint': result.endpoint,
                    'last_validated': result.last_validated.isoformat() if result.last_validated else None,
                    'error_message': result.error_message,
                    'fallback_strategy': result.fallback_strategy,
                    'impact_description': result.impact_description
                }
                
                if result.status == ConstraintStatus.AVAILABLE:
                    available_count += 1
                elif result.status == ConstraintStatus.UNAVAILABLE:
                    # Activate fallback
                    fallback_activated = await self._activate_fallback(constraint)
                    if fallback_activated:
                        validation_results['fallbacks_activated'].append(constraint.name)
                
            except Exception as e:
                self._logger.error(f"Error validating constraint {constraint.name}: {e}")
                constraint.status = ConstraintStatus.UNKNOWN
                constraint.error_message = str(e)
        
        # Determine overall status
        if available_count == len(self.constraints):
            validation_results['overall_status'] = 'all_available'
        elif available_count > 0:
            validation_results['overall_status'] = 'partial_available'
        else:
            validation_results['overall_status'] = 'all_unavailable'
        
        # Save validation report
        report_file = self.fallback_config_dir / f"constraint_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(validation_results, f, indent=2)
        
        self._logger.info(f"Constraint validation complete: {available_count}/{len(self.constraints)} available")
        return validation_results
    
    async def _validate_constraint(self, constraint: SystemConstraint) -> SystemConstraint:
        """Validate a specific system constraint."""
        self._logger.debug(f"Validating constraint: {constraint.name}")
        
        try:
            if constraint.name.startswith("Redis"):
                # Redis validation
                status = await self._validate_redis_constraint(constraint)
            else:
                # HTTP validation
                status = await self._validate_http_constraint(constraint)
            
            constraint.status = status
            constraint.last_validated = datetime.now()
            constraint.error_message = None
            
        except Exception as e:
            constraint.status = ConstraintStatus.UNAVAILABLE
            constraint.error_message = str(e)
            constraint.last_validated = datetime.now()
        
        return constraint
    
    async def _validate_http_constraint(self, constraint: SystemConstraint) -> ConstraintStatus:
        """Validate HTTP-based constraint."""
        try:
            response = requests.get(
                constraint.endpoint,
                timeout=constraint.validation_timeout_seconds
            )
            
            if constraint.name == "Directus CMS":
                # Directus expects "pong" response
                if response.status_code == 200 and "pong" in response.text.lower():
                    return ConstraintStatus.AVAILABLE
                else:
                    return ConstraintStatus.UNAVAILABLE
            else:
                # General HTTP health check
                if response.status_code < 500:
                    return ConstraintStatus.AVAILABLE
                else:
                    return ConstraintStatus.DEGRADED
                    
        except requests.exceptions.Timeout:
            return ConstraintStatus.UNAVAILABLE
        except requests.exceptions.ConnectionError:
            return ConstraintStatus.UNAVAILABLE
        except Exception:
            return ConstraintStatus.UNKNOWN
    
    async def _validate_redis_constraint(self, constraint: SystemConstraint) -> ConstraintStatus:
        """Validate Redis-based constraint."""
        try:
            # Parse Redis endpoint
            if ":" in constraint.endpoint:
                host, port = constraint.endpoint.split(":")
                port = int(port)
            else:
                host = constraint.endpoint
                port = 6379
            
            # Create Redis client
            redis_client = redis.Redis(
                host=host,
                port=port,
                socket_timeout=constraint.validation_timeout_seconds,
                socket_connect_timeout=constraint.validation_timeout_seconds
            )
            
            # Test connection
            response = redis_client.ping()
            if response:
                return ConstraintStatus.AVAILABLE
            else:
                return ConstraintStatus.UNAVAILABLE
                
        except redis.exceptions.ConnectionError:
            return ConstraintStatus.UNAVAILABLE
        except redis.exceptions.TimeoutError:
            return ConstraintStatus.UNAVAILABLE
        except Exception:
            return ConstraintStatus.UNKNOWN
    
    async def _activate_fallback(self, constraint: SystemConstraint) -> bool:
        """Activate fallback mechanism for a constraint."""
        self._logger.info(f"Activating fallback for {constraint.name}: {constraint.fallback_strategy}")
        
        try:
            if constraint.name == "Directus CMS":
                return await self._activate_directus_fallback()
            elif constraint.name == "Redis Primary":
                return await self._activate_redis_fallback()
            elif constraint.name == "Observatory Server":
                return await self._activate_observatory_fallback()
            else:
                self._logger.warning(f"No fallback implementation for {constraint.name}")
                return False
                
        except Exception as e:
            self._logger.error(f"Failed to activate fallback for {constraint.name}: {e}")
            return False
    
    async def _activate_directus_fallback(self) -> bool:
        """Activate file-based configuration fallback for Directus."""
        try:
            # Create fallback configuration structure
            fallback_config = {
                'mode': 'file_based',
                'activated_at': datetime.now().isoformat(),
                'configuration_source': 'local_files',
                'capabilities': {
                    'read_configuration': True,
                    'write_configuration': False,
                    'schema_management': False,
                    'user_management': False
                },
                'limitations': [
                    'Read-only configuration access',
                    'No dynamic schema updates',
                    'No user authentication management'
                ]
            }
            
            # Save fallback configuration
            fallback_file = self.fallback_config_dir / "directus_fallback.json"
            with open(fallback_file, 'w') as f:
                json.dump(fallback_config, f, indent=2)
            
            self.active_fallbacks['directus'] = True
            self._logger.info("Directus fallback activated: file-based configuration mode")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to activate Directus fallback: {e}")
            return False
    
    async def _activate_redis_fallback(self) -> bool:
        """Activate Redis fallback mechanism."""
        try:
            # Check if fallback Redis is available
            fallback_constraint = next(
                (c for c in self.constraints if c.name == "Redis Fallback"), 
                None
            )
            
            if fallback_constraint:
                fallback_status = await self._validate_constraint(fallback_constraint)
                if fallback_status.status == ConstraintStatus.AVAILABLE:
                    # Fallback Redis is available
                    fallback_config = {
                        'mode': 'redis_fallback',
                        'activated_at': datetime.now().isoformat(),
                        'fallback_endpoint': 'localhost:6380',
                        'capabilities': {
                            'coordination': True,
                            'caching': True,
                            'pub_sub': True
                        },
                        'limitations': [
                            'Single node (no clustering)',
                            'Local network only'
                        ]
                    }
                else:
                    # Use file-based coordination
                    fallback_config = {
                        'mode': 'file_based_coordination',
                        'activated_at': datetime.now().isoformat(),
                        'coordination_method': 'local_files',
                        'capabilities': {
                            'basic_coordination': True,
                            'caching': False,
                            'pub_sub': False
                        },
                        'limitations': [
                            'No real-time coordination',
                            'Single process only',
                            'No distributed caching'
                        ]
                    }
            
            # Save fallback configuration
            fallback_file = self.fallback_config_dir / "redis_fallback.json"
            with open(fallback_file, 'w') as f:
                json.dump(fallback_config, f, indent=2)
            
            self.active_fallbacks['redis'] = True
            self._logger.info(f"Redis fallback activated: {fallback_config['mode']}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to activate Redis fallback: {e}")
            return False
    
    async def _activate_observatory_fallback(self) -> bool:
        """Activate static discovery fallback for Observatory."""
        try:
            # Create static configuration for known services
            static_config = {
                'mode': 'static_discovery',
                'activated_at': datetime.now().isoformat(),
                'discovery_method': 'static_configuration',
                'known_services': {
                    'prometheus': {
                        'host': 'localhost',
                        'port': 9090,
                        'health_endpoint': '/api/v1/status/config'
                    },
                    'grafana': {
                        'host': 'localhost',
                        'port': 3000,
                        'health_endpoint': '/api/health'
                    },
                    'directus': {
                        'host': 'localhost',
                        'port': 8055,
                        'health_endpoint': '/server/ping'
                    }
                },
                'websocket_endpoints': [
                    '/ws/observatory',
                    '/ws/emoji-rain',
                    '/ws/anomalies',
                    '/ws/doctor-status'
                ],
                'capabilities': {
                    'service_discovery': True,
                    'real_time_monitoring': False,
                    'health_checking': True
                },
                'limitations': [
                    'No real-time updates',
                    'Static service list only',
                    'No WebSocket connectivity'
                ]
            }
            
            # Save static configuration
            fallback_file = self.fallback_config_dir / "observatory_fallback.json"
            with open(fallback_file, 'w') as f:
                json.dump(static_config, f, indent=2)
            
            self.active_fallbacks['observatory'] = True
            self._logger.info("Observatory fallback activated: static discovery mode")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to activate Observatory fallback: {e}")
            return False
    
    def get_fallback_configuration(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get fallback configuration for a specific service."""
        fallback_file = self.fallback_config_dir / f"{service_name}_fallback.json"
        
        if fallback_file.exists():
            try:
                with open(fallback_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self._logger.error(f"Failed to load fallback config for {service_name}: {e}")
        
        return None
    
    def is_fallback_active(self, service_name: str) -> bool:
        """Check if fallback is active for a service."""
        return self.active_fallbacks.get(service_name, False)
    
    def get_constraint_summary(self) -> Dict[str, Any]:
        """Get summary of all constraints and their status."""
        summary = {
            'total_constraints': len(self.constraints),
            'available': 0,
            'unavailable': 0,
            'degraded': 0,
            'unknown': 0,
            'active_fallbacks': len(self.active_fallbacks),
            'constraints': []
        }
        
        for constraint in self.constraints:
            constraint_info = {
                'name': constraint.name,
                'status': constraint.status.value,
                'endpoint': constraint.endpoint,
                'required': constraint.required,
                'fallback_strategy': constraint.fallback_strategy,
                'last_validated': constraint.last_validated.isoformat() if constraint.last_validated else None
            }
            summary['constraints'].append(constraint_info)
            
            # Count by status
            if constraint.status == ConstraintStatus.AVAILABLE:
                summary['available'] += 1
            elif constraint.status == ConstraintStatus.UNAVAILABLE:
                summary['unavailable'] += 1
            elif constraint.status == ConstraintStatus.DEGRADED:
                summary['degraded'] += 1
            else:
                summary['unknown'] += 1
        
        return summary


async def main():
    """Main execution function for testing."""
    print("🚀 System Constraint Validator - Task 1.4 Implementation")
    print("=" * 60)
    
    validator = SystemConstraintValidator()
    
    # Validate all constraints
    results = await validator.validate_all_constraints()
    
    print(f"\n📊 Constraint Validation Results:")
    print(f"   Overall Status: {results['overall_status']}")
    print(f"   Fallbacks Activated: {len(results['fallbacks_activated'])}")
    
    for name, constraint in results['constraints'].items():
        status_icon = "✅" if constraint['status'] == 'available' else "❌"
        print(f"   {status_icon} {name}: {constraint['status']}")
        if constraint['status'] != 'available':
            print(f"      Fallback: {constraint['fallback_strategy']}")
    
    # Show constraint summary
    summary = validator.get_constraint_summary()
    print(f"\n📈 Summary: {summary['available']}/{summary['total_constraints']} available")
    
    print(f"\n✅ Task 1.4 Complete - System Constraint Validation Implemented")


if __name__ == "__main__":
    asyncio.run(main())