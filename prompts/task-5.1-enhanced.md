# Task 5.1: Cloudflare Bot Protection Integration

## Ontological Context (22 Dimensions)
- **Problem Taxonomy**: Observatory traffic triggers Cloudflare bot protection (Error 1033)
- **Security**: Whitelist legitimate traffic while maintaining protection
- **Vendor Management**: Cloudflare API integration for rule management
- **Risk Assessment**: Changes must not compromise security posture
- **Compliance**: Maintain audit trail of security rule changes
- **Cost**: Use existing Cloudflare plan features, no additional costs

## Task Requirements
Write CloudflareWhitelistManager class for API integration, implement Observatory traffic pattern whitelisting, create rate limiting exception management.

**Requirements Coverage**: 4.1, 4.2, 4.3, 4.4, 4.5

## Implementation Instructions

**CRITICAL LOGGING REQUIREMENTS:**
- Log ALL actions in JSON format to stdout
- Use format: `{"timestamp": "ISO8601", "task": "5.1", "action": "description", "status": "in_progress|completed|error", "details": {...}}`
- Log all Cloudflare API calls, rule changes, whitelist updates
- Final log: `{"task": "5.1", "status": "completed", "summary": "Cloudflare integration implemented"}`

**File Structure to Create:**
```
src/beast_mode/observatory/cloudflare/
├── __init__.py
├── whitelist_manager.py
├── api_client.py
├── rule_manager.py
├── traffic_analyzer.py
└── security_validator.py

tests/unit/cloudflare/
├── test_whitelist_manager.py
├── test_api_client.py
├── test_rule_manager.py
└── test_traffic_analyzer.py
```

**Core Implementation:**

```python
class CloudflareWhitelistManager:
    def __init__(self, api_token: str, zone_id: str):
        self.api_client = CloudflareAPIClient(api_token)
        self.zone_id = zone_id
        self.rule_manager = RuleManager(self.api_client)
        
    async def whitelist_observatory_patterns(self) -> List[str]
    async def create_rate_limit_exception(self) -> str
    async def validate_security_rules(self) -> bool
    async def get_bot_protection_events(self) -> List[Dict]
```

**Whitelist Rules to Create:**
```python
OBSERVATORY_WHITELIST_RULES = [
    {
        "expression": '(http.user_agent contains "Observatory-Internal")',
        "action": "allow",
        "description": "Observatory internal polling traffic"
    },
    {
        "expression": '(http.request.uri.path matches "^/ws/")',
        "action": "allow", 
        "description": "Observatory WebSocket endpoints"
    },
    {
        "expression": '(http.request.headers["x-observatory-client"][0] eq "internal-polling")',
        "action": "allow",
        "description": "Observatory polling fallback"
    }
]
```

**Rate Limiting Exceptions:**
- Observatory origin IP whitelist
- WebSocket upgrade requests
- Internal polling patterns
- Health check endpoints

**Security Validation:**
- Ensure whitelist rules are specific to Observatory
- Validate that general bot protection remains active
- Test that actual attacks are still blocked
- Monitor for abuse of whitelisted patterns

**API Integration:**
- Cloudflare API v4 for rule management
- Zone-level firewall rules
- Rate limiting rule exceptions
- Bot management configuration

**Error Handling:**
- API rate limiting and retries
- Authentication failures
- Rule validation errors
- Rollback procedures for failed changes

Begin implementation with careful security validation and comprehensive API error handling.