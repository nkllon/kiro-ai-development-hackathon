#!/usr/bin/env python3
"""
Base ReflectiveModule class - RDI Compliant
This is the SINGLE, CANONICAL base class for all ReflectiveModule implementations.
"""

import argparse
import sys
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass

class ModuleStatus(Enum):
    """Module operational status - RDI Compliant"""
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"

class ModuleCapability(Enum):
    """Module capability types - RDI Compliant"""
    # Core capabilities
    CORE_FUNCTIONALITY = "core_functionality"
    DATA_PROCESSING = "data_processing"
    API_INTEGRATION = "api_integration"
    FILE_OPERATIONS = "file_operations"
    VALIDATION = "validation"
    MONITORING = "monitoring"
    
    # SCA capabilities
    SCA_ANALYSIS = "sca_analysis"
    COMPLIANCE_CHECKING = "compliance_checking"
    RANDOM_ATTACK = "random_attack"
    EFFICIENCY_ANALYSIS = "efficiency_analysis"
    BEAST_MODE = "beast_mode"

@dataclass
class ModuleHealth:
    """Module health information - RDI Compliant"""
    module_id: str
    status: ModuleStatus
    health_score: float  # 0.0 to 1.0
    issues: List[str]
    capabilities: List[ModuleCapability]
    dependencies: List[str]
    metrics: Dict[str, Any]
    last_check: datetime
    uptime_seconds: float = 0.0
    error_count: int = 0
    warning_count: int = 0

class ReflectiveModule(ABC):
    """
    Base ReflectiveModule class - RDI Compliant
    
    This is the SINGLE, CANONICAL base class for all ReflectiveModule implementations.
    Provides systematic compliance, health monitoring, and registry integration.
    """
    
    def __init__(self, module_name: str, version: str = "1.0.0"):
        """Initialize the reflective module - RDI Compliant"""
        self.module_name = module_name
        self.version = version
        self.module_id = f"{module_name}_{self.__class__.__name__}"
        self._start_time = datetime.now()
        self._last_activity = datetime.now()
        self._error_count = 0
        self._warning_count = 0
        
    @abstractmethod
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        pass
        
    @abstractmethod
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        pass
        
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """Get module dependencies - RDI Compliant"""
        pass
        
    @abstractmethod
    def check_health(self) -> ModuleHealth:
        """Check module health - RDI Compliant"""
        pass
        
    def get_configuration(self) -> Dict[str, Any]:
        """Get module configuration - RDI Compliant"""
        return {
            'module_name': self.module_name,
            'version': self.version,
            'module_id': self.module_id
        }
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics - RDI Compliant"""
        return {
            'uptime_seconds': self.get_uptime_seconds(),
            'error_count': self._error_count,
            'warning_count': self._warning_count,
            'last_activity': self._last_activity.isoformat()
        }
        
    def is_healthy(self) -> bool:
        """Check if module is healthy - RDI Compliant"""
        health = self.check_health()
        return health.status == ModuleStatus.HEALTHY
        
    def get_module_status(self) -> ModuleStatus:
        """Get module status - RDI Compliant"""
        health = self.check_health()
        return health.status
        
    def get_health_indicators(self) -> Dict[str, Any]:
        """Get health indicators - RDI Compliant"""
        health = self.check_health()
        return {
            "status": health.status.value,
            "health_score": health.health_score,
            "issues": health.issues,
            "uptime_seconds": health.uptime_seconds,
            "error_count": health.error_count,
            "warning_count": health.warning_count
        }
        
    def update_activity(self) -> None:
        """Update last activity timestamp - RDI Compliant"""
        self._last_activity = datetime.now()
        
    def get_uptime_seconds(self) -> float:
        """Get module uptime in seconds - RDI Compliant"""
        return (datetime.now() - self._start_time).total_seconds()
        
    def increment_error_count(self) -> None:
        """Increment error count - RDI Compliant"""
        self._error_count += 1
        
    def increment_warning_count(self) -> None:
        """Increment warning count - RDI Compliant"""
        self._warning_count += 1
        
    def reset_metrics(self) -> None:
        """Reset module metrics - RDI Compliant"""
        self._error_count = 0
        self._warning_count = 0
        self._start_time = datetime.now()
        self._last_activity = datetime.now()
        
    def get_interface_metadata(self) -> Dict[str, Any]:
        """Get interface metadata for registry - RDI Compliant"""
        return {
            'module_id': self.module_id,
            'interface_type': self.__class__.__name__,
            'version': self.version,
            'dependencies': self.get_dependencies(),
            'capabilities': [cap.value for cap in self.get_capabilities()]
        }
        
    def register_module(self, registry) -> None:
        """Register module with registry - RDI Compliant"""
        if hasattr(registry, 'register'):
            registry.register(self.get_interface_metadata())
            
    def health_check(self) -> Dict[str, Any]:
        """Perform health check - RDI Compliant"""
        health = self.check_health()
        return {
            'status': health.status.value,
            'timestamp': datetime.now().isoformat(),
            'module_id': self.module_id,
            'health_score': health.health_score,
            'issues': health.issues
        }
        
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status - RDI Compliant"""
        return self.health_check()
    
    # CLI Implementation - RDI Compliant
    def cli_main(self, args: Optional[List[str]] = None) -> int:
        """Main CLI entry point - RDI Compliant"""
        if args is None:
            args = sys.argv[1:]
        
        parser = self._create_cli_parser()
        parsed_args = parser.parse_args(args)
        
        try:
            return self._handle_cli_command(parsed_args)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    
    def _create_cli_parser(self) -> argparse.ArgumentParser:
        """Create CLI argument parser - RDI Compliant"""
        parser = argparse.ArgumentParser(
            description=f"{self.__class__.__name__} - ReflectiveModule CLI",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # Standard commands
        parser.add_argument('--version', action='version', version=f'{self.__class__.__name__} 1.0.0')
        parser.add_argument('--status', action='store_true', help='Show module status')
        parser.add_argument('--health', action='store_true', help='Show module health')
        parser.add_argument('--capabilities', action='store_true', help='Show module capabilities')
        parser.add_argument('--info', action='store_true', help='Show module information')
        parser.add_argument('--config', action='store_true', help='Show module configuration')
        parser.add_argument('--metrics', action='store_true', help='Show module metrics')
        
        # Add module-specific commands based on capabilities
        capabilities = self.get_capabilities()
        if ModuleCapability.DATA_PROCESSING in capabilities:
            parser.add_argument('--process', help='Process data input')
        if ModuleCapability.VALIDATION in capabilities:
            parser.add_argument('--validate', help='Validate input data')
        if ModuleCapability.MONITORING in capabilities:
            parser.add_argument('--monitor', action='store_true', help='Start monitoring')
        
        return parser
    
    def _handle_cli_command(self, args: argparse.Namespace) -> int:
        """Handle CLI commands - RDI Compliant"""
        if args.status:
            self._cli_show_status()
        elif args.health:
            self._cli_show_health()
        elif args.capabilities:
            self._cli_show_capabilities()
        elif args.info:
            self._cli_show_info()
        elif args.config:
            self._cli_show_config()
        elif args.metrics:
            self._cli_show_metrics()
        elif hasattr(args, 'process') and args.process:
            self._cli_process_data(args.process)
        elif hasattr(args, 'validate') and args.validate:
            self._cli_validate_data(args.validate)
        elif hasattr(args, 'monitor') and args.monitor:
            self._cli_start_monitoring()
        else:
            # Default: show help
            self._cli_show_help()
        
        return 0
    
    def _cli_show_status(self):
        """Show module status - RDI Compliant"""
        info = self.get_module_info()
        print(f"Module: {info.get('module_name', 'Unknown')}")
        print(f"Version: {info.get('version', 'Unknown')}")
        print(f"Status: {info.get('status', 'Unknown')}")
        print(f"Module ID: {self.module_id}")
    
    def _cli_show_health(self):
        """Show module health - RDI Compliant"""
        health = self.check_health()
        print(f"Health Status: {health.status.value}")
        print(f"Health Score: {health.health_score:.2f}")
        print(f"Uptime: {health.uptime_seconds:.2f} seconds")
        if health.issues:
            print("Issues:")
            for issue in health.issues:
                print(f"  - {issue}")
    
    def _cli_show_capabilities(self):
        """Show module capabilities - RDI Compliant"""
        capabilities = self.get_capabilities()
        print("Module Capabilities:")
        for cap in capabilities:
            print(f"  - {cap.value}")
    
    def _cli_show_info(self):
        """Show module information - RDI Compliant"""
        info = self.get_module_info()
        print(json.dumps(info, indent=2, default=str))
    
    def _cli_show_config(self):
        """Show module configuration - RDI Compliant"""
        config = {
            "module_id": self.module_id,
            "class_name": self.__class__.__name__,
            "module_file": self.__class__.__module__,
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "dependencies": self.get_dependencies()
        }
        print(json.dumps(config, indent=2, default=str))
    
    def _cli_show_metrics(self):
        """Show module metrics - RDI Compliant"""
        health = self.check_health()
        metrics = {
            "module_id": self.module_id,
            "health_score": health.health_score,
            "uptime_seconds": health.uptime_seconds,
            "last_check": health.last_check.isoformat(),
            "metrics": health.metrics
        }
        print(json.dumps(metrics, indent=2, default=str))
    
    def _cli_show_help(self):
        """Show help information - RDI Compliant"""
        print(f"{self.__class__.__name__} - ReflectiveModule CLI")
        print("Available commands:")
        print("  --status       Show module status")
        print("  --health       Show module health")
        print("  --capabilities Show module capabilities")
        print("  --info         Show module information")
        print("  --config       Show module configuration")
        print("  --metrics      Show module metrics")
        print("  --help         Show this help message")
        print("  --version      Show version information")
    
    def _cli_process_data(self, data: str):
        """Process data input - RDI Compliant"""
        if ModuleCapability.DATA_PROCESSING in self.get_capabilities():
            print(f"Processing data: {data}")
            # Override in subclasses for actual processing
        else:
            print("Data processing not supported by this module")
    
    def _cli_validate_data(self, data: str):
        """Validate data input - RDI Compliant"""
        if ModuleCapability.VALIDATION in self.get_capabilities():
            print(f"Validating data: {data}")
            # Override in subclasses for actual validation
        else:
            print("Validation not supported by this module")
    
    def _cli_start_monitoring(self):
        """Start monitoring - RDI Compliant"""
        if ModuleCapability.MONITORING in self.get_capabilities():
            print("Starting monitoring...")
            # Override in subclasses for actual monitoring
        else:
            print("Monitoring not supported by this module")

# RDI Compliance Marker
RDI_COMPLIANT = True
UNIFIED_INTERFACE_VERSION = "1.0.0"
CANONICAL_SOURCE = "src/rm_ddd/core/base_reflective_module.py"
