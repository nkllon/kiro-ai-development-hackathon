# Finding and Archiving GIGABYTES - Documents Edition

## 🎯 Goal: Find and Archive Gigabytes of Data

This guide helps you identify and archive large folders in ~/Documents that are eating up disk space.

## 🚀 Quick Start

### Step 1: Analyze Your Documents Folder
```bash
cd /Users/lou/kiro-2/kiro-ai-development-hackathon
python3 analyze_documents.py
```

This will show you:
- All folders sorted by size
- Which folders are >1GB
- Which folders haven't been modified in over a year
- High-priority candidates for archiving (old AND large)

### Step 2: Bulk Archive Old/Large Folders
```bash
chmod +x bulk_archive_documents.sh
./bulk_archive_documents.sh ~/Documents your-bucket-name
```

This will:
- Find all folders >100MB in Documents
- Show size and last modified date
- Let you archive each folder interactively
- Verify uploads before allowing deletion
- Track what's been archived

## 📊 What to Look For

### High-Value Targets (Likely Gigabytes):

1. **Old Project Folders**
   - Development projects from old jobs
   - Client work from years ago
   - Archived codebases

2. **Media Libraries**
   - Old photo libraries
   - Video editing projects
   - Audio files

3. **Virtual Machines**
   - Old VM images (.vmdk, .vdi files)
   - Docker volumes
   - Vagrant boxes

4. **Downloads Accumulation**
   - Software installers
   - Old downloads never cleaned up

5. **Backup Folders**
   - Time Machine local snapshots
   - Manual backup folders
   - Sync tool caches

## 🔍 Advanced Analysis

### Analyze a Specific Folder
```bash
python3 analyze_documents.py ~/Documents/OldProjects
```

### Find Largest Files Anywhere
```bash
# Top 20 largest files in Documents
find ~/Documents -type f -exec du -h {} + 2>/dev/null | sort -rh | head -20
```

### Find Folders by Age AND Size
```bash
# Folders >1GB and >1 year old
find ~/Documents -maxdepth 1 -type d -mtime +365 -exec du -sh {} + | grep -E "^[0-9.]+G"
```

### Check Disk Usage by Top-Level Folder
```bash
du -h -d 1 ~/Documents | sort -rh
```

## 💾 Expected Savings

Typical Documents folders contain:

| Category | Typical Size | Archive Priority |
|----------|--------------|------------------|
| Old dev projects | 5-20 GB | High |
| Photo libraries | 10-50 GB | Medium |
| VM images | 5-50 GB per VM | High |
| Old downloads | 2-10 GB | High |
| Work archives | 5-20 GB | High |
| **TOTAL POTENTIAL** | **30-150 GB** | - |

## 📦 Archiving Strategies

### Strategy 1: Archive by Age (Recommended)
Archive folders not touched in 1+ year:

```bash
# Find and review
find ~/Documents -maxdepth 1 -type d -mtime +365 -exec du -sh {} + | sort -rh

# Archive each (replace folder_name)
aws s3 sync ~/Documents/folder_name s3://your-bucket/archive_$(date +%Y%m%d)/folder_name/
```

### Strategy 2: Archive by Size
Archive largest folders first:

```bash
# See largest
du -h -d 1 ~/Documents | sort -rh | head -10

# Archive with bulk script
./bulk_archive_documents.sh ~/Documents your-bucket
```

### Strategy 3: Archive by Type
Target specific file types:

```bash
# Find all .vmdk files (VMs)
find ~/Documents -name "*.vmdk" -exec du -sh {} +

# Archive VM folder
aws s3 sync ~/Documents/VirtualMachines s3://your-bucket/vm_archive/
```

## 🛡️ Safety Checklist

Before archiving LARGE folders (>1GB):

- [ ] Verify AWS credentials work: `aws sts get-caller-identity`
- [ ] Ensure S3 bucket has enough space
- [ ] Upload a test file first: `aws s3 cp testfile.txt s3://your-bucket/test/`
- [ ] Use `--dryrun` first to see what would be uploaded
- [ ] Verify upload completed: compare file counts
- [ ] Keep local copy until verified in S3
- [ ] Save manifest of what was archived

## 💰 Cost for Gigabytes

### S3 Storage Costs

| Data Size | S3 Standard | S3 Glacier | Deep Archive |
|-----------|-------------|------------|--------------|
| 10 GB | $0.23/mo | $0.04/mo | $0.01/mo |
| 50 GB | $1.15/mo | $0.20/mo | $0.05/mo |
| 100 GB | $2.30/mo | $0.40/mo | $0.10/mo |
| 500 GB | $11.50/mo | $2.00/mo | $0.50/mo |

**Recommendation**: Use S3 Standard initially, then lifecycle to Glacier after 30-90 days.

### Setting Up Lifecycle Policy

```bash
# Create lifecycle-policy.json
cat > lifecycle-policy.json << 'EOF'
{
  "Rules": [
    {
      "Id": "ArchiveOldDocuments",
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        },
        {
          "Days": 365,
          "StorageClass": "DEEP_ARCHIVE"
        }
      ],
      "Prefix": "documents_archive_"
    }
  ]
}
EOF

# Apply to bucket
aws s3api put-bucket-lifecycle-configuration \
  --bucket your-bucket \
  --lifecycle-configuration file://lifecycle-policy.json
```

## 📋 Example Workflow

Real example archiving 50GB of old projects:

```bash
# 1. Analyze
python3 analyze_documents.py ~/Documents

# Output shows:
# OldProjects/      15.2 GB    Last modified: 2022-03-15
# ClientWork2021/   12.8 GB    Last modified: 2021-11-20
# PhotoLibrary/     18.5 GB    Last modified: 2023-06-10
# VMs/               8.3 GB    Last modified: 2020-08-05

# 2. Archive old projects (not touched in >1 year)
aws s3 sync ~/Documents/OldProjects s3://my-archive/documents_20241001/OldProjects/
aws s3 sync ~/Documents/ClientWork2021 s3://my-archive/documents_20241001/ClientWork2021/
aws s3 sync ~/Documents/VMs s3://my-archive/documents_20241001/VMs/

# 3. Verify (check file counts match)
find ~/Documents/OldProjects -type f | wc -l
aws s3 ls s3://my-archive/documents_20241001/OldProjects/ --recursive | wc -l

# 4. Delete local copies (only after verification!)
rm -rf ~/Documents/OldProjects
rm -rf ~/Documents/ClientWork2021
rm -rf ~/Documents/VMs

# Total saved: ~36 GB
# Monthly cost: $0.83 (Standard) or $0.14 (Glacier after 90 days)
```

## 🔄 Restoring Archives

### Restore Entire Folder
```bash
aws s3 sync s3://your-bucket/documents_archive_20241001/OldProjects/ ~/Documents/OldProjects/
```

### Restore Single File
```bash
aws s3 cp s3://your-bucket/documents_archive_20241001/OldProjects/file.txt ~/Documents/
```

### From Glacier (requires restore request)
```bash
# 1. Request restore (takes 3-5 hours)
aws s3api restore-object \
  --bucket your-bucket \
  --key documents_archive_20241001/OldProjects/file.txt \
  --restore-request Days=7,GlacierJobParameters={Tier=Standard}

# 2. Wait 3-5 hours

# 3. Download
aws s3 cp s3://your-bucket/documents_archive_20241001/OldProjects/file.txt ./
```

## 🎯 Recommended Action Plan

For finding gigabytes in Documents:

```bash
# Day 1: Analysis (15 minutes)
python3 analyze_documents.py ~/Documents > ~/Documents/space_analysis.txt
cat ~/Documents/space_analysis.txt

# Identify top 5-10 largest old folders

# Day 2: Archive (1-2 hours depending on size)
./bulk_archive_documents.sh ~/Documents your-bucket

# Select folders that are:
# - >1GB AND >1 year old (high priority)
# - >5GB AND >6 months old (medium priority)

# Expected savings: 30-150 GB
```

## 📝 Keep a Log

Create an archive log:

```bash
cat > ~/Documents/ARCHIVED_FOLDERS.txt << EOF
Archive Date: $(date)
S3 Bucket: s3://your-bucket/documents_archive_$(date +%Y%m%d)/

Archived Folders:
- OldProjects/ (15.2 GB)
- ClientWork2021/ (12.8 GB)
- VMs/ (8.3 GB)

Total Archived: 36.3 GB
Monthly Cost: ~$0.83 (reducing to ~$0.14 after lifecycle)

To restore:
aws s3 sync s3://your-bucket/documents_archive_$(date +%Y%m%d)/FOLDER_NAME/ ~/Documents/FOLDER_NAME/
EOF
```

## ⚡ Quick Commands Reference

```bash
# Analyze Documents
python3 analyze_documents.py ~/Documents

# Bulk archive
./bulk_archive_documents.sh ~/Documents bucket-name

# Check bucket contents
aws s3 ls s3://your-bucket/ --recursive --human-readable --summarize

# Check local disk space
df -h ~

# Find largest folders
du -h -d 1 ~/Documents | sort -rh | head -20
```

---

**Remember**: Always verify uploads before deleting local files!

For gigabytes of data, expect:
- Upload time: 1-5 hours depending on connection
- Monthly cost: $2-5 for 100GB
- Space savings: 30-150GB typical
