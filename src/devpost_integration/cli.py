#!/usr/bin/env python3
"""
DevPost Integration CLI
=======================

Command line interface for DevPost integration.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Provide CLI interface for DevPost integration
"""

import argparse
import json
import sys
from typing import Dict, Any, List
from datetime import datetime
from .reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability


class Unknown:
    """Unknown class for backward compatibility."""
    pass


class DevPostCLI(ReflectiveModule):
    """DevPost Integration CLI class."""

    def __init__(self):
        super().__init__()
        self.module_id = "devpost_cli"
        self.capabilities = [ModuleCapability.CORE_FUNCTIONALITY]
        self.dependencies = []

    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            'module_id': self.module_id,
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': self.dependencies,
            'capabilities': [cap.value for cap in self.capabilities]
        }

    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return self.capabilities

    def get_health_status(self) -> ModuleHealth:
        """Get module health status."""
        return ModuleHealth(
            module_id=self.module_id,
            status=ModuleStatus.HEALTHY,
            health_score=100.0,
            issues=[],
            last_check=datetime.now()
        )

    def graceful_degradation(self):
        """Perform graceful degradation."""
        return {
            'success': True,
            'degraded_capabilities': [],
            'remaining_capabilities': [cap.value for cap in self.capabilities]
        }

    def create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser."""
        parser = argparse.ArgumentParser(
            description='DevPost Integration CLI',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        parser.add_argument('--version', action='version', version='1.0.0')
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Browser automation commands
        extract_parser = subparsers.add_parser('extract', help='Extract data from DevPost')
        extract_parser.add_argument('url', help='DevPost URL to extract from')
        extract_parser.add_argument('--type', choices=['hackathon', 'project'], default='hackathon', help='Type of data to extract')
        extract_parser.set_defaults(func=self.extract_command)
        
        search_parser = subparsers.add_parser('search', help='Search for hackathons')
        search_parser.add_argument('query', help='Search query')
        search_parser.add_argument('--limit', type=int, default=10, help='Maximum number of results')
        search_parser.set_defaults(func=self.search_command)
        
        # Status command
        status_parser = subparsers.add_parser('status', help='Show module status')
        status_parser.set_defaults(func=self.status_command)
        
        return parser

    def extract_command(self, args) -> Dict[str, Any]:
        """Extract data from DevPost using browser automation."""
        from .hybrid_integration import DevPostHybridIntegration
        
        try:
            with DevPostHybridIntegration() as integration:
                if args.type == 'hackathon':
                    result = integration.extract_hackathon_data_sync(args.url)
                else:
                    result = integration.extract_project_data_sync(args.url)
                
                if result.success:
                    return {
                        "success": True,
                        "data": result.data,
                        "method_used": result.method_used
                    }
                else:
                    return {
                        "success": False,
                        "error": result.error
                    }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_command(self, args) -> Dict[str, Any]:
        """Search for hackathons using browser automation."""
        from .hybrid_integration import DevPostHybridIntegration
        
        try:
            with DevPostHybridIntegration() as integration:
                hackathons = integration.search_hackathons(query=args.query, limit=args.limit)
                return {
                    "success": True,
                    "hackathons": hackathons,
                    "count": len(hackathons)
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def status_command(self, args) -> Dict[str, Any]:
        """Status command handler."""
        return {
            'module_id': self.module_id,
            'status': 'healthy',
            'timestamp': datetime.now().isoformat()
        }


def main():
    """Main CLI entry point."""
    cli = DevPostCLI()
    parser = cli.create_parser()
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        result = args.func(args)
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
