"""
Templates Core

This module was extracted from templates.py
as part of RM-DDD compliance refactoring.
"""

import logging
from typing import Dict, List, Optional
from .project_generator import ProjectTemplate, ProjectType, TemplateType

def get_default_project_templates() -> Dict[str, ProjectTemplate]:
    """
    Get all default project templates.
    
    Returns:
        Dict[str, ProjectTemplate]: Available default templates
    """
    templates = {}
    microservice_template = create_microservice_template()
    templates[microservice_template.name] = microservice_template
    web_api_template = create_web_api_template()
    templates[web_api_template.name] = web_api_template
    cli_template = create_cli_tool_template()
    templates[cli_template.name] = cli_template
    library_template = create_library_template()
    templates[library_template.name] = library_template
    event_driven_template = create_event_driven_template()
    templates[event_driven_template.name] = event_driven_template
    return templates

def create_microservice_template() -> ProjectTemplate:
    """Create microservice project template."""
    template = ProjectTemplate('microservice', TemplateType.STANDARD, [ProjectType.MICROSERVICE])
    directories = ['src', 'tests', 'docs', 'deployment', 'config', 'src/domain', 'src/application', 'src/infrastructure', 'src/presentation', 'src/presentation/api', 'src/presentation/health', 'tests/unit', 'tests/integration', 'tests/contract', 'deployment/docker', 'deployment/k8s']
    for directory in directories:
        template.add_directory(directory)
    template.add_file_template('src/presentation/api/main.py', _get_fastapi_main_template())
    template.add_file_template('src/presentation/health/endpoints.py', _get_health_endpoints_template())
    template.add_file_template('deployment/docker/Dockerfile', _get_microservice_dockerfile_template())
    template.add_file_template('deployment/k8s/deployment.yaml', _get_k8s_deployment_template())
    template.add_file_template('deployment/k8s/service.yaml', _get_k8s_service_template())
    template.add_dependency('fastapi', '>=0.95.0')
    template.add_dependency('uvicorn', '>=0.21.0')
    template.add_dependency('pydantic', '>=1.10.0')
    template.add_dependency('prometheus-client', '>=0.16.0')
    return template

def create_web_api_template() -> ProjectTemplate:
    """Create web API project template."""
    template = ProjectTemplate('web_api', TemplateType.STANDARD, [ProjectType.WEB_API])
    directories = ['src', 'tests', 'docs', 'config', 'src/domain', 'src/application', 'src/infrastructure', 'src/presentation', 'src/presentation/api', 'src/presentation/middleware', 'tests/unit', 'tests/integration', 'tests/api']
    for directory in directories:
        template.add_directory(directory)
    template.add_file_template('src/presentation/api/routes.py', _get_api_routes_template())
    template.add_file_template('src/presentation/middleware/auth.py', _get_auth_middleware_template())
    template.add_file_template('src/presentation/middleware/cors.py', _get_cors_middleware_template())
    template.add_dependency('fastapi', '>=0.95.0')
    template.add_dependency('uvicorn', '>=0.21.0')
    template.add_dependency('python-jose', '>=3.3.0')
    template.add_dependency('passlib', '>=1.7.4')
    return template

def create_library_template() -> ProjectTemplate:
    """Create library project template."""
    template = ProjectTemplate('library', TemplateType.STANDARD, [ProjectType.LIBRARY])
    directories = ['src', 'tests', 'docs', 'examples', 'src/domain', 'src/utilities', 'tests/unit', 'tests/integration', 'examples/basic', 'examples/advanced']
    for directory in directories:
        template.add_directory(directory)
    template.add_file_template('src/utilities/helpers.py', _get_library_helpers_template())
    template.add_file_template('examples/basic/usage.py', _get_basic_usage_example_template())
    template.add_file_template('examples/advanced/patterns.py', _get_advanced_patterns_template())
    template.add_dependency('typing-extensions', '>=4.0.0')
    return template

def create_event_driven_template() -> ProjectTemplate:
    """Create event-driven project template."""
    template = ProjectTemplate('event_driven', TemplateType.ENTERPRISE, [ProjectType.EVENT_DRIVEN])
    directories = ['src', 'tests', 'docs', 'config', 'src/domain', 'src/application', 'src/infrastructure', 'src/presentation', 'src/domain/events', 'src/domain/handlers', 'src/domain/sagas', 'src/infrastructure/messaging', 'src/infrastructure/event_store', 'tests/unit', 'tests/integration', 'tests/events']
    for directory in directories:
        template.add_directory(directory)
    template.add_file_template('src/domain/events/base.py', _get_event_base_template())
    template.add_file_template('src/domain/handlers/event_handlers.py', _get_event_handlers_template())
    template.add_file_template('src/domain/sagas/process_manager.py', _get_saga_template())
    template.add_file_template('src/infrastructure/messaging/publisher.py', _get_message_publisher_template())
    template.add_dependency('celery', '>=5.2.0')
    template.add_dependency('redis', '>=4.5.0')
    template.add_dependency('pika', '>=1.3.0')
    return template

def create_custom_project_template(name: str, template_type: TemplateType, supported_types: List[ProjectType], custom_structure: Optional[Dict[str, any]]=None) -> ProjectTemplate:
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
        for directory in custom_structure.get('directories', []):
            template.add_directory(directory)
        for file_path, content in custom_structure.get('files', {}).items():
            template.add_file_template(file_path, content)
        for package, version in custom_structure.get('dependencies', {}).items():
            template.add_dependency(package, version)
        for package, version in custom_structure.get('dev_dependencies', {}).items():
            template.add_dev_dependency(package, version)
    logger.info(f'Created custom template: {name}')
    return template

def _get_fastapi_main_template() -> str:
    """FastAPI main application template."""
    return '"""\nFastAPI main application for {{project_name}}.\n"""\n\nfrom fastapi import FastAPI\nfrom fastapi.middleware.cors import CORSMiddleware\n\nfrom ..domain import create_bounded_context\nfrom .health.endpoints import health_router\n\napp = FastAPI(\n    title="{{project_name}}",\n    description="{{description}}",\n    version="0.1.0"\n)\n\n# CORS middleware\napp.add_middleware(\n    CORSMiddleware,\n    allow_origins=["*"],\n    allow_credentials=True,\n    allow_methods=["*"],\n    allow_headers=["*"],\n)\n\n# Health endpoints\napp.include_router(health_router, prefix="/health", tags=["health"])\n\n# Initialize domain context\nbounded_context = create_bounded_context()\n\n@app.get("/")\nasync def root():\n    return {"message": "{{project_name}} API", "status": "running"}\n\nif __name__ == "__main__":\n    import uvicorn\n    uvicorn.run(app, host="0.0.0.0", port=8000)\n'

def _get_health_endpoints_template() -> str:
    """Health check endpoints template."""
    return '"""\nHealth check endpoints for microservice monitoring.\n"""\n\nfrom fastapi import APIRouter\nfrom rm_ddd import get_global_registry\n\nhealth_router = APIRouter()\n\n@health_router.get("/")\nasync def health_check():\n    """Basic health check."""\n    return {"status": "healthy", "service": "{{project_name}}"}\n\n@health_router.get("/ready")\nasync def readiness_check():\n    """Readiness check for Kubernetes."""\n    registry = get_global_registry()\n    \n    # Check if all RM components are healthy\n    healthy_modules = await registry.get_healthy_modules()\n    total_modules = await registry.get_all_modules()\n    \n    if len(healthy_modules) == len(total_modules):\n        return {"status": "ready", "modules": len(healthy_modules)}\n    else:\n        return {"status": "not_ready", "healthy": len(healthy_modules), "total": len(total_modules)}\n\n@health_router.get("/metrics")\nasync def metrics():\n    """Prometheus metrics endpoint."""\n    # TODO: Implement Prometheus metrics\n    return {"metrics": "TODO: Implement Prometheus metrics"}\n'

def _get_microservice_dockerfile_template() -> str:
    """Microservice Dockerfile template."""
    return 'FROM python:{{python_version}}-slim\n\nWORKDIR /app\n\n# Install system dependencies\nRUN apt-get update && apt-get install -y \\\n    gcc \\\n    && rm -rf /var/lib/apt/lists/*\n\n# Copy requirements and install Python dependencies\nCOPY pyproject.toml .\nRUN pip install -e .\n\n# Copy source code\nCOPY src/ src/\n\n# Create non-root user\nRUN useradd --create-home --shell /bin/bash app\nUSER app\n\n# Health check\nHEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\\n    CMD curl -f http://localhost:8000/health/ || exit 1\n\nEXPOSE 8000\n\nCMD ["python", "-m", "src.presentation.api.main"]\n'

def _get_k8s_deployment_template() -> str:
    """Kubernetes deployment template."""
    return 'apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: {{project_name}}\n  labels:\n    app: {{project_name}}\nspec:\n  replicas: 3\n  selector:\n    matchLabels:\n      app: {{project_name}}\n  template:\n    metadata:\n      labels:\n        app: {{project_name}}\n    spec:\n      containers:\n      - name: {{project_name}}\n        image: {{project_name}}:latest\n        ports:\n        - containerPort: 8000\n        env:\n        - name: ENV\n          value: "production"\n        livenessProbe:\n          httpGet:\n            path: /health/\n            port: 8000\n          initialDelaySeconds: 30\n          periodSeconds: 10\n        readinessProbe:\n          httpGet:\n            path: /health/ready\n            port: 8000\n          initialDelaySeconds: 5\n          periodSeconds: 5\n        resources:\n          requests:\n            memory: "128Mi"\n            cpu: "100m"\n          limits:\n            memory: "512Mi"\n            cpu: "500m"\n'

def _get_k8s_service_template() -> str:
    """Kubernetes service template."""
    return 'apiVersion: v1\nkind: Service\nmetadata:\n  name: {{project_name}}-service\nspec:\n  selector:\n    app: {{project_name}}\n  ports:\n    - protocol: TCP\n      port: 80\n      targetPort: 8000\n  type: ClusterIP\n'

def _get_api_routes_template() -> str:
    return '"""API routes for {{project_name}}."""\n\nfrom fastapi import APIRouter\n\nrouter = APIRouter()\n\n@router.get("/")\nasync def get_items():\n    return {"items": []}\n'

def _get_auth_middleware_template() -> str:
    return '"""Authentication middleware."""\n\nfrom fastapi import Request, HTTPException\nfrom fastapi.security import HTTPBearer\n\nsecurity = HTTPBearer()\n\nasync def auth_middleware(request: Request, call_next):\n    # TODO: Implement authentication\n    response = await call_next(request)\n    return response\n'

def _get_cors_middleware_template() -> str:
    return '"""CORS middleware configuration."""\n\nfrom fastapi.middleware.cors import CORSMiddleware\n\ndef setup_cors(app):\n    app.add_middleware(\n        CORSMiddleware,\n        allow_origins=["*"],\n        allow_credentials=True,\n        allow_methods=["*"],\n        allow_headers=["*"],\n    )\n'

def _get_cli_main_template() -> str:
    return '"""CLI main entry point for {{project_name}}."""\n\nimport click\nfrom .commands import cli_group\n\n@click.group()\ndef main():\n    """{{project_name}} CLI tool."""\n    pass\n\nmain.add_command(cli_group)\n\nif __name__ == "__main__":\n    main()\n'

def _get_cli_commands_template() -> str:
    return '"""CLI commands for {{project_name}}."""\n\nimport click\n\n@click.group()\ndef cli_group():\n    """{{project_name}} commands."""\n    pass\n\n@cli_group.command()\n@click.argument(\'name\')\ndef hello(name):\n    """Say hello to NAME."""\n    click.echo(f"Hello {name}!")\n'

def _get_cli_config_template() -> str:
    return '"""CLI configuration management."""\n\nimport os\nfrom pathlib import Path\n\nCONFIG_DIR = Path.home() / ".{{project_name}}"\nCONFIG_FILE = CONFIG_DIR / "config.json"\n\ndef ensure_config_dir():\n    CONFIG_DIR.mkdir(exist_ok=True)\n'

def _get_basic_usage_example_template() -> str:
    return '"""Basic usage example for {{project_name}}."""\n\nfrom {{project_name}} import helper_function\n\ndef main():\n    result = helper_function("example data")\n    print(result)\n\nif __name__ == "__main__":\n    main()\n'

def _get_advanced_patterns_template() -> str:
    return '"""Advanced usage patterns for {{project_name}}."""\n\n# TODO: Add advanced usage examples\npass\n'

def _get_event_base_template() -> str:
    return '"""Base event classes for event-driven architecture."""\n\nfrom rm_ddd import DomainEvent\n\nclass BaseBusinessEvent(DomainEvent):\n    """Base class for business events."""\n    pass\n'

def _get_event_handlers_template() -> str:
    return '"""Event handlers for domain events."""\n\nfrom rm_ddd import DomainEventHandler\n\nclass ExampleEventHandler(DomainEventHandler):\n    """Example event handler."""\n    \n    def __init__(self):\n        super().__init__("ExampleEventHandler")\n    \n    async def handle(self, event):\n        # TODO: Implement event handling logic\n        pass\n    \n    def can_handle(self, event_type: str) -> bool:\n        return event_type == "ExampleEvent"\n'

def _get_saga_template() -> str:
    return '"""Process manager/saga for coordinating business processes."""\n\nclass ExampleSaga:\n    """Example saga for coordinating multi-step processes."""\n    \n    def __init__(self):\n        self.state = "initial"\n    \n    async def handle_event(self, event):\n        # TODO: Implement saga logic\n        pass\n'

def _get_message_publisher_template() -> str:
    return '"""Message publisher for event-driven communication."""\n\nclass MessagePublisher:\n    """Publisher for domain events to message broker."""\n    \n    async def publish(self, event):\n        # TODO: Implement message publishing\n        pass\n'
