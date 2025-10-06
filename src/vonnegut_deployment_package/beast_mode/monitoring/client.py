#!/usr/bin/env python3
"""
Monitoring Client Library
=========================

Client library for communicating with the Prometheus monitoring daemon.
Provides a simple interface for applications to register metrics and send
updates without managing Prometheus infrastructure directly.

Author: Beast Mode Framework
Date: 2025-09-19
Purpose: Client interface for daemon-based monitoring system
"""

import os
import time
import json
import socket
import logging
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import urllib.request
import urllib.error

from .daemon import MetricRegistration, MetricUpdate


class MonitoringClient:
    """
    Client for communicating with Prometheus monitoring daemon.
    
    Provides a simple interface for registering metrics and sending updates.
    Handles daemon discovery, connection management, and fallback behavior.
    """
    
    def __init__(
        self,
        client_id: str,
        daemon_port: int = 8000,
        daemon_host: str = "localhost",
        socket_path: str = "/tmp/prometheus-monitor.sock",
        fallback_mode: bool = True,
        retry_attempts: int = 3,
        retry_delay: float = 1.0
    ):
        self.client_id = client_id
        self.daemon_port = daemon_port
        self.daemon_host = daemon_host
        self.socket_path = socket_path
        self.fallback_mode = fallback_mode
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        
        self.logger = self._setup_logging()
        
        # Client state
        self.registered_metrics: Dict[str, MetricRegistration] = {}
        self.daemon_available = False
        self.last_health_check = datetime.min
        self.health_check_interval = 30  # seconds
        
        # Fallback metrics storage for when daemon is unavailable
        self.fallback_metrics: Dict[str, Any] = {}
        self.pending_updates: List[MetricUpdate] = []
        
        # Thread for background tasks
        self.background_thread = None
        self.running = False
        
        # Initial daemon discovery
        self._check_daemon_availability()
        
        # Start background thread for health checks and retry logic
        self._start_background_thread()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for monitoring client."""
        logger = logging.getLogger(f"monitoring_client_{self.client_id}")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _start_background_thread(self) -> None:
        """Start background thread for health checks and retries."""
        if self.background_thread is None or not self.background_thread.is_alive():
            self.running = True
            self.background_thread = threading.Thread(
                target=self._background_loop,
                daemon=True,
                name=f"MonitoringClient-{self.client_id}"
            )
            self.background_thread.start()

    def _background_loop(self) -> None:
        """Background loop for periodic health checks and cleanup."""
        while self.running:
            try:
                # Periodic health check (less frequent since we have direct socket communication)
                now = datetime.now()
                if (now - self.last_health_check).total_seconds() > self.health_check_interval:
                    self._check_daemon_availability()
                    self.last_health_check = now
                
                # Only retry pending updates if we have fallback mode enabled
                if self.fallback_mode and self.daemon_available and self.pending_updates:
                    self._retry_pending_updates()
                
                # Cleanup old pending updates to prevent memory growth
                if self.fallback_mode and len(self.pending_updates) > 1000:
                    # Keep only recent updates
                    cutoff_time = datetime.now() - timedelta(hours=1)
                    old_count = len(self.pending_updates)
                    self.pending_updates = [
                        update for update in self.pending_updates
                        if update.timestamp > cutoff_time
                    ]
                    # If still too many, keep only the most recent
                    if len(self.pending_updates) > 500:
                        self.pending_updates = self.pending_updates[-500:]
                    
                    if len(self.pending_updates) != old_count:
                        self.logger.debug(f"Cleaned up {old_count - len(self.pending_updates)} old pending updates")
                
                time.sleep(30)  # Check every 30 seconds (less frequent)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"Error in background loop: {e}")
                time.sleep(30)

    def _check_daemon_availability(self) -> bool:
        """Check if monitoring daemon is available via socket."""
        try:
            # Try to connect to daemon's Unix socket
            client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client_socket.settimeout(2.0)
            client_socket.connect(self.socket_path)
            
            # Send health check request
            request = {"action": "health_check"}
            request_data = json.dumps(request).encode('utf-8')
            client_socket.send(request_data)
            
            # Receive response
            response_data = client_socket.recv(1024).decode('utf-8')
            response = json.loads(response_data)
            
            client_socket.close()
            
            if response.get("success") and response.get("healthy"):
                if not self.daemon_available:
                    self.logger.info("Monitoring daemon is now available")
                self.daemon_available = True
                return True
            else:
                if self.daemon_available:
                    self.logger.warning("Monitoring daemon health check failed")
                self.daemon_available = False
                return False
                
        except (socket.error, ConnectionRefusedError, FileNotFoundError):
            # Socket doesn't exist or connection refused - daemon not running
            pass
        except Exception as e:
            self.logger.debug(f"Daemon availability check failed: {e}")
        
        if self.daemon_available:
            self.logger.warning("Monitoring daemon is no longer available")
        self.daemon_available = False
        return False

    def _retry_pending_updates(self) -> None:
        """Retry pending metric updates."""
        if not self.pending_updates:
            return
        
        updates_to_retry = self.pending_updates[:10]  # Process in batches
        successful_updates = []
        
        for update in updates_to_retry:
            if self._send_metric_update(update):
                successful_updates.append(update)
        
        # Remove successful updates from pending list
        for update in successful_updates:
            if update in self.pending_updates:
                self.pending_updates.remove(update)
        
        if successful_updates:
            self.logger.info(f"Successfully retried {len(successful_updates)} pending updates")

    def is_daemon_available(self) -> bool:
        """Check if daemon is available."""
        return self.daemon_available

    def register_counter(
        self,
        name: str,
        description: str,
        labels: List[str] = None
    ) -> bool:
        """Register a counter metric."""
        return self._register_metric("counter", name, description, labels)

    def register_gauge(
        self,
        name: str,
        description: str,
        labels: List[str] = None
    ) -> bool:
        """Register a gauge metric."""
        return self._register_metric("gauge", name, description, labels)

    def register_histogram(
        self,
        name: str,
        description: str,
        labels: List[str] = None,
        buckets: List[float] = None
    ) -> bool:
        """Register a histogram metric."""
        return self._register_metric("histogram", name, description, labels, buckets)

    def _register_metric(
        self,
        metric_type: str,
        name: str,
        description: str,
        labels: List[str] = None,
        buckets: List[float] = None
    ) -> bool:
        """Register a metric with the daemon."""
        if labels is None:
            labels = []
        
        registration = MetricRegistration(
            client_id=self.client_id,
            metric_name=name,
            metric_type=metric_type,
            description=description,
            labels=labels,
            buckets=buckets
        )
        
        # Store registration locally
        self.registered_metrics[name] = registration
        
        # Try to register with daemon
        if self.daemon_available:
            success = self._send_metric_registration(registration)
            if success:
                self.logger.debug(f"Registered {metric_type} metric: {name}")
                return True
        
        # Fallback: store locally for later retry
        if self.fallback_mode:
            self.logger.debug(f"Stored {metric_type} metric for later registration: {name}")
            return True
        
        self.logger.warning(f"Failed to register {metric_type} metric: {name}")
        return False

    def increment_counter(
        self,
        name: str,
        labels: Dict[str, str] = None,
        value: float = 1.0
    ) -> bool:
        """Increment a counter metric."""
        return self._update_metric(name, "increment", value, labels)

    def set_gauge(
        self,
        name: str,
        value: float,
        labels: Dict[str, str] = None
    ) -> bool:
        """Set a gauge metric value."""
        return self._update_metric(name, "set", value, labels)

    def observe_histogram(
        self,
        name: str,
        value: float,
        labels: Dict[str, str] = None
    ) -> bool:
        """Observe a value in a histogram metric."""
        return self._update_metric(name, "observe", value, labels)

    def _update_metric(
        self,
        name: str,
        operation: str,
        value: float,
        labels: Dict[str, str] = None
    ) -> bool:
        """Update a metric value."""
        if labels is None:
            labels = {}
        
        # Check if metric is registered
        if name not in self.registered_metrics:
            self.logger.warning(f"Metric not registered: {name}")
            return False
        
        update = MetricUpdate(
            client_id=self.client_id,
            metric_name=name,
            operation=operation,
            value=value,
            labels=labels
        )
        
        # Try direct socket communication first
        success = self._send_metric_update(update)
        if success:
            # Update daemon availability status
            if not self.daemon_available:
                self.daemon_available = True
                self.logger.debug("Daemon became available during metric update")
            return True
        
        # If direct communication failed, update availability status
        if self.daemon_available:
            self.daemon_available = False
            self.logger.debug("Daemon became unavailable during metric update")
        
        # Fallback: store update for later retry (only if fallback mode enabled)
        if self.fallback_mode:
            self.pending_updates.append(update)
            return True
        
        return False

    def _send_metric_registration(self, registration: MetricRegistration) -> bool:
        """Send metric registration to daemon via socket."""
        return self._send_daemon_request("register_metric", asdict(registration))

    def _send_metric_update(self, update: MetricUpdate) -> bool:
        """Send metric update to daemon via socket."""
        # Convert datetime to ISO string for JSON serialization
        update_dict = asdict(update)
        update_dict['timestamp'] = update.timestamp.isoformat()
        return self._send_daemon_request("update_metric", update_dict)

    def _send_daemon_request(self, action: str, data: Dict[str, Any]) -> bool:
        """Send request to daemon via Unix socket."""
        try:
            client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client_socket.settimeout(5.0)
            client_socket.connect(self.socket_path)
            
            # Send request
            request = {"action": action, "data": data}
            request_data = json.dumps(request).encode('utf-8')
            client_socket.send(request_data)
            
            # Receive response
            response_data = client_socket.recv(4096).decode('utf-8')
            response = json.loads(response_data)
            
            client_socket.close()
            
            return response.get("success", False)
            
        except (socket.error, ConnectionRefusedError, FileNotFoundError):
            # Daemon not available
            return False
        except Exception as e:
            self.logger.error(f"Failed to send daemon request: {e}")
            return False

    def get_registered_metrics(self) -> Dict[str, MetricRegistration]:
        """Get all registered metrics."""
        return self.registered_metrics.copy()

    def get_pending_updates_count(self) -> int:
        """Get number of pending updates."""
        return len(self.pending_updates)

    def flush_pending_updates(self) -> int:
        """Flush all pending updates to daemon if available."""
        if not self.daemon_available or not self.pending_updates:
            return 0
        
        successful_count = 0
        updates_to_flush = self.pending_updates.copy()
        
        for update in updates_to_flush:
            if self._send_metric_update(update):
                successful_count += 1
                self.pending_updates.remove(update)
        
        if successful_count > 0:
            self.logger.info(f"Flushed {successful_count} pending updates")
        
        return successful_count

    def shutdown(self) -> None:
        """Shutdown the monitoring client."""
        self.running = False
        
        # Try to flush any pending updates
        if self.daemon_available:
            self.flush_pending_updates()
        
        # Wait for background thread to finish
        if self.background_thread and self.background_thread.is_alive():
            self.background_thread.join(timeout=5)
        
        self.logger.info(f"Monitoring client {self.client_id} shutdown")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()


# Convenience functions for backward compatibility
def create_monitoring_client(client_id: str, **kwargs) -> MonitoringClient:
    """Create a monitoring client instance."""
    return MonitoringClient(client_id=client_id, **kwargs)


def get_default_client() -> MonitoringClient:
    """Get a default monitoring client instance."""
    # Singleton pattern for default client
    if not hasattr(get_default_client, '_instance'):
        get_default_client._instance = MonitoringClient(
            client_id="default",
            fallback_mode=True
        )
    return get_default_client._instance