#!/bin/bash
# Make all archiving scripts executable

chmod +x auto_archive.sh
chmod +x quick_analysis.py
chmod +x archive_to_s3.py
chmod +x archive_old_screenshots.py

echo "✓ All archiving scripts are now executable"
echo ""
echo "Available commands:"
echo "  ./quick_analysis.py                    - Quick read-only analysis"
echo "  ./archive_to_s3.py                     - Interactive archiving tool"
echo "  ./auto_archive.sh <bucket>             - Automated archiving (files > 1MB)"
echo "  ./archive_old_screenshots.py <bucket>  - Archive old screenshots only"
echo ""
echo "Read DISK_SPACE_README.md for detailed instructions"
