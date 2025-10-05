# Start Live Dashboard - Simple Instructions

## The Issue

The complex Redis+WebSocket streaming wasn't working reliably. I've created a **simpler file-watching WebSocket server** that works.

## Start the Live Dashboard

### Terminal 1: WebSocket Server
```bash
cd /Users/lou/kiro-2/kiro-ai-development-hackathon
python3 scripts/simple_websocket_server.py
```

**You should see:**
```
🚀 Starting WebSocket server on localhost:8765
📁 Status file: .kiro/execution-status.json
✅ WebSocket server running on ws://localhost:8765
🌐 Dashboard: http://localhost:8080/constellation_dashboard.html
📡 Broadcasting status file changes...
👁️  Watching .kiro/execution-status.json for changes...
```

### Terminal 2: HTTP Server (for dashboard)
```bash
cd /Users/lou/kiro-2/kiro-ai-development-hackathon/web
python3 -m http.server 8080
```

### Terminal 3: Orchestrator
```bash
cd /Users/lou/kiro-2/kiro-ai-development-hackathon
python3 scripts/constellation_orchestrator.py 2
```

**You should see:**
```
📡 Redis streaming enabled  (or warning if Redis unavailable)
🚀 Starting execution with 2 agents
📊 Total prompts: 12
```

### Browser: Open Dashboard
```
http://localhost:8080/constellation_dashboard.html
```

## What You'll See

**On connection:**
- Dashboard loads with current status
- Green "Connected" indicator

**As execution runs:**
- Progress bar updates every 500ms
- "Currently Running" section updates
- Stats update (completed/running/pending)
- Events appear in feed

## How It Works

1. **Orchestrator** writes `.kiro/execution-status.json` every status change
2. **WebSocket Server** watches the file (checks every 500ms)
3. **When file changes** → broadcasts to all connected browsers
4. **Browser** receives update → redraws dashboard

**Latency:** ~500ms (file watching interval)
**No Redis required** for this simple version

## Full Production Version (10 agents, all 106 prompts)

```bash
# Terminal 3: Full execution
python3 scripts/constellation_orchestrator.py 10
```

---

**The dashboard should update every 500ms with current execution status!**
