#!/usr/bin/env python3
"""
Auto-generated CLI for AgentLifecycleManager
Generated from Unified RM-DDD-CMS System
Bounded Context: AgentLifecycle
DDD Pattern: DomainService
"""

import argparse
import json
import sys
from typing import Any, Dict

def create_parser() -> argparse.ArgumentParser:
    """Create argument parser from unified RM-DDD-CMS capabilities."""
    parser = argparse.ArgumentParser(
        description=f"CLI for AgentLifecycleManager (DomainService in AgentLifecycle context)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Unified RM-DDD-CMS System
Bounded Context: AgentLifecycle
DDD Pattern: DomainService
Domain Vocabulary: agent, lifecycle, manager, add, capability, dependency, content, delete, execute, cli...
        """
    )
    
    # Core system commands
    parser.add_argument('--module-info', action='store_true',
                       help='Show module information including DDD metadata')
    parser.add_argument('--health-check', action='store_true',
                       help='Perform health check')
    parser.add_argument('--list-capabilities', action='store_true',
                       help='List all capabilities')
    
    # DDD commands
    parser.add_argument('--domain-vocabulary', action='store_true',
                       help='Show domain vocabulary and ubiquitous language terms')
    parser.add_argument('--bounded-context', action='store_true',
                       help='Show bounded context information')
    parser.add_argument('--validate-ddd', action='store_true',
                       help='Validate DDD compliance and ubiquitous language usage')
    
    # CMS commands
    parser.add_argument('--list-content', action='store_true',
                       help='List all content in integrated CMS')
    parser.add_argument('--content-types', action='store_true',
                       help='Show available content types')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands (using ubiquitous language)')
    
    # Command: add_capability
    add_capability_parser = subparsers.add_parser('add_capability', 
                                             help='Add a new capability to the module.')
    add_capability_parser.add_argument('capability', 
                                                     type=str, 
                                                     help='Parameter: capability')
    # Command: add_dependency
    add_dependency_parser = subparsers.add_parser('add_dependency', 
                                             help='Add a dependency to the module.')
    add_dependency_parser.add_argument('dependency', 
                                                     type=str, 
                                                     help='Parameter: dependency')
    # Command: delete_content
    delete_content_parser = subparsers.add_parser('delete_content', 
                                             help='Delete content from integrated CMS.')
    delete_content_parser.add_argument('content_id', 
                                                     type=str, 
                                                     help='Parameter: content_id')
    # Command: execute
    execute_parser = subparsers.add_parser('execute', 
                                             help='Execute agent lifecycle management operations.')
    execute_parser.add_argument('args', 
                                                     type=str, 
                                                     help='Parameter: args')
    execute_parser.add_argument('kwargs', 
                                                     type=str, 
                                                     help='Parameter: kwargs')
    # Command: generate_cli_interface
    generate_cli_interface_parser = subparsers.add_parser('generate_cli_interface', 
                                             help='Generate unified CLI interface with DDD and CMS capabilities.')
    # Command: get_bounded_context_info
    get_bounded_context_info_parser = subparsers.add_parser('get_bounded_context_info', 
                                             help='Get bounded context information.')
    # Command: get_capability
    get_capability_parser = subparsers.add_parser('get_capability', 
                                             help='Get a specific capability.')
    get_capability_parser.add_argument('capability_name', 
                                                     type=str, 
                                                     help='Parameter: capability_name')
    # Command: get_cli_commands
    get_cli_commands_parser = subparsers.add_parser('get_cli_commands', 
                                             help='Get CLI command definitions for external CLI generators.')
    # Command: get_content
    get_content_parser = subparsers.add_parser('get_content', 
                                             help='Retrieve content from integrated CMS.')
    get_content_parser.add_argument('content_id', 
                                                     type=str, 
                                                     help='Parameter: content_id')
    # Command: get_ddd_metadata
    get_ddd_metadata_parser = subparsers.add_parser('get_ddd_metadata', 
                                             help='Get DDD-specific metadata for the module.')
    # Command: get_domain_vocabulary
    get_domain_vocabulary_parser = subparsers.add_parser('get_domain_vocabulary', 
                                             help='Get domain vocabulary terms and definitions.')
    # Command: get_error_history
    get_error_history_parser = subparsers.add_parser('get_error_history', 
                                             help='Get error history for debugging.')
    # Command: get_health_status
    get_health_status_parser = subparsers.add_parser('get_health_status', 
                                             help='Get current health status with detailed metrics.')
    # Command: get_interface_metadata
    get_interface_metadata_parser = subparsers.add_parser('get_interface_metadata', 
                                             help='Get unified RM-DDD-CMS interface metadata for registry.')
    # Command: handle_agent_failure
    handle_agent_failure_parser = subparsers.add_parser('handle_agent_failure', 
                                             help='Handle agent failures gracefully with proper cleanup.')
    handle_agent_failure_parser.add_argument('failed_agent', 
                                                     type=str, 
                                                     help='Parameter: failed_agent')
    handle_agent_failure_parser.add_argument('failure_context', 
                                                     type=str, 
                                                     help='Parameter: failure_context')
    # Command: health_check
    health_check_parser = subparsers.add_parser('health_check', 
                                             help='Perform comprehensive health check.')
    # Command: list_capabilities
    list_capabilities_parser = subparsers.add_parser('list_capabilities', 
                                             help='List all capability names.')
    # Command: list_content
    list_content_parser = subparsers.add_parser('list_content', 
                                             help='List content from integrated CMS.')
    list_content_parser.add_argument('--content_type', 
                                                     type=str, 
                                                     default=None,
                                                     help='Parameter: content_type (default: None)')
    # Command: log_error
    log_error_parser = subparsers.add_parser('log_error', 
                                             help='Log an error for health tracking.')
    log_error_parser.add_argument('error', 
                                                     type=str, 
                                                     help='Parameter: error')
    log_error_parser.add_argument('--context', 
                                                     type=str, 
                                                     default=None,
                                                     help='Parameter: context (default: None)')
    # Command: register_agent
    register_agent_parser = subparsers.add_parser('register_agent', 
                                             help='Register new specialized agent with capability validation.')
    register_agent_parser.add_argument('agent', 
                                                     type=str, 
                                                     help='Parameter: agent')
    register_agent_parser.add_argument('capabilities', 
                                                     type=str, 
                                                     help='Parameter: capabilities')
    register_agent_parser.add_argument('perspective_profile', 
                                                     type=str, 
                                                     help='Parameter: perspective_profile')
    # Command: register_module
    register_module_parser = subparsers.add_parser('register_module', 
                                             help='Register module with registry.')
    register_module_parser.add_argument('registry', 
                                                     type=str, 
                                                     help='Parameter: registry')
    # Command: remove_capability
    remove_capability_parser = subparsers.add_parser('remove_capability', 
                                             help='Remove a capability from the module.')
    remove_capability_parser.add_argument('capability_name', 
                                                     type=str, 
                                                     help='Parameter: capability_name')
    # Command: remove_dependency
    remove_dependency_parser = subparsers.add_parser('remove_dependency', 
                                             help='Remove a dependency from the module.')
    remove_dependency_parser.add_argument('dependency', 
                                                     type=str, 
                                                     help='Parameter: dependency')
    # Command: save_cli_interface
    save_cli_interface_parser = subparsers.add_parser('save_cli_interface', 
                                             help='Save generated CLI interface to file.')
    save_cli_interface_parser.add_argument('output_path', 
                                                     type=str, 
                                                     help='Parameter: output_path')
    # Command: set_health
    set_health_parser = subparsers.add_parser('set_health', 
                                             help='Set module health.')
    set_health_parser.add_argument('health', 
                                                     type=str, 
                                                     help='Parameter: health')
    # Command: set_status
    set_status_parser = subparsers.add_parser('set_status', 
                                             help='Set module status.')
    set_status_parser.add_argument('status', 
                                                     type=str, 
                                                     help='Parameter: status')
    # Command: store_content
    store_content_parser = subparsers.add_parser('store_content', 
                                             help='Store content in integrated CMS.')
    store_content_parser.add_argument('content_id', 
                                                     type=str, 
                                                     help='Parameter: content_id')
    store_content_parser.add_argument('content_type', 
                                                     type=str, 
                                                     help='Parameter: content_type')
    store_content_parser.add_argument('data', 
                                                     type=str, 
                                                     help='Parameter: data')
    # Command: track_agent_health
    track_agent_health_parser = subparsers.add_parser('track_agent_health', 
                                             help='Track agent availability and health status.')
    track_agent_health_parser.add_argument('agent_pool', 
                                                     type=str, 
                                                     help='Parameter: agent_pool')
    # Command: update_content
    update_content_parser = subparsers.add_parser('update_content', 
                                             help='Update content in integrated CMS.')
    update_content_parser.add_argument('content_id', 
                                                     type=str, 
                                                     help='Parameter: content_id')
    update_content_parser.add_argument('data', 
                                                     type=str, 
                                                     help='Parameter: data')
    # Command: update_custom_metrics
    update_custom_metrics_parser = subparsers.add_parser('update_custom_metrics', 
                                             help='Update custom health metrics.')
    update_custom_metrics_parser.add_argument('metrics', 
                                                     type=str, 
                                                     help='Parameter: metrics')
    # Command: validate_command_language
    validate_command_language_parser = subparsers.add_parser('validate_command_language', 
                                             help='Validate that a command follows ubiquitous language.')
    validate_command_language_parser.add_argument('command', 
                                                     type=str, 
                                                     help='Parameter: command')
    # Command: validate_ddd_compliance
    validate_ddd_compliance_parser = subparsers.add_parser('validate_ddd_compliance', 
                                             help='Validate DDD compliance and return detailed results.')

    return parser

def main():
    """Unified RM-DDD-CMS CLI entry point with ubiquitous language enforcement."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Import and instantiate the module
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    from multi_perspective_ghostbusters.agent_lifecycle_manager import AgentLifecycleManager
    module = AgentLifecycleManager()
    
    if args.module_info:
        metadata = module.get_interface_metadata()
        metadata['ddd_metadata'] = module.get_ddd_metadata()
        print(json.dumps(metadata, indent=2))
        return
    
    if args.health_check:
        print(json.dumps(module.get_health_status(), indent=2))
        return
    
    if args.list_capabilities:
        capabilities = module.list_capabilities()
        print(f"Available capabilities in {module.bounded_context.name if module.bounded_context else 'Unknown'} context:")
        for cap in capabilities:
            capability = module.get_capability(cap)
            pattern = capability.get('ddd_pattern', 'Unknown pattern') if capability else 'Unknown pattern'
            print(f"  - {cap} ({pattern})")
        return
    
    if args.domain_vocabulary:
        vocab = module.get_domain_vocabulary()
        print("Domain Vocabulary (Ubiquitous Language):")
        for term, definition in vocab.items():
            print(f"  - {term}: {definition}")
        return
    
    if args.bounded_context:
        context_info = module.get_bounded_context_info()
        print(json.dumps(context_info, indent=2))
        return
    
    if args.validate_ddd:
        validation_results = module.validate_ddd_compliance()
        print("DDD Compliance Validation:")
        print(json.dumps(validation_results, indent=2))
        return
    
    if args.list_content:
        content = module.list_content()
        print("CMS Content:")
        print(json.dumps(content, indent=2, default=str))
        return
    
    if args.content_types:
        content = module.list_content()
        types = set(item.get('type', 'unknown') for item in content)
        print("Available content types:")
        for content_type in sorted(types):
            print(f"  - {content_type}")
        return
    
    if args.command:
        # Validate command uses ubiquitous language
        validation_result = module.validate_command_language(args.command)
        if not validation_result['valid']:
            print(f"Warning: Command '{args.command}' may not follow ubiquitous language: {validation_result['message']}")
        
        # Execute the requested capability
        if hasattr(module, args.command):
            method = getattr(module, args.command)
            
            # Build kwargs from parsed arguments
            kwargs = {}
            for key, value in vars(args).items():
                if key not in ['command', 'module_info', 'health_check', 'list_capabilities', 
                              'domain_vocabulary', 'bounded_context', 'validate_ddd', 
                              'list_content', 'content_types']:
                    if value is not None:
                        kwargs[key] = value
            
            try:
                result = method(**kwargs)
                if result is not None:
                    if isinstance(result, (dict, list)):
                        print(json.dumps(result, indent=2, default=str))
                    else:
                        print(result)
            except Exception as e:
                print(f"Error executing {args.command}: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
