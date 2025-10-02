#!/bin/bash
# Auto-Archive to S3
# Archives large files automatically to S3 bucket

set -e

# Configuration
BASE_DIR="/Users/lou/kiro-2/kiro-ai-development-hackathon"
S3_BUCKET="${1:-}"
ARCHIVE_DATE=$(date +%Y%m%d_%H%M%S)
ARCHIVE_PREFIX="archive_${ARCHIVE_DATE}"
MIN_SIZE_MB=1  # Archive files larger than 1 MB

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "Auto-Archive to S3"
echo "========================================"
echo ""

# Check if S3 bucket is provided
if [ -z "$S3_BUCKET" ]; then
    echo -e "${RED}Error: S3 bucket not provided${NC}"
    echo "Usage: $0 <s3-bucket-name>"
    echo "Example: $0 my-archive-bucket"
    exit 1
fi

# Ensure bucket has s3:// prefix
if [[ ! $S3_BUCKET == s3://* ]]; then
    S3_BUCKET="s3://${S3_BUCKET}"
fi

echo "Base directory: $BASE_DIR"
echo "S3 destination: $S3_BUCKET/$ARCHIVE_PREFIX/"
echo "Minimum file size: ${MIN_SIZE_MB}MB"
echo ""

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI not found${NC}"
    echo "Install it with: brew install awscli"
    exit 1
fi

# Verify AWS credentials
echo "Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS credentials not configured${NC}"
    echo "Configure with: aws configure"
    exit 1
fi
echo -e "${GREEN}✓ AWS credentials valid${NC}"
echo ""

# Find large files
echo "Scanning for large files..."
TEMP_FILE=$(mktemp)

find "$BASE_DIR" -type f -size +${MIN_SIZE_MB}M \
    ! -path "*/.git/*" \
    ! -path "*/node_modules/*" \
    ! -path "*/.venv/*" \
    ! -path "*/__pycache__/*" \
    ! -path "*/.pytest_cache/*" \
    -print0 | while IFS= read -r -d '' file; do
    
    size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
    size_mb=$(echo "scale=2; $size / 1048576" | bc)
    rel_path=$(python3 -c "import os; print(os.path.relpath('$file', '$BASE_DIR'))")
    
    # Categorize
    case "$file" in
        *.png|*.jpg|*.jpeg|*.gif)
            category="images"
            ;;
        *.log)
            category="logs"
            ;;
        *.sh)
            category="scripts"
            ;;
        *backup*)
            category="backups"
            ;;
        *)
            category="other"
            ;;
    esac
    
    echo "$size_mb|$category|$rel_path|$file" >> "$TEMP_FILE"
done

# Sort by size
sort -t'|' -k1 -rn "$TEMP_FILE" -o "$TEMP_FILE"

# Display summary
total_size=0
total_files=0
declare -A category_totals

echo ""
echo "========================================"
echo "LARGE FILES FOUND"
echo "========================================"
echo ""

while IFS='|' read -r size_mb category rel_path full_path; do
    ((total_files++))
    total_size=$(echo "$total_size + $size_mb" | bc)
    category_totals[$category]=$(echo "${category_totals[$category]:-0} + $size_mb" | bc)
    
    if [ $total_files -le 20 ]; then
        printf "%8.2f MB | %-10s | %s\n" "$size_mb" "$category" "$rel_path"
    fi
done < "$TEMP_FILE"

if [ $total_files -gt 20 ]; then
    echo "... and $(($total_files - 20)) more files"
fi

echo ""
echo "Category breakdown:"
for category in "${!category_totals[@]}"; do
    printf "  %-10s : %8.2f MB\n" "$category" "${category_totals[$category]}"
done

echo ""
echo "========================================"
printf "Total: %d files | %.2f MB\n" "$total_files" "$total_size"
echo "========================================"
echo ""

# Ask for confirmation
read -p "Archive these files to S3? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Archiving cancelled."
    rm "$TEMP_FILE"
    exit 0
fi

# Create archive manifest
MANIFEST_FILE="$BASE_DIR/archive_manifest_${ARCHIVE_DATE}.json"
echo "{" > "$MANIFEST_FILE"
echo "  \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"," >> "$MANIFEST_FILE"
echo "  \"source\": \"$BASE_DIR\"," >> "$MANIFEST_FILE"
echo "  \"destination\": \"$S3_BUCKET/$ARCHIVE_PREFIX\"," >> "$MANIFEST_FILE"
echo "  \"files\": [" >> "$MANIFEST_FILE"

# Archive files
successful=0
failed=0
first=true

while IFS='|' read -r size_mb category rel_path full_path; do
    s3_path="$S3_BUCKET/$ARCHIVE_PREFIX/$rel_path"
    
    echo -n "Uploading: $rel_path ... "
    
    if aws s3 cp "$full_path" "$s3_path" --quiet; then
        echo -e "${GREEN}✓${NC}"
        ((successful++))
        
        # Add to manifest
        if [ "$first" = false ]; then
            echo "," >> "$MANIFEST_FILE"
        fi
        first=false
        
        cat >> "$MANIFEST_FILE" << EOF
    {
      "path": "$rel_path",
      "size_mb": $size_mb,
      "s3_location": "$s3_path",
      "status": "success"
    }
EOF
        
        # Ask about deletion
        read -p "Delete local file? (y/n/all): " delete
        if [ "$delete" = "y" ] || [ "$delete" = "yes" ]; then
            rm "$full_path"
            echo "  Deleted local file"
        elif [ "$delete" = "all" ]; then
            # Auto-delete mode
            rm "$full_path"
            echo "  Deleted local file"
            # Continue with auto-delete for remaining files
            while IFS='|' read -r size_mb category rel_path full_path; do
                s3_path="$S3_BUCKET/$ARCHIVE_PREFIX/$rel_path"
                echo -n "Uploading: $rel_path ... "
                if aws s3 cp "$full_path" "$s3_path" --quiet; then
                    echo -e "${GREEN}✓${NC}"
                    rm "$full_path"
                    echo "  Deleted local file"
                    ((successful++))
                else
                    echo -e "${RED}✗${NC}"
                    ((failed++))
                fi
            done < "$TEMP_FILE"
            break
        fi
    else
        echo -e "${RED}✗${NC}"
        ((failed++))
    fi
done < "$TEMP_FILE"

# Close manifest
echo "" >> "$MANIFEST_FILE"
echo "  ]," >> "$MANIFEST_FILE"
echo "  \"summary\": {" >> "$MANIFEST_FILE"
echo "    \"successful\": $successful," >> "$MANIFEST_FILE"
echo "    \"failed\": $failed" >> "$MANIFEST_FILE"
echo "  }" >> "$MANIFEST_FILE"
echo "}" >> "$MANIFEST_FILE"

# Cleanup
rm "$TEMP_FILE"

# Upload manifest
echo ""
echo "Uploading manifest..."
aws s3 cp "$MANIFEST_FILE" "$S3_BUCKET/$ARCHIVE_PREFIX/manifest.json"

echo ""
echo "========================================"
echo "ARCHIVE COMPLETE"
echo "========================================"
echo "Successful: $successful"
echo "Failed: $failed"
echo "Manifest: $MANIFEST_FILE"
echo "S3 Location: $S3_BUCKET/$ARCHIVE_PREFIX/"
echo ""
echo "To restore files:"
echo "  aws s3 sync $S3_BUCKET/$ARCHIVE_PREFIX/ $BASE_DIR/"
echo ""
