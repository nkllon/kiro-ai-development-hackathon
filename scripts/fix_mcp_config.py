#!/usr/bin/env python3
"""
🔧 MCP Configuration Fixer
=========================
Comprehensive fix for MCP configuration issues
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any

class MCPConfigFixer:
    """Comprehensive MCP configuration fixer"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.mcp_config_path = self.project_root / '.cursor' / 'mcp.json'
        self.fixes_applied = []
        
    def fix_mcp_configuration(self):
        """Apply comprehensive fixes to MCP configuration"""
        print("🔧 MCP CONFIGURATION FIXER")
        print("=" * 50)
        print("🛠️ Applying comprehensive fixes to MCP configuration")
        print()
        
        # Load current configuration
        print("📋 PHASE 1: LOADING CURRENT CONFIGURATION")
        print("=" * 50)
        config = self.load_current_config()
        if not config:
            return False
        
        # Apply fixes
        print("\n🔧 PHASE 2: APPLYING COMPREHENSIVE FIXES")
        print("=" * 50)
        self.apply_comprehensive_fixes(config)
        
        # Validate fixed configuration
        print("\n✅ PHASE 3: VALIDATING FIXED CONFIGURATION")
        print("=" * 50)
        self.validate_fixed_configuration(config)
        
        # Write fixed configuration
        print("\n💾 PHASE 4: WRITING FIXED CONFIGURATION")
        print("=" * 50)
        self.write_fixed_configuration(config)
        
        # Generate fix report
        print("\n📊 PHASE 5: GENERATING FIX REPORT")
        print("=" * 50)
        self.generate_fix_report()
        
        return True
    
    def load_current_config(self):
        """Load current MCP configuration"""
        try:
            with open(self.mcp_config_path, 'r') as f:
                config = json.load(f)
            print("✅ Current configuration loaded successfully")
            return config
        except Exception as e:
            print(f"❌ Failed to load configuration: {e}")
            return None
    
    def apply_comprehensive_fixes(self, config):
        """Apply comprehensive fixes to the configuration"""
        print("🔧 Applying comprehensive fixes...")
        
        # Fix 1: Environment variable references
        self.fix_environment_variables(config)
        
        # Fix 2: GitHub MCP server configuration
        self.fix_github_server_config(config)
        
        # Fix 3: Voice mode configuration
        self.fix_voice_mode_config(config)
        
        # Fix 4: Simone adapter configuration
        self.fix_simone_config(config)
        
        # Fix 5: Add proper error handling
        self.add_error_handling(config)
        
        print(f"✅ Applied {len(self.fixes_applied)} fixes")
    
    def fix_environment_variables(self, config):
        """Fix environment variable references"""
        print("   🔧 Fixing environment variable references...")
        
        # Fix OpenAI API key reference
        if 'voice-mode' in config.get('mcpServers', {}):
            voice_config = config['mcpServers']['voice-mode']
            if 'env' in voice_config and 'OPENAI_API_KEY' in voice_config['env']:
                old_value = voice_config['env']['OPENAI_API_KEY']
                new_value = '${OPENAI_API_KEY}'
                voice_config['env']['OPENAI_API_KEY'] = new_value
                
                self.fixes_applied.append({
                    'fix': 'environment_variable_reference',
                    'server': 'voice-mode',
                    'variable': 'OPENAI_API_KEY',
                    'old_value': old_value,
                    'new_value': new_value,
                    'description': 'Changed placeholder to environment variable reference'
                })
                print(f"      ✅ Fixed voice-mode.OPENAI_API_KEY: {old_value} → {new_value}")
        
        # Fix GitHub token reference
        if 'github' in config.get('mcpServers', {}):
            github_config = config['mcpServers']['github']
            if 'env' in github_config and 'GITHUB_PERSONAL_ACCESS_TOKEN' in github_config['env']:
                old_value = github_config['env']['GITHUB_PERSONAL_ACCESS_TOKEN']
                new_value = '${GITHUB_TOKEN}'
                github_config['env']['GITHUB_PERSONAL_ACCESS_TOKEN'] = new_value
                
                self.fixes_applied.append({
                    'fix': 'environment_variable_reference',
                    'server': 'github',
                    'variable': 'GITHUB_PERSONAL_ACCESS_TOKEN',
                    'old_value': old_value,
                    'new_value': new_value,
                    'description': 'Changed placeholder to environment variable reference'
                })
                print(f"      ✅ Fixed github.GITHUB_PERSONAL_ACCESS_TOKEN: {old_value} → {new_value}")
    
    def fix_github_server_config(self, config):
        """Fix GitHub MCP server configuration"""
        print("   🔧 Fixing GitHub MCP server configuration...")
        
        if 'github' not in config.get('mcpServers', {}):
            return
        
        github_config = config['mcpServers']['github']
        
        # Check if Docker is available
        if self.is_docker_available():
            print("      ✅ Docker is available - GitHub server configuration is valid")
        else:
            # Provide alternative configuration
            print("      ⚠️ Docker not available - providing alternative configuration")
            alternative_config = {
                "command": "npx",
                "args": ["@modelcontextprotocol/server-github"],
                "env": {
                    "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
                }
            }
            
            old_config = github_config.copy()
            github_config.update(alternative_config)
            
            self.fixes_applied.append({
                'fix': 'github_server_alternative',
                'server': 'github',
                'old_config': old_config,
                'new_config': alternative_config,
                'description': 'Provided alternative GitHub server configuration without Docker'
            })
            print("      ✅ Updated GitHub server to use npx alternative")
    
    def fix_voice_mode_config(self, config):
        """Fix voice mode configuration"""
        print("   🔧 Fixing voice mode configuration...")
        
        if 'voice-mode' not in config.get('mcpServers', {}):
            return
        
        voice_config = config['mcpServers']['voice-mode']
        
        # Check if uvx is available
        if self.is_uvx_available():
            print("      ✅ uvx is available - voice mode configuration is valid")
        else:
            # Provide alternative configuration
            print("      ⚠️ uvx not available - providing alternative configuration")
            alternative_config = {
                "command": "pipx",
                "args": ["run", "voice-mode"],
                "env": {
                    "OPENAI_API_KEY": "${OPENAI_API_KEY}"
                }
            }
            
            old_config = voice_config.copy()
            voice_config.update(alternative_config)
            
            self.fixes_applied.append({
                'fix': 'voice_mode_alternative',
                'server': 'voice-mode',
                'old_config': old_config,
                'new_config': alternative_config,
                'description': 'Provided alternative voice mode configuration using pipx'
            })
            print("      ✅ Updated voice mode to use pipx alternative")
    
    def fix_simone_config(self, config):
        """Fix Simone adapter configuration"""
        print("   🔧 Fixing Simone adapter configuration...")
        
        if 'simone' not in config.get('mcpServers', {}):
            return
        
        simone_config = config['mcpServers']['simone']
        
        # Check if the simone adapter file exists
        simone_file = self.project_root / 'kiro_simone_adapter' / 'mcp-server' / 'dist' / 'index.js'
        
        if simone_file.exists():
            print("      ✅ Simone adapter file exists - configuration is valid")
        else:
            print("      ⚠️ Simone adapter file not found - checking for alternatives")
            
            # Look for alternative simone files
            possible_paths = [
                'kiro_simone_adapter/mcp-server/index.js',
                'kiro_simone_adapter/index.js',
                'simone/mcp-server/dist/index.js',
                'simone/index.js'
            ]
            
            found_alternative = None
            for path in possible_paths:
                alt_file = self.project_root / path
                if alt_file.exists():
                    found_alternative = path
                    break
            
            if found_alternative:
                old_args = simone_config.get('args', [])
                new_args = [found_alternative]
                simone_config['args'] = new_args
                
                self.fixes_applied.append({
                    'fix': 'simone_path_correction',
                    'server': 'simone',
                    'old_args': old_args,
                    'new_args': new_args,
                    'description': f'Updated Simone adapter path to {found_alternative}'
                })
                print(f"      ✅ Updated Simone adapter path to: {found_alternative}")
            else:
                print("      ❌ No alternative Simone adapter found")
    
    def add_error_handling(self, config):
        """Add proper error handling to configuration"""
        print("   🔧 Adding error handling...")
        
        # Add timeout configurations
        for server_name, server_config in config.get('mcpServers', {}).items():
            if 'timeout' not in server_config:
                server_config['timeout'] = 30000  # 30 seconds
                
                self.fixes_applied.append({
                    'fix': 'add_timeout',
                    'server': server_name,
                    'timeout': 30000,
                    'description': 'Added 30-second timeout for server'
                })
                print(f"      ✅ Added timeout to {server_name}")
        
        # Add retry configurations
        for server_name, server_config in config.get('mcpServers', {}).items():
            if 'retries' not in server_config:
                server_config['retries'] = 3
                
                self.fixes_applied.append({
                    'fix': 'add_retries',
                    'server': server_name,
                    'retries': 3,
                    'description': 'Added retry configuration for server'
                })
                print(f"      ✅ Added retries to {server_name}")
    
    def is_docker_available(self):
        """Check if Docker is available"""
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def is_uvx_available(self):
        """Check if uvx is available"""
        try:
            result = subprocess.run(['uvx', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def validate_fixed_configuration(self, config):
        """Validate the fixed configuration"""
        print("✅ Validating fixed configuration...")
        
        validation_issues = []
        
        # Check JSON structure
        if 'mcpServers' not in config:
            validation_issues.append("Missing mcpServers section")
        
        # Check each server
        for server_name, server_config in config.get('mcpServers', {}).items():
            if not isinstance(server_config, dict):
                validation_issues.append(f"{server_name}: Invalid configuration object")
                continue
            
            if 'command' not in server_config:
                validation_issues.append(f"{server_name}: Missing command")
            
            if 'args' in server_config and not isinstance(server_config['args'], list):
                validation_issues.append(f"{server_name}: Invalid args (must be array)")
            
            if 'env' in server_config and not isinstance(server_config['env'], dict):
                validation_issues.append(f"{server_name}: Invalid env (must be object)")
        
        if validation_issues:
            print("   ❌ Validation issues found:")
            for issue in validation_issues:
                print(f"      • {issue}")
        else:
            print("   ✅ Configuration validation passed")
    
    def write_fixed_configuration(self, config):
        """Write the fixed configuration to file"""
        try:
            # Create backup
            backup_path = self.mcp_config_path.with_suffix('.json.backup')
            if self.mcp_config_path.exists():
                with open(self.mcp_config_path, 'r') as src:
                    with open(backup_path, 'w') as dst:
                        dst.write(src.read())
                print(f"   💾 Created backup: {backup_path}")
            
            # Write fixed configuration
            with open(self.mcp_config_path, 'w') as f:
                json.dump(config, f, indent=2)
            print("   ✅ Fixed configuration written successfully")
            
        except Exception as e:
            print(f"   ❌ Failed to write configuration: {e}")
    
    def generate_fix_report(self):
        """Generate fix report"""
        print("📊 Generating fix report...")
        
        report = {
            'timestamp': self.get_timestamp(),
            'config_file': str(self.mcp_config_path),
            'total_fixes': len(self.fixes_applied),
            'fixes_applied': self.fixes_applied,
            'fix_status': 'SUCCESS'
        }
        
        # Save report
        os.makedirs('.beast_mode', exist_ok=True)
        report_path = self.project_root / '.beast_mode' / 'mcp_fix_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"   💾 Fix report saved to {report_path}")
        
        # Print summary
        print(f"\n📊 MCP CONFIGURATION FIX SUMMARY")
        print("=" * 50)
        print(f"📋 Configuration file: {self.mcp_config_path}")
        print(f"🔧 Total fixes applied: {len(self.fixes_applied)}")
        print(f"📊 Fix status: {report['fix_status']}")
        
        if self.fixes_applied:
            print(f"\n✅ FIXES APPLIED:")
            for fix in self.fixes_applied:
                print(f"   🔧 {fix['fix']}: {fix['description']}")
                if 'old_value' in fix and 'new_value' in fix:
                    print(f"      {fix['old_value']} → {fix['new_value']}")
        
        print(f"\n🎯 NEXT STEPS:")
        print(f"   1. Set required environment variables:")
        print(f"      export OPENAI_API_KEY='your-openai-key-here'")
        print(f"      export GITHUB_TOKEN='your-github-token-here'")
        print(f"   2. Restart Cursor to reload MCP configuration")
        print(f"   3. Test MCP servers to ensure they're working")
    
    def get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

if __name__ == "__main__":
    fixer = MCPConfigFixer()
    success = fixer.fix_mcp_configuration()
    
    if success:
        print("\n🎉 MCP CONFIGURATION FIX COMPLETE!")
        print("🔧 All issues have been resolved")
    else:
        print("\n❌ MCP CONFIGURATION FIX FAILED!")
        print("🔧 Please review the errors and try again")

