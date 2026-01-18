# Redis Deployment Guide for Beast Mode Observatory

**Date**: 2025-10-13  
**Branch**: `fresh-install-venv-setup` (beast-mode-observatory-v1)  
**Status**: Quick Start Configuration (Pending Working Instance Details)

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Docker and Docker Compose installed
- Port 6380 available (using 6380 to avoid conflict with existing Redis cluster on 6379)
- Existing Redis cluster on 6379 (will not be disturbed)

### Steps

1. **Create data directory**:
   ```bash
   mkdir -p data/redis
   ```

2. **Copy environment file**:
   ```bash
   cp .env.redis.example .env.redis
   ```

3. **Start Redis**:
   ```bash
   docker-compose -f docker-compose.redis.yml up -d
   ```

4. **Verify Redis is running**:
   ```bash
   docker-compose -f docker-compose.redis.yml ps
   docker-compose -f docker-compose.redis.yml logs redis
   ```

5. **Test connection** (note: using port 6380):
   ```bash
   docker exec beast-mode-redis redis-cli -a beastmode2025 ping
   # Should return: PONG
   
   # Or from host (note port 6380):
   redis-cli -p 6380 -a beastmode2025 ping
   ```

6. **Test from Python** (note: using port 6380):
   ```bash
   source venv/bin/activate
   python -c "import redis; r = redis.Redis(host='localhost', port=6380, password='beastmode2025', decode_responses=True); print('PING:', r.ping())"
   ```

---

## 📋 What's Included

### Core Redis Service
- **Image**: `redis:7-alpine` (lightweight, production-ready)
- **Persistence**: Enabled (AOF + RDB)
- **Memory Limit**: 512MB with LRU eviction
- **Security**: Password authentication
- **Monitoring**: Health checks enabled
- **Notifications**: Keyspace events configured

### Optional Tools (Profiles)

#### Redis Commander (Web UI)
Access at: http://localhost:8081
```bash
# Start with Redis Commander
docker-compose -f docker-compose.redis.yml --profile tools up -d
```
- **Username**: admin
- **Password**: admin (change in .env.redis)

#### Redis Exporter (Prometheus Metrics)
Metrics at: http://localhost:9121/metrics
```bash
# Start with monitoring
docker-compose -f docker-compose.redis.yml --profile monitoring up -d
```

---

## 🔧 Configuration Details

### Redis Server Settings
Current configuration (customizable in docker-compose.redis.yml):

```
appendonly yes              # Enable AOF persistence
requirepass beastmode2025   # Password authentication
maxmemory 512mb            # Memory limit
maxmemory-policy allkeys-lru # Eviction policy
save 900 1                 # RDB: save after 900s if 1 key changed
save 300 10                # RDB: save after 300s if 10 keys changed
save 60 10000              # RDB: save after 60s if 10000 keys changed
notify-keyspace-events Ex  # Enable expiration notifications
```

### Port Mappings
- **6380**: Redis server (external, maps to internal 6379)
  - **Note**: Using 6380 to avoid conflict with existing Redis cluster on 6379
- **8081**: Redis Commander UI (with --profile tools)
- **9121**: Redis Exporter metrics (with --profile monitoring)

### Volumes
- `redis_data`: Persistent data storage (`./data/redis`)
- `redis_logs`: Log files

---

## 🔐 Security Configuration

### Default Credentials
⚠️ **CHANGE THESE IN PRODUCTION!**

- **Redis Password**: `beastmode2025`
- **Redis Commander**: admin/admin

### Changing Password

1. **Edit .env.redis**:
   ```bash
   REDIS_PASSWORD=your_secure_password_here
   ```

2. **Restart Redis**:
   ```bash
   docker-compose -f docker-compose.redis.yml down
   docker-compose -f docker-compose.redis.yml up -d
   ```

3. **Update application config**:
   - Update `REDIS_PASSWORD` in application environment
   - Update connection strings in application code

---

## 📊 Data Structures Expected

Based on code analysis, these Redis structures are used:

### Streams
- **observatory_metrics**: Main event stream
  - Consumer Group: `observatory_group`
  - Used for: Metrics, events, coordination

### Key Patterns
```
observatory:*            # Observatory-specific keys
beast_mode:*            # Beast Mode framework keys
task_queue:*            # Task queue management
ai_consultation:*       # AI consultation status
metrics:*               # Performance metrics
__keyspace@0__:*        # Keyspace notifications
```

### Pub/Sub Channels (Expected)
```
observatory:events
beast_mode:coordination
ai_consultation:status
```

---

## 🔍 Verification & Testing

### 1. Health Check
```bash
docker exec beast-mode-redis redis-cli -a beastmode2025 ping
```

### 2. Check Server Info
```bash
docker exec beast-mode-redis redis-cli -a beastmode2025 INFO
```

### 3. Test Stream Operations
```bash
# Create a test stream
docker exec beast-mode-redis redis-cli -a beastmode2025 \
  XADD observatory_metrics \* test_key test_value

# Check stream length
docker exec beast-mode-redis redis-cli -a beastmode2025 \
  XLEN observatory_metrics

# Read from stream
docker exec beast-mode-redis redis-cli -a beastmode2025 \
  XREAD COUNT 1 STREAMS observatory_metrics 0
```

### 4. Test Pub/Sub
```bash
# Terminal 1 - Subscribe
docker exec -it beast-mode-redis redis-cli -a beastmode2025 \
  SUBSCRIBE test_channel

# Terminal 2 - Publish
docker exec beast-mode-redis redis-cli -a beastmode2025 \
  PUBLISH test_channel "Hello Beast Mode"
```

### 5. Test from Application
```python
# test_redis_connection.py
import redis
import os

# Load from environment
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_password = os.getenv('REDIS_PASSWORD', 'beastmode2025')

try:
    # Connect
    r = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password,
        decode_responses=True
    )
    
    # Test basic operations
    print("✅ PING:", r.ping())
    
    # Test set/get
    r.set('test_key', 'test_value')
    print("✅ GET:", r.get('test_key'))
    
    # Test stream
    r.xadd('test_stream', {'field': 'value'})
    print("✅ XLEN:", r.xlen('test_stream'))
    
    # Test pub/sub
    pubsub = r.pubsub()
    pubsub.subscribe('test_channel')
    r.publish('test_channel', 'test message')
    print("✅ Pub/Sub: OK")
    
    print("\n✅ All Redis tests passed!")
    
except redis.ConnectionError as e:
    print(f"❌ Connection failed: {e}")
except Exception as e:
    print(f"❌ Test failed: {e}")
```

Run test:
```bash
source venv/bin/activate
python test_redis_connection.py
```

---

## 🛠️ Management Commands

### Start/Stop/Restart
```bash
# Start
docker-compose -f docker-compose.redis.yml up -d

# Stop
docker-compose -f docker-compose.redis.yml stop

# Restart
docker-compose -f docker-compose.redis.yml restart

# Stop and remove
docker-compose -f docker-compose.redis.yml down

# Stop and remove volumes (⚠️ DATA LOSS)
docker-compose -f docker-compose.redis.yml down -v
```

### Logs
```bash
# Follow logs
docker-compose -f docker-compose.redis.yml logs -f redis

# Last 100 lines
docker-compose -f docker-compose.redis.yml logs --tail 100 redis

# Specific time
docker-compose -f docker-compose.redis.yml logs --since 10m redis
```

### Shell Access
```bash
# Redis CLI
docker exec -it beast-mode-redis redis-cli -a beastmode2025

# Container shell
docker exec -it beast-mode-redis sh
```

### Backup Data
```bash
# Create backup
docker exec beast-mode-redis redis-cli -a beastmode2025 SAVE
docker cp beast-mode-redis:/data/dump.rdb ./backups/dump-$(date +%Y%m%d-%H%M%S).rdb

# Copy AOF
docker cp beast-mode-redis:/data/appendonly.aof ./backups/appendonly-$(date +%Y%m%d-%H%M%S).aof
```

### Restore Data
```bash
# Stop Redis
docker-compose -f docker-compose.redis.yml stop redis

# Copy backup
docker cp ./backups/dump-YYYYMMDD-HHMMSS.rdb beast-mode-redis:/data/dump.rdb

# Start Redis
docker-compose -f docker-compose.redis.yml start redis
```

---

## 📈 Monitoring

### Health Status
```bash
# Container health
docker-compose -f docker-compose.redis.yml ps

# Redis INFO sections
docker exec beast-mode-redis redis-cli -a beastmode2025 INFO SERVER
docker exec beast-mode-redis redis-cli -a beastmode2025 INFO MEMORY
docker exec beast-mode-redis redis-cli -a beastmode2025 INFO STATS
docker exec beast-mode-redis redis-cli -a beastmode2025 INFO REPLICATION
```

### Key Metrics
```bash
# Memory usage
docker exec beast-mode-redis redis-cli -a beastmode2025 INFO MEMORY | grep used_memory_human

# Connected clients
docker exec beast-mode-redis redis-cli -a beastmode2025 INFO CLIENTS | grep connected_clients

# Operations per second
docker exec beast-mode-redis redis-cli -a beastmode2025 INFO STATS | grep instantaneous_ops_per_sec

# Key count
docker exec beast-mode-redis redis-cli -a beastmode2025 DBSIZE
```

### With Redis Commander
1. Start with tools profile:
   ```bash
   docker-compose -f docker-compose.redis.yml --profile tools up -d
   ```

2. Open browser: http://localhost:8081

3. Login: admin/admin

4. Browse keys, run commands, monitor performance

---

## 🚨 Troubleshooting

### Redis Won't Start
```bash
# Check logs
docker-compose -f docker-compose.redis.yml logs redis

# Common issues:
# - Port 6379 already in use
# - Permission issues with data directory
# - Invalid configuration

# Solutions:
# 1. Change port in .env.redis
# 2. Fix permissions: sudo chown -R $(whoami) data/redis
# 3. Check docker-compose.redis.yml syntax
```

### Can't Connect
```bash
# Verify Redis is running
docker ps | grep redis

# Check if port is exposed
docker port beast-mode-redis

# Test connection
redis-cli -h localhost -p 6379 -a beastmode2025 ping

# Check firewall
sudo ufw status
```

### Out of Memory
```bash
# Check memory usage
docker exec beast-mode-redis redis-cli -a beastmode2025 INFO MEMORY

# Check eviction stats
docker exec beast-mode-redis redis-cli -a beastmode2025 INFO STATS | grep evicted

# Solutions:
# 1. Increase maxmemory in docker-compose.redis.yml
# 2. Adjust eviction policy
# 3. Clean up old keys
# 4. Increase container memory limit
```

### Slow Performance
```bash
# Check slow log
docker exec beast-mode-redis redis-cli -a beastmode2025 SLOWLOG GET 10

# Monitor commands in real-time
docker exec beast-mode-redis redis-cli -a beastmode2025 MONITOR

# Check latency
docker exec beast-mode-redis redis-cli -a beastmode2025 --latency

# Solutions:
# 1. Optimize command patterns
# 2. Use connection pooling
# 3. Enable pipelining
# 4. Increase resources
```

---

## 🔄 Integration with Application

### Update Application Configuration

1. **Environment Variables** (.env or application config):
   ```bash
   REDIS_URL=redis://:beastmode2025@localhost:6379/0
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_PASSWORD=beastmode2025
   REDIS_DB=0
   ```

2. **Python Code** (already configured in codebase):
   ```python
   from src.beast_mode.messaging.redis_foundation import RedisFoundation, RedisConfig
   
   config = RedisConfig(
       host=os.getenv('REDIS_HOST', 'localhost'),
       port=int(os.getenv('REDIS_PORT', 6379)),
       password=os.getenv('REDIS_PASSWORD'),
       max_connections=10
   )
   
   redis_foundation = RedisFoundation(config)
   await redis_foundation.initialize()
   ```

3. **Test Integration**:
   ```bash
   source venv/bin/activate
   python -m pytest tests/unit/test_redis_transport.py -v
   ```

---

## 📚 Next Steps

### After Getting Working Instance Details

Once you complete the `REDIS_CONFIGURATION_QUESTIONNAIRE.md`, I will:

1. ✅ Update docker-compose.redis.yml with exact configuration
2. ✅ Set correct stream names and consumer groups
3. ✅ Match persistence settings
4. ✅ Replicate security configuration
5. ✅ Add any custom redis.conf
6. ✅ Document all key patterns and data structures
7. ✅ Create deployment verification script

### Current Status

- ✅ Basic Redis container configured
- ✅ Security enabled (password auth)
- ✅ Persistence enabled (AOF + RDB)
- ✅ Health checks configured
- ✅ Resource limits set
- ⏳ Awaiting working instance details for fine-tuning
- ⏳ Stream configuration pending
- ⏳ Exact memory/performance settings pending

---

## 📞 Support

For issues:
1. Check troubleshooting section above
2. Review REDIS_CONFIGURATION_QUESTIONNAIRE.md
3. Check logs: `docker-compose -f docker-compose.redis.yml logs redis`
4. Verify network: `docker network inspect beast-mode-network`

---

**Status**: Ready for testing with default configuration. Awaiting working instance questionnaire for production configuration.

