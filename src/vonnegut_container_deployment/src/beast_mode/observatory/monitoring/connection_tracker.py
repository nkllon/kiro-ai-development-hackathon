"""
Connection Tracker

Real-time connection status tracking for WebSocket connections with minimal overhead.
Tracks connection state, duration, and basic metrics for health monitoring.
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Set
import json
from datetime import datetime, timedelta


@dataclass
class ConnectionInfo:
    """Information about a WebSocket connection"""
    endpoint: str
    websocket: Any
    connected_at: datetime
    last_activity: datetime
    message_count: int = 0
    error_count: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConnectionTracker:
    """
    Tracks WebSocket connections in real-time with minimal overhead.
    
    Provides connection state monitoring, duration tracking, and basic
    metrics collection for health monitoring purposes.
    """

    def __init__(self):
        """Initialize the connection tracker"""
        self._connections: Dict[str, ConnectionInfo] = {}
        self._connection_metrics: Dict[str, Dict[str, Any]] = {}
        self._tracking_tasks: Dict[str, asyncio.Task] = {}
        
        # Performance tracking
        self._start_time = time.time()
        self._total_connections = 0
        self._total_disconnections = 0

    async def track_connection(self, endpoint: str, websocket: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Start tracking a WebSocket connection.
        
        Args:
            endpoint: Unique identifier for the connection
            websocket: WebSocket connection object
            metadata: Optional metadata about the connection
        """
        current_time = datetime.now()
        
        # Create connection info
        connection_info = ConnectionInfo(
            endpoint=endpoint,
            websocket=websocket,
            connected_at=current_time,
            last_activity=current_time,
            metadata=metadata or {}
        )
        
        self._connections[endpoint] = connection_info
        self._total_connections += 1
        
        # Initialize metrics
        self._connection_metrics[endpoint] = {
            'connection_duration_sec': 0.0,
            'messages_per_minute': 0.0,
            'error_rate': 0.0,
            'bytes_per_second': 0.0,
            'last_activity_sec_ago': 0.0
        }
        
        # Start background tracking task
        self._tracking_tasks[endpoint] = asyncio.create_task(
            self._track_connection_background(endpoint)
        )
        
        self._log_action("connection_tracked", {
            "endpoint": endpoint,
            "total_connections": len(self._connections),
            "metadata": metadata
        })

    async def stop_tracking(self, endpoint: str) -> None:
        """
        Stop tracking a WebSocket connection.
        
        Args:
            endpoint: The endpoint to stop tracking
        """
        if endpoint in self._connections:
            # Cancel background task
            if endpoint in self._tracking_tasks:
                self._tracking_tasks[endpoint].cancel()
                try:
                    await self._tracking_tasks[endpoint]
                except asyncio.CancelledError:
                    pass
                del self._tracking_tasks[endpoint]
            
            # Remove connection
            del self._connections[endpoint]
            del self._connection_metrics[endpoint]
            self._total_disconnections += 1
            
            self._log_action("connection_stopped", {
                "endpoint": endpoint,
                "remaining_connections": len(self._connections)
            })

    async def record_message_sent(self, endpoint: str, message_size: int = 0) -> None:
        """Record a message sent event"""
        if endpoint in self._connections:
            conn = self._connections[endpoint]
            conn.message_count += 1
            conn.bytes_sent += message_size
            conn.last_activity = datetime.now()
            
            self._log_action("message_sent_tracked", {
                "endpoint": endpoint,
                "message_count": conn.message_count,
                "bytes_sent": conn.bytes_sent
            })

    async def record_message_received(self, endpoint: str, message_size: int = 0) -> None:
        """Record a message received event"""
        if endpoint in self._connections:
            conn = self._connections[endpoint]
            conn.message_count += 1
            conn.bytes_received += message_size
            conn.last_activity = datetime.now()
            
            self._log_action("message_received_tracked", {
                "endpoint": endpoint,
                "message_count": conn.message_count,
                "bytes_received": conn.bytes_received
            })

    async def record_error(self, endpoint: str, error_type: str = "unknown") -> None:
        """Record an error event"""
        if endpoint in self._connections:
            conn = self._connections[endpoint]
            conn.error_count += 1
            
            self._log_action("error_recorded", {
                "endpoint": endpoint,
                "error_count": conn.error_count,
                "error_type": error_type
            })

    def get_connection_info(self, endpoint: str) -> Optional[ConnectionInfo]:
        """Get connection information for an endpoint"""
        return self._connections.get(endpoint)

    def get_all_connections(self) -> Dict[str, ConnectionInfo]:
        """Get all tracked connections"""
        return self._connections.copy()

    async def get_connection_metrics(self, endpoint: str) -> Dict[str, Any]:
        """
        Get comprehensive metrics for a connection.
        
        Args:
            endpoint: The endpoint to get metrics for
            
        Returns:
            Dictionary containing connection metrics
        """
        if endpoint not in self._connections:
            return {}
        
        conn = self._connections[endpoint]
        current_time = datetime.now()
        
        # Calculate duration
        duration = (current_time - conn.connected_at).total_seconds()
        
        # Calculate messages per minute
        messages_per_minute = 0.0
        if duration > 0:
            messages_per_minute = (conn.message_count / duration) * 60
        
        # Calculate error rate
        error_rate = 0.0
        if conn.message_count > 0:
            error_rate = conn.error_count / conn.message_count
        
        # Calculate bytes per second
        bytes_per_second = 0.0
        if duration > 0:
            total_bytes = conn.bytes_sent + conn.bytes_received
            bytes_per_second = total_bytes / duration
        
        # Calculate time since last activity
        last_activity_sec_ago = (current_time - conn.last_activity).total_seconds()
        
        metrics = {
            'connection_duration_sec': duration,
            'messages_per_minute': messages_per_minute,
            'error_rate': error_rate,
            'bytes_per_second': bytes_per_second,
            'last_activity_sec_ago': last_activity_sec_ago,
            'message_count': conn.message_count,
            'error_count': conn.error_count,
            'bytes_sent': conn.bytes_sent,
            'bytes_received': conn.bytes_received,
            'is_active': conn.is_active,
            'connected_at': conn.connected_at.isoformat(),
            'last_activity': conn.last_activity.isoformat()
        }
        
        # Update cached metrics
        self._connection_metrics[endpoint] = metrics
        
        return metrics

    def get_overall_stats(self) -> Dict[str, Any]:
        """Get overall statistics for all connections"""
        current_time = datetime.now()
        total_duration = time.time() - self._start_time
        
        active_connections = len(self._connections)
        total_messages = sum(conn.message_count for conn in self._connections.values())
        total_errors = sum(conn.error_count for conn in self._connections.values())
        total_bytes = sum(conn.bytes_sent + conn.bytes_received for conn in self._connections.values())
        
        return {
            'active_connections': active_connections,
            'total_connections': self._total_connections,
            'total_disconnections': self._total_disconnections,
            'total_messages': total_messages,
            'total_errors': total_errors,
            'total_bytes': total_bytes,
            'uptime_sec': total_duration,
            'avg_messages_per_connection': total_messages / max(active_connections, 1),
            'avg_bytes_per_connection': total_bytes / max(active_connections, 1),
            'overall_error_rate': total_errors / max(total_messages, 1)
        }

    def is_connection_active(self, endpoint: str) -> bool:
        """Check if a connection is currently active"""
        if endpoint not in self._connections:
            return False
        
        conn = self._connections[endpoint]
        current_time = datetime.now()
        
        # Consider connection inactive if no activity for 5 minutes
        inactive_threshold = timedelta(minutes=5)
        return (current_time - conn.last_activity) < inactive_threshold

    async def _track_connection_background(self, endpoint: str) -> None:
        """Background task to continuously track connection metrics"""
        try:
            while endpoint in self._connections:
                # Update connection activity status
                if endpoint in self._connections:
                    conn = self._connections[endpoint]
                    current_time = datetime.now()
                    
                    # Check if connection is still active
                    inactive_threshold = timedelta(minutes=5)
                    conn.is_active = (current_time - conn.last_activity) < inactive_threshold
                    
                    # Update metrics periodically
                    await self.get_connection_metrics(endpoint)
                
                # Sleep for 10 seconds between updates
                await asyncio.sleep(10.0)
                
        except asyncio.CancelledError:
            # Task was cancelled, which is expected when stopping tracking
            pass
        except Exception as e:
            self._log_action("tracking_error", {
                "endpoint": endpoint,
                "error": str(e),
                "status": "error"
            })

    def _log_action(self, action: str, details: Dict[str, Any]) -> None:
        """Log action in JSON format to stdout"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "task": "3.1",
            "action": f"connection_tracker_{action}",
            "status": "in_progress",
            "details": details
        }
        
        print(json.dumps(log_entry))