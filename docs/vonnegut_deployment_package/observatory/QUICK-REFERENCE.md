# Observatory Quick Reference

## Health Check Commands

```bash
# Check Observatory status
curl https://observatory.nkllon.com/api/observatory/status | python3 -m json.tool

# Check if healthy
curl -s https://observatory.nkllon.com/api/observatory/status | \
  python3 -c "import sys, json; d=json.load(sys.stdin); exit(0 if d['health']['status']=='healthy' else 1)" && \
  echo "✅ Observatory is healthy" || echo "❌ Observatory has issues"

# Check WebSocket connections
docker logs beast-mode-observatory --tail 50 | grep -E "(WebSocket|accepted|403)"

# Check container status
docker ps --filter "name=observatory" --format "table {{.Names}}\t{{.Status}}"
```

## Common Operations

### Restart Observatory
```bash
docker restart beast-mode-observatory
```

### View Logs
```bash
# Recent logs
docker logs beast-mode-observatory --tail 100

# Follow logs
docker logs beast-mode-observatory -f

# Search for errors
docker logs beast-mode-observatory 2>&1 | grep -E "(ERROR|Failed|Exception)"
```

### Check Dependencies
```bash
# Verify ML dependencies installed
docker exec beast-mode-observatory python3 -c "
import numpy, sklearn, pandas, scipy
print('✅ All ML dependencies OK')
print(f'numpy: {numpy.__version__}')
print(f'sklearn: {sklearn.__version__}')
print(f'pandas: {pandas.__version__}')
print(f'scipy: {scipy.__version__}')
"
```

### Test Redis Connection
```bash
# Test from Observatory container
docker exec beast-mode-observatory python3 -c "
import redis
r = redis.Redis(host='msp-ssl-redis', port=6379, password='mspssl123')
print(f'✅ Redis: {r.ping()}')
"
```

## Deployment

### Production (Vonnegut)
```bash
cd deployment/observatory
docker-compose up -d
```

### Local Development
```bash
cd deployment/observatory
docker-compose -f docker-compose.local.yml up -d
```

### Rebuild Image
```bash
cd deployment/observatory
docker-compose build observatory
docker-compose up -d
```

## Access URLs

### Production
- Observatory: https://observatory.nkllon.com
- Prometheus: https://prometheus.observatory.nkllon.com
- Grafana: https://grafana.observatory.nkllon.com

### Local
- Observatory: http://localhost:8888
- Prometheus: http://localhost:9091
- Grafana: http://localhost:3001
- Jaeger: http://localhost:16687

## Troubleshooting

### WebSocket 403 Errors
**Symptom**: `"WebSocket /ws/engagement" 403`
**Fix**: Install ML dependencies
```bash
docker exec beast-mode-observatory pip install numpy scikit-learn pandas scipy
docker restart beast-mode-observatory
```

### Redis Connection Failed
**Symptom**: `Failed to connect to Redis: [Errno 111] Connect call failed`
**Fix**: Use correct Redis configuration for environment (see docker-compose.local.yml)

### Container Won't Start
**Check**:
```bash
docker logs beast-mode-observatory
docker inspect beast-mode-observatory
```

### Port Already in Use
**Fix**: Use local docker-compose with different ports
```bash
docker-compose -f docker-compose.local.yml up -d
```

## Files Reference

| File | Purpose |
|------|---------|
| [LOCAL-DEVELOPMENT-SETUP.md](./LOCAL-DEVELOPMENT-SETUP.md) | Complete setup guide |
| [OBSERVATORY-FIX-SUMMARY.md](./OBSERVATORY-FIX-SUMMARY.md) | Detailed diagnostics |
| [docker-compose.yml](../../deployment/observatory/docker-compose.yml) | Production config |
| [docker-compose.local.yml](../../deployment/observatory/docker-compose.local.yml) | Local dev config |
| [requirements.txt](../../requirements.txt) | Python dependencies |

## Status Indicators

### ✅ Healthy System
```json
{
  "health": {
    "status": "healthy",
    "health_score": 1.0,
    "issues": []
  }
}
```

### ❌ Unhealthy System
```json
{
  "health": {
    "status": "error",
    "health_score": 0.0,
    "issues": ["Observatory is not running"]
  }
}
```

### 🔍 Key Metrics to Watch
- `health.status`: Should be "healthy"
- `health.health_score`: Should be 1.0
- `health.issues`: Should be empty array
- WebSocket logs: Should show "[accepted]", not "403"
