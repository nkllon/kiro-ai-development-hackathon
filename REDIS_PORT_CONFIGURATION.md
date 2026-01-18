# Redis Port Configuration - Avoiding Cluster Conflict

**Issue**: Existing Redis cluster on network using port 6379  
**Solution**: Run Beast Mode Redis on port 6380  
**Date**: 2025-10-13

---

## 🔧 Port Configuration

### Network Setup
- **Existing Redis Cluster**: Port `6379` (network-wide)
- **Beast Mode Redis**: Port `6380` (this instance)
- **Redis Commander**: Port `8081` (optional UI)
- **Redis Exporter**: Port `9121` (optional monitoring)

### Why Port 6380?
1. Avoids conflict with existing cluster on 6379
2. Standard alternative Redis port
3. Allows both instances to coexist
4. Easy to remember (6379 + 1)

---

## 📝 Updated Configuration

### Docker Compose
```yaml
# docker-compose.redis.yml
redis:
  ports:
    - "6380:6379"  # External:Internal
```

**Note**: Inside the container, Redis still runs on 6379. We map external port 6380 to internal 6379.

### Environment Variables
```bash
# redis.env or .env
REDIS_HOST=localhost
REDIS_PORT=6380          # Changed from 6379
REDIS_PASSWORD=beastmode2025
REDIS_URL=redis://:beastmode2025@localhost:6380/0
```

### Application Configuration
Update any hardcoded references:
```python
# Before
redis_config = RedisConfig(host="localhost", port=6379)

# After  
redis_config = RedisConfig(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6380))
)
```

---

## ✅ Quick Start (Updated)

### 1. Start Beast Mode Redis
```bash
# Create data directory
mkdir -p data/redis

# Start on port 6380
docker-compose -f docker-compose.redis.yml up -d
```

### 2. Verify Running on Correct Port
```bash
# Check port mapping
docker port beast-mode-redis

# Should show: 6379/tcp -> 0.0.0.0:6380

# Test connection
redis-cli -p 6380 -a beastmode2025 ping
# Should return: PONG
```

### 3. Test from Python
```bash
source venv/bin/activate
python -c "import redis; r = redis.Redis(host='localhost', port=6380, password='beastmode2025'); print('PING:', r.ping())"
```

---

## 🔍 Verification Commands

### Check Both Redis Instances

```bash
# Existing cluster (if accessible)
redis-cli -p 6379 ping

# Beast Mode Redis
redis-cli -p 6380 -a beastmode2025 ping
```

### Verify Port Usage
```bash
# Check what's listening on Redis ports
netstat -an | grep 6379
netstat -an | grep 6380

# Or using lsof
lsof -i :6379
lsof -i :6380

# Docker port mapping
docker ps | grep redis
docker port beast-mode-redis
```

### Connection Test Script
```python
# test_both_redis.py
import redis

print("Testing Redis instances...")

# Test existing cluster (if accessible locally)
try:
    r_cluster = redis.Redis(host='localhost', port=6379, decode_responses=True)
    print(f"✅ Cluster (6379): {r_cluster.ping()}")
except Exception as e:
    print(f"❌ Cluster (6379): {e}")

# Test Beast Mode Redis
try:
    r_beast = redis.Redis(host='localhost', port=6380, password='beastmode2025', decode_responses=True)
    print(f"✅ Beast Mode (6380): {r_beast.ping()}")
    
    # Test operations
    r_beast.set('beast_mode:test', 'working')
    print(f"✅ Beast Mode (6380) Write/Read: {r_beast.get('beast_mode:test')}")
except Exception as e:
    print(f"❌ Beast Mode (6380): {e}")
```

---

## 🚨 Important Notes

### 1. Port Consistency
**Ensure all configuration uses port 6380:**
- ✅ docker-compose.redis.yml
- ✅ redis.env.example
- ✅ Application .env files
- ✅ Python code environment variables
- ✅ Documentation examples

### 2. Connection Strings
Update all connection strings:
```bash
# Old (conflicts with cluster)
redis://localhost:6379

# New (Beast Mode specific)
redis://localhost:6380
redis://:beastmode2025@localhost:6380/0
```

### 3. Firewall Rules
If you have firewall rules, ensure port 6380 is allowed:
```bash
# UFW (Ubuntu)
sudo ufw allow 6380/tcp

# iptables
sudo iptables -A INPUT -p tcp --dport 6380 -j ACCEPT

# macOS (usually not needed for localhost)
```

### 4. Network Isolation
The two Redis instances are completely separate:
- Different ports
- Different data
- Different authentication
- No communication between them

---

## 📊 Comparison

| Aspect | Existing Cluster | Beast Mode Redis |
|--------|-----------------|------------------|
| Port | 6379 | 6380 |
| Purpose | Network-wide services | Beast Mode Observatory |
| Authentication | (Unknown) | Password: beastmode2025 |
| Data | Shared cluster data | Beast Mode specific |
| Management | Network admin | Local control |
| Container | (Unknown) | beast-mode-redis |

---

## 🔧 Troubleshooting

### "Address already in use" Error
```bash
# Check what's on the port
lsof -i :6380

# If something is there, either:
# 1. Stop it
# 2. Use a different port in .env:
echo "REDIS_PORT=6381" >> .env
```

### Can't Connect on Port 6380
```bash
# 1. Verify Redis is running
docker ps | grep beast-mode-redis

# 2. Check port mapping
docker port beast-mode-redis

# 3. Test from inside container
docker exec beast-mode-redis redis-cli ping

# 4. Test from host
redis-cli -p 6380 -a beastmode2025 ping
```

### Application Still Trying Port 6379
```bash
# 1. Check environment variables
env | grep REDIS

# 2. Update .env file
cat > .env << EOF
REDIS_HOST=localhost
REDIS_PORT=6380
REDIS_PASSWORD=beastmode2025
EOF

# 3. Restart application
```

### Need to Change Port Again
Edit `docker-compose.redis.yml`:
```yaml
ports:
  - "6381:6379"  # Use 6381 instead
```

Then update all configs:
```bash
# Update environment
export REDIS_PORT=6381
echo "REDIS_PORT=6381" >> .env

# Restart container
docker-compose -f docker-compose.redis.yml down
docker-compose -f docker-compose.redis.yml up -d
```

---

## 🎯 Checklist

Before running application:
- [ ] Existing cluster confirmed on port 6379
- [ ] Beast Mode Redis configured for port 6380
- [ ] Docker container running on correct port
- [ ] Environment variables updated (port 6380)
- [ ] Connection string updated
- [ ] Test connection successful
- [ ] Application configuration updated
- [ ] No port conflicts
- [ ] Firewall allows port 6380 (if applicable)

---

## 📚 Related Files

### Configuration Files
- `docker-compose.redis.yml` - Port mapping configured
- `redis.env.example` - Port 6380 set as default
- `.env` - Your local environment (update this)

### Documentation  
- `REDIS_DEPLOYMENT_GUIDE.md` - Full deployment guide
- `REDIS_SETUP_SUMMARY.md` - Quick reference
- `REDIS_CONFIGURATION_QUESTIONNAIRE.md` - For gathering details

### Code Locations
Check these files if hardcoded port 6379:
- `src/beast_mode/messaging/redis_foundation.py`
- `src/beast_mode/observatory/redis_streams.py`
- `src/beast_mode/observatory/ai_consultation/status_persistence.py`
- Test files in `tests/unit/beast_mode/`

---

## 💡 Quick Commands Reference

```bash
# Start Beast Mode Redis (port 6380)
docker-compose -f docker-compose.redis.yml up -d

# Connect to Beast Mode Redis
redis-cli -p 6380 -a beastmode2025

# Check what's on each port
lsof -i :6379  # Existing cluster
lsof -i :6380  # Beast Mode

# Test Python connection
python -c "import redis; r = redis.Redis(host='localhost', port=6380, password='beastmode2025'); print(r.ping())"

# View logs
docker-compose -f docker-compose.redis.yml logs -f redis

# Stop Beast Mode Redis
docker-compose -f docker-compose.redis.yml down
```

---

**Summary**: Beast Mode Redis runs on port **6380** to coexist with the existing cluster on port **6379**. All configuration files have been updated accordingly.


