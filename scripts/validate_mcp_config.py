#!/usr/bin/env python3
"""
🔧 MCP Configuration Validator
=============================
Validates and fixes MCP configuration issues
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

class MCPConfigValidator:
    """Validates and fixes MCP configuration"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.mcp_config_path = self.project_root / '.cursor' / 'mcp.json'
        self.issues_found = []
        self.fixes_applied = []
        
    def validate_and_fix_mcp_config(self):
        """Validate and fix MCP configuration"""
        print("🔧 MCP CONFIGURATION VALIDATOR")
        print("=" * 50)
        print("🔍 Validating and fixing MCP configuration issues")
        print()
        
        # Check if MCP config exists
        if not self.mcp_config_path.exists():
            print("❌ MCP configuration file not found")
            return False
        
        # Load and validate configuration
        print("📋 PHASE 1: LOADING AND VALIDATING CONFIGURATION")
        print("=" * 50)
        config = self.load_mcp_config()
        if not config:
            return False
        
        # Validate each server configuration
        print("\n🔍 PHASE 2: VALIDATING SERVER CONFIGURATIONS")
        print("=" * 50)
        self.validate_server_configurations(config)
        
        # Check for duplicate entries
        print("\n🔍 PHASE 3: CHECKING FOR DUPLICATES")
        print("=" * 50)
        self.check_for_duplicates(config)
        
        # Validate environment variables
        print("\n🔍 PHASE 4: VALIDATING ENVIRONMENT VARIABLES")
        print("=" * 50)
        self.validate_environment_variables(config)
        
        # Check file paths
        print("\n🔍 PHASE 5: VALIDATING FILE PATHS")
        print("=" * 50)
        self.validate_file_paths(config)
        
        # Apply fixes if needed
        print("\n🔧 PHASE 6: APPLYING FIXES")
        print("=" * 50)
        if self.issues_found:
            self.apply_fixes(config)
        else:
            print("✅ No issues found - configuration is valid")
        
        # Generate validation report
        print("\n📊 PHASE 7: GENERATING VALIDATION REPORT")
        print("=" * 50)
        self.generate_validation_report()
        
        return len(self.issues_found) == 0
    
    def load_mcp_config(self):
        """Load MCP configuration"""
        try:
            with open(self.mcp_config_path, 'r') as f:
                config = json.load(f)
            print("✅ MCP configuration loaded successfully")
            return config
        except json.JSONDecodeError as e:
            self.issues_found.append({
                'type': 'json_syntax_error',
                'message': f'Invalid JSON syntax: {e}',
                'severity': 'critical'
            })
            print(f"❌ JSON syntax error: {e}")
            return None
        except Exception as e:
            self.issues_found.append({
                'type': 'file_read_error',
                'message': f'Failed to read MCP config: {e}',
                'severity': 'critical'
            })
            print(f"❌ Failed to read MCP config: {e}")
            return None
    
    def validate_server_configurations(self, config):
        """Validate each server configuration"""
        if 'mcpServers' not in config:
            self.issues_found.append({
                'type': 'missing_mcp_servers',
                'message': 'Missing mcpServers section',
                'severity': 'critical'
            })
            print("❌ Missing mcpServers section")
            return
        
        servers = config['mcpServers']
        if not isinstance(servers, dict):
            self.issues_found.append({
                'type': 'invalid_servers_type',
                'message': 'mcpServers must be an object',
                'severity': 'critical'
            })
            print("❌ mcpServers must be an object")
            return
        
        print(f"📊 Found {len(servers)} MCP servers configured")
        
        for server_name, server_config in servers.items():
            print(f"   🔍 Validating server: {server_name}")
            self.validate_single_server(server_name, server_config)
    
    def validate_single_server(self, server_name, server_config):
        """Validate a single server configuration"""
        if not isinstance(server_config, dict):
            self.issues_found.append({
                'type': 'invalid_server_config',
                'server': server_name,
                'message': 'Server configuration must be an object',
                'severity': 'critical'
            })
            print(f"      ❌ Invalid server configuration")
            return
        
        # Check required fields
        required_fields = ['command']
        for field in required_fields:
            if field not in server_config:
                self.issues_found.append({
                    'type': 'missing_required_field',
                    'server': server_name,
                    'field': field,
                    'message': f'Missing required field: {field}',
                    'severity': 'critical'
                })
                print(f"      ❌ Missing required field: {field}")
        
        # Validate command
        if 'command' in server_config:
            command = server_config['command']
            if not isinstance(command, str) or not command.strip():
                self.issues_found.append({
                    'type': 'invalid_command',
                    'server': server_name,
                    'message': 'Command must be a non-empty string',
                    'severity': 'critical'
                })
                print(f"      ❌ Invalid command")
        
        # Validate args
        if 'args' in server_config:
            args = server_config['args']
            if not isinstance(args, list):
                self.issues_found.append({
                    'type': 'invalid_args',
                    'server': server_name,
                    'message': 'Args must be an array',
                    'severity': 'critical'
                })
                print(f"      ❌ Invalid args (must be array)")
        
        # Validate env
        if 'env' in server_config:
            env = server_config['env']
            if not isinstance(env, dict):
                self.issues_found.append({
                    'type': 'invalid_env',
                    'server': server_name,
                    'message': 'Environment variables must be an object',
                    'severity': 'critical'
                })
                print(f"      ❌ Invalid env (must be object)")
        
        print(f"      ✅ Server {server_name} configuration validated")
    
    def check_for_duplicates(self, config):
        """Check for duplicate server entries"""
        if 'mcpServers' not in config:
            return
        
        servers = config['mcpServers']
        server_names = list(servers.keys())
        
        # Check for duplicate names
        seen_names = set()
        duplicates = []
        for name in server_names:
            if name in seen_names:
                duplicates.append(name)
            else:
                seen_names.add(name)
        
        if duplicates:
            self.issues_found.append({
                'type': 'duplicate_servers',
                'message': f'Duplicate server names found: {duplicates}',
                'severity': 'critical'
            })
            print(f"❌ Duplicate server names: {duplicates}")
        else:
            print("✅ No duplicate server names found")
        
        # Check for duplicate configurations
        server_configs = list(servers.values())
        seen_configs = set()
        duplicate_configs = []
        
        for i, config_item in enumerate(server_configs):
            config_str = json.dumps(config_item, sort_keys=True)
            if config_str in seen_configs:
                duplicate_configs.append(server_names[i])
            else:
                seen_configs.add(config_str)
        
        if duplicate_configs:
            self.issues_found.append({
                'type': 'duplicate_configurations',
                'message': f'Duplicate server configurations found: {duplicate_configs}',
                'severity': 'warning'
            })
            print(f"⚠️ Duplicate server configurations: {duplicate_configs}")
        else:
            print("✅ No duplicate configurations found")
    
    def validate_environment_variables(self, config):
        """Validate environment variables"""
        if 'mcpServers' not in config:
            return
        
        servers = config['mcpServers']
        env_issues = []
        
        for server_name, server_config in servers.items():
            if 'env' not in server_config:
                continue
            
            env_vars = server_config['env']
            for env_name, env_value in env_vars.items():
                # Check for placeholder values
                if self.is_placeholder_value(env_value):
                    env_issues.append({
                        'server': server_name,
                        'variable': env_name,
                        'value': env_value,
                        'issue': 'placeholder_value'
                    })
                    print(f"   ⚠️ {server_name}.{env_name}: Placeholder value detected")
                
                # Check for environment variable references
                if isinstance(env_value, str) and env_value.startswith('${') and env_value.endswith('}'):
                    env_var_name = env_value[2:-1]
                    if not os.getenv(env_var_name):
                        env_issues.append({
                            'server': server_name,
                            'variable': env_name,
                            'value': env_value,
                            'issue': 'missing_env_var'
                        })
                        print(f"   ⚠️ {server_name}.{env_name}: Environment variable {env_var_name} not set")
        
        if env_issues:
            self.issues_found.append({
                'type': 'environment_variable_issues',
                'message': f'Found {len(env_issues)} environment variable issues',
                'details': env_issues,
                'severity': 'warning'
            })
        else:
            print("✅ Environment variables validated")
    
    def is_placeholder_value(self, value):
        """Check if a value is a placeholder"""
        if not isinstance(value, str):
            return False
        
        placeholder_patterns = [
            'your-openai-key-here',
            'your-api-key-here',
            'your-token-here',
            'ghp_2BqBqBqBqBqBqBqBqBqBqBqBqBqBqBqBq',  # Dummy GitHub token
            'sk-',  # OpenAI key pattern
            'ghp_',  # GitHub token pattern
        ]
        
        return any(pattern in value.lower() for pattern in placeholder_patterns)
    
    def validate_file_paths(self, config):
        """Validate file paths in configurations"""
        if 'mcpServers' not in config:
            return
        
        servers = config['mcpServers']
        path_issues = []
        
        for server_name, server_config in servers.items():
            # Check args for file paths
            if 'args' in server_config:
                for arg in server_config['args']:
                    if isinstance(arg, str) and self.looks_like_file_path(arg):
                        if not self.is_absolute_path(arg) and not self.file_exists_relative(arg):
                            path_issues.append({
                                'server': server_name,
                                'path': arg,
                                'issue': 'file_not_found'
                            })
                            print(f"   ⚠️ {server_name}: File not found: {arg}")
            
            # Check command for executable
            if 'command' in server_config:
                command = server_config['command']
                if command not in ['node', 'docker', 'uvx', 'python', 'python3']:
                    # Assume it's a file path
                    if self.looks_like_file_path(command) and not self.file_exists_relative(command):
                        path_issues.append({
                            'server': server_name,
                            'path': command,
                            'issue': 'executable_not_found'
                        })
                        print(f"   ⚠️ {server_name}: Executable not found: {command}")
        
        if path_issues:
            self.issues_found.append({
                'type': 'file_path_issues',
                'message': f'Found {len(path_issues)} file path issues',
                'details': path_issues,
                'severity': 'warning'
            })
        else:
            print("✅ File paths validated")
    
    def looks_like_file_path(self, path):
        """Check if a string looks like a file path"""
        return '/' in path or path.endswith('.js') or path.endswith('.py') or path.endswith('.exe')
    
    def is_absolute_path(self, path):
        """Check if a path is absolute"""
        return os.path.isabs(path)
    
    def file_exists_relative(self, path):
        """Check if a relative file exists"""
        full_path = self.project_root / path
        return full_path.exists()
    
    def apply_fixes(self, config):
        """Apply fixes to the configuration"""
        print(f"🔧 Applying fixes for {len(self.issues_found)} issues...")
        
        # Fix placeholder values
        for issue in self.issues_found:
            if issue['type'] == 'environment_variable_issues':
                self.fix_environment_variables(config, issue['details'])
        
        # Write fixed configuration
        if self.fixes_applied:
            self.write_fixed_config(config)
    
    def fix_environment_variables(self, config, env_issues):
        """Fix environment variable issues"""
        for env_issue in env_issues:
            if env_issue['issue'] == 'placeholder_value':
                server_name = env_issue['server']
                variable_name = env_issue['variable']
                
                # Suggest environment variable reference
                suggested_value = f"${{{variable_name.upper()}}}"
                
                if server_name in config['mcpServers']:
                    if 'env' in config['mcpServers'][server_name]:
                        config['mcpServers'][server_name]['env'][variable_name] = suggested_value
                        
                        self.fixes_applied.append({
                            'type': 'environment_variable_fix',
                            'server': server_name,
                            'variable': variable_name,
                            'old_value': env_issue['value'],
                            'new_value': suggested_value
                        })
                        print(f"   ✅ Fixed {server_name}.{variable_name}: {env_issue['value']} → {suggested_value}")
    
    def write_fixed_config(self, config):
        """Write the fixed configuration back to file"""
        try:
            with open(self.mcp_config_path, 'w') as f:
                json.dump(config, f, indent=2)
            print("✅ Fixed configuration written to file")
        except Exception as e:
            print(f"❌ Failed to write fixed configuration: {e}")
    
    def generate_validation_report(self):
        """Generate validation report"""
        print("📊 Generating validation report...")
        
        report = {
            'timestamp': self.get_timestamp(),
            'config_file': str(self.mcp_config_path),
            'total_issues': len(self.issues_found),
            'issues': self.issues_found,
            'fixes_applied': self.fixes_applied,
            'validation_status': 'PASS' if len(self.issues_found) == 0 else 'FAIL'
        }
        
        # Save report
        os.makedirs('.beast_mode', exist_ok=True)
        report_path = self.project_root / '.beast_mode' / 'mcp_validation_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"   💾 Validation report saved to {report_path}")
        
        # Print summary
        print(f"\n📊 MCP CONFIGURATION VALIDATION SUMMARY")
        print("=" * 50)
        print(f"📋 Configuration file: {self.mcp_config_path}")
        print(f"🔍 Total issues found: {len(self.issues_found)}")
        print(f"🔧 Fixes applied: {len(self.fixes_applied)}")
        print(f"📊 Validation status: {report['validation_status']}")
        
        if self.issues_found:
            print(f"\n❌ ISSUES FOUND:")
            for issue in self.issues_found:
                severity_icon = "🔴" if issue['severity'] == 'critical' else "🟡"
                print(f"   {severity_icon} {issue['type']}: {issue['message']}")
        
        if self.fixes_applied:
            print(f"\n✅ FIXES APPLIED:")
            for fix in self.fixes_applied:
                print(f"   🔧 {fix['type']}: {fix.get('old_value', 'N/A')} → {fix.get('new_value', 'N/A')}")
    
    def get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

if __name__ == "__main__":
    validator = MCPConfigValidator()
    success = validator.validate_and_fix_mcp_config()
    
    if success:
        print("\n✅ MCP CONFIGURATION VALIDATION COMPLETE!")
        print("🎉 Configuration is valid and ready to use")
    else:
        print("\n❌ MCP CONFIGURATION VALIDATION FAILED!")
        print("🔧 Please review and fix the identified issues")
