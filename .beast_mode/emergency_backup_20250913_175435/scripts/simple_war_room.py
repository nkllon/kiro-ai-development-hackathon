#!/usr/bin/env python3
"""
Simple War Room Dashboard

Quick working version without the datetime serialization issues.
"""

import asyncio
import json
import random
import uuid
from datetime import datetime
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn


app = FastAPI(title="Beast Mode War Room")
connected_clients = []
events = []


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>🚨 Beast Mode War Room</title>
    <style>
        body { 
            font-family: monospace; 
            background: #0a0a0a; 
            color: #00ff00; 
            margin: 0; 
            padding: 20px;
        }
        .header {
            background: linear-gradient(90deg, #ff0000, #ff6600);
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .dashboard {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .panel {
            background: #1a1a1a;
            border: 2px solid #333;
            padding: 15px;
            border-radius: 8px;
        }
        .panel-title {
            color: #00ffff;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            border-bottom: 1px solid #333;
            padding-bottom: 5px;
        }
        .event {
            background: #2a2a2a;
            padding: 10px;
            margin: 5px 0;
            border-left: 3px solid #00ff00;
            border-radius: 3px;
        }
        .event.warning { border-left-color: #ffff00; }
        .event.error { border-left-color: #ff0000; }
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #333;
        }
        .metric-value {
            color: #00ff00;
            font-weight: bold;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #00ff00;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
</head>
<body>
    <div class="header">
        🚨 BEAST MODE WAR ROOM - ALL HANDS ON DECK
        <div style="font-size: 14px; margin-top: 5px;">
            <span class="status-indicator"></span> Real-time DevOps Monitoring
        </div>
    </div>
    
    <div class="dashboard">
        <div class="panel">
            <div class="panel-title">📊 System Metrics</div>
            <div class="metric">
                <span>Test Pass Rate</span>
                <span class="metric-value" id="test-rate">94.5%</span>
            </div>
            <div class="metric">
                <span>System Health</span>
                <span class="metric-value" id="health">87.2%</span>
            </div>
            <div class="metric">
                <span>Deployment Status</span>
                <span class="metric-value" id="deploy">STABLE</span>
            </div>
            <div class="metric">
                <span>Active Users</span>
                <span class="metric-value" id="users">0</span>
            </div>
        </div>
        
        <div class="panel">
            <div class="panel-title">⚡ Real-time Events</div>
            <div id="events-list">
                <div class="event">System initialized - Waiting for events...</div>
            </div>
        </div>
        
        <div class="panel">
            <div class="panel-title">🛡️ Hubris Prevention</div>
            <div id="hubris-status">
                <div style="color: #00ff00;">All systems nominal</div>
                <div style="color: #666; font-size: 12px;">No hubris detected</div>
            </div>
        </div>
        
        <div class="panel">
            <div class="panel-title">🚨 Active Incidents</div>
            <div id="incidents">
                <div style="color: #666; text-align: center;">No active incidents</div>
            </div>
        </div>
    </div>

    <script>
        const ws = new WebSocket(`ws://localhost:8080/ws`);
        let eventCount = 0;
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            
            if (data.type === 'event') {
                addEvent(data.message, data.severity);
            } else if (data.type === 'metrics') {
                updateMetrics(data);
            }
        };
        
        function addEvent(message, severity = 'info') {
            const eventsList = document.getElementById('events-list');
            const eventEl = document.createElement('div');
            eventEl.className = `event ${severity}`;
            eventEl.innerHTML = `
                <div>${message}</div>
                <div style="font-size: 10px; color: #666;">${new Date().toLocaleTimeString()}</div>
            `;
            
            eventsList.insertBefore(eventEl, eventsList.firstChild);
            
            // Keep only last 10 events
            while (eventsList.children.length > 10) {
                eventsList.removeChild(eventsList.lastChild);
            }
            
            eventCount++;
        }
        
        function updateMetrics(metrics) {
            document.getElementById('test-rate').textContent = metrics.test_rate + '%';
            document.getElementById('health').textContent = metrics.health + '%';
            document.getElementById('deploy').textContent = metrics.deploy;
            document.getElementById('users').textContent = metrics.users;
        }
        
        // Simulate some activity
        setInterval(() => {
            const messages = [
                'Unit tests completed successfully',
                'Deployment pipeline triggered',
                'System health check passed',
                'Hubris prevention activated',
                'Emergency bypass blocked',
                'Mama discovery protocol engaged'
            ];
            
            const severities = ['info', 'info', 'info', 'warning', 'error', 'warning'];
            const idx = Math.floor(Math.random() * messages.length);
            
            addEvent(messages[idx], severities[idx]);
            
            // Update metrics
            updateMetrics({
                test_rate: (85 + Math.random() * 15).toFixed(1),
                health: (75 + Math.random() * 25).toFixed(1),
                deploy: Math.random() > 0.8 ? 'DEPLOYING' : 'STABLE',
                users: Math.floor(Math.random() * 5) + 1
            });
        }, 3000);
    </script>
</body>
</html>
    """


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    
    try:
        while True:
            await websocket.receive_text()
    except:
        connected_clients.remove(websocket)


async def main():
    print("🚨 Starting Simple War Room Dashboard...")
    print("📡 Open: http://localhost:8080")
    print("🔥 Press Ctrl+C to stop")
    
    config = uvicorn.Config(app, host="0.0.0.0", port=8080, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())