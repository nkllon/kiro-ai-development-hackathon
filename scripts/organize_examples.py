#!/usr/bin/env python3
"""
Examples Organization Script
Cleans up and organizes the examples/ directory structure
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

def main():
    """Organize examples directory structure"""
    
    print("🚀 Starting Examples Organization...")
    
    # Directories to archive from examples/ (move to archive/development/examples/)
    archive_dirs = [
        '.kiro', 'demo_project', 'demo_spores', 'poe_deployment_20251004_152642',
        'vonnegut_container_deployment', 'vonnegut_deployment_package'
    ]
    
    # Files to archive from examples/
    archive_files = [
        '.DS_Store', 'cli_usage_results.json', 'quick_start_results.json'
    ]
    
    # Create archive directory
    archive_dir = Path('archive/development/examples')
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Create organized examples structure
    organized_dirs = [
        'examples/basic',
        'examples/advanced',
        'examples/integrations',
        'examples/notebooks',
        'examples/demos'
    ]
    
    operations = []
    
    # Archive directories from examples/
    print("📦 Archiving development directories from examples/...")
    for dir_name in archive_dirs:
        src_path = Path('examples') / dir_name
        if src_path.exists() and src_path.is_dir():
            target = archive_dir / dir_name
            if not target.exists():
                print(f"   📁 Archiving: examples/{dir_name} -> archive/development/examples/{dir_name}")
                shutil.move(str(src_path), str(target))
                operations.append({
                    'action': 'archive',
                    'source': f'examples/{dir_name}',
                    'target': str(target),
                    'type': 'directory'
                })
            else:
                print(f"   ⚠️  Skipping examples/{dir_name} (target exists)")
    
    # Archive files from examples/
    print("📦 Archiving development files from examples/...")
    for file_name in archive_files:
        src_path = Path('examples') / file_name
        if src_path.exists():
            target = archive_dir / file_name
            print(f"   📁 Archiving: examples/{file_name} -> archive/development/examples/{file_name}")
            shutil.move(str(src_path), str(target))
            operations.append({
                'action': 'archive',
                'source': f'examples/{file_name}',
                'target': str(target),
                'type': 'file'
            })
    
    # Create organized directory structure
    print("📚 Creating organized examples structure...")
    for dir_path in organized_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"   📁 Created: {dir_path}")
    
    # Organize existing example files by category
    basic_examples = [
        'quick_start_demo.py', 'simple_beast_agent.py', 'simple_hotrod_queue.py',
        'secure_credential_usage.py', 'cli_usage_examples.py'
    ]
    
    advanced_examples = [
        'beast_mode_collaboration_agents.py', 'comprehensive_reporting_demo.py',
        'enhanced_rm_validator_demo.py', 'rca_performance_optimization_demo.py',
        'rca_report_generation_demo.py', 'spec_framework_demo.py'
    ]
    
    integration_examples = [
        'agent_discovery_demo.py', 'deployment_demo.py', 'observatory_demo.py',
        'tool_orchestration_demo.py', 'unified_client_demo.py', 'web_server_demo.py'
    ]
    
    demo_examples = [
        'emoji_rain_demo.py', 'daemon_hotrod.py', 'hotrod_agent.py',
        'monitoring_system_demo.py', 'spore_management_demo.py'
    ]
    
    # Move files to appropriate categories
    print("🔄 Organizing examples by category...")
    
    for file_name in basic_examples:
        src_path = Path('examples') / file_name
        if src_path.exists():
            target = Path('examples/basic') / file_name
            print(f"   🔄 Moving: examples/{file_name} -> examples/basic/{file_name}")
            shutil.move(str(src_path), str(target))
            operations.append({
                'action': 'organize',
                'source': f'examples/{file_name}',
                'target': str(target),
                'type': 'file'
            })
    
    for file_name in advanced_examples:
        src_path = Path('examples') / file_name
        if src_path.exists():
            target = Path('examples/advanced') / file_name
            print(f"   🔄 Moving: examples/{file_name} -> examples/advanced/{file_name}")
            shutil.move(str(src_path), str(target))
            operations.append({
                'action': 'organize',
                'source': f'examples/{file_name}',
                'target': str(target),
                'type': 'file'
            })
    
    for file_name in integration_examples:
        src_path = Path('examples') / file_name
        if src_path.exists():
            target = Path('examples/integrations') / file_name
            print(f"   🔄 Moving: examples/{file_name} -> examples/integrations/{file_name}")
            shutil.move(str(src_path), str(target))
            operations.append({
                'action': 'organize',
                'source': f'examples/{file_name}',
                'target': str(target),
                'type': 'file'
            })
    
    for file_name in demo_examples:
        src_path = Path('examples') / file_name
        if src_path.exists():
            target = Path('examples/demos') / file_name
            print(f"   🔄 Moving: examples/{file_name} -> examples/demos/{file_name}")
            shutil.move(str(src_path), str(target))
            operations.append({
                'action': 'organize',
                'source': f'examples/{file_name}',
                'target': str(target),
                'type': 'file'
            })
    
    # Move notebook directory to organized structure
    if Path('examples/notebook').exists():
        target = Path('examples/notebooks')
        print(f"   🔄 Moving: examples/notebook -> examples/notebooks")
        shutil.move('examples/notebook', str(target))
        operations.append({
            'action': 'organize',
            'source': 'examples/notebook',
            'target': str(target),
            'type': 'directory'
        })
    
    # Move remaining files to appropriate categories
    remaining_files = []
    for item in Path('examples').iterdir():
        if item.is_file() and item.suffix == '.py':
            remaining_files.append(item.name)
    
    if remaining_files:
        print("🔄 Moving remaining files to advanced category...")
        for file_name in remaining_files:
            src_path = Path('examples') / file_name
            target = Path('examples/advanced') / file_name
            print(f"   🔄 Moving: examples/{file_name} -> examples/advanced/{file_name}")
            shutil.move(str(src_path), str(target))
            operations.append({
                'action': 'organize',
                'source': f'examples/{file_name}',
                'target': str(target),
                'type': 'file'
            })
    
    # Create README files for each category
    print("📝 Creating README files for each category...")
    
    readme_content = {
        'basic': """# Basic Examples

This directory contains simple, introductory examples that demonstrate basic functionality.

## Examples

- `quick_start_demo.py` - Quick start demonstration
- `simple_beast_agent.py` - Simple Beast Mode agent example
- `secure_credential_usage.py` - How to use secure credentials
- `cli_usage_examples.py` - Command-line interface examples

## Usage

Each example can be run independently:

```bash
python examples/basic/quick_start_demo.py
```
""",
        'advanced': """# Advanced Examples

This directory contains complex examples that demonstrate advanced features and integrations.

## Examples

- `beast_mode_collaboration_agents.py` - Multi-agent collaboration
- `comprehensive_reporting_demo.py` - Advanced reporting features
- `spec_framework_demo.py` - Specification framework usage

## Usage

These examples may require additional setup or configuration. Check each file for specific requirements.
""",
        'integrations': """# Integration Examples

This directory contains examples showing how to integrate with external systems and services.

## Examples

- `agent_discovery_demo.py` - Agent discovery integration
- `deployment_demo.py` - Deployment system integration
- `observatory_demo.py` - Observatory system integration

## Usage

Integration examples may require external services to be running. Check documentation for setup requirements.
""",
        'demos': """# Demo Examples

This directory contains demonstration scripts and interactive examples.

## Examples

- `emoji_rain_demo.py` - Fun emoji rain demonstration
- `monitoring_system_demo.py` - System monitoring demo
- `spore_management_demo.py` - Spore management demonstration

## Usage

Demo examples are designed to be interactive and educational.
""",
        'notebooks': """# Jupyter Notebooks

This directory contains Jupyter notebooks for interactive exploration and learning.

## Notebooks

- `5D2_Complete_Use_Cases_Exploration.ipynb` - Complete use cases exploration
- `ai_memory_palace_demo.ipynb` - AI Memory Palace demonstration
- `redis_data_exploration.ipynb` - Redis data exploration

## Usage

Start Jupyter Lab or Notebook server:

```bash
jupyter lab examples/notebooks/
```
"""
    }
    
    for category, content in readme_content.items():
        readme_path = Path(f'examples/{category}/README.md')
        if not readme_path.exists():
            with open(readme_path, 'w') as f:
                f.write(content)
            print(f"   📝 Created: {readme_path}")
            operations.append({
                'action': 'create_readme',
                'target': str(readme_path),
                'type': 'file'
            })
    
    # Create main examples README
    main_readme = """# Examples

This directory contains examples and demonstrations of the Beast Mode AI Development Framework.

## Directory Structure

- **[basic/](basic/)** - Simple, introductory examples
- **[advanced/](advanced/)** - Complex examples with advanced features
- **[integrations/](integrations/)** - External system integration examples
- **[demos/](demos/)** - Interactive demonstrations
- **[notebooks/](notebooks/)** - Jupyter notebooks for exploration

## Getting Started

1. Start with the [basic examples](basic/) to understand core concepts
2. Explore [notebooks](notebooks/) for interactive learning
3. Try [demos](demos/) for hands-on experience
4. Review [integrations](integrations/) for real-world usage
5. Study [advanced examples](advanced/) for complex scenarios

## Requirements

Most examples require:
- Python 3.9+
- Dependencies from `requirements.txt`
- Environment variables configured (see `.env.example`)

## Running Examples

```bash
# Basic example
python examples/basic/quick_start_demo.py

# Jupyter notebooks
jupyter lab examples/notebooks/

# Interactive demo
python examples/demos/emoji_rain_demo.py
```

## Contributing

When adding new examples:
1. Place them in the appropriate category directory
2. Include clear documentation and comments
3. Add usage instructions
4. Update the relevant README file
"""
    
    with open('examples/README.md', 'w') as f:
        f.write(main_readme)
    print(f"   📝 Created: examples/README.md")
    operations.append({
        'action': 'create_readme',
        'target': 'examples/README.md',
        'type': 'file'
    })
    
    # Save operation log
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'operations': operations,
        'summary': {
            'directories_archived': len([op for op in operations if op['action'] == 'archive' and op['type'] == 'directory']),
            'files_archived': len([op for op in operations if op['action'] == 'archive' and op['type'] == 'file']),
            'files_organized': len([op for op in operations if op['action'] == 'organize']),
            'readmes_created': len([op for op in operations if op['action'] == 'create_readme']),
            'total_operations': len(operations)
        }
    }
    
    with open('data/examples_organization_log.json', 'w') as f:
        json.dump(log_data, f, indent=2)
    
    print(f"\n✅ Examples organization completed!")
    print(f"   📦 Directories archived: {log_data['summary']['directories_archived']}")
    print(f"   📁 Files archived: {log_data['summary']['files_archived']}")
    print(f"   🔄 Files organized: {log_data['summary']['files_organized']}")
    print(f"   📝 README files created: {log_data['summary']['readmes_created']}")
    print(f"   📄 Log saved to: data/examples_organization_log.json")

if __name__ == "__main__":
    main()