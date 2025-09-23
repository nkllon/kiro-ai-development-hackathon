#!/usr/bin/env python3
"""
Beast Mode Deployment System Demo

This example demonstrates the complete deployment and configuration
management system for the Beast Mode Agent Collaboration Network.
"""

import os
import sys
import time
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from beast_mode.deployment.config_manager import (
    ConfigManager,
    DeploymentConfig,
    RedisConfig,
    AgentConfig,
    MonitoringConfig,
    DeploymentEnvironment,
)
from beast_mode.deployment.deployment_manager import DeploymentManager
from beast_mode.deployment.service_monitor import ServiceMonitor, MonitoredService
from beast_mode.deployment.validator import DeploymentValidator, ValidationLevel


def setup_logging():
    """Setup logging for the demo"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def demo_configuration_management():
    """Demonstrate configuration management"""
    print("\n" + "=" * 60)
    print("CONFIGURATION MANAGEMENT DEMO")
    print("=" * 60)

    # Create config manager
    config_manager = ConfigManager("./demo_config")

    print("\n1. Available environments:")
    environments = config_manager.list_environments()
    for env in environments:
        print(f"   - {env}")

    print("\n2. Development configuration:")
    dev_config = config_manager.get_config("development")
    print(f"   Environment: {dev_config.environment}")
    print(f"   Redis Host: {dev_config.redis.host}:{dev_config.redis.port}")
    print(f"   Agent ID: {dev_config.agent.agent_id}")
    print(f"   Capabilities: {', '.join(dev_config.agent.capabilities)}")
    print(f"   Log Level: {dev_config.agent.log_level}")

    print("\n3. Creating custom configuration:")
    custom_config = DeploymentConfig(
        environment=DeploymentEnvironment.DEVELOPMENT,
        redis=RedisConfig(host="demo-redis", port=6380, password="demo-password"),
        agent=AgentConfig(
            agent_id="demo_agent",
            capabilities=["demo", "example", "testing"],
            log_level="DEBUG",
        ),
        monitoring=MonitoringConfig(
            health_check_interval=15, enable_performance_monitoring=True
        ),
    )

    # Save custom configuration
    config_manager.save_config("demo", custom_config)
    print("   Custom configuration saved as 'demo'")

    print("\n4. Validating configuration:")
    issues = config_manager.validate_config(custom_config)
    if issues:
        print("   Issues found:")
        for issue in issues:
            print(f"     - {issue}")
    else:
        print("   Configuration is valid!")

    print("\n5. Environment variables:")
    env_vars = config_manager.get_environment_variables("demo")
    for key, value in list(env_vars.items())[:5]:  # Show first 5
        print(f"   {key}={value}")
    print(f"   ... and {len(env_vars) - 5} more")

    return config_manager


def demo_single_machine_deployment(config_manager):
    """Demonstrate single machine deployment"""
    print("\n" + "=" * 60)
    print("SINGLE MACHINE DEPLOYMENT DEMO")
    print("=" * 60)

    deployment_manager = DeploymentManager(config_manager)

    print("\n1. Creating single machine deployment...")

    # Note: This would normally start actual processes
    # For demo purposes, we'll mock the process creation
    from unittest.mock import patch, Mock

    with patch("subprocess.Popen") as mock_popen:
        # Mock successful process creation
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.poll.return_value = None  # Process is running
        mock_popen.return_value = mock_process

        deployment_id = deployment_manager.create_single_machine_deployment("demo")
        print(f"   Deployment created: {deployment_id}")

        print("\n2. Deployment status:")
        status = deployment_manager.get_deployment_status(deployment_id)
        print(f"   ID: {status.deployment_id}")
        print(f"   Type: {status.type}")
        print(f"   Environment: {status.environment}")
        print(f"   Status: {status.status}")
        print(f"   Started: {status.started_at}")

        print("\n3. Services:")
        for service_name, service_info in status.services.items():
            print(f"   - {service_name}: {service_info.get('status', 'unknown')}")
            if "pid" in service_info and service_info["pid"]:
                print(f"     PID: {service_info['pid']}")

        print("\n4. Health check:")
        with (
            patch("psutil.Process"),
            patch("psutil.cpu_percent"),
            patch("psutil.virtual_memory"),
            patch("psutil.disk_usage"),
        ):

            health = deployment_manager.health_check_deployment(deployment_id)
            print(f"   Overall status: {health['overall_status']}")
            print(
                f"   System CPU: {health['system_resources'].get('cpu_percent', 0):.1f}%"
            )
            print(
                f"   System Memory: {health['system_resources'].get('memory_percent', 0):.1f}%"
            )

        print("\n5. Stopping deployment...")
        deployment_manager.stop_deployment(deployment_id)

        final_status = deployment_manager.get_deployment_status(deployment_id)
        print(f"   Final status: {final_status.status}")

    return deployment_manager


def demo_distributed_deployment(config_manager):
    """Demonstrate distributed deployment"""
    print("\n" + "=" * 60)
    print("DISTRIBUTED DEPLOYMENT DEMO")
    print("=" * 60)

    deployment_manager = DeploymentManager(config_manager)

    print("\n1. Creating distributed deployment...")
    nodes = ["node1.example.com", "node2.example.com", "node3.example.com"]
    print(f"   Target nodes: {', '.join(nodes)}")

    deployment_id = deployment_manager.create_distributed_deployment("demo", nodes)
    print(f"   Deployment created: {deployment_id}")

    print("\n2. Deployment manifest:")
    manifest_file = f"deployment_{deployment_id}.json"
    if os.path.exists(manifest_file):
        import json

        with open(manifest_file, "r") as f:
            manifest = json.load(f)

        print(f"   Manifest file: {manifest_file}")
        print(f"   Services: {len(manifest['services'])}")

        print("\n3. Service distribution:")
        for service_name, service_info in manifest["services"].items():
            print(f"   - {service_name} -> {service_info['node']}")

        # Cleanup
        os.remove(manifest_file)
        print(f"\n   Cleaned up manifest file: {manifest_file}")

    return deployment_manager


def demo_docker_deployment(config_manager):
    """Demonstrate Docker deployment"""
    print("\n" + "=" * 60)
    print("DOCKER DEPLOYMENT DEMO")
    print("=" * 60)

    deployment_manager = DeploymentManager(config_manager)

    print("\n1. Creating Docker deployment...")
    deployment_id = deployment_manager.create_docker_deployment("demo")
    print(f"   Deployment created: {deployment_id}")

    print("\n2. Generated files:")
    compose_file = f"docker-compose-{deployment_id}.yml"
    env_file = f".env-{deployment_id}"

    if os.path.exists(compose_file):
        print(f"   Docker Compose: {compose_file}")

        # Show compose file structure
        import yaml

        with open(compose_file, "r") as f:
            compose_content = yaml.safe_load(f)

        print(f"   Services: {', '.join(compose_content['services'].keys())}")

        # Show Redis service config
        redis_config = compose_content["services"]["redis"]
        print(f"   Redis image: {redis_config['image']}")
        print(f"   Redis ports: {redis_config['ports']}")

    if os.path.exists(env_file):
        print(f"   Environment file: {env_file}")

        with open(env_file, "r") as f:
            env_lines = f.readlines()[:5]  # Show first 5 lines

        print("   Environment variables:")
        for line in env_lines:
            print(f"     {line.strip()}")
        print(f"     ... and {len(open(env_file).readlines()) - 5} more")

    print("\n3. Docker commands:")
    print(f"   Start: docker-compose -f {compose_file} --env-file {env_file} up -d")
    print(f"   Stop:  docker-compose -f {compose_file} down")
    print(f"   Logs:  docker-compose -f {compose_file} logs -f")

    # Cleanup
    for file in [compose_file, env_file]:
        if os.path.exists(file):
            os.remove(file)
            print(f"\n   Cleaned up: {file}")

    return deployment_manager


def demo_service_monitoring(config_manager):
    """Demonstrate service monitoring"""
    print("\n" + "=" * 60)
    print("SERVICE MONITORING DEMO")
    print("=" * 60)

    config = config_manager.get_config("demo")
    monitor = ServiceMonitor(config)

    print("\n1. Creating monitored service...")
    service = MonitoredService(
        name="demo_service",
        command=[
            "python",
            "-c",
            "import time; print('Demo service running'); time.sleep(5)",
        ],
        working_directory=".",
        environment={"DEMO": "true"},
        auto_restart=False,  # Disable for demo
        health_check_command=["echo", "healthy"],
    )

    monitor.add_service(service)
    print(f"   Service added: {service.name}")
    print(f"   Command: {' '.join(service.command)}")
    print(f"   Auto-restart: {service.auto_restart}")

    print("\n2. Service configuration:")
    print(f"   Max restarts: {service.max_restarts}")
    print(f"   Restart delay: {service.restart_delay}s")
    print(
        f"   Health check: {' '.join(service.health_check_command) if service.health_check_command else 'None'}"
    )

    print("\n3. Starting service (simulated)...")
    from unittest.mock import patch, Mock

    with patch("subprocess.Popen") as mock_popen:
        mock_process = Mock()
        mock_process.pid = 54321
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process

        success = monitor.start_service("demo_service")
        print(f"   Start result: {'Success' if success else 'Failed'}")

        if success:
            status = monitor.get_service_status("demo_service")
            print(f"   Status: {status.status}")
            print(f"   PID: {status.pid}")
            print(f"   Restart count: {status.metrics.restart_count}")

    print("\n4. Service metrics (simulated):")
    with patch("psutil.Process") as mock_psutil:
        mock_proc = Mock()
        mock_proc.cpu_percent.return_value = 12.5
        mock_proc.memory_percent.return_value = 8.3
        mock_proc.memory_info.return_value = Mock(rss=1024 * 1024 * 25)  # 25MB
        mock_proc.open_files.return_value = [1, 2, 3]
        mock_proc.connections.return_value = [1]
        mock_psutil.return_value = mock_proc

        monitor._update_service_metrics(service)

        print(f"   CPU: {service.metrics.cpu_percent}%")
        print(
            f"   Memory: {service.metrics.memory_percent}% ({service.metrics.memory_mb:.1f}MB)"
        )
        print(f"   Open files: {service.metrics.open_files}")
        print(f"   Connections: {service.metrics.connections}")

    print("\n5. Exporting metrics...")
    metrics_file = "demo_metrics.json"
    monitor.export_metrics(metrics_file)

    if os.path.exists(metrics_file):
        import json

        with open(metrics_file, "r") as f:
            metrics_data = json.load(f)

        print(f"   Metrics exported to: {metrics_file}")
        print(f"   Timestamp: {metrics_data['timestamp']}")
        print(f"   Services: {len(metrics_data['services'])}")

        # Cleanup
        os.remove(metrics_file)
        print(f"   Cleaned up: {metrics_file}")

    # Cleanup monitor
    monitor.cleanup()

    return monitor


def demo_deployment_validation(config_manager):
    """Demonstrate deployment validation"""
    print("\n" + "=" * 60)
    print("DEPLOYMENT VALIDATION DEMO")
    print("=" * 60)

    validator = DeploymentValidator(config_manager)

    print("\n1. Running basic validation...")

    # Mock all external dependencies for demo
    from unittest.mock import patch, Mock

    with (
        patch("socket.socket") as mock_socket,
        patch("redis.Redis") as mock_redis,
        patch("subprocess.run") as mock_run,
        patch("os.path.exists") as mock_exists,
    ):

        # Mock successful connectivity
        mock_sock = Mock()
        mock_sock.connect_ex.return_value = 0
        mock_socket.return_value = mock_sock

        # Mock successful Redis
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.set.return_value = True
        mock_client.get.return_value = b"test_value"
        mock_client.delete.return_value = 1
        mock_client.publish.return_value = 1

        # Mock pub/sub
        mock_pubsub = Mock()
        mock_pubsub.get_message.side_effect = [
            {"type": "subscribe"},
            {"type": "message", "data": b"test"},
        ]
        mock_client.pubsub.return_value = mock_pubsub
        mock_redis.return_value = mock_client

        # Mock process check
        mock_run.return_value = Mock(returncode=0, stdout="12345\n")

        # Mock file existence
        mock_exists.return_value = True

        # Run validation
        report = validator.validate_deployment(
            "demo_deployment", "demo", ValidationLevel.STANDARD
        )

        print(f"   Deployment ID: {report.deployment_id}")
        print(f"   Environment: {report.environment}")
        print(f"   Validation level: {report.validation_level}")
        print(f"   Overall result: {'PASSED' if report.overall_passed else 'FAILED'}")
        print(f"   Total checks: {report.total_checks}")
        print(f"   Passed: {report.passed_checks}")
        print(f"   Failed: {report.failed_checks}")
        print(f"   Duration: {report.total_duration_ms:.0f}ms")

        print("\n2. Validation results:")
        for i, result in enumerate(report.results[:5], 1):  # Show first 5
            status = "✓" if result.passed else "✗"
            print(f"   {status} {result.name}")
            if not result.passed:
                print(f"     Error: {result.message}")

        if len(report.results) > 5:
            print(f"   ... and {len(report.results) - 5} more checks")

        print("\n3. Generating HTML report...")
        report_file = "demo_validation_report.html"
        validator.generate_report_html(report, report_file)

        if os.path.exists(report_file):
            print(f"   Report generated: {report_file}")

            # Show file size
            file_size = os.path.getsize(report_file)
            print(f"   File size: {file_size} bytes")

            # Cleanup
            os.remove(report_file)
            print(f"   Cleaned up: {report_file}")

    return validator


def demo_complete_workflow():
    """Demonstrate complete deployment workflow"""
    print("\n" + "=" * 60)
    print("COMPLETE WORKFLOW DEMO")
    print("=" * 60)

    print("\n1. Initialize components...")
    config_manager = ConfigManager("./demo_workflow_config")
    deployment_manager = DeploymentManager(config_manager)
    validator = DeploymentValidator(config_manager)

    print("\n2. Create and validate configuration...")
    config = config_manager.get_config("development")
    config.agent.agent_id = "workflow_demo_agent"
    config.agent.capabilities = ["workflow", "demo", "complete"]

    issues = config_manager.validate_config(config)
    print(f"   Configuration issues: {len(issues)}")

    print("\n3. Deploy system...")
    from unittest.mock import patch, Mock

    with patch("subprocess.Popen") as mock_popen:
        mock_process = Mock()
        mock_process.pid = 99999
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process

        deployment_id = deployment_manager.create_single_machine_deployment(
            "development"
        )
        print(f"   Deployment ID: {deployment_id}")

        print("\n4. Monitor deployment...")
        status = deployment_manager.get_deployment_status(deployment_id)
        print(f"   Status: {status.status}")
        print(f"   Services: {len(status.services)}")

        print("\n5. Validate deployment...")
        with (
            patch("socket.socket"),
            patch("redis.Redis"),
            patch("subprocess.run"),
            patch("os.path.exists"),
        ):

            report = validator.validate_deployment(
                deployment_id, "development", ValidationLevel.BASIC
            )
            print(f"   Validation: {'PASSED' if report.overall_passed else 'FAILED'}")
            print(f"   Checks: {report.passed_checks}/{report.total_checks}")

        print("\n6. Cleanup...")
        deployment_manager.stop_deployment(deployment_id)
        print(f"   Deployment stopped")

    # Cleanup config directory
    import shutil

    if os.path.exists("./demo_workflow_config"):
        shutil.rmtree("./demo_workflow_config")
        print("   Configuration directory cleaned up")

    print("\n✓ Complete workflow demonstration finished!")


def main():
    """Main demo function"""
    setup_logging()

    print("Beast Mode Deployment System Demo")
    print("=" * 60)
    print("This demo showcases the complete deployment and configuration")
    print("management system for the Beast Mode Agent Collaboration Network.")

    try:
        # Run all demos
        config_manager = demo_configuration_management()
        demo_single_machine_deployment(config_manager)
        demo_distributed_deployment(config_manager)
        demo_docker_deployment(config_manager)
        demo_service_monitoring(config_manager)
        demo_deployment_validation(config_manager)
        demo_complete_workflow()

        print("\n" + "=" * 60)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nKey features demonstrated:")
        print("✓ Configuration management with validation")
        print("✓ Single machine deployment")
        print("✓ Distributed deployment with manifests")
        print("✓ Docker deployment with Compose")
        print("✓ Service monitoring and metrics")
        print("✓ Deployment validation and reporting")
        print("✓ Complete deployment lifecycle")

        print("\nNext steps:")
        print("- Run actual deployments using the scripts in scripts/")
        print("- Customize configurations for your environment")
        print("- Set up monitoring and alerting")
        print("- Integrate with your CI/CD pipeline")

    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    finally:
        # Cleanup any remaining demo files
        cleanup_files = [
            "./demo_config",
            "demo_metrics.json",
            "demo_validation_report.html",
        ]

        for item in cleanup_files:
            if os.path.exists(item):
                if os.path.isdir(item):
                    import shutil

                    shutil.rmtree(item)
                else:
                    os.remove(item)

    return 0


if __name__ == "__main__":
    sys.exit(main())
