#!/usr/bin/env python3
"""
CLI Parser - Argument parsing and validation

Extracted from cli.py for RM-DDD compliance.
Single responsibility: CLI argument parsing and validation.
"""

import argparse
import logging
from typing import Dict, Any, Optional
from .reflective_module import (
    ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, 
    ModuleConfiguration, register_module
)
from datetime import datetime


logger = logging.getLogger(__name__)

    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information."""
        return {
            'module_id': self.module_id,
            'version': self.version,
            'name': 'Cli Parser',
            'description': 'cli_parser module for DevPost integration',
            'author': 'DevPost Integration Team',
            'created_at': self._start_time.isoformat(),
            'interface_version': self.get_interface_version()
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return []
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return []
    
    def check_health(self) -> ModuleHealth:
        """Perform comprehensive health check."""
        issues = []
        health_score = 1.0
        
        try:
            # Basic health checks
            if not hasattr(self, 'module_id'):
                issues.append("Missing module_id")
                health_score -= 0.2
            
            # Add module-specific health checks here
            
            
            # Determine status
            if health_score >= 0.9:
                status = ModuleStatus.HEALTHY
            elif health_score >= 0.7:
                status = ModuleStatus.DEGRADED
            else:
                status = ModuleStatus.UNHEALTHY
            
            return ModuleHealth(
                module_id=self.module_id,
                status=status,
                last_check=datetime.now(),
                health_score=max(0.0, health_score),
                issues=issues,
                capabilities=self.get_capabilities(),
                dependencies=self.get_dependencies(),
                metrics=self.get_metrics()
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return ModuleHealth(
                module_id=self.module_id,
                status=ModuleStatus.UNHEALTHY,
                last_check=datetime.now(),
                health_score=0.0,
                issues=[f"Health check exception: {e}"],
                capabilities=self.get_capabilities(),
                dependencies=self.get_dependencies(),
                metrics={}
            )
    
    def get_configuration(self) -> ModuleConfiguration:
        """Get module configuration."""
        return ModuleConfiguration(
            module_id=self.module_id,
            config_version="1.0.0",
            parameters={},
            required_parameters=[],
            optional_parameters=[],
            validation_rules={},
            last_updated=datetime.now()
        )
    
    def update_configuration(self, config: ModuleConfiguration) -> bool:
        """Update module configuration."""
        try:
            if not config.is_valid():
                logger.error("Invalid configuration provided")
                return False
            
            logger.info(f"Configuration updated for {self.module_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        uptime = (datetime.now() - self._start_time).total_seconds()
        
        return {
            'uptime_seconds': uptime,
            'uptime_hours': uptime / 3600,
            'last_check': datetime.now().isoformat()
        }
    
    def reset_metrics(self) -> None:
        """Reset module metrics to initial state."""
        self._start_time = datetime.now()
        logger.info("Metrics reset for {self.module_id} module")


class CLIParser(ReflectiveModule):
    """CLI argument parser and validator."""
    
    def __init__(self):
        super().__init__(module_id="cli_parser", version="1.0.0")
        self._start_time = datetime.now()
        register_module(self)

        """Initialize CLI parser."""
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser with all commands."""
        parser = argparse.ArgumentParser(
            description="DevPost Integration CLI",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  devpost-cli interrogate                    # List all projects
  devpost-cli interrogate --verbose          # Detailed project information
  devpost-cli interrogate --json             # JSON output
  devpost-cli status                         # Show project status
  devpost-cli status --project-id proj123    # Show specific project status
  devpost-cli create --title "My Project" --description "Description"
  devpost-cli update --project-id proj123 --title "New Title"
  devpost-cli delete --project-id proj123    # Delete project
            """
        )
        
        # Global options
        parser.add_argument(
            '--verbose', '-v',
            action='store_true',
            help='Enable verbose output'
        )
        
        parser.add_argument(
            '--json', '-j',
            action='store_true',
            help='Output in JSON format'
        )
        
        parser.add_argument(
            '--log-level',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
            default='INFO',
            help='Set logging level'
        )
        
        # Subcommands
        subparsers = parser.add_subparsers(
            dest='command',
            help='Available commands',
            required=True
        )
        
        # Interrogate command
        interrogate_parser = subparsers.add_parser(
            'interrogate',
            help='Interrogate and analyze projects'
        )
        interrogate_parser.add_argument(
            '--project-id',
            help='Specific project ID to interrogate'
        )
        
        # Status command
        status_parser = subparsers.add_parser(
            'status',
            help='Get project status information'
        )
        status_parser.add_argument(
            '--project-id',
            help='Specific project ID to check status'
        )
        
        # Create command
        create_parser = subparsers.add_parser(
            'create',
            help='Create a new project'
        )
        create_parser.add_argument(
            '--title',
            required=True,
            help='Project title'
        )
        create_parser.add_argument(
            '--description',
            required=True,
            help='Project description'
        )
        create_parser.add_argument(
            '--technologies',
            nargs='+',
            help='Project technologies'
        )
        create_parser.add_argument(
            '--tags',
            nargs='+',
            help='Project tags'
        )
        
        # Update command
        update_parser = subparsers.add_parser(
            'update',
            help='Update an existing project'
        )
        update_parser.add_argument(
            '--project-id',
            required=True,
            help='Project ID to update'
        )
        update_parser.add_argument(
            '--title',
            help='New project title'
        )
        update_parser.add_argument(
            '--description',
            help='New project description'
        )
        update_parser.add_argument(
            '--technologies',
            nargs='+',
            help='New project technologies'
        )
        update_parser.add_argument(
            '--tags',
            nargs='+',
            help='New project tags'
        )
        
        # Delete command
        delete_parser = subparsers.add_parser(
            'delete',
            help='Delete a project'
        )
        delete_parser.add_argument(
            '--project-id',
            required=True,
            help='Project ID to delete'
        )
        delete_parser.add_argument(
            '--force',
            action='store_true',
            help='Force deletion without confirmation'
        )
        
        return parser
    
    def parse_args(self, args: Optional[list] = None) -> Dict[str, Any]:
        """Parse command line arguments."""
        try:
            parsed_args = self.parser.parse_args(args)
            return self._validate_args(parsed_args)
        except SystemExit:
            # argparse calls sys.exit() on error
            raise ValueError("Invalid command line arguments")
        except Exception as e:
            logger.error(f"Error parsing arguments: {e}")
            raise ValueError(f"Error parsing arguments: {str(e)}")
    
    def _validate_args(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Validate parsed arguments."""
        from .cli_validation import CLIValidation
        
        validation = CLIValidation()
        
        # Convert argparse.Namespace to dict
        args_dict = vars(args)
        
        return validation.validate_args(args_dict)
    
    def get_help_text(self) -> str:
        """Get help text for the CLI."""
        return self.parser.format_help()
    
    def get_command_help(self, command: str) -> str:
        """Get help text for specific command."""
        try:
            # Find the subparser for the command
            for action in self.parser._subparsers._actions:
                if hasattr(action, 'choices') and command in action.choices:
                    return action.choices[command].format_help()
            return f"No help available for command: {command}"
        except Exception as e:
            logger.error(f"Error getting command help: {e}")
            return f"Error getting help for command {command}: {str(e)}"
    
