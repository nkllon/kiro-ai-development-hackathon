# Cloudflare Custom Error Pages - Automated CLI Deployment

🚀 **Fully automated command-line deployment with progress indicators, logging, and CI/CD integration**

## Features

- ✅ **Interactive Mode**: Rich progress bars and colored output
- ✅ **Silent Mode**: Machine-readable JSON output for CI/CD
- ✅ **Comprehensive Validation**: HTML, size, dependencies, API connectivity
- ✅ **Cloudflare API Integration**: Automated deployment when API supports it
- ✅ **Fallback Instructions**: Manual deployment guidance when API unavailable
- ✅ **Rollback Capabilities**: Version management and quick rollback
- ✅ **CI/CD Ready**: GitHub Actions, Docker, and pipeline integration
- ✅ **Monitoring Integration**: Analytics and performance tracking

## Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/nkllon/observatory.git
cd observatory

# Install dependencies
make install

# Set up environment
export CLOUDFLARE_API_TOKEN="your_api_token_here"
```

### 2. Interactive Deployment

```bash
# Deploy with rich progress indicators
make deploy

# Or use CLI directly
./cloudflare-error-pages-cli.py deploy --interactive
```

### 3. CI/CD Deployment

```bash
# Silent deployment with JSON output
make deploy-ci

# Or use CLI directly
./cloudflare-error-pages-cli.py deploy --silent --output json
```

## CLI Usage

### Basic Commands

```bash
# Interactive deployment
./cloudflare-error-pages-cli.py deploy --interactive

# Silent deployment for scripts
./cloudflare-error-pages-cli.py deploy --silent --output json

# Verify existing deployment
./cloudflare-error-pages-cli.py verify

# Rollback to previous version
./cloudflare-error-pages-cli.py rollback
```

### Advanced Options

```bash
# Deploy to specific zone
./cloudflare-error-pages-cli.py deploy --zone staging.nkllon.com

# Use custom HTML file
./cloudflare-error-pages-cli.py deploy --html-file custom-error.html

# Deploy with custom API token
./cloudflare-error-pages-cli.py deploy --api-token $CUSTOM_TOKEN

# Validation only (no deployment)
./cloudflare-error-pages-cli.py deploy --verify-only
```

### Configuration File

```bash
# Use configuration file
./cloudflare-error-pages-cli.py deploy --config cloudflare-config.yaml
```

## Output Formats

### Interactive Mode
```
🚀 Cloudflare Error Pages Deployment
====================================
[████████████████████████████████] 100% Validating HTML content
[████████████████████████████████] 100% Connecting to Cloudflare API
[██████████████████░░░░░░░░░░░░░░] 70%  Uploading error page content
✅ Deployment completed successfully
```

### Silent Mode (JSON)
```json
{
  "success": true,
  "message": "Deployment completed successfully",
  "details": {
    "zone": "nkllon.com",
    "error_code": 1033,
    "file_size": 23433,
    "validation_results": {
      "html_file_exists": true,
      "file_size_ok": true,
      "api_token_present": true,
      "api_connectivity": true
    }
  },
  "timestamp": "2025-01-27T14:30:00Z",
  "duration": 12.5
}
```

## Makefile Commands

```bash
# Installation and setup
make install          # Install dependencies
make setup-env        # Create environment template

# Deployment
make deploy           # Interactive deployment
make deploy-ci        # CI/CD deployment (silent)
make deploy-config    # Deploy with custom config

# Verification and testing
make verify           # Verify deployment
make verify-detailed  # Detailed verification with JSON
make test             # Full test suite

# Maintenance
make rollback         # Rollback deployment
make backup           # Create backup
make clean            # Clean temporary files

# Development
make dev-validate     # Validate HTML content
make dev-preview      # Open HTML preview

# Monitoring
make monitor-logs     # Monitor deployment logs
make status           # Show deployment status
make info             # Show CLI information

# Docker
make docker-build     # Build Docker image
make docker-deploy    # Deploy via Docker

# CI/CD helpers
make ci-validate      # CI validation
make ci-deploy        # CI deployment
make ci-test          # CI testing
```

## Configuration

### Environment Variables

```bash
# Required
export CLOUDFLARE_API_TOKEN="your_api_token_here"

# Optional
export CLOUDFLARE_ZONE="nkllon.com"
export SLACK_WEBHOOK_URL="your_slack_webhook"
export EMAIL_USERNAME="your_email"
export EMAIL_PASSWORD="your_password"
```

### Configuration File (cloudflare-config.yaml)

```yaml
zone:
  name: "nkllon.com"
  api_token: "${CLOUDFLARE_API_TOKEN}"

error_page:
  error_code: 1033
  html_file: "cloudflare/error-pages/1033-enhanced.html"

deployment:
  interactive_mode: true
  log_level: "INFO"
  max_retries: 3

testing:
  test_domains:
    - "observatory.nkllon.com"
    - "grafana.observatory.nkllon.com"
    - "prometheus.observatory.nkllon.com"
  auto_test: true

monitoring:
  enable_monitoring: true
  target_engagement_rate: 0.6
```

## CI/CD Integration

### GitHub Actions

The repository includes a complete GitHub Actions workflow:

```yaml
# .github/workflows/deploy-error-pages.yml
name: Deploy Cloudflare Error Pages

on:
  push:
    branches: [ main, develop ]
  workflow_dispatch:

jobs:
  validate:
    # Validation job
  deploy-staging:
    # Staging deployment
  deploy-production:
    # Production deployment
  rollback:
    # Automatic rollback on failure
```

### Required Secrets

```bash
# GitHub repository secrets
CLOUDFLARE_API_TOKEN_STAGING
CLOUDFLARE_API_TOKEN_PRODUCTION
SLACK_WEBHOOK_URL
```

### Docker Deployment

```bash
# Build container
docker build -t cloudflare-error-pages-cli .

# Run deployment
docker run --rm \
  -e CLOUDFLARE_API_TOKEN=$CLOUDFLARE_API_TOKEN \
  -v $(pwd):/workspace \
  cloudflare-error-pages-cli deploy --silent --output json
```

## Validation

The CLI performs comprehensive validation:

### Pre-deployment Checks
- ✅ HTML file exists and is readable
- ✅ File size under 50KB Cloudflare limit
- ✅ Required elements present (lab rat, countdown, etc.)
- ✅ No external dependencies
- ✅ API token present and valid
- ✅ Internet connectivity
- ✅ Zone access permissions

### Content Validation
- ✅ Valid HTML5 structure
- ✅ CSS syntax validation
- ✅ JavaScript syntax validation
- ✅ Accessibility compliance (WCAG 2.1 AA)
- ✅ Performance requirements (<1s load, 60fps)

### Post-deployment Verification
- ✅ Error page displays correctly
- ✅ Interactive features work (countdown, retry)
- ✅ Responsive design on mobile/desktop
- ✅ Cross-browser compatibility

## Monitoring and Analytics

### Built-in Monitoring
- 📊 Cloudflare Analytics integration
- 📈 Performance metrics tracking
- 🔔 Alert configuration
- 📝 Success metrics monitoring

### Success Metrics
- **Error page engagement rate**: Target >60%
- **Average time on page**: Target 15-45 seconds
- **Retry button click rate**: Target >50%
- **Support ticket reduction**: Target >50%

## Troubleshooting

### Common Issues

**API Token Invalid**
```bash
# Check token validity
curl -X GET "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN"
```

**File Too Large**
```bash
# Check file size
ls -lh cloudflare/error-pages/1033-enhanced.html
# Should be < 50KB
```

**Missing Dependencies**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Debug Mode

```bash
# Enable debug logging
./cloudflare-error-pages-cli.py deploy --log-level DEBUG --interactive
```

### Manual Fallback

If API deployment fails, the CLI provides manual instructions:

1. Go to https://dash.cloudflare.com/
2. Select zone: nkllon.com
3. Navigate: Rules → Custom Error Responses
4. Create response for Error 1033
5. Upload HTML content

## Development

### Project Structure
```
├── cloudflare-error-pages-cli.py    # Main CLI tool
├── cloudflare-config.yaml           # Configuration template
├── requirements.txt                 # Python dependencies
├── Makefile                         # Build and deployment commands
├── Dockerfile                       # Container configuration
├── .github/workflows/               # CI/CD workflows
├── cloudflare/error-pages/          # HTML error pages
└── docs/                           # Documentation
```

### Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Run validation: `make ci-validate`
5. Submit pull request

### Testing

```bash
# Run full test suite
make test

# Run specific tests
python3 -m pytest tests/

# Validate HTML content
make dev-validate
```

## Support

- 📧 **Email**: support@nkllon.com
- 💬 **Discord**: Observatory Community
- 🐛 **Issues**: GitHub Issues
- 📖 **Docs**: Internal Wiki

## License

MIT License - see LICENSE file for details.

---

**Ready to deploy!** 🚀

Start with `make install` and then `make deploy` for your first deployment.