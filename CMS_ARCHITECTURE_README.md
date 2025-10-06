# CMS Architecture - Enhanced Implementation

## Overview

The CMS (Content Management System) Architecture provides a comprehensive, stakeholder-centric platform for managing code artifacts, documentation, configurations, and organizational knowledge within the Beast Mode Framework ecosystem.

## Current Status (2025-10-05)

### ✅ Implemented Components

- **Directus CMS Core**: Deployed and operational on localhost:8055
- **PostgreSQL Database**: Healthy backend database with proper schema
- **Redis Cache**: Operational caching layer (v8.2.1) for performance
- **Enhanced Infrastructure**: Docker Compose configuration with all services
- **CMS Search Service**: FastAPI service with Elasticsearch integration
- **Repository Sync Service**: Automated Git repository synchronization
- **Health Monitoring**: Comprehensive health checks for all services
- **Deployment Automation**: Systematic deployment and validation scripts

### ⚠️ Pending Implementation

- **Elasticsearch Deployment**: Search engine infrastructure (configured but not deployed)
- **Custom Schema Extensions**: Stakeholder-specific collections and relationships
- **Stakeholder Dashboards**: Role-specific interfaces for developers, DevOps, executives, architects
- **AI-Powered Features**: Content intelligence and semantic search capabilities
- **Full Repository Integration**: Webhook handlers and automated content processing

## Architecture Components

### Core Services

1. **Directus CMS** (Port 8055)
   - Primary content management platform
   - REST and GraphQL APIs
   - Admin interface for content management
   - Custom extensions and workflows

2. **PostgreSQL Database** (Port 5432)
   - Primary data storage
   - Optimized schema for CMS content
   - Backup and recovery procedures

3. **Redis Cache** (Port 6379)
   - Session management
   - Query result caching
   - Rate limiting storage

4. **Elasticsearch** (Port 9200)
   - Full-text search engine
   - Semantic search capabilities
   - Content indexing and analytics

5. **Kibana** (Port 5601)
   - Search analytics dashboard
   - Elasticsearch management interface
   - Data visualization tools

### Custom Services

6. **CMS Search Service** (Port 8056)
   - FastAPI-based search API
   - Semantic search with sentence transformers
   - Multi-modal search capabilities
   - Stakeholder-specific filtering

7. **Repository Sync Service** (Port 8057)
   - Git webhook handling
   - Automated content extraction
   - Real-time repository synchronization
   - File change monitoring

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Git
- 8GB+ RAM recommended
- 10GB+ disk space

### Deployment

1. **Deploy Enhanced Infrastructure**:
   ```bash
   python scripts/deploy_cms_enhanced.py
   ```

2. **Validate Deployment**:
   ```bash
   python scripts/validate_cms_dag_readiness.py
   ```

3. **Access Services**:
   - Directus CMS: http://localhost:8055
   - Elasticsearch: http://localhost:9200
   - Kibana: http://localhost:5601
   - Search API: http://localhost:8056
   - Sync API: http://localhost:8057

### Manual Deployment

If you prefer manual deployment:

```bash
# Deploy all services
docker compose -f docker-compose.cms-enhanced.yml up -d

# Check service health
docker compose -f docker-compose.cms-enhanced.yml ps

# View logs
docker compose -f docker-compose.cms-enhanced.yml logs -f
```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Database Configuration
DB_PASSWORD=your_secure_password
DIRECTUS_KEY=your_directus_key
DIRECTUS_SECRET=your_directus_secret

# Admin Configuration
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=your_admin_password

# API Configuration
PUBLIC_URL=http://localhost:8055
DIRECTUS_TOKEN=your_api_token

# External Services
GITHUB_TOKEN=your_github_token
EMAIL_SMTP_HOST=your_smtp_host
EMAIL_SMTP_PORT=587
EMAIL_FROM=noreply@yourdomain.com
```

### Service Configuration

Each service can be configured through environment variables or configuration files:

- **Directus**: Configure via environment variables in docker-compose
- **Elasticsearch**: Configure via `elasticsearch.yml` (if needed)
- **Search Service**: Configure via environment variables
- **Sync Service**: Configure via environment variables and webhook setup

## API Documentation

### CMS Search Service (Port 8056)

#### Search Content
```bash
# Text search
curl "http://localhost:8056/search?q=your_query&limit=10"

# Semantic search
curl "http://localhost:8056/search?q=your_query&semantic=true"

# Stakeholder-specific search
curl "http://localhost:8056/search?q=your_query&stakeholder_role=developer"
```

#### Health Check
```bash
curl http://localhost:8056/health
```

### Repository Sync Service (Port 8057)

#### Manual Sync
```bash
curl -X POST http://localhost:8057/sync/repository_name
```

#### Webhook Handler
```bash
curl -X POST http://localhost:8057/webhook \
  -H "Content-Type: application/json" \
  -d @webhook_payload.json
```

#### Sync Status
```bash
curl http://localhost:8057/status/repository_name
```

## Development

### Adding Custom Collections

1. **Access Directus Admin**: http://localhost:8055
2. **Create Collections**: Define stakeholder-specific collections
3. **Set Permissions**: Configure role-based access control
4. **Create Relationships**: Link collections appropriately

### Extending Search Capabilities

1. **Modify Search Service**: Edit `src/cms_search/main.py`
2. **Add Custom Analyzers**: Configure Elasticsearch mappings
3. **Implement New Endpoints**: Add specialized search functionality
4. **Update Documentation**: Document new features

### Repository Integration

1. **Configure Webhooks**: Set up Git repository webhooks
2. **Customize Processing**: Modify content extraction logic
3. **Add File Types**: Extend supported file type processing
4. **Configure Filters**: Set up content classification rules

## Monitoring and Maintenance

### Health Checks

All services provide health check endpoints:

```bash
# Check all services
python scripts/validate_cms_dag_readiness.py

# Individual service checks
curl http://localhost:8055/server/health  # Directus
curl http://localhost:9200/_cluster/health  # Elasticsearch
curl http://localhost:8056/health  # Search Service
curl http://localhost:8057/health  # Sync Service
```

### Logs

View service logs:

```bash
# All services
docker compose -f docker-compose.cms-enhanced.yml logs -f

# Specific service
docker compose -f docker-compose.cms-enhanced.yml logs -f directus
docker compose -f docker-compose.cms-enhanced.yml logs -f elasticsearch
```

### Backup and Recovery

#### Database Backup
```bash
docker exec cms_postgres pg_dump -U directus directus > backup.sql
```

#### Elasticsearch Backup
```bash
curl -X PUT "localhost:9200/_snapshot/backup_repo" -H 'Content-Type: application/json' -d'
{
  "type": "fs",
  "settings": {
    "location": "/usr/share/elasticsearch/backup"
  }
}'
```

#### Directus Configuration Backup
```bash
docker exec cms_directus directus schema snapshot ./snapshots/schema.yaml
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   - Check if ports 8055, 9200, 5601, 8056, 8057 are available
   - Stop conflicting services or change port mappings

2. **Memory Issues**
   - Elasticsearch requires significant memory
   - Increase Docker memory allocation to 8GB+
   - Monitor system resources during deployment

3. **Service Dependencies**
   - Services have startup dependencies
   - Wait for infrastructure services before starting application services
   - Use health checks to verify service readiness

4. **Permission Issues**
   - Ensure Docker has proper permissions
   - Check file system permissions for volumes
   - Verify user permissions for service accounts

### Diagnostic Commands

```bash
# Check Docker resources
docker system df
docker system info

# Check service status
docker compose -f docker-compose.cms-enhanced.yml ps

# Check network connectivity
docker network ls
docker network inspect cms_network

# Check volumes
docker volume ls
docker volume inspect cms_postgres_data
```

## DAG Execution Readiness

The CMS Architecture is designed for DAG (Directed Acyclic Graph) execution. Current readiness status:

### ✅ Ready Components
- Infrastructure foundation (Directus, PostgreSQL, Redis)
- Service architecture and deployment automation
- Health monitoring and validation systems
- Basic search and sync service implementations

### ⚠️ Pending for Full Readiness
- Elasticsearch deployment and configuration
- Custom schema implementation for stakeholder collections
- Complete stakeholder dashboard implementation
- Full AI-powered content intelligence features

### Validation

Run the DAG readiness validation:

```bash
python scripts/validate_cms_dag_readiness.py
```

This will provide a comprehensive readiness score and identify any blocking issues.

## Contributing

1. **Follow Beast Mode Patterns**: Use ReflectiveModule for all components
2. **Maintain Health Checks**: Implement comprehensive health monitoring
3. **Document Changes**: Update specifications and documentation
4. **Test Thoroughly**: Ensure all changes pass validation
5. **Follow Security Best Practices**: Never hardcode credentials

## Support

For issues and questions:

1. **Check Logs**: Review service logs for error details
2. **Run Validation**: Use the readiness validation script
3. **Review Documentation**: Check this README and specification files
4. **Health Checks**: Verify all services are healthy

## License

This CMS Architecture implementation is part of the Beast Mode Framework and follows the project's licensing terms.

---

**Last Updated**: 2025-10-05  
**Version**: 1.1 (Enhanced Infrastructure)  
**Status**: Partially Implemented - Ready for DAG Execution with Infrastructure Completion