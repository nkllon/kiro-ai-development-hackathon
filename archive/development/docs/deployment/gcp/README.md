# Research CMA System - GCP Cloud Run Deployment

## Quick Start

### One-Command Deployment
```bash
./deployment/gcp/deploy.sh your-project-id us-central1 dev
```

### Prerequisites
- Google Cloud SDK installed and authenticated
- Docker installed (for local testing)
- Terraform installed (optional, for infrastructure as code)

## Architecture

```
Research CMA on GCP Cloud Run
├── Cloud Run Service (Auto-scaling web app)
├── Cloud SQL PostgreSQL (Managed database)
├── Cloud Storage (Document storage)
├── Secret Manager (Secure configuration)
└── Cloud Build (CI/CD pipeline)
```

## Cost Optimization

### Serverless Benefits
- **Pay-per-request**: Only pay when researchers are using the system
- **Auto-scaling to zero**: No cost when idle
- **Managed services**: No infrastructure maintenance overhead

### Estimated Costs (Monthly)
- **Light usage** (1-2 researchers): $10-30
- **Medium usage** (5-10 researchers): $30-80  
- **Heavy usage** (20+ researchers): $80-200

### Cost Monitoring Integration
The system integrates with your existing Beast Mode GCP billing monitoring:
- Tracks Cloud Run request costs ($0.000024/request)
- Monitors CPU and memory usage costs
- Provides real-time cost correlation analysis

## Deployment Options

### Option 1: One-Click Script (Recommended)
```bash
# Deploy to development environment
./deployment/gcp/deploy.sh your-project-id us-central1 dev

# Deploy to production environment  
./deployment/gcp/deploy.sh your-project-id us-central1 prod
```

### Option 2: Terraform Infrastructure as Code
```bash
cd deployment/gcp/terraform
terraform init
terraform plan -var="project_id=your-project-id"
terraform apply -var="project_id=your-project-id"
```

### Option 3: Manual gcloud Commands
```bash
# Enable APIs
gcloud services enable run.googleapis.com sql-component.googleapis.com

# Create database
gcloud sql instances create research-cms-db --database-version=POSTGRES_14

# Deploy application
gcloud run deploy research-cms --source . --platform managed
```

## Configuration

### Environment Variables
- `PROJECT_ID`: GCP Project ID
- `ENVIRONMENT`: Deployment environment (dev/staging/prod)
- `DB_HOST`: Cloud SQL instance IP
- `DB_NAME`: Database name
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password (from Secret Manager)
- `STORAGE_BUCKET`: Cloud Storage bucket name

### Secrets Management
Database passwords and API keys are stored in Google Secret Manager:
```bash
# View secrets
gcloud secrets list

# Access secret value
gcloud secrets versions access latest --secret="research-cms-db-password"
```

## Monitoring and Logging

### View Application Logs
```bash
gcloud logs tail --follow \
  --resource-type=cloud_run_revision \
  --resource-labels=service_name=research-cms
```

### Monitor Performance
```bash
# Service status
gcloud run services describe research-cms --region=us-central1

# Database status
gcloud sql instances describe research-cms-db
```

### Cost Monitoring
Visit the GCP Console:
- **Billing Reports**: https://console.cloud.google.com/billing/reports
- **Cloud Run Metrics**: https://console.cloud.google.com/run
- **Beast Mode Integration**: Your existing cost dashboard will show Research CMA costs

## Scaling and Performance

### Auto-scaling Configuration
- **Min instances**: 0 (scales to zero when idle)
- **Max instances**: 100 (handles research team collaboration spikes)
- **CPU**: 2 vCPUs per instance
- **Memory**: 2GB per instance

### Database Scaling
- **Tier**: db-f1-micro (1 vCPU, 0.6GB RAM) for development
- **Upgrade**: db-n1-standard-1 (1 vCPU, 3.75GB RAM) for production
- **Connections**: Up to 100 concurrent connections

### Storage Scaling
- **Unlimited**: Cloud Storage scales automatically
- **Versioning**: Enabled for document history
- **Lifecycle**: Automatic cleanup after 365 days

## Security

### Authentication
- Google Cloud IAM for user management
- Service accounts with minimal required permissions
- Secret Manager for sensitive configuration

### Network Security
- HTTPS-only communication
- Private IP for database connections
- VPC integration available for enhanced security

### Data Protection
- Encrypted at rest (Cloud SQL, Cloud Storage)
- Encrypted in transit (TLS 1.2+)
- Automated backups with point-in-time recovery

## Troubleshooting

### Common Issues

#### Deployment Fails
```bash
# Check build logs
gcloud builds log --region=us-central1

# Check service logs
gcloud logs read --resource-type=cloud_run_revision
```

#### Database Connection Issues
```bash
# Test database connectivity
gcloud sql connect research-cms-db --user=research_cms

# Check Cloud SQL proxy
cloud_sql_proxy -instances=PROJECT_ID:us-central1:research-cms-db=tcp:5432
```

#### Permission Issues
```bash
# Check service account permissions
gcloud projects get-iam-policy PROJECT_ID

# Grant missing permissions
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:research-cms@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"
```

## Integration with Existing Infrastructure

### Beast Mode Billing Integration
The Research CMA system automatically integrates with your existing Beast Mode GCP billing monitoring:

```python
# Cost correlation appears in your existing dashboard
💰 Total Cost: $45.67 (LLM: $12.34, GCP: $33.33, Research CMA: $8.50)
🔥 Burn Rate: $8.50/hour (LLM: $2.50, GCP: $6.00, Research CMA: $2.00)
```

### Shared Cloud Run Cluster
- Uses your existing VPC and network configuration
- Leverages shared monitoring and logging infrastructure
- Integrates with existing CI/CD pipelines

## Support

### Documentation
- **GCP Cloud Run**: https://cloud.google.com/run/docs
- **Cloud SQL**: https://cloud.google.com/sql/docs
- **Beast Mode Integration**: See existing Beast Mode documentation

### Monitoring
- **Uptime**: 99.9% SLA with Cloud Run
- **Performance**: Sub-second response times
- **Costs**: Real-time tracking in Beast Mode dashboard