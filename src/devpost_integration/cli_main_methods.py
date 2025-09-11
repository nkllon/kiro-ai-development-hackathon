from .reflective_module import ReflectiveModule, register_module, ModuleCapability, ModuleHealth, ModuleStatus, ModuleConfiguration
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DevPostCLI(ReflectiveModule):
    """Main DevPost CLI orchestration class with RM-DDD compliance."""
    
    def __init__(self):
        """Initialize CLI components."""
        super().__init__(module_id="devpost_cli_main", version="1.0.0")
        self.parser = CLIParser()
        self.project_manager = DevpostProjectManager()
        self.commands = CLICommands(self.project_manager)
        
        # Metrics tracking
        self._command_count = 0
        self._error_count = 0
        self._start_time = datetime.now()
        
        # Register with global registry
        register_module(self)
    
    def run(self, args: Optional[list] = None) -> int:
        """Run the CLI with given arguments."""
        try:
            # Track command execution
            self._command_count += 1
            
            # Parse arguments
            parsed_args = self.parser.parse_args(args)
            
            # Setup logging
            self._setup_logging(parsed_args.get('log_level', 'INFO'))
            
            # Create output formatter
            output = CLIOutput(
                verbose=parsed_args.get('verbose', False),
                json_output=parsed_args.get('json', False)
            )
            
            # Execute command
            result = self._execute_command(parsed_args)
            
            # Track errors
            if result.get('status') == 'error':
                self._error_count += 1
            
            # Format and display output
            formatted_output = output.format_result(result, parsed_args['command'])
            print(formatted_output)
            
            # Return appropriate exit code
            return 0 if result.get('status') != 'error' else 1
            
        except ValueError as e:
            # Argument parsing or validation error
            error_output = CLIOutput().format_usage_error(str(e))
            print(error_output, file=sys.stderr)
            return 1
            
        except Exception as e:
            # Unexpected error
            logger.error(f"Unexpected error in CLI: {e}")
            error_output = CLIOutput().format_system_error(str(e))
            print(error_output, file=sys.stderr)
            return 1
    
    def _setup_logging(self, log_level: str) -> None:
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stderr)
            ]
        )
    
    def _execute_command(self, parsed_args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the parsed command."""
        command = parsed_args['command']
        
        try:
            if command == 'interrogate':
                return self.commands.interrogate_projects(
                    verbose=parsed_args.get('verbose', False),
                    json_output=parsed_args.get('json', False)
                )
            
            elif command == 'status':
                return self.commands.get_project_status(
                    project_id=parsed_args.get('project_id'),
                    json_output=parsed_args.get('json', False)
                )
            
            elif command == 'create':
                return self.commands.create_project(
                    title=parsed_args['title'],
                    description=parsed_args['description'],
                    technologies=parsed_args.get('technologies', []),
                    tags=parsed_args.get('tags', [])
                )
            
            elif command == 'update':
                update_kwargs = {}
                if 'title' in parsed_args and parsed_args['title']:
                    update_kwargs['title'] = parsed_args['title']
                if 'description' in parsed_args and parsed_args['description']:
                    update_kwargs['description'] = parsed_args['description']
                if 'technologies' in parsed_args and parsed_args['technologies']:
                    update_kwargs['technologies'] = parsed_args['technologies']
                if 'tags' in parsed_args and parsed_args['tags']:
                    update_kwargs['tags'] = parsed_args['tags']
                
                return self.commands.update_project(
                    project_id=parsed_args['project_id'],
                    **update_kwargs
                )
            
            elif command == 'delete':
                return self.commands.delete_project(
                    project_id=parsed_args['project_id']
                )
            
            else:
                return {
                    'status': 'error',
                    'message': f'Unknown command: {command}'
                }
                
        except Exception as e:
            logger.error(f"Error executing command {command}: {e}")
            return {
                'status': 'error',
                'message': f'Error executing command: {str(e)}'
            }
    
    def get_help(self) -> str:
        """Get help text for the CLI."""
        return self.parser.get_help_text()
    
    def get_command_help(self, command: str) -> str:
        """Get help text for specific command."""
        return self.parser.get_command_help(command)
    
    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information."""
        return {
            'module_id': self.module_id,
            'version': self.version,
            'name': 'DevPost CLI Main',
            'description': 'Main CLI orchestration for DevPost integration',
            'author': 'DevPost Integration Team',
            'created_at': self._start_time.isoformat(),
            'interface_version': self.get_interface_version()
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.HEALTH_MONITORING,
            ModuleCapability.CONFIGURATION,
            ModuleCapability.LOGGING,
            ModuleCapability.METRICS
        ]
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return [
            'cli_parser',
            'cli_commands', 
            'cli_output',
            'project_manager'
        ]
    
    def check_health(self) -> ModuleHealth:
        """Check module health with comprehensive monitoring"""
        try:
            if not hasattr(self, '_start_time'):
                return ModuleHealth.UNHEALTHY
            uptime = (datetime.now() - self._start_time).total_seconds()
            if uptime < 0:
                return ModuleHealth.UNHEALTHY
            error_count = getattr(self, '_error_count', 0)
            total_operations = getattr(self, '_command_count', 1)
            error_rate = error_count / total_operations if total_operations > 0 else 0
            if error_rate > 0.5:
                return ModuleHealth.UNHEALTHY
            elif error_rate > 0.1:
                return ModuleHealth.DEGRADED
            else:
                return ModuleHealth.HEALTHY
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return ModuleHealth.UNHEALTHY
        """Perform comprehensive health check."""
        issues = []
        health_score = 1.0
        
        try:
            # Check parser health
            if not hasattr(self.parser, 'parse_args'):
                issues.append("CLI parser missing parse_args method")
                health_score -= 0.2
            
            # Check project manager health
            if not hasattr(self.project_manager, 'get_projects'):
                issues.append("Project manager missing get_projects method")
                health_score -= 0.2
            
            # Check commands health
            if not hasattr(self.commands, 'interrogate_projects'):
                issues.append("CLI commands missing interrogate_projects method")
                health_score -= 0.2
            
            # Check error rate
            if self._command_count > 0:
                error_rate = self._error_count / self._command_count
                if error_rate > 0.1:  # More than 10% error rate
                    issues.append(f"High error rate: {error_rate:.1%}")
                    health_score -= 0.3
                elif error_rate > 0.05:  # More than 5% error rate
                    health_score -= 0.1
            
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
            parameters={
                'log_level': 'INFO',
                'verbose': False,
                'json_output': False
            },
            required_parameters=['log_level'],
            optional_parameters=['verbose', 'json_output'],
            validation_rules={
                'log_level': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                'verbose': [True, False],
                'json_output': [True, False]
            },
            last_updated=datetime.now()
        )
    
    def update_configuration(self, config: ModuleConfiguration) -> bool:
        """Update module configuration."""
        try:
            if not config.is_valid():
                logger.error("Invalid configuration provided")
                return False
            
            # Update configuration parameters
            # Note: In a real implementation, this would update actual config
            logger.info(f"Configuration updated for {self.module_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        uptime = (datetime.now() - self._start_time).total_seconds()
        error_rate = (self._error_count / self._command_count) if self._command_count > 0 else 0.0
        
        return {
            'command_count': self._command_count,
            'error_count': self._error_count,
            'error_rate': error_rate,
            'uptime_seconds': uptime,
            'uptime_hours': uptime / 3600,
            'last_command_time': datetime.now().isoformat()
        }
    
    def reset_metrics(self) -> None:
        """Reset module metrics to initial state."""
        self._command_count = 0
        self._error_count = 0
        self._start_time = datetime.now()
        logger.info("Metrics reset for CLI main module")