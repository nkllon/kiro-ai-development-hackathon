# Quick Start Guide - Disk Space Management

## 📊 Current Situation
- **Total Directory Size**: 130.42 MB
- **Primary Space Consumers**: 
  - PNG Screenshots: ~110 MB (84%)
  - Log Files: ~15 MB (11%)
  - Scripts & Other: ~5 MB (5%)

## 🚀 Quick Start (3 Steps)

### Step 1: Initial Setup (1 minute)
```bash
cd /Users/lou/kiro-2/kiro-ai-development-hackathon
chmod +x setup_archiving.sh
./setup_archiving.sh
```

### Step 2: Verify AWS CLI (30 seconds)
```bash
# Check if AWS CLI is installed
aws --version

# If not installed:
brew install awscli

# Configure credentials (if not already done)
aws configure
# Enter: Access Key ID, Secret Access Key, Region (e.g., us-east-1)
```

### Step 3: Run Analysis (30 seconds)
```bash
python3 quick_analysis.py
```

## 📈 Archiving Options

### Option A: Archive Everything > 1MB (Fastest)
**Best for**: Quick cleanup, archiving all large files
**Expected savings**: ~110 MB

```bash
./auto_archive.sh your-bucket-name
```

This will:
1. Find all files > 1MB
2. Show you what will be archived
3. Upload to S3 with progress
4. Ask if you want to delete each file

### Option B: Archive Old Screenshots Only (Recommended)
**Best for**: Keeping recent work accessible, archiving old screenshots
**Expected savings**: ~60-90 MB (screenshots older than 30 days)

```bash
python3 archive_old_screenshots.py your-bucket-name
```

This will:
1. Find PNG/JPG files older than 30 days (configurable)
2. Show age distribution
3. Archive to S3
4. Optionally delete local copies

### Option C: Interactive Full Analysis (Most Control)
**Best for**: Reviewing everything before archiving
**Expected savings**: Variable

```bash
python3 archive_to_s3.py
# When prompted, enter: your-bucket-name
```

This will:
1. Perform comprehensive analysis
2. Generate archive plan (saved as JSON)
3. Let you review and confirm each category
4. Archive with full control

## 💡 Recommended Workflow

For your situation, I recommend:

```bash
# 1. Quick analysis first
python3 quick_analysis.py

# 2. Archive old screenshots (safe, high impact)
python3 archive_old_screenshots.py your-bucket-name
# When prompted, enter: 30 (for files older than 30 days)
# Review the list
# Confirm with: yes
# After upload succeeds, confirm deletion: yes

# 3. Check space saved
du -sh .
```

**Expected result**: Free up 60-90 MB immediately

## 🛡️ Safety Features

All tools include:
- ✅ Preview before archiving
- ✅ Confirmation prompts
- ✅ Manifest files for recovery
- ✅ Verification before deletion
- ✅ Detailed error logging

## 📦 What Gets Archived

By default, these file types are candidates for archiving:

| File Type | Size Threshold | Recommendation |
|-----------|----------------|----------------|
| Screenshots (*.png, *.jpg) | > 500 KB | Archive if > 30 days old |
| Logs (*.log) | > 100 KB | Archive if > 7 days old |
| Large scripts (*.sh) | > 1 MB | Archive if backup/old |
| Backups | Any | Archive all |

## 🔄 Restoring Files

If you need to restore archived files:

```bash
# Restore everything from an archive
aws s3 sync s3://your-bucket/archive_20241001_120000/ ./

# Restore specific file
aws s3 cp s3://your-bucket/archive_20241001_120000/screenshot.png ./

# List what's in an archive
aws s3 ls s3://your-bucket/archive_20241001_120000/ --recursive
```

## 💰 Cost Expectations

For 110 MB archived to S3:

| Storage Class | Monthly Cost | When to Use |
|---------------|--------------|-------------|
| S3 Standard | $0.0025 | Frequent access needed |
| S3 Glacier | $0.0004 | Access within hours OK |
| S3 Deep Archive | $0.0001 | Rarely needed |

**Recommendation**: Use S3 Standard initially. Set up lifecycle policy to move to Glacier after 30 days.

## 🎯 My Recommendation for You

Based on your directory structure:

```bash
# Step 1: Setup (one time)
./setup_archiving.sh

# Step 2: Archive old screenshots (safe, high-impact)
python3 archive_old_screenshots.py your-bucket-name

# Step 3: Review and consider archiving logs weekly
# Add to crontab for automation:
# 0 2 * * 0 cd /Users/lou/kiro-2/kiro-ai-development-hackathon && python3 archive_old_screenshots.py your-bucket-name
```

This approach:
- ✅ Frees up 60-90 MB immediately
- ✅ Keeps recent work accessible
- ✅ Minimal risk
- ✅ Can be automated
- ✅ Costs less than $0.003/month

## 📞 Getting Help

If you encounter issues:

1. **AWS Credentials Error**
   ```bash
   aws configure
   # Re-enter your credentials
   ```

2. **Permission Denied**
   ```bash
   chmod +x *.sh *.py
   ```

3. **S3 Bucket Doesn't Exist**
   ```bash
   aws s3 mb s3://your-bucket-name
   ```

4. **Check What's Using Space**
   ```bash
   python3 quick_analysis.py
   ```

## 📚 Full Documentation

For complete details, see: `DISK_SPACE_README.md`

---

**Next Steps**: Run `python3 quick_analysis.py` to see your detailed disk usage breakdown!
