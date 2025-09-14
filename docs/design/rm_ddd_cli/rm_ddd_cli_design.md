# RM-DDD CLI Design

## Document Information
- **Version:** 1.0
- **Date:** 2024-12-19
- **Status:** Draft
- **Author:** AI Development Team
- **Reviewer:** TBD

## 1. Overview

### 1.1 Purpose
This document defines the design for the RM-DDD CLI generation system, which automatically generates command-line interfaces for every ReflectiveModule with stdin/stdout pipe support.

### 1.2 Architecture Overview
The RM-DDD CLI system consists of:
- **CLI Generator Engine**: Analyzes ReflectiveModule and generates CLI code
- **CLI Template System**: Provides templates for different CLI patterns
- **Pipe Handler System**: Manages stdin/stdout pipe processing
- **CLI Registry**: Manages and orchestrates all module CLIs
- **CLI Runtime**: Executes and manages CLI instances

### 1.3 Design Principles
- **Auto-Generation**: CLI generated automatically from module models
- **Standardization**: Consistent CLI interface across all modules
- **Pipe-First**: Stdin/stdout pipes as primary data exchange mechanism
- **Introspection**: CLI reflects module capabilities and state
- **Composability**: CLIs can be chained and orchestrated

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    RM-DDD CLI System                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  CLI Generator  │  │  CLI Registry   │  │ CLI Runtime  │ │
│  │     Engine      │  │                 │  │              │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│           │                     │                   │        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ CLI Template    │  │  Pipe Handler   │  │ CLI Monitor  │ │
│  │    System       │  │     System      │  │              │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
           │                     │                   │
    ┌─────────────┐      ┌─────────────┐    ┌─────────────┐
    │ Reflective  │      │   Stdin/    │    │   Module    │
    │   Module    │      │   Stdout    │    │  Registry   │
    │             │      │   Pipes     │    │             │
    └─────────────┘      └─────────────┘    └─────────────┘
```

### 2.2 Component Design

#### 2.2.1 CLI Generator Engine
**Purpose**: Analyzes ReflectiveModule and generates CLI code

**Key Components**:
- **Module Analyzer**: Extracts module capabilities, methods, and configuration
- **Command Generator**: Creates CLI commands from module methods
- **Argument Parser Generator**: Generates argument parsers for commands
- **Help Generator**: Creates help text and documentation
- **Code Generator**: Generates Python CLI code

**Interface**:
```python
class CLIGeneratorEngine:
    def analyze_module(self, module: ReflectiveModule) -> ModuleAnalysis
    def generate_cli_code(self, analysis: ModuleAnalysis) -> str
    def generate_commands(self, module: ReflectiveModule) -> List[CLICommand]
    def generate_help(self, module: ReflectiveModule) -> str
    def generate_entry_point(self, module: ReflectiveModule) -> str
```

#### 2.2.2 CLI Template System
**Purpose**: Provides templates for different CLI patterns

**Key Components**:
- **Base CLI Template**: Standard CLI structure
- **Module CLI Template**: Module-specific CLI patterns
- **Command Template**: Individual command templates
- **Help Template**: Help text templates
- **Error Template**: Error handling templates

**Template Structure**:
```python
class CLITemplate:
    def __init__(self, template_type: str, module: ReflectiveModule):
        self.template_type = template_type
        self.module = module
    
    def render(self) -> str:
        """Render template with module data"""
        pass
    
    def get_commands(self) -> List[CommandTemplate]:
        """Get command templates for module"""
        pass
    
    def get_help(self) -> str:
        """Get help template for module"""
        pass
```

#### 2.2.3 Pipe Handler System
**Purpose**: Manages stdin/stdout pipe processing

**Key Components**:
- **Input Processor**: Handles stdin input processing
- **Output Processor**: Handles stdout output processing
- **Error Handler**: Handles stderr output processing
- **Format Handler**: Manages different input/output formats
- **Pipe State Manager**: Maintains pipe state and context

**Interface**:
```python
class PipeHandler:
    def process_stdin(self, input_data: bytes) -> ProcessedInput
    def process_stdout(self, output_data: Any) -> bytes
    def process_stderr(self, error_data: Any) -> bytes
    def handle_pipe_error(self, error: Exception) -> None
    def get_pipe_state(self) -> PipeState
```

#### 2.2.4 CLI Registry
**Purpose**: Manages and orchestrates all module CLIs

**Key Components**:
- **CLI Discovery**: Discovers available module CLIs
- **CLI Registration**: Registers module CLIs
- **CLI Orchestration**: Manages CLI chaining and composition
- **CLI Monitoring**: Monitors CLI health and performance
- **CLI Management**: Manages CLI lifecycle

**Interface**:
```python
class CLIRegistry:
    def register_cli(self, module: ReflectiveModule, cli: ModuleCLI) -> None
    def discover_clis(self) -> List[ModuleCLI]
    def get_cli(self, module_id: str) -> ModuleCLI
    def orchestrate_clis(self, commands: List[CLICommand]) -> CLIResult
    def monitor_clis(self) -> Dict[str, CLIHealth]
```

#### 2.2.5 CLI Runtime
**Purpose**: Executes and manages CLI instances

**Key Components**:
- **CLI Executor**: Executes CLI commands
- **Command Router**: Routes commands to appropriate handlers
- **State Manager**: Manages CLI state and context
- **Error Handler**: Handles CLI errors and exceptions
- **Performance Monitor**: Monitors CLI performance

**Interface**:
```python
class CLIRuntime:
    def execute_command(self, command: str, args: List[str]) -> CLIResult
    def route_command(self, command: str) -> CommandHandler
    def manage_state(self, state: CLIState) -> None
    def handle_error(self, error: Exception) -> None
    def monitor_performance(self) -> PerformanceMetrics
```

## 3. CLI Generation Process

### 3.1 Module Analysis Phase

#### 3.1.1 Capability Analysis
```python
def analyze_capabilities(module: ReflectiveModule) -> List[CLICapability]:
    """Analyze module capabilities and generate CLI capabilities"""
    capabilities = module.get_capabilities()
    cli_capabilities = []
    
    for capability in capabilities:
        cli_cap = CLICapability(
            name=capability.value,
            description=f"Execute {capability.value} operations",
            commands=generate_capability_commands(capability),
            arguments=generate_capability_arguments(capability)
        )
        cli_capabilities.append(cli_cap)
    
    return cli_capabilities
```

#### 3.1.2 Method Analysis
```python
def analyze_methods(module: ReflectiveModule) -> List[CLIMethod]:
    """Analyze module methods and generate CLI methods"""
    methods = inspect.getmembers(module, predicate=inspect.ismethod)
    cli_methods = []
    
    for method_name, method in methods:
        if not method_name.startswith('_'):
            cli_method = CLIMethod(
                name=method_name,
                description=extract_method_docstring(method),
                arguments=extract_method_arguments(method),
                return_type=extract_method_return_type(method),
                handler=create_method_handler(method)
            )
            cli_methods.append(cli_method)
    
    return cli_methods
```

#### 3.1.3 Configuration Analysis
```python
def analyze_configuration(module: ReflectiveModule) -> CLIConfiguration:
    """Analyze module configuration and generate CLI configuration"""
    config = module.get_configuration()
    
    cli_config = CLIConfiguration(
        module_id=config.module_id,
        settings=config.settings,
        commands=generate_config_commands(config),
        arguments=generate_config_arguments(config)
    )
    
    return cli_config
```

### 3.2 CLI Code Generation Phase

#### 3.2.1 Command Generation
```python
def generate_commands(analysis: ModuleAnalysis) -> List[CLICommand]:
    """Generate CLI commands from module analysis"""
    commands = []
    
    # Standard commands
    commands.extend(generate_standard_commands())
    
    # Module-specific commands
    commands.extend(generate_module_commands(analysis.methods))
    
    # Capability commands
    commands.extend(generate_capability_commands(analysis.capabilities))
    
    # Configuration commands
    commands.extend(generate_configuration_commands(analysis.configuration))
    
    return commands
```

#### 3.2.2 Argument Parser Generation
```python
def generate_argument_parser(commands: List[CLICommand]) -> str:
    """Generate argument parser code for CLI commands"""
    parser_code = """
import argparse
import sys
import json
from typing import Any, Dict, List

def create_argument_parser():
    parser = argparse.ArgumentParser(description='{module_description}')
    
    # Add subparsers for commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    {command_parsers}
    
    return parser
"""
    
    command_parsers = []
    for command in commands:
        command_parser = generate_command_parser(command)
        command_parsers.append(command_parser)
    
    return parser_code.format(
        module_description=analysis.module.get_module_info()['description'],
        command_parsers='\n'.join(command_parsers)
    )
```

#### 3.2.3 CLI Entry Point Generation
```python
def generate_cli_entry_point(module: ReflectiveModule) -> str:
    """Generate CLI entry point for module"""
    entry_point = """
#!/usr/bin/env python3
\"\"\"
Auto-generated CLI for {module_name}
Generated from ReflectiveModule: {module_id}
\"\"\"

import sys
import json
from {module_path} import {module_class}

def main():
    # Initialize module
    module = {module_class}()
    
    # Create argument parser
    parser = create_argument_parser()
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle stdin input
    if not sys.stdin.isatty():
        stdin_data = sys.stdin.read()
        args.stdin_data = stdin_data
    
    # Execute command
    result = execute_command(module, args)
    
    # Output result
    if result.success:
        print(json.dumps(result.data, indent=2))
    else:
        print(f"Error: {{result.error}}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
"""
    
    return entry_point.format(
        module_name=module.get_module_info()['name'],
        module_id=module.module_id,
        module_path=module.__class__.__module__,
        module_class=module.__class__.__name__
    )
```

### 3.3 Pipe Processing Implementation

#### 3.3.1 Stdin Processing
```python
class StdinProcessor:
    def __init__(self):
        self.formats = {
            'json': self.process_json_input,
            'text': self.process_text_input,
            'binary': self.process_binary_input
        }
    
    def process_input(self, input_data: bytes, format_type: str = 'auto') -> ProcessedInput:
        """Process stdin input based on format"""
        if format_type == 'auto':
            format_type = self.detect_format(input_data)
        
        processor = self.formats.get(format_type, self.process_text_input)
        return processor(input_data)
    
    def process_json_input(self, input_data: bytes) -> ProcessedInput:
        """Process JSON input from stdin"""
        try:
            data = json.loads(input_data.decode('utf-8'))
            return ProcessedInput(
                format='json',
                data=data,
                success=True
            )
        except json.JSONDecodeError as e:
            return ProcessedInput(
                format='json',
                data=None,
                success=False,
                error=str(e)
            )
    
    def process_text_input(self, input_data: bytes) -> ProcessedInput:
        """Process text input from stdin"""
        try:
            text = input_data.decode('utf-8')
            lines = text.strip().split('\n')
            return ProcessedInput(
                format='text',
                data=lines,
                success=True
            )
        except UnicodeDecodeError as e:
            return ProcessedInput(
                format='text',
                data=None,
                success=False,
                error=str(e)
            )
```

#### 3.3.2 Stdout Processing
```python
class StdoutProcessor:
    def __init__(self):
        self.formats = {
            'json': self.output_json,
            'text': self.output_text,
            'table': self.output_table
        }
    
    def process_output(self, output_data: Any, format_type: str = 'json') -> bytes:
        """Process output data for stdout"""
        processor = self.formats.get(format_type, self.output_json)
        return processor(output_data)
    
    def output_json(self, data: Any) -> bytes:
        """Output data as JSON"""
        try:
            json_str = json.dumps(data, indent=2, default=str)
            return json_str.encode('utf-8')
        except (TypeError, ValueError) as e:
            error_data = {'error': str(e), 'data': str(data)}
            return json.dumps(error_data).encode('utf-8')
    
    def output_text(self, data: Any) -> bytes:
        """Output data as text"""
        if isinstance(data, list):
            return '\n'.join(str(item) for item in data).encode('utf-8')
        else:
            return str(data).encode('utf-8')
```

## 4. CLI Command Structure

### 4.1 Standard Commands

#### 4.1.1 Help Command
```python
def help_command(module: ReflectiveModule, args: argparse.Namespace) -> CLIResult:
    """Generate help information for module"""
    info = module.get_module_info()
    capabilities = module.get_capabilities()
    
    help_data = {
        'module': info,
        'capabilities': [cap.value for cap in capabilities],
        'commands': get_available_commands(module),
        'usage': get_usage_examples(module)
    }
    
    return CLIResult(success=True, data=help_data)
```

#### 4.1.2 Status Command
```python
def status_command(module: ReflectiveModule, args: argparse.Namespace) -> CLIResult:
    """Get module status information"""
    info = module.get_module_info()
    health = module.check_health()
    metrics = module.get_metrics()
    
    status_data = {
        'module_id': info['module_id'],
        'version': info['version'],
        'status': health.status.value,
        'health_score': health.health_score,
        'metrics': metrics
    }
    
    return CLIResult(success=True, data=status_data)
```

#### 4.1.3 Health Command
```python
def health_command(module: ReflectiveModule, args: argparse.Namespace) -> CLIResult:
    """Get detailed health information"""
    health = module.check_health()
    
    health_data = {
        'module_id': health.module_id,
        'status': health.status.value,
        'health_score': health.health_score,
        'issues': health.issues,
        'capabilities': [cap.value for cap in health.capabilities],
        'dependencies': health.dependencies,
        'last_check': health.last_check.isoformat()
    }
    
    return CLIResult(success=True, data=health_data)
```

### 4.2 Module-Specific Commands

#### 4.2.1 Capability Commands
```python
def generate_capability_commands(capabilities: List[ModuleCapability]) -> List[CLICommand]:
    """Generate commands for each module capability"""
    commands = []
    
    for capability in capabilities:
        if capability == ModuleCapability.CORE_FUNCTIONALITY:
            commands.append(CLICommand(
                name='core',
                description='Execute core functionality operations',
                handler=core_functionality_handler
            ))
        elif capability == ModuleCapability.DATA_PROCESSING:
            commands.append(CLICommand(
                name='process',
                description='Process data using module capabilities',
                handler=data_processing_handler
            ))
        # ... other capabilities
    
    return commands
```

#### 4.2.2 Method Commands
```python
def generate_method_commands(methods: List[CLIMethod]) -> List[CLICommand]:
    """Generate commands for module methods"""
    commands = []
    
    for method in methods:
        command = CLICommand(
            name=method.name,
            description=method.description,
            arguments=method.arguments,
            handler=method.handler
        )
        commands.append(command)
    
    return commands
```

## 5. CLI Integration

### 5.1 Module Integration

#### 5.1.1 Auto-Generation Integration
```python
class ReflectiveModuleCLI:
    """Mixin class for ReflectiveModule CLI integration"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cli_generator = CLIGeneratorEngine()
        self._cli_code = None
        self._cli_commands = None
    
    def generate_cli(self) -> str:
        """Generate CLI code for this module"""
        if self._cli_code is None:
            analysis = self._cli_generator.analyze_module(self)
            self._cli_code = self._cli_generator.generate_cli_code(analysis)
        return self._cli_code
    
    def get_cli_commands(self) -> List[CLICommand]:
        """Get CLI commands for this module"""
        if self._cli_commands is None:
            analysis = self._cli_generator.analyze_module(self)
            self._cli_commands = self._cli_generator.generate_commands(analysis)
        return self._cli_commands
```

#### 5.1.2 CLI Registration
```python
def register_module_cli(module: ReflectiveModule) -> None:
    """Register module CLI with the registry"""
    cli_registry = CLIRegistry.get_instance()
    
    # Generate CLI for module
    cli_generator = CLIGeneratorEngine()
    analysis = cli_generator.analyze_module(module)
    cli_code = cli_generator.generate_cli_code(analysis)
    
    # Create CLI instance
    cli = ModuleCLI(module, cli_code)
    
    # Register with registry
    cli_registry.register_cli(module, cli)
```

### 5.2 Registry Integration

#### 5.2.1 CLI Discovery
```python
def discover_module_clis() -> List[ModuleCLI]:
    """Discover all available module CLIs"""
    cli_registry = CLIRegistry.get_instance()
    module_registry = ReflectiveModuleRegistry.get_instance()
    
    clis = []
    for module in module_registry.get_all_modules():
        cli = cli_registry.get_cli(module.module_id)
        if cli:
            clis.append(cli)
    
    return clis
```

#### 5.2.2 CLI Orchestration
```python
def orchestrate_cli_commands(commands: List[CLICommand]) -> CLIResult:
    """Orchestrate multiple CLI commands"""
    cli_registry = CLIRegistry.get_instance()
    results = []
    
    for command in commands:
        # Find appropriate CLI for command
        cli = cli_registry.find_cli_for_command(command)
        if cli:
            result = cli.execute_command(command)
            results.append(result)
        else:
            results.append(CLIResult(
                success=False,
                error=f"No CLI found for command: {command.name}"
            ))
    
    return CLIResult(
        success=all(r.success for r in results),
        data=results
    )
```

## 6. Error Handling and Recovery

### 6.1 CLI Error Handling
```python
class CLIErrorHandler:
    def __init__(self):
        self.error_handlers = {
            'ModuleError': self.handle_module_error,
            'ValidationError': self.handle_validation_error,
            'PipeError': self.handle_pipe_error,
            'CommandError': self.handle_command_error
        }
    
    def handle_error(self, error: Exception, context: CLIContext) -> CLIResult:
        """Handle CLI errors with appropriate recovery"""
        error_type = type(error).__name__
        handler = self.error_handlers.get(error_type, self.handle_generic_error)
        return handler(error, context)
    
    def handle_module_error(self, error: Exception, context: CLIContext) -> CLIResult:
        """Handle module-specific errors"""
        return CLIResult(
            success=False,
            error=f"Module error: {str(error)}",
            recovery_suggestions=[
                "Check module health status",
                "Verify module configuration",
                "Restart module if necessary"
            ]
        )
```

### 6.2 Pipe Error Recovery
```python
class PipeErrorRecovery:
    def __init__(self):
        self.recovery_strategies = {
            'json_parse_error': self.recover_json_error,
            'unicode_error': self.recover_unicode_error,
            'pipe_broken': self.recover_pipe_broken
        }
    
    def recover_from_error(self, error: Exception, input_data: bytes) -> ProcessedInput:
        """Recover from pipe processing errors"""
        error_type = type(error).__name__
        strategy = self.recovery_strategies.get(error_type, self.recover_generic)
        return strategy(error, input_data)
    
    def recover_json_error(self, error: Exception, input_data: bytes) -> ProcessedInput:
        """Recover from JSON parsing errors"""
        # Try to fix common JSON issues
        fixed_data = self.fix_json_syntax(input_data)
        try:
            data = json.loads(fixed_data)
            return ProcessedInput(format='json', data=data, success=True)
        except:
            # Fall back to text processing
            return ProcessedInput(format='text', data=input_data.decode('utf-8', errors='replace'), success=True)
```

## 7. Performance and Monitoring

### 7.1 CLI Performance Monitoring
```python
class CLIPerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'command_execution_time': {},
            'pipe_processing_time': {},
            'error_rates': {},
            'throughput': {}
        }
    
    def record_command_execution(self, command: str, execution_time: float):
        """Record command execution time"""
        if command not in self.metrics['command_execution_time']:
            self.metrics['command_execution_time'][command] = []
        self.metrics['command_execution_time'][command].append(execution_time)
    
    def record_pipe_processing(self, format_type: str, processing_time: float):
        """Record pipe processing time"""
        if format_type not in self.metrics['pipe_processing_time']:
            self.metrics['pipe_processing_time'][format_type] = []
        self.metrics['pipe_processing_time'][format_type].append(processing_time)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all CLIs"""
        summary = {}
        for metric_type, metrics in self.metrics.items():
            summary[metric_type] = self.calculate_metric_summary(metrics)
        return summary
```

### 7.2 CLI Health Monitoring
```python
class CLIHealthMonitor:
    def __init__(self):
        self.health_checks = {
            'cli_availability': self.check_cli_availability,
            'pipe_functionality': self.check_pipe_functionality,
            'command_execution': self.check_command_execution,
            'error_rates': self.check_error_rates
        }
    
    def check_cli_health(self, cli: ModuleCLI) -> CLIHealth:
        """Check health of a specific CLI"""
        health_results = {}
        for check_name, check_func in self.health_checks.items():
            try:
                result = check_func(cli)
                health_results[check_name] = result
            except Exception as e:
                health_results[check_name] = {'status': 'error', 'error': str(e)}
        
        overall_health = self.calculate_overall_health(health_results)
        return CLIHealth(
            cli_id=cli.module_id,
            overall_status=overall_health['status'],
            health_score=overall_health['score'],
            checks=health_results,
            last_check=datetime.now()
        )
```

## 8. Implementation Strategy

### 8.1 Phase 1: Core CLI Generation
1. Implement CLI Generator Engine
2. Create base CLI templates
3. Implement pipe processing system
4. Generate CLIs for existing modules

### 8.2 Phase 2: Advanced Features
1. Implement CLI orchestration
2. Add performance monitoring
3. Implement error recovery
4. Add CLI health monitoring

### 8.3 Phase 3: Integration and Optimization
1. Integrate with module registry
2. Optimize performance
3. Add advanced pipe features
4. Implement CLI composition

## 9. Testing Strategy

### 9.1 Unit Testing
- Test CLI generation for each module type
- Test pipe processing for different formats
- Test command execution and error handling
- Test CLI integration with modules

### 9.2 Integration Testing
- Test CLI orchestration across modules
- Test pipe chaining and composition
- Test CLI registry integration
- Test end-to-end CLI workflows

### 9.3 Performance Testing
- Test CLI response times
- Test pipe processing throughput
- Test CLI scalability
- Test error recovery performance

## 10. Dependencies

### 10.1 Internal Dependencies
- ReflectiveModule base class
- Module registry system
- Health monitoring system
- Configuration management system

### 10.2 External Dependencies
- Python argparse library
- JSON processing library
- Text processing library
- Error handling library
- Logging infrastructure

## 11. Constraints and Assumptions

### 11.1 Constraints
- Must maintain compatibility with existing ReflectiveModule interface
- Must support all standard CLI patterns and conventions
- Must maintain performance requirements for all operations
- Must provide comprehensive error handling and recovery

### 11.2 Assumptions
- All ReflectiveModule implementations will follow the standard interface
- CLI generation will be automated and require no manual intervention
- Stdin/stdout pipes will be used for data exchange
- Module capabilities will be discoverable and introspectable










