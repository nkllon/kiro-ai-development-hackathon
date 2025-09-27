"""
Traffic Analyzer for Observatory Pattern Detection.

Analyzes traffic patterns to identify Observatory-specific requests and behaviors.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

from .api_client import CloudflareAPIClient, CloudflareAPIError


class TrafficPattern:
    """Represents a traffic pattern for Observatory."""
    
    def __init__(
        self,
        pattern_type: str,
        expression: str,
        description: str,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.pattern_type = pattern_type
        self.expression = expression
        self.description = description
        self.confidence = confidence
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "pattern_type": self.pattern_type,
            "expression": self.expression,
            "description": self.description,
            "confidence": self.confidence,
            "metadata": self.metadata
        }


class TrafficAnalyzer:
    """Analyzes traffic patterns to identify Observatory requests."""
    
    # Predefined Observatory patterns
    OBSERVATORY_PATTERNS = [
        TrafficPattern(
            pattern_type="user_agent",
            expression='(http.user_agent contains "Observatory-Internal")',
            description="Observatory internal polling traffic",
            confidence=1.0,
            metadata={"source": "user_agent_header"}
        ),
        TrafficPattern(
            pattern_type="websocket",
            expression='(http.request.uri.path matches "^/ws/")',
            description="Observatory WebSocket endpoints",
            confidence=0.9,
            metadata={"source": "uri_path", "protocol": "websocket"}
        ),
        TrafficPattern(
            pattern_type="custom_header",
            expression='(http.request.headers["x-observatory-client"][0] eq "internal-polling")',
            description="Observatory polling fallback",
            confidence=0.95,
            metadata={"source": "custom_header", "header_name": "x-observatory-client"}
        ),
        TrafficPattern(
            pattern_type="health_check",
            expression='(http.request.uri.path matches "^/health")',
            description="Observatory health check endpoints",
            confidence=0.8,
            metadata={"source": "uri_path", "endpoint_type": "health"}
        ),
        TrafficPattern(
            pattern_type="api_endpoint",
            expression='(http.request.uri.path matches "^/api/observatory/")',
            description="Observatory API endpoints",
            confidence=0.85,
            metadata={"source": "uri_path", "endpoint_type": "api"}
        )
    ]
    
    def __init__(self, api_client: CloudflareAPIClient):
        self.api_client = api_client
        self.logger = logging.getLogger(__name__)
        
    async def analyze_recent_traffic(
        self,
        zone_id: str,
        hours_back: int = 24,
        sample_size: int = 1000
    ) -> Dict[str, Any]:
        """Analyze recent traffic to identify Observatory patterns."""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours_back)
            
            self.logger.info(f"Analyzing traffic from {start_time} to {end_time}")
            
            # Get security events
            events = await self.api_client.get_security_events(zone_id, start_time, end_time)
            
            # Analyze events for Observatory patterns
            analysis_result = self._analyze_events(events.get("result", []), sample_size)
            
            self.logger.info(f"Traffic analysis completed: {len(analysis_result.get('patterns', []))} patterns found")
            return analysis_result
            
        except CloudflareAPIError as e:
            self.logger.error(f"Failed to analyze traffic: {e}")
            raise
            
    def _analyze_events(self, events: List[Dict[str, Any]], sample_size: int) -> Dict[str, Any]:
        """Analyze security events for Observatory patterns."""
        if not events:
            return {"patterns": [], "summary": {"total_events": 0}}
            
        # Sample events if too many
        if len(events) > sample_size:
            events = events[:sample_size]
            
        patterns_found = []
        observatory_requests = 0
        blocked_requests = 0
        
        for event in events:
            # Check if this looks like Observatory traffic
            if self._is_observatory_request(event):
                observatory_requests += 1
                
                # Check if it was blocked
                if event.get("action") in ["block", "challenge"]:
                    blocked_requests += 1
                    
                    # Find matching pattern
                    pattern = self._find_matching_pattern(event)
                    if pattern:
                        patterns_found.append({
                            "pattern": pattern.to_dict(),
                            "event": event,
                            "blocked": True
                        })
                        
        return {
            "patterns": patterns_found,
            "summary": {
                "total_events": len(events),
                "observatory_requests": observatory_requests,
                "blocked_observatory_requests": blocked_requests,
                "block_rate": blocked_requests / max(observatory_requests, 1)
            }
        }
        
    def _is_observatory_request(self, event: Dict[str, Any]) -> bool:
        """Check if an event represents Observatory traffic."""
        # Check user agent
        user_agent = event.get("user_agent", "").lower()
        if "observatory" in user_agent:
            return True
            
        # Check URI path
        uri_path = event.get("uri", "").lower()
        if any(path in uri_path for path in ["/ws/", "/health", "/api/observatory/"]):
            return True
            
        # Check headers
        headers = event.get("request_headers", {})
        if "x-observatory-client" in headers:
            return True
            
        return False
        
    def _find_matching_pattern(self, event: Dict[str, Any]) -> Optional[TrafficPattern]:
        """Find the best matching pattern for an event."""
        best_pattern = None
        best_score = 0.0
        
        for pattern in self.OBSERVATORY_PATTERNS:
            score = self._calculate_pattern_match_score(event, pattern)
            if score > best_score:
                best_score = score
                best_pattern = pattern
                
        return best_pattern if best_score > 0.5 else None
        
    def _calculate_pattern_match_score(self, event: Dict[str, Any], pattern: TrafficPattern) -> float:
        """Calculate how well an event matches a pattern."""
        score = 0.0
        
        if pattern.pattern_type == "user_agent":
            user_agent = event.get("user_agent", "").lower()
            if "observatory" in user_agent:
                score += 0.8
                
        elif pattern.pattern_type == "websocket":
            uri_path = event.get("uri", "").lower()
            if "/ws/" in uri_path:
                score += 0.9
                
        elif pattern.pattern_type == "custom_header":
            headers = event.get("request_headers", {})
            if "x-observatory-client" in headers:
                score += 0.95
                
        elif pattern.pattern_type == "health_check":
            uri_path = event.get("uri", "").lower()
            if "/health" in uri_path:
                score += 0.8
                
        elif pattern.pattern_type == "api_endpoint":
            uri_path = event.get("uri", "").lower()
            if "/api/observatory/" in uri_path:
                score += 0.85
                
        return score * pattern.confidence
        
    def get_recommended_whitelist_rules(self) -> List[TrafficPattern]:
        """Get recommended whitelist rules for Observatory."""
        return self.OBSERVATORY_PATTERNS.copy()
        
    def create_custom_pattern(
        self,
        pattern_type: str,
        expression: str,
        description: str,
        confidence: float = 0.8
    ) -> TrafficPattern:
        """Create a custom traffic pattern."""
        return TrafficPattern(
            pattern_type=pattern_type,
            expression=expression,
            description=description,
            confidence=confidence,
            metadata={"source": "custom", "created_at": datetime.utcnow().isoformat()}
        )
        
    async def validate_pattern_effectiveness(
        self,
        zone_id: str,
        pattern: TrafficPattern,
        test_duration_hours: int = 1
    ) -> Dict[str, Any]:
        """Validate how effective a pattern is at identifying Observatory traffic."""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=test_duration_hours)
            
            events = await self.api_client.get_security_events(zone_id, start_time, end_time)
            
            total_matches = 0
            false_positives = 0
            
            for event in events.get("result", []):
                if self._calculate_pattern_match_score(event, pattern) > 0.5:
                    total_matches += 1
                    if not self._is_observatory_request(event):
                        false_positives += 1
                        
            precision = (total_matches - false_positives) / max(total_matches, 1)
            
            return {
                "pattern": pattern.to_dict(),
                "total_matches": total_matches,
                "false_positives": false_positives,
                "precision": precision,
                "test_duration_hours": test_duration_hours
            }
            
        except CloudflareAPIError as e:
            self.logger.error(f"Failed to validate pattern effectiveness: {e}")
            raise