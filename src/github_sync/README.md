# GitHub Synchronization Module

This module provides comprehensive GitHub integration for the Beast Mode AI Development Framework, enabling bidirectional synchronization of repository data, issues, pull requests, and collaborative features while maintaining security best practices.

## Features

- **Secure Authentication**: Environment variable-based credential management with zero tolerance for hardcoded secrets
- **Comprehensive Synchronization**: Repository metadata, issues, pull requests, commits, and branches
- **Real-time Updates**: Webhook integration for immediate synchronization
- **Intelligent Caching**: Local storage with offline access capabilities
- **Rate Limit Handling**: Automatic rate limit detection and exponential backoff
- **Conflict Resolution**: Configurable strategies for handling data conflicts
- **Monitoring & Observability**: Detailed logging and metrics collection

## Quick Start

### 1. Set Up Credentials

Create a GitHub Personal Access Token at https://github.com/settings/tokens and set it as an environment variable:

```bash
export GITHUB_TOKEN=ghp_your_token_here
```

Or create a `~/.env` file:

```bash
# ~/.env
GITHUB_TOKEN=ghp_your_token_here
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here  # Optional
```

### 2. Basic Usage

```python
from src.github_sync import GitHubConfig, AuthenticationManager, GitHubAPIClient

# Load configuration from environment
config = GitHubConfig.from_env()

# Test authentication
auth_manager = AuthenticationManager()
auth_manager.load_credentials()

if auth_manager.validate_token():
    print("✓ Authentication successful")
    
    # Get token information
    token_info = auth_manager.get_token_info()
    print(f"User: {token_info['user']['login']}")
else:
    print("✗ Authentication failed")
```

### 3. Command Line Interface

```bash
# Test authentication
python -m src.github_sync.cli auth test

# Validate configuration
python -m src.github_sync.cli config validate

# Show system status
python -m src.github_sync.cli status
```

## Security Requirements

**CRITICAL**: This module enforces zero tolerance for hardcoded credentials. All sensitive data MUST be loaded from environment variables only.

### Required Environment Variables

- `GITHUB_TOKEN`: GitHub Personal Access Token (required)
- `GITHUB_WEBHOOK_SECRET`: Webhook secret for signature validation (optional)
- `GITHUB_APP_ID`: GitHub App ID for app-based authentication (optional)
- `GITHUB_APP_PRIVATE_KEY`: GitHub App private key (optional)

### Security Best Practices

1. **Never hardcode credentials** in source code
2. **Use environment variables** for all sensitive data
3. **Validate tokens** before use
4. **Implement proper error handling** for authentication failures
5. **Use HTTPS** for all API communications

## Architecture

The module is organized into several key components:

- **`models.py`**: Core data structures for GitHub entities
- **`config.py`**: Configuration management with secure credential handling
- **`auth.py`**: Authentication manager with token validation
- **`client.py`**: GitHub API client with rate limiting
- **`sync.py`**: Synchronization engine for data consistency
- **`cache.py`**: Local caching and data persistence
- **`webhooks.py`**: Real-time webhook event processing
- **`cli.py`**: Command-line interface

## Configuration

### Repository Configuration

```python
from src.github_sync import RepositoryConfig, SyncConfig

# Configure a repository for synchronization
repo_config = RepositoryConfig(
    owner="your-org",
    name="your-repo",
    sync_issues=True,
    sync_pull_requests=True,
    sync_branches=["main", "develop"],
    webhook_events=["push", "issues", "pull_request"]
)

# Global sync configuration
sync_config = SyncConfig(
    repositories=[repo_config],
    sync_interval=300,  # 5 minutes
    enable_webhooks=True,
    cache_retention_days=30
)
```

### Environment Configuration

```bash
# Basic configuration
GITHUB_TOKEN=ghp_your_token_here

# Advanced configuration
GITHUB_API_BASE_URL=https://api.github.com
GITHUB_SYNC_INTERVAL=300
GITHUB_MAX_CONCURRENT_SYNCS=5
GITHUB_ENABLE_WEBHOOKS=true
```

## Development Status

This module is currently under development. The following tasks are planned:

- [x] **Task 1**: Project structure and core interfaces ✓
- [ ] **Task 2**: Secure authentication manager
- [ ] **Task 3**: GitHub API client with rate limiting
- [ ] **Task 4**: Synchronization engine
- [ ] **Task 5**: Local cache and data persistence
- [ ] **Task 6**: Webhook integration system
- [ ] **Task 7**: Collaborative features integration
- [ ] **Task 8**: Configuration and customization
- [ ] **Task 9**: Monitoring and observability
- [ ] **Task 10**: Git commit management
- [ ] **Task 11**: Error handling and recovery
- [ ] **Task 12**: CLI and user interfaces
- [ ] **Task 13**: Testing and validation

## Testing

Run the basic tests to validate the implementation:

```bash
# Run basic tests
python -m pytest tests/test_github_sync_basic.py -v

# Run with coverage
python -m pytest tests/test_github_sync_basic.py --cov=src.github_sync
```

## Error Handling

The module provides comprehensive error handling for common scenarios:

- **Authentication Errors**: Invalid or expired tokens
- **Rate Limiting**: Automatic backoff and retry
- **Network Errors**: Connection timeouts and failures
- **Data Conflicts**: Configurable resolution strategies
- **Webhook Failures**: Event queuing and retry mechanisms

## Monitoring

The module includes built-in monitoring capabilities:

- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Metrics Collection**: Sync performance, API usage, cache efficiency
- **Health Monitoring**: System status and connectivity checks
- **Rate Limit Tracking**: API usage and remaining quota

## Contributing

When contributing to this module, please ensure:

1. **Security compliance**: No hardcoded credentials
2. **Environment variables**: Use secure credential management
3. **Error handling**: Comprehensive error handling and recovery
4. **Testing**: Include tests for new functionality
5. **Documentation**: Update documentation for changes

## License

This module is part of the Beast Mode AI Development Framework and follows the same licensing terms.