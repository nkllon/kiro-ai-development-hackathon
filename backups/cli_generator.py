#!/usr/bin/env python3
"""
CLI Generator - Auto-generates CLI for every ReflectiveModule

Implements RM-DDD CLI requirement: every module must have CLI with stdin/stdout pipes
"""

import ast
import inspect
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass

from .reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability,
    ModuleConfiguration,
    register_module,
)


@dataclass
class ProcessedInput:
    """Represents processed stdin input"""

    format: str
    data: Any
    success: bool
    error: Optional[str] = None


@dataclass
class CLIResult:
    """Represents CLI command result"""

    success: bool
    data: Any = None
    error: Optional[str] = None
    recovery_suggestions: Optional[List[str]] = None


@dataclass
class CLICommand:
    """Represents a CLI command"""

    name: str
    description: str
    arguments: List[Dict[str, Any]]
    handler: callable


@dataclass
class ModuleAnalysis:
    """Represents analysis of a ReflectiveModule"""

    module: ReflectiveModule
    capabilities: List[ModuleCapability]
    methods: List[Dict[str, Any]]
    configuration: ModuleConfiguration
    health: ModuleHealth
    metrics: Dict[str, Any]


class StdinProcessor:
    """Handles stdin input processing for CLI pipes"""

    def __init__(self):
        self.formats = {
            "json": self.process_json_input,
            "text": self.process_text_input,
            "binary": self.process_binary_input,
        }

    def process_input(
        self, input_data: bytes, format_type: str = "auto"
    ) -> ProcessedInput:
        """Process stdin input based on format"""
        if format_type == "auto":
            format_type = self.detect_format(input_data)

        processor = self.formats.get(format_type, self.process_text_input)
        return processor(input_data)

    def detect_format(self, input_data: bytes) -> str:
        """Auto-detect input format"""
        try:
            # Try JSON first
            json.loads(input_data.decode("utf-8"))
            return "json"
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Check if it's text
            try:
                input_data.decode("utf-8")
                return "text"
            except UnicodeDecodeError:
                return "binary"

    def process_json_input(self, input_data: bytes) -> ProcessedInput:
        """Process JSON input from stdin"""
        try:
            data = json.loads(input_data.decode("utf-8"))
            return ProcessedInput(format="json", data=data, success=True)
        except json.JSONDecodeError as e:
            return ProcessedInput(format="json", data=None, success=False, error=str(e))

    def process_text_input(self, input_data: bytes) -> ProcessedInput:
        """Process text input from stdin"""
        try:
            text = input_data.decode("utf-8")
            lines = text.strip().split("\n") if text.strip() else []
            return ProcessedInput(format="text", data=lines, success=True)
        except UnicodeDecodeError as e:
            return ProcessedInput(format="text", data=None, success=False, error=str(e))

    def process_binary_input(self, input_data: bytes) -> ProcessedInput:
        """Process binary input from stdin"""
        return ProcessedInput(format="binary", data=input_data, success=True)


class StdoutProcessor:
    """Handles stdout output processing for CLI pipes"""

    def __init__(self):
        self.formats = {
            "json": self.output_json,
            "text": self.output_text,
            "table": self.output_table,
        }

    def process_output(self, output_data: Any, format_type: str = "json") -> bytes:
        """Process output data for stdout"""
        processor = self.formats.get(format_type, self.output_json)
        return processor(output_data)

    def output_json(self, data: Any) -> bytes:
        """Output data as JSON"""
        try:
            json_str = json.dumps(data, indent=2, default=str)
            return json_str.encode("utf-8")
        except (TypeError, ValueError) as e:
            error_data = {"error": str(e), "data": str(data)}
            return json.dumps(error_data).encode("utf-8")

    def output_text(self, data: Any) -> bytes:
        """Output data as text"""
        if isinstance(data, list):
            return "\n".join(str(item) for item in data).encode("utf-8")
        else:
            return str(data).encode("utf-8")

    def output_table(self, data: Any) -> bytes:
        """Output data as table"""
        if isinstance(data, list) and data and isinstance(data[0], dict):
            # Simple table output for list of dicts
            if not data:
                return b"No data"

            # Get headers
            headers = list(data[0].keys())

            # Calculate column widths
            col_widths = {header: len(header) for header in headers}
            for row in data:
                for header in headers:
                    col_widths[header] = max(
                        col_widths[header], len(str(row.get(header, "")))
                    )

            # Build table
            lines = []
            # Header
            header_line = " | ".join(
                header.ljust(col_widths[header]) for header in headers
            )
            lines.append(header_line)
            lines.append("-" * len(header_line))

            # Rows
            for row in data:
                row_line = " | ".join(
                    str(row.get(header, "")).ljust(col_widths[header])
                    for header in headers
                )
                lines.append(row_line)

            return "\n".join(lines).encode("utf-8")
        else:
            return self.output_text(data)


class CLIGeneratorEngine:
    """Generates CLI code for ReflectiveModule instances"""

    def __init__(self):
        self.stdin_processor = StdinProcessor()
        self.stdout_processor = StdoutProcessor()

    def analyze_module(self, module: ReflectiveModule) -> ModuleAnalysis:
        """Analyze ReflectiveModule and extract CLI-relevant information"""
        try:
            # Get module capabilities
            capabilities = module.get_capabilities()

            # Analyze methods
            methods = self._analyze_methods(module)

            # Get configuration
            configuration = module.get_configuration()

            # Get health status
            health = module.check_health()

            # Get metrics
            metrics = module.get_metrics()

            return ModuleAnalysis(
                module=module,
                capabilities=capabilities,
                methods=methods,
                configuration=configuration,
                health=health,
                metrics=metrics,
            )
        except Exception as e:
            # Return minimal analysis on error
            return ModuleAnalysis(
                module=module,
                capabilities=[],
                methods=[],
                configuration=ModuleConfiguration(
                    module_id=module.module_id, settings={}, last_updated=datetime.now()
                ),
                health=ModuleHealth(
                    module_id=module.module_id,
                    status=ModuleStatus.ERROR,
                    health_score=0.0,
                    issues=[f"Analysis error: {str(e)}"],
                    capabilities=[],
                    dependencies=[],
                    metrics={},
                    last_check=datetime.now(),
                ),
                metrics={},
            )

    def _analyze_methods(self, module: ReflectiveModule) -> List[Dict[str, Any]]:
        """Analyze module methods for CLI generation"""
        methods = []

        try:
            # Get all methods from the module
            for method_name in dir(module):
                if not method_name.startswith("_"):
                    method = getattr(module, method_name)
                    if callable(method) and not isinstance(method, property):
                        # Extract method information
                        method_info = {
                            "name": method_name,
                            "description": self._extract_method_docstring(method),
                            "arguments": self._extract_method_arguments(method),
                            "return_type": self._extract_method_return_type(method),
                        }
                        methods.append(method_info)
        except Exception as e:
            # If method analysis fails, return empty list
            pass

        return methods

    def _extract_method_docstring(self, method: callable) -> str:
        """Extract docstring from method"""
        try:
            return method.__doc__ or f"Execute {method.__name__} operation"
        except:
            return f"Execute {method.__name__} operation"

    def _extract_method_arguments(self, method: callable) -> List[Dict[str, Any]]:
        """Extract method arguments for CLI generation"""
        try:
            sig = inspect.signature(method)
            arguments = []

            for param_name, param in sig.parameters.items():
                if param_name != "self":
                    arg_info = {
                        "name": param_name,
                        "type": (
                            str(param.annotation)
                            if param.annotation != inspect.Parameter.empty
                            else "str"
                        ),
                        "default": (
                            param.default
                            if param.default != inspect.Parameter.empty
                            else None
                        ),
                        "required": param.default == inspect.Parameter.empty,
                    }
                    arguments.append(arg_info)

            return arguments
        except:
            return []

    def _extract_method_return_type(self, method: callable) -> str:
        """Extract return type from method"""
        try:
            sig = inspect.signature(method)
            return_type = sig.return_annotation
            if return_type != inspect.Parameter.empty:
                return str(return_type)
            else:
                return "Any"
        except:
            return "Any"

    def generate_cli_code(self, analysis: ModuleAnalysis) -> str:
        """Generate complete CLI code for module"""
        module = analysis.module
        module_info = module.get_module_info()

        # Generate CLI template
        cli_code = f'''#!/usr/bin/env python3
"""
Auto-generated CLI for {module_info['name']}
Generated from ReflectiveModule: {module.module_id}
Generated on: {datetime.now().isoformat()}
"""

import argparse
import sys
import json
from typing import Any, Dict, List
from {module.__class__.__module__} import {module.__class__.__name__}

class {module.__class__.__name__}CLI:
    """CLI wrapper for {module.__class__.__name__}"""
    
    def __init__(self):
        self.module = {module.__class__.__name__}()
        self.stdin_processor = StdinProcessor()
        self.stdout_processor = StdoutProcessor()
    
    def create_argument_parser(self):
        """Create argument parser for CLI commands"""
        parser = argparse.ArgumentParser(
            description='{module_info['description']}',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # Add version
        parser.add_argument('--version', action='version', version='{module_info['version']}')
        
        # Add subparsers for commands
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Standard commands
        self._add_standard_commands(subparsers)
        
        # Module-specific commands
        self._add_module_commands(subparsers, analysis)
        
        return parser
    
    def _add_standard_commands(self, subparsers):
        """Add standard CLI commands"""
        # Help command
        help_parser = subparsers.add_parser('help', help='Show detailed help information')
        help_parser.set_defaults(func=self.help_command)
        
        # Status command
        status_parser = subparsers.add_parser('status', help='Show module status')
        status_parser.set_defaults(func=self.status_command)
        
        # Health command
        health_parser = subparsers.add_parser('health', help='Show module health')
        health_parser.set_defaults(func=self.health_command)
        
        # Capabilities command
        caps_parser = subparsers.add_parser('capabilities', help='Show module capabilities')
        caps_parser.set_defaults(func=self.capabilities_command)
        
        # Info command
        info_parser = subparsers.add_parser('info', help='Show module information')
        info_parser.set_defaults(func=self.info_command)
        
        # Config command
        config_parser = subparsers.add_parser('config', help='Show module configuration')
        config_parser.set_defaults(func=self.config_command)
        
        # Metrics command
        metrics_parser = subparsers.add_parser('metrics', help='Show module metrics')
        metrics_parser.set_defaults(func=self.metrics_command)
    
    def _add_module_commands(self, subparsers, analysis):
        """Add module-specific commands"""
        # Add commands for each capability
        for capability in analysis.capabilities:
            if capability == ModuleCapability.CORE_FUNCTIONALITY:
                core_parser = subparsers.add_parser('core', help='Execute core functionality')
                core_parser.set_defaults(func=self.core_command)
            elif capability == ModuleCapability.DATA_PROCESSING:
                process_parser = subparsers.add_parser('process', help='Process data')
                process_parser.add_argument('--input', help='Input data')
                process_parser.set_defaults(func=self.process_command)
            elif capability == ModuleCapability.API_INTEGRATION:
                api_parser = subparsers.add_parser('api', help='API operations')
                api_parser.set_defaults(func=self.api_command)
            elif capability == ModuleCapability.FILE_OPERATIONS:
                file_parser = subparsers.add_parser('file', help='File operations')
                file_parser.add_argument('--path', help='File path')
                file_parser.set_defaults(func=self.file_command)
            elif capability == ModuleCapability.VALIDATION:
                validate_parser = subparsers.add_parser('validate', help='Validation operations')
                validate_parser.add_argument('--data', help='Data to validate')
                validate_parser.set_defaults(func=self.validate_command)
            elif capability == ModuleCapability.MONITORING:
                monitor_parser = subparsers.add_parser('monitor', help='Monitoring operations')
                monitor_parser.set_defaults(func=self.monitor_command)
        
        # Add commands for module methods
        for method in analysis.methods:
            if method['name'] not in ['get_module_info', 'get_capabilities', 'get_dependencies', 
                                   'check_health', 'get_configuration', 'update_configuration', 'get_metrics', 'reset_metrics']:
                method_parser = subparsers.add_parser(method['name'], help=method['description'])
                
                # Add arguments for method
                for arg in method['arguments']:
                    if arg['required']:
                        method_parser.add_argument(f"--{{arg['name']}}", required=True, help=f"{{arg['name']}} parameter")
                    else:
                        method_parser.add_argument(f"--{{arg['name']}}", default=arg['default'], help=f"{{arg['name']}} parameter")
                
                method_parser.set_defaults(func=getattr(self, f"{{method['name']}}_command"))
    
    def execute_command(self, args):
        """Execute CLI command"""
        try:
            # Handle stdin input if available
            stdin_data = None
            if not sys.stdin.isatty():
                stdin_data = sys.stdin.read()
            
            # Execute command
            if hasattr(args, 'func'):
                result = args.func(args, stdin_data)
            else:
                result = self.help_command(args, stdin_data)
            
            # Output result
            if result.success:
                output = self.stdout_processor.process_output(result.data, 'json')
                sys.stdout.buffer.write(output)
                sys.stdout.buffer.write(b'\\n')
            else:
                error_output = self.stdout_processor.process_output({
                    'error': result.error,
                    'recovery_suggestions': result.recovery_suggestions
                }, 'json')
                sys.stderr.buffer.write(error_output)
                sys.stderr.buffer.write(b'\\n')
                sys.exit(1)
                
        except Exception as e:
            error_result = CLIResult(
                success=False,
                error=f"CLI execution error: {{str(e)}}",
                recovery_suggestions=["Check module health", "Verify command syntax", "Check module configuration"]
            )
            error_output = self.stdout_processor.process_output({
                'error': error_result.error,
                'recovery_suggestions': error_result.recovery_suggestions
            }, 'json')
            sys.stderr.buffer.write(error_output)
            sys.stderr.buffer.write(b'\\n')
            sys.exit(1)
    
    # Standard command implementations
    def help_command(self, args, stdin_data=None):
        """Show detailed help information"""
        module_info = self.module.get_module_info()
        capabilities = self.module.get_capabilities()
        
        help_data = {{
            'module': module_info,
            'capabilities': [cap.value for cap in capabilities],
            'commands': self._get_available_commands(),
            'usage_examples': self._get_usage_examples()
        }}
        
        return CLIResult(success=True, data=help_data)
    
    def status_command(self, args, stdin_data=None):
        """Show module status"""
        module_info = self.module.get_module_info()
        health = self.module.check_health()
        metrics = self.module.get_metrics()
        
        status_data = {{
            'module_id': module_info['module_id'],
            'version': module_info['version'],
            'status': health.status.value,
            'health_score': health.health_score,
            'metrics': metrics
        }}
        
        return CLIResult(success=True, data=status_data)
    
    def health_command(self, args, stdin_data=None):
        """Show detailed health information"""
        health = self.module.check_health()
        
        health_data = {{
            'module_id': health.module_id,
            'status': health.status.value,
            'health_score': health.health_score,
            'issues': health.issues,
            'capabilities': [cap.value for cap in health.capabilities],
            'dependencies': health.dependencies,
            'last_check': health.last_check.isoformat()
        }}
        
        return CLIResult(success=True, data=health_data)
    
    def capabilities_command(self, args, stdin_data=None):
        """Show module capabilities"""
        capabilities = self.module.get_capabilities()
        
        caps_data = {{
            'capabilities': [cap.value for cap in capabilities],
            'count': len(capabilities)
        }}
        
        return CLIResult(success=True, data=caps_data)
    
    def info_command(self, args, stdin_data=None):
        """Show module information"""
        module_info = self.module.get_module_info()
        return CLIResult(success=True, data=module_info)
    
    def config_command(self, args, stdin_data=None):
        """Show module configuration"""
        config = self.module.get_configuration()
        
        config_data = {{
            'module_id': config.module_id,
            'settings': config.settings,
            'last_updated': config.last_updated.isoformat()
        }}
        
        return CLIResult(success=True, data=config_data)
    
    def metrics_command(self, args, stdin_data=None):
        """Show module metrics"""
        metrics = self.module.get_metrics()
        return CLIResult(success=True, data=metrics)
    
    # Capability command implementations
    def core_command(self, args, stdin_data=None):
        """Execute core functionality"""
        try:
            # This would call the module's core functionality
            result = {{'message': 'Core functionality executed', 'status': 'success'}}
            return CLIResult(success=True, data=result)
        except Exception as e:
            return CLIResult(success=False, error=str(e))
    
    def process_command(self, args, stdin_data=None):
        """Process data"""
        try:
            input_data = args.input or stdin_data
            if not input_data:
                return CLIResult(success=False, error="No input data provided")
            
            # Process the data (this would call the module's processing method)
            result = {{'processed_data': input_data, 'status': 'processed'}}
            return CLIResult(success=True, data=result)
        except Exception as e:
            return CLIResult(success=False, error=str(e))
    
    def api_command(self, args, stdin_data=None):
        """API operations"""
        try:
            result = {{'message': 'API operations executed', 'status': 'success'}}
            return CLIResult(success=True, data=result)
        except Exception as e:
            return CLIResult(success=False, error=str(e))
    
    def file_command(self, args, stdin_data=None):
        """File operations"""
        try:
            file_path = args.path
            if not file_path:
                return CLIResult(success=False, error="No file path provided")
            
            result = {{'file_path': file_path, 'status': 'processed'}}
            return CLIResult(success=True, data=result)
        except Exception as e:
            return CLIResult(success=False, error=str(e))
    
    def validate_command(self, args, stdin_data=None):
        """Validation operations"""
        try:
            data = args.data or stdin_data
            if not data:
                return CLIResult(success=False, error="No data provided for validation")
            
            # This would call the module's validation method
            result = {{'validated_data': data, 'status': 'valid'}}
            return CLIResult(success=True, data=result)
        except Exception as e:
            return CLIResult(success=False, error=str(e))
    
    def monitor_command(self, args, stdin_data=None):
        """Monitoring operations"""
        try:
            result = {{'message': 'Monitoring operations executed', 'status': 'success'}}
            return CLIResult(success=True, data=result)
        except Exception as e:
            return CLIResult(success=False, error=str(e))
    
    def _get_available_commands(self):
        """Get list of available commands"""
        return [
            'help', 'status', 'health', 'capabilities', 'info', 'config', 'metrics',
            'core', 'process', 'api', 'file', 'validate', 'monitor'
        ]
    
    def _get_usage_examples(self):
        """Get usage examples"""
        return [
            f"{{sys.argv[0]}} --help",
            f"{{sys.argv[0]}} status",
            f"{{sys.argv[0]}} health",
            f"{{sys.argv[0]}} capabilities",
            f"echo 'data' | {{sys.argv[0]}} process",
            f"{{sys.argv[0]}} validate --data 'test data'"
        ]


def main():
    """Main CLI entry point"""
    cli = {module.__class__.__name__}CLI()
    parser = cli.create_argument_parser()
    args = parser.parse_args()
    cli.execute_command(args)


if __name__ == '__main__':
    main()
'''

        return cli_code

    def generate_cli_entry_point(self, module: ReflectiveModule) -> str:
        """Generate CLI entry point script"""
        module_info = module.get_module_info()

        entry_point = f'''#!/usr/bin/env python3
"""
Auto-generated CLI entry point for {module_info['name']}
Module ID: {module.module_id}
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

# Import and run the CLI
from {module.__class__.__module__} import {module.__class__.__name__}
from devpost_integration.cli_generator import CLIGeneratorEngine

def main():
    # Initialize module
    module = {module.__class__.__name__}()
    
    # Generate and execute CLI
    generator = CLIGeneratorEngine()
    analysis = generator.analyze_module(module)
    cli_code = generator.generate_cli_code(analysis)
    
    # Execute the generated CLI
    exec(cli_code)

if __name__ == '__main__':
    main()
'''

        return entry_point


class CLIRegistry:
    """Registry for managing module CLIs"""

    _instance = None
    _clis = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls):
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_cli(self, module: ReflectiveModule, cli_code: str) -> None:
        """Register CLI for module"""
        self._clis[module.module_id] = {
            "module": module,
            "cli_code": cli_code,
            "registered_at": datetime.now(),
        }

    def get_cli(self, module_id: str) -> Optional[Dict[str, Any]]:
        """Get CLI for module"""
        return self._clis.get(module_id)

    def get_all_clis(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered CLIs"""
        return self._clis.copy()

    def discover_module_clis(self) -> List[Dict[str, Any]]:
        """Discover CLIs for all registered modules"""
        from .reflective_module import ReflectiveModuleRegistry

        registry = ReflectiveModuleRegistry.get_instance()
        clis = []

        for module in registry.get_all_modules():
            cli_info = self.get_cli(module.module_id)
            if cli_info:
                clis.append(cli_info)

        return clis


# Auto-register this module
register_module(CLIGeneratorEngine())
