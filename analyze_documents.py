#!/usr/bin/env python3
"""
Documents Folder Analyzer
Finds large folders and old files in ~/Documents
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def get_size(path):
    """Get size of file or directory"""
    total = 0
    try:
        if os.path.isfile(path):
            return os.path.getsize(path)
        for entry in os.scandir(path):
            if entry.is_file(follow_symlinks=False):
                total += entry.stat().st_size
            elif entry.is_dir(follow_symlinks=False):
                total += get_size(entry.path)
    except (PermissionError, FileNotFoundError):
        pass
    return total

def human_readable(size_bytes):
    """Convert bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def get_folder_age(path):
    """Get the age of the most recently modified file in folder"""
    try:
        latest_mtime = 0
        for entry in os.scandir(path):
            try:
                mtime = entry.stat().st_mtime
                if mtime > latest_mtime:
                    latest_mtime = mtime
            except:
                continue
        if latest_mtime > 0:
            age_days = (datetime.now().timestamp() - latest_mtime) / 86400
            return age_days, datetime.fromtimestamp(latest_mtime)
    except:
        pass
    return None, None

def analyze_documents_folder(base_path=None):
    """Analyze Documents folder"""
    if base_path is None:
        base_path = Path.home() / "Documents"
    else:
        base_path = Path(base_path)
    
    if not base_path.exists():
        print(f"Error: {base_path} does not exist")
        return
    
    print("=" * 80)
    print(f"ANALYZING: {base_path}")
    print("=" * 80)
    print()
    print("This may take a few minutes for large directories...")
    print()
    
    # Analyze top-level folders
    folders = []
    
    print("Scanning folders...")
    for entry in base_path.iterdir():
        if entry.is_dir():
            try:
                size = get_size(str(entry))
                age_days, last_modified = get_folder_age(str(entry))
                
                folders.append({
                    'name': entry.name,
                    'path': str(entry),
                    'size': size,
                    'age_days': age_days or 0,
                    'last_modified': last_modified
                })
                print(f"  Scanned: {entry.name} ({human_readable(size)})")
            except Exception as e:
                print(f"  Error scanning {entry.name}: {e}")
    
    # Sort by size
    folders.sort(key=lambda x: x['size'], reverse=True)
    
    print()
    print("=" * 80)
    print("FOLDERS BY SIZE")
    print("=" * 80)
    print()
    
    total_size = sum(f['size'] for f in folders)
    
    print(f"{'Folder':<40} {'Size':>12} {'% of Total':>10} {'Last Modified':>15}")
    print("-" * 80)
    
    for folder in folders:
        percentage = (folder['size'] / total_size * 100) if total_size > 0 else 0
        last_mod = folder['last_modified'].strftime('%Y-%m-%d') if folder['last_modified'] else 'Unknown'
        print(f"{folder['name']:<40} {human_readable(folder['size']):>12} {percentage:>9.1f}% {last_mod:>15}")
    
    print("-" * 80)
    print(f"{'TOTAL':<40} {human_readable(total_size):>12}")
    
    # Find old folders (>1 year)
    print()
    print("=" * 80)
    print("OLD FOLDERS (Last modified > 1 year ago)")
    print("=" * 80)
    print()
    
    old_folders = [f for f in folders if f['age_days'] > 365]
    old_folders.sort(key=lambda x: x['size'], reverse=True)
    
    if old_folders:
        old_size = sum(f['size'] for f in old_folders)
        print(f"Found {len(old_folders)} old folders totaling {human_readable(old_size)}")
        print()
        print(f"{'Folder':<40} {'Size':>12} {'Age (days)':>12} {'Last Modified':>15}")
        print("-" * 80)
        
        for folder in old_folders[:20]:  # Show top 20
            last_mod = folder['last_modified'].strftime('%Y-%m-%d') if folder['last_modified'] else 'Unknown'
            print(f"{folder['name']:<40} {human_readable(folder['size']):>12} {int(folder['age_days']):>12} {last_mod:>15}")
        
        if len(old_folders) > 20:
            remaining_size = sum(f['size'] for f in old_folders[20:])
            print(f"... and {len(old_folders) - 20} more folders ({human_readable(remaining_size)})")
    else:
        print("No folders older than 1 year found")
    
    # Find very large folders (>1GB)
    print()
    print("=" * 80)
    print("VERY LARGE FOLDERS (>1GB)")
    print("=" * 80)
    print()
    
    large_folders = [f for f in folders if f['size'] > 1024**3]  # 1GB
    
    if large_folders:
        print(f"Found {len(large_folders)} folders larger than 1GB")
        print()
        print(f"{'Folder':<40} {'Size':>12} {'Last Modified':>15}")
        print("-" * 80)
        
        for folder in large_folders:
            last_mod = folder['last_modified'].strftime('%Y-%m-%d') if folder['last_modified'] else 'Unknown'
            print(f"{folder['name']:<40} {human_readable(folder['size']):>12} {last_mod:>15}")
    else:
        print("No folders larger than 1GB found")
    
    # Recommendations
    print()
    print("=" * 80)
    print("ARCHIVING RECOMMENDATIONS")
    print("=" * 80)
    print()
    
    # Old AND large
    candidates = [f for f in folders if f['age_days'] > 365 and f['size'] > 100*1024*1024]  # >100MB and >1 year
    if candidates:
        candidate_size = sum(f['size'] for f in candidates)
        print(f"🎯 HIGH PRIORITY: Old (>1 year) AND large (>100MB)")
        print(f"   {len(candidates)} folders totaling {human_readable(candidate_size)}")
        print()
        for folder in candidates[:10]:
            print(f"   • {folder['name']:<40} {human_readable(folder['size']):>12}")
        if len(candidates) > 10:
            print(f"   ... and {len(candidates) - 10} more")
    
    print()
    print("💡 To archive a specific folder:")
    print("   aws s3 sync '/path/to/folder' s3://your-bucket/archive/folder_name/")
    print()
    print("💡 To analyze a specific folder in detail:")
    print(f"   python3 {sys.argv[0]} /path/to/specific/folder")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        analyze_documents_folder(sys.argv[1])
    else:
        analyze_documents_folder()
