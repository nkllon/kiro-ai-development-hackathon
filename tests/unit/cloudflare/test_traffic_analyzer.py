"""
Unit tests for TrafficAnalyzer

Tests traffic pattern analysis, Observatory traffic detection,
and suspicious activity monitoring functionality.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta

from src.beast_mode.observatory.cloudflare.traffic_analyzer import (
    TrafficAnalyzer,
    TrafficEvent,
    TrafficAnalysis,
    TrafficPattern
)
from src.beast_mode.observatory.cloudflare.api_client import CloudflareAPIError


class TestTrafficEvent:
    """Test TrafficEvent dataclass"""
    
    def test_traffic_event_creation(self):
        """Test basic traffic event creation"""
        event = TrafficEvent(
            timestamp=datetime.utcnow(),
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            uri_path="/test",
            method="GET",
            status_code=200,
            country="US",
            action_taken="allow",
            rule_id="rule1",
            pattern_type=TrafficPattern.API_REQUEST
        )
        
        assert event.ip_address == "192.168.1.1"
        assert event.user_agent == "Mozilla/5.0"
        assert event.uri_path == "/test"
        assert event.method == "GET"
        assert event.status_code == 200
        assert event.country == "US"
        assert event.action_taken == "allow"
        assert event.rule_id == "rule1"
        assert event.pattern_type == TrafficPattern.API_REQUEST
    
    def test_traffic_event_minimal(self):
        """Test traffic event with minimal data"""
        event = TrafficEvent(
            timestamp=datetime.utcnow(),
            ip_address="192.168.1.1",
            user_agent="",
            uri_path="",
            method="GET",
            status_code=200,
            country="US",
            action_taken="block"
        )
        
        assert event.ip_address == "192.168.1.1"
        assert event.user_agent == ""
        assert event.uri_path == ""
        assert event.pattern_type is None


class TestTrafficAnalyzer:
    """Test TrafficAnalyzer functionality"""
    
    @pytest.fixture
    def mock_api_client(self):
        """Create mock API client"""
        return AsyncMock()
    
    @pytest.fixture
    def traffic_analyzer(self, mock_api_client):
        """Create traffic analyzer with mock client"""
        return TrafficAnalyzer(mock_api_client)
    
    def test_traffic_analyzer_initialization(self, traffic_analyzer):
        """Test traffic analyzer initialization"""
        assert traffic_analyzer.api_client is not None
        assert len(traffic_analyzer.OBSERVATORY_PATTERNS) == 5
    
    def test_observatory_patterns(self, traffic_analyzer):
        """Test Observatory patterns are properly defined"""
        patterns = traffic_analyzer.OBSERVATORY_PATTERNS
        
        assert TrafficPattern.INTERNAL_POLLING in patterns
        assert TrafficPattern.WEBSOCKET_CONNECTION in patterns
        assert TrafficPattern.HEALTH_CHECK in patterns
        assert TrafficPattern.METRICS_COLLECTION in patterns
        assert TrafficPattern.API_REQUEST in patterns
        
        # Check that patterns contain regex patterns
        for pattern_type, regex_patterns in patterns.items():
            assert len(regex_patterns) > 0
            for pattern in regex_patterns:
                assert isinstance(pattern, str)
                assert len(pattern) > 0
    
    def test_parse_event_timestamp_valid(self, traffic_analyzer):
        """Test parsing valid timestamp"""
        event = {"occurred_at": "2023-12-01T10:00:00Z"}
        timestamp = traffic_analyzer._parse_event_timestamp(event)
        
        assert isinstance(timestamp, datetime)
        assert timestamp.year == 2023
        assert timestamp.month == 12
        assert timestamp.day == 1
    
    def test_parse_event_timestamp_invalid(self, traffic_analyzer):
        """Test parsing invalid timestamp"""
        event = {"occurred_at": "invalid-timestamp"}
        timestamp = traffic_analyzer._parse_event_timestamp(event)
        
        # Should return a default timestamp (1 day ago)
        assert isinstance(timestamp, datetime)
        assert timestamp < datetime.utcnow()
    
    def test_parse_event_timestamp_missing(self, traffic_analyzer):
        """Test parsing missing timestamp"""
        event = {}
        timestamp = traffic_analyzer._parse_event_timestamp(event)
        
        # Should return a default timestamp (1 day ago)
        assert isinstance(timestamp, datetime)
        assert timestamp < datetime.utcnow()
    
    def test_classify_traffic_pattern_internal_polling(self, traffic_analyzer):
        """Test classifying internal polling traffic"""
        user_agent = "Observatory-Internal-Polling/1.0"
        uri_path = "/api/data"
        
        pattern = traffic_analyzer._classify_traffic_pattern(user_agent, uri_path)
        
        assert pattern == TrafficPattern.INTERNAL_POLLING
    
    def test_classify_traffic_pattern_websocket(self, traffic_analyzer):
        """Test classifying WebSocket traffic"""
        user_agent = "Mozilla/5.0"
        uri_path = "/ws/observatory"
        
        pattern = traffic_analyzer._classify_traffic_pattern(user_agent, uri_path)
        
        assert pattern == TrafficPattern.WEBSOCKET_CONNECTION
    
    def test_classify_traffic_pattern_health_check(self, traffic_analyzer):
        """Test classifying health check traffic"""
        user_agent = "Observatory-Health-Check"
        uri_path = "/health"
        
        pattern = traffic_analyzer._classify_traffic_pattern(user_agent, uri_path)
        
        assert pattern == TrafficPattern.HEALTH_CHECK
    
    def test_classify_traffic_pattern_metrics(self, traffic_analyzer):
        """Test classifying metrics traffic"""
        user_agent = "Prometheus"
        uri_path = "/metrics"
        
        pattern = traffic_analyzer._classify_traffic_pattern(user_agent, uri_path)
        
        assert pattern == TrafficPattern.METRICS_COLLECTION
    
    def test_classify_traffic_pattern_api(self, traffic_analyzer):
        """Test classifying API traffic"""
        user_agent = "Observatory-Client"
        uri_path = "/api/observatory/data"
        
        pattern = traffic_analyzer._classify_traffic_pattern(user_agent, uri_path)
        
        assert pattern == TrafficPattern.API_REQUEST
    
    def test_classify_traffic_pattern_unknown(self, traffic_analyzer):
        """Test classifying unknown traffic"""
        user_agent = "Regular-Browser"
        uri_path = "/regular-page"
        
        pattern = traffic_analyzer._classify_traffic_pattern(user_agent, uri_path)
        
        assert pattern == TrafficPattern.UNKNOWN
    
    def test_parse_traffic_event(self, traffic_analyzer):
        """Test parsing Cloudflare event into TrafficEvent"""
        event = {
            "occurred_at": "2023-12-01T10:00:00Z",
            "source": {
                "ip": "192.168.1.1",
                "user_agent": "Observatory-Internal",
                "uri": "/ws/test",
                "method": "GET",
                "status_code": 200,
                "country": "US"
            },
            "action": "allow",
            "rule_id": "rule1"
        }
        
        traffic_event = traffic_analyzer._parse_traffic_event(event)
        
        assert isinstance(traffic_event, TrafficEvent)
        assert traffic_event.ip_address == "192.168.1.1"
        assert traffic_event.user_agent == "Observatory-Internal"
        assert traffic_event.uri_path == "/ws/test"
        assert traffic_event.method == "GET"
        assert traffic_event.status_code == 200
        assert traffic_event.country == "US"
        assert traffic_event.action_taken == "allow"
        assert traffic_event.rule_id == "rule1"
        assert traffic_event.pattern_type == TrafficPattern.WEBSOCKET_CONNECTION
    
    def test_parse_traffic_event_missing_fields(self, traffic_analyzer):
        """Test parsing event with missing fields"""
        event = {
            "occurred_at": "2023-12-01T10:00:00Z",
            "source": {},
            "action": "block"
        }
        
        traffic_event = traffic_analyzer._parse_traffic_event(event)
        
        assert traffic_event.ip_address == "unknown"
        assert traffic_event.user_agent == ""
        assert traffic_event.uri_path == ""
        assert traffic_event.method == "GET"
        assert traffic_event.status_code == 200
        assert traffic_event.country == "unknown"
        assert traffic_event.action_taken == "block"
        assert traffic_event.rule_id is None
        assert traffic_event.pattern_type == TrafficPattern.UNKNOWN
    
    def test_analyze_traffic_patterns(self, traffic_analyzer):
        """Test traffic pattern analysis"""
        events = [
            TrafficEvent(
                timestamp=datetime.utcnow(),
                ip_address="192.168.1.1",
                user_agent="Observatory-Internal",
                uri_path="/api/data",
                method="GET",
                status_code=200,
                country="US",
                action_taken="allow",
                pattern_type=TrafficPattern.INTERNAL_POLLING
            ),
            TrafficEvent(
                timestamp=datetime.utcnow(),
                ip_address="192.168.1.2",
                user_agent="Mozilla/5.0",
                uri_path="/ws/test",
                method="GET",
                status_code=200,
                country="US",
                action_taken="allow",
                pattern_type=TrafficPattern.WEBSOCKET_CONNECTION
            ),
            TrafficEvent(
                timestamp=datetime.utcnow(),
                ip_address="192.168.1.3",
                user_agent="Bad-Bot",
                uri_path="/malicious",
                method="GET",
                status_code=403,
                country="RU",
                action_taken="block",
                pattern_type=TrafficPattern.UNKNOWN
            )
        ]
        
        analysis = traffic_analyzer._analyze_traffic_patterns(events)
        
        assert isinstance(analysis, TrafficAnalysis)
        assert analysis.total_requests == 3
        assert analysis.observatory_requests == 2
        assert analysis.blocked_requests == 1
        assert analysis.pattern_breakdown[TrafficPattern.INTERNAL_POLLING] == 1
        assert analysis.pattern_breakdown[TrafficPattern.WEBSOCKET_CONNECTION] == 1
        assert analysis.pattern_breakdown[TrafficPattern.UNKNOWN] == 1
    
    def test_detect_suspicious_activity_high_frequency(self, traffic_analyzer):
        """Test detection of high-frequency suspicious activity"""
        # Create events with high frequency from single IP
        events = []
        for i in range(150):  # Above threshold of 100
            events.append(TrafficEvent(
                timestamp=datetime.utcnow(),
                ip_address="192.168.1.1",  # Same IP
                user_agent="Observatory-Internal",
                uri_path="/api/data",
                method="GET",
                status_code=200,
                country="US",
                action_taken="allow",
                pattern_type=TrafficPattern.INTERNAL_POLLING
            ))
        
        suspicious = traffic_analyzer._detect_suspicious_activity(events)
        
        assert len(suspicious) > 0
        assert any(activity["type"] == "high_frequency_observatory_traffic" for activity in suspicious)
    
    def test_detect_suspicious_activity_suspicious_ua(self, traffic_analyzer):
        """Test detection of suspicious user agents"""
        events = []
        for i in range(25):  # Above threshold of 20
            events.append(TrafficEvent(
                timestamp=datetime.utcnow(),
                ip_address="192.168.1.1",
                user_agent="Fake-Observatory-Bot",  # Suspicious UA
                uri_path="/api/data",
                method="GET",
                status_code=200,
                country="US",
                action_taken="allow",
                pattern_type=TrafficPattern.INTERNAL_POLLING
            ))
        
        suspicious = traffic_analyzer._detect_suspicious_activity(events)
        
        assert len(suspicious) > 0
        assert any(activity["type"] == "suspicious_user_agent" for activity in suspicious)
    
    def test_is_legitimate_observatory_ua(self, traffic_analyzer):
        """Test legitimate Observatory user agent detection"""
        legitimate_uas = [
            "Observatory-Internal/1.0",
            "Observatory-Polling/2.0",
            "Observatory-Monitoring/1.5",
            "Observatory-Health-Check/1.0"
        ]
        
        for ua in legitimate_uas:
            assert traffic_analyzer._is_legitimate_observatory_ua(ua)
    
    def test_is_legitimate_observatory_ua_illegitimate(self, traffic_analyzer):
        """Test illegitimate Observatory user agent detection"""
        illegitimate_uas = [
            "Fake-Observatory-Bot",
            "Observatory-Spam",
            "Regular-Browser",
            "Malicious-Bot-Observatory"
        ]
        
        for ua in illegitimate_uas:
            assert not traffic_analyzer._is_legitimate_observatory_ua(ua)
    
    def test_generate_recommendations_low_ratio(self, traffic_analyzer):
        """Test recommendation generation for low Observatory ratio"""
        events = [
            TrafficEvent(
                timestamp=datetime.utcnow(),
                ip_address="192.168.1.1",
                user_agent="Observatory-Internal",
                uri_path="/api/data",
                method="GET",
                status_code=200,
                country="US",
                action_taken="allow",
                pattern_type=TrafficPattern.INTERNAL_POLLING
            )
        ]
        
        # Add many non-Observatory events
        for i in range(20):
            events.append(TrafficEvent(
                timestamp=datetime.utcnow(),
                ip_address=f"192.168.1.{i}",
                user_agent="Regular-Browser",
                uri_path="/regular",
                method="GET",
                status_code=200,
                country="US",
                action_taken="allow",
                pattern_type=TrafficPattern.UNKNOWN
            ))
        
        pattern_breakdown = {TrafficPattern.INTERNAL_POLLING: 1, TrafficPattern.UNKNOWN: 20}
        recommendations = traffic_analyzer._generate_recommendations(events, pattern_breakdown)
        
        assert any("Low Observatory traffic ratio" in rec for rec in recommendations)
    
    def test_generate_recommendations_high_ratio(self, traffic_analyzer):
        """Test recommendation generation for high Observatory ratio"""
        events = []
        # Add many Observatory events
        for i in range(20):
            events.append(TrafficEvent(
                timestamp=datetime.utcnow(),
                ip_address=f"192.168.1.{i}",
                user_agent="Observatory-Internal",
                uri_path="/api/data",
                method="GET",
                status_code=200,
                country="US",
                action_taken="allow",
                pattern_type=TrafficPattern.INTERNAL_POLLING
            ))
        
        # Add few non-Observatory events
        events.append(TrafficEvent(
            timestamp=datetime.utcnow(),
            ip_address="192.168.1.100",
            user_agent="Regular-Browser",
            uri_path="/regular",
            method="GET",
            status_code=200,
            country="US",
            action_taken="allow",
            pattern_type=TrafficPattern.UNKNOWN
        ))
        
        pattern_breakdown = {TrafficPattern.INTERNAL_POLLING: 20, TrafficPattern.UNKNOWN: 1}
        recommendations = traffic_analyzer._generate_recommendations(events, pattern_breakdown)
        
        assert any("High Observatory traffic ratio" in rec for rec in recommendations)
    
    @pytest.mark.asyncio
    async def test_analyze_recent_traffic(self, traffic_analyzer, mock_api_client):
        """Test analyzing recent traffic"""
        # Mock security events
        mock_events = [
            {
                "occurred_at": "2023-12-01T10:00:00Z",
                "source": {
                    "ip": "192.168.1.1",
                    "user_agent": "Observatory-Internal",
                    "uri": "/api/data",
                    "method": "GET",
                    "status_code": 200,
                    "country": "US"
                },
                "action": "allow"
            }
        ]
        
        mock_api_client.get_security_events.return_value = mock_events
        
        analysis = await traffic_analyzer.analyze_recent_traffic(hours=24)
        
        assert isinstance(analysis, TrafficAnalysis)
        assert analysis.total_requests == 1
        assert analysis.observatory_requests == 1
        mock_api_client.get_security_events.assert_called_once_with(limit=1000)
    
    @pytest.mark.asyncio
    async def test_analyze_recent_traffic_api_error(self, traffic_analyzer, mock_api_client):
        """Test API error handling in traffic analysis"""
        mock_api_client.get_security_events.side_effect = CloudflareAPIError("API Error")
        
        with pytest.raises(CloudflareAPIError):
            await traffic_analyzer.analyze_recent_traffic(hours=24)
    
    @pytest.mark.asyncio
    async def test_get_observatory_traffic_summary(self, traffic_analyzer, mock_api_client):
        """Test getting Observatory traffic summary"""
        # Mock traffic analysis
        mock_analysis = TrafficAnalysis(
            total_requests=100,
            observatory_requests=20,
            blocked_requests=5,
            pattern_breakdown={TrafficPattern.INTERNAL_POLLING: 10, TrafficPattern.WEBSOCKET_CONNECTION: 10},
            suspicious_activity=[],
            recommendations=["Test recommendation"]
        )
        
        with patch.object(traffic_analyzer, 'analyze_recent_traffic', new_callable=AsyncMock) as mock_analyze:
            mock_analyze.return_value = mock_analysis
            
            summary = await traffic_analyzer.get_observatory_traffic_summary()
            
            assert summary["total_requests_24h"] == 100
            assert summary["observatory_requests_24h"] == 20
            assert summary["blocked_requests_24h"] == 5
            assert summary["pattern_distribution"]["internal_polling"] == 10
            assert summary["pattern_distribution"]["websocket_connection"] == 10
            assert summary["suspicious_activity_count"] == 0
            assert summary["recommendations"] == ["Test recommendation"]
            assert "analysis_timestamp" in summary
    
    @pytest.mark.asyncio
    async def test_monitor_whitelist_effectiveness(self, traffic_analyzer, mock_api_client):
        """Test monitoring whitelist effectiveness"""
        # Mock traffic analysis
        mock_analysis = TrafficAnalysis(
            total_requests=100,
            observatory_requests=50,
            blocked_requests=2,
            pattern_breakdown={TrafficPattern.INTERNAL_POLLING: 25, TrafficPattern.WEBSOCKET_CONNECTION: 25},
            suspicious_activity=[],
            recommendations=[]
        )
        
        with patch.object(traffic_analyzer, 'analyze_recent_traffic', new_callable=AsyncMock) as mock_analyze:
            mock_analyze.return_value = mock_analysis
            
            effectiveness = await traffic_analyzer.monitor_whitelist_effectiveness()
            
            assert effectiveness["total_observatory_requests"] == 50
            assert effectiveness["blocked_observatory_requests"] == 0  # No blocked Observatory traffic
            assert effectiveness["whitelist_success_rate"] == 100.0
            assert effectiveness["false_positive_rate"] == 0.0
            assert effectiveness["monitoring_period"] == "1 hour"
            assert "timestamp" in effectiveness
    
    def test_log_action(self, traffic_analyzer):
        """Test logging functionality"""
        with patch('builtins.print') as mock_print:
            traffic_analyzer._log_action("test_action", "completed", {"test": "data"})
            
            mock_print.assert_called_once()
            # Verify JSON format
            call_args = mock_print.call_args[0][0]
            import json
            log_data = json.loads(call_args)
            
            assert log_data["task"] == "5.1"
            assert log_data["action"] == "test_action"
            assert log_data["status"] == "completed"
            assert log_data["details"] == {"test": "data"}