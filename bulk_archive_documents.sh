#!/bin/bash
# Bulk Documents Archiver
# Archives old or large folders from Documents to S3

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

DOCS_DIR="${1:-$HOME/Documents}"
S3_BUCKET="${2:-}"

echo "=========================================="
echo "BULK DOCUMENTS ARCHIVER"
echo "=========================================="
echo ""
echo "Documents Directory: $DOCS_DIR"

if [ -z "$S3_BUCKET" ]; then
    read -p "Enter S3 bucket name: " S3_BUCKET
fi

if [ -z "$S3_BUCKET" ]; then
    echo -e "${RED}Error: S3 bucket required${NC}"
    exit 1
fi

if [[ ! $S3_BUCKET == s3://* ]]; then
    S3_BUCKET="s3://${S3_BUCKET}"
fi

echo "S3 Bucket: $S3_BUCKET"
echo ""

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI not found${NC}"
    echo "Install with: brew install awscli"
    exit 1
fi

# Check credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS credentials not configured${NC}"
    echo "Run: aws configure"
    exit 1
fi

echo -e "${GREEN}✓ AWS configured${NC}"
echo ""

# Function to get folder size
get_folder_size() {
    du -sh "$1" 2>/dev/null | cut -f1
}

# Function to get last modified date
get_last_modified() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        stat -f "%Sm" -t "%Y-%m-%d" "$1" 2>/dev/null || echo "Unknown"
    else
        stat -c "%y" "$1" 2>/dev/null | cut -d' ' -f1 || echo "Unknown"
    fi
}

# Find folders to archive
echo "Scanning for archive candidates..."
echo ""

TEMP_FILE=$(mktemp)

find "$DOCS_DIR" -maxdepth 1 -type d ! -name "." ! -name ".." 2>/dev/null | while read -r folder; do
    if [ "$folder" = "$DOCS_DIR" ]; then
        continue
    fi
    
    size=$(get_folder_size "$folder")
    last_mod=$(get_last_modified "$folder")
    
    # Convert size to bytes for comparison
    size_bytes=0
    if [[ $size =~ ^([0-9.]+)G$ ]]; then
        size_bytes=$(echo "${BASH_REMATCH[1]} * 1073741824" | bc | cut -d. -f1)
    elif [[ $size =~ ^([0-9.]+)M$ ]]; then
        size_bytes=$(echo "${BASH_REMATCH[1]} * 1048576" | bc | cut -d. -f1)
    fi
    
    # Check if >100MB or old
    if [ "$size_bytes" -gt 104857600 ]; then  # >100MB
        echo "$size|$last_mod|$(basename "$folder")|$folder" >> "$TEMP_FILE"
    fi
done

if [ ! -s "$TEMP_FILE" ]; then
    echo "No folders found for archiving"
    rm "$TEMP_FILE"
    exit 0
fi

# Sort by size (reverse)
sort -t'|' -k1 -rh "$TEMP_FILE" -o "$TEMP_FILE"

echo "=========================================="
echo "ARCHIVE CANDIDATES"
echo "=========================================="
echo ""
printf "%-15s %-12s %s\n" "Size" "Last Modified" "Folder"
echo "------------------------------------------"

while IFS='|' read -r size last_mod name full_path; do
    printf "%-15s %-12s %s\n" "$size" "$last_mod" "$name"
done < "$TEMP_FILE"

echo ""
read -p "Review folders and press Enter to continue (or Ctrl+C to cancel)..."
echo ""

# Archive each folder
ARCHIVE_DATE=$(date +%Y%m%d_%H%M%S)
SUCCESS=0
FAILED=0

while IFS='|' read -r size last_mod name full_path; do
    echo ""
    echo "=========================================="
    echo "Folder: $name"
    echo "Size: $size"
    echo "Last Modified: $last_mod"
    echo "=========================================="
    
    read -p "Archive this folder? (y/n/quit): " response
    
    case $response in
        [Yy]*)
            S3_PATH="$S3_BUCKET/documents_archive_${ARCHIVE_DATE}/$name"
            
            echo "Uploading to: $S3_PATH"
            
            if aws s3 sync "$full_path" "$S3_PATH" --storage-class STANDARD; then
                echo -e "${GREEN}✓ Upload successful${NC}"
                ((SUCCESS++))
                
                # Verify upload
                echo "Verifying..."
                LOCAL_COUNT=$(find "$full_path" -type f | wc -l | tr -d ' ')
                S3_COUNT=$(aws s3 ls "$S3_PATH" --recursive | wc -l | tr -d ' ')
                
                echo "Local files: $LOCAL_COUNT"
                echo "S3 files: $S3_COUNT"
                
                if [ "$LOCAL_COUNT" -eq "$S3_COUNT" ]; then
                    echo -e "${GREEN}✓ Verification passed${NC}"
                    
                    read -p "Delete local folder? (yes/no): " delete_response
                    if [ "$delete_response" = "yes" ]; then
                        rm -rf "$full_path"
                        echo -e "${GREEN}✓ Local folder deleted${NC}"
                    fi
                else
                    echo -e "${YELLOW}⚠ File count mismatch - keeping local copy${NC}"
                fi
            else
                echo -e "${RED}✗ Upload failed${NC}"
                ((FAILED++))
            fi
            ;;
        [Qq]*)
            echo "Quitting..."
            break
            ;;
        *)
            echo "Skipped"
            ;;
    esac
done < "$TEMP_FILE"

rm "$TEMP_FILE"

echo ""
echo "=========================================="
echo "ARCHIVE COMPLETE"
echo "=========================================="
echo "Successful: $SUCCESS"
echo "Failed: $FAILED"
echo ""
echo "Archive location: $S3_BUCKET/documents_archive_${ARCHIVE_DATE}/"
echo ""
echo "To restore:"
echo "  aws s3 sync $S3_BUCKET/documents_archive_${ARCHIVE_DATE}/folder_name/ ./folder_name/"
echo ""
