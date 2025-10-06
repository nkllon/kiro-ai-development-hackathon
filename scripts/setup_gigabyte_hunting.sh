#!/bin/bash
# Complete setup and analysis for finding gigabytes

echo "=========================================="
echo "GIGABYTE HUNTER - Setup & Analysis"
echo "=========================================="
echo ""

# Make scripts executable
echo "Making scripts executable..."
chmod +x analyze_documents.py
chmod +x bulk_archive_documents.sh
chmod +x check_aws_setup.py
echo "✓ Done"
echo ""

# Check AWS
echo "Checking AWS setup..."
python3 check_aws_setup.py
echo ""

# Run Documents analysis
echo "=========================================="
echo "Ready to analyze ~/Documents for gigabytes!"
echo "=========================================="
echo ""
echo "Run one of these commands:"
echo ""
echo "1. Analyze Documents folder:"
echo "   python3 analyze_documents.py ~/Documents"
echo ""
echo "2. Bulk archive old/large folders:"
echo "   ./bulk_archive_documents.sh ~/Documents your-bucket-name"
echo ""
echo "3. Quick disk usage check:"
echo "   du -h -d 1 ~/Documents | sort -rh | head -20"
echo ""
echo "📖 Full guide: GIGABYTE_HUNTING_GUIDE.md"
echo ""
