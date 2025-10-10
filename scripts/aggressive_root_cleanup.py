#!/usr/bin/env python3
"""
Aggressive Root Directory Cleanup
Moves development artifacts and temporary directories to archive
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

def main():
    """Execute aggressive root directory cleanup"""
    
    print("🚀 Starting Aggressive Root Directory Cleanup...")
    
    # Directories to archive (move to archive/development)
    archive_dirs = [
        '.cleanup-workspace',
        '.repair_backups', 
        '.repair_backups_phase3d',
        '.task_execution',
        'backup_20250915_124042',
        'beast_mode_metrics',
        'brownfield_analysis',
        'cloudflare_parallel_logs',
        'deployment',
        'docker-migration-backup-20251003_161735',
        'empirical_data',
        'generated_diagrams',
        'generated_docs',
        'hackathons',
        'investigation',
        'kiro_outputs',
        'kiro_simone_adapter',
        'learning_patterns',
        'logs',
        'makefile_system',
        'makefile_system_implemented',
        'makefiles',
        'metrics_data',
        'monitoring',
        'nginx',
        'observatory_data',
        'ontology',
        'packer-systo-go',
        'packer-systo-python',
        'parallel_execution_logs',
        'poe_deployment_20251004_152642',
        'reports',
        'requirements',
        'scripts-archive',
        'spores',
        'static',
        'templates',
        'test_evidence',
        'validation_evidence',
        'var',
        'vonnegut_container_deployment',
        'vonnegut_deployment',
        'vonnegut_deployment_package',
        'web'
    ]
    
    # Files to delete (temporary/cache files)
    delete_files = [
        '.coverage',
        'claude',
        'file_organization_log.json',
        'ghostbusters_test_validation.txt',
        'nohup.out',
        'test_prompt.txt',
        'test_write.txt'
    ]
    
    # Files to move to archive
    archive_files = [
        'Makefile.deployment-auditor',
        'Makefile.legacy',
        'Makefile.services',
        'sample.env.template'
    ]
    
    # Create archive directory
    archive_dir = Path('archive/development')
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    operations = []
    
    # Archive directories
    print("📦 Archiving development directories...")
    for dir_name in archive_dirs:
        if os.path.exists(dir_name) and os.path.isdir(dir_name):
            target = archive_dir / dir_name
            if not target.exists():
                print(f"   📁 Archiving: {dir_name} -> archive/development/{dir_name}")
                shutil.move(dir_name, str(target))
                operations.append({
                    'action': 'archive',
                    'source': dir_name,
                    'target': str(target),
                    'type': 'directory'
                })
            else:
                print(f"   ⚠️  Skipping {dir_name} (target exists)")
    
    # Delete temporary files
    print("🗑️  Deleting temporary files...")
    for file_name in delete_files:
        if os.path.exists(file_name):
            print(f"   🗑️  Deleting: {file_name}")
            os.remove(file_name)
            operations.append({
                'action': 'delete',
                'source': file_name,
                'type': 'file'
            })
    
    # Archive files
    print("📦 Archiving legacy files...")
    for file_name in archive_files:
        if os.path.exists(file_name):
            target = archive_dir / file_name
            print(f"   📁 Archiving: {file_name} -> archive/development/{file_name}")
            shutil.move(file_name, str(target))
            operations.append({
                'action': 'archive',
                'source': file_name,
                'target': str(target),
                'type': 'file'
            })
    
    # Save operation log
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'operations': operations,
        'summary': {
            'directories_archived': len([op for op in operations if op['action'] == 'archive' and op['type'] == 'directory']),
            'files_archived': len([op for op in operations if op['action'] == 'archive' and op['type'] == 'file']),
            'files_deleted': len([op for op in operations if op['action'] == 'delete']),
            'total_operations': len(operations)
        }
    }
    
    with open('data/aggressive_cleanup_log.json', 'w') as f:
        json.dump(log_data, f, indent=2)
    
    print(f"\n✅ Aggressive cleanup completed!")
    print(f"   📦 Directories archived: {log_data['summary']['directories_archived']}")
    print(f"   📁 Files archived: {log_data['summary']['files_archived']}")
    print(f"   🗑️  Files deleted: {log_data['summary']['files_deleted']}")
    print(f"   📄 Log saved to: data/aggressive_cleanup_log.json")

if __name__ == "__main__":
    main()