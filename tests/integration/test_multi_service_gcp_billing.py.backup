"""
RDI Enhanced Test Module

Requirements Traceability:

Enhanced: 2025-09-14T06:24:55.711889
"""



import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from beast_mode.billing.gcp_integration import GCPBillingMonitor
from beast_mode.billing.interfaces import BillingProviderType, HealthStatus


class TestMultiServiceGCPBilling:
    """Test suite for multi-service GCP billing integration"""
    
    @pytest.fixture
    def billing_config(self):
        """Standard billing configuration for tests"""
        return {
            'billing_account_id': 'test-account-123',
            'project_ids': ['test-project-1', 'test-project-2'],
            'cache_duration_minutes': 15,
            'cost_attribution': {
                'development': ['beast-mode-dev'],
                'ai_ml': ['systematic-pdca'],
                'networking': ['load-balancer']
            },
            'budget_alerts': {
                'daily_limit_usd': 100.0,
                'hourly_spike_threshold': 10.0
            }
        }
    
    @pytest.fixture
    def gcp_monitor(self, billing_config):
        """GCP billing monitor instance"""
        return GCPBillingMonitor(billing_config)
    
    @pytest.mark.asyncio
    async def test_multi_service_cost_collection(self, gcp_monitor):
        """Test multi-service cost collection includes all services"""
        metrics = await gcp_monitor.collect_billing_metrics()
        
        # Verify provider information
        assert metrics.provider_type == BillingProviderType.GCP
        assert "Multi-Service" in metrics.provider_name
        
        # Verify multi-service cost breakdown
        expected_services = [
            "Cloud Run Requests",
            "Cloud Run CPU", 
            "Cloud Run Memory",
            "Cloud SQL Instance",
            "Cloud SQL Storage",
            "Cloud Storage Data",
            "Cloud Storage Operations",
            "Secret Manager Versions",
            "Secret Manager Access",
            "Networking (Egress)",
            "Container Registry",
            "Cloud Logging"
        ]
        
        for service in expected_services:
            assert service in metrics.cost_breakdown, f"Missing service: {service}"
            assert metrics.cost_breakdown[service] >= 0, f"Negative cost for {service}"
    
    @pytest.mark.asyncio
    async def test_correlation_metrics_calculation(self, gcp_monitor):
        """Test correlation metrics are calculated correctly"""
        metrics = await gcp_monitor.collect_billing_metrics()
        
        # Verify correlation metrics exist
        correlation_metrics = [
            "cost_per_request",
            "cost_per_cpu_second", 
            "cost_per_db_operation",
            "cost_per_storage_operation",
            "cost_per_secret_access"
        ]
        
        for metric in correlation_metrics:
            assert metric in metrics.usage_metrics, f"Missing correlation metric: {metric}"
            assert metrics.usage_metrics[metric] >= 0, f"Negative correlation for {metric}"
        
        # Verify correlation logic
        usage = metrics.usage_metrics
        daily_cost = metrics.daily_cost_usd
        requests = usage["cloud_run_requests"]
        
        # Cost per request should be reasonable
        cost_per_request = usage["cost_per_request"]
        expected_cost_per_request = daily_cost / requests
        assert abs(cost_per_request - expected_cost_per_request) < 0.000001
    
    @pytest.mark.asyncio
    async def test_usage_metrics_completeness(self, gcp_monitor):
        """Test all usage metrics are present and reasonable"""
        metrics = await gcp_monitor.collect_billing_metrics()
        usage = metrics.usage_metrics
        
        # Cloud Run metrics
        assert usage["cloud_run_requests"] > 0
        assert usage["cpu_seconds"] > 0
        assert usage["memory_gb_seconds"] > 0
        assert 0 < usage["avg_request_duration_ms"] < 10000  # Reasonable range
        assert 0 < usage["avg_memory_mb"] < 2048  # Reasonable range
        
        # Cloud SQL metrics
        assert usage["cloud_sql_operations"] > 0
        assert usage["cloud_sql_instance_hours"] == 24  # Always-on
        assert usage["cloud_sql_storage_gb"] > 0
        
        # Cloud Storage metrics
        assert usage["cloud_storage_gb"] > 0
        assert usage["storage_operations"] > 0
        assert usage["class_a_operations"] >= 0
        assert usage["class_b_operations"] >= 0
        
        # Secret Manager metrics
        assert usage["secret_versions"] > 0
        assert usage["secret_access_operations"] > 0
        
        # Networking metrics
        assert usage["avg_response_kb"] > 0
        assert usage["data_transfer_gb"] >= 0
    
    def test_cost_optimization_recommendations(self, gcp_monitor):
        """Test cost optimization recommendations are generated"""
        # First collect metrics to populate cache
        asyncio.run(gcp_monitor.collect_billing_metrics())
        
        recommendations = gcp_monitor.get_cost_optimization_recommendations()
        
        # Should have at least one recommendation
        assert len(recommendations) > 0
        
        # Verify recommendation structure
        for rec in recommendations:
            assert "type" in rec
            assert "priority" in rec
            assert "title" in rec
            assert "description" in rec
            assert "potential_savings_usd" in rec
            assert "action" in rec
            
            # Verify priority levels
            assert rec["priority"] in ["low", "medium", "high"]
            
            # Verify savings are positive
            assert rec["potential_savings_usd"] >= 0
    
    def test_cloud_sql_optimization_recommendations(self, gcp_monitor):
        """Test Cloud SQL specific optimization recommendations"""
        # Mock high SQL costs
        with patch.object(gcp_monitor, '_get_mock_metrics') as mock_metrics:
            mock_result = Mock()
            mock_result.cost_breakdown = {
                "Cloud SQL Instance": 2.0,  # High cost triggers recommendation
                "Cloud SQL Storage": 0.5
            }
            mock_result.usage_metrics = {"cost_per_request": 0.0005}
            mock_result.daily_cost_usd = 10.0
            mock_metrics.return_value = mock_result
            gcp_monitor.cached_metrics = mock_result
            
            recommendations = gcp_monitor.get_cost_optimization_recommendations()
            
            # Should have SQL optimization recommendation
            sql_recs = [r for r in recommendations if "sql" in r["type"].lower()]
            assert len(sql_recs) > 0
            
            sql_rec = sql_recs[0]
            assert sql_rec["priority"] == "high"
            assert "connection pooling" in sql_rec["action"].lower()
    
    def test_storage_optimization_recommendations(self, gcp_monitor):
        """Test Cloud Storage specific optimization recommendations"""
        # Mock high storage operation costs
        with patch.object(gcp_monitor, '_get_mock_metrics') as mock_metrics:
            mock_result = Mock()
            mock_result.cost_breakdown = {
                "Cloud Storage Operations": 0.15  # High operation cost
            }
            mock_result.usage_metrics = {"cost_per_request": 0.0005}
            mock_result.daily_cost_usd = 5.0
            mock_metrics.return_value = mock_result
            gcp_monitor.cached_metrics = mock_result
            
            recommendations = gcp_monitor.get_cost_optimization_recommendations()
            
            # Should have storage optimization recommendation
            storage_recs = [r for r in recommendations if "storage" in r["type"].lower()]
            assert len(storage_recs) > 0
            
            storage_rec = storage_recs[0]
            assert "caching" in storage_rec["action"].lower()
    
    def test_secret_manager_optimization_recommendations(self, gcp_monitor):
        """Test Secret Manager specific optimization recommendations"""
        # Mock high secret access costs
        with patch.object(gcp_monitor, '_get_mock_metrics') as mock_metrics:
            mock_result = Mock()
            mock_result.cost_breakdown = {
                "Secret Manager Access": 0.06  # High access cost
            }
            mock_result.usage_metrics = {"cost_per_request": 0.0005}
            mock_result.daily_cost_usd = 3.0
            mock_metrics.return_value = mock_result
            gcp_monitor.cached_metrics = mock_result
            
            recommendations = gcp_monitor.get_cost_optimization_recommendations()
            
            # Should have secret manager optimization recommendation
            secret_recs = [r for r in recommendations if "secret" in r["type"].lower()]
            assert len(secret_recs) > 0
            
            secret_rec = secret_recs[0]
            assert "caching" in secret_rec["action"].lower()
    
    def test_request_efficiency_optimization(self, gcp_monitor):
        """Test high cost per request optimization recommendations"""
        # Mock high cost per request
        with patch.object(gcp_monitor, '_get_mock_metrics') as mock_metrics:
            mock_result = Mock()
            mock_result.cost_breakdown = {"Cloud Run Requests": 1.0}
            mock_result.usage_metrics = {"cost_per_request": 0.002}  # High cost per request
            mock_result.daily_cost_usd = 20.0
            mock_metrics.return_value = mock_result
            gcp_monitor.cached_metrics = mock_result
            
            recommendations = gcp_monitor.get_cost_optimization_recommendations()
            
            # Should have request efficiency recommendation
            efficiency_recs = [r for r in recommendations if "request_efficiency" in r["type"]]
            assert len(efficiency_recs) > 0
            
            efficiency_rec = efficiency_recs[0]
            assert efficiency_rec["priority"] == "high"
            assert "request caching" in efficiency_rec["action"].lower()
    
    @pytest.mark.asyncio
    async def test_health_status_reporting(self, gcp_monitor):
        """Test health status reporting follows RM pattern"""
        # Test initial health status
        health = gcp_monitor.get_health_status()
        assert isinstance(health, HealthStatus)
        assert health.is_healthy == True
        assert "Initialized" in health.status_message
        
        # Test health after successful collection
        await gcp_monitor.collect_billing_metrics()
        health = gcp_monitor.get_health_status()
        assert health.is_healthy == True
        assert "Successfully collected" in health.status_message
        assert "last_cost" in health.metrics
    
    def test_reflective_module_compliance(self, gcp_monitor):
        """Test ReflectiveModule pattern compliance"""
        # Test get_metrics
        metrics = gcp_monitor.get_metrics()
        assert "integration_mode" in metrics
        assert "openflow_assets_available" in metrics
        assert "cache_valid" in metrics
        
        # Test get_configuration
        config = gcp_monitor.get_configuration()
        assert "integration_mode" in config
        assert "cache_duration_minutes" in config
        
        # Test get_configuration_schema
        schema = gcp_monitor.get_configuration_schema()
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "billing_account_id" in schema["required"]
    
    @pytest.mark.asyncio
    async def test_caching_behavior(self, gcp_monitor):
        """Test caching behavior works correctly"""
        # First call should fetch new data
        metrics1 = await gcp_monitor.collect_billing_metrics()
        assert gcp_monitor.last_update is not None
        
        # Second call should use cache
        metrics2 = await gcp_monitor.collect_billing_metrics()
        assert metrics1.timestamp == metrics2.timestamp  # Same cached data
        
        # Verify cache validity check
        assert gcp_monitor._is_cache_valid() == True
    
    @pytest.mark.asyncio
    async def test_error_handling(self, gcp_monitor):
        """Test error handling and graceful degradation"""
        # Clear cache to force fresh collection
        gcp_monitor.cached_metrics = None
        gcp_monitor.last_update = None
        
        # Mock an error in both collection methods
        with patch.object(gcp_monitor, '_collect_via_gcp_sdk', side_effect=Exception("Test error")), \
             patch.object(gcp_monitor, '_collect_via_openflow_bridge', side_effect=Exception("Test error")):
            
            # Should not raise exception, should return fallback mock data
            metrics = await gcp_monitor.collect_billing_metrics()
            
            # Should still return metrics (fallback mock data)
            assert metrics is not None
            assert metrics.provider_type == BillingProviderType.GCP
            
            # Health status should reflect the error
            health = gcp_monitor.get_health_status()
            assert health.is_healthy == False
            assert "Error collecting metrics" in health.status_message


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])