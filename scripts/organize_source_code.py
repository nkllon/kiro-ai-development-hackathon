#!/usr/bin/env python3
"""
Source Code Organization Script
Cleans up and organizes the src/ directory structure
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

def main():
    """Organize source code directory structure"""
    
    print("🚀 Starting Source Code Organization...")
    
    # Directories to archive from src/ (move to archive/development/src/)
    archive_dirs = [
        '.claude', '.cursor', '.github', '.kiro', '.make-tasks', '.simone', 
        '.task_execution', '.vscode', '~',
        'audit_reports', 'beast_mode_metrics', 'cloudflare', 'config', 'data',
        'demo_project', 'demo_spores', 'deployment', 'docker-migration-backup-20251003_161735',
        'empirical_data', 'generated_docs', 'logs', 'monitoring', 'nginx',
        'observatory_data', 'packer-systo-python', 'patterns', 'poe_deployment_20251004_152642',
        'prompts', 'reports', 'static', 'templates', 'vonnegut_container_deployment',
        'vonnegut_deployment', 'vonnegut_deployment_package'
    ]
    
    # Files to archive from src/
    archive_files = [
        '.DS_Store', '.env.directus', '.gitguardian.yaml', '.gitlab-ci-patch-validation.yml',
        'file_organization_log.json', 'websocket_fix_monitoring_config.yml',
        'cloudflare-tunnel-config-websocket.yml', 'cloudflared-config-poe.yml'
    ]
    
    # Standalone Python files to move to appropriate directories
    standalone_files = [
        'advanced_migration_planner.py', 'advanced_uml_viewer.py', 'cli_safety_linter.py',
        'comprehensive_migration_planner.py', 'documentation_index_generator.py',
        'domain_diagram_generator.py', 'emergency_cli_fix.py', 'ghostbusters_plan_validator.py',
        'ghostbusters_root_cleanup_system.py', 'health_dashboard.py', 'makefile_system_implementation.py',
        'makefile_system_model.py', 'migration_graph_generator.py', 'multi_dimensional_vocabulary_projector.py',
        'random_test_runner.py', 'registry_dashboard.py', 'root_cleanup_planner.py',
        'safe_shell_wrapper.py', 'shell_command_fix.py', 'targeted_test_runner.py',
        'test_migration_executor.py', 'ubiquitous_language_generator.py', 'uml_diagram_viewer.py',
        'uml_documentation_system.py'
    ]
    
    # Create archive directory
    archive_dir = Path('archive/development/src')
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Create tools directory for standalone scripts
    tools_dir = Path('src/tools')
    tools_dir.mkdir(exist_ok=True)
    
    operations = []
    
    # Archive directories from src/
    print("📦 Archiving development directories from src/...")
    for dir_name in archive_dirs:
        src_path = Path('src') / dir_name
        if src_path.exists() and src_path.is_dir():
            target = archive_dir / dir_name
            if not target.exists():
                print(f"   📁 Archiving: src/{dir_name} -> archive/development/src/{dir_name}")
                shutil.move(str(src_path), str(target))
                operations.append({
                    'action': 'archive',
                    'source': f'src/{dir_name}',
                    'target': str(target),
                    'type': 'directory'
                })
            else:
                print(f"   ⚠️  Skipping src/{dir_name} (target exists)")
    
    # Archive files from src/
    print("📦 Archiving development files from src/...")
    for file_name in archive_files:
        src_path = Path('src') / file_name
        if src_path.exists():
            target = archive_dir / file_name
            print(f"   📁 Archiving: src/{file_name} -> archive/development/src/{file_name}")
            shutil.move(str(src_path), str(target))
            operations.append({
                'action': 'archive',
                'source': f'src/{file_name}',
                'target': str(target),
                'type': 'file'
            })
    
    # Move standalone files to tools directory
    print("🔧 Moving standalone scripts to tools directory...")
    for file_name in standalone_files:
        src_path = Path('src') / file_name
        if src_path.exists():
            target = tools_dir / file_name
            print(f"   🔧 Moving: src/{file_name} -> src/tools/{file_name}")
            shutil.move(str(src_path), str(target))
            operations.append({
                'action': 'move',
                'source': f'src/{file_name}',
                'target': str(target),
                'type': 'file'
            })
    
    # Clean up empty directories
    print("🧹 Cleaning up empty directories...")
    for root, dirs, files in os.walk('src', topdown=False):
        for dir_name in dirs:
            dir_path = Path(root) / dir_name
            try:
                if dir_path.is_dir() and not any(dir_path.iterdir()):
                    print(f"   🗑️  Removing empty directory: {dir_path}")
                    dir_path.rmdir()
                    operations.append({
                        'action': 'remove_empty',
                        'source': str(dir_path),
                        'type': 'directory'
                    })
            except OSError:
                pass  # Directory not empty or other issue
    
    # Save operation log
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'operations': operations,
        'summary': {
            'directories_archived': len([op for op in operations if op['action'] == 'archive' and op['type'] == 'directory']),
            'files_archived': len([op for op in operations if op['action'] == 'archive' and op['type'] == 'file']),
            'files_moved': len([op for op in operations if op['action'] == 'move']),
            'empty_dirs_removed': len([op for op in operations if op['action'] == 'remove_empty']),
            'total_operations': len(operations)
        }
    }
    
    with open('data/source_code_organization_log.json', 'w') as f:
        json.dump(log_data, f, indent=2)
    
    print(f"\n✅ Source code organization completed!")
    print(f"   📦 Directories archived: {log_data['summary']['directories_archived']}")
    print(f"   📁 Files archived: {log_data['summary']['files_archived']}")
    print(f"   🔧 Files moved to tools: {log_data['summary']['files_moved']}")
    print(f"   🗑️  Empty directories removed: {log_data['summary']['empty_dirs_removed']}")
    print(f"   📄 Log saved to: data/source_code_organization_log.json")

if __name__ == "__main__":
    main()