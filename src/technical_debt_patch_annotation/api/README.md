# Technical Debt Patch Annotation REST API

This module provides a comprehensive REST API for external integration with the Technical Debt Patch Annotation System. The API enables CRUD operations for patches, webhook support for external notifications, and comprehensive reporting capabilities.

## Features

- **Complete CRUD Operations**: Create, read, update, and delete patch annotations
- **Patch Discovery**: Automated scanning of source files for patch annotations
- **Webhook Support**: Real-time notifications for external systems
- **Comprehensive Reporting**: Generate detailed reports on technical debt status
- **Health Monitoring**: Built-in health checks and metrics endpoints
- **OpenAPI Documentation**: Auto-generated API documentation with Swagger UI

## Requirements Addressed

- **6.1**: Integration with development workflow through REST API
- **6.2**: Code review and CI/CD integration via webhooks and scanning endpoints
- **6.4**: Cleanup task validation through patch lifecycle management
- **6.5**: Technical debt reporting through comprehensive report endpoints

## Quick Start

### Starting the API Server

```python
from src.technical_debt_patch_annotation.api.patch_api import create_api_instance

# Create API instance
api = create_api_instance(host="0.0.0.0", port=8080)

# Start the server
api.start_server()
```

### Command Line Usage

```bash
# Start the API server
python src/technical_debt_patch_annotation/api/patch_api.py --host 0.0.0.0 --port 8080

# Start with debug logging
python src/technical_debt_patch_annotation/api/patch_api.py --debug
```

## API Endpoints

### Health and Monitoring

- `GET /health` - Health check endpoint
- `GET /ready` - Readiness check endpoint  
- `GET /metrics` - Prometheus metrics endpoint
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc API documentation

### Patch Management

- `POST /api/v1/patches` - Create a new patch annotation
- `GET /api/v1/patches/{patch_id}` - Get a specific patch by ID
- `PUT /api/v1/patches/{patch_id}` - Update an existing patch
- `DELETE /api/v1/patches/{patch_id}` - Delete a patch annotation
- `GET /api/v1/patches` - List patches with filtering and pagination

### Patch Discovery

- `POST /api/v1/patches/scan` - Scan files for patch annotations

### Webhook Management

- `POST /api/v1/webhooks` - Register a new webhook
- `GET /api/v1/webhooks` - List all registered webhooks
- `DELETE /api/v1/webhooks/{webhook_id}` - Delete a webhook

### Reporting

- `POST /api/v1/reports/patches` - Generate comprehensive patch reports

## API Usage Examples

### Creating a Patch

```python
import requests

patch_data = {
    "reason": "Temporary workaround for upstream API rate limiting",
    "upstream_issue": "API-ISSUE-456",
    "cleanup_task": "Replace with proper retry mechanism when API v2 available",
    "debt_level": "Medium",
    "bypass_type": "Architecture",
    "component": "data_processor",
    "file_path": "src/data/processor.py",
    "line_start": 45,
    "line_end": 48,
    "expected_resolution": "2024-03-15T00:00:00",
    "validation_criteria": ["API v2 integration tests pass", "Rate limiting removed"],
    "created_by": "developer@example.com",
    "assigned_to": "team-lead@example.com",
    "tags": ["api", "rate-limiting"]
}

response = requests.post("http://localhost:8080/api/v1/patches", json=patch_data)
patch = response.json()
print(f"Created patch: {patch['patch_id']}")
```

### Listing Patches with Filters

```python
import requests

# Get all high-priority patches for a specific component
params = {
    "component": "data_processor",
    "debt_level": "High",
    "limit": 50,
    "offset": 0
}

response = requests.get("http://localhost:8080/api/v1/patches", params=params)
patches = response.json()
print(f"Found {patches['total']} patches")
```

### Scanning Files for Patches

```python
import requests

scan_data = {
    "file_paths": [
        "src/data/processor.py",
        "src/api/handlers.py",
        "src/utils/helpers.py"
    ],
    "include_patterns": ["*.py"],
    "exclude_patterns": ["*test*.py"]
}

response = requests.post("http://localhost:8080/api/v1/patches/scan", json=scan_data)
results = response.json()
print(f"Scanned {results['summary']['files_scanned']} files")
print(f"Found {results['summary']['total_patches_found']} patches")
```

### Registering a Webhook

```python
import requests

webhook_data = {
    "url": "https://your-system.com/webhooks/patches",
    "events": ["patch.created", "patch.updated", "patch.deleted"],
    "secret": "your-webhook-secret",
    "active": True
}

response = requests.post("http://localhost:8080/api/v1/webhooks", json=webhook_data)
webhook = response.json()
print(f"Registered webhook: {webhook['webhook_id']}")
```

### Generating Reports

```python
import requests

report_data = {
    "component_filter": "data_processor",
    "debt_level_filter": "High",
    "date_from": "2024-01-01T00:00:00",
    "date_to": "2024-12-31T23:59:59",
    "include_resolved": False
}

response = requests.post("http://localhost:8080/api/v1/reports/patches", json=report_data)
report = response.json()
print(f"Report generated with {report['summary']['total_patches']} patches")
print(f"Overdue patches: {report['summary']['overdue_patches']}")
```

## Webhook Events

The API supports the following webhook events:

- `patch.created` - Triggered when a new patch is created
- `patch.updated` - Triggered when a patch is updated
- `patch.deleted` - Triggered when a patch is deleted
- `patches.discovered` - Triggered when patches are discovered during scanning

### Webhook Payload Format

```json
{
    "event": "patch.created",
    "timestamp": "2024-01-15T10:30:00Z",
    "webhook_id": "webhook-uuid",
    "data": {
        "patch": {
            "patch_id": "PATCH-ABC123",
            "reason": "Temporary workaround...",
            "component": "data_processor",
            // ... full patch data
        }
    }
}
```

## Integration Examples

### CI/CD Pipeline Integration

```yaml
# .github/workflows/patch-scan.yml
name: Patch Annotation Scan
on: [push, pull_request]

jobs:
  scan-patches:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Scan for patches
        run: |
          curl -X POST "http://patch-api:8080/api/v1/patches/scan" \
            -H "Content-Type: application/json" \
            -d '{
              "file_paths": ["src/**/*.py"],
              "include_patterns": ["*.py"],
              "exclude_patterns": ["*test*.py"]
            }'
```

### Code Review Integration

```python
# Example GitHub webhook handler
from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/github-webhook', methods=['POST'])
def handle_github_webhook():
    if request.json['action'] == 'opened':
        # Scan PR files for patches
        files = [f['filename'] for f in request.json['pull_request']['changed_files']]
        
        scan_response = requests.post('http://patch-api:8080/api/v1/patches/scan', json={
            'file_paths': files
        })
        
        if scan_response.json()['summary']['total_patches_found'] > 0:
            # Add comment to PR about patches found
            pass
    
    return 'OK'
```

## Configuration

### Environment Variables

- `PATCH_API_HOST` - Host to bind the server to (default: "0.0.0.0")
- `PATCH_API_PORT` - Port to bind the server to (default: 8080)
- `PATCH_API_DEBUG` - Enable debug logging (default: False)
- `BEAST_MODE_PROMETHEUS_ENABLED` - Enable Prometheus metrics (default: True)
- `BEAST_MODE_PROMETHEUS_PORT` - Prometheus metrics port (default: 8000)

### Production Deployment

For production deployment, consider:

1. **Persistent Storage**: Replace in-memory storage with a database
2. **Authentication**: Add API key or OAuth authentication
3. **Rate Limiting**: Implement rate limiting for API endpoints
4. **HTTPS**: Use HTTPS for secure communication
5. **Load Balancing**: Deploy multiple instances behind a load balancer

## Error Handling

The API uses standard HTTP status codes:

- `200 OK` - Successful operation
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

Error responses include detailed error information:

```json
{
    "detail": {
        "message": "Patch validation failed",
        "errors": ["Reason field is required and cannot be empty"],
        "warnings": ["No validation criteria specified"]
    }
}
```

## Monitoring and Observability

The API includes comprehensive monitoring capabilities:

- **Health Checks**: `/health` and `/ready` endpoints for load balancer health checks
- **Metrics**: Prometheus metrics at `/metrics` endpoint
- **Tracing**: Operation tracing with correlation IDs
- **Logging**: Structured logging with configurable levels

## Security Considerations

- **Webhook Signatures**: Webhooks include HMAC signatures for verification
- **Input Validation**: All inputs are validated using Pydantic models
- **CORS**: CORS middleware configured (adjust for production)
- **Rate Limiting**: Consider implementing rate limiting for production use

## Development

### Running Tests

```bash
# Run API tests
python -m pytest tests/api/ -v

# Run with coverage
python -m pytest tests/api/ --cov=src/technical_debt_patch_annotation/api
```

### API Documentation

The API automatically generates OpenAPI documentation available at:
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

## Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the health status at `/health`
3. Check logs for error details
4. Consult the comprehensive error messages in API responses