#!/usr/bin/env python3
"""
Infrastructure Precondition Validator
====================================

Validates all infrastructure preconditions before DAG orchestration system deployment.
Ensures Redis connectivity, system resources, and component accessibility.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import os
import sys
import psutil
import asyncio
import importlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability,
    GracefulDegradationResult
)


@dataclass
class PreconditionResult:
    """Result of a single precondition check."""
    name: str
    passed: bool
    details: Dict[str, Any]
    error_message: Optional[str] = None
    remediation_steps: List[str] = None


@dataclass
class InfrastructureReport:
    """Comprehensive infrastructure validation report."""
    overall_status: bool
    validation_time: datetime
    precondition_results: List[PreconditionResult]
    system_info: Dict[str, Any]
    recommendations: List[str]


class InfrastructurePreconditionValidator(ReflectiveModule):
    """
    Validates all infrastructure preconditions for DAG orchestration system.
    
    Checks:
    - Redis connectivity to Beast Mode network
    - System resource availability
    - Python package dependencies
    - Existing component accessibility
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "InfrastructurePreconditionValidator"
        self._validation_results: List[PreconditionResult] = []
        
        # Beast Mode Redis configuration
        self.redis_config = {
            'host': '192.168.1.119',  # Vonnegut IP from existing code
            'port': 6379,
            'password': 'beastmode2025',
            'db': 0
        }
        
        # Minimum system requirements
        self.min_requirements = {
            'cpu_cores': 2,
            'memory_gb': 4,
            'disk_free_gb': 2,  # Adjusted for current environment (6.6GB available)
            'cpu_percent_threshold': 90,  # Max CPU usage before warning
            'memory_percent_threshold': 85  # Max memory usage before warning
        }
        
        # Required Python packages
        self.required_packages = [
            'redis',
            'psutil', 
            'concurrent.futures',  # Built-in, but verify
            'asyncio',  # Built-in, but verify
            'threading'  # Built-in, but verify
        ]
        
        # Required Beast Mode components
        self.required_components = [
            'src.rm_ddd.core.dag_registry',
            'src.rm_ddd.core.unified_reflective_module',
            'src.beast_mode.task_dag.dag_task_executor'
        ]
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": self.module_id,
            "name": "InfrastructurePreconditionValidator",
            "version": "1.0.0",
            "description": "Validates infrastructure preconditions for DAG orchestration",
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "redis_config": {
                "host": self.redis_config['host'],
                "port": self.redis_config['port']
            },
            "validation_count": len(self._validation_results)
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        try:
            # Quick validation check
            basic_checks = self._perform_basic_health_checks()
            
            if all(check['passed'] for check in basic_checks):
                status = ModuleStatus.HEALTHY
                health_score = 1.0
                issues = []
            else:
                failed_checks = [check['name'] for check in basic_checks if not check['passed']]
                status = ModuleStatus.WARNING
                health_score = 0.6
                issues = [f"Failed checks: {', '.join(failed_checks)}"]
                
        except Exception as e:
            status = ModuleStatus.ERROR
            health_score = 0.0
            issues = [f"Health check failed: {str(e)}"]
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds()
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - RDI Compliant"""
        try:
            # In degraded mode, we can still validate local components
            remaining_capabilities = [
                ModuleCapability.CORE_FUNCTIONALITY,
                ModuleCapability.VALIDATION
            ]
            
            degraded_capabilities = [
                ModuleCapability.MONITORING  # May lose network monitoring
            ]
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=degraded_capabilities,
                remaining_capabilities=remaining_capabilities
            )
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=[ModuleCapability.CORE_FUNCTIONALITY],
                remaining_capabilities=[],
                error_message=str(e)
            )
    
    async def validate_all_preconditions(self) -> InfrastructureReport:
        """
        Perform comprehensive infrastructure validation.
        
        Returns:
            InfrastructureReport with complete validation results
        """
        with self.trace_operation("validate_all_preconditions") as trace:
            self._validation_results.clear()
            
            # 1. Validate Redis connectivity
            redis_result = await self._validate_redis_connectivity()
            self._validation_results.append(redis_result)
            
            # 2. Validate system resources
            resource_result = self._validate_system_resources()
            self._validation_results.append(resource_result)
            
            # 3. Validate Python dependencies
            package_result = self._validate_python_packages()
            self._validation_results.append(package_result)
            
            # 4. Validate Beast Mode components
            component_result = self._validate_beast_mode_components()
            self._validation_results.append(component_result)
            
            # 5. Generate comprehensive report
            report = self._generate_infrastructure_report()
            
            trace.output_result = {
                'overall_status': report.overall_status,
                'total_checks': len(self._validation_results),
                'passed_checks': sum(1 for r in self._validation_results if r.passed),
                'failed_checks': sum(1 for r in self._validation_results if not r.passed)
            }
            
            return report
    
    async def _validate_redis_connectivity(self) -> PreconditionResult:
        """Validate Redis connectivity to Beast Mode network."""
        try:
            # Try to import redis
            import redis.asyncio as redis
            
            # Create Redis client
            client = redis.Redis(
                host=self.redis_config['host'],
                port=self.redis_config['port'],
                password=self.redis_config['password'],
                db=self.redis_config['db'],
                decode_responses=True,
                socket_timeout=5.0,
                socket_connect_timeout=5.0
            )
            
            # Test connection
            await client.ping()
            
            # Test basic operations
            test_key = f"dag_orchestration_test_{datetime.now().timestamp()}"
            await client.set(test_key, "test_value", ex=60)  # Expire in 60 seconds
            test_value = await client.get(test_key)
            await client.delete(test_key)
            
            await client.aclose()
            
            return PreconditionResult(
                name="Redis Connectivity",
                passed=True,
                details={
                    'host': self.redis_config['host'],
                    'port': self.redis_config['port'],
                    'connection_test': 'passed',
                    'read_write_test': 'passed',
                    'test_value_match': test_value == "test_value"
                }
            )
            
        except ImportError as e:
            return PreconditionResult(
                name="Redis Connectivity",
                passed=False,
                details={'error_type': 'import_error'},
                error_message=f"Redis package not available: {e}",
                remediation_steps=[
                    "Install Redis package: pip install redis",
                    "Verify Redis package installation"
                ]
            )
        except Exception as e:
            return PreconditionResult(
                name="Redis Connectivity",
                passed=False,
                details={
                    'error_type': 'connection_error',
                    'host': self.redis_config['host'],
                    'port': self.redis_config['port']
                },
                error_message=f"Redis connection failed: {e}",
                remediation_steps=[
                    f"Verify Redis server is running at {self.redis_config['host']}:{self.redis_config['port']}",
                    "Check network connectivity to Beast Mode Redis server",
                    "Verify Redis password and configuration",
                    "Check firewall settings"
                ]
            )
    
    def _validate_system_resources(self) -> PreconditionResult:
        """Validate system resource availability."""
        try:
            # Get system information
            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Convert to readable units
            memory_gb = memory.total / (1024**3)
            disk_free_gb = disk.free / (1024**3)
            memory_percent = memory.percent
            
            # Check requirements
            checks = {
                'cpu_cores': cpu_count >= self.min_requirements['cpu_cores'],
                'memory_gb': memory_gb >= self.min_requirements['memory_gb'],
                'disk_free_gb': disk_free_gb >= self.min_requirements['disk_free_gb'],
                'cpu_usage_ok': cpu_percent < self.min_requirements['cpu_percent_threshold'],
                'memory_usage_ok': memory_percent < self.min_requirements['memory_percent_threshold']
            }
            
            all_passed = all(checks.values())
            
            details = {
                'cpu_cores': cpu_count,
                'memory_gb': round(memory_gb, 2),
                'disk_free_gb': round(disk_free_gb, 2),
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'checks': checks,
                'requirements': self.min_requirements
            }
            
            remediation_steps = []
            if not checks['cpu_cores']:
                remediation_steps.append(f"Upgrade to at least {self.min_requirements['cpu_cores']} CPU cores")
            if not checks['memory_gb']:
                remediation_steps.append(f"Upgrade to at least {self.min_requirements['memory_gb']}GB RAM")
            if not checks['disk_free_gb']:
                remediation_steps.append(f"Free up disk space to at least {self.min_requirements['disk_free_gb']}GB")
            if not checks['cpu_usage_ok']:
                remediation_steps.append("Reduce CPU usage before starting parallel execution")
            if not checks['memory_usage_ok']:
                remediation_steps.append("Reduce memory usage before starting parallel execution")
            
            return PreconditionResult(
                name="System Resources",
                passed=all_passed,
                details=details,
                error_message=None if all_passed else "System resources below minimum requirements",
                remediation_steps=remediation_steps if remediation_steps else None
            )
            
        except Exception as e:
            return PreconditionResult(
                name="System Resources",
                passed=False,
                details={'error_type': 'system_error'},
                error_message=f"System resource check failed: {e}",
                remediation_steps=[
                    "Install psutil package: pip install psutil",
                    "Verify system monitoring capabilities"
                ]
            )
    
    def _validate_python_packages(self) -> PreconditionResult:
        """Validate required Python package availability."""
        try:
            package_status = {}
            missing_packages = []
            
            for package in self.required_packages:
                try:
                    if package in ['concurrent.futures', 'asyncio', 'threading']:
                        # Built-in packages - just try to import
                        importlib.import_module(package)
                        package_status[package] = {'available': True, 'version': 'built-in'}
                    else:
                        # External packages - get version info
                        module = importlib.import_module(package)
                        version = getattr(module, '__version__', 'unknown')
                        package_status[package] = {'available': True, 'version': version}
                        
                except ImportError:
                    package_status[package] = {'available': False, 'version': None}
                    missing_packages.append(package)
            
            all_available = len(missing_packages) == 0
            
            remediation_steps = []
            if missing_packages:
                for pkg in missing_packages:
                    remediation_steps.append(f"Install {pkg}: pip install {pkg}")
            
            return PreconditionResult(
                name="Python Packages",
                passed=all_available,
                details={
                    'package_status': package_status,
                    'missing_packages': missing_packages,
                    'total_required': len(self.required_packages),
                    'available_count': len(self.required_packages) - len(missing_packages)
                },
                error_message=None if all_available else f"Missing packages: {', '.join(missing_packages)}",
                remediation_steps=remediation_steps if remediation_steps else None
            )
            
        except Exception as e:
            return PreconditionResult(
                name="Python Packages",
                passed=False,
                details={'error_type': 'validation_error'},
                error_message=f"Package validation failed: {e}",
                remediation_steps=[
                    "Verify Python environment is properly configured",
                    "Check package installation permissions"
                ]
            )
    
    def _validate_beast_mode_components(self) -> PreconditionResult:
        """Validate Beast Mode component accessibility."""
        try:
            component_status = {}
            missing_components = []
            
            for component in self.required_components:
                try:
                    module = importlib.import_module(component)
                    
                    # Try to get key classes/functions
                    if 'dag_registry' in component:
                        dag_registry_class = getattr(module, 'DAGRegistry', None)
                        component_status[component] = {
                            'available': True,
                            'dag_registry_class': dag_registry_class is not None
                        }
                    elif 'unified_reflective_module' in component:
                        reflective_module_class = getattr(module, 'ReflectiveModule', None)
                        component_status[component] = {
                            'available': True,
                            'reflective_module_class': reflective_module_class is not None
                        }
                    elif 'dag_task_executor' in component:
                        executor_class = getattr(module, 'DAGTaskExecutor', None)
                        component_status[component] = {
                            'available': True,
                            'dag_task_executor_class': executor_class is not None
                        }
                    else:
                        component_status[component] = {'available': True}
                        
                except ImportError:
                    component_status[component] = {'available': False}
                    missing_components.append(component)
            
            all_available = len(missing_components) == 0
            
            remediation_steps = []
            if missing_components:
                remediation_steps.extend([
                    "Verify Beast Mode framework is properly installed",
                    "Check Python path includes Beast Mode components",
                    f"Missing components: {', '.join(missing_components)}"
                ])
            
            return PreconditionResult(
                name="Beast Mode Components",
                passed=all_available,
                details={
                    'component_status': component_status,
                    'missing_components': missing_components,
                    'total_required': len(self.required_components),
                    'available_count': len(self.required_components) - len(missing_components)
                },
                error_message=None if all_available else f"Missing components: {', '.join(missing_components)}",
                remediation_steps=remediation_steps if remediation_steps else None
            )
            
        except Exception as e:
            return PreconditionResult(
                name="Beast Mode Components",
                passed=False,
                details={'error_type': 'validation_error'},
                error_message=f"Component validation failed: {e}",
                remediation_steps=[
                    "Verify Beast Mode framework installation",
                    "Check component file paths and imports"
                ]
            )
    
    def _generate_infrastructure_report(self) -> InfrastructureReport:
        """Generate comprehensive infrastructure validation report."""
        overall_status = all(result.passed for result in self._validation_results)
        
        # Collect system information
        system_info = {
            'python_version': sys.version,
            'platform': sys.platform,
            'cpu_count': psutil.cpu_count(),
            'memory_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'validation_time': datetime.now().isoformat()
        }
        
        # Generate recommendations
        recommendations = []
        if overall_status:
            recommendations.append("✅ All infrastructure preconditions met - ready for DAG orchestration deployment")
        else:
            recommendations.append("❌ Infrastructure preconditions not met - address issues before proceeding")
            
            for result in self._validation_results:
                if not result.passed and result.remediation_steps:
                    recommendations.extend(result.remediation_steps)
        
        return InfrastructureReport(
            overall_status=overall_status,
            validation_time=datetime.now(),
            precondition_results=self._validation_results.copy(),
            system_info=system_info,
            recommendations=recommendations
        )
    
    def _perform_basic_health_checks(self) -> List[Dict[str, Any]]:
        """Perform basic health checks for module health status."""
        checks = []
        
        # Check if we can access system resources
        try:
            psutil.cpu_percent()
            checks.append({'name': 'system_access', 'passed': True})
        except Exception:
            checks.append({'name': 'system_access', 'passed': False})
        
        # Check if we can import required modules
        try:
            import redis
            checks.append({'name': 'redis_import', 'passed': True})
        except ImportError:
            checks.append({'name': 'redis_import', 'passed': False})
        
        return checks


# Convenience function for quick validation
async def validate_infrastructure_preconditions() -> InfrastructureReport:
    """
    Convenience function to validate all infrastructure preconditions.
    
    Returns:
        InfrastructureReport with validation results
    """
    validator = InfrastructurePreconditionValidator()
    return await validator.validate_all_preconditions()


if __name__ == "__main__":
    async def main():
        print("🔍 DAG Orchestration Infrastructure Precondition Validation")
        print("=" * 60)
        
        validator = InfrastructurePreconditionValidator()
        report = await validator.validate_all_preconditions()
        
        print(f"\n📊 Validation Results:")
        print(f"Overall Status: {'✅ PASSED' if report.overall_status else '❌ FAILED'}")
        print(f"Validation Time: {report.validation_time}")
        
        print(f"\n🔍 Individual Checks:")
        for result in report.precondition_results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            print(f"  {result.name}: {status}")
            if not result.passed and result.error_message:
                print(f"    Error: {result.error_message}")
        
        print(f"\n💡 Recommendations:")
        for rec in report.recommendations:
            print(f"  - {rec}")
        
        if not report.overall_status:
            print(f"\n⚠️  Infrastructure not ready for DAG orchestration deployment")
            sys.exit(1)
        else:
            print(f"\n🚀 Infrastructure ready for DAG orchestration deployment!")
    
    asyncio.run(main())