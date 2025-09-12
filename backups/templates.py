"""
Template management for RM-DDD project scaffolding.

Provides default project templates and utilities for creating
custom templates for different project types and scenarios.
"""

import logging
from typing import Dict, List, Optional

from .project_generator import ProjectTemplate, ProjectType, TemplateType


logger = logging.getLogger(__name__)


def get_default_project_templates() -> Dict[str, ProjectTemplate]:
    """
    Get all default project templates.
    
    Returns:
        Dict[str, ProjectTemplate]: Available default templates
    """
    templates = {}
    
    # Microservice template
    microservice_template = create_microservice_template()
    templates[microservice_template.name] = microservice_template
    
    # Web API template
    web_api_template = create_web_api_template()
    templates[web_api_template.name] = web_api_template
    
    # CLI tool template
    cli_template = create_cli_tool_template()
    templates[cli_template.name] = cli_template
    
    # Library template
    library_template = create_library_template()
    templates[library_template.name] = library_template
    
    # Event-driven template
    event_driven_template = create_event_driven_template()
    templates[event_driven_template.name] = event_driven_template
    
    return templates


def create_microservice_template() -> ProjectTemplate:
    """Create microservice project template."""
    template = ProjectTemplate(
        "microservice",
        TemplateType.STANDARD,
        [ProjectType.MICROSERVICE]
    )
    
    # Microservice-specific directory structure
    directories = [
        "src", "tests", "docs", "deployment", "config",
        "src/domain", "src/application", "src/infrastructure", "src/presentation",
        "src/presentation/api", "src/presentation/health",
        "tests/unit", "tests/integration", "tests/contract",
        "deployment/docker", "deployment/k8s"
    ]
    
    for directory in directories:
        template.add_directory(directory)
    
    # Microservice-specific files
    template.add_file_template("src/presentation/api/main.py", _get_fastapi_main_template())
    template.add_file_template("src/presentation/health/endpoints.py", _get_health_endpoints_template())
    template.add_file_template("deployment/docker/Dockerfile", _get_microservice_dockerfile_template())
    template.add_file_template("deployment/k8s/deployment.yaml", _get_k8s_deployment_template())
    template.add_file_template("deployment/k8s/service.yaml", _get_k8s_service_template())
    
    # Microservice dependencies
    template.add_dependency("fastapi", ">=0.95.0")
    template.add_dependency("uvicorn", ">=0.21.0")
    template.add_dependency("pydantic", ">=1.10.0")
    template.add_dependency("prometheus-client", ">=0.16.0")
    
    return template


def create_web_api_template() -> ProjectTemplate:
    """Create web API project template."""
    template = ProjectTemplate(
        "web_api",
        TemplateType.STANDARD,
        [ProjectType.WEB_API]
    )
    
    # Web API specific structure
    directories = [
        "src", "tests", "docs", "config",
        "src/domain", "src/application", "src/infrastructure", "src/presentation",
        "src/presentation/api", "src/presentation/middleware",
        "tests/unit", "tests/integration", "tests/api"
    ]
    
    for directory in directories:
        template.add_directory(directory)
    
    # Web API files
    template.add_file_template("src/presentation/api/routes.py", _get_api_routes_template())
    template.add_file_template("src/presentation/middleware/auth.py", _get_auth_middleware_template())
    template.add_file_template("src/presentation/middleware/cors.py", _get_cors_middleware_template())
    
    # Web API dependencies
    template.add_dependency("fastapi", ">=0.95.0")
    template.add_dependency("uvicorn", ">=0.21.0")
    template.add_dependency("python-jose", ">=3.3.0")
    template.add_dependency("passlib", ">=1.7.4")
    
    return template


def create_cli_tool_template() -> ProjectTemplate:
    """Create CLI tool project template."""
    template = ProjectTemplate(
        "cli_tool",
        TemplateType.STANDARD,
        [ProjectType.CLI_TOOL]
    )
    
    # CLI tool structure
    directories = [
        "src", "tests", "docs",
        "src/domain", "src/application", "src/infrastructure", "src/cli",
        "tests/unit", "tests/integration", "tests/cli"
    ]
    
    for directory in directories:
        template.add_directory(directory)
    
    # CLI tool files
    template.add_file_template("src/cli/main.py", _get_cli_main_template())
    template.add_file_template("src/cli/commands.py", _get_cli_commands_template())
    template.add_file_template("src/cli/config.py", _get_cli_config_template())
    
    # CLI dependencies
    template.add_dependency("click", ">=8.0.0")
    template.add_dependency("rich", ">=13.0.0")
    template.add_dependency("typer", ">=0.7.0")
    
    return template


def create_library_template() -> ProjectTemplate:
    """Create library project template."""
    template = ProjectTemplate(
        "library",
        TemplateType.STANDARD,
        [ProjectType.LIBRARY]
    )
    
    # Library structure
    directories = [
        "src", "tests", "docs", "examples",
        "src/domain", "src/utilities",
        "tests/unit", "tests/integration",
        "examples/basic", "examples/advanced"
    ]
    
    for directory in directories:
        template.add_directory(directory)
    
    # Library files
    template.add_file_template("src/utilities/helpers.py", _get_library_helpers_template())
    template.add_file_template("examples/basic/usage.py", _get_basic_usage_example_template())
    template.add_file_template("examples/advanced/patterns.py", _get_advanced_patterns_template())
    
    # Library dependencies (minimal)
    template.add_dependency("typing-extensions", ">=4.0.0")
    
    return template


def create_event_driven_template() -> ProjectTemplate:
    """Create event-driven project template."""
    template = ProjectTemplate(
        "event_driven",
        TemplateType.ENTERPRISE,
        [ProjectType.EVENT_DRIVEN]
    )
    
    # Event-driven structure
    directories = [
        "src", "tests", "docs", "config",
        "src/domain", "src/application", "src/infrastructure", "src/presentation",
        "src/domain/events", "src/domain/handlers", "src/domain/sagas",
        "src/infrastructure/messaging", "src/infrastructure/event_store",
        "tests/unit", "tests/integration", "tests/events"
    ]
    
    for directory in directories:
        template.add_directory(directory)
    
    # Event-driven files
    template.add_file_template("src/domain/events/base.py", _get_event_base_template())
    template.add_file_template("src/domain/handlers/event_handlers.py", _get_event_handlers_template())
    template.add_file_template("src/domain/sagas/process_manager.py", _get_saga_template())
    template.add_file_template("src/infrastructure/messaging/publisher.py", _get_message_publisher_template())
    
    # Event-driven dependencies
    template.add_dependency("celery", ">=5.2.0")
    template.add_dependency("redis", ">=4.5.0")
    template.add_dependency("pika", ">=1.3.0")
    
    return template


def create_custom_project_template(name: str,
                                 template_type: TemplateType,
                                 supported_types: List[ProjectType],
                                 custom_structure: Optional[Dict[str, any]] = None) -> ProjectTemplate:
    """
    Create a custom project template.
    
    Args:
        name: Template name
        template_type: Template type
        supported_types: Supported project types
        custom_structure: Custom structure definition
        
    Returns:
        ProjectTemplate: Custom template
    """
    template = ProjectTemplate(name, template_type, supported_types)
    
    if custom_structure:
        # Add custom directories
        for directory in custom_structure.get('directories', []):
            template.add_directory(directory)
        
        # Add custom files
        for file_path, content in custom_structure.get('files', {}).items():
            template.add_file_template(file_path, content)
        
        # Add custom dependencies
        for package, version in custom_structure.get('dependencies', {}).items():
            template.add_dependency(package, version)
        
        # Add custom dev dependencies
        for package, version in custom_structure.get('dev_dependencies', {}).items():
            template.add_dev_dependency(package, version)
    
    logger.info(f"Created custom template: {name}")
    return template


# Template content functions

def _get_fastapi_main_template() -> str:
    """FastAPI main application template."""
    return '''"""
FastAPI main application for {{project_name}}.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..domain import create_bounded_context
from .health.endpoints import health_router

app = FastAPI(
    title="{{project_name}}",
    description="{{description}}",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health endpoints
app.include_router(health_router, prefix="/health", tags=["health"])

# Initialize domain context
bounded_context = create_bounded_context()

@app.get("/")
async def root():
    return {"message": "{{project_name}} API", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''


def _get_health_endpoints_template() -> str:
    """Health check endpoints template."""
    return '''"""
Health check endpoints for microservice monitoring.
"""

from fastapi import APIRouter
from rm_ddd import get_global_registry

health_router = APIRouter()

@health_router.get("/")
async def health_check():
    """Basic health check."""
    return {"status": "healthy", "service": "{{project_name}}"}

@health_router.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes."""
    registry = get_global_registry()
    
    # Check if all RM components are healthy
    healthy_modules = await registry.get_healthy_modules()
    total_modules = await registry.get_all_modules()
    
    if len(healthy_modules) == len(total_modules):
        return {"status": "ready", "modules": len(healthy_modules)}
    else:
        return {"status": "not_ready", "healthy": len(healthy_modules), "total": len(total_modules)}

@health_router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    # TODO: Implement Prometheus metrics
    return {"metrics": "TODO: Implement Prometheus metrics"}
'''


def _get_microservice_dockerfile_template() -> str:
    """Microservice Dockerfile template."""
    return '''FROM python:{{python_version}}-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY pyproject.toml .
RUN pip install -e .

# Copy source code
COPY src/ src/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health/ || exit 1

EXPOSE 8000

CMD ["python", "-m", "src.presentation.api.main"]
'''


def _get_k8s_deployment_template() -> str:
    """Kubernetes deployment template."""
    return '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{project_name}}
  labels:
    app: {{project_name}}
spec:
  replicas: 3
  selector:
    matchLabels:
      app: {{project_name}}
  template:
    metadata:
      labels:
        app: {{project_name}}
    spec:
      containers:
      - name: {{project_name}}
        image: {{project_name}}:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENV
          value: "production"
        livenessProbe:
          httpGet:
            path: /health/
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
'''


def _get_k8s_service_template() -> str:
    """Kubernetes service template."""
    return '''apiVersion: v1
kind: Service
metadata:
  name: {{project_name}}-service
spec:
  selector:
    app: {{project_name}}
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: ClusterIP
'''


# Additional template functions would be implemented here...
# For brevity, showing key templates only

def _get_api_routes_template() -> str:
    return '''"""API routes for {{project_name}}."""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_items():
    return {"items": []}
'''


def _get_auth_middleware_template() -> str:
    return '''"""Authentication middleware."""

from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def auth_middleware(request: Request, call_next):
    # TODO: Implement authentication
    response = await call_next(request)
    return response
'''


def _get_cors_middleware_template() -> str:
    return '''"""CORS middleware configuration."""

from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
'''


def _get_cli_main_template() -> str:
    return '''"""CLI main entry point for {{project_name}}."""

import click
from .commands import cli_group

@click.group()
def main():
    """{{project_name}} CLI tool."""
    pass

main.add_command(cli_group)

if __name__ == "__main__":
    main()
'''


def _get_cli_commands_template() -> str:
    return '''"""CLI commands for {{project_name}}."""

import click

@click.group()
def cli_group():
    """{{project_name}} commands."""
    pass

@cli_group.command()
@click.argument('name')
def hello(name):
    """Say hello to NAME."""
    click.echo(f"Hello {name}!")
'''


def _get_cli_config_template() -> str:
    return '''"""CLI configuration management."""

import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".{{project_name}}"
CONFIG_FILE = CONFIG_DIR / "config.json"

def ensure_config_dir():
    CONFIG_DIR.mkdir(exist_ok=True)
'''


def _get_library_helpers_template() -> str:
    return '''"""Helper utilities for {{project_name}} library."""

def helper_function(data: str) -> str:
    """Example helper function."""
    return f"Processed: {data}"
'''


def _get_basic_usage_example_template() -> str:
    return '''"""Basic usage example for {{project_name}}."""

from {{project_name}} import helper_function

def main():
    result = helper_function("example data")
    print(result)

if __name__ == "__main__":
    main()
'''


def _get_advanced_patterns_template() -> str:
    return '''"""Advanced usage patterns for {{project_name}}."""

# TODO: Add advanced usage examples
pass
'''


def _get_event_base_template() -> str:
    return '''"""Base event classes for event-driven architecture."""

from rm_ddd import DomainEvent

class BaseBusinessEvent(DomainEvent):
    """Base class for business events."""
    pass
'''


def _get_event_handlers_template() -> str:
    return '''"""Event handlers for domain events."""

from rm_ddd import DomainEventHandler

class ExampleEventHandler(DomainEventHandler):
    """Example event handler."""
    
    def __init__(self):
        super().__init__("ExampleEventHandler")
    
    async def handle(self, event):
        # TODO: Implement event handling logic
        pass
    
    def can_handle(self, event_type: str) -> bool:
        return event_type == "ExampleEvent"
'''


def _get_saga_template() -> str:
    return '''"""Process manager/saga for coordinating business processes."""

class ExampleSaga:
    """Example saga for coordinating multi-step processes."""
    
    def __init__(self):
        self.state = "initial"
    
    async def handle_event(self, event):
        # TODO: Implement saga logic
        pass
'''


def _get_message_publisher_template() -> str:
    return '''"""Message publisher for event-driven communication."""

class MessagePublisher:
    """Publisher for domain events to message broker."""
    
    async def publish(self, event):
        # TODO: Implement message publishing
        pass
'''