#!/usr/bin/env python3
"""
Example usage of the Technical Debt Patch Annotation API.

This script demonstrates how to use the API for common operations:
- Creating patches
- Scanning files for patches
- Setting up webhooks
- Generating reports
"""

import sys
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


async def demonstrate_api_usage():
    """Demonstrate comprehensive API usage."""
    from src.technical_debt_patch_annotation.api.patch_api import TechnicalDebtPatchAPI
    from src.technical_debt_patch_annotation.core.models import PatchAnnotation, DebtLevel, BypassType
    
    print("🚀 Technical Debt Patch Annotation API Usage Demonstration")
    print("=" * 60)
    
    # Create API instance
    api = TechnicalDebtPatchAPI(host="127.0.0.1", port=8082)
    print(f"✅ Created API instance: {api.get_module_info()['name']}")
    
    # 1. Create sample patches
    print("\n📝 Creating sample patches...")
    
    patches_data = [
        {
            "reason": "Temporary workaround for upstream API rate limiting",
            "upstream_issue": "API-ISSUE-456",
            "cleanup_task": "Replace with proper retry mechanism when API v2 available",
            "debt_level": DebtLevel.MEDIUM,
            "bypass_type": BypassType.ARCHITECTURE,
            "component": "data_processor",
            "file_path": "src/data/processor.py",
            "line_start": 45,
            "line_end": 48,
            "expected_resolution": datetime.now() + timedelta(days=30),
            "validation_criteria": ["API v2 integration tests pass", "Rate limiting removed"],
            "created_by": "developer@example.com",
            "assigned_to": "team-lead@example.com",
            "tags": ["api", "rate-limiting"]
        },
        {
            "reason": "Critical security bypass for authentication",
            "upstream_issue": "SEC-001",
            "cleanup_task": "Apply proper authentication mechanism",
            "debt_level": DebtLevel.CRITICAL,
            "bypass_type": BypassType.SECURITY,
            "component": "auth_service",
            "file_path": "src/auth/service.py",
            "line_start": 120,
            "line_end": 125,
            "expected_resolution": datetime.now() + timedelta(days=7),
            "validation_criteria": ["Security audit passes", "Authentication tests pass"],
            "created_by": "security@example.com",
            "assigned_to": "security-lead@example.com",
            "tags": ["security", "critical"]
        },
        {
            "reason": "Performance optimization needed for database queries",
            "upstream_issue": "PERF-001",
            "cleanup_task": "Optimize database queries and add proper indexing",
            "debt_level": DebtLevel.HIGH,
            "bypass_type": BypassType.PERFORMANCE,
            "component": "database_service",
            "file_path": "src/db/queries.py",
            "line_start": 200,
            "line_end": 210,
            "expected_resolution": datetime.now() + timedelta(days=14),
            "validation_criteria": ["Query performance benchmarks pass", "Database load tests pass"],
            "created_by": "perf-team@example.com",
            "assigned_to": "db-admin@example.com",
            "tags": ["performance", "database"]
        }
    ]
    
    created_patches = []
    for patch_data in patches_data:
        patch = PatchAnnotation(**patch_data)
        api.patches[patch.patch_id] = patch
        created_patches.append(patch)
        print(f"  ✅ Created patch {patch.patch_id} ({patch.debt_level.value} priority)")
    
    # 2. Demonstrate patch retrieval and filtering
    print(f"\n🔍 Patch retrieval and filtering...")
    
    # Get all patches
    all_patches = list(api.patches.values())
    print(f"  📊 Total patches: {len(all_patches)}")
    
    # Filter by debt level
    critical_patches = [p for p in all_patches if p.debt_level == DebtLevel.CRITICAL]
    print(f"  🚨 Critical patches: {len(critical_patches)}")
    
    # Filter by component
    auth_patches = [p for p in all_patches if p.component == "auth_service"]
    print(f"  🔐 Auth service patches: {len(auth_patches)}")
    
    # 3. Set up webhooks
    print(f"\n🔗 Setting up webhooks...")
    
    webhooks_data = [
        {
            "webhook_id": "cicd-webhook",
            "url": "https://ci-system.example.com/webhooks/patches",
            "events": ["patch.created", "patch.updated", "patches.discovered"],
            "secret": "cicd-webhook-secret",
            "active": True,
            "created_at": datetime.now(),
            "last_triggered": None
        },
        {
            "webhook_id": "monitoring-webhook",
            "url": "https://monitoring.example.com/webhooks/patches",
            "events": ["patch.created", "patch.deleted"],
            "secret": "monitoring-webhook-secret",
            "active": True,
            "created_at": datetime.now(),
            "last_triggered": None
        }
    ]
    
    for webhook_data in webhooks_data:
        api.webhooks[webhook_data["webhook_id"]] = webhook_data
        print(f"  ✅ Registered webhook: {webhook_data['webhook_id']}")
    
    # 4. Simulate webhook triggering
    print(f"\n📡 Simulating webhook triggers...")
    
    # Trigger webhooks for patch creation
    await api._trigger_webhooks("patch.created", {
        "patch": {
            "patch_id": created_patches[0].patch_id,
            "component": created_patches[0].component,
            "debt_level": created_patches[0].debt_level.value
        }
    })
    print("  ✅ Triggered patch.created webhooks")
    
    # 5. Generate comprehensive reports
    print(f"\n📊 Generating comprehensive reports...")
    
    # Basic statistics report
    def generate_statistics_report():
        patches = list(api.patches.values())
        
        # Debt level distribution
        debt_levels = {}
        for patch in patches:
            level = patch.debt_level.value
            debt_levels[level] = debt_levels.get(level, 0) + 1
        
        # Component distribution
        components = {}
        for patch in patches:
            comp = patch.component
            components[comp] = components.get(comp, 0) + 1
        
        # Overdue patches
        now = datetime.now()
        overdue = [p for p in patches if p.expected_resolution and p.expected_resolution < now]
        
        return {
            "total_patches": len(patches),
            "debt_level_distribution": debt_levels,
            "component_distribution": components,
            "overdue_patches": len(overdue),
            "overdue_details": [
                {
                    "patch_id": p.patch_id,
                    "component": p.component,
                    "days_overdue": (now - p.expected_resolution).days
                }
                for p in overdue
            ]
        }
    
    stats_report = generate_statistics_report()
    print(f"  📈 Statistics Report:")
    print(f"    - Total patches: {stats_report['total_patches']}")
    print(f"    - Debt levels: {stats_report['debt_level_distribution']}")
    print(f"    - Components: {stats_report['component_distribution']}")
    print(f"    - Overdue patches: {stats_report['overdue_patches']}")
    
    # Component-specific report
    def generate_component_report(component_name: str):
        patches = [p for p in api.patches.values() if p.component == component_name]
        
        if not patches:
            return {"error": f"No patches found for component: {component_name}"}
        
        total_patches = len(patches)
        debt_levels = {}
        for patch in patches:
            level = patch.debt_level.value
            debt_levels[level] = debt_levels.get(level, 0) + 1
        
        return {
            "component": component_name,
            "total_patches": total_patches,
            "debt_level_distribution": debt_levels,
            "patches": [
                {
                    "patch_id": p.patch_id,
                    "reason": p.reason,
                    "debt_level": p.debt_level.value,
                    "assigned_to": p.assigned_to
                }
                for p in patches
            ]
        }
    
    auth_report = generate_component_report("auth_service")
    print(f"  🔐 Auth Service Report:")
    print(f"    - Patches: {auth_report['total_patches']}")
    print(f"    - Debt levels: {auth_report['debt_level_distribution']}")
    
    # 6. Demonstrate cleanup validation
    print(f"\n🧹 Demonstrating cleanup validation...")
    
    # Select a patch for cleanup validation
    test_patch = created_patches[0]
    
    def validate_cleanup(patch_id: str, completed_criteria: list):
        if patch_id not in api.patches:
            return {"error": "Patch not found"}
        
        patch = api.patches[patch_id]
        required_criteria = patch.validation_criteria
        
        all_met = all(criterion in completed_criteria for criterion in required_criteria)
        
        return {
            "patch_id": patch_id,
            "required_criteria": required_criteria,
            "completed_criteria": completed_criteria,
            "all_criteria_met": all_met,
            "ready_for_removal": all_met,
            "missing_criteria": [c for c in required_criteria if c not in completed_criteria]
        }
    
    # Test incomplete cleanup
    incomplete_validation = validate_cleanup(test_patch.patch_id, ["API v2 integration tests pass"])
    print(f"  ⏳ Incomplete cleanup validation:")
    print(f"    - Ready for removal: {incomplete_validation['ready_for_removal']}")
    print(f"    - Missing criteria: {incomplete_validation['missing_criteria']}")
    
    # Test complete cleanup
    complete_validation = validate_cleanup(test_patch.patch_id, test_patch.validation_criteria)
    print(f"  ✅ Complete cleanup validation:")
    print(f"    - Ready for removal: {complete_validation['ready_for_removal']}")
    print(f"    - All criteria met: {complete_validation['all_criteria_met']}")
    
    # 7. Health and monitoring
    print(f"\n🏥 Health and monitoring information...")
    
    health = api.get_health_status()
    print(f"  💚 Health Status: {health.status.value} (score: {health.health_score})")
    print(f"  ⏱️  Uptime: {health.uptime_seconds:.1f} seconds")
    
    metrics = api.get_performance_metrics()
    print(f"  📊 Performance Metrics:")
    print(f"    - Operations: {metrics['operation_count']}")
    print(f"    - Errors: {metrics['error_count']}")
    print(f"    - Average operation time: {metrics['average_operation_time_ms']:.2f}ms")
    
    # 8. CLI interface demonstration
    print(f"\n💻 CLI interface capabilities...")
    
    cli_interface = api.get_cli_interface()
    print(f"  🔧 Available CLI commands: {len(cli_interface['commands'])}")
    
    # Show a few example commands
    example_commands = list(cli_interface['commands'].keys())[:5]
    for cmd in example_commands:
        cmd_info = cli_interface['commands'][cmd]
        print(f"    - {cmd}: {cmd_info['description'][:50]}...")
    
    print(f"\n🎉 API demonstration completed successfully!")
    print(f"📊 Final Statistics:")
    print(f"  - Patches created: {len(created_patches)}")
    print(f"  - Webhooks registered: {len(api.webhooks)}")
    print(f"  - Health score: {api.get_health_status().health_score}")
    print(f"  - API capabilities: {[cap.value for cap in api.get_capabilities()]}")


def demonstrate_file_scanning():
    """Demonstrate file scanning capabilities."""
    import tempfile
    import os
    
    print("\n🔍 File Scanning Demonstration")
    print("-" * 40)
    
    # Create sample files with patch annotations
    sample_files = {
        "processor.py": '''
def process_data(data):
    """
    PATCH_START: PATCH-SCAN001
    REASON: Temporary workaround for upstream API rate limiting
    UPSTREAM: API-ISSUE-456
    CLEANUP: Replace with proper retry mechanism when API v2 available
    DEBT_LEVEL: Medium
    EXPECTED_RESOLUTION: 2024-03-15T00:00:00
    COMPONENT: data_processor
    BYPASS_TYPE: Architecture
    VALIDATION: ["API v2 integration tests pass", "Rate limiting removed"]
    PATCH_END: PATCH-SCAN001
    """
    # Temporary rate limiting workaround
    time.sleep(0.5)  # PATCH: Remove when API v2 deployed
    return api_client.fetch_data(data)
        ''',
        "auth.py": '''
def authenticate_user(token):
    """
    PATCH_START: PATCH-SCAN002
    REASON: Bypass authentication for testing
    UPSTREAM: AUTH-TEST-001
    CLEANUP: Remove test bypass and implement proper auth
    DEBT_LEVEL: Critical
    EXPECTED_RESOLUTION: 2024-02-01T00:00:00
    COMPONENT: auth_service
    BYPASS_TYPE: Security
    VALIDATION: ["All auth tests pass", "Security audit complete"]
    PATCH_END: PATCH-SCAN002
    """
    if token == "test-bypass":  # PATCH: Remove this bypass
        return True
    return validate_token(token)
        '''
    }
    
    # Create temporary files
    temp_files = []
    try:
        for filename, content in sample_files.items():
            with tempfile.NamedTemporaryFile(mode='w', suffix=f'_{filename}', delete=False) as f:
                f.write(content)
                temp_files.append(f.name)
        
        # Scan files for patches
        from src.technical_debt_patch_annotation.core.models import AnnotationParser
        
        total_patches = 0
        for file_path in temp_files:
            with open(file_path, 'r') as f:
                content = f.read()
            
            result = AnnotationParser.extract_annotations(content, file_path)
            print(f"  📄 Scanned {os.path.basename(file_path)}:")
            print(f"    - Patches found: {len(result.patches)}")
            print(f"    - Lines scanned: {result.total_lines_scanned}")
            
            for patch in result.patches:
                print(f"    - {patch.patch_id}: {patch.debt_level.value} priority ({patch.component})")
            
            total_patches += len(result.patches)
        
        print(f"\n  📊 Scanning Summary:")
        print(f"    - Files scanned: {len(temp_files)}")
        print(f"    - Total patches found: {total_patches}")
        
    finally:
        # Clean up temporary files
        for file_path in temp_files:
            try:
                os.unlink(file_path)
            except:
                pass


async def main():
    """Main demonstration function."""
    try:
        await demonstrate_api_usage()
        demonstrate_file_scanning()
        
        print(f"\n✨ All demonstrations completed successfully!")
        
    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())