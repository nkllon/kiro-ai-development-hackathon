# Task 3.2: Tunnel Connectivity Diagnostics

## Ontological Context (22 Dimensions)
- **Problem Taxonomy**: Need diagnostic tools to identify tunnel connectivity issues
- **Infrastructure**: Cloudflare tunnel diagnostic and validation tools
- **Solution Architecture**: Comprehensive tunnel health checking system
- **Operational**: Automated diagnostics reduce manual troubleshooting time

## Task Requirements
Write tunnel health check utilities, implement WebSocket upgrade request validation, create Cloudflare edge server connectivity tests.

**Requirements Coverage**: 5.4, 5.7, 5.8, 7.1, 7.2

## Implementation Instructions

**CRITICAL LOGGING REQUIREMENTS:**
- Log ALL actions in JSON format to stdout
- Use format: `{"timestamp": "ISO8601", "task": "3.2", "action": "description", "status": "in_progress|completed|error", "details": {...}}`
- Final log: `{"task": "3.2", "status": "completed", "summary": "Tunnel diagnostics implemented", "files_created": N, "tests_passed": N}`

## DEFINITION OF DONE - MANDATORY REQUIREMENTS

**Task is NOT complete until ALL of these are verified:**

1. **Files Created and Functional:**
   - `src/beast_mode/observatory/tunnel/diagnostics.py` (>80 lines, working TunnelDiagnostics class)
   - `src/beast_mode/observatory/tunnel/health_checker.py` (>60 lines, working HealthChecker class)
   - `src/beast_mode/observatory/tunnel/websocket_validator.py` (>50 lines, WebSocket upgrade validation)
   - `src/beast_mode/observatory/tunnel/edge_tester.py` (>40 lines, Cloudflare edge connectivity)
   - `tests/unit/tunnel/test_diagnostics.py` (>50 lines, comprehensive tests)
   - `tests/unit/tunnel/test_health_checker.py` (>30 lines, health check tests)

2. **Code Quality Standards:**
   - All classes inherit from ReflectiveModule pattern
   - Comprehensive error handling for network failures
   - Proper async/await patterns throughout
   - Type hints on all methods and parameters
   - Docstrings following Google style

3. **Functional Requirements:**
   - Tunnel health check validates cloudflared process status
   - WebSocket upgrade validation tests HTTP→WebSocket protocol upgrade
   - Edge server connectivity tests multiple Cloudflare locations
   - Diagnostic reports include actionable recommendations
   - All network timeouts and retries properly configured

4. **Integration Requirements:**
   - Integrates with existing tunnel configuration management
   - Uses established logging patterns from other Observatory modules
   - Follows Beast Mode framework patterns
   - No circular imports or dependency issues

5. **Testing Requirements:**
   - Unit tests cover all major code paths
   - Mock external network calls appropriately
   - Test both success and failure scenarios
   - Tests run without external dependencies

**VERIFICATION STEPS:**
1. Run `python -c "from src.beast_mode.observatory.tunnel.diagnostics import TunnelDiagnostics; print('Import successful')"`
2. Run `python -m pytest tests/unit/tunnel/test_diagnostics.py -v`
3. Verify all files exist: `ls -la src/beast_mode/observatory/tunnel/diagnostics.py`
4. Check line counts: `wc -l src/beast_mode/observatory/tunnel/*.py`

**FINAL LOG ENTRY MUST INCLUDE:**
```json
{
  "task": "3.2", 
  "status": "completed", 
  "summary": "Tunnel diagnostics implemented",
  "files_created": 6,
  "total_lines": 300,
  "tests_passed": 15,
  "verification_complete": true
}
```

**Only log completion when ALL requirements are met and verification steps pass.**

Begin implementation of comprehensive tunnel connectivity diagnostics.