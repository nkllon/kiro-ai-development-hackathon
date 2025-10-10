"""
Integration tests for production endpoint validation.

These tests will actually connect to the production endpoints to validate
or refute the WebSocket Implementation Gap Analysis claims.
"""

import pytest
import asyncio
from pathlib import Path

from src.websocket_validation.config import ValidationConfig
from src.websocket_validation.collectors import EvidenceCollector
from src.websocket_validation.testers.system_state import SystemStateTester
from src.websocket_validation.models import TestStatus


class TestProductionEndpoints:
    """Integration tests for production WebSocket endpoints."""
    
    @pytest.fixture
    def config(self, tmp_path):
        """Create test configuration for production testing."""
        return ValidationConfig(
            production_base_url="https://observatory.nkllon.com",
            local_base_url="http://localhost:8888",
            websocket_endpoints=["/ws/emoji-rain", "/ws/status", "/ws/health"],
            connection_timeout=30.0,
            websocket_timeout=10.0,
            evidence_dir=tmp_path / "integration_evidence",
            verify_ssl=True
        )
    
    @pytest.fixture
    def evidence_collector(self, config):
        """Create evidence collector for integration tests."""
        return EvidenceCollector(config)
    
    @pytest.fixture
    def system_tester(self, config, evidence_collector):
        """Create SystemStateTester for integration tests."""
        return SystemStateTester(config, evidence_collector)
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_production_websocket_endpoints_exist(self, system_tester):
        """
        Test that production WebSocket endpoints exist and respond.
        
        This is the critical test that will validate or refute the gap analysis
        claim that WebSocket endpoints return HTTP 404 errors.
        """
        results = await system_tester.test_production_endpoints()
        
        # Filter to WebSocket endpoint results only
        websocket_results = [
            r for r in results 
            if "wss://" in r.metrics.get("url", "") or "wss://" in r.metrics.get("endpoint_url", "")
        ]
        
        assert len(websocket_results) > 0, "No WebSocket endpoint tests were executed"
        
        # Analyze results to determine if gap analysis claims are accurate
        failed_with_404 = []
        failed_with_400 = []
        successful_connections = []
        other_failures = []
        
        for result in websocket_results:
            if result.status == TestStatus.PASSED:
                successful_connections.append(result)
            elif result.status == TestStatus.FAILED:
                status_code = result.metrics.get("status_code", 0)
                if status_code == 404:
                    failed_with_404.append(result)
                elif status_code == 400:
                    failed_with_400.append(result)
                else:
                    other_failures.append(result)
        
        # Generate evidence-based assessment
        total_tests = len(websocket_results)
        gap_analysis_supporting_failures = len(failed_with_404) + len(failed_with_400)
        
        print(f"\n=== PRODUCTION WEBSOCKET ENDPOINT VALIDATION RESULTS ===")
        print(f"Total WebSocket endpoint tests: {total_tests}")
        print(f"Successful connections: {len(successful_connections)}")
        print(f"Failed with HTTP 404 (gap analysis claim): {len(failed_with_404)}")
        print(f"Failed with HTTP 400 (gap analysis claim): {len(failed_with_400)}")
        print(f"Other failures: {len(other_failures)}")
        
        if successful_connections:
            print(f"\n🔍 GAP ANALYSIS ASSESSMENT: CLAIMS REFUTED")
            print(f"Evidence: {len(successful_connections)} WebSocket endpoints are functional")
            print("The gap analysis claim of 'HTTP/2 404' errors is INCORRECT")
        elif gap_analysis_supporting_failures == total_tests:
            print(f"\n🔍 GAP ANALYSIS ASSESSMENT: CLAIMS VALIDATED")
            print(f"Evidence: All {total_tests} WebSocket endpoints return 404/400 errors")
            print("The gap analysis claim of implementation theater is CORRECT")
        else:
            print(f"\n🔍 GAP ANALYSIS ASSESSMENT: MIXED RESULTS")
            print(f"Evidence: Partial implementation detected")
        
        # The test doesn't assert success/failure - it collects evidence
        # The actual validation/refutation is determined by the evidence
        
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_local_websocket_endpoints_exist(self, system_tester):
        """
        Test that local WebSocket endpoints exist and respond.
        
        This tests the local development server to determine if WebSocket
        endpoints are implemented at the code level.
        """
        results = await system_tester.test_local_endpoints()
        
        # Filter to WebSocket endpoint results only
        websocket_results = [
            r for r in results 
            if "ws://" in r.metrics.get("url", "") or "ws://" in r.metrics.get("endpoint_url", "")
        ]
        
        assert len(websocket_results) > 0, "No local WebSocket endpoint tests were executed"
        
        # Analyze results
        failed_with_404 = []
        failed_with_400 = []
        successful_connections = []
        connection_refused = []
        other_failures = []
        
        for result in websocket_results:
            if result.status == TestStatus.PASSED:
                successful_connections.append(result)
            elif result.status == TestStatus.FAILED:
                status_code = result.metrics.get("status_code", 0)
                if status_code == 404:
                    failed_with_404.append(result)
                elif status_code == 400:
                    failed_with_400.append(result)
                else:
                    other_failures.append(result)
            elif result.status == TestStatus.ERROR:
                if "connection refused" in result.error_details.lower():
                    connection_refused.append(result)
                else:
                    other_failures.append(result)
        
        total_tests = len(websocket_results)
        
        print(f"\n=== LOCAL WEBSOCKET ENDPOINT VALIDATION RESULTS ===")
        print(f"Total local WebSocket endpoint tests: {total_tests}")
        print(f"Successful connections: {len(successful_connections)}")
        print(f"Failed with HTTP 404: {len(failed_with_404)}")
        print(f"Failed with HTTP 400: {len(failed_with_400)}")
        print(f"Connection refused (server not running): {len(connection_refused)}")
        print(f"Other failures: {len(other_failures)}")
        
        if successful_connections:
            print(f"\n🔍 LOCAL IMPLEMENTATION ASSESSMENT: WEBSOCKETS IMPLEMENTED")
            print(f"Evidence: {len(successful_connections)} local WebSocket endpoints are functional")
        elif connection_refused:
            print(f"\n🔍 LOCAL IMPLEMENTATION ASSESSMENT: SERVER NOT RUNNING")
            print(f"Evidence: Local server is not running (expected for this test)")
        elif failed_with_404 or failed_with_400:
            print(f"\n🔍 LOCAL IMPLEMENTATION ASSESSMENT: WEBSOCKETS NOT IMPLEMENTED")
            print(f"Evidence: WebSocket endpoints return 404/400 errors even locally")
        
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_websocket_handshake_validation(self, system_tester):
        """
        Test WebSocket handshake process specifically.
        
        This tests the HTTP upgrade request that should result in
        HTTP/1.1 101 Switching Protocols for functional WebSocket endpoints.
        """
        # We'll implement this in the next subtask
        pass
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_evidence_collection_completeness(self, system_tester, evidence_collector):
        """
        Test that comprehensive evidence is collected during validation.
        
        This ensures that the validation framework provides objective,
        verifiable evidence for all claims.
        """
        # Run a subset of tests
        results = await system_tester.test_production_endpoints()
        
        # Verify evidence was collected
        evidence_summary = evidence_collector.generate_summary()
        
        assert evidence_summary["total_items"] > 0, "No evidence was collected"
        assert evidence_summary["by_type"]["http_response"] > 0, "No HTTP response evidence collected"
        
        # Verify evidence integrity
        assert evidence_summary["integrity_verified"], "Evidence integrity verification failed"
        
        print(f"\n=== EVIDENCE COLLECTION VALIDATION ===")
        print(f"Total evidence items collected: {evidence_summary['total_items']}")
        print(f"Evidence types: {list(evidence_summary['by_type'].keys())}")
        print(f"Evidence integrity verified: {evidence_summary['integrity_verified']}")
        print(f"Total evidence size: {evidence_summary['total_size']} bytes")
        
        # This validates that the framework provides objective evidence
        # rather than just subjective assessments