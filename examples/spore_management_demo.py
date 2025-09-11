#!/usr/bin/env python3
"""
Beast Mode Spore Management Demo

Demonstrates the complete spore management system including:
- Creating and saving spores
- Loading and validating spores
- Version management
- Search and discovery
- Import/export functionality
- Usage statistics tracking
"""

import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime

from src.beast_mode.messaging.spore_manager import SporeManager
from src.beast_mode.messaging.models import BeastModeMessage, MessageType


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_spores():
    """Create sample spore content and metadata for demonstration"""
    
    # Cost optimization spore
    cost_optimization_spore = '''
def execute(context):
    """
    Systematic cost optimization for cloud resources
    
    Args:
        context: Dictionary containing resource information
        
    Returns:
        Dictionary with optimization results
    """
    resources = context.get('resources', [])
    optimizations = []
    total_savings = 0
    
    for resource in resources:
        if resource.get('type') == 'compute':
            # Right-size instances
            current_size = resource.get('size', 'medium')
            if resource.get('utilization', 0) < 0.3:
                optimizations.append({
                    'resource': resource['id'],
                    'action': 'downsize',
                    'from': current_size,
                    'to': 'small',
                    'savings': 200
                })
                total_savings += 200
        
        elif resource.get('type') == 'storage':
            # Optimize storage class
            if resource.get('access_pattern') == 'infrequent':
                optimizations.append({
                    'resource': resource['id'],
                    'action': 'change_storage_class',
                    'to': 'coldline',
                    'savings': 50
                })
                total_savings += 50
    
    return {
        'status': 'success',
        'optimizations': optimizations,
        'total_monthly_savings': total_savings,
        'recommendations': [
            'Enable auto-scaling for compute resources',
            'Set up lifecycle policies for storage',
            'Review unused resources monthly'
        ]
    }

class CostOptimizationSpore:
    """Systematic cost optimization methodology"""
    
    def __init__(self):
        self.name = "cost_optimization"
        self.version = "1.0.0"
        self.capabilities = ["gcp_access", "cost_analysis"]
    
    def analyze_resources(self, project_id):
        """Analyze resource usage patterns"""
        return {
            'analysis_complete': True,
            'resources_analyzed': 25,
            'optimization_opportunities': 8
        }
    
    def generate_report(self, optimizations):
        """Generate cost optimization report"""
        return {
            'report_generated': True,
            'format': 'json',
            'timestamp': datetime.now().isoformat()
        }
'''
    
    cost_metadata = {
        "name": "cost_optimization_spore",
        "version": "1.0.0",
        "author": "beast_mode_cost_agent",
        "description": "Systematic cost optimization methodology for GCP resources",
        "tags": ["cost", "optimization", "gcp", "systematic"],
        "capabilities_required": ["gcp_access", "cost_analysis", "resource_management"],
        "compatibility_version": "1.0",
        "validation_criteria": {
            "has_execute_function": True,
            "has_class_definition": True,
            "syntax_valid": True
        }
    }
    
    # Security scanning spore
    security_scanner_spore = '''
def execute(context):
    """
    Systematic security vulnerability scanning
    
    Args:
        context: Dictionary containing scan configuration
        
    Returns:
        Dictionary with scan results
    """
    scan_targets = context.get('targets', [])
    vulnerabilities = []
    
    for target in scan_targets:
        # Simulate security scanning
        if target.get('type') == 'instance':
            # Check for common vulnerabilities
            issues = []
            
            if not target.get('firewall_enabled', False):
                issues.append({
                    'severity': 'high',
                    'type': 'firewall_disabled',
                    'description': 'Instance firewall is disabled'
                })
            
            if target.get('ssh_keys_count', 0) > 10:
                issues.append({
                    'severity': 'medium',
                    'type': 'excessive_ssh_keys',
                    'description': 'Too many SSH keys configured'
                })
            
            if issues:
                vulnerabilities.extend(issues)
    
    return {
        'status': 'success',
        'scan_completed': True,
        'vulnerabilities_found': len(vulnerabilities),
        'vulnerabilities': vulnerabilities,
        'recommendations': [
            'Enable firewall on all instances',
            'Regularly audit SSH key access',
            'Implement least privilege access'
        ]
    }

class SecurityScannerSpore:
    """Systematic security scanning methodology"""
    
    def __init__(self):
        self.name = "security_scanner"
        self.version = "1.2.0"
        self.capabilities = ["security_scanning", "vulnerability_assessment"]
    
    def configure_scan(self, targets):
        """Configure security scan parameters"""
        return {'scan_configured': True, 'target_count': len(targets)}
    
    def generate_security_report(self, results):
        """Generate security assessment report"""
        return {
            'report_type': 'security_assessment',
            'format': 'json',
            'timestamp': datetime.now().isoformat()
        }
'''
    
    security_metadata = {
        "name": "security_scanner_spore",
        "version": "1.2.0",
        "author": "beast_mode_security_agent",
        "description": "Systematic security vulnerability scanning for cloud infrastructure",
        "tags": ["security", "scanning", "vulnerability", "systematic"],
        "capabilities_required": ["security_access", "vulnerability_scanning"],
        "compatibility_version": "1.0",
        "validation_criteria": {
            "has_execute_function": True,
            "has_class_definition": True,
            "syntax_valid": True
        }
    }
    
    return [
        (cost_optimization_spore, cost_metadata),
        (security_scanner_spore, security_metadata)
    ]


async def demonstrate_spore_management():
    """Demonstrate complete spore management functionality"""
    
    print("🧬 Beast Mode Spore Management Demo")
    print("=" * 50)
    
    # Initialize SporeManager
    spore_manager = SporeManager(spore_directory="demo_spores")
    print(f"✅ Initialized SporeManager with directory: {spore_manager.spore_directory}")
    
    # Create sample spores
    sample_spores = create_sample_spores()
    print(f"📝 Created {len(sample_spores)} sample spores")
    
    # Save spores
    saved_spores = []
    for spore_content, metadata in sample_spores:
        try:
            spore_name = spore_manager.save_spore(spore_content, metadata)
            saved_spores.append(spore_name)
            print(f"💾 Saved spore: {spore_name}")
        except Exception as e:
            print(f"❌ Failed to save spore: {e}")
    
    print(f"\n📋 Spore Management Operations:")
    
    # List all spores
    all_spores = spore_manager.list_spores()
    print(f"📊 Total spores in repository: {len(all_spores)}")
    
    for spore in all_spores:
        print(f"  • {spore['name']} v{spore['version']} by {spore['author']}")
        print(f"    Tags: {', '.join(spore['tags'])}")
        print(f"    Capabilities: {', '.join(spore['capabilities_required'])}")
        print()
    
    # Demonstrate spore loading
    print("🔍 Loading and validating spores:")
    for spore_name in saved_spores:
        loaded_spore = spore_manager.load_spore(spore_name)
        if loaded_spore:
            print(f"✅ Successfully loaded: {spore_name}")
            
            # Validate spore content
            is_valid = spore_manager.validate_spore(loaded_spore['implementation'])
            print(f"   Validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
        else:
            print(f"❌ Failed to load: {spore_name}")
    
    # Demonstrate search functionality
    print("\n🔎 Search and Discovery:")
    
    # Search by keyword
    cost_spores = spore_manager.search_spores("cost")
    print(f"💰 Cost-related spores: {len(cost_spores)}")
    for spore in cost_spores:
        print(f"  • {spore['name']}: {spore['description']}")
    
    # Search by tags
    security_spores = spore_manager.search_spores("", tags=["security"])
    print(f"🔒 Security spores: {len(security_spores)}")
    for spore in security_spores:
        print(f"  • {spore['name']}: {spore['description']}")
    
    # Demonstrate version management
    print("\n📈 Version Management:")
    
    if saved_spores:
        test_spore = saved_spores[0]
        
        # Update spore to create version
        updated_metadata = spore_manager.load_spore(test_spore)['metadata'].copy()
        updated_metadata['version'] = "1.1.0"
        updated_metadata['description'] += " - Enhanced with ML predictions"
        
        original_content = spore_manager.load_spore(test_spore)['implementation']
        spore_manager.save_spore(original_content, updated_metadata)
        
        print(f"📦 Updated {test_spore} to version 1.1.0")
        
        # Check versions
        versions = spore_manager.get_spore_versions(test_spore)
        print(f"📚 Available versions: {len(versions)}")
        for version in versions:
            print(f"  • {version}")
    
    # Demonstrate usage statistics
    print("\n📊 Usage Statistics:")
    
    for spore_name in saved_spores:
        # Simulate some usage
        spore_manager.update_spore_stats(spore_name, success=True)
        spore_manager.update_spore_stats(spore_name, success=True)
        spore_manager.update_spore_stats(spore_name, success=False)
        
        spore_data = spore_manager.load_spore(spore_name)
        metadata = spore_data['metadata']
        
        print(f"📈 {spore_name}:")
        print(f"   Usage count: {metadata['usage_count']}")
        print(f"   Success rate: {metadata['success_rate']:.1%}")
    
    # Demonstrate export/import
    print("\n📤 Export/Import Operations:")
    
    if saved_spores:
        export_spore = saved_spores[0]
        export_path = Path("demo_spores") / "exported" / f"{export_spore}.json"
        
        # Export spore
        export_success = spore_manager.export_spore(export_spore, str(export_path))
        if export_success:
            print(f"📤 Exported {export_spore} to {export_path}")
            
            # Delete original
            spore_manager.delete_spore(export_spore)
            print(f"🗑️  Deleted original {export_spore}")
            
            # Import back
            imported_name = spore_manager.import_spore(str(export_path))
            if imported_name:
                print(f"📥 Imported {imported_name} from {export_path}")
            else:
                print("❌ Import failed")
        else:
            print(f"❌ Export failed for {export_spore}")
    
    # Demonstrate spore distribution messages
    print("\n📡 Spore Distribution Messages:")
    
    if saved_spores:
        spore_name = saved_spores[0]
        spore_data = spore_manager.load_spore(spore_name)
        
        # Create spore delivery message
        delivery_message = BeastModeMessage(
            type=MessageType.SPORE_DELIVERY,
            source="demo_agent",
            target="receiving_agent",
            payload={
                "spore_name": spore_name,
                "spore_data": spore_data,
                "delivery_method": "direct_transfer",
                "sender_note": "This spore has proven effective for cost optimization"
            }
        )
        
        print(f"📨 Created spore delivery message:")
        print(f"   Type: {delivery_message.type}")
        print(f"   Source: {delivery_message.source}")
        print(f"   Target: {delivery_message.target}")
        print(f"   Spore: {delivery_message.payload['spore_name']}")
        
        # Create spore request message
        request_message = BeastModeMessage(
            type=MessageType.SPORE_REQUEST,
            source="requesting_agent",
            payload={
                "requested_capabilities": ["cost_optimization", "gcp_access"],
                "urgency": "normal",
                "use_case": "Monthly cost optimization review",
                "preferred_tags": ["cost", "systematic"]
            }
        )
        
        print(f"\n📨 Created spore request message:")
        print(f"   Type: {request_message.type}")
        print(f"   Source: {request_message.source}")
        print(f"   Requested capabilities: {request_message.payload['requested_capabilities']}")
        print(f"   Use case: {request_message.payload['use_case']}")
    
    print("\n✨ Demo completed successfully!")
    print(f"📁 Spore repository location: {spore_manager.spore_directory}")
    print("🧬 All spores are ready for systematic collaboration!")


def demonstrate_spore_execution():
    """Demonstrate executing a spore"""
    
    print("\n🚀 Spore Execution Demo")
    print("=" * 30)
    
    spore_manager = SporeManager(spore_directory="demo_spores")
    
    # Load cost optimization spore
    cost_spore = spore_manager.load_spore("cost_optimization_spore")
    
    if cost_spore:
        print("📋 Executing cost optimization spore...")
        
        # Sample context data
        context = {
            'resources': [
                {
                    'id': 'instance-1',
                    'type': 'compute',
                    'size': 'large',
                    'utilization': 0.2  # Low utilization
                },
                {
                    'id': 'storage-1',
                    'type': 'storage',
                    'access_pattern': 'infrequent'
                },
                {
                    'id': 'instance-2',
                    'type': 'compute',
                    'size': 'medium',
                    'utilization': 0.8  # High utilization
                }
            ]
        }
        
        try:
            # Execute the spore (in a real scenario, this would be done safely)
            # For demo purposes, we'll simulate the execution
            print("⚡ Simulating spore execution...")
            
            # This would normally execute the spore code
            # exec(cost_spore['implementation'])
            # result = execute(context)
            
            # Simulated result
            result = {
                'status': 'success',
                'optimizations': [
                    {
                        'resource': 'instance-1',
                        'action': 'downsize',
                        'from': 'large',
                        'to': 'small',
                        'savings': 200
                    },
                    {
                        'resource': 'storage-1',
                        'action': 'change_storage_class',
                        'to': 'coldline',
                        'savings': 50
                    }
                ],
                'total_monthly_savings': 250,
                'recommendations': [
                    'Enable auto-scaling for compute resources',
                    'Set up lifecycle policies for storage',
                    'Review unused resources monthly'
                ]
            }
            
            print("✅ Spore execution completed!")
            print(f"💰 Total monthly savings: ${result['total_monthly_savings']}")
            print(f"🔧 Optimizations found: {len(result['optimizations'])}")
            
            for opt in result['optimizations']:
                print(f"  • {opt['resource']}: {opt['action']} (${opt['savings']}/month)")
            
            print("\n💡 Recommendations:")
            for rec in result['recommendations']:
                print(f"  • {rec}")
            
            # Update spore statistics
            spore_manager.update_spore_stats("cost_optimization_spore", success=True)
            print("\n📊 Updated spore usage statistics")
            
        except Exception as e:
            print(f"❌ Spore execution failed: {e}")
            spore_manager.update_spore_stats("cost_optimization_spore", success=False)
    
    else:
        print("❌ Cost optimization spore not found")


if __name__ == "__main__":
    print("🧬 Starting Beast Mode Spore Management Demo")
    
    # Run the main demo
    asyncio.run(demonstrate_spore_management())
    
    # Demonstrate spore execution
    demonstrate_spore_execution()
    
    print("\n🎉 All demos completed!")
    print("📚 Check the demo_spores directory to see the created spore repository")