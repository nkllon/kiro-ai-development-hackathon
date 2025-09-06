"""
War Room Mode - Real-time DevOps Dashboard Server

"All hands on deck, show me everything"
Comprehensive web-based monitoring with real-time collaboration
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass, asdict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from ..core.interfaces import ReflectiveModule
from .events import Event, EventSeverity


@dataclass
class ConnectedUser:
    """Represents a connected user in the War Room"""
    user_id: str
    websocket: WebSocket
    username: str
    connected_at: datetime
    last_activity: datetime


@dataclass
class DashboardMetrics:
    """Real-time metrics for the dashboard"""
    total_events: int = 0
    critical_alerts: int = 0
    active_users: int = 0
    system_health_score: float = 100.0
    test_pass_rate: float = 0.0
    deployment_status: str = "stable"
    last_updated: datetime = None


class WarRoomServer(ReflectiveModule):
    """
    High-performance FastAPI server for War Room dashboard
    
    Features:
    - Real-time WebSocket communication
    - Multi-user collaboration
    - Event streaming and filtering
    - Interactive data visualization
    - Incident coordination tools
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        super().__init__()
        self.host = host
        self.port = port
        self.app = FastAPI(title="Beast Mode War Room", version="1.0.0")
        self.connected_users: Dict[str, ConnectedUser] = {}
        self.event_history: List[Event] = []
        self.metrics = DashboardMetrics(last_updated=datetime.now())
        
        # Real-time state
        self.active_incidents: List[Dict[str, Any]] = []
        self.shared_annotations: List[Dict[str, Any]] = []
        self.system_alerts: List[Dict[str, Any]] = []
        
        self._setup_routes()
        self._setup_middleware()
    
    def _setup_middleware(self):
        """Configure CORS and other middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """Setup all API routes and WebSocket endpoints"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard_home():
            """Serve the main dashboard HTML"""
            return self._get_dashboard_html()
        
        @self.app.get("/api/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "active_connections": len(self.connected_users),
                "metrics": asdict(self.metrics)
            }
        
        @self.app.get("/api/metrics")
        async def get_metrics():
            """Get current dashboard metrics"""
            self.metrics.active_users = len(self.connected_users)
            self.metrics.last_updated = datetime.now()
            return asdict(self.metrics)
        
        @self.app.get("/api/events")
        async def get_events(limit: int = 100, severity: Optional[str] = None):
            """Get recent events with optional filtering"""
            events = self.event_history[-limit:]
            
            if severity:
                try:
                    severity_filter = EventSeverity(severity.lower())
                    events = [e for e in events if e.severity == severity_filter]
                except ValueError:
                    raise HTTPException(status_code=400, detail=f"Invalid severity: {severity}")
            
            return {
                "events": [asdict(event) for event in events],
                "total": len(events),
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.get("/api/incidents")
        async def get_incidents():
            """Get active incidents"""
            return {
                "incidents": self.active_incidents,
                "count": len(self.active_incidents)
            }
        
        @self.app.post("/api/incidents")
        async def create_incident(incident_data: Dict[str, Any]):
            """Create a new incident"""
            incident = {
                "id": str(uuid.uuid4()),
                "title": incident_data.get("title", "New Incident"),
                "severity": incident_data.get("severity", "medium"),
                "status": "open",
                "created_at": datetime.now().isoformat(),
                "created_by": incident_data.get("created_by", "system"),
                "description": incident_data.get("description", ""),
                "tags": incident_data.get("tags", [])
            }
            
            self.active_incidents.append(incident)
            
            # Broadcast to all connected users
            await self._broadcast_to_all({
                "type": "incident_created",
                "data": incident
            })
            
            return incident
        
        @self.app.websocket("/ws/{user_id}")
        async def websocket_endpoint(websocket: WebSocket, user_id: str):
            """WebSocket endpoint for real-time communication"""
            await self._handle_websocket_connection(websocket, user_id)
    
    async def _handle_websocket_connection(self, websocket: WebSocket, user_id: str):
        """Handle WebSocket connection lifecycle"""
        await websocket.accept()
        
        # Create user session
        user = ConnectedUser(
            user_id=user_id,
            websocket=websocket,
            username=f"User-{user_id[:8]}",
            connected_at=datetime.now(),
            last_activity=datetime.now()
        )
        
        self.connected_users[user_id] = user
        
        # Send welcome message with current state
        await websocket.send_json({
            "type": "welcome",
            "data": {
                "user_id": user_id,
                "metrics": asdict(self.metrics),
                "active_users": len(self.connected_users),
                "recent_events": [asdict(e) for e in self.event_history[-10:]]
            }
        })
        
        # Notify other users
        await self._broadcast_to_others(user_id, {
            "type": "user_joined",
            "data": {"user_id": user_id, "username": user.username}
        })
        
        try:
            while True:
                # Receive messages from client
                message = await websocket.receive_json()
                await self._handle_websocket_message(user_id, message)
                
        except WebSocketDisconnect:
            # Clean up on disconnect
            del self.connected_users[user_id]
            
            # Notify other users
            await self._broadcast_to_others(user_id, {
                "type": "user_left",
                "data": {"user_id": user_id}
            })
    
    async def _handle_websocket_message(self, user_id: str, message: Dict[str, Any]):
        """Handle incoming WebSocket messages"""
        message_type = message.get("type")
        data = message.get("data", {})
        
        # Update user activity
        if user_id in self.connected_users:
            self.connected_users[user_id].last_activity = datetime.now()
        
        if message_type == "annotation":
            # Handle shared annotations
            annotation = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "content": data.get("content", ""),
                "x": data.get("x", 0),
                "y": data.get("y", 0),
                "timestamp": datetime.now().isoformat()
            }
            
            self.shared_annotations.append(annotation)
            
            # Broadcast to all users
            await self._broadcast_to_all({
                "type": "annotation_added",
                "data": annotation
            })
        
        elif message_type == "cursor_move":
            # Handle collaborative cursors
            await self._broadcast_to_others(user_id, {
                "type": "cursor_update",
                "data": {
                    "user_id": user_id,
                    "x": data.get("x", 0),
                    "y": data.get("y", 0)
                }
            })
        
        elif message_type == "incident_update":
            # Handle incident updates
            incident_id = data.get("incident_id")
            updates = data.get("updates", {})
            
            # Find and update incident
            for incident in self.active_incidents:
                if incident["id"] == incident_id:
                    incident.update(updates)
                    incident["updated_at"] = datetime.now().isoformat()
                    incident["updated_by"] = user_id
                    
                    # Broadcast update
                    await self._broadcast_to_all({
                        "type": "incident_updated",
                        "data": incident
                    })
                    break
    
    async def _broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast message to all connected users"""
        if not self.connected_users:
            return
        
        disconnected_users = []
        
        for user_id, user in self.connected_users.items():
            try:
                await user.websocket.send_json(message)
            except Exception:
                # Mark for removal
                disconnected_users.append(user_id)
        
        # Clean up disconnected users
        for user_id in disconnected_users:
            del self.connected_users[user_id]
    
    async def _broadcast_to_others(self, sender_id: str, message: Dict[str, Any]):
        """Broadcast message to all users except sender"""
        for user_id, user in self.connected_users.items():
            if user_id != sender_id:
                try:
                    await user.websocket.send_json(message)
                except Exception:
                    pass  # Handle disconnections gracefully
    
    def _get_dashboard_html(self) -> str:
        """Generate the main dashboard HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚨 Beast Mode War Room</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Monaco', 'Menlo', monospace;
            background: #0a0a0a;
            color: #00ff00;
            overflow: hidden;
        }
        
        .war-room-header {
            background: linear-gradient(90deg, #ff0000, #ff6600);
            color: white;
            padding: 10px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #ff0000;
        }
        
        .war-room-title {
            font-size: 24px;
            font-weight: bold;
        }
        
        .status-indicators {
            display: flex;
            gap: 20px;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        .status-dot.green { background: #00ff00; }
        .status-dot.yellow { background: #ffff00; }
        .status-dot.red { background: #ff0000; }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            grid-template-rows: 1fr 1fr;
            height: calc(100vh - 60px);
            gap: 2px;
            background: #333;
        }
        
        .dashboard-panel {
            background: #1a1a1a;
            border: 1px solid #333;
            padding: 15px;
            overflow-y: auto;
        }
        
        .panel-title {
            color: #00ffff;
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 10px;
            border-bottom: 1px solid #333;
            padding-bottom: 5px;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .metric-card {
            background: #2a2a2a;
            padding: 10px;
            border-radius: 4px;
            border-left: 3px solid #00ff00;
        }
        
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #00ff00;
        }
        
        .metric-label {
            font-size: 12px;
            color: #888;
        }
        
        .event-list {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .event-item {
            padding: 8px;
            margin-bottom: 5px;
            background: #2a2a2a;
            border-radius: 3px;
            border-left: 3px solid #00ff00;
            font-size: 12px;
        }
        
        .event-item.warning { border-left-color: #ffff00; }
        .event-item.error { border-left-color: #ff0000; }
        .event-item.critical { border-left-color: #ff0000; background: #330000; }
        
        .event-timestamp {
            color: #666;
            font-size: 10px;
        }
        
        .chart-container {
            position: relative;
            height: 200px;
            margin-top: 10px;
        }
        
        .user-list {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
        }
        
        .user-badge {
            background: #333;
            color: #00ff00;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 10px;
            border: 1px solid #00ff00;
        }
        
        .connection-status {
            position: fixed;
            top: 10px;
            right: 10px;
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 12px;
            z-index: 1000;
        }
        
        .connection-status.connected {
            background: #004400;
            color: #00ff00;
            border: 1px solid #00ff00;
        }
        
        .connection-status.disconnected {
            background: #440000;
            color: #ff0000;
            border: 1px solid #ff0000;
        }
        
        .incident-item {
            background: #2a2a2a;
            border: 1px solid #666;
            border-radius: 4px;
            padding: 10px;
            margin-bottom: 8px;
        }
        
        .incident-title {
            color: #ff6600;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .incident-meta {
            font-size: 10px;
            color: #888;
        }
        
        .severity-high { border-left: 3px solid #ff0000; }
        .severity-medium { border-left: 3px solid #ffff00; }
        .severity-low { border-left: 3px solid #00ff00; }
    </style>
</head>
<body>
    <div class="war-room-header">
        <div class="war-room-title">🚨 BEAST MODE WAR ROOM</div>
        <div class="status-indicators">
            <div class="status-indicator">
                <div class="status-dot green"></div>
                <span>Systems Nominal</span>
            </div>
            <div class="status-indicator">
                <div class="status-dot yellow"></div>
                <span id="active-users">0 Active Users</span>
            </div>
            <div class="status-indicator">
                <div class="status-dot red"></div>
                <span id="critical-alerts">0 Critical Alerts</span>
            </div>
        </div>
    </div>
    
    <div class="connection-status" id="connection-status">Connecting...</div>
    
    <div class="dashboard-grid">
        <!-- System Metrics Panel -->
        <div class="dashboard-panel">
            <div class="panel-title">📊 System Metrics</div>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value" id="test-pass-rate">0%</div>
                    <div class="metric-label">Test Pass Rate</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="system-health">100%</div>
                    <div class="metric-label">System Health</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="deployment-status">STABLE</div>
                    <div class="metric-label">Deployment</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="total-events">0</div>
                    <div class="metric-label">Total Events</div>
                </div>
            </div>
            <div class="chart-container">
                <canvas id="metrics-chart"></canvas>
            </div>
        </div>
        
        <!-- Real-time Events Panel -->
        <div class="dashboard-panel">
            <div class="panel-title">⚡ Real-time Events</div>
            <div class="event-list" id="event-list">
                <div class="event-item">
                    <div>System initialized</div>
                    <div class="event-timestamp">Waiting for events...</div>
                </div>
            </div>
        </div>
        
        <!-- Active Incidents Panel -->
        <div class="dashboard-panel">
            <div class="panel-title">🚨 Active Incidents</div>
            <div id="incident-list">
                <div style="color: #666; text-align: center; padding: 20px;">
                    No active incidents
                </div>
            </div>
        </div>
        
        <!-- Hubris Prevention Panel -->
        <div class="dashboard-panel">
            <div class="panel-title">🛡️ Hubris Prevention</div>
            <div id="hubris-status">
                <div style="color: #00ff00;">All systems nominal</div>
                <div style="color: #666; font-size: 12px;">No hubris detected</div>
            </div>
        </div>
        
        <!-- Team Collaboration Panel -->
        <div class="dashboard-panel">
            <div class="panel-title">👥 Team Collaboration</div>
            <div>Active Users:</div>
            <div class="user-list" id="user-list">
                <div class="user-badge">Connecting...</div>
            </div>
        </div>
        
        <!-- System Health Chart Panel -->
        <div class="dashboard-panel">
            <div class="panel-title">📈 System Health Trends</div>
            <div class="chart-container">
                <canvas id="health-chart"></canvas>
            </div>
        </div>
    </div>

    <script>
        // War Room Dashboard JavaScript
        class WarRoomDashboard {
            constructor() {
                this.userId = 'user-' + Math.random().toString(36).substr(2, 9);
                this.websocket = null;
                this.metricsChart = null;
                this.healthChart = null;
                this.init();
            }
            
            init() {
                this.connectWebSocket();
                this.initCharts();
                this.startHeartbeat();
            }
            
            connectWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws/${this.userId}`;
                
                this.websocket = new WebSocket(wsUrl);
                
                this.websocket.onopen = () => {
                    this.updateConnectionStatus('connected');
                };
                
                this.websocket.onmessage = (event) => {
                    const message = JSON.parse(event.data);
                    this.handleMessage(message);
                };
                
                this.websocket.onclose = () => {
                    this.updateConnectionStatus('disconnected');
                    // Reconnect after 3 seconds
                    setTimeout(() => this.connectWebSocket(), 3000);
                };
                
                this.websocket.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    this.updateConnectionStatus('disconnected');
                };
            }
            
            handleMessage(message) {
                switch(message.type) {
                    case 'welcome':
                        this.updateMetrics(message.data.metrics);
                        this.updateEvents(message.data.recent_events);
                        break;
                    case 'metrics_update':
                        this.updateMetrics(message.data);
                        break;
                    case 'event':
                        this.addEvent(message.data);
                        break;
                    case 'user_joined':
                        this.addUser(message.data);
                        break;
                    case 'user_left':
                        this.removeUser(message.data.user_id);
                        break;
                    case 'incident_created':
                        this.addIncident(message.data);
                        break;
                }
            }
            
            updateConnectionStatus(status) {
                const statusEl = document.getElementById('connection-status');
                statusEl.textContent = status === 'connected' ? '🟢 Connected' : '🔴 Disconnected';
                statusEl.className = `connection-status ${status}`;
            }
            
            updateMetrics(metrics) {
                document.getElementById('test-pass-rate').textContent = `${metrics.test_pass_rate.toFixed(1)}%`;
                document.getElementById('system-health').textContent = `${metrics.system_health_score.toFixed(1)}%`;
                document.getElementById('deployment-status').textContent = metrics.deployment_status.toUpperCase();
                document.getElementById('total-events').textContent = metrics.total_events;
                document.getElementById('active-users').textContent = `${metrics.active_users} Active Users`;
                document.getElementById('critical-alerts').textContent = `${metrics.critical_alerts} Critical Alerts`;
            }
            
            addEvent(event) {
                const eventList = document.getElementById('event-list');
                const eventEl = document.createElement('div');
                eventEl.className = `event-item ${event.severity}`;
                
                const timestamp = new Date(event.timestamp).toLocaleTimeString();
                eventEl.innerHTML = `
                    <div>${event.data.message || event.event_type}</div>
                    <div class="event-timestamp">${timestamp} - ${event.source}</div>
                `;
                
                eventList.insertBefore(eventEl, eventList.firstChild);
                
                // Keep only last 20 events
                while (eventList.children.length > 20) {
                    eventList.removeChild(eventList.lastChild);
                }
            }
            
            updateEvents(events) {
                const eventList = document.getElementById('event-list');
                eventList.innerHTML = '';
                
                events.forEach(event => this.addEvent(event));
            }
            
            addIncident(incident) {
                const incidentList = document.getElementById('incident-list');
                const incidentEl = document.createElement('div');
                incidentEl.className = `incident-item severity-${incident.severity}`;
                
                incidentEl.innerHTML = `
                    <div class="incident-title">${incident.title}</div>
                    <div class="incident-meta">
                        ${incident.severity.toUpperCase()} • Created: ${new Date(incident.created_at).toLocaleTimeString()}
                    </div>
                `;
                
                incidentList.appendChild(incidentEl);
            }
            
            initCharts() {
                // Metrics Chart
                const metricsCtx = document.getElementById('metrics-chart').getContext('2d');
                this.metricsChart = new Chart(metricsCtx, {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: 'System Health',
                            data: [],
                            borderColor: '#00ff00',
                            backgroundColor: 'rgba(0, 255, 0, 0.1)',
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: { beginAtZero: true, max: 100 }
                        },
                        plugins: {
                            legend: { display: false }
                        }
                    }
                });
                
                // Health Chart
                const healthCtx = document.getElementById('health-chart').getContext('2d');
                this.healthChart = new Chart(healthCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Healthy', 'Warning', 'Critical'],
                        datasets: [{
                            data: [85, 10, 5],
                            backgroundColor: ['#00ff00', '#ffff00', '#ff0000']
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { position: 'bottom' }
                        }
                    }
                });
            }
            
            startHeartbeat() {
                setInterval(() => {
                    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
                        this.websocket.send(JSON.stringify({
                            type: 'heartbeat',
                            timestamp: new Date().toISOString()
                        }));
                    }
                }, 30000); // Every 30 seconds
            }
        }
        
        // Initialize dashboard when page loads
        document.addEventListener('DOMContentLoaded', () => {
            new WarRoomDashboard();
        });
    </script>
</body>
</html>
        """
    
    async def publish_event(self, event: Event):
        """Publish an event to all connected clients"""
        self.event_history.append(event)
        
        # Keep only last 1000 events
        if len(self.event_history) > 1000:
            self.event_history = self.event_history[-1000:]
        
        # Update metrics
        self.metrics.total_events = len(self.event_history)
        
        if event.severity in [EventSeverity.ERROR, EventSeverity.CRITICAL]:
            self.metrics.critical_alerts += 1
        
        # Broadcast to all connected users
        await self._broadcast_to_all({
            "type": "event",
            "data": asdict(event)
        })
    
    async def update_metrics(self, metrics_update: Dict[str, Any]):
        """Update dashboard metrics"""
        for key, value in metrics_update.items():
            if hasattr(self.metrics, key):
                setattr(self.metrics, key, value)
        
        self.metrics.last_updated = datetime.now()
        
        # Broadcast metrics update
        await self._broadcast_to_all({
            "type": "metrics_update",
            "data": asdict(self.metrics)
        })
    
    async def start_server(self):
        """Start the War Room server"""
        self.status = "running"
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
    
    # ReflectiveModule interface
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the War Room server"""
        return {
            "status": self.status,
            "connected_users": len(self.connected_users),
            "total_events": len(self.event_history),
            "active_incidents": len(self.active_incidents),
            "server_host": self.host,
            "server_port": self.port
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return {
            "websocket_connections": len(self.connected_users),
            "events_processed": len(self.event_history),
            "memory_usage": "moderate",
            "cpu_usage": "low"
        }