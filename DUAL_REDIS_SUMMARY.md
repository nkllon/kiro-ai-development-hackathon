# Dual Redis Architecture - Quick Reference

**Discovery**: beast-mailbox-core enables lab-wide communication!  
**Architecture**: Two Redis instances for different purposes

---

## 🎯 The Big Picture

You now have access to **TWO Redis instances**:

### Redis Instance 1: Local (Port 6380) - YOUR REDIS
**Status**: ✅ Running (docker-compose.redis.yml)  
**Purpose**: App internal state  
**Access**: Only you

**Used for**:
- Observatory metrics
- Task queue
- AI consultation state
- Internal coordination

**Connection**:
```bash
REDIS_HOST=localhost
REDIS_PORT=6380
REDIS_PASSWORD=beastmode2025
```

---

### Redis Instance 2: Network Cluster (Port 6379) - LAB REDIS
**Status**: ⏳ Existing (managed by lab)  
**Purpose**: Inter-agent communication  
**Access**: All lab agents

**Used for**:
- Sending messages to herbert, poe, vonnegut
- Receiving messages from lab agents
- Lab-wide coordination
- Distributed system participation

**Connection**:
```bash
LAB_REDIS_HOST=<cluster_ip>  # Get from questionnaire
LAB_REDIS_PORT=6379
LAB_REDIS_PASSWORD=<cluster_password>  # Get from questionnaire
AGENT_ID=devbox  # Your agent name
```

---

## 🛠️ How to Use Both

### For App Internal State → Use Port 6380
```python
from src.beast_mode.messaging.redis_foundation import RedisFoundation, RedisConfig

# Internal app state
local_redis = RedisFoundation(
    RedisConfig(
        host='localhost',
        port=6380,
        password='beastmode2025'
    )
)
```

### For Lab Communication → Use Port 6379
```python
from beast_mailbox_core import RedisMailboxService
import redis

# Lab communication
network_redis = redis.Redis(
    host='<cluster_ip>',
    port=6379,
    password='<cluster_password>',
    decode_responses=True
)

mailbox = RedisMailboxService(network_redis)

# Send to herbert
mailbox.send_message(
    sender='devbox',
    recipient='herbert',
    message_type='greeting',
    payload={'message': 'Hello from fresh install!'}
)
```

---

## 🎮 Quick Examples

### Send Message to Lab Agent
```bash
# CLI: Send to herbert via lab cluster
beast-mailbox-send devbox herbert \
  --redis-host <cluster_ip> \
  --redis-port 6379 \
  --redis-password <cluster_password> \
  --message "Fresh Beast Mode instance online!"
```

### Listen for Lab Messages
```bash
# CLI: Listen for messages from lab
beast-mailbox-service devbox \
  --redis-host <cluster_ip> \
  --redis-port 6379 \
  --redis-password <cluster_password> \
  --verbose
```

### Check Lab Inbox
```bash
# CLI: Check latest 5 messages from lab
beast-mailbox-service devbox --latest --count 5 \
  --redis-host <cluster_ip> \
  --redis-port 6379 \
  --redis-password <cluster_password>
```

---

## 📊 Network Topology

```
YOU (devbox)
    ├─> Local Redis (6380)
    │   └─> Observatory, Task Queue, AI state
    │
    └─> Network Redis (6379)
        └─> Lab cluster
            ├─> herbert agent
            ├─> poe agent  
            ├─> vonnegut container
            └─> other agents
```

---

## ✅ Setup Checklist

### Local Redis (6380) - ✅ Complete
- [x] Container running
- [x] Port 6380 accessible
- [x] Password: beastmode2025
- [x] Tested and verified
- [x] Ready for app use

### Network Redis (6379) - ⏳ Needs Config
- [ ] Get cluster IP address
- [ ] Get cluster password
- [ ] Get your agent ID
- [ ] Test connection
- [ ] Discover other agents

---

## 🧪 Test Scripts

### Test Local Redis
```bash
python test_redis_connection.py
# Tests port 6380 (local)
```

### Test Lab Communication
```bash
export LAB_REDIS_HOST=<cluster_ip>
export LAB_REDIS_PASSWORD=<cluster_password>
python test_lab_communication.py
# Tests port 6379 (network cluster)
```

---

## 🎯 Use Cases

### Standalone Mode (Local Redis Only)
```python
# Just use local Redis for everything
# No lab participation
# Isolated operation
```

### Lab Participation Mode (Both Redis)
```python
# Use local Redis for app state
# Use network Redis for lab messaging
# Full collaboration capability
```

### Hybrid Mode (Recommended)
```python
# Default: Use local Redis (always available)
# Optional: Use network Redis when configured
# Graceful degradation if cluster unavailable
```

---

## 📞 Getting Lab Cluster Details

**Fill out in REDIS_CONFIGURATION_QUESTIONNAIRE.md**:

Section 1.1: Basic Connection
- Network Redis Host: _______________
- Network Redis Port: 6379
- Network Redis Password: ___________

Section 7.1: Agent IDs in Lab
- Your agent ID: _____________
- Other agents: _____________

---

## 🚀 Quick Start

### Minimal Lab Integration

1. **Get credentials** (from questionnaire or lab admin)
2. **Set environment**:
   ```bash
   export LAB_REDIS_HOST=192.168.1.119
   export LAB_REDIS_PASSWORD=<password>
   export AGENT_ID=devbox
   ```
3. **Test connection**:
   ```bash
   python test_lab_communication.py
   ```
4. **Send first message**:
   ```bash
   beast-mailbox-send devbox herbert --message "Hi!"
   ```

---

## 💡 Key Insight

**The genius of this architecture**:
- Local Redis (6380): Fast, reliable, isolated
- Network Redis (6379): Distributed, collaborative, connected
- beast-mailbox-core: Bridge between them
- **Best of both worlds!**

---

**Status**: 
- ✅ Local Redis: Deployed and tested
- ⏳ Lab Redis: Ready to connect (need credentials)
- ✅ beast-mailbox-core: Installed and ready

**Next**: Get lab cluster credentials and join the conversation! 🎉



