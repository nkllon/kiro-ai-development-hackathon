#!/usr/bin/env python3
"""
Fix Prometheus Integration
=========================

Remove legacy mode warnings and configure proper Prometheus integration.
"""

import os
import sys
import yaml
from pathlib import Path

def fix_prometheus_config():
    """Fix Prometheus configuration to avoid legacy mode."""
    print("🔧 Fixing Prometheus integration...")
    
    compose_file = Path("deployment/observatory/docker-compose.yml")
    if not compose_file.exists():
        print(f"❌ Docker Compose file not found: {compose_file}")
        return False
    
    # Read current config
    with open(compose_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Fix Observatory environment to disable legacy Prometheus
    if 'services' in config and 'observatory' in config['services']:
        env = config['services']['observatory'].get('environment', {})
        
        # Convert list to dict if needed
        if isinstance(env, list):
            env_dict = {}
            for item in env:
                if '=' in item:
                    key, value = item.split('=', 1)
                    env_dict[key] = value
            env = env_dict
        
        # Disable legacy Prometheus mode
        env.update({
            'DISABLE_PROMETHEUS_LEGACY': 'true',
            'PROMETHEUS_ENABLED': 'true',
            'PROMETHEUS_URL': 'http://observatory-prometheus:9090',
            'MONITORING_DAEMON_ENABLED': 'false',  # Disable the daemon that's not running
            'METRICS_EXPORT_ENABLED': 'true'
        })
        
        config['services']['observatory']['environment'] = env
        print("✅ Updated Observatory Prometheus configuration")
    
    # Write updated config
    with open(compose_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    return True

def create_prometheus_override():
    """Create override to properly configure Prometheus."""
    print("📝 Creating Prometheus configuration override...")
    
    override_content = {
        'version': '3.8',
        'services': {
            'observatory': {
                'environment': {
                    'DISABLE_PROMETHEUS_LEGACY': 'true',
                    'PROMETHEUS_ENABLED': 'true', 
                    'PROMETHEUS_URL': 'http://observatory-prometheus:9090',
                    'MONITORING_DAEMON_ENABLED': 'false',
                    'METRICS_EXPORT_ENABLED': 'true',
                    'LOG_LEVEL': 'INFO'  # Reduce log noise
                }
            }
        }
    }
    
    override_file = Path("deployment/observatory/docker-compose.prometheus.yml")
    with open(override_file, 'w') as f:
        yaml.dump(override_content, f, default_flow_style=False)
    
    print(f"✅ Created Prometheus override: {override_file}")
    return True

def restart_with_prometheus_fix():
    """Restart Observatory with Prometheus fixes."""
    print("🔄 Restarting Observatory with Prometheus fixes...")
    
    deployment_dir = Path("deployment/observatory")
    os.chdir(deployment_dir)
    
    import subprocess
    
    # Stop containers
    subprocess.run(["docker-compose", "down"], capture_output=True)
    
    # Start with all overrides
    env = os.environ.copy()
    env.update({
        'COMPOSE_FILE': 'docker-compose.yml:docker-compose.linux.yml:docker-compose.prometheus.yml'
    })
    
    result = subprocess.run([
        "docker-compose", "up", "-d"
    ], capture_output=True, text=True, env=env)
    
    if result.returncode == 0:
        print("✅ Observatory restarted with Prometheus fixes")
        return True
    else:
        print(f"❌ Restart failed: {result.stderr}")
        return False

def main():
    """Main execution."""
    print("🚀 Fixing Prometheus Integration")
    print("=" * 40)
    
    if not fix_prometheus_config():
        return False
    
    if not create_prometheus_override():
        return False
    
    if not restart_with_prometheus_fix():
        return False
    
    print("\n✅ Prometheus integration fixed!")
    print("⏳ Observatory should start without legacy mode warnings")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)