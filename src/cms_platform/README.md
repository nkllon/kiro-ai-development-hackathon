# CMS Platform - Directus Implementation

## Overview
Enhanced Directus CMS platform with custom extensions and Beast Mode Framework integration.

## Quick Start

1. Configure environment:
   ```bash
   cd docker
   cp .env.template .env
   # Edit .env with your configuration
   ```

2. Start services:
   ```bash
   docker-compose up -d
   ```

3. Access CMS:
   - Web UI: http://localhost:8055
   - Health Check: http://localhost:8055/server/health

## Architecture

- **Directus CMS**: Core content management platform
- **PostgreSQL**: Primary database
- **Redis**: Caching layer
- **Health Monitoring**: ReflectiveModule-compliant health checks

## Development

See `docs/` for detailed development guidelines.
