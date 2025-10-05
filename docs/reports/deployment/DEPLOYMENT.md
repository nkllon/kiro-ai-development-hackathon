# Observatory Deployment Guide

Your Observatory is now production-ready! Here are your deployment options:

## 🚀 Quick Start (Current Setup)

Your Observatory is already running in production mode:

```bash
# Check status
python scripts/start_observatory_production.py --status

# View logs
python scripts/start_observatory_production.py --logs observatory
python scripts/start_observatory_production.py --logs cloudflared

# Restart services
python scripts/start_observatory_production.py --restart

# Stop services
python scripts/start_observatory_production.py --stop
```

**URLs:**
- **Public**: https://observatory.nkllon.com/
- **Local**: http://localhost:8888/
- **Health**: http://localhost:8888/health

## 🔄 Auto-Start on Boot (Recommended)

Install Observatory as a system service so it starts automatically:

```bash
# Install system service (macOS/Linux)
python scripts/install_observatory_service.py --install

# Check service status
python scripts/install_observatory_service.py --status

# Uninstall if needed
python scripts/install_observatory_service.py --uninstall
```

After installation:
- ✅ Starts automatically on boot
- ✅ Restarts if it crashes
- ✅ Runs in background
- ✅ Persistent across reboots

## 🐳 Docker Deployment (Alternative)

If you prefer Docker:

```bash
# Make sure Docker Desktop is running
open -a Docker

# Deploy with Docker
python scripts/deploy_observatory.py
```

Docker benefits:
- ✅ Isolated environment
- ✅ Easy to update
- ✅ Portable across systems
- ✅ Built-in health checks

## ☁️ Cloud Deployment Options

### 1. DigitalOcean Droplet ($6/month)
```bash
# Create a $6/month droplet
# SSH into it and clone your repo
git clone <your-repo>
cd <your-repo>
python scripts/install_observatory_service.py --install
```

### 2. AWS EC2 t3.micro (Free tier)
```bash
# Launch t3.micro instance
# Install dependencies and clone repo
# Run the service installer
```

### 3. Google Cloud Run (Pay per use)
```bash
# Build and deploy container
gcloud run deploy observatory --source .
```

### 4. Railway/Render (Simple deployment)
- Connect your GitHub repo
- Set build command: `pip install -r requirements.txt`
- Set start command: `python -m src.beast_mode.observatory.main`

## 📊 Monitoring Your Deployment

### Health Checks
```bash
# Local health check
curl http://localhost:8888/health

# Public health check  
curl https://observatory.nkllon.com/health
```

### Log Monitoring
```bash
# Follow logs in real-time
python scripts/start_observatory_production.py --logs observatory --follow

# Check tunnel logs
python scripts/start_observatory_production.py --logs cloudflared --follow
```

### Process Monitoring
```bash
# Check what's running
python scripts/start_observatory_production.py --status

# System process info
ps aux | grep -E "(python|cloudflared)"
```

## 🔧 Configuration

### Environment Variables
Create `.env` file for configuration:
```bash
# Observatory settings
OBSERVATORY_PORT=8888
OBSERVATORY_HOST=0.0.0.0
LOG_LEVEL=INFO

# Cloudflare tunnel
TUNNEL_NAME=observatory-tunnel
```

### Cloudflare Tunnel Management
```bash
# List tunnels
cloudflared tunnel list

# Check tunnel info
cloudflared tunnel info observatory-tunnel

# Update tunnel config
vim ~/.cloudflared/config.yml
```

## 🚨 Troubleshooting

### Observatory Won't Start
```bash
# Check logs
cat logs/observatory.log

# Check port conflicts
lsof -i :8888

# Restart services
python scripts/start_observatory_production.py --restart
```

### Tunnel Connection Issues
```bash
# Check tunnel logs
cat logs/cloudflared.log

# Test tunnel manually
cloudflared tunnel run observatory-tunnel

# Check DNS
dig observatory.nkllon.com
```

### Performance Issues
```bash
# Check resource usage
python scripts/start_observatory_production.py --status

# Monitor system resources
top -p $(cat observatory.pid | jq -r '.observatory')
```

## 📈 Scaling Up

When you need more power:

1. **Vertical Scaling**: Upgrade your server specs
2. **Horizontal Scaling**: Add load balancer + multiple instances
3. **Database**: Add Redis/PostgreSQL for persistence
4. **CDN**: Use Cloudflare for static assets
5. **Monitoring**: Add Prometheus + Grafana

## 🔐 Security Checklist

- ✅ Cloudflare tunnel (no open ports)
- ✅ HTTPS everywhere
- ✅ Process isolation
- ✅ Log rotation
- ✅ Health monitoring
- ✅ Automatic restarts

Your Observatory is production-ready! 🎉