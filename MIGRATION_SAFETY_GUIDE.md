# Migration Safety Guide
**Complete Test & Rollback Plan for Docker Volume Migration**

## 🧪 **Testing Strategy**

### **Step 1: Run the Test Suite (MANDATORY)**
```bash
python scripts/test_docker_migration.py
```

**What it tests:**
- ✅ Environment creation with mock data
- ✅ Data comparison logic
- ✅ docker-compose.yml modification
- ✅ .gitignore update logic
- ✅ Backup creation procedures
- ✅ Complete rollback procedures

**Expected output:** All tests should pass before proceeding.

### **Step 2: Dry Run Analysis**
```bash
# Check current state
python scripts/deployment_auditor_scan.py deployment/ --quiet

# Check what containers are running
docker ps --filter name=observatory

# Check current volumes
docker volume ls | grep observatory

# Check current data sizes
find deployment/observatory/grafana-data -type f | wc -l
find deployment/observatory/prometheus-data -type f | wc -l
```

## 🚀 **Migration Execution**

### **Step 3: Run the Migration**
```bash
python scripts/fix_docker_volume_migration.py
```

**What it does:**
1. **Safety check** - Ensures you ran the test suite
2. **Pre-flight checks** - Verifies Docker is running
3. **Container management** - Stops containers safely
4. **Backup creation** - Full backup of both data sources
5. **Data analysis** - Compares host vs Docker volume data
6. **Data migration** - Moves data to Docker volumes
7. **Configuration fix** - Updates docker-compose.yml
8. **Git cleanup** - Removes files from tracking, updates .gitignore
9. **Verification** - Tests that everything works

## 🔄 **Rollback Plan**

### **Automatic Rollback (If Migration Fails)**
The migration script includes automatic rollback if verification fails.

### **Manual Rollback (If Needed Later)**
```bash
python scripts/rollback_docker_migration.py
```

**What rollback does:**
1. **Finds backups** - Lists available backup directories
2. **Backup selection** - Lets you choose which backup to restore
3. **Verification** - Checks backup integrity
4. **Container stop** - Safely stops all containers
5. **Data restoration** - Restores both host directories and Docker volumes
6. **Configuration restore** - Restores original docker-compose.yml and .gitignore
7. **Git restoration** - Re-adds directories to git tracking
8. **Verification** - Tests that rollback worked

### **Emergency Manual Rollback**
If scripts fail, manual rollback:

```bash
# 1. Stop containers
docker-compose -f deployment/observatory/docker-compose.yml down

# 2. Restore data from backup (replace TIMESTAMP with actual backup)
cp -r docker-migration-backup-TIMESTAMP/host-grafana-data deployment/observatory/grafana-data
cp -r docker-migration-backup-TIMESTAMP/host-prometheus-data deployment/observatory/prometheus-data

# 3. Restore configuration files
git checkout deployment/observatory/docker-compose.yml
git checkout .gitignore

# 4. Re-add to git tracking
git add deployment/observatory/grafana-data/
git add deployment/observatory/prometheus-data/

# 5. Test containers
docker-compose -f deployment/observatory/docker-compose.yml up -d
```

## 📊 **Verification Checklist**

### **After Migration:**
- [ ] Containers start successfully
- [ ] Grafana UI loads with existing dashboards
- [ ] Prometheus UI loads with existing data
- [ ] No violations in deployment auditor scan
- [ ] .gitignore contains governance patterns
- [ ] Host directories removed from git tracking

### **After Rollback:**
- [ ] Host directories restored with original data
- [ ] docker-compose.yml back to original format
- [ ] .gitignore back to original state
- [ ] Containers start with original configuration
- [ ] All data intact and accessible

## 🛡️ **Safety Features**

### **Multiple Backup Layers:**
1. **Host directory backup** - Complete copy of current host directories
2. **Docker volume backup** - Compressed archives of Docker volumes
3. **Configuration backup** - Git can restore original files
4. **Timestamped backups** - Multiple backups preserved

### **Verification at Every Step:**
- ✅ Pre-flight checks before starting
- ✅ Data comparison before migration
- ✅ Backup verification before proceeding
- ✅ Migration verification before completion
- ✅ Container startup testing
- ✅ Data integrity checks

### **Fail-Safe Mechanisms:**
- 🛑 **Stops on errors** - Won't proceed if critical steps fail
- 🔄 **Automatic rollback** - Rolls back if verification fails
- 💾 **Preserves backups** - Never deletes backup data
- 🧪 **Test mode** - Full test suite before real migration

## 📋 **Migration Timeline**

**Estimated time:** 15-30 minutes total

1. **Testing** (5 minutes)
   - Run test suite
   - Analyze current state

2. **Migration** (10-15 minutes)
   - Backup creation
   - Data migration
   - Configuration updates
   - Verification

3. **Validation** (5-10 minutes)
   - Container testing
   - Data integrity checks
   - Final cleanup

## 🚨 **Risk Assessment**

### **Low Risk:**
- ✅ Complete backups before any changes
- ✅ Tested migration logic
- ✅ Automatic rollback capability
- ✅ No data loss possible (backups preserved)

### **Medium Risk:**
- ⚠️ Temporary service downtime during migration
- ⚠️ Potential for configuration issues

### **Mitigation:**
- 🛡️ Run during maintenance window
- 🛡️ Test suite validates all logic
- 🛡️ Rollback script provides quick recovery
- 🛡️ Manual rollback procedures documented

## 🎯 **Success Criteria**

**Migration is successful when:**
1. ✅ Deployment auditor shows 0 violations
2. ✅ Containers start and run normally
3. ✅ Grafana shows all existing dashboards
4. ✅ Prometheus shows all existing data
5. ✅ Git repository is clean (no binary files)
6. ✅ Docker volumes contain all data
7. ✅ Host directories removed from git tracking

**Rollback is successful when:**
1. ✅ System restored to pre-migration state
2. ✅ All data accessible and intact
3. ✅ Containers work with original configuration
4. ✅ Git tracking restored to original state

---

**Bottom line:** This migration has comprehensive testing, multiple backup layers, and proven rollback procedures. The risk is minimal and the benefits (clean git repo, proper Docker volumes) are significant.