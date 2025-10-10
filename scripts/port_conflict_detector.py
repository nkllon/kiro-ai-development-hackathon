#!/usr/bin/env python3
"""
Port Conflict Detection for Kiro Services
=========================================

Detects and resolves port conflicts before starting services.
Prevents the "pork gonna cause a conflict" problem.
"""

import subprocess
import socket
from typing import Dict, List, Optional, Set

class PortConflictDetector:
    """Detects and manages port conflicts for Kiro services."""
    
    def __init__(self):
        # Known Kiro service ports
        self.known_ports = {
            3000: "Grafana Dashboard",
            6379: "Redis Database", 
            8000: "Beast Mode Monitoring Daemon",
            8055: "Directus CMS",
            8888: "Observatory Server (RESERVED)",
            8889: "Admin Dashboard",
            9090: "Prometheus Monitoring",
            16686: "Jaeger Tracing"
        }
        
        # Port ranges for different service types
        self.port_ranges = {
            'admin': range(8889, 8899),      # Admin interfaces
            'monitoring': range(9000, 9099), # Monitoring services  
            'api': range(8100, 8199),        # API services
            'web': range(3000, 3099),        # Web interfaces
            'database': range(6300, 6399),   # Database services
        }
    
    def is_port_in_use(self, port: int) -> bool:
        """Check if a port is currently in use."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                return result == 0
        except Exception:
            return False
    
    def get_process_using_port(self, port: int) -> Optional[str]:
        """Get the process name using a specific port."""
        try:
            result = subprocess.run(
                ['lsof', '-i', f':{port}', '-t'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                pid = result.stdout.strip().split('\n')[0]
                
                # Get process name
                ps_result = subprocess.run(
                    ['ps', '-p', pid, '-o', 'comm='],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if ps_result.returncode == 0:
                    return ps_result.stdout.strip()
            
            return None
            
        except Exception as e:
            print(f"Error checking process for port {port}: {e}")
            return None
    
    def scan_port_usage(self) -> Dict[int, Dict[str, str]]:
        """Scan all known ports for usage."""
        usage = {}
        
        for port, service_name in self.known_ports.items():
            in_use = self.is_port_in_use(port)
            process = self.get_process_using_port(port) if in_use else None
            
            usage[port] = {
                'service': service_name,
                'in_use': in_use,
                'process': process or 'Unknown'
            }
        
        return usage
    
    def find_available_port(self, service_type: str = 'admin', preferred_port: Optional[int] = None) -> int:
        """Find an available port for a service type."""
        # Try preferred port first
        if preferred_port and not self.is_port_in_use(preferred_port):
            return preferred_port
        
        # Try ports in the appropriate range
        port_range = self.port_ranges.get(service_type, range(8000, 9000))
        
        for port in port_range:
            if not self.is_port_in_use(port):
                return port
        
        # Fallback to any available port in 8000-9999 range
        for port in range(8000, 10000):
            if not self.is_port_in_use(port):
                return port
        
        raise Exception(f"No available ports found for service type: {service_type}")
    
    def check_conflicts_for_service(self, service_name: str, port: int) -> Dict[str, any]:
        """Check for conflicts when starting a specific service."""
        result = {
            'service': service_name,
            'requested_port': port,
            'conflict': False,
            'conflicting_process': None,
            'suggested_port': None,
            'action': 'proceed'
        }
        
        if self.is_port_in_use(port):
            result['conflict'] = True
            result['conflicting_process'] = self.get_process_using_port(port)
            result['action'] = 'resolve_conflict'
            
            # Suggest alternative port
            try:
                service_type = self._guess_service_type(service_name)
                result['suggested_port'] = self.find_available_port(service_type)
            except Exception:
                result['suggested_port'] = None
        
        return result
    
    def _guess_service_type(self, service_name: str) -> str:
        """Guess service type from service name."""
        name_lower = service_name.lower()
        
        if 'admin' in name_lower or 'dashboard' in name_lower:
            return 'admin'
        elif 'monitor' in name_lower or 'prometheus' in name_lower:
            return 'monitoring'
        elif 'api' in name_lower:
            return 'api'
        elif 'web' in name_lower or 'grafana' in name_lower:
            return 'web'
        elif 'database' in name_lower or 'redis' in name_lower:
            return 'database'
        else:
            return 'admin'  # Default
    
    def generate_port_report(self) -> str:
        """Generate a comprehensive port usage report."""
        usage = self.scan_port_usage()
        
        report = ["🔍 Kiro Port Usage Report", "=" * 30, ""]
        
        # Active ports
        active_ports = {port: info for port, info in usage.items() if info['in_use']}
        if active_ports:
            report.append("🟢 Active Ports:")
            for port, info in active_ports.items():
                report.append(f"   {port:5d} - {info['service']} ({info['process']})")
            report.append("")
        
        # Available ports
        available_ports = {port: info for port, info in usage.items() if not info['in_use']}
        if available_ports:
            report.append("⚪ Available Ports:")
            for port, info in available_ports.items():
                report.append(f"   {port:5d} - {info['service']} (available)")
            report.append("")
        
        # Port range availability
        report.append("📊 Port Range Availability:")
        for service_type, port_range in self.port_ranges.items():
            available_count = sum(1 for port in port_range if not self.is_port_in_use(port))
            total_count = len(port_range)
            report.append(f"   {service_type:10s}: {available_count:2d}/{total_count:2d} available")
        
        return "\n".join(report)
    
    def resolve_conflict_interactive(self, service_name: str, port: int) -> int:
        """Interactively resolve a port conflict."""
        conflict_info = self.check_conflicts_for_service(service_name, port)
        
        if not conflict_info['conflict']:
            print(f"✅ Port {port} is available for {service_name}")
            return port
        
        print(f"⚠️  Port Conflict Detected!")
        print(f"   Service: {service_name}")
        print(f"   Requested Port: {port}")
        print(f"   Conflicting Process: {conflict_info['conflicting_process']}")
        
        if conflict_info['suggested_port']:
            print(f"   Suggested Alternative: {conflict_info['suggested_port']}")
            
            response = input(f"Use suggested port {conflict_info['suggested_port']}? [Y/n]: ")
            if response.lower() in ['', 'y', 'yes']:
                return conflict_info['suggested_port']
        
        # Manual port selection
        while True:
            try:
                manual_port = input("Enter a different port number: ")
                manual_port = int(manual_port)
                
                if not self.is_port_in_use(manual_port):
                    return manual_port
                else:
                    print(f"❌ Port {manual_port} is also in use. Try another.")
                    
            except ValueError:
                print("❌ Please enter a valid port number.")
            except KeyboardInterrupt:
                print("\n❌ Port selection cancelled.")
                raise

def main():
    """Main CLI interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Port Conflict Detection for Kiro Services")
    parser.add_argument('action', choices=['scan', 'check', 'find', 'report'],
                       help='Action to perform')
    parser.add_argument('--service', help='Service name for check action')
    parser.add_argument('--port', type=int, help='Port number for check action')
    parser.add_argument('--type', default='admin', help='Service type for find action')
    
    args = parser.parse_args()
    
    detector = PortConflictDetector()
    
    if args.action == 'scan':
        usage = detector.scan_port_usage()
        print("🔍 Port Usage Scan:")
        for port, info in usage.items():
            status = "🟢 IN USE" if info['in_use'] else "⚪ AVAILABLE"
            process = f" ({info['process']})" if info['in_use'] else ""
            print(f"   {port:5d} - {info['service']} - {status}{process}")
    
    elif args.action == 'check':
        if not args.service or not args.port:
            print("❌ --service and --port required for check action")
            return
        
        result = detector.check_conflicts_for_service(args.service, args.port)
        if result['conflict']:
            print(f"⚠️  CONFLICT: Port {args.port} is in use by {result['conflicting_process']}")
            if result['suggested_port']:
                print(f"💡 Suggested alternative: {result['suggested_port']}")
        else:
            print(f"✅ Port {args.port} is available for {args.service}")
    
    elif args.action == 'find':
        try:
            available_port = detector.find_available_port(args.type)
            print(f"✅ Available port for {args.type} services: {available_port}")
        except Exception as e:
            print(f"❌ Error finding available port: {e}")
    
    elif args.action == 'report':
        print(detector.generate_port_report())

if __name__ == "__main__":
    main()