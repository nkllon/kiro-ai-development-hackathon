#!/usr/bin/env python3
"""
GitHub Personal Access Token Configuration Facilitator
Implements the requirement to retrieve and configure GitHub PAT for MCP integration.
"""

import os
import sys
import json
import webbrowser
from pathlib import Path
from typing import Optional, Dict, Any

# Add src to path for safe subprocess import
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from beast_mode.core.safe_subprocess import safe_execute, ExecutionResult

class GitHubPATFacilitator:
    """Facilitates GitHub PAT retrieval and configuration."""
    
    def __init__(self):
        self.cursor_config_path = Path.home() / ".cursor" / "mcp.json"
        self.project_root = Path(__file__).parent.parent
        self.required_scopes = [
            "repo",           # Full repository access
            "read:org",       # Read organization membership
            "read:user",      # Read user profile
            "read:project",   # Read project information
            "workflow"        # Update GitHub Action workflows
        ]
    
    def check_existing_token(self) -> Optional[str]:
        """Check if a valid GitHub PAT is already configured."""
        try:
            if self.cursor_config_path.exists():
                with open(self.cursor_config_path, 'r') as f:
                    config = json.load(f)
                
                github_config = config.get("mcpServers", {}).get("github", {})
                token = github_config.get("env", {}).get("GITHUB_PERSONAL_ACCESS_TOKEN", "")
                
                if token and token != "your_actual_token_here":
                    # Test token validity
                    if self.validate_token(token):
                        print(f"✅ Valid GitHub PAT already configured")
                        return token
                    else:
                        print(f"❌ Existing GitHub PAT is invalid")
                        return None
                        
        except Exception as e:
            print(f"⚠️ Error checking existing token: {e}")
        
        return None
    
    def validate_token(self, token: str) -> bool:
        """Validate GitHub PAT by making API call."""
        try:
            result = safe_execute([
                'curl', '-s', '-H', f'Authorization: token {token}',
                'https://api.github.com/user'
            ], timeout=10)
            
            if result.success:
                response = json.loads(result.stdout)
                if "login" in response and "message" not in response:
                    print(f"✅ Token valid for user: {response['login']}")
                    return True
            
            print(f"❌ Token validation failed: {result.stdout}")
            return False
            
        except Exception as e:
            print(f"❌ Token validation error: {e}")
            return False
    
    def validate_token_authorizations(self, token: str) -> Dict[str, bool]:
        """Validate GitHub PAT has required authorizations and privileges."""
        authorizations = {}
        
        print("\n🔐 Step 3a: Validating Required Authorizations")
        print("-" * 50)
        
        # Test each required scope
        scope_tests = {
            "repo": {
                "url": "https://api.github.com/user/repos",
                "description": "Repository access (read/write)"
            },
            "read:org": {
                "url": "https://api.github.com/user/orgs",
                "description": "Organization membership access"
            },
            "read:user": {
                "url": "https://api.github.com/user",
                "description": "User profile access"
            },
            "read:project": {
                "url": "https://api.github.com/user/projects",
                "description": "Project access"
            },
            "workflow": {
                "url": "https://api.github.com/user/repos",
                "description": "GitHub Actions workflow access"
            }
        }
        
        for scope, test_config in scope_tests.items():
            try:
                result = safe_execute([
                    'curl', '-s', '-H', f'Authorization: token {token}',
                    test_config["url"]
                ], timeout=10)
                
                if result.success:
                    try:
                        response = json.loads(result.stdout)
                        # Check if we got actual data (not error message)
                        if isinstance(response, (list, dict)) and "message" not in response:
                            authorizations[scope] = True
                            print(f"✅ {scope}: {test_config['description']}")
                        else:
                            authorizations[scope] = False
                            print(f"❌ {scope}: {test_config['description']} - {response.get('message', 'Access denied')}")
                    except json.JSONDecodeError:
                        authorizations[scope] = False
                        print(f"❌ {scope}: {test_config['description']} - Invalid response format")
                else:
                    authorizations[scope] = False
                    print(f"❌ {scope}: {test_config['description']} - HTTP {result.return_code}")
                    
            except Exception as e:
                authorizations[scope] = False
                print(f"❌ {scope}: {test_config['description']} - Error: {e}")
        
        # Check overall authorization status
        required_scopes = ["repo", "read:org", "read:user", "read:project", "workflow"]
        missing_scopes = [scope for scope in required_scopes if not authorizations.get(scope, False)]
        
        if missing_scopes:
            print(f"\n❌ CRITICAL: Missing required authorizations: {', '.join(missing_scopes)}")
            print("🔧 Resolution Required:")
            print("1. Go to GitHub Settings → Developer settings → Personal access tokens")
            print("2. Edit your token or create a new one")
            print("3. Ensure these scopes are selected:")
            for scope in missing_scopes:
                print(f"   ✓ {scope}")
            print("4. Save and regenerate the token")
            return False
        else:
            print(f"\n✅ All required authorizations validated!")
            return True
    
    def facilitate_token_retrieval(self) -> str:
        """Facilitate GitHub PAT retrieval through guided process."""
        print("🔧 GitHub Personal Access Token Configuration Facilitator")
        print("=" * 60)
        
        # Step 1: Check existing token
        existing_token = self.check_existing_token()
        if existing_token:
            return existing_token
        
        print("\n📋 GitHub PAT Setup Required")
        print("-" * 30)
        print("To enable GitHub MCP integration, you need a GitHub Personal Access Token.")
        print(f"Required scopes: {', '.join(self.required_scopes)}")
        
        # Step 2: Guide user to GitHub token creation
        print("\n🚀 Step 1: Create GitHub Personal Access Token")
        print("-" * 45)
        print("1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)")
        print("2. Click 'Generate new token (classic)'")
        print("3. Set expiration (recommend 90 days)")
        print("4. Select these scopes:")
        for scope in self.required_scopes:
            print(f"   ✓ {scope}")
        print("5. Click 'Generate token'")
        print("6. Copy the token immediately (you won't see it again)")
        
        # Step 3: Offer to open browser
        try:
            open_browser = input("\n🌐 Open GitHub token creation page? (y/n): ").lower().strip()
            if open_browser in ['y', 'yes']:
                webbrowser.open("https://github.com/settings/tokens/new")
                print("✅ Opened GitHub token creation page")
        except Exception:
            print("⚠️ Could not open browser automatically")
            print("   Please manually navigate to: https://github.com/settings/tokens/new")
        
        # Step 4: Get token from user
        print("\n🔑 Step 2: Enter Your GitHub Personal Access Token")
        print("-" * 50)
        token = input("Paste your GitHub PAT here: ").strip()
        
        if not token:
            print("❌ No token provided. Configuration cancelled.")
            sys.exit(1)
        
        # Step 5: Validate token
        print("\n🧪 Step 3: Validating Token")
        print("-" * 30)
        if not self.validate_token(token):
            print("❌ Token validation failed. Please check your token and try again.")
            sys.exit(1)
        
        # Step 6: Validate authorizations
        if not self.validate_token_authorizations(token):
            print("❌ Token authorization validation failed. Please fix token permissions and try again.")
            sys.exit(1)
        
        return token
    
    def configure_mcp_json(self, token: str) -> bool:
        """Configure the .cursor/mcp.json file with the GitHub PAT."""
        try:
            # Ensure .cursor directory exists
            self.cursor_config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Load existing config or create new
            if self.cursor_config_path.exists():
                with open(self.cursor_config_path, 'r') as f:
                    config = json.load(f)
            else:
                config = {"mcpServers": {}}
            
            # Update GitHub MCP server configuration
            if "mcpServers" not in config:
                config["mcpServers"] = {}
            
            config["mcpServers"]["github"] = {
                "command": "docker",
                "args": ["run", "-i", "--rm", "--network=host", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN", "ghcr.io/github/github-mcp-server"],
                "env": {
                    "GITHUB_PERSONAL_ACCESS_TOKEN": token
                }
            }
            
            # Save configuration
            with open(self.cursor_config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"✅ GitHub PAT configured in {self.cursor_config_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error configuring MCP JSON: {e}")
            return False
    
    def test_github_mcp_integration(self) -> bool:
        """Test GitHub MCP integration after configuration."""
        try:
            print("\n🧪 Step 4: Testing GitHub MCP Integration")
            print("-" * 45)
            
            # Test Docker GitHub MCP server with safe execution
            test_input = '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}}}'
            
            docker_result = safe_execute([
                'docker', 'run', '--rm', '-i', '-e', 'GITHUB_PERSONAL_ACCESS_TOKEN',
                'ghcr.io/github/github-mcp-server'
            ], timeout=15)
            
            if docker_result.success:
                response = json.loads(docker_result.stdout)
                if "result" in response and "serverInfo" in response["result"]:
                    server_info = response["result"]["serverInfo"]
                    print(f"✅ GitHub MCP Server operational: {server_info['name']} v{server_info['version']}")
                    return True
            
            print(f"❌ GitHub MCP test failed: {docker_result.stderr}")
            return False
            
        except Exception as e:
            print(f"❌ GitHub MCP test error: {e}")
            return False
    
    def run_facilitation(self) -> bool:
        """Run the complete GitHub PAT facilitation process."""
        try:
            # Step 1: Facilitate token retrieval
            token = self.facilitate_token_retrieval()
            
            # Step 2: Configure MCP JSON
            if not self.configure_mcp_json(token):
                return False
            
            # Step 3: Test integration
            if not self.test_github_mcp_integration():
                return False
            
            print("\n🎉 GitHub PAT Configuration Complete!")
            print("=" * 40)
            print("✅ GitHub Personal Access Token configured")
            print("✅ MCP server configuration updated")
            print("✅ GitHub MCP integration tested and operational")
            print("\n📝 Next Steps:")
            print("1. Restart Claude Desktop to load new MCP configuration")
            print("2. Test GitHub integration in Claude Desktop")
            print("3. Run 'make validate-integrations' to verify all systems")
            
            return True
            
        except KeyboardInterrupt:
            print("\n⚠️ Configuration cancelled by user")
            return False
        except Exception as e:
            print(f"❌ Configuration failed: {e}")
            return False

def main():
    """Main facilitation function."""
    facilitator = GitHubPATFacilitator()
    success = facilitator.run_facilitation()
    
    if success:
        print("\n✅ GitHub PAT facilitation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ GitHub PAT facilitation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
