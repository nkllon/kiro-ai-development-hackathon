#!/usr/bin/env python3
"""
Integration Validation Script
Prevents failure modes by validating all external dependencies and credentials
before declaring integration success.
"""

import subprocess
import json
import sys
import os
from typing import Dict, List, Tuple, Any

class IntegrationValidator:
    """Validates all integrations before declaring success."""
    
    def __init__(self):
        self.failures = []
        self.warnings = []
        self.successes = []
    
    def validate_github_mcp(self) -> Tuple[bool, str]:
        """Validate GitHub MCP server authentication."""
        try:
            # Test token validity
            result = subprocess.run([
                'curl', '-s', '-H', 
                f'Authorization: token {os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "")}',
                'https://api.github.com/user'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return False, f"GitHub API request failed: {result.stderr}"
            
            response = json.loads(result.stdout)
            if "message" in response and "Bad credentials" in response["message"]:
                return False, "GitHub token authentication failed - Bad credentials"
            
            if "login" in response:
                return True, f"GitHub authentication successful for user: {response['login']}"
            else:
                return False, "Unexpected GitHub API response format"
                
        except subprocess.TimeoutExpired:
            return False, "GitHub API request timed out"
        except json.JSONDecodeError:
            return False, "Invalid JSON response from GitHub API"
        except Exception as e:
            return False, f"GitHub validation error: {str(e)}"
    
    def validate_simone_mcp(self) -> Tuple[bool, str]:
        """Validate Simone MCP server functionality."""
        try:
            # Test Simone MCP server
            result = subprocess.run([
                'node', '/Users/lou/kiro-2/kiro-ai-development-hackathon/kiro_simone_adapter/mcp-server/dist/index.js',
                '--help'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return False, f"Simone MCP server failed: {result.stderr}"
            
            return True, "Simone MCP server operational"
            
        except subprocess.TimeoutExpired:
            return False, "Simone MCP server request timed out"
        except Exception as e:
            return False, f"Simone validation error: {str(e)}"
    
    def validate_docker_github_mcp(self) -> Tuple[bool, str]:
        """Validate Docker-based GitHub MCP server."""
        try:
            # Test Docker GitHub MCP server
            result = subprocess.run([
                'docker', 'run', '--rm', '-i', '-e', 'GITHUB_PERSONAL_ACCESS_TOKEN',
                'ghcr.io/github/github-mcp-server'
            ], input='{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}}}',
            capture_output=True, text=True, timeout=15)
            
            if result.returncode != 0:
                return False, f"Docker GitHub MCP failed: {result.stderr}"
            
            response = json.loads(result.stdout)
            if "result" in response and "serverInfo" in response["result"]:
                return True, f"Docker GitHub MCP operational: {response['result']['serverInfo']['name']}"
            else:
                return False, "Docker GitHub MCP unexpected response format"
                
        except subprocess.TimeoutExpired:
            return False, "Docker GitHub MCP request timed out"
        except json.JSONDecodeError:
            return False, "Invalid JSON response from Docker GitHub MCP"
        except Exception as e:
            return False, f"Docker GitHub MCP validation error: {str(e)}"
    
    def validate_interface_registry(self) -> Tuple[bool, str]:
        """Validate interface registry functionality."""
        try:
            # Test interface registry
            result = subprocess.run([
                'make', 'check-registry'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return False, f"Interface registry check failed: {result.stderr}"
            
            return True, "Interface registry operational"
            
        except subprocess.TimeoutExpired:
            return False, "Interface registry check timed out"
        except Exception as e:
            return False, f"Interface registry validation error: {str(e)}"
    
    def run_all_validations(self) -> Dict[str, Any]:
        """Run all integration validations."""
        print("🔍 Integration Validation Suite")
        print("=" * 50)
        
        validations = [
            ("GitHub Token Authentication", self.validate_github_mcp),
            ("Simone MCP Server", self.validate_simone_mcp),
            ("Docker GitHub MCP", self.validate_docker_github_mcp),
            ("Interface Registry", self.validate_interface_registry),
        ]
        
        for name, validator in validations:
            print(f"\n🧪 Testing: {name}")
            try:
                success, message = validator()
                if success:
                    self.successes.append((name, message))
                    print(f"✅ {message}")
                else:
                    self.failures.append((name, message))
                    print(f"❌ {message}")
            except Exception as e:
                self.failures.append((name, f"Validation exception: {str(e)}"))
                print(f"💥 Validation exception: {str(e)}")
        
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate validation report."""
        total = len(self.successes) + len(self.failures)
        success_rate = (len(self.successes) / total * 100) if total > 0 else 0
        
        report = {
            "total_validations": total,
            "successes": len(self.successes),
            "failures": len(self.failures),
            "success_rate": success_rate,
            "status": "PASS" if len(self.failures) == 0 else "FAIL",
            "success_details": self.successes,
            "failure_details": self.failures,
            "recommendations": self.generate_recommendations()
        }
        
        print(f"\n📊 Validation Report")
        print(f"=" * 30)
        print(f"Total Validations: {total}")
        print(f"Successes: {len(self.successes)}")
        print(f"Failures: {len(self.failures)}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Status: {report['status']}")
        
        if self.failures:
            print(f"\n❌ Failures Detected:")
            for name, message in self.failures:
                print(f"   - {name}: {message}")
        
        if report['recommendations']:
            print(f"\n🔧 Recommendations:")
            for rec in report['recommendations']:
                print(f"   - {rec}")
        
        return report
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on failures."""
        recommendations = []
        
        for name, message in self.failures:
            if "GitHub token authentication failed" in message:
                recommendations.append("Generate new GitHub Personal Access Token with required scopes")
            elif "GitHub API request failed" in message:
                recommendations.append("Check network connectivity and GitHub API availability")
            elif "Simone MCP server failed" in message:
                recommendations.append("Rebuild Simone MCP server or check Node.js dependencies")
            elif "Docker GitHub MCP" in message:
                recommendations.append("Pull latest Docker image or check Docker daemon status")
            elif "Interface registry" in message:
                recommendations.append("Reinitialize interface registry or check file permissions")
        
        return recommendations

def main():
    """Main validation function."""
    validator = IntegrationValidator()
    report = validator.run_all_validations()
    
    # Exit with error code if any validations failed
    if report['status'] == 'FAIL':
        print(f"\n🚨 Integration validation FAILED!")
        print(f"Fix {report['failures']} failure(s) before proceeding.")
        sys.exit(1)
    else:
        print(f"\n✅ All integrations validated successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()

