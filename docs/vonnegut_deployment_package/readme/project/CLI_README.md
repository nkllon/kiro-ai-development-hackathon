# Beast Mode CLI - Network Collaboration Tool

## 🚀 Quick Start

### Installation
```bash
# Make executable
chmod +x bin/beast-mode

# Test CLI
./bin/beast-mode --help

# Install system-wide (optional)
python scripts/install_cli.py
```

### Basic Usage
```bash
# Check network status
beast-mode status

# Share content with network
beast-mode share --file your-document.md --sender-id your_name

# Share a message
beast-mode share --message "Your network message" --sender-id your_name

# Listen to network activity
beast-mode network-listen --timeout 30

# Start collaboration agents
beast-mode start-agents
```

## 🌐 Network Sharing

The Beast Mode CLI enables systematic sharing of content with the development network:

### Share Files
```bash
# Share analysis, feedback, or documentation
beast-mode share --file docs/beast_mode/execution/GKE_HACKATHON_FEEDBACK_BEAST_MODE.md --sender-id reviewer

# Share code examples
beast-mode share --file examples/my_solution.py --sender-id developer

# Share specifications
beast-mode share --file .kiro/specs/my-feature/requirements.md --sender-id architect
```

### Share Messages
```bash
# Quick updates
beast-mode share --message "New deployment pipeline ready for testing" --sender-id devops_lead

# Status updates
beast-mode share --message "Security review complete - no critical issues found" --sender-id security_team

# Announcements
beast-mode share --message "Beast Mode framework v1.0 released!" --sender-id maintainer
```

### Listen to Network
```bash
# Monitor all network activity
beast-mode network-listen

# Filter by content type
beast-mode network-listen --filter-type security

# Different output formats
beast-mode network-listen --output-format json
beast-mode network-listen --output-format text
beast-mode network-listen --output-format markdown  # default
```

## 🤖 Agent Collaboration

### Request Help
```bash
# General help request
beast-mode request-help --description "Need help with Kubernetes deployment"

# Specific capabilities
beast-mode request-help \
  --capability security_analysis \
  --capability code_review \
  --description "Security review needed for authentication module"

# Priority levels
beast-mode request-help \
  --description "Production issue with payment processing" \
  --priority urgent
```

### Agent Management
```bash
# Start all agents
beast-mode start-agents

# Start specific agent types
beast-mode start-agents --agent-type cost
beast-mode start-agents --agent-type deployment
beast-mode start-agents --agent-type quality

# Background mode
beast-mode start-agents --background
```

## 📊 Network Monitoring

### Status Checks
```bash
# Quick status
beast-mode status

# Verbose status with details
beast-mode -v status

# Listen to heartbeats
beast-mode listen --channel beast_mode_heartbeats --timeout 10
```

### Message Monitoring
```bash
# General network traffic
beast-mode listen --channel beast_mode_general

# Help requests
beast-mode listen --channel help_requests

# Direct messages (replace 'your_id' with your sender ID)
beast-mode listen --channel direct_your_id
```

## 🔧 Configuration

### Redis Connection
```bash
# Custom Redis server
beast-mode --redis-host your-redis-server.com --redis-port 6380 status

# Environment variables
export BEAST_MODE_REDIS_HOST=localhost
export BEAST_MODE_REDIS_PORT=6379
```

### Command Aliases
The CLI provides multiple command aliases:
- `beast-mode` - Full command name
- `bm` - Short alias  
- `beast` - Shorter alias

## 🎯 Use Cases

### 1. Hackathon Collaboration
```bash
# Share your project analysis
beast-mode share --file PROJECT_ANALYSIS.md --sender-id team_lead

# Request code review
beast-mode request-help \
  --capability code_review \
  --description "Final review before submission" \
  --priority high

# Monitor team communications
beast-mode network-listen --filter-type hackathon
```

### 2. Code Review Workflow
```bash
# Request systematic review
beast-mode request-help \
  --capability code_quality \
  --capability security_analysis \
  --description "Review authentication module before merge"

# Share review results
beast-mode share --file SECURITY_REVIEW_RESULTS.md --sender-id security_reviewer
```

### 3. DevOps Coordination
```bash
# Share deployment status
beast-mode share --message "Production deployment successful - all services healthy" --sender-id devops

# Request infrastructure help
beast-mode request-help \
  --capability deployment_management \
  --capability monitoring_setup \
  --description "Need help setting up monitoring for new microservice"
```

### 4. Network Learning
```bash
# Listen to learn from network activity
beast-mode network-listen --timeout 300 > network_activity.log

# Share knowledge and insights
beast-mode share --file ../../beast_mode/execution/RM_DDD_CRITICAL_REQUIREMENTS_LESSONS_LEARNED.md --sender-id mentor

# Request mentorship
beast-mode request-help \
  --capability knowledge_sharing \
  --description "New to Beast Mode framework - need guidance on best practices"
```

## 🏆 Beast Mode Principles

The CLI embodies core Beast Mode principles:

- **Systematic Collaboration**: Structured communication over ad-hoc messaging
- **Network Effects**: Every interaction strengthens the entire ecosystem  
- **Requirements-Driven**: Clear, actionable requests and responses
- **Accountability Chains**: Traceable contributions and decisions
- **Physics-Informed**: Realistic expectations, systematic approaches

## 🚀 Advanced Features

### Custom Message Types
```bash
# Send custom messages
beast-mode send-message \
  --message-type direct_message \
  --recipient specific_agent_id \
  --content '{"custom": "data"}' \
  --subject "Custom Integration"
```

### Batch Operations
```bash
# Share multiple files
for file in docs/*.md; do
  beast-mode share --file "$file" --sender-id documentation_team
done

# Monitor multiple channels
beast-mode listen --channel help_requests &
beast-mode listen --channel beast_mode_heartbeats &
beast-mode network-listen &
wait
```

### Integration Examples
```bash
# Git hook integration
#!/bin/bash
# .git/hooks/pre-push
beast-mode request-help \
  --capability code_review \
  --description "Pre-push review for $(git rev-parse --abbrev-ref HEAD)" \
  --sender-id "$(git config user.name)"

# CI/CD integration  
beast-mode share \
  --message "Build #${BUILD_NUMBER} completed successfully" \
  --sender-id ci_system
```

---

**Beast Mode CLI**: Making systematic collaboration as easy as a single command.  
**Network Philosophy**: "We're the glue between humans and AI"  
**Systematic Superiority**: Proven approaches over ad-hoc solutions