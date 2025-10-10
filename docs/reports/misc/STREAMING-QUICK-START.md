# Real-Time Streaming - Quick Start

## 🚀 3-Terminal Setup

```bash
# Terminal 1: WebSocket Server
python3 -m src.constellation_streaming.websocket_server

# Terminal 2: Orchestrator (with streaming)
python3 scripts/constellation_orchestrator.py 10

# Terminal 3: Monitor (streaming)
python3 scripts/constellation_monitor_stream.py

# OR Browser: Open web/constellation_dashboard.html
```

## 📊 Status Reporting Architecture

### Before (Polling):
```
Orchestrator ─writes→ JSON file
                        ↑
Monitor ───polls every 2s─┘ (2000ms latency)
```

### Now (Streaming):
```
Orchestrator ─→ Redis ─→ WebSocket ─→ Monitor/Browser
           (<10ms)    (<10ms)      (<10ms)
```

## 🔧 Components

| Component | Purpose | Status |
|-----------|---------|--------|
| **Redis** | Message broker | ✅ Running |
| **Orchestrator** | Executes prompts + publishes updates | ✅ Ready |
| **WebSocket Server** | Relays updates to clients | ✅ Ready |
| **Streaming Monitor** | Terminal UI (WebSocket) | ✅ Ready |
| **Browser Dashboard** | Web UI (WebSocket) | ✅ Ready |
| **Legacy Monitor** | Terminal UI (polling) | ✅ Still works |

## 📡 Redis Channels

| Channel | Content | Frequency |
|---------|---------|-----------|
| `constellation:status` | Full status | On change |
| `constellation:prompt` | Prompt updates | On change |
| `constellation:event` | Events | On event |
| `constellation:heartbeat` | Stats | Every 10s |

## 🎯 Key Features

✅ **Sub-10ms latency** (vs 2000ms polling)
✅ **Real-time events** (start/complete/fail)
✅ **Multiple clients** (many monitors simultaneously)
✅ **Browser dashboard** (modern web UI)
✅ **Optional** (can disable with `--no-streaming`)
✅ **Backward compatible** (old monitor still works)

## 🔍 Quick Tests

```bash
# Test Redis
redis-cli ping  # Should return: PONG

# Test WebSocket server
python3 -m src.constellation_streaming.websocket_server
# Look for: "✅ WebSocket server running on ws://localhost:8765"

# Test streaming monitor
python3 scripts/constellation_monitor_stream.py
# Look for: "✅ Connected! Receiving real-time updates..."

# Test browser dashboard
open web/constellation_dashboard.html
# Look for: Green "Connected" indicator
```

## 🛠️ Disable Streaming

```bash
# Run without Redis streaming (file-only mode)
python3 scripts/constellation_orchestrator.py 10 --no-streaming
```

---

**Full docs:** `STREAMING-SETUP.md`
