"""
Attack Detection Engine
Intelligent bot behavior analysis and attack identification.
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from collections import defaultdict, deque
import ipaddress

from .models import Attack, AttackType, BotProfile
from .config import get_config
from .database import get_database

logger = logging.getLogger(__name__)

@dataclass
class IPBehavior:
    """Track IP behavior patterns over time."""
    
    ip: str
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    request_count: int = 0
    endpoints_accessed: Set[str] = field(default_factory=set)
    user_agents: Set[str] = field(default_factory=set)
    methods: Set[str] = field(default_factory=set)
    
    # Rate limiting tracking
    requests_per_minute: deque = field(default_factory=lambda: deque(maxlen=60))
    requests_per_hour: deque = field(default_factory=lambda: deque(maxlen=3600))
    
    # Suspicious behavior indicators
    suspicious_endpoints_hit: int = 0
    consecutive_404s: int = 0
    rapid_fire_requests: int = 0
    
    def add_request(self, endpoint: str, user_agent: str, method: str = "GET", 
                   is_suspicious_endpoint: bool = False, is_404: bool = False):
        """Record a new request from this IP."""
        now = datetime.now()
        self.last_seen = now
        self.request_count += 1
        
        # Track unique values
        self.endpoints_accessed.add(endpoint)
        self.user_agents.add(user_agent)
        self.methods.add(method)
        
        # Track rate limiting
        self.requests_per_minute.append(now)
        self.requests_per_hour.append(now)
        
        # Track suspicious behavior
        if is_suspicious_endpoint:
            self.suspicious_endpoints_hit += 1
        
        if is_404:
            self.consecutive_404s += 1
        else:
            self.consecutive_404s = 0  # Reset on successful request
    
    def get_requests_per_minute(self) -> int:
        """Get requests in the last minute."""
        cutoff = datetime.now() - timedelta(minutes=1)
        return sum(1 for req_time in self.requests_per_minute if req_time > cutoff)
    
    def get_requests_per_hour(self) -> int:
        """Get requests in the last hour."""
        cutoff = datetime.now() - timedelta(hours=1)
        return sum(1 for req_time in self.requests_per_hour if req_time > cutoff)
    
    def calculate_suspicion_score(self) -> float:
        """Calculate overall suspicion score (0.0 - 1.0)."""
        score = 0.0
        
        # Rate limiting violations
        rpm = self.get_requests_per_minute()
        rph = self.get_requests_per_hour()
        
        if rpm > 60:  # More than 1 request per second
            score += min(0.3, rpm / 200)
        
        if rph > 1000:  # More than 1000 requests per hour
            score += min(0.2, rph / 5000)
        
        # Suspicious endpoint targeting
        if self.suspicious_endpoints_hit > 0:
            score += min(0.3, self.suspicious_endpoints_hit / 10)
        
        # Consecutive 404s (scanning behavior)
        if self.consecutive_404s > 5:
            score += min(0.2, self.consecutive_404s / 20)
        
        # Diverse endpoint scanning
        if len(self.endpoints_accessed) > 50:
            score += min(0.2, len(self.endpoints_accessed) / 200)
        
        # Bot-like user agents
        bot_indicators = ['bot', 'crawler', 'spider', 'scraper', 'curl', 'wget', 'python']
        for ua in self.user_agents:
            if any(indicator in ua.lower() for indicator in bot_indicators):
                score += 0.1
                break
        
        return min(1.0, score)

@dataclass
class AttackAnalysis:
    """Result of attack analysis."""
    
    is_suspicious: bool
    confidence_score: float
    attack_type: AttackType
    reasons: List[str] = field(default_factory=list)
    recommended_punishment_level: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'is_suspicious': self.is_suspicious,
            'confidence_score': self.confidence_score,
            'attack_type': self.attack_type.value,
            'reasons': self.reasons,
            'recommended_punishment_level': self.recommended_punishment_level
        }

class AttackDetector:
    """Intelligent attack detection and analysis engine."""
    
    def __init__(self):
        self.config = get_config()
        self.database = get_database()
        
        # In-memory behavior tracking
        self.ip_behaviors: Dict[str, IPBehavior] = {}
        
        # Compile regex patterns for efficiency
        self.suspicious_ua_patterns = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in self.config.attack_detection.suspicious_user_agents
        ]
        
        # Known attack patterns
        self.vulnerability_patterns = {
            'sql_injection': [
                re.compile(r"['\";].*(\bor\b|\band\b).*['\";]", re.IGNORECASE),
                re.compile(r"union.*select", re.IGNORECASE),
                re.compile(r"drop\s+table", re.IGNORECASE)
            ],
            'xss': [
                re.compile(r"<script", re.IGNORECASE),
                re.compile(r"javascript:", re.IGNORECASE),
                re.compile(r"on\w+\s*=", re.IGNORECASE)
            ],
            'path_traversal': [
                re.compile(r"\.\./", re.IGNORECASE),
                re.compile(r"\.\.\\", re.IGNORECASE),
                re.compile(r"%2e%2e", re.IGNORECASE)
            ]
        }
        
        logger.info("Attack detector initialized with comprehensive pattern matching")
    
    async def analyze_request(self, 
                            source_ip: str,
                            endpoint: str,
                            user_agent: str = "",
                            method: str = "GET",
                            headers: Optional[Dict[str, str]] = None,
                            query_params: Optional[Dict[str, str]] = None,
                            response_code: int = 200) -> AttackAnalysis:
        """Analyze a request for suspicious behavior."""
        
        headers = headers or {}
        query_params = query_params or {}
        
        # Get or create IP behavior tracking
        ip_behavior = await self._get_ip_behavior(source_ip)
        
        # Check if endpoint is suspicious
        is_suspicious_endpoint = self._is_suspicious_endpoint(endpoint)
        is_404 = response_code == 404
        
        # Update behavior tracking
        ip_behavior.add_request(
            endpoint=endpoint,
            user_agent=user_agent,
            method=method,
            is_suspicious_endpoint=is_suspicious_endpoint,
            is_404=is_404
        )
        
        # Analyze the request
        analysis = AttackAnalysis(
            is_suspicious=False,
            confidence_score=0.0,
            attack_type=AttackType.UNKNOWN
        )
        
        # Check various attack indicators
        await self._check_suspicious_endpoint(analysis, endpoint)
        await self._check_rate_limiting(analysis, ip_behavior)
        await self._check_user_agent(analysis, user_agent)
        await self._check_vulnerability_patterns(analysis, endpoint, query_params)
        await self._check_scanning_behavior(analysis, ip_behavior)
        
        # Calculate overall confidence and determine if suspicious
        analysis.confidence_score = min(1.0, analysis.confidence_score)
        analysis.is_suspicious = analysis.confidence_score >= self.config.attack_detection.confidence_threshold
        
        # Determine punishment level based on confidence
        if analysis.confidence_score >= 0.9:
            analysis.recommended_punishment_level = 5
        elif analysis.confidence_score >= 0.7:
            analysis.recommended_punishment_level = 3
        elif analysis.confidence_score >= 0.5:
            analysis.recommended_punishment_level = 2
        else:
            analysis.recommended_punishment_level = 1
        
        return analysis
    
    async def _get_ip_behavior(self, ip: str) -> IPBehavior:
        """Get or create IP behavior tracking."""
        if ip not in self.ip_behaviors:
            self.ip_behaviors[ip] = IPBehavior(ip=ip)
        return self.ip_behaviors[ip]
    
    def _is_suspicious_endpoint(self, endpoint: str) -> bool:
        """Check if endpoint is known to be suspicious."""
        return any(
            suspicious in endpoint.lower() 
            for suspicious in self.config.attack_detection.suspicious_endpoints
        )
    
    async def _check_suspicious_endpoint(self, analysis: AttackAnalysis, endpoint: str):
        """Check if the endpoint is suspicious."""
        if self._is_suspicious_endpoint(endpoint):
            analysis.confidence_score += 0.4
            analysis.attack_type = AttackType.SUSPICIOUS_ENDPOINT
            analysis.reasons.append(f"Accessing suspicious endpoint: {endpoint}")
    
    async def _check_rate_limiting(self, analysis: AttackAnalysis, ip_behavior: IPBehavior):
        """Check for rate limiting violations."""
        rpm = ip_behavior.get_requests_per_minute()
        rph = ip_behavior.get_requests_per_hour()
        
        rate_limits = self.config.attack_detection.rate_limits
        
        if rpm > rate_limits['requests_per_minute']:
            analysis.confidence_score += 0.3
            analysis.attack_type = AttackType.RATE_LIMIT_EXCEEDED
            analysis.reasons.append(f"Rate limit exceeded: {rpm} requests/minute")
        
        if rph > rate_limits['requests_per_hour']:
            analysis.confidence_score += 0.2
            analysis.attack_type = AttackType.RATE_LIMIT_EXCEEDED
            analysis.reasons.append(f"Hourly rate limit exceeded: {rph} requests/hour")
        
        # Check for suspicious request patterns
        suspicious_rpm = rate_limits.get('suspicious_requests_per_minute', 5)
        if ip_behavior.suspicious_endpoints_hit > 0 and rpm > suspicious_rpm:
            analysis.confidence_score += 0.4
            analysis.attack_type = AttackType.VULNERABILITY_SCAN
            analysis.reasons.append(f"Rapid suspicious endpoint scanning: {rpm} requests/minute")
    
    async def _check_user_agent(self, analysis: AttackAnalysis, user_agent: str):
        """Check user agent for bot indicators."""
        if not user_agent:
            analysis.confidence_score += 0.1
            analysis.reasons.append("Missing user agent")
            return
        
        # Check against suspicious patterns
        for pattern in self.suspicious_ua_patterns:
            if pattern.search(user_agent):
                analysis.confidence_score += 0.2
                analysis.attack_type = AttackType.SUSPICIOUS_USER_AGENT
                analysis.reasons.append(f"Suspicious user agent: {user_agent[:50]}...")
                break
    
    async def _check_vulnerability_patterns(self, analysis: AttackAnalysis, 
                                          endpoint: str, query_params: Dict[str, str]):
        """Check for vulnerability exploitation patterns."""
        
        # Combine endpoint and query parameters for analysis
        full_request = endpoint + "?" + "&".join(f"{k}={v}" for k, v in query_params.items())
        
        # Check SQL injection patterns
        for pattern in self.vulnerability_patterns['sql_injection']:
            if pattern.search(full_request):
                analysis.confidence_score += 0.6
                analysis.attack_type = AttackType.VULNERABILITY_SCAN
                analysis.reasons.append("SQL injection attempt detected")
                break
        
        # Check XSS patterns
        for pattern in self.vulnerability_patterns['xss']:
            if pattern.search(full_request):
                analysis.confidence_score += 0.5
                analysis.attack_type = AttackType.VULNERABILITY_SCAN
                analysis.reasons.append("XSS attempt detected")
                break
        
        # Check path traversal patterns
        for pattern in self.vulnerability_patterns['path_traversal']:
            if pattern.search(full_request):
                analysis.confidence_score += 0.5
                analysis.attack_type = AttackType.VULNERABILITY_SCAN
                analysis.reasons.append("Path traversal attempt detected")
                break
    
    async def _check_scanning_behavior(self, analysis: AttackAnalysis, ip_behavior: IPBehavior):
        """Check for scanning behavior patterns."""
        
        # Check for excessive 404s (directory/file scanning)
        if ip_behavior.consecutive_404s > 10:
            analysis.confidence_score += 0.3
            analysis.attack_type = AttackType.VULNERABILITY_SCAN
            analysis.reasons.append(f"Excessive 404 errors: {ip_behavior.consecutive_404s} consecutive")
        
        # Check for diverse endpoint access (reconnaissance)
        if len(ip_behavior.endpoints_accessed) > 100:
            analysis.confidence_score += 0.2
            analysis.attack_type = AttackType.VULNERABILITY_SCAN
            analysis.reasons.append(f"Extensive endpoint scanning: {len(ip_behavior.endpoints_accessed)} unique endpoints")
        
        # Check for brute force patterns (repeated access to login endpoints)
        login_endpoints = ['/login', '/admin', '/wp-admin', '/administrator']
        login_attempts = sum(1 for endpoint in ip_behavior.endpoints_accessed 
                           if any(login in endpoint.lower() for login in login_endpoints))
        
        if login_attempts > 20:
            analysis.confidence_score += 0.4
            analysis.attack_type = AttackType.BRUTE_FORCE
            analysis.reasons.append(f"Potential brute force: {login_attempts} login endpoint attempts")
    
    async def track_ip_behavior(self, ip: str, analysis: AttackAnalysis) -> IPBehavior:
        """Update and return IP behavior tracking."""
        ip_behavior = await self._get_ip_behavior(ip)
        
        # Update suspicion score
        ip_behavior.suspicion_score = ip_behavior.calculate_suspicion_score()
        
        return ip_behavior
    
    async def get_suspicious_ips(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get most suspicious IPs currently being tracked."""
        suspicious_ips = []
        
        for ip, behavior in self.ip_behaviors.items():
            suspicion_score = behavior.calculate_suspicion_score()
            if suspicion_score > 0.3:  # Only include moderately suspicious and above
                suspicious_ips.append({
                    'ip': ip,
                    'suspicion_score': suspicion_score,
                    'request_count': behavior.request_count,
                    'requests_per_minute': behavior.get_requests_per_minute(),
                    'requests_per_hour': behavior.get_requests_per_hour(),
                    'suspicious_endpoints_hit': behavior.suspicious_endpoints_hit,
                    'unique_endpoints': len(behavior.endpoints_accessed),
                    'unique_user_agents': len(behavior.user_agents),
                    'consecutive_404s': behavior.consecutive_404s,
                    'first_seen': behavior.first_seen.isoformat(),
                    'last_seen': behavior.last_seen.isoformat()
                })
        
        # Sort by suspicion score (highest first)
        suspicious_ips.sort(key=lambda x: x['suspicion_score'], reverse=True)
        
        return suspicious_ips[:limit]
    
    async def cleanup_old_behaviors(self, max_age_hours: int = 24):
        """Clean up old IP behavior tracking to prevent memory leaks."""
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        
        old_ips = [
            ip for ip, behavior in self.ip_behaviors.items()
            if behavior.last_seen < cutoff
        ]
        
        for ip in old_ips:
            del self.ip_behaviors[ip]
        
        if old_ips:
            logger.info(f"Cleaned up {len(old_ips)} old IP behavior records")
    
    def get_detection_stats(self) -> Dict[str, Any]:
        """Get attack detection statistics."""
        total_ips = len(self.ip_behaviors)
        suspicious_ips = sum(1 for behavior in self.ip_behaviors.values() 
                           if behavior.calculate_suspicion_score() > 0.5)
        
        return {
            'total_ips_tracked': total_ips,
            'suspicious_ips': suspicious_ips,
            'detection_patterns': {
                'suspicious_endpoints': len(self.config.attack_detection.suspicious_endpoints),
                'user_agent_patterns': len(self.suspicious_ua_patterns),
                'vulnerability_patterns': sum(len(patterns) for patterns in self.vulnerability_patterns.values())
            },
            'rate_limits': self.config.attack_detection.rate_limits,
            'confidence_threshold': self.config.attack_detection.confidence_threshold
        }

# Global detector instance
_detector: Optional[AttackDetector] = None

def get_attack_detector() -> AttackDetector:
    """Get the global attack detector instance."""
    global _detector
    if _detector is None:
        _detector = AttackDetector()
    return _detector