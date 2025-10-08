"""
Cloudflare API integration for Dashboard verification.

This module provides Cloudflare API integration to verify:
- WebSocket support configuration
- SSL/TLS settings and certificates
- DNS records and routing configuration
- Domain-specific WebSocket settings

Implements requirements 3.2, 3.4, 3.6 from the WebSocket validation specification.
"""

import os
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional

from ..models import TestResult, TestStatus
from ..config import ValidationConfig
from ..collectors import EvidenceCollector
from ..utils.logging import get_logger, log_test_start, log_test_end
from ..utils.errors import ValidationError


class CloudflareAPITester:
    """
    Cloudflare API integration for Dashboard verification.
    
    Provides automated Cloudflare API integration for configuration checks,
    WebSocket support verification, and SSL/TLS settings validation.
    """
    
    def __init__(self, config: ValidationConfig, evidence_collector: EvidenceCollector):
        """Initialize CloudflareAPITester."""
        self.config = config
        self.evidence_collector = evidence_collector
        self.logger = get_logger(__name__)
        
        # Cloudflare API configuration
        self.api_token = os.getenv('CLOUDFLARE_API_TOKEN')
        self.api_email = os.getenv('CLOUDFLARE_API_EMAIL')
        self.api_key = os.getenv('CLOUDFLARE_API_KEY')
        self.base_url = "https://api.cloudflare.com/client/v4"
        
        # Test domains
        self.test_domains = [
            "nkllon.com",
            "louspringer.com"
        ]
    
    def run_dashboard_verification_tests(self) -> List[TestResult]:
        """
        Run all Cloudflare Dashboard verification tests.
        
        Returns:
            List[TestResult]: Results from Dashboard verification tests
        """
        self.logger.info("Running Cloudflare Dashboard verification tests")
        results = []
        
        # Test 1: Verify API connectivity
        api_test = self._test_api_connectivity()
        results.append(api_test)
        
        if api_test.status == TestStatus.PASSED:
            # Test 2: Verify domain configurations
            for domain in self.test_domains:
                domain_tests = self._verify_domain_configuration(domain)
                results.extend(domain_tests)
        
        self.logger.info(f"Dashboard verification completed: {len(results)} tests run")
        return results
    
    def _test_api_connectivity(self) -> TestResult:
        """Test Cloudflare API connectivity and authentication."""
        test_name = "cloudflare_api_connectivity"
        start_time = datetime.utcnow()
        
        log_test_start(self.logger, test_name, "configuration")
        
        try:
            # Check if API credentials are available
            if not (self.api_token or (self.api_email and self.api_key)):
                raise ValidationError(
                    "API_CREDENTIALS_MISSING",
                    "Cloudflare API credentials not found in environment variables",
                    {"required_vars": ["CLOUDFLARE_API_TOKEN or (CLOUDFLARE_API_EMAIL + CLOUDFLARE_API_KEY)"]}
                )
            
            # Set up headers for API request
            headers = {
                "Content-Type": "application/json"
            }
            
            if self.api_token:
                headers["Authorization"] = f"Bearer {self.api_token}"
            else:
                headers["X-Auth-Email"] = self.api_email
                headers["X-Auth-Key"] = self.api_key
            
            # Test API connectivity with user verification endpoint
            response = requests.get(
                f"{self.base_url}/user/tokens/verify",
                headers=headers,
                timeout=10
            )
            
            api_status = {
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "authenticated": response.status_code == 200
            }
            
            if response.status_code == 200:
                api_data = response.json()
                api_status["success"] = api_data.get("success", False)
                api_status["result"] = api_data.get("result", {})
            
            # Store API test results as evidence
            api_test_data = {
                "api_status": api_status,
                "test_timestamp": datetime.utcnow().isoformat(),
                "credentials_type": "token" if self.api_token else "email_key"
            }
            
            evidence_id = self.evidence_collector.snapshot_configuration(
                config_type="cloudflare_api_test",
                config_data=api_test_data
            )
            
            # Determine test status
            if response.status_code == 200 and api_status.get("authenticated", False):
                status = TestStatus.PASSED
                error_details = None
            else:
                status = TestStatus.FAILED
                error_details = f"API authentication failed: HTTP {response.status_code}"
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            test_result = TestResult(
                test_name=test_name,
                test_category="configuration",
                status=status,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                evidence_ids=[evidence_id],
                metrics={
                    "api_authenticated": api_status.get("authenticated", False),
                    "response_time": api_status["response_time"],
                    "status_code": api_status["status_code"]
                },
                error_details=error_details,
                assertions_passed=1 if status == TestStatus.PASSED else 0,
                assertions_failed=1 if status == TestStatus.FAILED else 0
            )
            
            log_test_end(
                self.logger, test_name, "configuration",
                status.value, execution_time,
                f"API authenticated: {api_status.get('authenticated', False)}"
            )
            
            return test_result
            
        except Exception as e:
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            self.logger.error(f"Cloudflare API connectivity test failed: {e}")
            
            test_result = TestResult(
                test_name=test_name,
                test_category="configuration",
                status=TestStatus.ERROR,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                error_details=str(e),
                assertions_passed=0,
                assertions_failed=1
            )
            
            log_test_end(
                self.logger, test_name, "configuration",
                "ERROR", execution_time, str(e)
            )
            
            return test_result
    
    def _verify_domain_configuration(self, domain: str) -> List[TestResult]:
        """Verify Cloudflare configuration for a specific domain."""
        results = []
        
        # Get zone information for the domain
        zone_result = self._get_zone_info(domain)
        results.append(zone_result)
        
        if zone_result.status == TestStatus.PASSED:
            zone_id = zone_result.metrics.get("zone_id")
            
            if zone_id:
                # Verify WebSocket support settings
                websocket_result = self._verify_websocket_support(domain, zone_id)
                results.append(websocket_result)
                
                # Verify SSL/TLS settings
                ssl_result = self._verify_ssl_settings(domain, zone_id)
                results.append(ssl_result)
                
                # Verify DNS records
                dns_result = self._verify_dns_records(domain, zone_id)
                results.append(dns_result)
        
        return results
    
    def _get_zone_info(self, domain: str) -> TestResult:
        """Get Cloudflare zone information for a domain."""
        test_name = f"zone_info_{domain.replace('.', '_')}"
        start_time = datetime.utcnow()
        
        log_test_start(self.logger, test_name, "configuration")
        
        try:
            # Set up headers for API request
            headers = {
                "Content-Type": "application/json"
            }
            
            if self.api_token:
                headers["Authorization"] = f"Bearer {self.api_token}"
            else:
                headers["X-Auth-Email"] = self.api_email
                headers["X-Auth-Key"] = self.api_key
            
            # Get zone information
            response = requests.get(
                f"{self.base_url}/zones",
                headers=headers,
                params={"name": domain},
                timeout=10
            )
            
            zone_info = {
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds()
            }
            
            if response.status_code == 200:
                api_data = response.json()
                zone_info["success"] = api_data.get("success", False)
                
                if api_data.get("result"):
                    zone = api_data["result"][0]
                    zone_info["zone_id"] = zone.get("id")
                    zone_info["zone_name"] = zone.get("name")
                    zone_info["status"] = zone.get("status")
                    zone_info["name_servers"] = zone.get("name_servers", [])
                else:
                    zone_info["zone_found"] = False
            
            # Store zone info as evidence
            zone_data = {
                "domain": domain,
                "zone_info": zone_info,
                "test_timestamp": datetime.utcnow().isoformat()
            }
            
            evidence_id = self.evidence_collector.snapshot_configuration(
                config_type="cloudflare_zone_info",
                config_data=zone_data
            )
            
            # Determine test status
            if (response.status_code == 200 and 
                zone_info.get("success", False) and 
                zone_info.get("zone_id")):
                status = TestStatus.PASSED
                error_details = None
            else:
                status = TestStatus.FAILED
                error_details = f"Zone not found or API error for domain {domain}"
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            test_result = TestResult(
                test_name=test_name,
                test_category="configuration",
                status=status,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                evidence_ids=[evidence_id],
                metrics={
                    "domain": domain,
                    "zone_id": zone_info.get("zone_id"),
                    "zone_found": zone_info.get("zone_id") is not None,
                    "zone_status": zone_info.get("status"),
                    "response_time": zone_info["response_time"]
                },
                error_details=error_details,
                assertions_passed=1 if status == TestStatus.PASSED else 0,
                assertions_failed=1 if status == TestStatus.FAILED else 0
            )
            
            log_test_end(
                self.logger, test_name, "configuration",
                status.value, execution_time,
                f"Zone found: {zone_info.get('zone_id') is not None}"
            )
            
            return test_result
            
        except Exception as e:
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            self.logger.error(f"Zone info retrieval failed for {domain}: {e}")
            
            test_result = TestResult(
                test_name=test_name,
                test_category="configuration",
                status=TestStatus.ERROR,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                error_details=str(e),
                assertions_passed=0,
                assertions_failed=1
            )
            
            log_test_end(
                self.logger, test_name, "configuration",
                "ERROR", execution_time, str(e)
            )
            
            return test_result
    
    def _verify_websocket_support(self, domain: str, zone_id: str) -> TestResult:
        """Verify WebSocket support is enabled for the domain."""
        test_name = f"websocket_support_{domain.replace('.', '_')}"
        start_time = datetime.utcnow()
        
        log_test_start(self.logger, test_name, "configuration")
        
        try:
            # Set up headers for API request
            headers = {
                "Content-Type": "application/json"
            }
            
            if self.api_token:
                headers["Authorization"] = f"Bearer {self.api_token}"
            else:
                headers["X-Auth-Email"] = self.api_email
                headers["X-Auth-Key"] = self.api_key
            
            # Get WebSocket setting (this is typically enabled by default in Cloudflare)
            # We'll check the zone settings to see if WebSocket is supported
            response = requests.get(
                f"{self.base_url}/zones/{zone_id}/settings/websockets",
                headers=headers,
                timeout=10
            )
            
            websocket_info = {
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds()
            }
            
            if response.status_code == 200:
                api_data = response.json()
                websocket_info["success"] = api_data.get("success", False)
                
                if api_data.get("result"):
                    result = api_data["result"]
                    websocket_info["websocket_enabled"] = result.get("value") == "on"
                    websocket_info["setting_id"] = result.get("id")
                    websocket_info["editable"] = result.get("editable", False)
            
            # Store WebSocket info as evidence
            websocket_data = {
                "domain": domain,
                "zone_id": zone_id,
                "websocket_info": websocket_info,
                "test_timestamp": datetime.utcnow().isoformat()
            }
            
            evidence_id = self.evidence_collector.snapshot_configuration(
                config_type="cloudflare_websocket_support",
                config_data=websocket_data
            )
            
            # Determine test status
            if (response.status_code == 200 and 
                websocket_info.get("success", False) and 
                websocket_info.get("websocket_enabled", False)):
                status = TestStatus.PASSED
                error_details = None
            else:
                status = TestStatus.FAILED
                error_details = f"WebSocket support not enabled for domain {domain}"
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            test_result = TestResult(
                test_name=test_name,
                test_category="configuration",
                status=status,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                evidence_ids=[evidence_id],
                metrics={
                    "domain": domain,
                    "zone_id": zone_id,
                    "websocket_enabled": websocket_info.get("websocket_enabled", False),
                    "setting_editable": websocket_info.get("editable", False),
                    "response_time": websocket_info["response_time"]
                },
                error_details=error_details,
                assertions_passed=1 if status == TestStatus.PASSED else 0,
                assertions_failed=1 if status == TestStatus.FAILED else 0
            )
            
            log_test_end(
                self.logger, test_name, "configuration",
                status.value, execution_time,
                f"WebSocket enabled: {websocket_info.get('websocket_enabled', False)}"
            )
            
            return test_result
            
        except Exception as e:
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            self.logger.error(f"WebSocket support verification failed for {domain}: {e}")
            
            test_result = TestResult(
                test_name=test_name,
                test_category="configuration",
                status=TestStatus.ERROR,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                error_details=str(e),
                assertions_passed=0,
                assertions_failed=1
            )
            
            log_test_end(
                self.logger, test_name, "configuration",
                "ERROR", execution_time, str(e)
            )
            
            return test_result
    
    def _verify_ssl_settings(self, domain: str, zone_id: str) -> TestResult:
        """Verify SSL/TLS settings for the domain."""
        test_name = f"ssl_settings_{domain.replace('.', '_')}"
        start_time = datetime.utcnow()
        
        log_test_start(self.logger, test_name, "configuration")
        
        try:
            # Set up headers for API request
            headers = {
                "Content-Type": "application/json"
            }
            
            if self.api_token:
                headers["Authorization"] = f"Bearer {self.api_token}"
            else:
                headers["X-Auth-Email"] = self.api_email
                headers["X-Auth-Key"] = self.api_key
            
            # Get SSL/TLS settings
            response = requests.get(
                f"{self.base_url}/zones/{zone_id}/settings/ssl",
                headers=headers,
                timeout=10
            )
            
            ssl_info = {
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds()
            }
            
            if response.status_code == 200:
                api_data = response.json()
                ssl_info["success"] = api_data.get("success", False)
                
                if api_data.get("result"):
                    result = api_data["result"]
                    ssl_info["ssl_mode"] = result.get("value")
                    ssl_info["setting_id"] = result.get("id")
                    ssl_info["editable"] = result.get("editable", False)
            
            # Store SSL info as evidence
            ssl_data = {
                "domain": domain,
                "zone_id": zone_id,
                "ssl_info": ssl_info,
                "test_timestamp": datetime.utcnow().isoformat()
            }
            
            evidence_id = self.evidence_collector.snapshot_configuration(
                config_type="cloudflare_ssl_settings",
                config_data=ssl_data
            )
            
            # Determine test status
            ssl_mode = ssl_info.get("ssl_mode", "")
            ssl_enabled = ssl_mode in ["flexible", "full", "full_strict"]
            
            if (response.status_code == 200 and 
                ssl_info.get("success", False) and 
                ssl_enabled):
                status = TestStatus.PASSED
                error_details = None
            else:
                status = TestStatus.FAILED
                error_details = f"SSL/TLS not properly configured for domain {domain}"
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            test_result = TestResult(
                test_name=test_name,
                test_category="configuration",
                status=status,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                evidence_ids=[evidence_id],
                metrics={
                    "domain": domain,
                    "zone_id": zone_id,
                    "ssl_mode": ssl_mode,
                    "ssl_enabled": ssl_enabled,
                    "setting_editable": ssl_info.get("editable", False),
                    "response_time": ssl_info["response_time"]
                },
                error_details=error_details,
                assertions_passed=1 if status == TestStatus.PASSED else 0,
                assertions_failed=1 if status == TestStatus.FAILED else 0
            )
            
            log_test_end(
                self.logger, test_name, "configuration",
                status.value, execution_time,
                f"SSL mode: {ssl_mode}"
            )
            
            return test_result
            
        except Exception as e:
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            self.logger.error(f"SSL settings verification failed for {domain}: {e}")
            
            test_result = TestResult(
                test_name=test_name,
                test_category="configuration",
                status=TestStatus.ERROR,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                error_details=str(e),
                assertions_passed=0,
                assertions_failed=1
            )
            
            log_test_end(
                self.logger, test_name, "configuration",
                "ERROR", execution_time, str(e)
            )
            
            return test_result
    
    def _verify_dns_records(self, domain: str, zone_id: str) -> TestResult:
        """Verify DNS records for the domain."""
        test_name = f"dns_records_{domain.replace('.', '_')}"
        start_time = datetime.utcnow()
        
        log_test_start(self.logger, test_name, "configuration")
        
        try:
            # Set up headers for API request
            headers = {
                "Content-Type": "application/json"
            }
            
            if self.api_token:
                headers["Authorization"] = f"Bearer {self.api_token}"
            else:
                headers["X-Auth-Email"] = self.api_email
                headers["X-Auth-Key"] = self.api_key
            
            # Get DNS records
            response = requests.get(
                f"{self.base_url}/zones/{zone_id}/dns_records",
                headers=headers,
                timeout=10
            )
            
            dns_info = {
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds()
            }
            
            if response.status_code == 200:
                api_data = response.json()
                dns_info["success"] = api_data.get("success", False)
                
                if api_data.get("result"):
                    records = api_data["result"]
                    dns_info["total_records"] = len(records)
                    
                    # Categorize records by type
                    record_types = {}
                    for record in records:
                        record_type = record.get("type", "unknown")
                        if record_type not in record_types:
                            record_types[record_type] = 0
                        record_types[record_type] += 1
                    
                    dns_info["record_types"] = record_types
                    dns_info["has_a_records"] = "A" in record_types
                    dns_info["has_cname_records"] = "CNAME" in record_types
            
            # Store DNS info as evidence
            dns_data = {
                "domain": domain,
                "zone_id": zone_id,
                "dns_info": dns_info,
                "test_timestamp": datetime.utcnow().isoformat()
            }
            
            evidence_id = self.evidence_collector.snapshot_configuration(
                config_type="cloudflare_dns_records",
                config_data=dns_data
            )
            
            # Determine test status
            if (response.status_code == 200 and 
                dns_info.get("success", False) and 
                dns_info.get("total_records", 0) > 0):
                status = TestStatus.PASSED
                error_details = None
            else:
                status = TestStatus.FAILED
                error_details = f"No DNS records found for domain {domain}"
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            test_result = TestResult(
                test_name=test_name,
                test_category="configuration",
                status=status,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                evidence_ids=[evidence_id],
                metrics={
                    "domain": domain,
                    "zone_id": zone_id,
                    "total_records": dns_info.get("total_records", 0),
                    "has_a_records": dns_info.get("has_a_records", False),
                    "has_cname_records": dns_info.get("has_cname_records", False),
                    "record_types": len(dns_info.get("record_types", {})),
                    "response_time": dns_info["response_time"]
                },
                error_details=error_details,
                assertions_passed=1 if status == TestStatus.PASSED else 0,
                assertions_failed=1 if status == TestStatus.FAILED else 0
            )
            
            log_test_end(
                self.logger, test_name, "configuration",
                status.value, execution_time,
                f"DNS records: {dns_info.get('total_records', 0)}"
            )
            
            return test_result
            
        except Exception as e:
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            self.logger.error(f"DNS records verification failed for {domain}: {e}")
            
            test_result = TestResult(
                test_name=test_name,
                test_category="configuration",
                status=TestStatus.ERROR,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                error_details=str(e),
                assertions_passed=0,
                assertions_failed=1
            )
            
            log_test_end(
                self.logger, test_name, "configuration",
                "ERROR", execution_time, str(e)
            )
            
            return test_result