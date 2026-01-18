# Redis Configuration Questionnaire
## For Working Instance Data Collection

**Purpose**: Gather complete Redis configuration details from your working deployment to replicate in fresh Docker setup.

**Date**: 2025-10-13  
**Branch**: `fresh-install-venv-setup` (beast-mode-observatory-v1)

---

## 📋 QUICK COMMANDS SECTION

### On Your Working Instance, Run These Commands:

```bash
# 1. Redis Connection Test
redis-cli ping

# 2. Get Redis Server Info
redis-cli INFO

# 3. Get Configuration
redis-cli CONFIG GET '*'

# 4. Check Active Keys by Pattern
redis-cli KEYS '*'

# 5. Check Stream Groups
redis-cli XINFO GROUPS observatory_metrics

# 6. Check Pub/Sub Channels
redis-cli PUBSUB CHANNELS

# 7. Check Memory Usage
redis-cli INFO MEMORY

# 8. Check Persistence Settings
redis-cli CONFIG GET save
redis-cli CONFIG GET appendonly

# 9. Docker Container Info (if running in Docker)
docker ps | grep redis
docker inspect <redis_container_name>

# 10. Environment Variables
env | grep REDIS
```

---

## 🔌 SECTION 1: Connection Details

### 1.1 Basic Connection
- **Redis Host**: _________________________
- **Redis Port**: _________________________ (default: 6379)
- **Redis Password**: _____________________ (found as `REDIS_PASSWORD` or `requirepass`)
- **Redis Database Number**: ______________ (default: 0, found in code as `db=`)

### 1.2 Network Configuration
- **Network Mode**: 
  - [ ] Bridge (default Docker)
  - [ ] Host
  - [ ] Custom Network Name: _____________
- **Container Name**: _____________________
- **Exposed Ports**: _______________________
- **Internal IP (if bridge)**: _____________

### 1.3 Connection URL Format
What format does your application use?
- [ ] `redis://localhost:6379`
- [ ] `redis://:password@localhost:6379`
- [ ] `redis://localhost:6379/0`
- [ ] `redis://:password@localhost:6379/0`
- [ ] Other: ______________________________

**Example from your env**: ________________

---

## ⚙️ SECTION 2: Redis Server Configuration

### 2.1 Version and Image
```bash
# Run: redis-cli INFO SERVER
```
- **Redis Version**: _____________________
- **Docker Image**: ______________________ (e.g., `redis:7-alpine`, `redis:latest`)
- **OS/Arch**: ___________________________

### 2.2 Persistence Configuration
```bash
# Run: redis-cli CONFIG GET save
# Run: redis-cli CONFIG GET appendonly
```
- **RDB Persistence (snapshots)**:
  - Enabled: [ ] Yes [ ] No
  - Save intervals: _____________________ (e.g., `900 1 300 10 60 10000`)
  - RDB filename: ______________________ (default: `dump.rdb`)

- **AOF Persistence (append-only file)**:
  - Enabled: [ ] Yes [ ] No
  - AOF filename: ______________________ (default: `appendonly.aof`)
  - fsync policy: ______________________ (everysec/always/no)

### 2.3 Memory Configuration
```bash
# Run: redis-cli CONFIG GET maxmemory
# Run: redis-cli CONFIG GET maxmemory-policy
```
- **Max Memory**: ________________________ (e.g., `128M`, `512M`, `1G`)
- **Max Memory Policy**: _________________ (e.g., `allkeys-lru`, `noeviction`)
- **Current Memory Usage**: ______________ (from `INFO MEMORY`)

### 2.4 Performance Settings
```bash
# Run: redis-cli CONFIG GET tcp-backlog
# Run: redis-cli CONFIG GET timeout
```
- **TCP Backlog**: _______________________
- **Timeout**: ___________________________ (seconds)
- **Max Connections**: ___________________ (`maxclients`)
- **Connection Pool Size (app)**: ________ (from application config)

---

## 📊 SECTION 3: Data Structures & Keys

### 3.1 Active Key Patterns
```bash
# Run: redis-cli KEYS '*'
# Run: redis-cli DBSIZE
```
- **Total Keys**: ________________________
- **Key Patterns Found** (list all patterns):
  ```
  observatory:*
  beast_mode:*
  task_queue:*
  ai_consultation:*
  metrics:*
  __keyspace@0__:*
  (list others...)
  ```

### 3.2 Stream Configuration
```bash
# Run: redis-cli XINFO GROUPS observatory_metrics
# Run: redis-cli XINFO STREAM observatory_metrics
```
- **Stream Name**: _______________________ (found in code: `observatory_metrics`)
- **Consumer Groups**: __________________
  - Group Name: _________________________
  - Consumer Names: _____________________
- **Stream Max Length**: _________________ (if using MAXLEN)
- **Approximate Entries**: _______________

### 3.3 Pub/Sub Channels
```bash
# Run: redis-cli PUBSUB CHANNELS
# Run: redis-cli PUBSUB NUMSUB <channel_name>
```
- **Active Channels**: ___________________
  ```
  observatory:events
  beast_mode:coordination
  ai_consultation:status
  (list others...)
  ```
- **Subscribers per Channel**: ___________

### 3.4 Key Expiration Settings
```bash
# Run: redis-cli CONFIG GET notify-keyspace-events
```
- **Keyspace Notifications**: ____________ (should be `Ex` or `KEA`)
- **Keys with TTL**: _____________________ (if known)

---

## 🔐 SECTION 4: Security Configuration

### 4.1 Authentication
- **Password Protection**: 
  - [ ] Enabled
  - [ ] Disabled
- **Password**: ___________________________ (from `requirepass` or env var)
- **ACL Enabled**: [ ] Yes [ ] No

### 4.2 Network Security
- **Bind Address**: _______________________ (e.g., `127.0.0.1`, `0.0.0.0`)
- **Protected Mode**: [ ] Yes [ ] No
- **SSL/TLS**: [ ] Enabled [ ] Disabled

---

## 🐳 SECTION 5: Docker Configuration

### 5.1 Docker Compose Settings
```yaml
# From your docker-compose.yml:
```
```yaml
redis:
  image: ___________________________
  container_name: ___________________
  restart: _________________________
  command: __________________________
  ports:
    - "__________:6379"
  volumes:
    - _______________________________
  networks:
    - _______________________________
```

### 5.2 Environment Variables in Container
```bash
# Run: docker exec <redis_container> env
```
List all REDIS_* environment variables:
```
REDIS_PASSWORD=________________
REDIS_HOST=____________________
REDIS_PORT=____________________
(others...)
```

### 5.3 Volume Mounts
- **Data Volume**: _______________________ (e.g., `redis_data:/data`)
- **Config Volume**: _____________________ (if any)
- **Persistent Storage Path**: ___________

---

## 🔧 SECTION 6: Application Integration

### 6.1 Python Application Config
From your application code/environment:

```python
# RedisConfig values being used:
{
    "host": "___________",
    "port": ___________,
    "db": _____________,
    "password": "_______",
    "max_connections": ___,
    "socket_connect_timeout": ___,
    "socket_timeout": ___,
    "health_check_interval": ___,
    "connection_pool_size": ___,
    "ssl": ____________,
}
```

### 6.2 Application Environment Variables
```bash
# From your application's .env or environment:
```
```
REDIS_URL=_________________________________
REDIS_HOST=________________________________
REDIS_PORT=________________________________
REDIS_PASSWORD=____________________________
REDIS_DB=__________________________________
REDIS_MAX_CONNECTIONS=_____________________
REDIS_POOL_SIZE=___________________________
```

### 6.3 Observatory Configuration
From `src/beast_mode/observatory/models.py`:
```python
RedisConfig:
    host: "___________"
    port: ___________
    password: "_______"
    ssl: ___________
    connection_pool_size: ___
    stream_name: "___________"
    consumer_group: "___________"
```

---

## 🎯 SECTION 7: Beast Mode Specific Settings

### 7.1 Task Queue Configuration
- **Queue Names**: _______________________
  ```
  beast_mode:tasks:pending
  beast_mode:tasks:processing
  beast_mode:tasks:completed
  (list others...)
  ```

### 7.2 Coordination Events
- **Event Stream**: _____________________ (default: `observatory_metrics`)
- **Event Types**: ______________________
  ```
  HEALTH_CHECK
  METRIC_UPDATED
  ALERT_TRIGGERED
  (list others...)
  ```

### 7.3 AI Consultation
- **Query Queue**: ______________________
- **Status Keys**: ______________________
- **Result Storage**: ___________________

---

## 📈 SECTION 8: Monitoring & Health

### 8.1 Current Health Status
```bash
# Run: redis-cli INFO STATS
```
- **Total Connections Received**: ________
- **Total Commands Processed**: __________
- **Instantaneous Ops/Sec**: _____________
- **Keyspace Hits/Misses**: ______________
- **Evicted Keys**: ______________________
- **Expired Keys**: ______________________

### 8.2 Replication Status
```bash
# Run: redis-cli INFO REPLICATION
```
- **Role**: [ ] Master [ ] Slave
- **Connected Slaves**: __________________
- **Replication Offset**: ________________

---

## 🚀 SECTION 9: Deployment Details

### 9.1 Host System
- **Host OS**: ___________________________
- **Docker Version**: ____________________
- **Docker Compose Version**: ____________
- **Host IP**: ___________________________

### 9.2 Resource Limits
```yaml
# From docker-compose.yml deploy section:
```
```yaml
deploy:
  resources:
    limits:
      memory: _______________
      cpus: _________________
    reservations:
      memory: _______________
      cpus: _________________
```

### 9.3 Restart Policy
- **Restart Policy**: ___________________ (e.g., `unless-stopped`, `always`)
- **Healthcheck**: [ ] Configured [ ] Not configured
- **Healthcheck Command**: ______________

---

## ✅ SECTION 10: Verification Commands

### 10.1 Connection Test from Application
```bash
# From your application host:
```
```bash
python -c "import redis; r = redis.Redis(host='___', port=___, password='___'); print(r.ping())"
```
Result: ___________________________________

### 10.2 Stream Operations Test
```bash
redis-cli XADD observatory_metrics * test "value"
redis-cli XLEN observatory_metrics
```
Result: ___________________________________

### 10.3 Pub/Sub Test
```bash
# Terminal 1:
redis-cli SUBSCRIBE test_channel

# Terminal 2:
redis-cli PUBLISH test_channel "test message"
```
Result: ___________________________________

---

## 📝 SECTION 11: Configuration Files

### 11.1 redis.conf
If using a custom redis.conf, provide:
```bash
# Run: redis-cli CONFIG GET '*' > redis-config-dump.txt
```
Attach or paste relevant sections: ________

### 11.2 docker-compose.yml
Provide your complete redis service section:
```yaml
(paste here)
```

### 11.3 .env File
Provide REDIS-related variables:
```
(paste here, mask sensitive data if needed for questions)
```

---

## 🔍 SECTION 12: Troubleshooting Info

### 12.1 Common Issues
Have you experienced any of these?
- [ ] Connection timeouts
- [ ] Memory issues
- [ ] Persistence failures
- [ ] Performance problems
- [ ] Authentication errors

If yes, describe: _________________________

### 12.2 Log Samples
```bash
# Run: docker logs <redis_container> --tail 50
```
Provide last 50 lines: ____________________

---

## 📤 SECTION 13: Export Commands

### 13.1 Complete Configuration Export
Run these commands and save output:

```bash
# 1. Full server info
redis-cli INFO > redis-info.txt

# 2. All configuration
redis-cli CONFIG GET '*' > redis-config.txt

# 3. All keys (if not too many)
redis-cli KEYS '*' > redis-keys.txt

# 4. Stream info
redis-cli XINFO STREAM observatory_metrics > redis-stream-info.txt

# 5. Docker inspect
docker inspect <redis_container> > redis-docker-inspect.json

# 6. Environment variables
env | grep -i redis > redis-env-vars.txt

# 7. Docker compose config
docker-compose config > docker-compose-resolved.yml
```

### 13.2 Attach Files
Please attach or provide:
- [ ] redis-info.txt
- [ ] redis-config.txt
- [ ] redis-docker-inspect.json
- [ ] docker-compose.yml (redis section)
- [ ] Application .env file (REDIS vars)
- [ ] Any custom redis.conf

---

## 🎓 SECTION 14: Best Practices Check

From your working instance:
- [ ] Redis is running in Docker container
- [ ] Using connection pooling
- [ ] Password authentication enabled
- [ ] Data persistence configured (RDB or AOF)
- [ ] Memory limits set
- [ ] Healthchecks configured
- [ ] Resource limits set
- [ ] Using named volumes for data
- [ ] Network isolation configured
- [ ] Monitoring/metrics enabled

---

## 💡 QUICK START - MINIMUM INFO NEEDED

**If time is limited, provide at minimum:**

1. **Connection String**: _______________________________________________
2. **Redis Version/Image**: _______________________________________________
3. **Port**: _______________________________________________________________
4. **Password**: __________________________________________________________
5. **Command Used**: ______________________________________________________
   (from docker-compose.yml, e.g., `redis-server --appendonly yes --requirepass xxx`)
6. **Volumes**: ___________________________________________________________
7. **Environment Variables**: _____________________________________________
   ```
   REDIS_HOST=
   REDIS_PORT=
   REDIS_PASSWORD=
   ```

---

## 📋 Response Checklist

Before submitting, ensure you've provided:
- [ ] Basic connection details (host, port, password)
- [ ] Docker image and version
- [ ] docker-compose.yml redis section
- [ ] Environment variables
- [ ] Redis INFO output
- [ ] Redis CONFIG GET '*' output
- [ ] Active key patterns
- [ ] Stream configuration
- [ ] Any custom configuration files
- [ ] Application integration settings

---

## 🎯 Next Steps

After completing this questionnaire:
1. I will create a production-ready docker-compose.yml
2. I will configure environment variables
3. I will set up proper volume mounts
4. I will add healthchecks and monitoring
5. I will document the deployment procedure
6. I will create startup/verification scripts

---

**End of Questionnaire**

*Please fill out as many sections as possible and return this document. The more complete the information, the better the Redis deployment replication will be.*


