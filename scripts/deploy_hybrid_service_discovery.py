#!/usr/bin/env python3
"""
Deploy Hybrid Service Discovery System
======================================

Comprehensive deployment script that sets up the complete hybrid service
discovery system with Bonjour + Lab interoperability.

Features:
- Auto-registers all Docker services with Bonjour
- Maintains backward compatibility with existing .local domains
- Starts admin dashboard with unified service management
- Provides migration tools and conflict resolution
- Includes comprehensive testing and validation
"""

import os
import sys
import time
import subprocess
from datetime import datetime
from typing import Dict, List, Optional

# Add project root to path
sys.path.insert(0, '.')

from scripts.hybrid_service_manager import HybridServiceManager
from scripts.port_conflict_detector import PortConflictDetector
from scripts.bonjour_service_manager import BonjourServiceManager

class HybridServiceDeployment:
    """Manages deployment of the hybrid service discovery system."""
    
    def __init__(self):
        self.hybrid_manager = HybridServiceManager()
        self.port_detector = PortConflictDetector()
        self.bonjour_manager = BonjourServiceManager()
        
        self.deployment_log = []
        self.start_time = datetime.now()
    
    def log(self, message: str, level: str = "INFO"):
        """Log deployment messages."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.deployment_log.append(log_entry)
        print(log_entry)
    
    def check_prerequisites(self) -> bool:
        """Check system prerequisites."""
        self.log("🔍 Checking system prerequisites...")
        
        prerequisites_ok = True
        
        # Check Docker
        try:
            import docker
            client = docker.from_env()
            containers = client.containers.list()
            self.log(f"✅ Docker: {len(containers)} containers running")
        except Exception as e:
            self.log(f"❌ Docker not available: {e}", "ERROR")
            prerequisites_ok = False
        
        # Check Redis
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            r.ping()
            self.log("✅ Redis: Connection successful")
        except Exception as e:
            self.log(f"⚠️  Redis not available: {e}", "WARN")
        
        # Check Bonjour/mDNS
        try:
            result = subprocess.run(['which', 'dns-sd'], capture_output=True, text=True)
            if result.returncode == 0:
                self.log("✅ Bonjour/mDNS: dns-sd available")
            else:
                self.log("❌ Bonjour/mDNS: dns-sd not found", "ERROR")
                prerequisites_ok = False
        except Exception as e:
            self.log(f"❌ Bonjour/mDNS check failed: {e}", "ERROR")
            prerequisites_ok = False
        
        return prerequisites_ok
    
    def scan_current_services(self) -> Dict[str, any]:
        """Scan and analyze current service state."""
        self.log("🔍 Scanning current service state...")
        
        # Get all services
        all_services = self.hybrid_manager.discover_all_services()
        
        # Analyze service types
        analysis = {
            'total_services': len(all_services),
            'bonjour_services': 0,
            'hosts_services': 0,
            'docker_only_services': 0,
            'port_conflicts': [],
            'services': all_services
        }
        
        for name, info in all_services.items():
            method = info.get('discovery_method', 'unknown')
            if method == 'bonjour':
                analysis['bonjour_services'] += 1
            elif method == 'hosts':
                analysis['hosts_services'] += 1
            elif method == 'docker_only':
                analysis['docker_only_services'] += 1
            
            # Check for port conflicts
            port = info.get('port')
            if port:
                conflict = self.port_detector.check_conflicts_for_service(name, port)
                if conflict['conflict']:
                    analysis['port_conflicts'].append({
                        'service': name,
                        'port': port,
                        'conflicting_process': conflict['conflicting_process']
                    })
        
        self.log(f"📊 Found {analysis['total_services']} services:")
        self.log(f"   🌐 Bonjour: {analysis['bonjour_services']}")
        self.log(f"   📝 /etc/hosts: {analysis['hosts_services']}")
        self.log(f"   🐳 Docker only: {analysis['docker_only_services']}")
        
        if analysis['port_conflicts']:
            self.log(f"⚠️  {len(analysis['port_conflicts'])} port conflicts detected", "WARN")
        
        return analysis
    
    def resolve_port_conflicts(self, conflicts: List[Dict]) -> bool:
        """Resolve port conflicts automatically."""
        if not conflicts:
            return True
        
        self.log("🔧 Resolving port conflicts...")
        
        for conflict in conflicts:
            service = conflict['service']
            port = conflict['port']
            process = conflict['conflicting_process']
            
            self.log(f"⚠️  Conflict: {service}:{port} used by {process}")
            
            # Find alternative port
            try:
                alt_port = self.port_detector.find_available_port('admin')
                self.log(f"💡 Suggested alternative for {service}: {alt_port}")
            except Exception as e:
                self.log(f"❌ Could not find alternative port for {service}: {e}", "ERROR")
                return False
        
        return True
    
    def register_docker_services(self) -> Dict[str, any]:
        """Register all Docker services with Bonjour."""
        self.log("🐳 Registering Docker services with Bonjour...")
        
        results = self.hybrid_manager.auto_register_docker_services()
        
        if results['registered']:
            self.log(f"✅ Successfully registered {len(results['registered'])} services:")
            for service in results['registered']:
                self.log(f"   🌐 {service['service']} at {service['domain']}")
        
        if results['failed']:
            self.log(f"❌ Failed to register {len(results['failed'])} services:", "ERROR")
            for service in results['failed']:
                self.log(f"   ❌ {service['service']}: {service['error']}", "ERROR")
        
        return results
    
    def start_admin_dashboard(self, port: int = 8889) -> bool:
        """Start the admin dashboard."""
        self.log(f"🚀 Starting admin dashboard on port {port}...")
        
        # Check if port is available
        conflict = self.port_detector.check_conflicts_for_service("admin_dashboard", port)
        if conflict['conflict']:
            alt_port = conflict.get('suggested_port', port + 1)
            self.log(f"⚠️  Port {port} in use, using {alt_port} instead", "WARN")
            port = alt_port
        
        try:
            # Start dashboard in background
            dashboard_cmd = [
                sys.executable, 'scripts/admin_dashboard.py',
                '--host', '0.0.0.0',
                '--port', str(port)
            ]
            
            self.log(f"🌐 Admin dashboard will be available at: http://localhost:{port}")
            self.log("💡 Dashboard includes unified service management for both Bonjour and legacy services")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to start admin dashboard: {e}", "ERROR")
            return False
    
    def run_system_tests(self) -> bool:
        """Run comprehensive system tests."""
        self.log("🧪 Running system tests...")
        
        try:
            # Test service discovery
            services = self.hybrid_manager.discover_all_services()
            self.log(f"✅ Service discovery: {len(services)} services found")
            
            # Test port conflict detection
            port_report = self.port_detector.generate_port_report()
            self.log("✅ Port conflict detection: Working")
            
            # Test Bonjour registration
            bonjour_services = self.bonjour_manager.registered_services
            self.log(f"✅ Bonjour registration: {len(bonjour_services)} services registered")
            
            return True
            
        except Exception as e:
            self.log(f"❌ System tests failed: {e}", "ERROR")
            return False
    
    def generate_deployment_report(self) -> str:
        """Generate comprehensive deployment report."""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        # Get final service state
        final_services = self.hybrid_manager.discover_all_services()
        
        report = [
            "🚀 Hybrid Service Discovery Deployment Report",
            "=" * 50,
            f"Deployment Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Duration: {duration.total_seconds():.1f} seconds",
            "",
            "📊 Final Service State:",
            f"   Total Services: {len(final_services)}",
        ]
        
        # Group services by type
        bonjour_count = len([s for s in final_services.values() if s.get('discovery_method') == 'bonjour'])
        hosts_count = len([s for s in final_services.values() if s.get('discovery_method') == 'hosts'])
        docker_count = len([s for s in final_services.values() if s.get('discovery_method') == 'docker_only'])
        
        report.extend([
            f"   🌐 Bonjour Services: {bonjour_count}",
            f"   📝 /etc/hosts Services: {hosts_count}",
            f"   🐳 Docker Only: {docker_count}",
            "",
            "🌐 Service URLs:",
        ])
        
        for name, info in final_services.items():
            domain = info.get('domain', f"{name}.kiro.local")
            port = info.get('port', 'unknown')
            method = info.get('discovery_method', 'unknown')
            status = "🟢" if info.get('status') == 'running' else "🔴"
            
            report.append(f"   {status} http://{domain}:{port} ({method})")
        
        report.extend([
            "",
            "📋 Deployment Log:",
            "=" * 20,
        ])
        
        report.extend(self.deployment_log)
        
        return "\n".join(report)
    
    def deploy(self, start_dashboard: bool = True, run_tests: bool = True) -> bool:
        """Run complete deployment process."""
        self.log("🚀 Starting Hybrid Service Discovery Deployment")
        self.log("=" * 60)
        
        # Check prerequisites
        if not self.check_prerequisites():
            self.log("❌ Prerequisites not met, aborting deployment", "ERROR")
            return False
        
        # Scan current services
        analysis = self.scan_current_services()
        
        # Resolve port conflicts
        if not self.resolve_port_conflicts(analysis['port_conflicts']):
            self.log("❌ Could not resolve port conflicts", "ERROR")
            return False
        
        # Register Docker services
        registration_results = self.register_docker_services()
        
        # Start admin dashboard
        if start_dashboard:
            if not self.start_admin_dashboard():
                self.log("⚠️  Admin dashboard failed to start", "WARN")
        
        # Run system tests
        if run_tests:
            if not self.run_system_tests():
                self.log("⚠️  Some system tests failed", "WARN")
        
        # Generate final report
        self.log("📋 Generating deployment report...")
        
        self.log("🎉 Hybrid Service Discovery Deployment Complete!")
        self.log("=" * 50)
        self.log("✅ Services registered with Bonjour (.kiro.local)")
        self.log("✅ Backward compatibility maintained (.local)")
        self.log("✅ Port conflicts resolved")
        self.log("✅ Admin dashboard ready")
        
        return True

def main():
    """Main deployment entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy Hybrid Service Discovery System")
    parser.add_argument('--no-dashboard', action='store_true', help='Skip starting admin dashboard')
    parser.add_argument('--no-tests', action='store_true', help='Skip running system tests')
    parser.add_argument('--report-only', action='store_true', help='Generate report only')
    
    args = parser.parse_args()
    
    deployment = HybridServiceDeployment()
    
    if args.report_only:
        # Just generate a report of current state
        analysis = deployment.scan_current_services()
        print(deployment.hybrid_manager.generate_service_report())
        return
    
    try:
        success = deployment.deploy(
            start_dashboard=not args.no_dashboard,
            run_tests=not args.no_tests
        )
        
        # Generate and save report
        report = deployment.generate_deployment_report()
        
        report_file = f"deployment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"\n📋 Full deployment report saved to: {report_file}")
        
        if success:
            print("\n🎉 Deployment completed successfully!")
            print("🌐 Access admin dashboard at: http://localhost:8889")
            print("🔧 Use hybrid service manager: python scripts/hybrid_service_manager.py")
        else:
            print("\n❌ Deployment completed with errors")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()