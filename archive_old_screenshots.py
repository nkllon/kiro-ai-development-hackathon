#!/usr/bin/env python3
"""
Smart Screenshot Archiver
Archives screenshots older than N days to S3
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import json

# Configuration
BASE_DIR = Path("/Users/lou/kiro-2/kiro-ai-development-hackathon")
DAYS_OLD = 30  # Archive screenshots older than this
S3_BUCKET = ""  # Will prompt if empty

def get_file_age_days(filepath):
    """Get file age in days"""
    mtime = filepath.stat().st_mtime
    file_date = datetime.fromtimestamp(mtime)
    age = datetime.now() - file_date
    return age.days

def human_readable(size_bytes):
    """Convert bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def find_old_screenshots(days=30):
    """Find screenshots older than specified days"""
    old_files = []
    total_size = 0
    
    print(f"Scanning for PNG/JPG files older than {days} days...")
    print()
    
    for pattern in ['*.png', '*.jpg', '*.jpeg']:
        for filepath in BASE_DIR.rglob(pattern):
            # Skip certain directories
            if any(skip in filepath.parts for skip in ['.git', 'node_modules', '.venv']):
                continue
            
            try:
                age_days = get_file_age_days(filepath)
                if age_days >= days:
                    size = filepath.stat().st_size
                    old_files.append({
                        'path': str(filepath.relative_to(BASE_DIR)),
                        'full_path': str(filepath),
                        'size': size,
                        'age_days': age_days,
                        'modified': datetime.fromtimestamp(filepath.stat().st_mtime).strftime('%Y-%m-%d')
                    })
                    total_size += size
            except (PermissionError, FileNotFoundError):
                continue
    
    return sorted(old_files, key=lambda x: x['age_days'], reverse=True), total_size

def main():
    global S3_BUCKET
    
    print("=" * 80)
    print("SMART SCREENSHOT ARCHIVER")
    print("=" * 80)
    print()
    
    # Get S3 bucket
    if len(sys.argv) > 1:
        S3_BUCKET = sys.argv[1]
    else:
        S3_BUCKET = input("Enter S3 bucket name: ").strip()
    
    if not S3_BUCKET:
        print("Error: S3 bucket name required")
        sys.exit(1)
    
    if not S3_BUCKET.startswith('s3://'):
        S3_BUCKET = f"s3://{S3_BUCKET}"
    
    # Get days threshold
    try:
        days = int(input(f"Archive files older than how many days? [{DAYS_OLD}]: ").strip() or DAYS_OLD)
    except ValueError:
        days = DAYS_OLD
    
    # Find old files
    old_files, total_size = find_old_screenshots(days)
    
    if not old_files:
        print(f"✓ No screenshots older than {days} days found!")
        return
    
    print(f"Found {len(old_files)} screenshots older than {days} days")
    print(f"Total size: {human_readable(total_size)}")
    print()
    
    # Show summary by age bracket
    brackets = {
        '30-60 days': [],
        '60-90 days': [],
        '90+ days': []
    }
    
    for file in old_files:
        age = file['age_days']
        if age < 60:
            brackets['30-60 days'].append(file)
        elif age < 90:
            brackets['60-90 days'].append(file)
        else:
            brackets['90+ days'].append(file)
    
    print("Age distribution:")
    for bracket, files in brackets.items():
        if files:
            size = sum(f['size'] for f in files)
            print(f"  {bracket}: {len(files)} files ({human_readable(size)})")
    print()
    
    # Show sample files
    print("Sample files (oldest 10):")
    for i, file in enumerate(old_files[:10], 1):
        print(f"  {i:2}. {file['age_days']:3} days old | {human_readable(file['size']):>10} | {file['path']}")
    
    if len(old_files) > 10:
        print(f"  ... and {len(old_files) - 10} more files")
    print()
    
    # Confirm
    response = input("Archive these files to S3? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        return
    
    # Create archive
    archive_date = datetime.now().strftime('%Y%m%d_%H%M%S')
    archive_prefix = f"screenshots_archive_{archive_date}"
    
    print()
    print(f"Archiving to: {S3_BUCKET}/{archive_prefix}/")
    print()
    
    manifest = {
        'timestamp': datetime.now().isoformat(),
        'days_threshold': days,
        'total_files': len(old_files),
        'total_size': total_size,
        'destination': f"{S3_BUCKET}/{archive_prefix}",
        'files': []
    }
    
    successful = 0
    failed = 0
    
    for file in old_files:
        local_path = file['full_path']
        s3_path = f"{S3_BUCKET}/{archive_prefix}/{file['path']}"
        
        print(f"Uploading: {file['path']}")
        
        try:
            subprocess.run(
                ['aws', 's3', 'cp', local_path, s3_path],
                capture_output=True,
                text=True,
                check=True
            )
            
            manifest['files'].append({
                'path': file['path'],
                'size': file['size'],
                'age_days': file['age_days'],
                'modified': file['modified'],
                's3_location': s3_path,
                'status': 'success'
            })
            
            successful += 1
            
        except subprocess.CalledProcessError as e:
            print(f"  ERROR: {e.stderr}")
            manifest['files'].append({
                'path': file['path'],
                'error': e.stderr,
                'status': 'failed'
            })
            failed += 1
    
    # Save manifest
    manifest_file = BASE_DIR / f"screenshot_archive_manifest_{archive_date}.json"
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print()
    print("=" * 80)
    print("ARCHIVE COMPLETE")
    print("=" * 80)
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Manifest: {manifest_file}")
    print()
    
    # Ask about deletion
    if successful > 0:
        print(f"Successfully archived {successful} files to S3.")
        delete_response = input("Delete local copies? (yes/no): ").strip().lower()
        
        if delete_response == 'yes':
            deleted = 0
            for file in manifest['files']:
                if file.get('status') == 'success':
                    try:
                        Path(BASE_DIR / file['path']).unlink()
                        deleted += 1
                    except Exception as e:
                        print(f"  Error deleting {file['path']}: {e}")
            
            print(f"Deleted {deleted} local files")
            print(f"Space freed: {human_readable(total_size)}")
        else:
            print("Local files retained. You can delete them manually later.")
    
    print()
    print("To restore archived files:")
    print(f"  aws s3 sync {S3_BUCKET}/{archive_prefix}/ ./")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
