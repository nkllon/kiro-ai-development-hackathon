#!/usr/bin/env python3
"""
Quick disk space analysis
"""

import os
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path("/Users/lou/kiro-2/kiro-ai-development-hackathon")

def human_readable(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

# Analyze by file type
categories = defaultdict(lambda: {'count': 0, 'size': 0})
large_files = []

for root, dirs, files in os.walk(BASE_DIR):
    # Skip certain directories
    skip_dirs = {'.git', 'node_modules', '.venv', '__pycache__'}
    dirs[:] = [d for d in dirs if d not in skip_dirs]
    
    for file in files:
        filepath = Path(root) / file
        try:
            size = filepath.stat().st_size
            ext = filepath.suffix.lower() or 'no_extension'
            
            categories[ext]['count'] += 1
            categories[ext]['size'] += size
            
            # Track files > 500KB
            if size > 500 * 1024:
                large_files.append((filepath.relative_to(BASE_DIR), size))
                
        except (PermissionError, FileNotFoundError):
            continue

print("=" * 80)
print("FILE TYPE BREAKDOWN")
print("=" * 80)

sorted_cats = sorted(categories.items(), key=lambda x: x[1]['size'], reverse=True)
for ext, data in sorted_cats[:15]:
    print(f"{ext:15} | {data['count']:5} files | {human_readable(data['size']):>12}")

print("\n" + "=" * 80)
print("TOP 50 LARGEST FILES")
print("=" * 80)

large_files.sort(key=lambda x: x[1], reverse=True)
for path, size in large_files[:50]:
    print(f"{human_readable(size):>12} | {path}")

# Calculate totals
total_size = sum(cat['size'] for cat in categories.values())
total_files = sum(cat['count'] for cat in categories.values())

print("\n" + "=" * 80)
print(f"TOTAL: {total_files} files | {human_readable(total_size)}")
print("=" * 80)

# Specific recommendations
print("\nRECOMMENDATIONS:")
print("-" * 80)

png_size = categories['.png']['size']
log_size = categories['.log']['size']

if png_size > 10 * 1024 * 1024:
    print(f"• Archive PNG screenshots: {human_readable(png_size)} ({categories['.png']['count']} files)")

if log_size > 5 * 1024 * 1024:
    print(f"• Archive or delete old logs: {human_readable(log_size)} ({categories['.log']['count']} files)")

# Check for backup directories
for root, dirs, files in os.walk(BASE_DIR):
    if any('backup' in d.lower() for d in dirs):
        print(f"• Consider archiving backup directories")
        break
