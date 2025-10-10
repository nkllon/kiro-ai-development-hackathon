"""
Unit tests for SecurityValidator.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.beast_mode.observatory.cloudflare.security_validator import (
    SecurityValidator, SecurityValidationResult
)
from src.beast_mode.observatory.cloudflare.traffic_analyzer import TrafficPattern
from src.beast_mode.observatory.cloudflare.api_client import CloudflareAPIError


class TestSecurityValidationResult:
    """Test cases for SecurityValidationResult."""
    
    def test_security_validation_result_init(self):
        """Test SecurityValidationResult initialization."""
        result = SecurityValidationResult(
            is_valid=True,
            score=0.9,
            issues=["Issue 1"],
            recommendations=["Recommendation 1"],
            metadata={"key": "value"}
        )
        
        assert result.is_valid is True
        assert result.score == 0.9
        assert result.issues == ["Issue 1"]
        assert result.recommendations == ["Recommendation 1"]
        assert result.metadata == {"key": "value"}
        
    def test_security_validation_result_to_dict(self):
        """Test SecurityValidationResult to_dict method."""
        result = SecurityValidationResult(
            is_valid=False,
            score=0.5,
            issues=["Issue 1", "Issue 2"],
            recommendations=["Recommendation 1"]
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["is_valid"] is False
        assert result_dict["score"] == 0.5
        assert result_dict["issues"] == ["Issue 1", "Issue 2"]
        assert result_dict["recommendations"] == ["Recommendation 1"]
        assert "metadata" in result_dict


class TestSecurityValidator:
    """Test cases for SecurityValidator."""
    
    @pytest.fixture
    def security_validator(self):
        """Create a SecurityValidator instance for testing."""
        mock_api_client = AsyncMock()
        return SecurityValidator(mock_api_client)
        
    @pytest.fixture
    def mock_api_client(self):
        """Mock API client."""
        return AsyncMock()
        
    def test_dangerous_patterns_configured(self, security_validator):
        """Test that dangerous patterns are properly configured."""
        patterns = security_validator.DANGEROUS_PATTERNS
        
        assert len(patterns) >= 4
        assert r".*\*.*" in patterns  # Wildcards
        assert r".*\.\*.*" in patterns  # Domain wildcards
        assert r".*all.*" in patterns  # Overly broad terms
        assert r".*any.*" in patterns  # Overly broad terms
        
    def test_required_security_checks_configured(self, security_validator):
        """Test that required security checks are properly configured."""
        checks = security_validator.REQUIRED_SECURITY_CHECKS
        
        assert len(checks) >= 5
        assert "specific_user_agent" in checks
        assert "specific_path_pattern" in checks
        assert "specific_header_value" in checks
        assert "no_wildcards" in checks
        assert "limited_scope" in checks
        
    @pytest.mark.asyncio
    async def test_validate_whitelist_rule_success(self, security_validator):
        """Test successful whitelist rule validation."""
        pattern = TrafficPattern(
            pattern_type="user_agent",
            expression='(http.user_agent contains "Observatory-Internal")',
            description="Observatory internal polling traffic",
            confidence=1.0
        )
        
        # Mock dependencies
        security_validator.api_client.get_bot_management_config.return_value = {
            "result": {"enable_js": True}
        }
        
        # Test the method
        result = await security_validator.validate_whitelist_rule("zone_123", pattern)
        
        # Verify results
        assert isinstance(result, SecurityValidationResult)
        assert result.is_valid is True
        assert result.score >= 0.7
        assert len(result.issues) == 0
        
    @pytest.mark.asyncio
    async def test_validate_whitelist_rule_invalid_syntax(self, security_validator):
        """Test whitelist rule validation with invalid syntax."""
        pattern = TrafficPattern(
            pattern_type="user_agent",
            expression="invalid syntax",  # Invalid syntax
            description="Test pattern",
            confidence=1.0
        )
        
        # Test the method
        result = await security_validator.validate_whitelist_rule("zone_123", pattern)
        
        # Verify results
        assert isinstance(result, SecurityValidationResult)
        assert result.is_valid is False
        assert result.score < 0.7
        assert len(result.issues) > 0
        
    @pytest.mark.asyncio
    async def test_validate_whitelist_rule_dangerous_patterns(self, security_validator):
        """Test whitelist rule validation with dangerous patterns."""
        pattern = TrafficPattern(
            pattern_type="user_agent",
            expression='(http.user_agent contains "*")',  # Contains wildcard
            description="Test pattern",
            confidence=1.0
        )
        
        # Test the method
        result = await security_validator.validate_whitelist_rule("zone_123", pattern)
        
        # Verify results
        assert isinstance(result, SecurityValidationResult)
        assert result.is_valid is False
        assert result.score < 0.7
        assert any("dangerous" in issue.lower() for issue in result.issues)
        
    @pytest.mark.asyncio
    async def test_validate_whitelist_rule_low_specificity(self, security_validator):
        """Test whitelist rule validation with low specificity."""
        pattern = TrafficPattern(
            pattern_type="user_agent",
            expression='(http.user_agent contains "bot")',  # Too generic
            description="Test pattern",
            confidence=1.0
        )
        
        # Test the method
        result = await security_validator.validate_whitelist_rule("zone_123", pattern)
        
        # Verify results
        assert isinstance(result, SecurityValidationResult)
        assert result.score < 0.7
        assert any("specific" in issue.lower() for issue in result.issues)
        
    @pytest.mark.asyncio
    async def test_validate_whitelist_rule_not_observatory_specific(self, security_validator):
        """Test whitelist rule validation with non-Observatory pattern."""
        pattern = TrafficPattern(
            pattern_type="user_agent",
            expression='(http.user_agent contains "Mozilla")',  # Not Observatory-specific
            description="Test pattern",
            confidence=1.0
        )
        
        # Test the method
        result = await security_validator.validate_whitelist_rule("zone_123", pattern)
        
        # Verify results
        assert isinstance(result, SecurityValidationResult)
        assert result.score < 0.7
        assert any("observatory" in issue.lower() for issue in result.issues)
        
    @pytest.mark.asyncio
    async def test_validate_whitelist_rule_with_existing_rules(self, security_validator):
        """Test whitelist rule validation with existing rules."""
        pattern = TrafficPattern(
            pattern_type="user_agent",
            expression='(http.user_agent contains "Observatory-Internal")',
            description="Observatory internal polling traffic",
            confidence=1.0
        )
        
        existing_rules = [
            {
                "id": "rule_1",
                "filter": {"expression": '(http.user_agent contains "Observatory-Internal")'},
                "action": "allow"
            }
        ]
        
        # Mock dependencies
        security_validator.api_client.get_bot_management_config.return_value = {
            "result": {"enable_js": True}
        }
        
        # Test the method
        result = await security_validator.validate_whitelist_rule("zone_123", pattern, existing_rules)
        
        # Verify results
        assert isinstance(result, SecurityValidationResult)
        assert result.score < 1.0  # Should be reduced due to duplicate
        assert any("duplicate" in issue.lower() for issue in result.issues)
        
    @pytest.mark.asyncio
    async def test_validate_whitelist_rule_exception(self, security_validator):
        """Test whitelist rule validation with exception."""
        pattern = TrafficPattern(
            pattern_type="user_agent",
            expression='(http.user_agent contains "Observatory-Internal")',
            description="Test pattern",
            confidence=1.0
        )
        
        # Mock exception
        security_validator.api_client.get_bot_management_config.side_effect = Exception("Test error")
        
        # Test the method
        result = await security_validator.validate_whitelist_rule("zone_123", pattern)
        
        # Verify results
        assert isinstance(result, SecurityValidationResult)
        assert result.is_valid is False
        assert result.score == 0.0
        assert len(result.issues) > 0
        assert any("error" in issue.lower() for issue in result.issues)
        
    def test_validate_expression_syntax_valid(self, security_validator):
        """Test expression syntax validation with valid expressions."""
        valid_expressions = [
            '(http.user_agent contains "Observatory-Internal")',
            '(http.request.uri.path matches "^/ws/")',
            '(ip.src eq 192.168.1.1)',
            '(cf.threat_score gt 10)',
            '(http.request.headers["x-observatory-client"][0] eq "internal-polling")'
        ]
        
        for expression in valid_expressions:
            assert security_validator._validate_expression_syntax(expression) is True
            
    def test_validate_expression_syntax_invalid(self, security_validator):
        """Test expression syntax validation with invalid expressions."""
        invalid_expressions = [
            "",  # Empty
            None,  # None
            "invalid expression",  # No parentheses
            "(unbalanced parentheses",  # Unbalanced
            "(no http field)",  # No required fields
            "()",  # Empty parentheses
        ]
        
        for expression in invalid_expressions:
            assert security_validator._validate_expression_syntax(expression) is False
            
    def test_contains_dangerous_patterns_true(self, security_validator):
        """Test dangerous pattern detection returning true."""
        dangerous_expressions = [
            '(http.user_agent contains "*")',
            '(http.request.uri.path matches ".*")',
            '(http.user_agent contains "all")',
            '(http.request.uri.path matches "any")'
        ]
        
        for expression in dangerous_expressions:
            assert security_validator._contains_dangerous_patterns(expression) is True
            
    def test_contains_dangerous_patterns_false(self, security_validator):
        """Test dangerous pattern detection returning false."""
        safe_expressions = [
            '(http.user_agent contains "Observatory-Internal")',
            '(http.request.uri.path matches "^/ws/")',
            '(ip.src eq 192.168.1.1)'
        ]
        
        for expression in safe_expressions:
            assert security_validator._contains_dangerous_patterns(expression) is False
            
    def test_check_specificity_high(self, security_validator):
        """Test specificity check with high specificity."""
        pattern = TrafficPattern(
            pattern_type="user_agent",
            expression='(http.user_agent contains "Observatory-Internal")',
            description="Test pattern",
            confidence=1.0
        )
        
        score = security_validator._check_specificity(pattern)
        
        assert score > 0.7  # Should be high specificity
        
    def test_check_specificity_low(self, security_validator):
        """Test specificity check with low specificity."""
        pattern = TrafficPattern(
            pattern_type="user_agent",
            expression='(http.user_agent contains "bot")',  # Too generic
            description="Test pattern",
            confidence=1.0
        )
        
        score = security_validator._check_specificity(pattern)
        
        assert score < 0.7  # Should be low specificity
        
    def test_check_rule_conflicts_no_conflicts(self, security_validator):
        """Test rule conflict check with no conflicts."""
        pattern = TrafficPattern(
            pattern_type="user_agent",
            expression='(http.user_agent contains "Observatory-Internal")',
            description="Test pattern",
            confidence=1.0
        )
        
        existing_rules = [
            {
                "id": "rule_1",
                "filter": {"expression": '(ip.src eq 192.168.1.1)'},
                "action": "block"
            }
        ]
        
        conflicts = security_validator._check_rule_conflicts(pattern, existing_rules)
        
        assert len(conflicts) == 0
        
    def test_check_rule_conflicts_duplicate(self, security_validator):
        """Test rule conflict check with duplicate expression."""
        pattern = TrafficPattern(
            pattern_type="user_agent",
            expression='(http.user_agent contains "Observatory-Internal")',
            description="Test pattern",
            confidence=1.0
        )
        
        existing_rules = [
            {
                "id": "rule_1",
                "filter": {"expression": '(http.user_agent contains "Observatory-Internal")'},
                "action": "allow"
            }
        ]
        
        conflicts = security_validator._check_rule_conflicts(pattern, existing_rules)
        
        assert len(conflicts) > 0
        assert any("duplicate" in conflict.lower() for conflict in conflicts)
        
    def test_check_rule_conflicts_overlap(self, security_validator):
        """Test rule conflict check with overlapping scope."""
        pattern = TrafficPattern(
            pattern_type="user_agent",
            expression='(http.user_agent contains "Observatory-Internal")',
            description="Test pattern",
            confidence=1.0
        )
        
        existing_rules = [
            {
                "id": "rule_1",
                "filter": {"expression": '(http.user_agent contains "Observatory")'},
                "action": "allow"
            }
        ]
        
        conflicts = security_validator._check_rule_conflicts(pattern, existing_rules)
        
        assert len(conflicts) > 0
        assert any("overlap" in conflict.lower() for conflict in conflicts)
        
    def test_rules_overlap_true(self, security_validator):
        """Test rule overlap detection returning true."""
        pattern = TrafficPattern(
            pattern_type="user_agent",
            expression='(http.user_agent contains "Observatory-Internal")',
            description="Test pattern",
            confidence=1.0
        )
        
        rule = {
            "id": "rule_1",
            "filter": {"expression": '(http.user_agent contains "Observatory")'},
            "action": "allow"
        }
        
        assert security_validator._rules_overlap(pattern, rule) is True
        
    def test_rules_overlap_false(self, security_validator):
        """Test rule overlap detection returning false."""
        pattern = TrafficPattern(
            pattern_type="user_agent",
            expression='(http.user_agent contains "Observatory-Internal")',
            description="Test pattern",
            confidence=1.0
        )
        
        rule = {
            "id": "rule_1",
            "filter": {"expression": '(ip.src eq 192.168.1.1)'},
            "action": "block"
        }
        
        assert security_validator._rules_overlap(pattern, rule) is False
        
    @pytest.mark.asyncio
    async def test_check_bot_protection_impact_success(self, security_validator):
        """Test bot protection impact check success."""
        pattern = TrafficPattern(
            pattern_type="user_agent",
            expression='(http.user_agent contains "Observatory-Internal")',
            description="Test pattern",
            confidence=1.0
        )
        
        # Mock bot protection config
        security_validator.api_client.get_bot_management_config.return_value = {
            "result": {"enable_js": True}
        }
        
        # Mock specificity check
        security_validator._check_specificity = MagicMock(return_value=0.9)
        
        # Test the method
        impact = await security_validator._check_bot_protection_impact("zone_123", pattern)
        
        # Verify results
        assert impact >= 0.8  # Should be good impact
        
    @pytest.mark.asyncio
    async def test_check_bot_protection_impact_api_error(self, security_validator):
        """Test bot protection impact check with API error."""
        pattern = TrafficPattern(
            pattern_type="user_agent",
            expression='(http.user_agent contains "Observatory-Internal")',
            description="Test pattern",
            confidence=1.0
        )
        
        # Mock API error
        security_validator.api_client.get_bot_management_config.side_effect = CloudflareAPIError("API Error")
        
        # Test the method
        impact = await security_validator._check_bot_protection_impact("zone_123", pattern)
        
        # Verify results - should return moderate impact
        assert impact == 0.7
        
    def test_is_observatory_specific_true(self, security_validator):
        """Test Observatory specificity check returning true."""
        pattern = TrafficPattern(
            pattern_type="user_agent",
            expression='(http.user_agent contains "Observatory-Internal")',
            description="Test pattern",
            confidence=1.0
        )
        
        assert security_validator._is_observatory_specific(pattern) is True
        
        pattern = TrafficPattern(
            pattern_type="websocket",
            expression='(http.request.uri.path matches "^/ws/")',
            description="Test pattern",
            confidence=1.0
        )
        
        assert security_validator._is_observatory_specific(pattern) is True
        
    def test_is_observatory_specific_false(self, security_validator):
        """Test Observatory specificity check returning false."""
        pattern = TrafficPattern(
            pattern_type="user_agent",
            expression='(http.user_agent contains "Mozilla")',
            description="Test pattern",
            confidence=1.0
        )
        
        assert security_validator._is_observatory_specific(pattern) is False
        
    @pytest.mark.asyncio
    async def test_validate_rule_set_success(self, security_validator):
        """Test successful rule set validation."""
        patterns = [
            TrafficPattern(
                pattern_type="user_agent",
                expression='(http.user_agent contains "Observatory-Internal")',
                description="Test pattern 1",
                confidence=1.0
            ),
            TrafficPattern(
                pattern_type="websocket",
                expression='(http.request.uri.path matches "^/ws/")',
                description="Test pattern 2",
                confidence=1.0
            )
        ]
        
        # Mock individual validation
        security_validator.validate_whitelist_rule = AsyncMock()
        security_validator.validate_whitelist_rule.return_value = SecurityValidationResult(
            is_valid=True,
            score=0.9,
            issues=[],
            recommendations=[]
        )
        
        # Test the method
        result = await security_validator.validate_rule_set("zone_123", patterns)
        
        # Verify results
        assert "overall_score" in result
        assert "individual_results" in result
        assert "total_issues" in result
        assert "total_recommendations" in result
        assert "recommendation" in result
        
        assert result["overall_score"] >= 0.8
        assert len(result["individual_results"]) == 2
        
    @pytest.mark.asyncio
    async def test_audit_security_rules_success(self, security_validator):
        """Test successful security rules audit."""
        # Mock firewall rules
        mock_rules = [
            {"id": "rule_1", "action": "allow", "filter": {"expression": "test"}},
            {"id": "rule_2", "action": "block", "filter": {"expression": "test2"}},
            {"id": "rule_3", "action": "challenge", "filter": {"expression": "test3"}},
            {"id": "rule_4", "action": "allow", "filter": {"expression": "*"}}  # Dangerous
        ]
        
        security_validator.api_client.list_firewall_rules.return_value = {"result": mock_rules}
        
        # Test the method
        result = await security_validator.audit_security_rules("zone_123")
        
        # Verify results
        assert result["total_rules"] == 4
        assert result["allow_rules"] == 2
        assert result["block_rules"] == 1
        assert result["challenge_rules"] == 1
        assert len(result["potential_issues"]) > 0  # Should detect dangerous rule
        
    @pytest.mark.asyncio
    async def test_audit_security_rules_api_error(self, security_validator):
        """Test security rules audit with API error."""
        # Mock API error
        security_validator.api_client.list_firewall_rules.side_effect = CloudflareAPIError("API Error")
        
        # Test the method
        result = await security_validator.audit_security_rules("zone_123")
        
        # Verify results
        assert "error" in result
        assert result["total_rules"] == 0
        assert len(result["potential_issues"]) > 0
        assert len(result["recommendations"]) > 0