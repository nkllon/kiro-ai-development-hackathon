#!/usr/bin/env python3
"""
Docker Deployment Script for Beast Mode Agent Collaboration Network

This script creates Docker Compose configurations for Beast Mode deployment.
"""

import os
import sys
import argparse
import logging
import subprocess
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from beast_mode.deployment.config_manager import ConfigManager
from beast_mode.deployment.deployment_manager import DeploymentManager
from beast_mode.deployment.validator import DeploymentValidator, ValidationLevel


def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("docker_deployment.log"),
        ],
    )


def check_docker_prerequisites():
    """Check Docker prerequisites"""
    logger = logging.getLogger(__name__)

    # Check if Docker is available
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"Docker found: {result.stdout.strip()}")
        else:
            logger.error("Docker not found or not working")
            return False
    except FileNotFoundError:
        logger.error("Docker not found. Please install Docker.")
        return False

    # Check if Docker Compose is available
    try:
        result = subprocess.run(
            ["docker-compose", "--version"], capture_output=True, text=True
        )
        if result.returncode == 0:
            logger.info(f"Docker Compose found: {result.stdout.strip()}")
        else:
            # Try docker compose (newer syntax)
            result = subprocess.run(
                ["docker", "compose", "version"], capture_output=True, text=True
            )
            if result.returncode == 0:
                logger.info(f"Docker Compose (plugin) found: {result.stdout.strip()}")
            else:
                logger.error("Docker Compose not found")
                return False
    except FileNotFoundError:
        logger.error("Docker Compose not found. Please install Docker Compose.")
        return False

    # Check if Docker daemon is running
    try:
        result = subprocess.run(["docker", "info"], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("Docker daemon is not running. Please start Docker.")
            return False
    except Exception as e:
        logger.error(f"Error checking Docker daemon: {e}")
        return False

    return True


def create_dockerfile():
    """Create Dockerfile for Beast Mode"""
    dockerfile_content = """# Beast Mode Agent Collaboration Network Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY scripts/ ./scripts/

# Create directories
RUN mkdir -p logs spores config data

# Set Python path
ENV PYTHONPATH=/app/src

# Default command (can be overridden)
CMD ["python", "-m", "beast_mode.messaging.bus_client"]
"""

    with open("Dockerfile", "w") as f:
        f.write(dockerfile_content)

    logging.getLogger(__name__).info("Created Dockerfile")


def create_docker_ignore():
    """Create .dockerignore file"""
    dockerignore_content = """# Beast Mode .dockerignore
.git
.gitignore
.DS_Store
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.pytest_cache
.mypy_cache

# Deployment artifacts
deployment_output/
*.pid
logs/*.log
assessment_results/
metrics_data/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
Thumbs.db
ehthumbs.db
Desktop.ini
"""

    with open(".dockerignore", "w") as f:
        f.write(dockerignore_content)

    logging.getLogger(__name__).info("Created .dockerignore")


def deploy_docker(
    environment: str,
    agent_id: str,
    capabilities: list,
    build_image: bool = True,
    start_services: bool = True,
    validate: bool = True,
):
    """Deploy Beast Mode using Docker"""
    logger = logging.getLogger(__name__)

    try:
        # Initialize managers
        config_manager = ConfigManager()
        deployment_manager = DeploymentManager(config_manager)

        logger.info(f"Creating Docker deployment for environment: {environment}")
        logger.info(f"Agent ID: {agent_id}")
        logger.info(f"Capabilities: {', '.join(capabilities)}")

        # Create Docker deployment
        deployment_id = deployment_manager.create_docker_deployment(environment)
        logger.info(f"Docker deployment created with ID: {deployment_id}")

        # Create Dockerfile and .dockerignore if they don't exist
        if not os.path.exists("Dockerfile"):
            create_dockerfile()

        if not os.path.exists(".dockerignore"):
            create_docker_ignore()

        # Build Docker image if requested
        if build_image:
            logger.info("Building Docker image...")
            build_cmd = ["docker", "build", "-t", "beast-mode:latest", "."]

            result = subprocess.run(build_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("Docker image built successfully")
            else:
                logger.error(f"Docker build failed: {result.stderr}")
                raise RuntimeError("Docker build failed")

        # Start services if requested
        if start_services:
            compose_file = f"docker-compose-{deployment_id}.yml"
            env_file = f".env-{deployment_id}"

            logger.info("Starting Docker services...")

            # Use docker-compose or docker compose based on availability
            compose_cmd = ["docker-compose"]
            try:
                subprocess.run(
                    ["docker-compose", "--version"], capture_output=True, check=True
                )
            except (subprocess.CalledProcessError, FileNotFoundError):
                compose_cmd = ["docker", "compose"]

            start_cmd = compose_cmd + [
                "-f",
                compose_file,
                "--env-file",
                env_file,
                "up",
                "-d",
            ]

            result = subprocess.run(start_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("Docker services started successfully")
                logger.info(result.stdout)
            else:
                logger.error(f"Failed to start Docker services: {result.stderr}")
                raise RuntimeError("Failed to start Docker services")

            # Wait for services to be ready
            import time

            logger.info("Waiting for services to be ready...")
            time.sleep(15)

            # Check service status
            status_cmd = compose_cmd + ["-f", compose_file, "ps"]
            result = subprocess.run(status_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("Service status:")
                logger.info(result.stdout)

            # Show logs
            logs_cmd = compose_cmd + ["-f", compose_file, "logs", "--tail=20"]
            result = subprocess.run(logs_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("Recent logs:")
                logger.info(result.stdout)

        # Run validation if requested
        if validate and start_services:
            logger.info("Running deployment validation...")

            # Wait a bit more for services to fully start
            import time

            time.sleep(10)

            validator = DeploymentValidator(config_manager)

            try:
                validation_report = validator.validate_deployment(
                    deployment_id,
                    environment,
                    ValidationLevel.BASIC,  # Use basic validation for Docker
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
                report_file = f"docker_validation_report_{deployment_id}.html"
                validator.generate_report_html(validation_report, report_file)
                logger.info(f"Validation report saved to: {report_file}")

            except Exception as e:
                logger.warning(f"Validation failed: {e}")

        # Create management scripts
        create_management_scripts(deployment_id)

        logger.info("Docker deployment completed successfully!")
        logger.info(f"Deployment ID: {deployment_id}")
        logger.info(f"Compose file: docker-compose-{deployment_id}.yml")
        logger.info(f"Environment file: .env-{deployment_id}")

        if start_services:
            logger.info("Services are running. Use the following commands:")
            logger.info(
                f"  View logs: docker-compose -f docker-compose-{deployment_id}.yml logs -f"
            )
            logger.info(
                f"  Stop services: docker-compose -f docker-compose-{deployment_id}.yml down"
            )
            logger.info(
                f"  Restart services: docker-compose -f docker-compose-{deployment_id}.yml restart"
            )

        return deployment_id

    except Exception as e:
        logger.error(f"Docker deployment failed: {e}")
        raise


def create_management_scripts(deployment_id: str):
    """Create management scripts for the Docker deployment"""
    logger = logging.getLogger(__name__)

    compose_file = f"docker-compose-{deployment_id}.yml"
    env_file = f".env-{deployment_id}"

    # Determine compose command
    compose_cmd = "docker-compose"
    try:
        subprocess.run(["docker-compose", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        compose_cmd = "docker compose"

    # Start script
    start_script = f"""#!/bin/bash
# Start Beast Mode Docker services
# Deployment ID: {deployment_id}

set -e

echo "Starting Beast Mode Docker services..."
{compose_cmd} -f {compose_file} --env-file {env_file} up -d

echo "Waiting for services to be ready..."
sleep 10

echo "Service status:"
{compose_cmd} -f {compose_file} ps

echo "Recent logs:"
{compose_cmd} -f {compose_file} logs --tail=10

echo "Beast Mode services started successfully!"
echo "Use './logs.sh' to view logs"
echo "Use './stop.sh' to stop services"
"""

    with open(f"start_{deployment_id}.sh", "w") as f:
        f.write(start_script)
    os.chmod(f"start_{deployment_id}.sh", 0o755)

    # Stop script
    stop_script = f"""#!/bin/bash
# Stop Beast Mode Docker services
# Deployment ID: {deployment_id}

set -e

echo "Stopping Beast Mode Docker services..."
{compose_cmd} -f {compose_file} down

echo "Beast Mode services stopped."
"""

    with open(f"stop_{deployment_id}.sh", "w") as f:
        f.write(stop_script)
    os.chmod(f"stop_{deployment_id}.sh", 0o755)

    # Logs script
    logs_script = f"""#!/bin/bash
# View Beast Mode Docker service logs
# Deployment ID: {deployment_id}

{compose_cmd} -f {compose_file} logs -f "$@"
"""

    with open(f"logs_{deployment_id}.sh", "w") as f:
        f.write(logs_script)
    os.chmod(f"logs_{deployment_id}.sh", 0o755)

    # Status script
    status_script = f"""#!/bin/bash
# Check Beast Mode Docker service status
# Deployment ID: {deployment_id}

echo "Service status:"
{compose_cmd} -f {compose_file} ps

echo ""
echo "Resource usage:"
docker stats --no-stream $(docker-compose -f {compose_file} ps -q) 2>/dev/null || echo "No running containers"
"""

    with open(f"status_{deployment_id}.sh", "w") as f:
        f.write(status_script)
    os.chmod(f"status_{deployment_id}.sh", 0o755)

    logger.info(f"Created management scripts:")
    logger.info(f"  start_{deployment_id}.sh - Start services")
    logger.info(f"  stop_{deployment_id}.sh - Stop services")
    logger.info(f"  logs_{deployment_id}.sh - View logs")
    logger.info(f"  status_{deployment_id}.sh - Check status")


def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(description="Deploy Beast Mode using Docker")
    parser.add_argument(
        "--environment",
        default="docker",
        help="Deployment environment (default: docker)",
    )
    parser.add_argument(
        "--agent-id",
        default="docker_agent",
        help="Agent identifier (default: docker_agent)",
    )
    parser.add_argument(
        "--capabilities",
        nargs="+",
        default=["docker", "containerization"],
        help="Agent capabilities (default: docker containerization)",
    )
    parser.add_argument(
        "--no-build", action="store_true", help="Skip Docker image build"
    )
    parser.add_argument(
        "--no-start",
        action="store_true",
        help="Don't start services after creating compose file",
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

    logger.info("Starting Beast Mode Docker deployment")

    # Check prerequisites
    if not check_docker_prerequisites():
        logger.error("Docker prerequisites check failed.")
        sys.exit(1)

    try:
        deployment_id = deploy_docker(
            environment=args.environment,
            agent_id=args.agent_id,
            capabilities=args.capabilities,
            build_image=not args.no_build,
            start_services=not args.no_start,
            validate=not args.no_validate,
        )

        logger.info(f"Docker deployment successful: {deployment_id}")

    except Exception as e:
        logger.error(f"Docker deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
