"""
Traffic Analyzer for Observatory Patterns

Analyzes traffic patterns to identify Observatory-specific requests
and detect potential abuse of whitelisted patterns.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import re

from .api_client import CloudflareAPIClient, CloudflareAPIError

logger = logging.getLogger(__name__)


class TrafficPattern(Enum):
    """Types of Observatory traffic patterns"""
    INTERNAL_POLLING = "internal_polling"
    WEBSOCKET_CONNECTION = "websocket_connection"
    HEALTH_CHECK = "health_check"
    METRICS_COLLECTION = "metrics_collection"
    API_REQUEST = "api_request"
    UNKNOWN = "unknown"


@dataclass
class TrafficEvent:
    """Individual traffic event from Cloudflare"""
    timestamp: datetime
    ip_address: str
    user_agent: str
    uri_path: str
    method: str
    status_code: int
    country: str
    action_taken: str
    rule_id: Optional[str] = None
    pattern_type: Optional[TrafficPattern] = None


@dataclass
class TrafficAnalysis:
    """Analysis results for traffic patterns"""
    total_requests: int
    observatory_requests: int
    blocked_requests: int
    pattern_breakdown: Dict[TrafficPattern, int]
    suspicious_activity: List[Dict[str, Any]]
    recommendations: List[str]


class TrafficAnalyzer:
    """
    Analyzes Observatory traffic patterns and detects abuse
    
    Monitors Cloudflare security events to identify legitimate
    Observatory traffic and detect potential abuse of whitelist rules.
    """
    
    # Observatory-specific patterns for identification
    OBSERVATORY_PATTERNS = {
        TrafficPattern.INTERNAL_POLLING: [
            r"Observatory-Internal",
            r"x-observatory-client.*internal-polling",
            r"observatory-polling"
        ],
        TrafficPattern.WEBSOCKET_CONNECTION: [
            r"/ws/",
            r"websocket",
            r"upgrade.*websocket"
        ],
        TrafficPattern.HEALTH_CHECK: [
            r"/health",
            r"/healthcheck",
            r"health.*endpoint"
        ],
        TrafficPattern.METRICS_COLLECTION: [
            r"/metrics",
            r"/observatory/metrics",
            r"prometheus"
        ],
        TrafficPattern.API_REQUEST: [
            r"/api/observatory",
            r"/observatory/api",
            r"observatory.*api"
        ]
    }
    
    def __init__(self, api_client: CloudflareAPIClient):
        self.api_client = api_client
        self._log_action("traffic_analyzer_init", "in_progress", {
            "pattern_types": len(self.OBSERVATORY_PATTERNS)
        })
    
    def _log_action(self, action: str, status: str, details: Dict[str, Any]):
        """Log action in JSON format as required"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "task": "5.1",
            "action": action,
            "status": status,
            "details": details
        }
        print(json.dumps(log_entry))
        logger.info(f"Traffic Analyzer action: {action} - {status}")
    
    async def analyze_recent_traffic(self, hours: int = 24) -> TrafficAnalysis:
        """
        Analyze recent traffic patterns for Observatory activity
        
        Args:
            hours: Number of hours to analyze (default: 24)
            
        Returns:
            TrafficAnalysis with pattern breakdown and recommendations
        """
        self._log_action("analyze_recent_traffic", "in_progress", {
            "hours": hours
        })
        
        try:
            # Get security events from Cloudflare
            events = await self.api_client.get_security_events(limit=1000)
            
            # Filter events from the specified time period
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            recent_events = [
                event for event in events
                if self._parse_event_timestamp(event) >= cutoff_time
            ]
            
            # Convert to TrafficEvent objects
            traffic_events = [self._parse_traffic_event(event) for event in recent_events]
            
            # Analyze patterns
            analysis = self._analyze_traffic_patterns(traffic_events)
            
            self._log_action("analyze_recent_traffic", "completed", {
                "total_events": len(traffic_events),
                "observatory_events": analysis.observatory_requests,
                "blocked_events": analysis.blocked_requests
            })
            
            return analysis
            
        except CloudflareAPIError as e:
            self._log_action("analyze_recent_traffic", "error", {
                "error": str(e)
            })
            raise
    
    def _parse_event_timestamp(self, event: Dict[str, Any]) -> datetime:
        """Parse timestamp from Cloudflare event"""
        timestamp_str = event.get("occurred_at", "")
        try:
            return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except ValueError:
            return datetime.utcnow() - timedelta(days=1)  # Default to 1 day ago
    
    def _parse_traffic_event(self, event: Dict[str, Any]) -> TrafficEvent:
        """Parse Cloudflare security event into TrafficEvent"""
        # Extract relevant fields from the event
        ip_address = event.get("source", {}).get("ip", "unknown")
        user_agent = event.get("source", {}).get("user_agent", "")
        uri_path = event.get("source", {}).get("uri", "")
        method = event.get("source", {}).get("method", "GET")
        status_code = event.get("source", {}).get("status_code", 200)
        country = event.get("source", {}).get("country", "unknown")
        action_taken = event.get("action", "unknown")
        rule_id = event.get("rule_id")
        
        # Determine traffic pattern type
        pattern_type = self._classify_traffic_pattern(user_agent, uri_path)
        
        return TrafficEvent(
            timestamp=self._parse_event_timestamp(event),
            ip_address=ip_address,
            user_agent=user_agent,
            uri_path=uri_path,
            method=method,
            status_code=status_code,
            country=country,
            action_taken=action_taken,
            rule_id=rule_id,
            pattern_type=pattern_type
        )
    
    def _classify_traffic_pattern(self, user_agent: str, uri_path: str) -> TrafficPattern:
        """Classify traffic pattern based on user agent and URI"""
        combined_text = f"{user_agent} {uri_path}".lower()
        
        for pattern_type, patterns in self.OBSERVATORY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern.lower(), combined_text):
                    return pattern_type
        
        return TrafficPattern.UNKNOWN
    
    def _analyze_traffic_patterns(self, events: List[TrafficEvent]) -> TrafficAnalysis:
        """Analyze traffic patterns and generate insights"""
        total_requests = len(events)
        observatory_requests = sum(1 for event in events if event.pattern_type != TrafficPattern.UNKNOWN)
        blocked_requests = sum(1 for event in events if event.action_taken in ["block", "challenge"])
        
        # Count pattern types
        pattern_breakdown = {pattern: 0 for pattern in TrafficPattern}
        for event in events:
            if event.pattern_type:
                pattern_breakdown[event.pattern_type] += 1
        
        # Detect suspicious activity
        suspicious_activity = self._detect_suspicious_activity(events)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(events, pattern_breakdown)
        
        return TrafficAnalysis(
            total_requests=total_requests,
            observatory_requests=observatory_requests,
            blocked_requests=blocked_requests,
            pattern_breakdown=pattern_breakdown,
            suspicious_activity=suspicious_activity,
            recommendations=recommendations
        )
    
    def _detect_suspicious_activity(self, events: List[TrafficEvent]) -> List[Dict[str, Any]]:
        """Detect potentially suspicious activity patterns"""
        suspicious = []
        
        # Group events by IP address
        ip_groups = {}
        for event in events:
            if event.ip_address not in ip_groups:
                ip_groups[event.ip_address] = []
            ip_groups[event.ip_address].append(event)
        
        # Check for high-frequency requests from single IPs
        for ip, ip_events in ip_groups.items():
            if len(ip_events) > 100:  # Threshold for suspicious activity
                observatory_events = [e for e in ip_events if e.pattern_type != TrafficPattern.UNKNOWN]
                if len(observatory_events) > 50:
                    suspicious.append({
                        "type": "high_frequency_observatory_traffic",
                        "ip_address": ip,
                        "total_requests": len(ip_events),
                        "observatory_requests": len(observatory_events),
                        "severity": "medium"
                    })
        
        # Check for unusual user agents claiming to be Observatory
        observatory_events = [e for e in events if e.pattern_type != TrafficPattern.UNKNOWN]
        user_agents = {}
        for event in observatory_events:
            if event.user_agent not in user_agents:
                user_agents[event.user_agent] = []
            user_agents[event.user_agent].append(event)
        
        for ua, ua_events in user_agents.items():
            if len(ua_events) > 20 and not self._is_legitimate_observatory_ua(ua):
                suspicious.append({
                    "type": "suspicious_user_agent",
                    "user_agent": ua,
                    "request_count": len(ua_events),
                    "severity": "high"
                })
        
        return suspicious
    
    def _is_legitimate_observatory_ua(self, user_agent: str) -> bool:
        """Check if user agent appears to be legitimate Observatory traffic"""
        legitimate_patterns = [
            r"observatory-internal",
            r"observatory-polling",
            r"observatory-monitoring",
            r"observatory-health-check"
        ]
        
        ua_lower = user_agent.lower()
        return any(re.search(pattern, ua_lower) for pattern in legitimate_patterns)
    
    def _generate_recommendations(self, events: List[TrafficEvent], 
                                pattern_breakdown: Dict[TrafficPattern, int]) -> List[str]:
        """Generate recommendations based on traffic analysis"""
        recommendations = []
        
        # Check Observatory traffic ratio
        total_observatory = sum(pattern_breakdown.values()) - pattern_breakdown[TrafficPattern.UNKNOWN]
        total_traffic = len(events)
        
        if total_traffic > 0:
            observatory_ratio = total_observatory / total_traffic
            if observatory_ratio < 0.1:
                recommendations.append(
                    "Low Observatory traffic ratio detected. Consider reviewing whitelist rules."
                )
            elif observatory_ratio > 0.8:
                recommendations.append(
                    "High Observatory traffic ratio. Monitor for potential abuse."
                )
        
        # Check for blocked Observatory traffic
        blocked_observatory = sum(
            1 for event in events 
            if event.pattern_type != TrafficPattern.UNKNOWN and 
               event.action_taken in ["block", "challenge"]
        )
        
        if blocked_observatory > 0:
            recommendations.append(
                f"Found {blocked_observatory} blocked Observatory requests. "
                "Review and update whitelist rules."
            )
        
        # Check pattern distribution
        if pattern_breakdown[TrafficPattern.WEBSOCKET_CONNECTION] == 0:
            recommendations.append(
                "No WebSocket connections detected. Verify Observatory WebSocket endpoints."
            )
        
        if pattern_breakdown[TrafficPattern.HEALTH_CHECK] == 0:
            recommendations.append(
                "No health check requests detected. Verify Observatory health endpoints."
            )
        
        return recommendations
    
    async def get_observatory_traffic_summary(self) -> Dict[str, Any]:
        """
        Get summary of Observatory traffic patterns
        
        Returns:
            Dictionary with traffic summary statistics
        """
        self._log_action("get_traffic_summary", "in_progress", {})
        
        try:
            analysis = await self.analyze_recent_traffic(hours=24)
            
            summary = {
                "total_requests_24h": analysis.total_requests,
                "observatory_requests_24h": analysis.observatory_requests,
                "blocked_requests_24h": analysis.blocked_requests,
                "pattern_distribution": {
                    pattern.value: count 
                    for pattern, count in analysis.pattern_breakdown.items()
                },
                "suspicious_activity_count": len(analysis.suspicious_activity),
                "recommendations": analysis.recommendations,
                "analysis_timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            self._log_action("get_traffic_summary", "completed", {
                "total_requests": analysis.total_requests,
                "observatory_requests": analysis.observatory_requests
            })
            
            return summary
            
        except CloudflareAPIError as e:
            self._log_action("get_traffic_summary", "error", {
                "error": str(e)
            })
            raise
    
    async def monitor_whitelist_effectiveness(self) -> Dict[str, Any]:
        """
        Monitor effectiveness of Observatory whitelist rules
        
        Returns:
            Dictionary with effectiveness metrics
        """
        self._log_action("monitor_whitelist_effectiveness", "in_progress", {})
        
        try:
            analysis = await self.analyze_recent_traffic(hours=1)  # Last hour
            
            # Calculate effectiveness metrics
            total_observatory = analysis.observatory_requests
            blocked_observatory = sum(
                1 for event in analysis.suspicious_activity
                if event.get("type") == "blocked_observatory_traffic"
            )
            
            effectiveness = {
                "total_observatory_requests": total_observatory,
                "blocked_observatory_requests": blocked_observatory,
                "whitelist_success_rate": (
                    (total_observatory - blocked_observatory) / total_observatory * 100
                    if total_observatory > 0 else 100
                ),
                "false_positive_rate": (
                    blocked_observatory / total_observatory * 100
                    if total_observatory > 0 else 0
                ),
                "suspicious_activity_detected": len(analysis.suspicious_activity),
                "monitoring_period": "1 hour",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            self._log_action("monitor_whitelist_effectiveness", "completed", {
                "success_rate": effectiveness["whitelist_success_rate"],
                "false_positive_rate": effectiveness["false_positive_rate"]
            })
            
            return effectiveness
            
        except CloudflareAPIError as e:
            self._log_action("monitor_whitelist_effectiveness", "error", {
                "error": str(e)
            })
            raise