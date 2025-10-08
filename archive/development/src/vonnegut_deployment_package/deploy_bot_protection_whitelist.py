#!/usr/bin/env python3
"""
Observatory Bot Protection Whitelist Deployment Script

Comprehensive deployment script for Observatory bot protection whitelist
configuration to prevent Error 1033 incidents.

This script orchestrates the complete deployment process including:
- Configuration generation
- Validation testing
- Security analysis
- Documentation
"""

import json
import sys
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class BotProtectionDeploymentOrchestrator:
    """Orchestrates the complete bot protection whitelist deployment"""
    
    def __init__(self, domain: str = "observatory.nkllon.com"):
        self.domain = domain
        self.deployment_start_time = datetime.utcnow()
        self.deployment_results = {}
        
    def _log_action(self, action: str, status: str, details: Optional[Dict[str, Any]] = None):
        """Log action in JSON format to stdout"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "task": "4.0",
            "action": action,
            "status": status,
            "details": details or {}
        }
        print(json.dumps(log_entry))
        
    def run_configuration_generation(self) -> Dict[str, Any]:
        """Run the bot protection configuration generation"""
        self._log_action("run_configuration_generation", "in_progress")
        
        try:
            # Run the configuration script
            result = subprocess.run([
                sys.executable, 
                "scripts/configure_observatory_bot_protection.py"
            ], capture_output=True, text=True, cwd=Path.cwd())
            
            success = result.returncode == 0
            
            self._log_action("run_configuration_generation", "completed" if success else "error", {
                "success": success,
                "return_code": result.returncode,
                "stdout_lines": len(result.stdout.splitlines()),
                "stderr_lines": len(result.stderr.splitlines()) if result.stderr else 0
            })
            
            return {
                "success": success,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except Exception as e:
            self._log_action("run_configuration_generation", "error", {
                "error": str(e)
            })
            return {
                "success": False,
                "error": str(e)
            }
            
    async def run_validation_testing(self) -> Dict[str, Any]:
        """Run the bot protection validation testing"""
        self._log_action("run_validation_testing", "in_progress")
        
        try:
            # Run the validation script
            result = subprocess.run([
                sys.executable,
                "scripts/validate_bot_protection_whitelist.py"
            ], capture_output=True, text=True, cwd=Path.cwd())
            
            success = result.returncode == 0
            
            # Parse validation results if available
            validation_results = {}
            try:
                validation_file = Path("config/bot_protection/validation_results.json")
                if validation_file.exists():
                    with open(validation_file) as f:
                        validation_results = json.load(f)
            except Exception:
                pass
                
            self._log_action("run_validation_testing", "completed" if success else "error", {
                "success": success,
                "return_code": result.returncode,
                "validation_success": validation_results.get("overall_success", False),
                "success_rate": validation_results.get("success_rate", 0)
            })
            
            return {
                "success": success,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "validation_results": validation_results
            }
            
        except Exception as e:
            self._log_action("run_validation_testing", "error", {
                "error": str(e)
            })
            return {
                "success": False,
                "error": str(e)
            }
            
    def generate_deployment_summary(self) -> Dict[str, Any]:
        """Generate comprehensive deployment summary"""
        self._log_action("generate_deployment_summary", "in_progress")
        
        # Check generated configuration files
        config_dir = Path("config/bot_protection")
        generated_files = []
        
        if config_dir.exists():
            for file_path in config_dir.glob("*.json"):
                generated_files.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "size_bytes": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
                
        # Check documentation files
        docs_dir = Path("docs")
        documentation_files = []
        
        if docs_dir.exists():
            for file_path in docs_dir.glob("bot_protection_*.md"):
                documentation_files.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "size_bytes": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
                
        deployment_summary = {
            "deployment_timestamp": self.deployment_start_time.isoformat(),
            "domain": self.domain,
            "configuration_files": generated_files,
            "documentation_files": documentation_files,
            "deployment_status": "completed",
            "next_steps": [
                "Review generated configuration files",
                "Apply Cloudflare dashboard settings",
                "Test Observatory traffic patterns",
                "Monitor bot protection events",
                "Validate WebSocket connectivity"
            ],
            "verification_commands": [
                f"curl -H 'X-Observatory-Client: internal-polling' -H 'X-Polling-Reason: websocket-fallback' https://{self.domain}/api/emoji-rain/stats",
                f"curl -I -N -H 'Connection: Upgrade' -H 'Upgrade: websocket' https://{self.domain}/ws/emoji-rain",
                f"curl -I https://{self.domain}/health"
            ],
            "monitoring_recommendations": [
                "Monitor Cloudflare Analytics for bot protection events",
                "Track Observatory traffic patterns in Security → Events",
                "Verify WebSocket connectivity through tunnel",
                "Test HTTP polling fallback functionality",
                "Regular validation of whitelist rules"
            ]
        }
        
        self._log_action("generate_deployment_summary", "completed", {
            "config_files": len(generated_files),
            "documentation_files": len(documentation_files)
        })
        
        return deployment_summary
        
    def save_deployment_report(self, summary: Dict[str, Any]) -> str:
        """Save comprehensive deployment report"""
        self._log_action("save_deployment_report", "in_progress")
        
        # Create reports directory
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        
        # Generate report filename with timestamp
        timestamp = self.deployment_start_time.strftime("%Y%m%d_%H%M%S")
        report_file = reports_dir / f"bot_protection_deployment_report_{timestamp}.json"
        
        # Add deployment results to summary
        summary["deployment_results"] = self.deployment_results
        summary["deployment_duration_seconds"] = (datetime.utcnow() - self.deployment_start_time).total_seconds()
        
        # Save report
        with open(report_file, "w") as f:
            json.dump(summary, f, indent=2)
            
        self._log_action("save_deployment_report", "completed", {
            "report_file": str(report_file),
            "report_size_bytes": report_file.stat().st_size
        })
        
        return str(report_file)
        
    async def run_complete_deployment(self) -> Dict[str, Any]:
        """Run the complete bot protection whitelist deployment"""
        self._log_action("run_complete_deployment", "in_progress")
        
        deployment_results = {
            "configuration_generation": {},
            "validation_testing": {},
            "deployment_summary": {},
            "overall_success": False
        }
        
        # Step 1: Generate configuration
        config_result = self.run_configuration_generation()
        deployment_results["configuration_generation"] = config_result
        
        if not config_result["success"]:
            self._log_action("run_complete_deployment", "error", {
                "reason": "Configuration generation failed",
                "error": config_result.get("error", "Unknown error")
            })
            return deployment_results
            
        # Step 2: Run validation testing
        validation_result = await self.run_validation_testing()
        deployment_results["validation_testing"] = validation_result
        
        # Step 3: Generate deployment summary
        summary = self.generate_deployment_summary()
        deployment_results["deployment_summary"] = summary
        
        # Step 4: Save deployment report
        report_file = self.save_deployment_report(summary)
        
        # Determine overall success
        overall_success = (
            config_result["success"] and
            validation_result["success"] and
            summary.get("configuration_files", [])
        )
        
        deployment_results["overall_success"] = overall_success
        deployment_results["report_file"] = report_file
        
        self._log_action("run_complete_deployment", "completed" if overall_success else "error", {
            "overall_success": overall_success,
            "config_success": config_result["success"],
            "validation_success": validation_result["success"],
            "report_file": report_file
        })
        
        return deployment_results


async def main():
    """Main deployment function"""
    print("🚀 Observatory Bot Protection Whitelist Deployment")
    print("=" * 60)
    
    orchestrator = BotProtectionDeploymentOrchestrator()
    
    # Run complete deployment
    deployment_results = await orchestrator.run_complete_deployment()
    
    # Print deployment summary
    print(f"\n📊 Deployment Summary:")
    print(f"   Overall Success: {'✅' if deployment_results['overall_success'] else '❌'}")
    print(f"   Configuration: {'✅' if deployment_results['configuration_generation']['success'] else '❌'}")
    print(f"   Validation: {'✅' if deployment_results['validation_testing']['success'] else '❌'}")
    
    if deployment_results.get("report_file"):
        print(f"   Report: {deployment_results['report_file']}")
        
    # Print next steps
    summary = deployment_results.get("deployment_summary", {})
    if summary.get("next_steps"):
        print(f"\n📋 Next Steps:")
        for step in summary["next_steps"]:
            print(f"   • {step}")
            
    # Print verification commands
    if summary.get("verification_commands"):
        print(f"\n🔍 Verification Commands:")
        for cmd in summary["verification_commands"]:
            print(f"   {cmd}")
            
    # Print monitoring recommendations
    if summary.get("monitoring_recommendations"):
        print(f"\n📈 Monitoring Recommendations:")
        for rec in summary["monitoring_recommendations"]:
            print(f"   • {rec}")
            
    # Final completion log
    orchestrator._log_action("main", "completed", {
        "summary": "Bot protection whitelist deployment completed",
        "overall_success": deployment_results['overall_success'],
        "report_file": deployment_results.get("report_file", "")
    })
    
    return 0 if deployment_results['overall_success'] else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)