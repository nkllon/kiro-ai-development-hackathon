#!/usr/bin/env python3
"""
Distributed Deployment Script for Beast Mode Agent Collaboration Network

This script creates deployment manifests for distributed Beast Mode deployment
across multiple nodes.
"""

import os
import sys
import argparse
import logging
import json
import yaml
from pathlib import Path
from typing import List, Dict

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from beast_mode.deployment.config_manager import ConfigManager, DeploymentEnvironment
from beast_mode.deployment.deployment_manager import DeploymentManager


def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('distributed_deployment.log')
        ]
    )


def load_node_config(config_file: str) -> Dict:
    """Load node configuration from file"""
    logger = logging.getLogger(__name__)
    
    if not os.path.exists(config_file):
        logger.error(f"Node configuration file not found: {config_file}")
        raise FileNotFoundError(f"Config file not found: {config_file}")
    
    with open(config_file, 'r') as f:
        if config_file.endswith('.yaml') or config_file.endswith('.yml'):
            config = yaml.safe_load(f)
        else:
            config = json.load(f)
    
    logger.info(f"Loaded node configuration from: {config_file}")
    return config


def create_node_deployment_script(node_config: Dict, deployment_manifest: Dict, output_dir: str):
    """Create deployment script for a specific node"""
    logger = logging.getLogger(__name__)
    
    node_name = node_config['name']
    script_content = f"""#!/bin/bash
# Beast Mode Deployment Script for Node: {node_name}
# Generated automatically - do not edit manually

set -e

echo "Starting Beast Mode deployment on node: {node_name}"

# Configuration
DEPLOYMENT_ID="{deployment_manifest['deployment_id']}"
ENVIRONMENT="{deployment_manifest['environment']}"
NODE_NAME="{node_name}"

# Create directories
mkdir -p logs
mkdir -p spores
mkdir -p config
mkdir -p data

# Set environment variables
export BEAST_MODE_ENVIRONMENT="$ENVIRONMENT"
export BEAST_MODE_NODE="$NODE_NAME"
export BEAST_MODE_DEPLOYMENT_ID="$DEPLOYMENT_ID"

"""
    
    # Add service-specific commands
    for service_name, service_info in deployment_manifest['services'].items():
        if service_info['node'] == node_name:
            service_def = service_info['service']
            
            script_content += f"""
# Start service: {service_name}
echo "Starting service: {service_name}"

# Set service environment
"""
            
            for env_key, env_value in service_def['environment'].items():
                script_content += f'export {env_key}="{env_value}"\n'
            
            script_content += f"""
# Change to working directory
cd "{service_def['working_directory']}"

# Start service in background
nohup {' '.join(service_def['command'])} > logs/{service_name}.log 2>&1 &
SERVICE_PID=$!
echo $SERVICE_PID > logs/{service_name}.pid
echo "Service {service_name} started with PID: $SERVICE_PID"

# Wait a moment for service to start
sleep 2

"""
    
    script_content += """
echo "All services started on this node"
echo "Check logs in the logs/ directory"
echo "To stop services, run: ./stop_services.sh"

# Create stop script
cat > stop_services.sh << 'EOF'
#!/bin/bash
echo "Stopping Beast Mode services..."

for pidfile in logs/*.pid; do
    if [ -f "$pidfile" ]; then
        service_name=$(basename "$pidfile" .pid)
        pid=$(cat "$pidfile")
        echo "Stopping $service_name (PID: $pid)"
        
        if kill -0 "$pid" 2>/dev/null; then
            kill -TERM "$pid"
            sleep 5
            
            if kill -0 "$pid" 2>/dev/null; then
                echo "Force killing $service_name"
                kill -KILL "$pid"
            fi
        fi
        
        rm -f "$pidfile"
    fi
done

echo "All services stopped"
EOF

chmod +x stop_services.sh
"""
    
    # Write script file
    script_file = Path(output_dir) / f"deploy_{node_name}.sh"
    with open(script_file, 'w') as f:
        f.write(script_content)
    
    # Make executable
    os.chmod(script_file, 0o755)
    
    logger.info(f"Created deployment script for {node_name}: {script_file}")
    return script_file


def create_kubernetes_manifests(deployment_manifest: Dict, output_dir: str):
    """Create Kubernetes deployment manifests"""
    logger = logging.getLogger(__name__)
    
    k8s_dir = Path(output_dir) / "kubernetes"
    k8s_dir.mkdir(exist_ok=True)
    
    # Redis deployment
    redis_manifest = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": "beast-mode-redis",
            "labels": {"app": "beast-mode-redis"}
        },
        "spec": {
            "replicas": 1,
            "selector": {"matchLabels": {"app": "beast-mode-redis"}},
            "template": {
                "metadata": {"labels": {"app": "beast-mode-redis"}},
                "spec": {
                    "containers": [{
                        "name": "redis",
                        "image": "redis:7-alpine",
                        "ports": [{"containerPort": 6379}],
                        "command": ["redis-server", "--appendonly", "yes"],
                        "volumeMounts": [{
                            "name": "redis-data",
                            "mountPath": "/data"
                        }]
                    }],
                    "volumes": [{
                        "name": "redis-data",
                        "persistentVolumeClaim": {"claimName": "redis-pvc"}
                    }]
                }
            }
        }
    }
    
    # Redis service
    redis_service = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {"name": "beast-mode-redis"},
        "spec": {
            "selector": {"app": "beast-mode-redis"},
            "ports": [{"port": 6379, "targetPort": 6379}],
            "type": "ClusterIP"
        }
    }
    
    # Redis PVC
    redis_pvc = {
        "apiVersion": "v1",
        "kind": "PersistentVolumeClaim",
        "metadata": {"name": "redis-pvc"},
        "spec": {
            "accessModes": ["ReadWriteOnce"],
            "resources": {"requests": {"storage": "1Gi"}}
        }
    }
    
    # Write Redis manifests
    with open(k8s_dir / "redis-deployment.yaml", 'w') as f:
        yaml.dump(redis_manifest, f, default_flow_style=False)
    
    with open(k8s_dir / "redis-service.yaml", 'w') as f:
        yaml.dump(redis_service, f, default_flow_style=False)
    
    with open(k8s_dir / "redis-pvc.yaml", 'w') as f:
        yaml.dump(redis_pvc, f, default_flow_style=False)
    
    # Agent deployment
    agent_manifest = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": "beast-mode-agent",
            "labels": {"app": "beast-mode-agent"}
        },
        "spec": {
            "replicas": 3,  # Default replica count
            "selector": {"matchLabels": {"app": "beast-mode-agent"}},
            "template": {
                "metadata": {"labels": {"app": "beast-mode-agent"}},
                "spec": {
                    "containers": [{
                        "name": "agent",
                        "image": "beast-mode:latest",  # Would need to be built
                        "env": [
                            {"name": "REDIS_HOST", "value": "beast-mode-redis"},
                            {"name": "REDIS_PORT", "value": "6379"},
                            {"name": "BEAST_MODE_ENVIRONMENT", "value": deployment_manifest['environment']},
                            {"name": "AGENT_ID", "valueFrom": {"fieldRef": {"fieldPath": "metadata.name"}}},
                            {"name": "AGENT_CAPABILITIES", "value": "kubernetes,distributed"}
                        ],
                        "command": [
                            "python", "-m", "beast_mode.messaging.bus_client",
                            "--redis-url", "redis://beast-mode-redis:6379"
                        ],
                        "volumeMounts": [
                            {"name": "spores", "mountPath": "/app/spores"},
                            {"name": "logs", "mountPath": "/app/logs"}
                        ]
                    }],
                    "volumes": [
                        {"name": "spores", "emptyDir": {}},
                        {"name": "logs", "emptyDir": {}}
                    ]
                }
            }
        }
    }
    
    with open(k8s_dir / "agent-deployment.yaml", 'w') as f:
        yaml.dump(agent_manifest, f, default_flow_style=False)
    
    # Create deployment script
    deploy_script = f"""#!/bin/bash
# Kubernetes deployment script for Beast Mode
# Deployment ID: {deployment_manifest['deployment_id']}

set -e

echo "Deploying Beast Mode to Kubernetes..."

# Apply manifests
kubectl apply -f redis-pvc.yaml
kubectl apply -f redis-deployment.yaml
kubectl apply -f redis-service.yaml
kubectl apply -f agent-deployment.yaml

echo "Waiting for Redis to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/beast-mode-redis

echo "Waiting for agents to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/beast-mode-agent

echo "Deployment completed!"
echo "Check status with: kubectl get pods -l app=beast-mode-redis,beast-mode-agent"
"""
    
    deploy_script_file = k8s_dir / "deploy.sh"
    with open(deploy_script_file, 'w') as f:
        f.write(deploy_script)
    
    os.chmod(deploy_script_file, 0o755)
    
    logger.info(f"Created Kubernetes manifests in: {k8s_dir}")


def deploy_distributed(
    environment: str, 
    nodes: List[str], 
    node_config_file: str = None,
    output_dir: str = "deployment_output",
    create_k8s: bool = False
):
    """Create distributed deployment"""
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize managers
        config_manager = ConfigManager()
        deployment_manager = DeploymentManager(config_manager)
        
        # Load node configuration if provided
        node_configs = {}
        if node_config_file:
            full_config = load_node_config(node_config_file)
            node_configs = {node['name']: node for node in full_config.get('nodes', [])}
            
            # Update nodes list from config
            if 'nodes' in full_config:
                nodes = [node['name'] for node in full_config['nodes']]
        
        logger.info(f"Creating distributed deployment for environment: {environment}")
        logger.info(f"Target nodes: {', '.join(nodes)}")
        
        # Create deployment manifest
        deployment_id = deployment_manager.create_distributed_deployment(environment, nodes)
        
        # Load the created manifest
        manifest_file = f"deployment_{deployment_id}.json"
        with open(manifest_file, 'r') as f:
            deployment_manifest = json.load(f)
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Create node-specific deployment scripts
        for node in nodes:
            node_config = node_configs.get(node, {'name': node})
            create_node_deployment_script(node_config, deployment_manifest, output_dir)
        
        # Create Kubernetes manifests if requested
        if create_k8s:
            create_kubernetes_manifests(deployment_manifest, output_dir)
        
        # Create master deployment script
        master_script = f"""#!/bin/bash
# Master deployment script for Beast Mode distributed deployment
# Deployment ID: {deployment_id}

set -e

echo "Starting distributed Beast Mode deployment..."
echo "Deployment ID: {deployment_id}"
echo "Environment: {environment}"
echo "Nodes: {' '.join(nodes)}"

# Deploy to each node
"""
        
        for node in nodes:
            master_script += f"""
echo "Deploying to node: {node}"
# Copy deployment script to {node} and execute
# scp deploy_{node}.sh {node}:~/
# ssh {node} "chmod +x deploy_{node}.sh && ./deploy_{node}.sh"
"""
        
        master_script += """
echo "Distributed deployment completed!"
echo "Check individual node logs for service status"
"""
        
        master_script_file = output_path / "deploy_all.sh"
        with open(master_script_file, 'w') as f:
            f.write(master_script)
        
        os.chmod(master_script_file, 0o755)
        
        # Create README
        readme_content = f"""# Beast Mode Distributed Deployment

Deployment ID: {deployment_id}
Environment: {environment}
Created: {deployment_manifest.get('created_at', 'unknown')}

## Nodes
{chr(10).join(f"- {node}" for node in nodes)}

## Deployment Instructions

### Manual Deployment
1. Copy the appropriate deployment script to each node:
   ```bash
   scp deploy_<node_name>.sh <node_name>:~/
   ```

2. Execute the deployment script on each node:
   ```bash
   ssh <node_name> "chmod +x deploy_<node_name>.sh && ./deploy_<node_name>.sh"
   ```

3. Or use the master script (update with your SSH configuration):
   ```bash
   ./deploy_all.sh
   ```

### Kubernetes Deployment
If Kubernetes manifests were generated:
```bash
cd kubernetes/
./deploy.sh
```

## Service Management

Each node will have:
- `deploy_<node>.sh` - Start services
- `stop_services.sh` - Stop services (created during deployment)
- `logs/` - Service logs directory

## Monitoring

Check service status on each node:
```bash
ps aux | grep beast_mode
tail -f logs/*.log
```

## Troubleshooting

1. Check Redis connectivity:
   ```bash
   redis-cli -h <redis_host> ping
   ```

2. Check service logs:
   ```bash
   tail -f logs/<service_name>.log
   ```

3. Restart failed services:
   ```bash
   ./stop_services.sh
   ./deploy_<node>.sh
   ```
"""
        
        readme_file = output_path / "README.md"
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        
        logger.info(f"Distributed deployment created successfully!")
        logger.info(f"Deployment ID: {deployment_id}")
        logger.info(f"Output directory: {output_dir}")
        logger.info(f"Deployment manifest: {manifest_file}")
        logger.info("See README.md for deployment instructions")
        
        return deployment_id
        
    except Exception as e:
        logger.error(f"Distributed deployment creation failed: {e}")
        raise


def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(description="Create Beast Mode distributed deployment")
    parser.add_argument("--environment", default="distributed", 
                       help="Deployment environment (default: distributed)")
    parser.add_argument("--nodes", nargs="+", required=True,
                       help="List of target nodes")
    parser.add_argument("--node-config", 
                       help="Node configuration file (JSON/YAML)")
    parser.add_argument("--output-dir", default="deployment_output",
                       help="Output directory for deployment files")
    parser.add_argument("--kubernetes", action="store_true",
                       help="Also create Kubernetes manifests")
    parser.add_argument("--log-level", default="INFO",
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Log level (default: INFO)")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Beast Mode distributed deployment creation")
    
    try:
        deployment_id = deploy_distributed(
            environment=args.environment,
            nodes=args.nodes,
            node_config_file=args.node_config,
            output_dir=args.output_dir,
            create_k8s=args.kubernetes
        )
        
        logger.info(f"Deployment creation successful: {deployment_id}")
        
    except Exception as e:
        logger.error(f"Deployment creation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()