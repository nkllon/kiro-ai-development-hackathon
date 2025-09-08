# Beast Mode CLI Usage Guide

## Installation

### Quick Install
```bash
# From project root
python scripts/install_cli.py

# Or manually
pip install -e .
```

### Verify Installation
```bash
beast-mode --help
bm --help          # Short alias
beast --help       # Shorter alias
```

## Core Commands

### Network Status
```bash
# Check overall network health
beast-mode status

# Verbose output with detailed info
beast-mode -v status
```

### Agent Management
```bash
# Start all collaboration agents
beast-mode start-agents

# Start specific agent types
beast-mode start-agents --agent-type cost
beast-mode start-agents --agent-type deployment
beast-mode start-agents --agent-type quality

# Run agents in background
beast-mode start-agents --background
```

### Communication

#### Request Help
```bash
# Basic help request
beast-mode request-help

# Specific capability requirements
beast-mode request-help --capability cost_optimization --capability deployment

# With priority and custom sender
beast-mode request-help \
  --capability security_analysis \
  --description "Need security review for API endpoints" \
  --priority high \
  --sender-id my_project_lead
```

#### Listen to Network
```bash
# Listen to general channel
beast-mode listen

# Listen to specific channel
beast-mode listen --channel help_requests

# Extended listening with timeout
beast-mode listen --channel beast_mode_heartbeats --timeout 60
```

#### Send Custom Messages
```bash
# Send direct message
beast-mode send-message \
  --recipient cost_optimizer_001 \
  --subject "Budget Review Request" \
  --content '{"project": "web_app", "budget": 5000}'

# Broadcast to general channel
beast-mode send-message \
  --message-type announcement \
  --subject "New deployment pipeline ready" \
  --content '{"pipeline": "v2.0", "features": ["auto-scaling", "monitoring"]}'
```

### Development & Testing

#### Run Demo
```bash
# Quick collaboration demonstration
beast-mode demo
```

## Configuration

### Redis Connection
```bash
# Custom Redis server
beast-mode --redis-host production.redis.com --redis-port 6380 status

# Environment variables
export BEAST_MODE_REDIS_HOST=localhost
export BEAST_MODE_REDIS_PORT=6379
```

### Verbose Output
```bash
# Enable verbose logging for any command
beast-mode -v <command>

# Example: verbose status check
beast-mode -v status
```

## Common Workflows

### 1. Network Health Check
```bash
# Quick health check
beast-mode status

# If no agents running, start them
beast-mode start-agents

# Verify agents are responding
beast-mode listen --channel beast_mode_heartbeats --timeout 10
```

### 2. Request Code Review
```bash
beast-mode request-help \
  --capability code_quality \
  --capability security_analysis \
  --description "Please review authentication module for security vulnerabilities" \
  --priority high
```

### 3. Cost Optimization Analysis
```bash
beast-mode request-help \
  --capability cost_optimization \
  --description "Analyze current AWS infrastructure for cost savings opportunities" \
  --priority normal
```

### 4. Deployment Assistance
```bash
beast-mode request-help \
  --capability deployment \
  --capability monitoring \
  --description "Help with Kubernetes deployment strategy for microservices" \
  --priority urgent
```

### 5. Monitor Network Activity
```bash
# Terminal 1: Listen to all help requests
beast-mode listen --channel help_requests

# Terminal 2: Listen to agent responses
beast-mode listen --channel beast_mode_general

# Terminal 3: Monitor agent health
beast-mode listen --channel beast_mode_heartbeats
```

## Advanced Usage

### Custom Agent Integration
```bash
# Send capability announcement for your custom agent
beast-mode send-message \
  --message-type agent_announcement \
  --sender-id my_custom_agent \
  --content '{
    "agent_name": "Custom Security Scanner",
    "capabilities": ["security_analysis", "vulnerability_scanning"],
    "max_tasks": 5,
    "specializations": ["OWASP", "container_security"]
  }'
```

### Network Debugging
```bash
# Verbose network status
beast-mode -v status

# Listen with full message details
beast-mode -v listen --channel beast_mode_general --timeout 30

# Send test message and monitor response
beast-mode send-message \
  --message-type ping \
  --content '{"test": true}' &
beast-mode listen --timeout 5
```

### Batch Operations
```bash
# Start multiple agent types in parallel
beast-mode start-agents --agent-type cost --background &
beast-mode start-agents --agent-type deployment --background &
beast-mode start-agents --agent-type quality --background &
wait

# Verify all started
beast-mode status
```

## Troubleshooting

### Redis Connection Issues
```bash
# Check Redis is running
redis-cli ping

# Start Redis (macOS)
brew services start redis

# Start Redis (Ubuntu)
sudo systemctl start redis-server

# Manual Redis start
redis-server
```

### Agent Not Responding
```bash
# Check agent status
beast-mode status

# Restart agents
beast-mode start-agents

# Monitor heartbeats
beast-mode listen --channel beast_mode_heartbeats --timeout 15
```

### Permission Issues
```bash
# Reinstall CLI
pip install -e . --force-reinstall

# Check Python path
python -c "import beast_mode; print(beast_mode.__file__)"
```

### Network Debugging
```bash
# Verbose mode for detailed logs
beast-mode -v status
beast-mode -v listen --timeout 10

# Check Redis subscriptions
redis-cli pubsub channels
```

## Integration Examples

### CI/CD Pipeline
```bash
#!/bin/bash
# .github/workflows/beast-mode-review.yml

# Start agents
beast-mode start-agents --background

# Request automated review
beast-mode request-help \
  --capability code_quality \
  --capability security_analysis \
  --description "Automated CI review for PR #${PR_NUMBER}" \
  --priority normal

# Wait for responses
beast-mode listen --channel direct_ci_bot --timeout 300
```

### Development Workflow
```bash
#!/bin/bash
# scripts/dev-review.sh

echo "🔍 Requesting Beast Mode review..."

beast-mode request-help \
  --capability code_quality \
  --capability performance \
  --description "Pre-commit review for $(git branch --show-current)" \
  --sender-id "$(git config user.name)"

echo "👂 Listening for feedback..."
beast-mode listen --channel "direct_$(git config user.name)" --timeout 60
```

## Best Practices

### 1. Descriptive Help Requests
```bash
# ❌ Vague request
beast-mode request-help --description "help with code"

# ✅ Specific request
beast-mode request-help \
  --capability code_quality \
  --description "Review error handling in user authentication module, focusing on input validation and SQL injection prevention"
```

### 2. Appropriate Priorities
- `low`: Nice-to-have improvements, refactoring
- `normal`: Standard development tasks, code reviews
- `high`: Bug fixes, security issues
- `urgent`: Production issues, critical security vulnerabilities

### 3. Network Etiquette
- Use specific capabilities to target the right agents
- Provide clear, actionable descriptions
- Monitor responses and acknowledge help received
- Don't spam the network with duplicate requests

### 4. Monitoring Best Practices
```bash
# Monitor specific channels for your needs
beast-mode listen --channel help_requests &      # See what others need
beast-mode listen --channel direct_your_id &    # Your responses
beast-mode listen --channel beast_mode_heartbeats & # Network health
```

## Command Reference

| Command | Alias | Description |
|---------|-------|-------------|
| `beast-mode` | `bm`, `beast` | Main CLI entry point |
| `start-agents` | - | Start collaboration agents |
| `request-help` | - | Send help request to network |
| `listen` | - | Listen to network channels |
| `send-message` | - | Send custom message |
| `status` | - | Check network status |
| `demo` | - | Run collaboration demo |

### Global Options
- `--redis-host HOST`: Redis server hostname (default: localhost)
- `--redis-port PORT`: Redis server port (default: 6379)
- `--verbose, -v`: Enable verbose output
- `--help`: Show help message

---

**Beast Mode Principle**: "The Requirements ARE the Solution"  
**CLI Philosophy**: Make systematic collaboration as easy as a single command  
**Network Effect**: Every interaction strengthens the entire development ecosystem