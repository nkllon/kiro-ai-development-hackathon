#!/usr/bin/env python3
"""
Prometheus Monitor Daemon
========================

A standalone daemon process that provides centralized Prometheus monitoring
services to Beast Mode components. Implements proper daemon lifecycle with
PID file management, service discovery, and metric aggregation.

Author: Beast Mode Framework
Date: 2025-09-19
Purpose: Centralized monitoring daemon to eliminate monitoring chaos
"""

import os
import sys
import time
import signal
import socket
import logging
import threading
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import atexit

# Prometheus client library
try:
    from prometheus_client import (
        Counter,
        Gauge,
        Histogram,
        Summary,
        Info,
        CollectorRegistry,
        start_http_server,
        generate_latest,
        CONTENT_TYPE_LATEST,
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


@dataclass
class MetricRegistration:
    """Metric registration data model."""
    client_id: str
    metric_name: str
    metric_type: str  # counter, gauge, histogram
    description: str
    labels: List[str]
    buckets: Optional[List[float]] = None  # for histograms
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class MetricUpdate:
    """Metric update data model."""
    client_id: str
    metric_name: str
    operation: str  # increment, set, observe
    value: float
    labels: Dict[str, str]
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class ServiceStatus:
    """Service status data model."""
    is_running: bool
    pid: Optional[int]
    port: int
    uptime: timedelta
    metrics_endpoint: str
    registered_clients: List[str]
    total_metrics: int
    last_activity: datetime


class DaemonManager:
    """Manages daemon process lifecycle with PID file handling."""
    
    def __init__(self, pid_file: str = "/tmp/prometheus-monitor.pid"):
        self.pid_file = Path(pid_file)
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for daemon manager."""
        logger = logging.getLogger("daemon_manager")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def write_pid_file(self, pid: int = None) -> None:
        """Write PID to file."""
        if pid is None:
            pid = os.getpid()
        
        try:
            self.pid_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.pid_file, 'w') as f:
                f.write(str(pid))
            self.logger.info(f"PID {pid} written to {self.pid_file}")
        except Exception as e:
            self.logger.error(f"Failed to write PID file: {e}")
            raise

    def read_pid_file(self) -> Optional[int]:
        """Read PID from file."""
        try:
            if not self.pid_file.exists():
                return None
            
            with open(self.pid_file, 'r') as f:
                pid_str = f.read().strip()
                return int(pid_str) if pid_str else None
        except (ValueError, FileNotFoundError):
            return None
        except Exception as e:
            self.logger.error(f"Failed to read PID file: {e}")
            return None

    def is_daemon_running(self) -> bool:
        """Check if daemon is running."""
        pid = self.read_pid_file()
        if pid is None:
            return False
        
        try:
            # Send signal 0 to check if process exists
            os.kill(pid, 0)
            return True
        except OSError:
            # Process doesn't exist, clean up stale PID file
            self.cleanup_stale_pid()
            return False

    def cleanup_stale_pid(self) -> None:
        """Clean up stale PID file."""
        try:
            if self.pid_file.exists():
                self.pid_file.unlink()
                self.logger.info(f"Cleaned up stale PID file: {self.pid_file}")
        except Exception as e:
            self.logger.error(f"Failed to cleanup stale PID file: {e}")

    def kill_daemon(self, signal_num: int = signal.SIGTERM) -> bool:
        """Kill daemon process."""
        pid = self.read_pid_file()
        if pid is None:
            self.logger.warning("No PID file found")
            return False
        
        try:
            os.kill(pid, signal_num)
            self.logger.info(f"Sent signal {signal_num} to daemon PID {pid}")
            
            # Wait for process to terminate
            for _ in range(30):  # Wait up to 30 seconds
                if not self.is_daemon_running():
                    self.cleanup_stale_pid()
                    return True
                time.sleep(1)
            
            # Force kill if still running
            if self.is_daemon_running():
                self.logger.warning("Daemon didn't terminate gracefully, force killing")
                os.kill(pid, signal.SIGKILL)
                time.sleep(2)
                self.cleanup_stale_pid()
            
            return True
        except OSError as e:
            self.logger.error(f"Failed to kill daemon: {e}")
            return False


class PrometheusMonitorDaemon:
    """
    Standalone Prometheus monitoring daemon.
    
    Provides centralized metrics collection and HTTP endpoint for all
    Beast Mode components. Implements proper daemon lifecycle with
    PID management and service discovery.
    """
    
    def __init__(
        self,
        port: int = 8000,
        pid_file: str = "/tmp/prometheus-monitor.pid",
        socket_path: str = "/tmp/prometheus-monitor.sock",
        log_file: str = "/tmp/prometheus-monitor.log"
    ):
        self.port = port
        self.pid_file = pid_file
        self.socket_path = socket_path
        self.log_file = log_file
        
        self.daemon_manager = DaemonManager(pid_file)
        self.logger = self._setup_logging()
        
        # Service state
        self.start_time = datetime.now()
        self.running = False
        self.shutdown_requested = False
        
        # Metrics infrastructure
        self.registry = CollectorRegistry() if PROMETHEUS_AVAILABLE else None
        self.registered_metrics: Dict[str, Any] = {}
        self.registered_clients: Set[str] = set()
        self.metric_updates_queue: List[MetricUpdate] = []
        
        # HTTP server
        self.http_server = None
        self.http_thread = None
        
        # Service threads
        self.service_thread = None
        self.cleanup_thread = None
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        atexit.register(self._cleanup)

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for daemon."""
        logger = logging.getLogger("prometheus_daemon")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            # Console handler for foreground mode
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
            
            # File handler for daemon mode
            try:
                file_handler = logging.FileHandler(self.log_file)
                file_formatter = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                logger.warning(f"Could not setup file logging: {e}")

        return logger

    def _signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, initiating shutdown")
        self.shutdown_requested = True
        self.stop_daemon()

    def _cleanup(self) -> None:
        """Cleanup resources on exit."""
        if self.running:
            self.stop_daemon()

    def start_daemon(self, daemonize: bool = True) -> bool:
        """Start the monitoring daemon."""
        # Check if already running
        if self.daemon_manager.is_daemon_running():
            existing_pid = self.daemon_manager.read_pid_file()
            self.logger.error(f"Daemon already running with PID {existing_pid}")
            return False

        if not PROMETHEUS_AVAILABLE:
            self.logger.error("Prometheus client not available. Install with: pip install prometheus-client")
            return False

        try:
            if daemonize:
                self._daemonize()
            
            # Write PID file
            self.daemon_manager.write_pid_file()
            
            # Start HTTP server
            self._start_http_server()
            
            # Start service threads
            self._start_service_threads()
            
            self.running = True
            self.logger.info(f"Prometheus monitoring daemon started on port {self.port}")
            self.logger.info(f"Metrics endpoint: http://localhost:{self.port}/metrics")
            
            # Main daemon loop
            self._daemon_loop()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start daemon: {e}")
            self._cleanup()
            return False

    def _daemonize(self) -> None:
        """Daemonize the process."""
        try:
            # First fork
            pid = os.fork()
            if pid > 0:
                sys.exit(0)  # Exit parent
        except OSError as e:
            self.logger.error(f"First fork failed: {e}")
            sys.exit(1)

        # Decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        try:
            # Second fork
            pid = os.fork()
            if pid > 0:
                sys.exit(0)  # Exit second parent
        except OSError as e:
            self.logger.error(f"Second fork failed: {e}")
            sys.exit(1)

        # Redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        
        with open('/dev/null', 'r') as si:
            os.dup2(si.fileno(), sys.stdin.fileno())
        with open('/dev/null', 'w') as so:
            os.dup2(so.fileno(), sys.stdout.fileno())
        with open('/dev/null', 'w') as se:
            os.dup2(se.fileno(), sys.stderr.fileno())

    def _start_http_server(self) -> None:
        """Start Prometheus HTTP server."""
        if not PROMETHEUS_AVAILABLE:
            return

        try:
            # Try the configured port first
            port = self.port
            for attempt in range(10):  # Try ports 8000-8009
                try:
                    start_http_server(port, registry=self.registry)
                    self.port = port  # Update actual port used
                    self.logger.info(f"HTTP server started on port {port}")
                    return
                except OSError as e:
                    if "Address already in use" in str(e):
                        port += 1
                        continue
                    raise
            
            raise RuntimeError("Could not find available port for HTTP server")
            
        except Exception as e:
            self.logger.error(f"Failed to start HTTP server: {e}")
            raise

    def _start_service_threads(self) -> None:
        """Start service threads."""
        # Service thread for handling client requests
        self.service_thread = threading.Thread(
            target=self._service_loop,
            daemon=True,
            name="ServiceThread"
        )
        self.service_thread.start()
        
        # Cleanup thread for maintenance tasks
        self.cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True,
            name="CleanupThread"
        )
        self.cleanup_thread.start()

    def _daemon_loop(self) -> None:
        """Main daemon loop."""
        while self.running and not self.shutdown_requested:
            try:
                time.sleep(1)
                
                # Process any pending metric updates
                self._process_metric_updates()
                
            except KeyboardInterrupt:
                self.logger.info("Received keyboard interrupt, shutting down")
                break
            except Exception as e:
                self.logger.error(f"Error in daemon loop: {e}")
                # Prevent tight error loops
                time.sleep(1)

    def _service_loop(self) -> None:
        """Service loop for handling client requests via Unix domain socket."""
        try:
            # Remove existing socket file if it exists
            if os.path.exists(self.socket_path):
                os.unlink(self.socket_path)
            
            # Create Unix domain socket
            server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            server_socket.bind(self.socket_path)
            server_socket.listen(5)
            server_socket.settimeout(1.0)  # Non-blocking with timeout
            
            self.logger.info(f"Service socket listening on {self.socket_path}")
            
            while self.running and not self.shutdown_requested:
                try:
                    client_socket, _ = server_socket.accept()
                    # Handle client request in separate thread to avoid blocking
                    client_thread = threading.Thread(
                        target=self._handle_client_request,
                        args=(client_socket,),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.timeout:
                    # Timeout is expected, continue loop
                    continue
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.logger.error(f"Error accepting client connection: {e}")
                    time.sleep(1)
        
        except Exception as e:
            self.logger.error(f"Error in service loop: {e}")
        finally:
            try:
                server_socket.close()
                if os.path.exists(self.socket_path):
                    os.unlink(self.socket_path)
            except:
                pass

    def _handle_client_request(self, client_socket: socket.socket) -> None:
        """Handle individual client request."""
        try:
            # Receive request data
            data = client_socket.recv(4096).decode('utf-8')
            if not data:
                return
            
            request = json.loads(data)
            response = self._process_client_request(request)
            
            # Send response
            response_data = json.dumps(response).encode('utf-8')
            client_socket.send(response_data)
            
        except Exception as e:
            self.logger.error(f"Error handling client request: {e}")
            error_response = {"success": False, "error": str(e)}
            try:
                client_socket.send(json.dumps(error_response).encode('utf-8'))
            except:
                pass
        finally:
            try:
                client_socket.close()
            except:
                pass

    def _process_client_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process client request and return response."""
        try:
            action = request.get("action")
            
            if action == "register_metric":
                registration = MetricRegistration(**request["data"])
                success = self.register_metric(registration)
                return {"success": success}
            
            elif action == "update_metric":
                update = MetricUpdate(**request["data"])
                success = self.update_metric(update)
                return {"success": success}
            
            elif action == "health_check":
                return {"success": True, "healthy": self.health_check()}
            
            elif action == "get_status":
                status = self.get_status()
                return {"success": True, "status": asdict(status)}
            
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _cleanup_loop(self) -> None:
        """Cleanup loop for maintenance tasks."""
        while self.running and not self.shutdown_requested:
            try:
                # Clean up old metric updates
                cutoff_time = datetime.now() - timedelta(hours=1)
                old_count = len(self.metric_updates_queue)
                self.metric_updates_queue = [
                    update for update in self.metric_updates_queue
                    if update.timestamp > cutoff_time
                ]
                new_count = len(self.metric_updates_queue)
                
                if old_count != new_count:
                    self.logger.debug(f"Cleaned up {old_count - new_count} old metric updates")
                
                # Prevent memory exhaustion by limiting queue size
                if len(self.metric_updates_queue) > 10000:
                    self.metric_updates_queue = self.metric_updates_queue[-5000:]
                    self.logger.warning("Metric updates queue was too large, truncated to 5000 items")
                
                time.sleep(300)  # Run every 5 minutes
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
                # Prevent tight error loops
                time.sleep(60)

    def _process_metric_updates(self) -> None:
        """Process pending metric updates."""
        if not self.metric_updates_queue:
            return
        
        # Process updates in batches
        updates_to_process = self.metric_updates_queue[:100]
        self.metric_updates_queue = self.metric_updates_queue[100:]
        
        for update in updates_to_process:
            try:
                self._apply_metric_update(update)
            except Exception as e:
                self.logger.error(f"Failed to apply metric update: {e}")

    def _apply_metric_update(self, update: MetricUpdate) -> None:
        """Apply a metric update to the registry."""
        metric_key = f"{update.client_id}:{update.metric_name}"
        metric = self.registered_metrics.get(metric_key)
        
        if not metric:
            self.logger.warning(f"Metric not found: {metric_key}")
            return
        
        try:
            if update.operation == "increment":
                metric.labels(**update.labels).inc(update.value)
            elif update.operation == "set":
                metric.labels(**update.labels).set(update.value)
            elif update.operation == "observe":
                metric.labels(**update.labels).observe(update.value)
            else:
                self.logger.warning(f"Unknown metric operation: {update.operation}")
        except Exception as e:
            self.logger.error(f"Failed to update metric {metric_key}: {e}")

    def stop_daemon(self) -> bool:
        """Stop the monitoring daemon."""
        self.logger.info("Stopping daemon...")
        self.running = False
        
        try:
            # Stop service threads
            if self.service_thread and self.service_thread.is_alive():
                self.service_thread.join(timeout=5)
            
            if self.cleanup_thread and self.cleanup_thread.is_alive():
                self.cleanup_thread.join(timeout=5)
            
            # Cleanup PID file
            self.daemon_manager.cleanup_stale_pid()
            
            self.logger.info("Daemon stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping daemon: {e}")
            return False

    def register_metric(self, registration: MetricRegistration) -> bool:
        """Register a new metric."""
        if not PROMETHEUS_AVAILABLE:
            return False
        
        metric_key = f"{registration.client_id}:{registration.metric_name}"
        
        if metric_key in self.registered_metrics:
            self.logger.warning(f"Metric already registered: {metric_key}")
            return True
        
        try:
            if registration.metric_type == "counter":
                metric = Counter(
                    registration.metric_name,
                    registration.description,
                    registration.labels,
                    registry=self.registry
                )
            elif registration.metric_type == "gauge":
                metric = Gauge(
                    registration.metric_name,
                    registration.description,
                    registration.labels,
                    registry=self.registry
                )
            elif registration.metric_type == "histogram":
                metric = Histogram(
                    registration.metric_name,
                    registration.description,
                    registration.labels,
                    buckets=registration.buckets,
                    registry=self.registry
                )
            else:
                self.logger.error(f"Unknown metric type: {registration.metric_type}")
                return False
            
            self.registered_metrics[metric_key] = metric
            self.registered_clients.add(registration.client_id)
            
            self.logger.info(f"Registered metric: {metric_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register metric {metric_key}: {e}")
            return False

    def update_metric(self, update: MetricUpdate) -> bool:
        """Queue a metric update."""
        self.metric_updates_queue.append(update)
        return True

    def get_status(self) -> ServiceStatus:
        """Get daemon status."""
        uptime = datetime.now() - self.start_time
        return ServiceStatus(
            is_running=self.running,
            pid=os.getpid() if self.running else None,
            port=self.port,
            uptime=uptime,
            metrics_endpoint=f"http://localhost:{self.port}/metrics",
            registered_clients=list(self.registered_clients),
            total_metrics=len(self.registered_metrics),
            last_activity=datetime.now()
        )

    def health_check(self) -> bool:
        """Perform health check."""
        try:
            # Check if HTTP server is responding
            import urllib.request
            urllib.request.urlopen(f"http://localhost:{self.port}/metrics", timeout=5)
            return True
        except Exception:
            return False


def main():
    """Main entry point for daemon."""
    parser = argparse.ArgumentParser(description="Prometheus Monitor Daemon")
    parser.add_argument("--start", action="store_true", help="Start daemon")
    parser.add_argument("--stop", action="store_true", help="Stop daemon")
    parser.add_argument("--restart", action="store_true", help="Restart daemon")
    parser.add_argument("--status", action="store_true", help="Show daemon status")
    parser.add_argument("--health-check", action="store_true", help="Perform health check")
    parser.add_argument("--foreground", action="store_true", help="Run in foreground (don't daemonize)")
    parser.add_argument("--port", type=int, default=8000, help="HTTP server port")
    parser.add_argument("--pid-file", default="/tmp/prometheus-monitor.pid", help="PID file path")
    
    args = parser.parse_args()
    
    daemon = PrometheusMonitorDaemon(
        port=args.port,
        pid_file=args.pid_file
    )
    
    if args.start:
        success = daemon.start_daemon(daemonize=not args.foreground)
        sys.exit(0 if success else 1)
    
    elif args.stop:
        success = daemon.daemon_manager.kill_daemon()
        sys.exit(0 if success else 1)
    
    elif args.restart:
        daemon.daemon_manager.kill_daemon()
        time.sleep(2)
        success = daemon.start_daemon(daemonize=not args.foreground)
        sys.exit(0 if success else 1)
    
    elif args.status:
        if daemon.daemon_manager.is_daemon_running():
            pid = daemon.daemon_manager.read_pid_file()
            print(f"Daemon is running with PID {pid}")
            sys.exit(0)
        else:
            print("Daemon is not running")
            sys.exit(1)
    
    elif args.health_check:
        if daemon.daemon_manager.is_daemon_running():
            healthy = daemon.health_check()
            print("Daemon is healthy" if healthy else "Daemon is unhealthy")
            sys.exit(0 if healthy else 1)
        else:
            print("Daemon is not running")
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()