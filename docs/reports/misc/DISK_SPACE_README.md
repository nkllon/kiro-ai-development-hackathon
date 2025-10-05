# Disk Space Management & S3 Archiving

This directory contains tools to analyze disk usage and archive large files to AWS S3.

## Quick Start

### 1. Quick Analysis (Read-Only)
```bash
python3 quick_analysis.py
```

This will show you:
- File type breakdown by size
- Top 50 largest files
- Recommendations for what to archive

### 2. Detailed Analysis & Interactive Archiving
```bash
python3 archive_to_s3.py
```

When prompted, enter your S3 bucket name (e.g., `my-archive-bucket` or `s3://my-archive-bucket`)

This will:
- Perform detailed disk usage analysis
- Generate an archive plan (saved as `archive_plan.json`)
- Let you review what will be archived
- Upload files to S3 with interactive confirmation
- Ask whether to delete each local file after upload
- Create a manifest of all archived files

### 3. Automated Archiving (Bash)
```bash
chmod +x auto_archive.sh
./auto_archive.sh my-bucket-name
```

This script:
- Finds all files larger than 1MB
- Shows you what will be archived
- Archives to S3 with progress indicators
- Creates a manifest for recovery

## Prerequisites

### AWS CLI
```bash
# Install AWS CLI (if not already installed)
brew install awscli

# Configure credentials
aws configure
```

You'll need:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., us-east-1)

### Python
Python 3.6+ (already installed on your system)

## Current Disk Usage Analysis

Based on the directory listing, here's what's taking up space:

### Large File Categories

1. **PNG Screenshots (~100-110 MB total)**
   - 80+ screenshot files, 1-2 MB each
   - Files like: `screenshot_beast_mode_deployment_*.png`, `our_hackathons_portfolio_*.png`
   - **Recommendation**: Archive all screenshots older than 30 days

2. **Large Scripts (~10 MB)**
   - `comprehensive_migration.sh` (6.06 MB)
   - Various automation scripts

3. **Log Files (~10-15 MB)**
   - `directus_scan_*.log`
   - `tso.log` (607 KB)
   - `emoji_rain_debug.log` (343 KB)
   - **Recommendation**: Archive logs older than 7 days

4. **Lock Files**
   - `uv.lock` (956 KB)
   
5. **JSON Configuration**
   - Various coverage and test result files

### Total Space Usage
- **Total Directory Size**: ~130 MB
- **Archivable Content**: ~100-110 MB (screenshots + old logs)
- **Potential Space Savings**: 75-85%

## Archive Strategies

### Strategy 1: Archive by Date
Archive files older than a certain date (e.g., 30 days for screenshots, 7 days for logs)

### Strategy 2: Archive by Type
- All PNG/JPG screenshots → S3
- Old log files → S3
- Backup directories → S3

### Strategy 3: Archive by Size
Archive all files larger than 500KB or 1MB threshold

## S3 Bucket Setup

### Create an S3 Bucket
```bash
# Using AWS CLI
aws s3 mb s3://my-archive-bucket --region us-east-1

# Set up lifecycle policy (optional - for cost savings)
# This will move files to cheaper storage after 30 days
aws s3api put-bucket-lifecycle-configuration \
  --bucket my-archive-bucket \
  --lifecycle-configuration file://lifecycle-policy.json
```

### Example Lifecycle Policy (lifecycle-policy.json)
```json
{
  "Rules": [
    {
      "Id": "ArchiveOldFiles",
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "GLACIER"
        },
        {
          "Days": 90,
          "StorageClass": "DEEP_ARCHIVE"
        }
      ]
    }
  ]
}
```

### Cost Estimate
- **S3 Standard**: ~$0.023/GB/month
- **S3 Glacier**: ~$0.004/GB/month (after 30 days)
- **S3 Deep Archive**: ~$0.00099/GB/month (after 90 days)

For 100MB of data:
- S3 Standard: ~$0.0023/month
- Glacier: ~$0.0004/month
- Deep Archive: ~$0.0001/month

## Restoring Archived Files

### Restore All Files
```bash
# Sync entire archive back to local directory
aws s3 sync s3://my-bucket/archive_20241001_120000/ /Users/lou/kiro-2/kiro-ai-development-hackathon/
```

### Restore Specific File
```bash
# Download a specific file
aws s3 cp s3://my-bucket/archive_20241001_120000/screenshot.png ./screenshot.png
```

### Restore from Glacier (if using lifecycle policy)
```bash
# First, initiate restore request
aws s3api restore-object \
  --bucket my-bucket \
  --key archive_20241001_120000/screenshot.png \
  --restore-request Days=7,GlacierJobParameters={Tier=Standard}

# Wait 3-5 hours, then download
aws s3 cp s3://my-bucket/archive_20241001_120000/screenshot.png ./screenshot.png
```

## Best Practices

### 1. Regular Cleanup Schedule
```bash
# Add to cron for weekly execution
0 2 * * 0 cd /Users/lou/kiro-2/kiro-ai-development-hackathon && ./auto_archive.sh my-bucket
```

### 2. Verify Before Deleting
Always verify files are successfully uploaded to S3 before deleting local copies:
```bash
# Check file exists in S3
aws s3 ls s3://my-bucket/archive_20241001_120000/screenshot.png

# Compare checksums
local_md5=$(md5 -q screenshot.png)
s3_etag=$(aws s3api head-object --bucket my-bucket --key archive_20241001_120000/screenshot.png --query ETag --output text | tr -d '"')
```

### 3. Keep Manifests
Archive manifests (`archive_manifest_*.json`) contain:
- List of all archived files
- S3 locations
- Original file sizes
- Archive timestamps

**Never delete manifest files** - they're your recovery map!

### 4. Tag Your Archives
```bash
# Add tags to S3 objects for better organization
aws s3api put-object-tagging \
  --bucket my-bucket \
  --key archive_20241001_120000/screenshot.png \
  --tagging 'TagSet=[{Key=project,Value=hackathon},{Key=type,Value=screenshot}]'
```

## Recommended Archiving Plan

Based on your current directory structure:

### Phase 1: Screenshots (Immediate - ~100MB savings)
```bash
# Archive all PNG screenshots
./auto_archive.sh my-bucket
# When prompted, select "yes" for PNG files
# Delete local copies after confirming upload
```

### Phase 2: Old Logs (Week 2 - ~10MB savings)
```bash
# Archive log files older than 7 days
find . -name "*.log" -mtime +7 -exec aws s3 cp {} s3://my-bucket/logs/ \; -delete
```

### Phase 3: Backups Directory (Week 3)
```bash
# If backup directories exist, archive them
aws s3 sync ./backups/ s3://my-bucket/backups/
rm -rf ./backups/
```

## Troubleshooting

### AWS CLI Not Found
```bash
# Install AWS CLI
brew install awscli
# Or using pip
pip3 install awscli
```

### Permission Denied Errors
```bash
# Make scripts executable
chmod +x auto_archive.sh
chmod +x quick_analysis.py
chmod +x archive_to_s3.py
```

### AWS Credentials Error
```bash
# Check current credentials
aws sts get-caller-identity

# Reconfigure if needed
aws configure

# Or use environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

### S3 Access Denied
Ensure your IAM user/role has these permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-bucket",
        "arn:aws:s3:::my-bucket/*"
      ]
    }
  ]
}
```

## Advanced Usage

### Selective Archiving by Pattern
```python
# Edit archive_to_s3.py to customize ARCHIVE_PATTERNS
ARCHIVE_PATTERNS = {
    'screenshots': ['*screenshot*.png', '*_page.png'],
    'logs': ['*.log', '*.txt'],
    'old_scripts': ['*_old.sh', '*_backup.py'],
}
```

### Compression Before Upload
```bash
# Compress files before archiving to save space and costs
tar -czf screenshots.tar.gz *.png
aws s3 cp screenshots.tar.gz s3://my-bucket/archives/
rm *.png
```

### Parallel Uploads (Faster)
```bash
# Use AWS CLI's built-in parallel upload
aws configure set default.s3.max_concurrent_requests 20
aws s3 sync . s3://my-bucket/archive/ --exclude "*" --include "*.png"
```

## Monitoring & Alerts

### Check Archive Size
```bash
# See how much space your archives are using
aws s3 ls s3://my-bucket/ --recursive --human-readable --summarize
```

### Set up CloudWatch Billing Alerts
```bash
# Create SNS topic for alerts
aws sns create-topic --name s3-cost-alerts

# Subscribe to alerts
aws sns subscribe --topic-arn arn:aws:sns:us-east-1:123456789:s3-cost-alerts \
  --protocol email --notification-endpoint your-email@example.com
```

## Files Created by These Tools

- `quick_analysis.py` - Fast read-only analysis
- `archive_to_s3.py` - Interactive Python archiving tool
- `auto_archive.sh` - Automated bash archiving script
- `archive_plan.json` - Generated archive plan (from archive_to_s3.py)
- `archive_manifest_*.json` - Archive manifests (one per archive operation)
- `DISK_SPACE_README.md` - This file

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review AWS CLI documentation: https://docs.aws.amazon.com/cli/
3. Check S3 pricing: https://aws.amazon.com/s3/pricing/

---

**Last Updated**: October 1, 2025
**Repository**: /Users/lou/kiro-2/kiro-ai-development-hackathon
