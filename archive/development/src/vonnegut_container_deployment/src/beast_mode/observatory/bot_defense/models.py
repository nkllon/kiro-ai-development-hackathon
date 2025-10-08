"""
Bot Defense Data Models
Database models for attacks, bot profiles, defense actions, and achievements.
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json

class AttackType(Enum):
    """Types of detected attacks."""
    SUSPICIOUS_ENDPOINT = "suspicious_endpoint"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_USER_AGENT = "suspicious_user_agent"
    REPEATED_404 = "repeated_404"
    VULNERABILITY_SCAN = "vulnerability_scan"
    BRUTE_FORCE = "brute_force"
    UNKNOWN = "unknown"

class DefenseActionType(Enum):
    """Types of defense actions."""
    EMOJI_NUKE = "emoji_nuke"
    BANDWIDTH_WASTE = "bandwidth_waste"
    PUNISHMENT_ESCALATION = "punishment_escalation"
    IP_BLOCK = "ip_block"
    WARNING_LOGGED = "warning_logged"

class BotStatus(Enum):
    """Bot status in the system."""
    ACTIVE = "active"           # Currently attacking
    BLOCKED = "blocked"         # Temporarily blocked
    TERMINATED = "terminated"   # Permanently blocked
    ARCHIVED = "archived"       # Old, inactive bot

@dataclass
class Attack:
    """Individual attack record."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_ip: str = ""
    country: Optional[str] = None
    coordinates: Optional[tuple[float, float]] = None
    endpoint: str = ""
    user_agent: str = ""
    method: str = "GET"
    timestamp: datetime = field(default_factory=datetime.now)
    attack_type: AttackType = AttackType.UNKNOWN
    confidence_score: float = 0.0
    punishment_level: int = 0
    bandwidth_wasted: int = 0  # bytes
    status: str = "active"
    
    # Additional metadata
    headers: Dict[str, str] = field(default_factory=dict)
    query_params: Dict[str, str] = field(default_factory=dict)
    response_code: int = 200
    response_size: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'source_ip': self.source_ip,
            'country': self.country,
            'coordinates': self.coordinates,
            'endpoint': self.endpoint,
            'user_agent': self.user_agent,
            'method': self.method,
            'timestamp': self.timestamp.isoformat(),
            'attack_type': self.attack_type.value,
            'confidence_score': self.confidence_score,
            'punishment_level': self.punishment_level,
            'bandwidth_wasted': self.bandwidth_wasted,
            'status': self.status,
            'headers': self.headers,
            'query_params': self.query_params,
            'response_code': self.response_code,
            'response_size': self.response_size
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Attack':
        """Create from dictionary."""
        attack = cls()
        attack.id = data.get('id', attack.id)
        attack.source_ip = data.get('source_ip', '')
        attack.country = data.get('country')
        attack.coordinates = data.get('coordinates')
        attack.endpoint = data.get('endpoint', '')
        attack.user_agent = data.get('user_agent', '')
        attack.method = data.get('method', 'GET')
        
        if 'timestamp' in data:
            if isinstance(data['timestamp'], str):
                attack.timestamp = datetime.fromisoformat(data['timestamp'])
            else:
                attack.timestamp = data['timestamp']
        
        if 'attack_type' in data:
            attack.attack_type = AttackType(data['attack_type'])
        
        attack.confidence_score = data.get('confidence_score', 0.0)
        attack.punishment_level = data.get('punishment_level', 0)
        attack.bandwidth_wasted = data.get('bandwidth_wasted', 0)
        attack.status = data.get('status', 'active')
        attack.headers = data.get('headers', {})
        attack.query_params = data.get('query_params', {})
        attack.response_code = data.get('response_code', 200)
        attack.response_size = data.get('response_size', 0)
        
        return attack

@dataclass
class Achievement:
    """Bot achievement/badge."""
    
    id: str
    name: str
    description: str
    icon: str
    threshold: int
    unlocked_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'threshold': self.threshold,
            'unlocked_at': self.unlocked_at.isoformat()
        }

@dataclass
class BotProfile:
    """Bot profile with behavior tracking."""
    
    ip: str
    country: Optional[str] = None
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    attack_count: int = 0
    max_punishment_level: int = 0
    total_bandwidth_wasted: int = 0  # bytes
    status: BotStatus = BotStatus.ACTIVE
    achievements: List[Achievement] = field(default_factory=list)
    
    # Behavior analysis
    most_targeted_endpoints: List[str] = field(default_factory=list)
    user_agents: List[str] = field(default_factory=list)
    attack_patterns: Dict[str, Any] = field(default_factory=dict)
    
    # Blocking information
    blocked_at: Optional[datetime] = None
    block_reason: Optional[str] = None
    block_duration: Optional[timedelta] = None
    
    def add_achievement(self, achievement: Achievement) -> None:
        """Add achievement if not already earned."""
        if not any(a.id == achievement.id for a in self.achievements):
            self.achievements.append(achievement)
    
    def get_achievement_score(self) -> int:
        """Calculate total achievement score."""
        return sum(a.threshold for a in self.achievements)
    
    def is_blocked(self) -> bool:
        """Check if bot is currently blocked."""
        if self.status != BotStatus.BLOCKED or not self.blocked_at:
            return False
        
        if self.block_duration is None:
            return True  # Permanent block
        
        return datetime.now() < self.blocked_at + self.block_duration
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'ip': self.ip,
            'country': self.country,
            'first_seen': self.first_seen.isoformat(),
            'last_seen': self.last_seen.isoformat(),
            'attack_count': self.attack_count,
            'max_punishment_level': self.max_punishment_level,
            'total_bandwidth_wasted': self.total_bandwidth_wasted,
            'status': self.status.value,
            'achievements': [a.to_dict() for a in self.achievements],
            'most_targeted_endpoints': self.most_targeted_endpoints,
            'user_agents': self.user_agents,
            'attack_patterns': self.attack_patterns,
            'blocked_at': self.blocked_at.isoformat() if self.blocked_at else None,
            'block_reason': self.block_reason,
            'block_duration_hours': self.block_duration.total_seconds() / 3600 if self.block_duration else None,
            'is_blocked': self.is_blocked(),
            'achievement_score': self.get_achievement_score()
        }

@dataclass
class DefenseAction:
    """Defense action taken against an attack."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    attack_id: str = ""
    action_type: DefenseActionType = DefenseActionType.WARNING_LOGGED
    intensity: int = 1
    success: bool = True
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Performance metrics
    execution_time_ms: float = 0.0
    bytes_generated: int = 0
    cpu_usage_percent: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'attack_id': self.attack_id,
            'action_type': self.action_type.value,
            'intensity': self.intensity,
            'success': self.success,
            'timestamp': self.timestamp.isoformat(),
            'details': self.details,
            'execution_time_ms': self.execution_time_ms,
            'bytes_generated': self.bytes_generated,
            'cpu_usage_percent': self.cpu_usage_percent
        }

@dataclass
class DefenseMetrics:
    """Real-time defense system metrics."""
    
    # Attack statistics
    total_attacks_detected: int = 0
    attacks_blocked: int = 0
    attacks_in_progress: int = 0
    
    # Defense system statistics
    emoji_nukes_deployed: int = 0
    total_bandwidth_wasted: int = 0  # bytes
    current_max_punishment_level: int = 0
    ips_blocked: int = 0
    ips_terminated: int = 0
    
    # Performance metrics
    average_response_time_ms: float = 0.0
    defense_success_rate: float = 1.0
    system_load_percent: float = 0.0
    
    # Active defense systems
    active_defense_systems: List[str] = field(default_factory=list)
    
    # Time window for metrics
    metrics_window_start: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'total_attacks_detected': self.total_attacks_detected,
            'attacks_blocked': self.attacks_blocked,
            'attacks_in_progress': self.attacks_in_progress,
            'emoji_nukes_deployed': self.emoji_nukes_deployed,
            'total_bandwidth_wasted': self.total_bandwidth_wasted,
            'bandwidth_wasted_mb': round(self.total_bandwidth_wasted / 1024 / 1024, 2),
            'current_max_punishment_level': self.current_max_punishment_level,
            'ips_blocked': self.ips_blocked,
            'ips_terminated': self.ips_terminated,
            'average_response_time_ms': self.average_response_time_ms,
            'defense_success_rate': self.defense_success_rate,
            'system_load_percent': self.system_load_percent,
            'active_defense_systems': self.active_defense_systems,
            'metrics_window_start': self.metrics_window_start.isoformat(),
            'last_updated': self.last_updated.isoformat()
        }

# Predefined achievements
PREDEFINED_ACHIEVEMENTS = [
    Achievement(
        id="persistent_pest",
        name="Persistent Pest",
        description="Made 100+ failed attempts",
        icon="🐛",
        threshold=100
    ),
    Achievement(
        id="bandwidth_waster",
        name="Bandwidth Waster",
        description="Wasted over 1GB of bandwidth",
        icon="📡",
        threshold=1073741824  # 1GB in bytes
    ),
    Achievement(
        id="endpoint_explorer",
        name="Endpoint Explorer", 
        description="Tried 50+ different endpoints",
        icon="🗺️",
        threshold=50
    ),
    Achievement(
        id="punishment_survivor",
        name="Punishment Survivor",
        description="Survived punishment level 10",
        icon="💪",
        threshold=10
    ),
    Achievement(
        id="completely_obliterated",
        name="Completely Obliterated",
        description="Reached maximum punishment level 15",
        icon="💀",
        threshold=15
    ),
    Achievement(
        id="speed_demon",
        name="Speed Demon",
        description="Made 1000+ requests in one hour",
        icon="⚡",
        threshold=1000
    ),
    Achievement(
        id="hall_of_fame",
        name="Hall of Fame",
        description="Top 10 most persistent bot",
        icon="🏆",
        threshold=1
    ),
    Achievement(
        id="terminated",
        name="TERMINATED",
        description="IP permanently blocked",
        icon="☠️",
        threshold=1
    )
]