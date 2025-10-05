# Observatory Local Development Setup

## Problem

The Observatory system was experiencing issues when running locally:

1. **Missing ML Dependencies**: Container was missing `numpy`, `scikit-learn`, `pandas`, `scipy`
   - **Impact**: Engagement system couldn't load, causing 403 WebSocket errors
   - **Root Cause**: `requirements.txt` was out of sync with `pyproject.toml`

2. **Redis Configuration Mismatch**: Observatory configured for production Redis
   - **Production**: `REDIS_HOST=vonnegut`, `REDIS_PASSWORD=beastmode2025`
   - **Local**: Redis at `msp-ssl-redis:6379`, `REDIS_PASSWORD=mspssl123`
   - **Impact**: All Redis-dependent features failed (metrics, analytics, cost tracking)

3. **Deployment Environment Confusion**: Single docker-compose for both prod and local

## Solution

### 1. Fixed requirements.txt

Added ML dependencies to `requirements.txt` (lines 62-77):

```txt
# ML/AI Dependencies (for Observatory engagement system)
numpy>=1.24.0
pandas>=2.0.0
scipy>=1.10.0
scikit-learn>=1.3.0
torch>=2.0.0
transformers>=4.30.0
datasets>=2.12.0

# Additional Beast Mode dependencies
cryptography>=3.4.0
google-api-python-client>=2.0.0
google-auth-oauthlib>=0.5.0
toml>=0.10.0
coverage>=7.0.0
psutil>=5.9.0
```

### 2. Created Local Development Docker Compose

**File**: `deployment/observatory/docker-compose.local.yml`

**Key Differences from Production**:

| Configuration | Production | Local Development |
|--------------|-----------|-------------------|
| Redis Host | `vonnegut` (remote) | `msp-ssl-redis` (local container) |
| Redis Password | `beastmode2025` | `mspssl123` |
| Container Names | `beast-mode-observatory` | `beast-mode-observatory-local` |
| Prometheus Port | `9090` | `9091` (avoid conflict) |
| Grafana Port | `3000` | `3001` (avoid conflict) |
| Jaeger UI Port | `16686` | `16687` (avoid conflict) |
| Engagement Port | `8891` | `8892` (avoid conflict) |
| Cloudflare Tunnel | Yes | No (not needed locally) |
| External Networks | `observatory-network` only | `observatory-network` + `msp-ssl-network` |

### 3. Network Configuration

The local setup connects to both:
- **observatory-network**: Internal Observatory services
- **msp-ssl-network**: External network with shared `msp-ssl-redis`

```yaml
networks:
  default:
    external: true
    name: kiro-ai-development-hackathon_msp-ssl-network
```

## Usage

### Production Deployment (Vonnegut Server)

```bash
cd deployment/observatory
docker-compose up -d
```

- Uses `~/.env` for production credentials
- Connects to remote Vonnegut Redis
- Includes Cloudflare tunnel for public access
- Available at: https://observatory.nkllon.com

### Local Development

```bash
cd deployment/observatory
docker-compose -f docker-compose.local.yml up -d
```

- Uses local `msp-ssl-redis` container
- No Cloudflare tunnel needed
- Available at:
  - Observatory: http://localhost:8888
  - Prometheus: http://localhost:9091
  - Grafana: http://localhost:3001
  - Jaeger UI: http://localhost:16687

### Installing Dependencies in Running Container

If you need to install dependencies in an already-running container:

```bash
# Install ML dependencies
docker exec beast-mode-observatory pip install \
  numpy pandas scipy scikit-learn torch transformers datasets

# Restart container to reload
docker restart beast-mode-observatory
```

## Verification

### Check Observatory Status

```bash
# Local
curl http://localhost:8888/api/observatory/status | python3 -m json.tool

# Production
curl https://observatory.nkllon.com/api/observatory/status | python3 -m json.tool
```

### Check WebSocket Connections

```bash
# Check if WebSocket endpoints accept connections
docker logs beast-mode-observatory --tail 50 | grep -E "(WebSocket|accepted|403)"
```

**Good Output** (working):
```
INFO:     172.21.0.7:38504 - "WebSocket /ws/engagement" [accepted]
INFO:     connection open
```

**Bad Output** (broken):
```
INFO:     172.21.0.7:43040 - "WebSocket /ws/engagement" 403
INFO:     connection rejected (403 Forbidden)
```

### Check Redis Connection

```bash
# Test Redis connection from Observatory container
docker exec beast-mode-observatory python3 -c "
import redis
r = redis.Redis(host='msp-ssl-redis', port=6379, password='mspssl123')
print('Redis ping:', r.ping())
"
```

### Check Dependencies

```bash
# Check if numpy is installed
docker exec beast-mode-observatory python3 -c "import numpy; print('numpy:', numpy.__version__)"

# Check if sklearn is installed
docker exec beast-mode-observatory python3 -c "import sklearn; print('sklearn:', sklearn.__version__)"
```

## Troubleshooting

### Issue: 403 WebSocket Errors

**Symptom**: `"WebSocket /ws/engagement" 403` in logs

**Cause**: Missing ML dependencies (numpy, sklearn, etc.)

**Fix**:
```bash
docker exec beast-mode-observatory pip install numpy scikit-learn pandas scipy
docker restart beast-mode-observatory
```

### Issue: Redis Connection Failures

**Symptom**: `Failed to connect to Redis: Error Multiple exceptions: [Errno 111] Connect call failed`

**Cause**: Wrong Redis host or password

**Fix for Local**:
- Use `docker-compose.local.yml` with correct Redis configuration
- Or update environment variables:
  ```bash
  docker exec beast-mode-observatory env | grep REDIS
  # Should show:
  # REDIS_HOST=msp-ssl-redis
  # REDIS_PASSWORD=mspssl123
  ```

### Issue: Port Conflicts

**Symptom**: `port is already allocated`

**Cause**: Production Observatory already running

**Fix**:
```bash
# Either stop production
docker-compose down

# Or use local compose with different ports
docker-compose -f docker-compose.local.yml up -d
```

## Architecture Decisions

### Why Two Docker Compose Files?

**Separation of Concerns**:
- Production needs external Vonnegut Redis, secure credentials, public access
- Local dev needs quick iteration, shared local Redis, no tunnel overhead

**Explicit Configuration**:
- Makes production vs local differences obvious
- Prevents accidental production deployments with dev config
- Avoids environment variable confusion

### Why External Network for Local?

**Shared Redis Access**:
- `msp-ssl-redis` already exists in `msp-ssl-network`
- Creating new Redis just for Observatory is wasteful
- Sharing Redis enables cross-service communication

### Why Not Use ~/.env for Local?

**Environment Safety**:
- `~/.env` contains production credentials
- Local should never accidentally use production Redis
- Explicit hardcoded values in docker-compose.local.yml prevent mistakes

## Future Improvements

1. **requirements.txt Generation**: Auto-generate from `pyproject.toml`
   ```bash
   pip-compile pyproject.toml -o requirements.txt
   ```

2. **Health Check Enhancement**: Add Redis connectivity to health check
   ```python
   @app.get("/health")
   async def health():
       redis_ok = await check_redis_connection()
       return {"status": "healthy" if redis_ok else "degraded"}
   ```

3. **Graceful Degradation**: Observatory should work without Redis
   - Use in-memory fallback for metrics
   - Disable engagement features but keep core working

4. **Docker Build Args**: Pass Redis config at build time
   ```dockerfile
   ARG REDIS_HOST=localhost
   ENV REDIS_HOST=${REDIS_HOST}
   ```

## See Also

- [deployment/observatory/docker-compose.yml](../../deployment/observatory/docker-compose.yml) - Production config
- [deployment/observatory/docker-compose.local.yml](../../deployment/observatory/docker-compose.local.yml) - Local dev config
- [deployment/observatory/Dockerfile](../../deployment/observatory/Dockerfile) - Container build
- [requirements.txt](../../requirements.txt) - Python dependencies
- [OBSERVATORY-FIX-SUMMARY.md](./OBSERVATORY-FIX-SUMMARY.md) - Detailed diagnosis and fixes
