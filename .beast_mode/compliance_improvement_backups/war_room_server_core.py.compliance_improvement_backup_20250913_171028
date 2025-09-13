"""
War Room Server Core

This module was extracted from war_room_server.py
as part of RM-DDD compliance refactoring.
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
    deployment_status: str = 'stable'
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

    def __init__(self, host: str='0.0.0.0', port: int=8080):
        super().__init__()
        self.host = host
        self.port = port
        self.app = FastAPI(title='Beast Mode War Room', version='1.0.0')
        self.connected_users: Dict[str, ConnectedUser] = {}
        self.event_history: List[Event] = []
        self.metrics = DashboardMetrics(last_updated=datetime.now())
        self.active_incidents: List[Dict[str, Any]] = []
        self.shared_annotations: List[Dict[str, Any]] = []
        self.system_alerts: List[Dict[str, Any]] = []
        self._setup_routes()
        self._setup_middleware()

    def _setup_middleware(self):
        """Configure CORS and other middleware"""
        self.app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

    def _setup_routes(self):
        """Setup all API routes and WebSocket endpoints"""

        @self.app.get('/', response_class=HTMLResponse)
        async def dashboard_home():
            """Serve the main dashboard HTML"""
            return self._get_dashboard_html()

        @self.app.get('/api/health')
        async def health_check():
            """Health check endpoint"""
            return {'status': 'healthy', 'timestamp': datetime.now().isoformat(), 'active_connections': len(self.connected_users), 'metrics': asdict(self.metrics)}

        @self.app.get('/api/metrics')
        async def get_metrics():
            """Get current dashboard metrics"""
            self.metrics.active_users = len(self.connected_users)
            self.metrics.last_updated = datetime.now()
            return asdict(self.metrics)

        @self.app.get('/api/events')
        async def get_events(limit: int=100, severity: Optional[str]=None):
            """Get recent events with optional filtering"""
            events = self.event_history[-limit:]
            if severity:
                try:
                    severity_filter = EventSeverity(severity.lower())
                    events = [e for e in events if e.severity == severity_filter]
                except ValueError:
                    raise HTTPException(status_code=400, detail=f'Invalid severity: {severity}')
            return {'events': [asdict(event) for event in events], 'total': len(events), 'timestamp': datetime.now().isoformat()}

        @self.app.get('/api/incidents')
        async def get_incidents():
            """Get active incidents"""
            return {'incidents': self.active_incidents, 'count': len(self.active_incidents)}

        @self.app.post('/api/incidents')
        async def create_incident(incident_data: Dict[str, Any]):
            """Create a new incident"""
            incident = {'id': str(uuid.uuid4()), 'title': incident_data.get('title', 'New Incident'), 'severity': incident_data.get('severity', 'medium'), 'status': 'open', 'created_at': datetime.now().isoformat(), 'created_by': incident_data.get('created_by', 'system'), 'description': incident_data.get('description', ''), 'tags': incident_data.get('tags', [])}
            self.active_incidents.append(incident)
            await self._broadcast_to_all({'type': 'incident_created', 'data': incident})
            return incident

        @self.app.websocket('/ws/{user_id}')
        async def websocket_endpoint(websocket: WebSocket, user_id: str):
            """WebSocket endpoint for real-time communication"""
            await self._handle_websocket_connection(websocket, user_id)

    async def _handle_websocket_connection(self, websocket: WebSocket, user_id: str):
        """Handle WebSocket connection lifecycle"""
        await websocket.accept()
        user = ConnectedUser(user_id=user_id, websocket=websocket, username=f'User-{user_id[:8]}', connected_at=datetime.now(), last_activity=datetime.now())
        self.connected_users[user_id] = user
        await websocket.send_json({'type': 'welcome', 'data': {'user_id': user_id, 'metrics': asdict(self.metrics), 'active_users': len(self.connected_users), 'recent_events': [asdict(e) for e in self.event_history[-10:]]}})
        await self._broadcast_to_others(user_id, {'type': 'user_joined', 'data': {'user_id': user_id, 'username': user.username}})
        try:
            while True:
                message = await websocket.receive_json()
                await self._handle_websocket_message(user_id, message)
        except WebSocketDisconnect:
            del self.connected_users[user_id]
            await self._broadcast_to_others(user_id, {'type': 'user_left', 'data': {'user_id': user_id}})

    async def _handle_websocket_message(self, user_id: str, message: Dict[str, Any]):
        """Handle incoming WebSocket messages"""
        message_type = message.get('type')
        data = message.get('data', {})
        if user_id in self.connected_users:
            self.connected_users[user_id].last_activity = datetime.now()
        if message_type == 'annotation':
            annotation = {'id': str(uuid.uuid4()), 'user_id': user_id, 'content': data.get('content', ''), 'x': data.get('x', 0), 'y': data.get('y', 0), 'timestamp': datetime.now().isoformat()}
            self.shared_annotations.append(annotation)
            await self._broadcast_to_all({'type': 'annotation_added', 'data': annotation})
        elif message_type == 'cursor_move':
            await self._broadcast_to_others(user_id, {'type': 'cursor_update', 'data': {'user_id': user_id, 'x': data.get('x', 0), 'y': data.get('y', 0)}})
        elif message_type == 'incident_update':
            incident_id = data.get('incident_id')
            updates = data.get('updates', {})
            for incident in self.active_incidents:
                if incident['id'] == incident_id:
                    incident.update(updates)
                    incident['updated_at'] = datetime.now().isoformat()
                    incident['updated_by'] = user_id
                    await self._broadcast_to_all({'type': 'incident_updated', 'data': incident})
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
                disconnected_users.append(user_id)
        for user_id in disconnected_users:
            del self.connected_users[user_id]

    async def _broadcast_to_others(self, sender_id: str, message: Dict[str, Any]):
        """Broadcast message to all users except sender"""
        for user_id, user in self.connected_users.items():
            if user_id != sender_id:
                try:
                    await user.websocket.send_json(message)
                except Exception:
                    pass

    def _get_dashboard_html(self) -> str:
        """Generate the main dashboard HTML"""
        return '\n<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>🚨 Beast Mode War Room</title>\n    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>\n    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>\n    <style>\n        * { margin: 0; padding: 0; box-sizing: border-box; }\n        \n        body {\n            font-family: \'Monaco\', \'Menlo\', monospace;\n            background: #0a0a0a;\n            color: #00ff00;\n            overflow: hidden;\n        }\n        \n        .war-room-header {\n            background: linear-gradient(90deg, #ff0000, #ff6600);\n            color: white;\n            padding: 10px 20px;\n            display: flex;\n            justify-content: space-between;\n            align-items: center;\n            border-bottom: 2px solid #ff0000;\n        }\n        \n        .war-room-title {\n            font-size: 24px;\n            font-weight: bold;\n        }\n        \n        .status-indicators {\n            display: flex;\n            gap: 20px;\n        }\n        \n        .status-indicator {\n            display: flex;\n            align-items: center;\n            gap: 5px;\n        }\n        \n        .status-dot {\n            width: 12px;\n            height: 12px;\n            border-radius: 50%;\n            animation: pulse 2s infinite;\n        }\n        \n        .status-dot.green { background: #00ff00; }\n        .status-dot.yellow { background: #ffff00; }\n        .status-dot.red { background: #ff0000; }\n        \n        @keyframes pulse {\n            0%, 100% { opacity: 1; }\n            50% { opacity: 0.5; }\n        }\n        \n        .dashboard-grid {\n            display: grid;\n            grid-template-columns: 1fr 1fr 1fr;\n            grid-template-rows: 1fr 1fr;\n            height: calc(100vh - 60px);\n            gap: 2px;\n            background: #333;\n        }\n        \n        .dashboard-panel {\n            background: #1a1a1a;\n            border: 1px solid #333;\n            padding: 15px;\n            overflow-y: auto;\n        }\n        \n        .panel-title {\n            color: #00ffff;\n            font-size: 16px;\n            font-weight: bold;\n            margin-bottom: 10px;\n            border-bottom: 1px solid #333;\n            padding-bottom: 5px;\n        }\n        \n        .metrics-grid {\n            display: grid;\n            grid-template-columns: 1fr 1fr;\n            gap: 10px;\n            margin-bottom: 15px;\n        }\n        \n        .metric-card {\n            background: #2a2a2a;\n            padding: 10px;\n            border-radius: 4px;\n            border-left: 3px solid #00ff00;\n        }\n        \n        .metric-value {\n            font-size: 24px;\n            font-weight: bold;\n            color: #00ff00;\n        }\n        \n        .metric-label {\n            font-size: 12px;\n            color: #888;\n        }\n        \n        .event-list {\n            max-height: 300px;\n            overflow-y: auto;\n        }\n        \n        .event-item {\n            padding: 8px;\n            margin-bottom: 5px;\n            background: #2a2a2a;\n            border-radius: 3px;\n            border-left: 3px solid #00ff00;\n            font-size: 12px;\n        }\n        \n        .event-item.warning { border-left-color: #ffff00; }\n        .event-item.error { border-left-color: #ff0000; }\n        .event-item.critical { border-left-color: #ff0000; background: #330000; }\n        \n        .event-timestamp {\n            color: #666;\n            font-size: 10px;\n        }\n        \n        .chart-container {\n            position: relative;\n            height: 200px;\n            margin-top: 10px;\n        }\n        \n        .user-list {\n            display: flex;\n            flex-wrap: wrap;\n            gap: 5px;\n        }\n        \n        .user-badge {\n            background: #333;\n            color: #00ff00;\n            padding: 2px 8px;\n            border-radius: 12px;\n            font-size: 10px;\n            border: 1px solid #00ff00;\n        }\n        \n        .connection-status {\n            position: fixed;\n            top: 10px;\n            right: 10px;\n            padding: 5px 10px;\n            border-radius: 3px;\n            font-size: 12px;\n            z-index: 1000;\n        }\n        \n        .connection-status.connected {\n            background: #004400;\n            color: #00ff00;\n            border: 1px solid #00ff00;\n        }\n        \n        .connection-status.disconnected {\n            background: #440000;\n            color: #ff0000;\n            border: 1px solid #ff0000;\n        }\n        \n        .incident-item {\n            background: #2a2a2a;\n            border: 1px solid #666;\n            border-radius: 4px;\n            padding: 10px;\n            margin-bottom: 8px;\n        }\n        \n        .incident-title {\n            color: #ff6600;\n            font-weight: bold;\n            margin-bottom: 5px;\n        }\n        \n        .incident-meta {\n            font-size: 10px;\n            color: #888;\n        }\n        \n        .severity-high { border-left: 3px solid #ff0000; }\n        .severity-medium { border-left: 3px solid #ffff00; }\n        .severity-low { border-left: 3px solid #00ff00; }\n    </style>\n</head>\n<body>\n    <div class="war-room-header">\n        <div class="war-room-title">🚨 BEAST MODE WAR ROOM</div>\n        <div class="status-indicators">\n            <div class="status-indicator">\n                <div class="status-dot green"></div>\n                <span>Systems Nominal</span>\n            </div>\n            <div class="status-indicator">\n                <div class="status-dot yellow"></div>\n                <span id="active-users">0 Active Users</span>\n            </div>\n            <div class="status-indicator">\n                <div class="status-dot red"></div>\n                <span id="critical-alerts">0 Critical Alerts</span>\n            </div>\n        </div>\n    </div>\n    \n    <div class="connection-status" id="connection-status">Connecting...</div>\n    \n    <div class="dashboard-grid">\n        <!-- System Metrics Panel -->\n        <div class="dashboard-panel">\n            <div class="panel-title">📊 System Metrics</div>\n            <div class="metrics-grid">\n                <div class="metric-card">\n                    <div class="metric-value" id="test-pass-rate">0%</div>\n                    <div class="metric-label">Test Pass Rate</div>\n                </div>\n                <div class="metric-card">\n                    <div class="metric-value" id="system-health">100%</div>\n                    <div class="metric-label">System Health</div>\n                </div>\n                <div class="metric-card">\n                    <div class="metric-value" id="deployment-status">STABLE</div>\n                    <div class="metric-label">Deployment</div>\n                </div>\n                <div class="metric-card">\n                    <div class="metric-value" id="total-events">0</div>\n                    <div class="metric-label">Total Events</div>\n                </div>\n            </div>\n            <div class="chart-container">\n                <canvas id="metrics-chart"></canvas>\n            </div>\n        </div>\n        \n        <!-- Real-time Events Panel -->\n        <div class="dashboard-panel">\n            <div class="panel-title">⚡ Real-time Events</div>\n            <div class="event-list" id="event-list">\n                <div class="event-item">\n                    <div>System initialized</div>\n                    <div class="event-timestamp">Waiting for events...</div>\n                </div>\n            </div>\n        </div>\n        \n        <!-- Active Incidents Panel -->\n        <div class="dashboard-panel">\n            <div class="panel-title">🚨 Active Incidents</div>\n            <div id="incident-list">\n                <div style="color: #666; text-align: center; padding: 20px;">\n                    No active incidents\n                </div>\n            </div>\n        </div>\n        \n        <!-- Hubris Prevention Panel -->\n        <div class="dashboard-panel">\n            <div class="panel-title">🛡️ Hubris Prevention</div>\n            <div id="hubris-status">\n                <div style="color: #00ff00;">All systems nominal</div>\n                <div style="color: #666; font-size: 12px;">No hubris detected</div>\n            </div>\n        </div>\n        \n        <!-- Team Collaboration Panel -->\n        <div class="dashboard-panel">\n            <div class="panel-title">👥 Team Collaboration</div>\n            <div>Active Users:</div>\n            <div class="user-list" id="user-list">\n                <div class="user-badge">Connecting...</div>\n            </div>\n        </div>\n        \n        <!-- System Health Chart Panel -->\n        <div class="dashboard-panel">\n            <div class="panel-title">📈 System Health Trends</div>\n            <div class="chart-container">\n                <canvas id="health-chart"></canvas>\n            </div>\n        </div>\n    </div>\n\n    <script>\n        // War Room Dashboard JavaScript\n        class WarRoomDashboard {\n            constructor() {\n                this.userId = \'user-\' + Math.random().toString(36).substr(2, 9);\n                this.websocket = null;\n                this.metricsChart = null;\n                this.healthChart = null;\n                this.init();\n            }\n            \n            init() {\n                this.connectWebSocket();\n                this.initCharts();\n                this.startHeartbeat();\n            }\n            \n            connectWebSocket() {\n                const protocol = window.location.protocol === \'https:\' ? \'wss:\' : \'ws:\';\n                const wsUrl = `${protocol}//${window.location.host}/ws/${this.userId}`;\n                \n                this.websocket = new WebSocket(wsUrl);\n                \n                this.websocket.onopen = () => {\n                    this.updateConnectionStatus(\'connected\');\n                };\n                \n                this.websocket.onmessage = (event) => {\n                    const message = JSON.parse(event.data);\n                    this.handleMessage(message);\n                };\n                \n                this.websocket.onclose = () => {\n                    this.updateConnectionStatus(\'disconnected\');\n                    // Reconnect after 3 seconds\n                    setTimeout(() => this.connectWebSocket(), 3000);\n                };\n                \n                this.websocket.onerror = (error) => {\n                    console.error(\'WebSocket error:\', error);\n                    this.updateConnectionStatus(\'disconnected\');\n                };\n            }\n            \n            handleMessage(message) {\n                switch(message.type) {\n                    case \'welcome\':\n                        this.updateMetrics(message.data.metrics);\n                        this.updateEvents(message.data.recent_events);\n                        break;\n                    case \'metrics_update\':\n                        this.updateMetrics(message.data);\n                        break;\n                    case \'event\':\n                        this.addEvent(message.data);\n                        break;\n                    case \'user_joined\':\n                        this.addUser(message.data);\n                        break;\n                    case \'user_left\':\n                        this.removeUser(message.data.user_id);\n                        break;\n                    case \'incident_created\':\n                        this.addIncident(message.data);\n                        break;\n                }\n            }\n            \n            updateConnectionStatus(status) {\n                const statusEl = document.getElementById(\'connection-status\');\n                statusEl.textContent = status === \'connected\' ? \'🟢 Connected\' : \'🔴 Disconnected\';\n                statusEl.className = `connection-status ${status}`;\n            }\n            \n            updateMetrics(metrics) {\n                document.getElementById(\'test-pass-rate\').textContent = `${metrics.test_pass_rate.toFixed(1)}%`;\n                document.getElementById(\'system-health\').textContent = `${metrics.system_health_score.toFixed(1)}%`;\n                document.getElementById(\'deployment-status\').textContent = metrics.deployment_status.toUpperCase();\n                document.getElementById(\'total-events\').textContent = metrics.total_events;\n                document.getElementById(\'active-users\').textContent = `${metrics.active_users} Active Users`;\n                document.getElementById(\'critical-alerts\').textContent = `${metrics.critical_alerts} Critical Alerts`;\n            }\n            \n            addEvent(event) {\n                const eventList = document.getElementById(\'event-list\');\n                const eventEl = document.createElement(\'div\');\n                eventEl.className = `event-item ${event.severity}`;\n                \n                const timestamp = new Date(event.timestamp).toLocaleTimeString();\n                eventEl.innerHTML = `\n                    <div>${event.data.message || event.event_type}</div>\n                    <div class="event-timestamp">${timestamp} - ${event.source}</div>\n                `;\n                \n                eventList.insertBefore(eventEl, eventList.firstChild);\n                \n                // Keep only last 20 events\n                while (eventList.children.length > 20) {\n                    eventList.removeChild(eventList.lastChild);\n                }\n            }\n            \n            updateEvents(events) {\n                const eventList = document.getElementById(\'event-list\');\n                eventList.innerHTML = \'\';\n                \n                events.forEach(event => this.addEvent(event));\n            }\n            \n            addIncident(incident) {\n                const incidentList = document.getElementById(\'incident-list\');\n                const incidentEl = document.createElement(\'div\');\n                incidentEl.className = `incident-item severity-${incident.severity}`;\n                \n                incidentEl.innerHTML = `\n                    <div class="incident-title">${incident.title}</div>\n                    <div class="incident-meta">\n                        ${incident.severity.toUpperCase()} • Created: ${new Date(incident.created_at).toLocaleTimeString()}\n                    </div>\n                `;\n                \n                incidentList.appendChild(incidentEl);\n            }\n            \n            initCharts() {\n                // Metrics Chart\n                const metricsCtx = document.getElementById(\'metrics-chart\').getContext(\'2d\');\n                this.metricsChart = new Chart(metricsCtx, {\n                    type: \'line\',\n                    data: {\n                        labels: [],\n                        datasets: [{\n                            label: \'System Health\',\n                            data: [],\n                            borderColor: \'#00ff00\',\n                            backgroundColor: \'rgba(0, 255, 0, 0.1)\',\n                            tension: 0.4\n                        }]\n                    },\n                    options: {\n                        responsive: true,\n                        maintainAspectRatio: false,\n                        scales: {\n                            y: { beginAtZero: true, max: 100 }\n                        },\n                        plugins: {\n                            legend: { display: false }\n                        }\n                    }\n                });\n                \n                // Health Chart\n                const healthCtx = document.getElementById(\'health-chart\').getContext(\'2d\');\n                this.healthChart = new Chart(healthCtx, {\n                    type: \'doughnut\',\n                    data: {\n                        labels: [\'Healthy\', \'Warning\', \'Critical\'],\n                        datasets: [{\n                            data: [85, 10, 5],\n                            backgroundColor: [\'#00ff00\', \'#ffff00\', \'#ff0000\']\n                        }]\n                    },\n                    options: {\n                        responsive: true,\n                        maintainAspectRatio: false,\n                        plugins: {\n                            legend: { position: \'bottom\' }\n                        }\n                    }\n                });\n            }\n            \n            startHeartbeat() {\n                setInterval(() => {\n                    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {\n                        this.websocket.send(JSON.stringify({\n                            type: \'heartbeat\',\n                            timestamp: new Date().toISOString()\n                        }));\n                    }\n                }, 30000); // Every 30 seconds\n            }\n        }\n        \n        // Initialize dashboard when page loads\n        document.addEventListener(\'DOMContentLoaded\', () => {\n            new WarRoomDashboard();\n        });\n    </script>\n</body>\n</html>\n        '

    async def publish_event(self, event: Event):
        """Publish an event to all connected clients"""
        self.event_history.append(event)
        if len(self.event_history) > 1000:
            self.event_history = self.event_history[-1000:]
        self.metrics.total_events = len(self.event_history)
        if event.severity in [EventSeverity.ERROR, EventSeverity.CRITICAL]:
            self.metrics.critical_alerts += 1
        await self._broadcast_to_all({'type': 'event', 'data': asdict(event)})

    async def update_metrics(self, metrics_update: Dict[str, Any]):
        """Update dashboard metrics"""
        for key, value in metrics_update.items():
            if hasattr(self.metrics, key):
                setattr(self.metrics, key, value)
        self.metrics.last_updated = datetime.now()
        await self._broadcast_to_all({'type': 'metrics_update', 'data': asdict(self.metrics)})

    async def start_server(self):
        """Start the War Room server"""
        self.status = 'running'
        config = uvicorn.Config(self.app, host=self.host, port=self.port, log_level='info')
        server = uvicorn.Server(config)
        await server.serve()

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the War Room server"""
        return {'status': self.status, 'connected_users': len(self.connected_users), 'total_events': len(self.event_history), 'active_incidents': len(self.active_incidents), 'server_host': self.host, 'server_port': self.port}

    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return {'websocket_connections': len(self.connected_users), 'events_processed': len(self.event_history), 'memory_usage': 'moderate', 'cpu_usage': 'low'}

def __init__(self, host: str='0.0.0.0', port: int=8080):
    super().__init__()
    self.host = host
    self.port = port
    self.app = FastAPI(title='Beast Mode War Room', version='1.0.0')
    self.connected_users: Dict[str, ConnectedUser] = {}
    self.event_history: List[Event] = []
    self.metrics = DashboardMetrics(last_updated=datetime.now())
    self.active_incidents: List[Dict[str, Any]] = []
    self.shared_annotations: List[Dict[str, Any]] = []
    self.system_alerts: List[Dict[str, Any]] = []
    self._setup_routes()
    self._setup_middleware()

def _setup_middleware(self):
    """Configure CORS and other middleware"""
    self.app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

def _setup_routes(self):
    """Setup all API routes and WebSocket endpoints"""

    @self.app.get('/', response_class=HTMLResponse)
    async def dashboard_home():
        """Serve the main dashboard HTML"""
        return self._get_dashboard_html()

    @self.app.get('/api/health')
    async def health_check():
        """Health check endpoint"""
        return {'status': 'healthy', 'timestamp': datetime.now().isoformat(), 'active_connections': len(self.connected_users), 'metrics': asdict(self.metrics)}

    @self.app.get('/api/metrics')
    async def get_metrics():
        """Get current dashboard metrics"""
        self.metrics.active_users = len(self.connected_users)
        self.metrics.last_updated = datetime.now()
        return asdict(self.metrics)

    @self.app.get('/api/events')
    async def get_events(limit: int=100, severity: Optional[str]=None):
        """Get recent events with optional filtering"""
        events = self.event_history[-limit:]
        if severity:
            try:
                severity_filter = EventSeverity(severity.lower())
                events = [e for e in events if e.severity == severity_filter]
            except ValueError:
                raise HTTPException(status_code=400, detail=f'Invalid severity: {severity}')
        return {'events': [asdict(event) for event in events], 'total': len(events), 'timestamp': datetime.now().isoformat()}

    @self.app.get('/api/incidents')
    async def get_incidents():
        """Get active incidents"""
        return {'incidents': self.active_incidents, 'count': len(self.active_incidents)}

    @self.app.post('/api/incidents')
    async def create_incident(incident_data: Dict[str, Any]):
        """Create a new incident"""
        incident = {'id': str(uuid.uuid4()), 'title': incident_data.get('title', 'New Incident'), 'severity': incident_data.get('severity', 'medium'), 'status': 'open', 'created_at': datetime.now().isoformat(), 'created_by': incident_data.get('created_by', 'system'), 'description': incident_data.get('description', ''), 'tags': incident_data.get('tags', [])}
        self.active_incidents.append(incident)
        await self._broadcast_to_all({'type': 'incident_created', 'data': incident})
        return incident

    @self.app.websocket('/ws/{user_id}')
    async def websocket_endpoint(websocket: WebSocket, user_id: str):
        """WebSocket endpoint for real-time communication"""
        await self._handle_websocket_connection(websocket, user_id)

def _get_dashboard_html(self) -> str:
    """Generate the main dashboard HTML"""
    return '\n<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>🚨 Beast Mode War Room</title>\n    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>\n    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>\n    <style>\n        * { margin: 0; padding: 0; box-sizing: border-box; }\n        \n        body {\n            font-family: \'Monaco\', \'Menlo\', monospace;\n            background: #0a0a0a;\n            color: #00ff00;\n            overflow: hidden;\n        }\n        \n        .war-room-header {\n            background: linear-gradient(90deg, #ff0000, #ff6600);\n            color: white;\n            padding: 10px 20px;\n            display: flex;\n            justify-content: space-between;\n            align-items: center;\n            border-bottom: 2px solid #ff0000;\n        }\n        \n        .war-room-title {\n            font-size: 24px;\n            font-weight: bold;\n        }\n        \n        .status-indicators {\n            display: flex;\n            gap: 20px;\n        }\n        \n        .status-indicator {\n            display: flex;\n            align-items: center;\n            gap: 5px;\n        }\n        \n        .status-dot {\n            width: 12px;\n            height: 12px;\n            border-radius: 50%;\n            animation: pulse 2s infinite;\n        }\n        \n        .status-dot.green { background: #00ff00; }\n        .status-dot.yellow { background: #ffff00; }\n        .status-dot.red { background: #ff0000; }\n        \n        @keyframes pulse {\n            0%, 100% { opacity: 1; }\n            50% { opacity: 0.5; }\n        }\n        \n        .dashboard-grid {\n            display: grid;\n            grid-template-columns: 1fr 1fr 1fr;\n            grid-template-rows: 1fr 1fr;\n            height: calc(100vh - 60px);\n            gap: 2px;\n            background: #333;\n        }\n        \n        .dashboard-panel {\n            background: #1a1a1a;\n            border: 1px solid #333;\n            padding: 15px;\n            overflow-y: auto;\n        }\n        \n        .panel-title {\n            color: #00ffff;\n            font-size: 16px;\n            font-weight: bold;\n            margin-bottom: 10px;\n            border-bottom: 1px solid #333;\n            padding-bottom: 5px;\n        }\n        \n        .metrics-grid {\n            display: grid;\n            grid-template-columns: 1fr 1fr;\n            gap: 10px;\n            margin-bottom: 15px;\n        }\n        \n        .metric-card {\n            background: #2a2a2a;\n            padding: 10px;\n            border-radius: 4px;\n            border-left: 3px solid #00ff00;\n        }\n        \n        .metric-value {\n            font-size: 24px;\n            font-weight: bold;\n            color: #00ff00;\n        }\n        \n        .metric-label {\n            font-size: 12px;\n            color: #888;\n        }\n        \n        .event-list {\n            max-height: 300px;\n            overflow-y: auto;\n        }\n        \n        .event-item {\n            padding: 8px;\n            margin-bottom: 5px;\n            background: #2a2a2a;\n            border-radius: 3px;\n            border-left: 3px solid #00ff00;\n            font-size: 12px;\n        }\n        \n        .event-item.warning { border-left-color: #ffff00; }\n        .event-item.error { border-left-color: #ff0000; }\n        .event-item.critical { border-left-color: #ff0000; background: #330000; }\n        \n        .event-timestamp {\n            color: #666;\n            font-size: 10px;\n        }\n        \n        .chart-container {\n            position: relative;\n            height: 200px;\n            margin-top: 10px;\n        }\n        \n        .user-list {\n            display: flex;\n            flex-wrap: wrap;\n            gap: 5px;\n        }\n        \n        .user-badge {\n            background: #333;\n            color: #00ff00;\n            padding: 2px 8px;\n            border-radius: 12px;\n            font-size: 10px;\n            border: 1px solid #00ff00;\n        }\n        \n        .connection-status {\n            position: fixed;\n            top: 10px;\n            right: 10px;\n            padding: 5px 10px;\n            border-radius: 3px;\n            font-size: 12px;\n            z-index: 1000;\n        }\n        \n        .connection-status.connected {\n            background: #004400;\n            color: #00ff00;\n            border: 1px solid #00ff00;\n        }\n        \n        .connection-status.disconnected {\n            background: #440000;\n            color: #ff0000;\n            border: 1px solid #ff0000;\n        }\n        \n        .incident-item {\n            background: #2a2a2a;\n            border: 1px solid #666;\n            border-radius: 4px;\n            padding: 10px;\n            margin-bottom: 8px;\n        }\n        \n        .incident-title {\n            color: #ff6600;\n            font-weight: bold;\n            margin-bottom: 5px;\n        }\n        \n        .incident-meta {\n            font-size: 10px;\n            color: #888;\n        }\n        \n        .severity-high { border-left: 3px solid #ff0000; }\n        .severity-medium { border-left: 3px solid #ffff00; }\n        .severity-low { border-left: 3px solid #00ff00; }\n    </style>\n</head>\n<body>\n    <div class="war-room-header">\n        <div class="war-room-title">🚨 BEAST MODE WAR ROOM</div>\n        <div class="status-indicators">\n            <div class="status-indicator">\n                <div class="status-dot green"></div>\n                <span>Systems Nominal</span>\n            </div>\n            <div class="status-indicator">\n                <div class="status-dot yellow"></div>\n                <span id="active-users">0 Active Users</span>\n            </div>\n            <div class="status-indicator">\n                <div class="status-dot red"></div>\n                <span id="critical-alerts">0 Critical Alerts</span>\n            </div>\n        </div>\n    </div>\n    \n    <div class="connection-status" id="connection-status">Connecting...</div>\n    \n    <div class="dashboard-grid">\n        <!-- System Metrics Panel -->\n        <div class="dashboard-panel">\n            <div class="panel-title">📊 System Metrics</div>\n            <div class="metrics-grid">\n                <div class="metric-card">\n                    <div class="metric-value" id="test-pass-rate">0%</div>\n                    <div class="metric-label">Test Pass Rate</div>\n                </div>\n                <div class="metric-card">\n                    <div class="metric-value" id="system-health">100%</div>\n                    <div class="metric-label">System Health</div>\n                </div>\n                <div class="metric-card">\n                    <div class="metric-value" id="deployment-status">STABLE</div>\n                    <div class="metric-label">Deployment</div>\n                </div>\n                <div class="metric-card">\n                    <div class="metric-value" id="total-events">0</div>\n                    <div class="metric-label">Total Events</div>\n                </div>\n            </div>\n            <div class="chart-container">\n                <canvas id="metrics-chart"></canvas>\n            </div>\n        </div>\n        \n        <!-- Real-time Events Panel -->\n        <div class="dashboard-panel">\n            <div class="panel-title">⚡ Real-time Events</div>\n            <div class="event-list" id="event-list">\n                <div class="event-item">\n                    <div>System initialized</div>\n                    <div class="event-timestamp">Waiting for events...</div>\n                </div>\n            </div>\n        </div>\n        \n        <!-- Active Incidents Panel -->\n        <div class="dashboard-panel">\n            <div class="panel-title">🚨 Active Incidents</div>\n            <div id="incident-list">\n                <div style="color: #666; text-align: center; padding: 20px;">\n                    No active incidents\n                </div>\n            </div>\n        </div>\n        \n        <!-- Hubris Prevention Panel -->\n        <div class="dashboard-panel">\n            <div class="panel-title">🛡️ Hubris Prevention</div>\n            <div id="hubris-status">\n                <div style="color: #00ff00;">All systems nominal</div>\n                <div style="color: #666; font-size: 12px;">No hubris detected</div>\n            </div>\n        </div>\n        \n        <!-- Team Collaboration Panel -->\n        <div class="dashboard-panel">\n            <div class="panel-title">👥 Team Collaboration</div>\n            <div>Active Users:</div>\n            <div class="user-list" id="user-list">\n                <div class="user-badge">Connecting...</div>\n            </div>\n        </div>\n        \n        <!-- System Health Chart Panel -->\n        <div class="dashboard-panel">\n            <div class="panel-title">📈 System Health Trends</div>\n            <div class="chart-container">\n                <canvas id="health-chart"></canvas>\n            </div>\n        </div>\n    </div>\n\n    <script>\n        // War Room Dashboard JavaScript\n        class WarRoomDashboard {\n            constructor() {\n                this.userId = \'user-\' + Math.random().toString(36).substr(2, 9);\n                this.websocket = null;\n                this.metricsChart = null;\n                this.healthChart = null;\n                this.init();\n            }\n            \n            init() {\n                this.connectWebSocket();\n                this.initCharts();\n                this.startHeartbeat();\n            }\n            \n            connectWebSocket() {\n                const protocol = window.location.protocol === \'https:\' ? \'wss:\' : \'ws:\';\n                const wsUrl = `${protocol}//${window.location.host}/ws/${this.userId}`;\n                \n                this.websocket = new WebSocket(wsUrl);\n                \n                this.websocket.onopen = () => {\n                    this.updateConnectionStatus(\'connected\');\n                };\n                \n                this.websocket.onmessage = (event) => {\n                    const message = JSON.parse(event.data);\n                    this.handleMessage(message);\n                };\n                \n                this.websocket.onclose = () => {\n                    this.updateConnectionStatus(\'disconnected\');\n                    // Reconnect after 3 seconds\n                    setTimeout(() => this.connectWebSocket(), 3000);\n                };\n                \n                this.websocket.onerror = (error) => {\n                    console.error(\'WebSocket error:\', error);\n                    this.updateConnectionStatus(\'disconnected\');\n                };\n            }\n            \n            handleMessage(message) {\n                switch(message.type) {\n                    case \'welcome\':\n                        this.updateMetrics(message.data.metrics);\n                        this.updateEvents(message.data.recent_events);\n                        break;\n                    case \'metrics_update\':\n                        this.updateMetrics(message.data);\n                        break;\n                    case \'event\':\n                        this.addEvent(message.data);\n                        break;\n                    case \'user_joined\':\n                        this.addUser(message.data);\n                        break;\n                    case \'user_left\':\n                        this.removeUser(message.data.user_id);\n                        break;\n                    case \'incident_created\':\n                        this.addIncident(message.data);\n                        break;\n                }\n            }\n            \n            updateConnectionStatus(status) {\n                const statusEl = document.getElementById(\'connection-status\');\n                statusEl.textContent = status === \'connected\' ? \'🟢 Connected\' : \'🔴 Disconnected\';\n                statusEl.className = `connection-status ${status}`;\n            }\n            \n            updateMetrics(metrics) {\n                document.getElementById(\'test-pass-rate\').textContent = `${metrics.test_pass_rate.toFixed(1)}%`;\n                document.getElementById(\'system-health\').textContent = `${metrics.system_health_score.toFixed(1)}%`;\n                document.getElementById(\'deployment-status\').textContent = metrics.deployment_status.toUpperCase();\n                document.getElementById(\'total-events\').textContent = metrics.total_events;\n                document.getElementById(\'active-users\').textContent = `${metrics.active_users} Active Users`;\n                document.getElementById(\'critical-alerts\').textContent = `${metrics.critical_alerts} Critical Alerts`;\n            }\n            \n            addEvent(event) {\n                const eventList = document.getElementById(\'event-list\');\n                const eventEl = document.createElement(\'div\');\n                eventEl.className = `event-item ${event.severity}`;\n                \n                const timestamp = new Date(event.timestamp).toLocaleTimeString();\n                eventEl.innerHTML = `\n                    <div>${event.data.message || event.event_type}</div>\n                    <div class="event-timestamp">${timestamp} - ${event.source}</div>\n                `;\n                \n                eventList.insertBefore(eventEl, eventList.firstChild);\n                \n                // Keep only last 20 events\n                while (eventList.children.length > 20) {\n                    eventList.removeChild(eventList.lastChild);\n                }\n            }\n            \n            updateEvents(events) {\n                const eventList = document.getElementById(\'event-list\');\n                eventList.innerHTML = \'\';\n                \n                events.forEach(event => this.addEvent(event));\n            }\n            \n            addIncident(incident) {\n                const incidentList = document.getElementById(\'incident-list\');\n                const incidentEl = document.createElement(\'div\');\n                incidentEl.className = `incident-item severity-${incident.severity}`;\n                \n                incidentEl.innerHTML = `\n                    <div class="incident-title">${incident.title}</div>\n                    <div class="incident-meta">\n                        ${incident.severity.toUpperCase()} • Created: ${new Date(incident.created_at).toLocaleTimeString()}\n                    </div>\n                `;\n                \n                incidentList.appendChild(incidentEl);\n            }\n            \n            initCharts() {\n                // Metrics Chart\n                const metricsCtx = document.getElementById(\'metrics-chart\').getContext(\'2d\');\n                this.metricsChart = new Chart(metricsCtx, {\n                    type: \'line\',\n                    data: {\n                        labels: [],\n                        datasets: [{\n                            label: \'System Health\',\n                            data: [],\n                            borderColor: \'#00ff00\',\n                            backgroundColor: \'rgba(0, 255, 0, 0.1)\',\n                            tension: 0.4\n                        }]\n                    },\n                    options: {\n                        responsive: true,\n                        maintainAspectRatio: false,\n                        scales: {\n                            y: { beginAtZero: true, max: 100 }\n                        },\n                        plugins: {\n                            legend: { display: false }\n                        }\n                    }\n                });\n                \n                // Health Chart\n                const healthCtx = document.getElementById(\'health-chart\').getContext(\'2d\');\n                this.healthChart = new Chart(healthCtx, {\n                    type: \'doughnut\',\n                    data: {\n                        labels: [\'Healthy\', \'Warning\', \'Critical\'],\n                        datasets: [{\n                            data: [85, 10, 5],\n                            backgroundColor: [\'#00ff00\', \'#ffff00\', \'#ff0000\']\n                        }]\n                    },\n                    options: {\n                        responsive: true,\n                        maintainAspectRatio: false,\n                        plugins: {\n                            legend: { position: \'bottom\' }\n                        }\n                    }\n                });\n            }\n            \n            startHeartbeat() {\n                setInterval(() => {\n                    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {\n                        this.websocket.send(JSON.stringify({\n                            type: \'heartbeat\',\n                            timestamp: new Date().toISOString()\n                        }));\n                    }\n                }, 30000); // Every 30 seconds\n            }\n        }\n        \n        // Initialize dashboard when page loads\n        document.addEventListener(\'DOMContentLoaded\', () => {\n            new WarRoomDashboard();\n        });\n    </script>\n</body>\n</html>\n        '

def get_health_status(self) -> Dict[str, Any]:
    """Get health status of the War Room server"""
    return {'status': self.status, 'connected_users': len(self.connected_users), 'total_events': len(self.event_history), 'active_incidents': len(self.active_incidents), 'server_host': self.host, 'server_port': self.port}

def get_metrics(self) -> Dict[str, Any]:
    """Get performance metrics"""
    return {'websocket_connections': len(self.connected_users), 'events_processed': len(self.event_history), 'memory_usage': 'moderate', 'cpu_usage': 'low'}
