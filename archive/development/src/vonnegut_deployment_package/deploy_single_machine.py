#!/usr/bin/env python3
"""
Single Machine Deployment Script for Beast Mode Agent Collaboration Network

This script deploys the complete Beast Mode system on a single machine,
including Redis, agents, and monitoring.
"""

import os
import sys
import argparse
import logging
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from beast_mode.deployment.config_manager import ConfigManager, DeploymentEnvironment
from beast_mode.deployment.deployment_manager import DeploymentManager
from beast_mode.deployment.service_monitor import ServiceMonitor, MonitoredService
from beast_mode.deployment.validator import DeploymentValidator, ValidationLevel


def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("deployment.log")],
    )


def check_prerequisites():
    """Check system prerequisites"""
    logger = logging.getLogger(__name__)

    # Check if Redis is available
    try:
        import redis

        logger.info("Redis Python client is available")
    except ImportError:
        logger.error("Redis Python client not found. Install with: pip install redis")
        return False

    # Check if Redis server is available
    try:
        import subprocess

        result = subprocess.run(["which", "redis-server"], capture_output=True)
        if result.returncode == 0:
            logger.info(f"Redis server found at: {result.stdout.decode().strip()}")
        else:
            logger.warning(
                "Redis server not found in PATH. Please install Redis server."
            )
            logger.info("On macOS: brew install redis")
            logger.info("On Ubuntu: sudo apt-get install redis-server")
            return False
    except Exception as e:
        logger.error(f"Error checking for Redis server: {e}")
        return False

    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("Python 3.8+ is required")
        return False

    logger.info(f"Python version: {sys.version}")
    return True


def create_directories(config):
    """Create required directories"""
    logger = logging.getLogger(__name__)

    directories = [config.agent.spore_directory, "logs", "config", "data"]

    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.info(f"Created directory: {directory}")


def deploy_single_machine(
    environment: str, agent_id: str, capabilities: list, validate: bool = True
):
    """Deploy Beast Mode on single machine"""
    logger = logging.getLogger(__name__)

    try:
        # Initialize managers
        config_manager = ConfigManager()
        deployment_manager = DeploymentManager(config_manager)

        # Get or create configuration
        try:
            config = config_manager.get_config(environment)
        except ValueError:
            logger.info(f"Creating new configuration for environment: {environment}")
            config = config_manager.get_config("single_machine")
            config.environment = DeploymentEnvironment(environment)
            config.agent.agent_id = agent_id
            config.agent.capabilities = capabilities
            config_manager.save_config(environment, config)

        # Update agent configuration
        config.agent.agent_id = agent_id
        config.agent.capabilities = capabilities

        logger.info(f"Deploying Beast Mode for environment: {environment}")
        logger.info(f"Agent ID: {agent_id}")
        logger.info(f"Capabilities: {', '.join(capabilities)}")

        # Create required directories
        create_directories(config)

        # Create deployment
        deployment_id = deployment_manager.create_single_machine_deployment(environment)
        logger.info(f"Deployment created with ID: {deployment_id}")

        # Wait for services to start
        logger.info("Waiting for services to start...")
        time.sleep(10)

        # Check deployment status
        status = deployment_manager.get_deployment_status(deployment_id)
        logger.info(f"Deployment status: {status.status}")

        for service_name, service_info in status.services.items():
            logger.info(f"  {service_name}: {service_info.get('status', 'unknown')}")

        # Run validation if requested
        if validate:
            logger.info("Running deployment validation...")
            validator = DeploymentValidator(config_manager)

            validation_report = validator.validate_deployment(
                deployment_id, environment, ValidationLevel.STANDARD
            )

            logger.info(
                f"Validation completed: {validation_report.passed_checks}/{validation_report.total_checks} checks passed"
            )

            if not validation_report.overall_passed:
                logger.warning("Some validation checks failed:")
                for result in validation_report.results:
                    if not result.passed:
                        logger.warning(f"  - {result.name}: {result.message}")

            # Generate validation report
            report_file = f"validation_report_{deployment_id}.html"
            validator.generate_report_html(validation_report, report_file)
            logger.info(f"Validation report saved to: {report_file}")

        # Setup service monitoring
        service_monitor = ServiceMonitor(config)

        # Add services to monitor (this would be expanded with actual service definitions)
        logger.info("Setting up service monitoring...")

        # Start monitoring
        service_monitor.start_monitoring()

        logger.info("Deployment completed successfully!")
        logger.info(f"Deployment ID: {deployment_id}")
        logger.info("Services are running and being monitored.")
        logger.info("Press Ctrl+C to stop the deployment.")

        # Keep the script running to maintain the deployment
        try:
            while True:
                time.sleep(30)

                # Periodic health check
                health = deployment_manager.health_check_deployment(deployment_id)
                if health["overall_status"] != "healthy":
                    logger.warning(f"Health check warning: {health}")

        except KeyboardInterrupt:
            logger.info("Shutdown requested...")

            # Cleanup
            service_monitor.cleanup()
            deployment_manager.stop_deployment(deployment_id)
            logger.info("Deployment stopped.")

        return deployment_id

    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        raise


def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(description="Deploy Beast Mode on single machine")
    parser.add_argument(
        "--environment",
        default="development",
        help="Deployment environment (default: development)",
    )
    parser.add_argument(
        "--agent-id",
        default="single_machine_agent",
        help="Agent identifier (default: single_machine_agent)",
    )
    parser.add_argument(
        "--capabilities",
        nargs="+",
        default=["python_coding", "system_administration"],
        help="Agent capabilities (default: python_coding system_administration)",
    )
    parser.add_argument(
        "--no-validate", action="store_true", help="Skip deployment validation"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Log level (default: INFO)",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    logger.info("Starting Beast Mode single machine deployment")

    # Check prerequisites
    if not check_prerequisites():
        logger.error(
            "Prerequisites check failed. Please install required dependencies."
        )
        sys.exit(1)

    try:
        deployment_id = deploy_single_machine(
            environment=args.environment,
            agent_id=args.agent_id,
            capabilities=args.capabilities,
            validate=not args.no_validate,
        )

        logger.info(f"Deployment successful: {deployment_id}")

    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
