# Devpost Hackathon Integration

This module provides seamless integration with Devpost to keep hackathon projects synchronized and up-to-date. It allows developers to manage their hackathon submissions directly from their development environment.

## Features

- **Project Connection**: Connect local projects to Devpost submissions
- **Automatic Synchronization**: Keep project metadata and files in sync
- **File Monitoring**: Detect changes and trigger updates automatically
- **Preview Generation**: Preview how projects will appear on Devpost
- **Multi-project Support**: Manage multiple hackathon projects simultaneously
- **Deadline Tracking**: Monitor submission deadlines and requirements

## Architecture

### Browser Automation Approach

This integration uses **browser automation** instead of API calls because DevPost does not provide a public API for hackathon project management. The system implements a hybrid approach:

1. **Primary**: Playwright browser automation for reliable data extraction
2. **Fallback**: Web scraping with BeautifulSoup when automation fails
3. **Cross-Browser**: Support for Chromium, Firefox, and WebKit
4. **Rate Limiting**: Respectful data extraction with proper delays

### Data Extraction Methods

- **Hackathon Data**: Extract hackathon information, deadlines, requirements
- **Project Data**: Extract project details, team members, GitHub links
- **Search Functionality**: Search for hackathons by query
- **Real-time Updates**: Live data extraction from DevPost pages

## Architecture

The integration is built with a modular architecture:

- **Models**: Data structures for projects, metadata, and configuration
- **Interfaces**: Abstract base classes defining component contracts
- **Validation**: Ensure data meets Devpost requirements
- **Configuration**: Manage project connections and settings
- **Web Scraping Fallback**: BeautifulSoup-based fallback when browser automation fails
- **Browser Automation**: Playwright-based web automation for DevPost data extraction
- **Sync Manager**: Orchestrate synchronization operations
- **File Monitor**: Watch for file system changes
- **Project Manager**: Manage local project metadata
- **Preview Generator**: Generate local previews
- **CLI**: Command-line interface for user interaction

## Getting Started

### Installation

The module is part of the Beast Mode system and uses the existing dependencies:

- `pydantic>=2.0.0` - Data validation and serialization
- `click>=8.0.0` - CLI framework
- `jinja2>=3.1.0` - Template rendering for previews

### Basic Usage

```python
from beast_mode.integration.devpost import DevpostProjectManager, DevpostConfig

# Create configuration
config = DevpostConfig(
    project_id="your-project-id",
    hackathon_id="hackathon-id"
)

# Initialize project manager
manager = DevpostProjectManager(config_path=Path(".kiro/devpost"))

# Connect to Devpost
connection = manager.connect_to_devpost("project-id", "hackathon-id")
```

## Development

### Running Tests

```bash
python3 -m pytest tests/unit/integration/devpost/ -v
```

### Project Structure

```
src/beast_mode/integration/devpost/
├── __init__.py              # Main module exports
├── models.py                # Data models and schemas
├── interfaces.py            # Abstract base classes
├── validation.py            # Validation utilities
├── config.py                # Configuration management
├── auth/                    # Authentication services
├── api/                     # API client
├── sync/                    # Synchronization services
├── project/                 # Project management
├── preview/                 # Preview generation
└── cli/                     # Command-line interface
```

## Status

This module is currently in development as part of Task 1 of the implementation plan. The foundation components (models, interfaces, validation, and configuration) are complete and tested.

## Next Steps

1. Implement authentication service (Task 3)
2. Build API client (Task 4)
3. Create project manager (Task 5)
4. Add file monitoring (Task 6)
5. Implement synchronization (Task 7)
6. Build preview generation (Task 8)
7. Create CLI interface (Task 9)