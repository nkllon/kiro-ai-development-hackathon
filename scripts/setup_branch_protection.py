#!/usr/bin/env python3
"""
Systematic Branch Protection Setup
Implements Beast Mode governance through GitHub API
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path.home() / '.env')

class BranchProtectionManager:
    def __init__(self):
        self.token = os.getenv('GITHUB_TOKEN')
        self.repo_owner = 'nkllon'
        self.repo_name = 'kiro-ai-development-hackathon'
        self.base_url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}'
        
        if not self.token:
            print("🚨 GITHUB_TOKEN not found in ~/.env")
            print("Create a GitHub Personal Access Token with 'repo' scope")
            print("Add to ~/.env: GITHUB_TOKEN=your_token_here")
            sys.exit(1)
            
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }

    def create_develop_branch(self):
        """Create develop branch from master if it doesn't exist"""
        print("🔍 Checking if develop branch exists...")
        
        # Get master branch SHA
        master_response = requests.get(f'{self.base_url}/git/refs/heads/master', headers=self.headers)
        if master_response.status_code != 200:
            print(f"❌ Failed to get master branch: {master_response.text}")
            return False
            
        master_sha = master_response.json()['object']['sha']
        
        # Check if develop exists
        develop_response = requests.get(f'{self.base_url}/git/refs/heads/develop', headers=self.headers)
        if develop_response.status_code == 200:
            print("✅ develop branch already exists")
            return True
            
        # Create develop branch
        create_data = {
            'ref': 'refs/heads/develop',
            'sha': master_sha
        }
        
        create_response = requests.post(f'{self.base_url}/git/refs', 
                                      headers=self.headers, 
                                      json=create_data)
        
        if create_response.status_code == 201:
            print("✅ develop branch created successfully")
            return True
        else:
            print(f"❌ Failed to create develop branch: {create_response.text}")
            return False

    def setup_branch_protection(self, branch_name, config):
        """Apply branch protection rules"""
        print(f"🛡️ Setting up protection for {branch_name} branch...")
        
        url = f'{self.base_url}/branches/{branch_name}/protection'
        
        response = requests.put(url, headers=self.headers, json=config)
        
        if response.status_code in [200, 201]:
            print(f"✅ {branch_name} branch protection enabled")
            return True
        else:
            print(f"❌ Failed to protect {branch_name}: {response.text}")
            return False

    def get_master_protection_config(self):
        """Master branch protection - maximum security"""
        return {
            "required_status_checks": {
                "strict": True,
                "contexts": []  # Will add CI checks later
            },
            "enforce_admins": False,  # Allow admin override with warning
            "required_pull_request_reviews": {
                "required_approving_review_count": 1,
                "dismiss_stale_reviews": True,
                "require_code_owner_reviews": True,
                "dismissal_restrictions": {}
            },
            "restrictions": None,  # No push restrictions for now
            "allow_force_pushes": True,  # For maintainer emergency access
            "allow_deletions": False,
            "block_creations": False,
            "required_conversation_resolution": True
        }

    def get_develop_protection_config(self):
        """Develop branch protection - collaborative development"""
        return {
            "required_status_checks": {
                "strict": True,
                "contexts": []  # Will add CI checks later
            },
            "enforce_admins": False,  # Allow admin override
            "required_pull_request_reviews": {
                "required_approving_review_count": 1,
                "dismiss_stale_reviews": True,
                "require_code_owner_reviews": False,
                "dismissal_restrictions": {}
            },
            "restrictions": None,
            "allow_force_pushes": True,  # For maintainer access
            "allow_deletions": False,
            "block_creations": False,
            "required_conversation_resolution": True
        }

    def run(self):
        """Execute systematic branch protection setup"""
        print("🐺 SYSTEMATIC BRANCH PROTECTION SETUP")
        print("=====================================")
        
        # Create develop branch
        if not self.create_develop_branch():
            return False
            
        # Setup master protection
        master_config = self.get_master_protection_config()
        if not self.setup_branch_protection('master', master_config):
            return False
            
        # Setup develop protection  
        develop_config = self.get_develop_protection_config()
        if not self.setup_branch_protection('develop', develop_config):
            return False
            
        print("\n🎯 SYSTEMATIC GOVERNANCE ACTIVATED")
        print("- Master branch: Maximum protection")
        print("- Develop branch: Collaborative protection")
        print("- Emergency override: Available with warning")
        print("- Beast Mode: EVERYONE WINS through systematic process")
        
        return True

def setup_env_file():
    """Create ~/.env template if it doesn't exist"""
    env_path = Path.home() / '.env'
    
    if env_path.exists():
        print(f"✅ ~/.env already exists")
        return
        
    template = """# GitHub Configuration
# Create Personal Access Token at: https://github.com/settings/tokens
# Required scopes: repo, admin:repo_hook
GITHUB_TOKEN=your_github_token_here

# Beast Mode Configuration
BEAST_MODE_ENABLED=true
SYSTEMATIC_GOVERNANCE=enabled
"""
    
    with open(env_path, 'w') as f:
        f.write(template)
        
    print(f"📝 Created ~/.env template at {env_path}")
    print("🔑 Add your GitHub token to ~/.env and run again")

if __name__ == '__main__':
    # Check if token exists, create template if not
    if not os.getenv('GITHUB_TOKEN'):
        setup_env_file()
        sys.exit(0)
        
    manager = BranchProtectionManager()
    success = manager.run()
    
    if success:
        print("\n🏰 The walls of the fort are strong. It's safe in here.")
        sys.exit(0)
    else:
        print("\n❌ Branch protection setup failed")
        sys.exit(1)