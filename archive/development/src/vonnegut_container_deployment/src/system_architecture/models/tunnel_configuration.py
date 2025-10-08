"""
Tunnel Configuration Models

Data models for Cloudflare tunnel configuration and connectivity testing.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional

# Import models from the discoverer module to maintain consistency
from src.system_architecture.discovery.cloudflare_tunnel_discoverer import (
    TunnelIngressRule,
    DNSRouting,
    TunnelConfiguration,
    WebSocketConnectivityTest
)


@dataclass
class TunnelPerformanceMetrics:
    """Tunnel performance metrics"""
    tunnel_id: str
    timestamp: datetime
    connectivity_tests: Dict[str, Dict[str, Any]]
    performance_summary: Dict[str, Any]
    websocket_tests: List[WebSocketConnectivityTest]
    error_count: int = 0
    warning_count: int = 0


@dataclass
class TunnelCredentialInfo:
    """Tunnel credential information"""
    tunnel_id: str
    credentials_file_path: str
    last_rotated: Optional[datetime] = None
    rotation_schedule: Optional[str] = None
    is_valid: bool = True
    error_message: Optional[str] = None