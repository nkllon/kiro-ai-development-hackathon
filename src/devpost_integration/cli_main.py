#!/usr/bin/env python3
"""
CLI Main - Main CLI orchestration

Extracted from cli.py for RM-DDD compliance.
Single responsibility: Main CLI orchestration and coordination.
"""

import logging
import sys
from typing import Dict, Any, Optional

from .cli_parser import CLIParser
from .cli_commands import CLICommands
from .cli_output import CLIOutput
from .project_manager import DevpostProjectManager

logger = logging.getLogger(__name__)


class DevPostCLI:
    """Main DevPost CLI orchestration class."""
    
    def __init__(self):
        """Initialize CLI components."""
        self.parser = CLIParser()
        self.project_manager = DevpostProjectManager()
        self.commands = CLICommands(self.project_manager)
    
    def run(self, args: Optional[list] = None) -> int:
        """Run the CLI with given arguments."""
        try:
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


def main() -> int:
    """Main CLI entry point."""
    cli = DevPostCLI()
    return cli.run()


if __name__ == '__main__':
    sys.exit(main())
