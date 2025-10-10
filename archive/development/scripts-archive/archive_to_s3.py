#!/usr/bin/env python3
"""
Disk Space Analyzer and S3 Archiver
Identifies large files and archives them to AWS S3
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Configuration
BASE_DIR = Path("/Users/lou/kiro-2/kiro-ai-development-hackathon")
S3_BUCKET = input("Enter your S3 bucket name (e.g., s3://my-bucket): ").strip()
ARCHIVE_PREFIX = f"archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# File size thresholds (in MB)
LARGE_FILE_THRESHOLD = 1.0  # Files larger than 1 MB
ARCHIVE_THRESHOLD = 0.5  # Archive files larger than 500 KB

# File categories to archive
ARCHIVE_PATTERNS = {
    'screenshots': ['*.png', '*.jpg', '*.jpeg'],
    'logs': ['*.log'],
    'large_scripts': ['*.sh'],
    'backups': ['backup_*', '*.bak'],
    'temp': ['*.tmp', 'tmp_*']
}

def get_dir_size(path):
    """Calculate directory size recursively"""
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file(follow_symlinks=False):
                total += entry.stat().st_size
            elif entry.is_dir(follow_symlinks=False):
                total += get_dir_size(entry.path)
    except PermissionError:
        pass
    return total

def human_readable_size(size_bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def analyze_disk_usage():
    """Analyze disk usage and categorize files"""
    print("=" * 80)
    print("DISK SPACE ANALYSIS")
    print("=" * 80)
    
    categories = defaultdict(lambda: {'count': 0, 'size': 0, 'files': []})
    
    # Walk through all files
    for root, dirs, files in os.walk(BASE_DIR):
        # Skip certain directories
        skip_dirs = {'.git', 'node_modules', '.venv', '__pycache__', '.pytest_cache'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            filepath = Path(root) / file
            try:
                size = filepath.stat().st_size
                ext = filepath.suffix.lower()
                
                # Categorize
                if ext in ['.png', '.jpg', '.jpeg', '.gif']:
                    category = 'images'
                elif ext in ['.log']:
                    category = 'logs'
                elif ext in ['.sh', '.bash']:
                    category = 'scripts'
                elif ext in ['.json']:
                    category = 'json'
                elif ext in ['.md']:
                    category = 'markdown'
                elif 'backup' in file.lower():
                    category = 'backups'
                else:
                    category = 'other'
                
                categories[category]['count'] += 1
                categories[category]['size'] += size
                
                # Track large files
                if size > LARGE_FILE_THRESHOLD * 1024 * 1024:
                    categories[category]['files'].append({
                        'path': str(filepath.relative_to(BASE_DIR)),
                        'size': size
                    })
                    
            except (PermissionError, FileNotFoundError):
                continue
    
    # Print summary
    print(f"\nBase directory: {BASE_DIR}")
    print(f"Total size: {human_readable_size(get_dir_size(BASE_DIR))}\n")
    
    # Sort categories by size
    sorted_categories = sorted(categories.items(), key=lambda x: x[1]['size'], reverse=True)
    
    print("Category breakdown:")
    print("-" * 80)
    for category, data in sorted_categories:
        print(f"{category:15} | {data['count']:5} files | {human_readable_size(data['size']):>12}")
    
    # Show largest files per category
    print("\n" + "=" * 80)
    print("LARGEST FILES BY CATEGORY")
    print("=" * 80)
    
    for category, data in sorted_categories:
        if data['files']:
            print(f"\n{category.upper()}:")
            sorted_files = sorted(data['files'], key=lambda x: x['size'], reverse=True)[:10]
            for file in sorted_files:
                print(f"  {human_readable_size(file['size']):>12} | {file['path']}")
    
    return categories

def generate_archive_plan(categories):
    """Generate a plan for what to archive"""
    print("\n" + "=" * 80)
    print("ARCHIVE RECOMMENDATIONS")
    print("=" * 80)
    
    archive_plan = []
    total_savings = 0
    
    # Identify archivable files
    for category, data in categories.items():
        for file_info in data['files']:
            if file_info['size'] > ARCHIVE_THRESHOLD * 1024 * 1024:
                archive_plan.append(file_info)
                total_savings += file_info['size']
    
    # Sort by size
    archive_plan.sort(key=lambda x: x['size'], reverse=True)
    
    print(f"\nFound {len(archive_plan)} files to archive")
    print(f"Potential space savings: {human_readable_size(total_savings)}\n")
    
    # Show top 20
    print("Top 20 files recommended for archiving:")
    for i, file in enumerate(archive_plan[:20], 1):
        print(f"{i:3}. {human_readable_size(file['size']):>12} | {file['path']}")
    
    if len(archive_plan) > 20:
        print(f"... and {len(archive_plan) - 20} more files")
    
    # Save full plan
    plan_file = BASE_DIR / "archive_plan.json"
    with open(plan_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_files': len(archive_plan),
            'total_size': total_savings,
            'files': archive_plan
        }, f, indent=2)
    
    print(f"\nFull archive plan saved to: {plan_file}")
    
    return archive_plan

def archive_to_s3(archive_plan, s3_bucket):
    """Archive files to S3"""
    print("\n" + "=" * 80)
    print("ARCHIVING TO S3")
    print("=" * 80)
    
    if not s3_bucket.startswith('s3://'):
        s3_bucket = f"s3://{s3_bucket}"
    
    print(f"\nTarget: {s3_bucket}/{ARCHIVE_PREFIX}/")
    print(f"Files to archive: {len(archive_plan)}")
    
    response = input("\nProceed with archiving? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Archiving cancelled.")
        return
    
    # Create archive manifest
    manifest = {
        'timestamp': datetime.now().isoformat(),
        'source': str(BASE_DIR),
        'destination': f"{s3_bucket}/{ARCHIVE_PREFIX}",
        'files': []
    }
    
    successful = 0
    failed = 0
    
    for file_info in archive_plan:
        local_path = BASE_DIR / file_info['path']
        s3_path = f"{s3_bucket}/{ARCHIVE_PREFIX}/{file_info['path']}"
        
        try:
            print(f"Uploading: {file_info['path']}")
            result = subprocess.run(
                ['aws', 's3', 'cp', str(local_path), s3_path],
                capture_output=True,
                text=True,
                check=True
            )
            
            manifest['files'].append({
                'path': file_info['path'],
                'size': file_info['size'],
                's3_location': s3_path,
                'status': 'success'
            })
            successful += 1
            
            # Optionally delete local file
            delete = input(f"Delete local file {file_info['path']}? (y/n/all/none): ").strip().lower()
            if delete in ['y', 'yes', 'all']:
                local_path.unlink()
                print(f"  Deleted local file")
                if delete == 'all':
                    # Auto-delete remaining files
                    pass
            elif delete == 'none':
                break
                
        except subprocess.CalledProcessError as e:
            print(f"  ERROR: {e.stderr}")
            manifest['files'].append({
                'path': file_info['path'],
                'size': file_info['size'],
                's3_location': s3_path,
                'status': 'failed',
                'error': e.stderr
            })
            failed += 1
        except Exception as e:
            print(f"  ERROR: {str(e)}")
            failed += 1
    
    # Save manifest
    manifest_file = BASE_DIR / f"archive_manifest_{ARCHIVE_PREFIX}.json"
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print("\n" + "=" * 80)
    print("ARCHIVE COMPLETE")
    print("=" * 80)
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Manifest saved to: {manifest_file}")

def main():
    """Main execution"""
    print("\n" + "=" * 80)
    print("DISK SPACE ANALYZER AND S3 ARCHIVER")
    print("=" * 80)
    
    # Analyze
    categories = analyze_disk_usage()
    
    # Generate plan
    archive_plan = generate_archive_plan(categories)
    
    # Ask if user wants to archive
    if archive_plan and S3_BUCKET:
        print(f"\nS3 Bucket: {S3_BUCKET}")
        response = input("\nProceed to S3 archiving? (yes/no): ").strip().lower()
        if response == 'yes':
            archive_to_s3(archive_plan, S3_BUCKET)
    else:
        print("\nTo archive files, run this script again with your S3 bucket configured.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
