#!/usr/bin/env python3
"""
Documentation Consolidation Script
Organizes and consolidates the docs/ directory structure
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

def main():
    """Consolidate documentation directory structure"""
    
    print("🚀 Starting Documentation Consolidation...")
    
    # Directories to archive from docs/ (move to archive/development/docs/)
    archive_dirs = [
        '.cleanup-workspace', '.kiro', '.simone', 'assessment-results',
        'brownfield_analysis', 'cloudflare', 'demo_project', 'deployment',
        'docker-migration-backup-20251003_161735', 'hackathon', 'html-samples',
        'implementation_guides_20250930-130220', 'logs', 'makefile_system',
        'makefile_system_implemented', 'monitoring', 'observatory_data',
        'ontology', 'poe_deployment_20251004_152642', 'prompts', 'python_scripts',
        'rc1', 'rms', 'screenshots', 'scripts', 'spores', 'summaries',
        'vonnegut_container_deployment', 'vonnegut_deployment_package', 'web'
    ]
    
    # Files to archive from docs/
    archive_files = [
        '.DS_Store', 'agent_control_governance_dag_validation_report.txt',
        'agent_coordination_log.txt', 'agent-spawn-test.txt', 'ARCHIVE_SOLUTION_SUMMARY.txt',
        'branch-state-before-cleanup.txt', 'dag_execution_claude_log.txt',
        'dag_execution_corrected_log.txt', 'dag_execution_cursor_log.txt',
        'dag_execution_log.txt', 'documentation-agent-log.txt', 'FILES_CREATED.txt',
        'finalization_body_20250915_023229.txt', 'ghostbusters_domain_triage.txt',
        'ghostbusters_framework_dag.mmd', 'ghostbusters_git_status.txt',
        'ghostbusters_phase1_report.txt', 'git_status_sample.txt',
        'git-graph-before-cleanup.txt', 'integration_log.txt', 'link_scan_results.txt',
        'my_projects_body_20250915_023413.txt', 'opensource-agent-log.txt',
        'persistent_dag_registry.mmd', 'redis_env_template.txt',
        'ubiquitous_language_vocabulary.json'
    ]
    
    # PDF files to archive
    pdf_files = [
        'Analytics & logs _ HTTP Traffic _ nkllon.com _ Lou@louspringer.com\'s Account _ Cloudflare.pdf'
    ]
    
    # Create archive directory
    archive_dir = Path('archive/development/docs')
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    operations = []
    
    # Archive directories from docs/
    print("📦 Archiving development directories from docs/...")
    for dir_name in archive_dirs:
        src_path = Path('docs') / dir_name
        if src_path.exists() and src_path.is_dir():
            target = archive_dir / dir_name
            if not target.exists():
                print(f"   📁 Archiving: docs/{dir_name} -> archive/development/docs/{dir_name}")
                shutil.move(str(src_path), str(target))
                operations.append({
                    'action': 'archive',
                    'source': f'docs/{dir_name}',
                    'target': str(target),
                    'type': 'directory'
                })
            else:
                print(f"   ⚠️  Skipping docs/{dir_name} (target exists)")
    
    # Archive files from docs/
    print("📦 Archiving development files from docs/...")
    for file_name in archive_files + pdf_files:
        src_path = Path('docs') / file_name
        if src_path.exists():
            target = archive_dir / file_name
            print(f"   📁 Archiving: docs/{file_name} -> archive/development/docs/{file_name}")
            shutil.move(str(src_path), str(target))
            operations.append({
                'action': 'archive',
                'source': f'docs/{file_name}',
                'target': str(target),
                'type': 'file'
            })
    
    # Create organized documentation structure
    print("📚 Creating organized documentation structure...")
    
    # Create main documentation directories
    main_dirs = [
        'docs/getting-started',
        'docs/user-guide', 
        'docs/developer-guide',
        'docs/api-reference',
        'docs/deployment',
        'docs/troubleshooting',
        'docs/examples'
    ]
    
    for dir_path in main_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"   📁 Created: {dir_path}")
    
    # Move key documentation files to appropriate locations
    key_moves = [
        ('docs/INSTALLATION.md', 'docs/getting-started/installation.md'),
        ('docs/USER_GUIDE.md', 'docs/user-guide/index.md'),
        ('docs/CONTRIBUTING.md', 'docs/developer-guide/contributing.md'),
        ('docs/README.md', 'docs/index.md')
    ]
    
    for src, dst in key_moves:
        if Path(src).exists():
            print(f"   🔄 Moving: {src} -> {dst}")
            shutil.move(src, dst)
            operations.append({
                'action': 'move',
                'source': src,
                'target': dst,
                'type': 'file'
            })
    
    # Clean up empty directories
    print("🧹 Cleaning up empty directories...")
    for root, dirs, files in os.walk('docs', topdown=False):
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
    
    with open('data/documentation_consolidation_log.json', 'w') as f:
        json.dump(log_data, f, indent=2)
    
    print(f"\n✅ Documentation consolidation completed!")
    print(f"   📦 Directories archived: {log_data['summary']['directories_archived']}")
    print(f"   📁 Files archived: {log_data['summary']['files_archived']}")
    print(f"   🔄 Files moved: {log_data['summary']['files_moved']}")
    print(f"   🗑️  Empty directories removed: {log_data['summary']['empty_dirs_removed']}")
    print(f"   📄 Log saved to: data/documentation_consolidation_log.json")

if __name__ == "__main__":
    main()