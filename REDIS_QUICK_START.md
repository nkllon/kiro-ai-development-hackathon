# Redis Quick Start - Port 6380 Configuration

**Critical Info**: Using port **6380** to avoid conflict with existing Redis cluster on **6379**

---

## ⚡ 30 Second Start

```bash
# 1. Create data directory
mkdir -p data/redis

# 2. Start Redis on port 6380
docker-compose -f docker-compose.redis.yml up -d

# 3. Test (note port 6380)
redis-cli -p 6380 -a beastmode2025 ping

# 4. Test from Python
source venv/bin/activate
python test_redis_connection.py
```

**Connection String**: `redis://:beastmode2025@localhost:6380/0`

---

## 🎯 Key Points

### Ports
- **Existing Cluster**: `6379` (on network, not touching this)
- **Beast Mode Redis**: `6380` (our instance)

### Connection Details
```bash
REDIS_HOST=localhost
REDIS_PORT=6380          # ← Note: 6380, not 6379
REDIS_PASSWORD=beastmode2025
```

### Python Connection
```python
import redis
r = redis.Redis(
    host='localhost',
    port=6380,           # ← Note: 6380
    password='beastmode2025'
)
```

---

## 🔍 Quick Tests

### Test Container
```bash
docker ps | grep beast-mode-redis
docker port beast-mode-redis  # Should show 6380->6379
```

### Test Connection
```bash
# From host
redis-cli -p 6380 -a beastmode2025 ping

# From container
docker exec beast-mode-redis redis-cli -a beastmode2025 ping

# From Python
python test_redis_connection.py
```

### View Logs
```bash
docker-compose -f docker-compose.redis.yml logs -f redis
```

---

## 🛠️ Management

```bash
# Start
docker-compose -f docker-compose.redis.yml up -d

# Stop
docker-compose -f docker-compose.redis.yml stop

# Restart
docker-compose -f docker-compose.redis.yml restart

# Remove (keeps data)
docker-compose -f docker-compose.redis.yml down

# Remove with data (⚠️ destructive)
docker-compose -f docker-compose.redis.yml down -v
```

---

## 📊 Port Verification

```bash
# What's on 6379 (existing cluster)
netstat -an | grep 6379
lsof -i :6379

# What's on 6380 (Beast Mode)
netstat -an | grep 6380
lsof -i :6380
```

---

## 🚨 Troubleshooting

### Can't Connect
1. Check container: `docker ps | grep redis`
2. Check logs: `docker-compose -f docker-compose.redis.yml logs redis`
3. Check port: `docker port beast-mode-redis`
4. Test: `redis-cli -p 6380 -a beastmode2025 ping`

### Wrong Port
- Application trying 6379? Update `.env` or environment:
  ```bash
  export REDIS_PORT=6380
  ```

### Port Already in Use
- Change to different port in `docker-compose.redis.yml`:
  ```yaml
  ports:
    - "6381:6379"  # Use 6381 instead
  ```

---

## 📚 Full Documentation

- **REDIS_PORT_CONFIGURATION.md** - Port conflict resolution details
- **REDIS_DEPLOYMENT_GUIDE.md** - Complete deployment guide
- **REDIS_CONFIGURATION_QUESTIONNAIRE.md** - For working instance details
- **REDIS_SETUP_SUMMARY.md** - Full overview

---

## ✅ Checklist

Before running application:
- [ ] Redis container running on port 6380
- [ ] `redis-cli -p 6380 -a beastmode2025 ping` returns PONG
- [ ] `test_redis_connection.py` passes all tests
- [ ] Environment variables set (REDIS_PORT=6380)
- [ ] Application configured for port 6380
- [ ] No conflicts with existing cluster on 6379

---

**Quick Test**: `python test_redis_connection.py`  
**Default Port**: `6380` (external) → `6379` (internal)  
**Password**: `beastmode2025`


