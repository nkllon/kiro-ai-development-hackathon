#!/usr/bin/env python3
"""
Basic API functionality test for Technical Debt Patch Annotation API.

This test verifies that the API can be instantiated and basic operations work correctly.
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def test_api_instantiation():
    """Test that the API can be instantiated successfully."""
    try:
        from src.technical_debt_patch_annotation.api.patch_api import TechnicalDebtPatchAPI
        
        # Create API instance
        api = TechnicalDebtPatchAPI(host="127.0.0.1", port=8081)
        
        print("✅ API instantiation successful")
        
        # Test module info
        module_info = api.get_module_info()
        print(f"✅ Module info: {module_info['name']} v{module_info['version']}")
        
        # Test capabilities
        capabilities = api.get_capabilities()
        print(f"✅ Capabilities: {[cap.value for cap in capabilities]}")
        
        # Test health status
        health = api.get_health_status()
        print(f"✅ Health status: {health.status.value} (score: {health.health_score})")
        
        # Test graceful degradation
        degradation = api.graceful_degradation()
        print(f"✅ Graceful degradation: {degradation.success}")
        
        return True
        
    except Exception as e:
        print(f"❌ API instantiation failed: {e}")
        return False


def test_patch_operations():
    """Test basic patch operations without starting the server."""
    try:
        from src.technical_debt_patch_annotation.api.patch_api import TechnicalDebtPatchAPI
        from src.technical_debt_patch_annotation.core.models import PatchAnnotation, DebtLevel, BypassType
        
        # Create API instance
        api = TechnicalDebtPatchAPI(host="127.0.0.1", port=8081)
        
        # Create a test patch
        patch = PatchAnnotation(
            reason="Test patch for API validation",
            upstream_issue="TEST-001",
            cleanup_task="Remove this test patch",
            debt_level=DebtLevel.LOW,
            bypass_type=BypassType.ARCHITECTURE,
            component="test_component",
            file_path="test_file.py",
            line_start=1,
            line_end=5,
            validation_criteria=["Test passes"],
            created_by="test@example.com"
        )
        
        # Store patch in API
        api.patches[patch.patch_id] = patch
        
        print(f"✅ Created test patch: {patch.patch_id}")
        
        # Verify patch is stored
        if patch.patch_id in api.patches:
            print("✅ Patch storage successful")
        else:
            print("❌ Patch storage failed")
            return False
        
        # Test patch retrieval
        retrieved_patch = api.patches[patch.patch_id]
        if retrieved_patch.reason == patch.reason:
            print("✅ Patch retrieval successful")
        else:
            print("❌ Patch retrieval failed")
            return False
        
        # Test patch deletion
        del api.patches[patch.patch_id]
        if patch.patch_id not in api.patches:
            print("✅ Patch deletion successful")
        else:
            print("❌ Patch deletion failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Patch operations test failed: {e}")
        return False


def test_webhook_operations():
    """Test basic webhook operations."""
    try:
        from src.technical_debt_patch_annotation.api.patch_api import TechnicalDebtPatchAPI
        
        # Create API instance
        api = TechnicalDebtPatchAPI(host="127.0.0.1", port=8081)
        
        # Create a test webhook
        webhook_id = "test-webhook-001"
        webhook_data = {
            "webhook_id": webhook_id,
            "url": "https://example.com/webhook",
            "events": ["patch.created", "patch.updated"],
            "secret": "test-secret",
            "active": True,
            "created_at": datetime.now(),
            "last_triggered": None
        }
        
        # Store webhook
        api.webhooks[webhook_id] = webhook_data
        
        print(f"✅ Created test webhook: {webhook_id}")
        
        # Verify webhook is stored
        if webhook_id in api.webhooks:
            print("✅ Webhook storage successful")
        else:
            print("❌ Webhook storage failed")
            return False
        
        # Test webhook retrieval
        retrieved_webhook = api.webhooks[webhook_id]
        if retrieved_webhook["url"] == webhook_data["url"]:
            print("✅ Webhook retrieval successful")
        else:
            print("❌ Webhook retrieval failed")
            return False
        
        # Test webhook deletion
        del api.webhooks[webhook_id]
        if webhook_id not in api.webhooks:
            print("✅ Webhook deletion successful")
        else:
            print("❌ Webhook deletion failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Webhook operations test failed: {e}")
        return False


def test_performance_metrics():
    """Test performance metrics collection."""
    try:
        from src.technical_debt_patch_annotation.api.patch_api import TechnicalDebtPatchAPI
        
        # Create API instance
        api = TechnicalDebtPatchAPI(host="127.0.0.1", port=8081)
        
        # Test performance metrics
        metrics = api.get_performance_metrics()
        
        required_metrics = [
            'operation_count', 'total_operation_time_ms', 'average_operation_time_ms',
            'error_count', 'warning_count', 'error_rate', 'uptime_seconds',
            'resource_usage', 'correlation_id', 'traces_stored'
        ]
        
        for metric in required_metrics:
            if metric not in metrics:
                print(f"❌ Missing metric: {metric}")
                return False
        
        print("✅ Performance metrics collection successful")
        
        # Test usage tracking
        usage_data = api.get_usage_tracking()
        
        required_usage_fields = [
            'module_id', 'tracking_period_start', 'tracking_period_end',
            'operation_frequency', 'performance_metrics', 'health_status',
            'capabilities_used'
        ]
        
        for field in required_usage_fields:
            if field not in usage_data:
                print(f"❌ Missing usage tracking field: {field}")
                return False
        
        print("✅ Usage tracking successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance metrics test failed: {e}")
        return False


def test_cli_interface():
    """Test CLI interface generation."""
    try:
        from src.technical_debt_patch_annotation.api.patch_api import TechnicalDebtPatchAPI
        
        # Create API instance
        api = TechnicalDebtPatchAPI(host="127.0.0.1", port=8081)
        
        # Test CLI interface generation
        cli_interface = api.get_cli_interface()
        
        required_fields = ['module_id', 'module_name', 'commands', 'generated_at']
        for field in required_fields:
            if field not in cli_interface:
                print(f"❌ Missing CLI interface field: {field}")
                return False
        
        print(f"✅ CLI interface generated with {len(cli_interface['commands'])} commands")
        
        # Test CLI help generation
        help_text = api.generate_cli_help()
        if "Technical Debt Patch API" in help_text or "TechnicalDebtPatchAPI" in help_text:
            print("✅ CLI help generation successful")
        else:
            print("❌ CLI help generation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ CLI interface test failed: {e}")
        return False


def main():
    """Run all basic API tests."""
    print("🧪 Running Technical Debt Patch Annotation API Basic Tests")
    print("=" * 60)
    
    tests = [
        ("API Instantiation", test_api_instantiation),
        ("Patch Operations", test_patch_operations),
        ("Webhook Operations", test_webhook_operations),
        ("Performance Metrics", test_performance_metrics),
        ("CLI Interface", test_cli_interface)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API implementation is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)