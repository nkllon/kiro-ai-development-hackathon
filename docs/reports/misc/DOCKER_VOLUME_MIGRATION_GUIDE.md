# Docker Volume Migration Guide
**Fixing the January 27, 2025 Incident - Data in Two Places**

## 🎯 **The Problem**
You have data in **two places**:
1. **Host directories** (in git): `deployment/observatory/grafana-data/` & `prometheus-data/`
2. **Docker volumes**: `observatory_grafana_data` & `observatory_prometheus_data`

We need to consolidate to **Docker volumes only** and remove the host directories from git.

## 🚀 **Automated Solution (Recommended)**

```bash
# Run the migration script
python scripts/fix_docker_volume_migration.py
```

This script will:
- ✅ Stop containers safely
- ✅ Backup both data sources
- ✅ Migrate data to Docker volumes
- ✅ Fix docker-compose.yml
- ✅ Clean up git tracking
- ✅ Verify the migration

## 🔧 **Manual Solution (Step by Step)**

### **Step 1: Stop Everything**
```bash
# Stop observatory containers
docker-compose -f deployment/observatory/docker-compose.yml down

# Verify nothing is running
docker ps --filter name=observatory
```

### **Step 2: Backup Current State**
```bash
# Create backup directory
mkdir docker-migration-backup-$(date +%Y%m%d)
cd docker-migration-backup-$(date +%Y%m%d)

# Backup host directories
cp -r ../deployment/observatory/grafana-data ./host-grafana-data
cp -r ../deployment/observatory/prometheus-data ./host-prometheus-data

# Backup Docker volumes
docker run --rm -v observatory_grafana_data:/data -v $(pwd):/backup alpine tar czf /backup/docker-grafana.tar.gz -C /data .
docker run --rm -v observatory_prometheus_data:/data -v $(pwd):/backup alpine tar czf /backup/docker-prometheus.tar.gz -C /data .

cd ..
```

### **Step 3: Compare Data Sources**
```bash
# Check host directory sizes
echo "Host Grafana files: $(find deployment/observatory/grafana-data -type f | wc -l)"
echo "Host Prometheus files: $(find deployment/observatory/prometheus-data -type f | wc -l)"

# Check Docker volume sizes
echo "Docker Grafana files: $(docker run --rm -v observatory_grafana_data:/data alpine find /data -type f | wc -l)"
echo "Docker Prometheus files: $(docker run --rm -v observatory_prometheus_data:/data alpine find /data -type f | wc -l)"
```

### **Step 4: Migrate Data (Choose the Larger Dataset)**

**If host directories have more data:**
```bash
# Migrate Grafana data
docker run --rm -v $(pwd)/deployment/observatory/grafana-data:/source -v observatory_grafana_data:/dest alpine sh -c 'cp -r /source/* /dest/'

# Migrate Prometheus data  
docker run --rm -v $(pwd)/deployment/observatory/prometheus-data:/source -v observatory_prometheus_data:/dest alpine sh -c 'cp -r /source/* /dest/'
```

**If Docker volumes have more data:**
```bash
# Keep Docker volumes as-is (they're already the source of truth)
echo "Docker volumes have more data - keeping them as primary"
```

### **Step 5: Fix docker-compose.yml**
```bash
# Edit deployment/observatory/docker-compose.yml
# Change these lines:
```

**FROM:**
```yaml
grafana:
  volumes:
    - ${GRAFANA_DATA_PATH:-./grafana-data}:/var/lib/grafana

prometheus:
  volumes:
    - ${PROMETHEUS_DATA_PATH:-./prometheus-data}:/prometheus
```

**TO:**
```yaml
grafana:
  volumes:
    - grafana_data:/var/lib/grafana

prometheus:
  volumes:
    - prometheus_data:/prometheus

# Add to volumes section:
volumes:
  grafana_data:
    driver: local
  prometheus_data:
    driver: local
```

### **Step 6: Clean Up Git Tracking**
```bash
# Remove from git tracking
git rm -r --cached deployment/observatory/grafana-data/
git rm -r --cached deployment/observatory/prometheus-data/

# Update .gitignore
cat >> .gitignore << EOF

# Deployment data governance
**/grafana-data/
**/prometheus-data/
*.db
*.exe
**/logs/
**/cache/
**/tmp/
EOF
```

### **Step 7: Test the Migration**
```bash
# Start containers with new configuration
docker-compose -f deployment/observatory/docker-compose.yml up -d

# Check containers are running
docker ps --filter name=observatory

# Check Grafana (should have your dashboards)
curl -s http://localhost:3000/api/health

# Check Prometheus (should have your data)
curl -s http://localhost:9090/-/healthy
```

### **Step 8: Verify Data Integrity**
```bash
# Check Grafana UI
open http://localhost:3000

# Check Prometheus UI  
open http://localhost:9090

# Verify your dashboards and data are intact
```

### **Step 9: Final Cleanup**
```bash
# Commit the .gitignore changes
git add .gitignore
git commit -m "🚨 Fix deployment data governance - migrate to Docker volumes"

# Run the auditor to verify cleanup
python scripts/deployment_auditor_scan.py deployment/

# Should show 0 violations now!
```

### **Step 10: Remove Host Directories (After Verification)**
```bash
# ONLY after verifying everything works
rm -rf deployment/observatory/grafana-data/
rm -rf deployment/observatory/prometheus-data/

# Run auditor again - should be completely clean
python scripts/deployment_auditor_scan.py deployment/
```

## 🎯 **Expected Results**

**Before migration:**
- ❌ 378 violations in deployment auditor
- ❌ Data in two places
- ❌ Git repository polluted with binary files

**After migration:**
- ✅ 0 violations in deployment auditor  
- ✅ Data only in Docker volumes
- ✅ Clean git repository
- ✅ Proper backup strategy

## 🚨 **Emergency Rollback**

If something goes wrong:
```bash
# Stop containers
docker-compose -f deployment/observatory/docker-compose.yml down

# Restore from backup
cp -r docker-migration-backup-*/host-grafana-data deployment/observatory/grafana-data
cp -r docker-migration-backup-*/host-prometheus-data deployment/observatory/prometheus-data

# Restore original docker-compose.yml from git
git checkout deployment/observatory/docker-compose.yml

# Start with original configuration
docker-compose -f deployment/observatory/docker-compose.yml up -d
```

## 💡 **Why This Fixes Everything**

1. **Consolidates data** to proper Docker volumes
2. **Removes 378 files** from git tracking
3. **Fixes the root cause** of the January 27, 2025 incident
4. **Enables proper backups** via Docker volume management
5. **Prevents future violations** with updated .gitignore

**Bottom line:** This migration gets you out of the mess by choosing Docker volumes as the single source of truth and properly configuring the containers to never write to the git repository again.