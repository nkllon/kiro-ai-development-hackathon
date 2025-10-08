# Devpost Integration Guide

## The Requirements ARE the Solution

Welcome to the Devpost Integration system - where systematic, requirements-driven development meets hackathon success. This guide demonstrates how comprehensive requirements definition becomes the solution architecture itself.

## Quick Start

### Installation

```bash
# Install the devpost integration package
pip install -e .

# Verify installation
devpost --version
```

### Basic Workflow

1. **Connect your project to Devpost**
   ```bash
   devpost connect --project-id YOUR_PROJECT_ID
   ```

2. **Check project status**
   ```bash
   devpost status
   ```

3. **Generate local preview**
   ```bash
   devpost preview --open-browser
   ```

4. **Validate submission requirements**
   ```bash
   devpost validate
   ```

5. **Sync with Devpost**
   ```bash
   devpost sync
   ```

## Core Features

### 🎯 Requirements-Driven Development

Our revolutionary approach where comprehensive requirements definition becomes the solution architecture itself:

- **Systematic Validation**: Every specification becomes executable validation
- **Automatic Quality Gates**: Requirements prevent rework and scope creep
- **Measurable Outcomes**: Clear success criteria from day one

### 🔗 Human-AI Collaboration Bridge

We're the glue between humans and AI:

- **LLMs Need Human Creativity**: AI provides systematic capability, humans provide vision
- **Amplify Don't Replace**: AI agents enhance human teams rather than replace them
- **Systematic Foundation**: Let humans focus on breakthroughs while AI handles the systematic work

### 🔬 Physics-Informed Pragmatism

Increase your odds, save work, pain, and misery:

- **Systematic Approaches**: Improve probability of success over ad-hoc methods
- **Steve Jobs Standard**: "It just works" through systematic design
- **Reality-Based Decisions**: Acknowledge uncertainty while maximizing success probability

## Detailed Usage

### Project Connection

Connect your local project to a Devpost submission:

```bash
# Basic connection
devpost connect --project-id abc123

# Specify custom local path
devpost connect --project-id abc123 --local-path /path/to/project

# Use custom configuration file
devpost connect --project-id abc123 --config-file custom-config.json
```

### Configuration Management

```bash
# View current configuration
devpost config --show

# Set authentication token
devpost config --key auth_token --value YOUR_TOKEN

# Set notification preferences
devpost notifications --enable --deadline-hours 48 --email user@example.com
```

### Multi-Project Management

```bash
# List all connected projects
devpost projects

# Switch between projects
devpost switch PROJECT_ID

# Disconnect a project
devpost disconnect --project-id PROJECT_ID

# Disconnect all projects
devpost disconnect --all
```

### Deadline Tracking

```bash
# Check current project deadlines
devpost deadlines

# View all hackathon deadlines
devpost deadlines --all

# Check specific hackathon
devpost deadlines --hackathon-id HACKATHON_ID
```

### Validation and Quality

```bash
# Validate current project
devpost validate

# Attempt automatic fixes
devpost validate --fix

# Generate detailed preview
devpost preview --output detailed-preview.html
```

### Synchronization

```bash
# Sync current project
devpost sync

# Force sync (ignore change detection)
devpost sync --force

# Dry run (show what would be synced)
devpost sync --dry-run
```

## Configuration

### Project Configuration

The system creates a `.devpost/config.json` file in your project directory:

```json
{
  "project_connections": [
    {
      "project_id": "abc123",
      "local_path": "/path/to/project",
      "remote_url": "https://devpost.com/software/my-project",
      "last_sync": "2024-09-07T10:30:00Z"
    }
  ],
  "notification_settings": {
    "enabled": true,
    "deadline_warning_hours": 24,
    "email_notifications": false,
    "desktop_notifications": true
  },
  "validation_rules": {
    "require_description": true,
    "min_description_length": 100,
    "require_demo_url": true,
    "require_team_members": true
  }
}
```

### Authentication

Set up authentication with your Devpost API token:

```bash
# Method 1: Via CLI
devpost config --key auth_token --value YOUR_TOKEN

# Method 2: Environment variable
export DEVPOST_API_TOKEN=YOUR_TOKEN

# Method 3: Configuration file
echo '{"auth_token": "YOUR_TOKEN"}' > ~/.devpost/auth.json
```

## Advanced Features

### File Monitoring

The system automatically monitors your project files for changes:

- **Documentation Changes**: docs/readme/project/README.md, docs/, etc.
- **Media Files**: Images, videos, presentations
- **Configuration Updates**: package.json, pyproject.toml, etc.
- **Code Changes**: Source files for technology detection

### Preview Generation

Generate local HTML previews that match Devpost's layout:

```bash
# Basic preview
devpost preview

# Custom output file
devpost preview --output my-preview.html

# Open in browser automatically
devpost preview --open-browser
```

The preview includes:
- Project description and metadata
- Team information
- Technology stack detection
- Media file gallery
- Validation results
- Missing field highlighting

### Validation Engine

Comprehensive validation against Devpost requirements:

- **Required Fields**: Title, description, team members
- **Content Quality**: Minimum lengths, formatting
- **Media Requirements**: Screenshots, demo videos
- **Technical Details**: Repository links, demo URLs
- **Submission Deadlines**: Time remaining, requirements checklist

### Notification System

Stay informed about deadlines and status changes:

- **Desktop Notifications**: Native OS notifications
- **Email Alerts**: Optional email notifications
- **Status Changes**: Project submission status updates
- **Deadline Reminders**: Configurable warning thresholds

## Troubleshooting

### Common Issues

#### Authentication Errors
```bash
# Check current authentication status
devpost config --show

# Re-authenticate
devpost config --key auth_token --value NEW_TOKEN
```

#### Network Connectivity
```bash
# Test API connectivity
curl -H "Authorization: Bearer YOUR_TOKEN" https://api.devpost.com/v2/user

# Check firewall settings
# Ensure devpost.com is accessible
```

#### File Permission Issues
```bash
# Check directory permissions
ls -la .devpost/

# Fix permissions if needed
chmod 755 .devpost/
chmod 644 .devpost/config.json
```

#### Validation Failures
```bash
# Get detailed validation report
devpost validate

# Check specific requirements
devpost deadlines

# Generate preview to see missing fields
devpost preview --open-browser
```

### Error Recovery

The system includes automatic error recovery:

- **Retry Logic**: Exponential backoff for network errors
- **Graceful Degradation**: Fallback modes when services are unavailable
- **Data Recovery**: Automatic backup and restore of configuration
- **User Guidance**: Clear error messages with actionable solutions

### Performance Optimization

For large projects:

```bash
# Exclude unnecessary files from monitoring
echo "node_modules/" >> .devpost/ignore
echo "*.log" >> .devpost/ignore

# Use selective sync
devpost sync --files-only

# Generate lightweight preview
devpost preview --minimal
```

## API Reference

### Python API

```python
from devpost_integration import DevpostProjectManager, DevpostSyncManager

# Project management
manager = DevpostProjectManager()
manager.connect_project('project-id', '/path/to/project')
status = manager.get_project_status()

# Synchronization
sync_manager = DevpostSyncManager()
result = sync_manager.sync_project()

# Preview generation
from devpost_integration import DevpostPreviewGenerator
generator = DevpostPreviewGenerator('/path/to/project')
preview = generator.generate_preview()
```

### CLI Integration

```python
import click
from devpost_integration.cli import cli

# Extend CLI with custom commands
@cli.command()
def custom_command():
    """Custom command for project-specific needs."""
    click.echo("Custom functionality")

if __name__ == '__main__':
    cli()
```

## Best Practices

### Project Structure

Organize your project for optimal Devpost integration:

```
your-project/
├── docs/readme/project/README.md              # Main project description
├── docs/                  # Additional documentation
├── media/                 # Screenshots, videos, presentations
├── src/                   # Source code
├── .devpost/              # Devpost integration configuration
│   ├── config.json        # Project configuration
│   └── preview.html       # Generated preview
└── package.json           # Project metadata (if applicable)
```

### Documentation Standards

Follow these guidelines for better Devpost integration:

1. **docs/readme/project/README.md Structure**:
   ```markdown
   # Project Title
   
   Brief tagline (20-50 characters)
   
   ## Description
   
   Detailed description (100+ words)
   
   ## Team
   
   - Team Member 1
   - Team Member 2
   
   ## Technologies
   
   - Technology 1
   - Technology 2
   
   ## Links
   
   - [Demo](https://demo-url.com)
   - [Repository](https://github.com/user/repo)
   ```

2. **Media Organization**:
   - Place screenshots in `media/` or `images/` directory
   - Use descriptive filenames: `dashboard-screenshot.png`
   - Include demo videos: `demo-video.mp4`
   - Add presentation files: `pitch-deck.pdf`

3. **Metadata Consistency**:
   - Keep `package.json` and `pyproject.toml` updated
   - Use consistent project names across files
   - Include proper version numbers

### Workflow Integration

Integrate with your development workflow:

```bash
# Pre-commit hook
echo "devpost validate" >> .git/hooks/pre-commit

# CI/CD integration
# .github/workflows/devpost.yml
name: Devpost Validation
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Validate Devpost Requirements
        run: |
          pip install -e .
          devpost validate
```

## Examples

### Complete Project Setup

```bash
# 1. Initialize new hackathon project
mkdir my-hackathon-project
cd my-hackathon-project

# 2. Create basic project structure
echo "# My Hackathon Project" > docs/readme/project/README.md
mkdir media src docs

# 3. Connect to Devpost
devpost connect --project-id my-project-123

# 4. Configure notifications
devpost notifications --enable --deadline-hours 48

# 5. Generate initial preview
devpost preview --open-browser

# 6. Set up file monitoring (automatic)
# Files are monitored automatically after connection

# 7. Validate and sync
devpost validate
devpost sync
```

### Multi-Project Workflow

```bash
# Manage multiple hackathon projects
devpost projects                    # List all projects
devpost switch project-1           # Switch to project 1
devpost status                     # Check status
devpost switch project-2           # Switch to project 2
devpost deadlines --all           # Check all deadlines
```

### Automated Validation Pipeline

```python
#!/usr/bin/env python3
"""Automated validation and sync pipeline."""

from devpost_integration import (
    DevpostProjectManager, 
    DevpostSyncManager, 
    ValidationEngine
)

def automated_pipeline():
    # Validate project
    validator = ValidationEngine()
    result = validator.validate_current_project()
    
    if not result.is_valid:
        print(f"❌ Validation failed: {len(result.errors)} errors")
        for error in result.errors:
            print(f"  • {error}")
        return False
    
    # Sync if validation passes
    sync_manager = DevpostSyncManager()
    sync_result = sync_manager.sync_project()
    
    if sync_result.success:
        print("✅ Project validated and synced successfully")
        return True
    else:
        print(f"❌ Sync failed: {sync_result.error}")
        return False

if __name__ == '__main__':
    automated_pipeline()
```

## Support

### Getting Help

- **CLI Help**: `devpost --help` or `devpost COMMAND --help`
- **Validation Issues**: `devpost validate` provides detailed feedback
- **Configuration Problems**: `devpost config --show` to inspect settings
- **Error Logs**: Check `.devpost/errors.log` for detailed error information

### Community Resources

- **Documentation**: Full API and CLI documentation
- **Examples**: Sample projects and configuration templates
- **Best Practices**: Proven patterns for hackathon success
- **Troubleshooting**: Common issues and solutions

### The Systematic Advantage

Remember: **The Requirements ARE the Solution**

This system demonstrates that when you systematically define what success looks like, you've already solved most of the problem. Every feature is built with:

- **Clear Acceptance Criteria**: Know exactly what "done" means
- **Systematic Validation**: Automatic verification against requirements
- **Measurable Outcomes**: Track progress toward defined goals
- **Physics-Informed Design**: Increase odds of success, reduce pain and rework

**"It just works"** - because systematic approaches make it work.