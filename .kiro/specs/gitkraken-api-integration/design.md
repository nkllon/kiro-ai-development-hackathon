# GitKraken API Integration Design

## Overview

The GitKraken API Integration implements a progressive enhancement model for git operations in the Beast Mode Framework. The system provides a unified git interface that automatically detects and utilizes GitKraken's premium features when available, while maintaining full functionality through standard git for open source developers.

## Architecture

### Core Design Principles

1. **Progressive Enhancement**: Standard git is the baseline, GitKraken API enhances the experience
2. **Transparent Fallback**: Automatic fallback to standard git without user intervention
3. **Unified Interface**: Single API for git operations regardless of underlying implementation
4. **Zero Dependencies**: No required premium licenses for core functionality

### Component Architecture

```
GitOperationsManager
├── GitProvider (Interface)
│   ├── StandardGitProvider (Default)
│   └── GitKrakenProvider (Optional)
├── GitConfigurationManager
├── LicenseDetector
└── OperationFallbackHandler
```

## Components and Interfaces

### GitProvider Interface

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class GitOperationResult:
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    provider_used: str = ""

@dataclass
class BranchInfo:
    name: str
    is_current: bool
    ahead_count: int
    behind_count: int
    last_commit: str
    last_commit_date: str

class GitProvider(ABC):
    """Abstract interface for git operations"""
    
    @abstractmethod
    def get_status(self) -> GitOperationResult:
        """Get repository status"""
        pass
    
    @abstractmethod
    def list_branches(self) -> List[BranchInfo]:
        """List all branches with metadata"""
        pass
    
    @abstractmethod
    def create_branch(self, name: str, from_branch: str = "HEAD") -> GitOperationResult:
        """Create a new branch"""
        pass
    
    @abstractmethod
    def switch_branch(self, name: str) -> GitOperationResult:
        """Switch to a branch"""
        pass
    
    @abstractmethod
    def merge_branch(self, source: str, target: str) -> GitOperationResult:
        """Merge branches"""
        pass
    
    @abstractmethod
    def commit_changes(self, message: str, files: List[str] = None) -> GitOperationResult:
        """Commit changes"""
        pass
    
    @abstractmethod
    def push_changes(self, branch: str = None) -> GitOperationResult:
        """Push changes to remote"""
        pass
    
    @abstractmethod
    def pull_changes(self, branch: str = None) -> GitOperationResult:
        """Pull changes from remote"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is available"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get provider name for logging"""
        pass
```

### StandardGitProvider Implementation

```python
import subprocess
import json
from typing import List, Dict, Any
from .git_provider import GitProvider, GitOperationResult, BranchInfo

class StandardGitProvider(GitProvider):
    """Standard git command-line implementation"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
    
    def get_status(self) -> GitOperationResult:
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain=v1"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            status_data = {
                "clean": len(result.stdout.strip()) == 0,
                "files": self._parse_status_output(result.stdout)
            }
            
            return GitOperationResult(
                success=True,
                message="Status retrieved successfully",
                data=status_data,
                provider_used="standard_git"
            )
        except subprocess.CalledProcessError as e:
            return GitOperationResult(
                success=False,
                message=f"Git status failed: {e.stderr}",
                provider_used="standard_git"
            )
    
    def list_branches(self) -> List[BranchInfo]:
        try:
            # Get branch list with tracking info
            result = subprocess.run(
                ["git", "branch", "-vv", "--all"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            return self._parse_branch_output(result.stdout)
        except subprocess.CalledProcessError:
            return []
    
    def is_available(self) -> bool:
        try:
            subprocess.run(
                ["git", "--version"],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def get_provider_name(self) -> str:
        return "Standard Git"
    
    # Additional implementation methods...
```

### GitKrakenProvider Implementation

```python
import requests
import json
from typing import List, Dict, Any, Optional
from .git_provider import GitProvider, GitOperationResult, BranchInfo

class GitKrakenProvider(GitProvider):
    """GitKraken API implementation"""
    
    def __init__(self, repo_path: str = ".", api_key: str = None):
        self.repo_path = repo_path
        self.api_key = api_key
        self.base_url = "https://api.gitkraken.com/v1"
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
    
    def get_status(self) -> GitOperationResult:
        try:
            response = self.session.get(f"{self.base_url}/repos/{self.repo_path}/status")
            response.raise_for_status()
            
            data = response.json()
            return GitOperationResult(
                success=True,
                message="Status retrieved via GitKraken API",
                data=data,
                provider_used="gitkraken_api"
            )
        except requests.RequestException as e:
            return GitOperationResult(
                success=False,
                message=f"GitKraken API error: {str(e)}",
                provider_used="gitkraken_api"
            )
    
    def is_available(self) -> bool:
        if not self.api_key:
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/user")
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def get_provider_name(self) -> str:
        return "GitKraken API"
    
    # Additional implementation methods...
```

### GitOperationsManager

```python
from typing import Optional, List
from .providers import GitProvider, StandardGitProvider, GitKrakenProvider
from .license_detector import LicenseDetector
from .config_manager import GitConfigurationManager

class GitOperationsManager:
    """Main interface for git operations with automatic provider selection"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.config = GitConfigurationManager()
        self.license_detector = LicenseDetector()
        self.providers: List[GitProvider] = []
        self.active_provider: Optional[GitProvider] = None
        
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available providers in priority order"""
        
        # Always add standard git as fallback
        standard_provider = StandardGitProvider(self.repo_path)
        self.providers.append(standard_provider)
        
        # Add GitKraken if available and enabled
        if self.config.is_gitkraken_enabled():
            api_key = self.license_detector.get_gitkraken_api_key()
            if api_key:
                gitkraken_provider = GitKrakenProvider(self.repo_path, api_key)
                if gitkraken_provider.is_available():
                    self.providers.insert(0, gitkraken_provider)  # Higher priority
        
        # Set active provider (first available)
        self.active_provider = self.providers[0] if self.providers else None
    
    def get_status(self):
        """Get repository status using best available provider"""
        return self._execute_with_fallback("get_status")
    
    def list_branches(self):
        """List branches using best available provider"""
        return self._execute_with_fallback("list_branches")
    
    def _execute_with_fallback(self, method_name: str, *args, **kwargs):
        """Execute method with automatic fallback to next provider"""
        
        for provider in self.providers:
            try:
                method = getattr(provider, method_name)
                result = method(*args, **kwargs)
                
                # If operation succeeded or this is the last provider, return result
                if hasattr(result, 'success') and result.success:
                    return result
                elif provider == self.providers[-1]:  # Last provider
                    return result
                    
            except Exception as e:
                # Log error and try next provider
                print(f"Provider {provider.get_provider_name()} failed: {e}")
                continue
        
        # All providers failed
        return GitOperationResult(
            success=False,
            message="All git providers failed",
            provider_used="none"
        )
```

## Data Models

### Configuration Model

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class GitConfiguration:
    gitkraken_enabled: bool = False
    gitkraken_api_key: Optional[str] = None
    fallback_to_standard: bool = True
    preferred_provider: str = "auto"  # "auto", "standard", "gitkraken"
    operation_timeout: int = 30
    retry_attempts: int = 3
```

### License Detection Model

```python
@dataclass
class LicenseInfo:
    has_gitkraken_license: bool
    license_type: Optional[str] = None
    api_key: Optional[str] = None
    expires_at: Optional[str] = None
```

## Error Handling

### Fallback Strategy

1. **Primary Provider Failure**: Automatically try next available provider
2. **All Providers Fail**: Return detailed error with attempted providers
3. **Configuration Errors**: Log warning and use standard git
4. **Network Issues**: Implement exponential backoff for API calls

### Error Response Format

```python
@dataclass
class GitError:
    error_code: str
    message: str
    provider_attempted: str
    fallback_used: bool
    suggestions: List[str]
```

## Testing Strategy

### Unit Tests

- Test each provider independently
- Mock GitKraken API responses
- Test fallback mechanisms
- Verify configuration handling

### Integration Tests

- Test with real git repositories
- Test GitKraken API integration (when available)
- Test provider switching scenarios
- Test error handling and recovery

### Compatibility Tests

- Test on systems without GitKraken
- Test with expired licenses
- Test network failure scenarios
- Test with various git repository states

## Implementation Notes

### Progressive Enhancement Implementation

1. **Baseline First**: Implement all functionality with standard git
2. **Enhancement Layer**: Add GitKraken features as optional enhancements
3. **Transparent Switching**: Users shouldn't notice provider changes
4. **Graceful Degradation**: Always fallback to working functionality

### Configuration Management

- Environment variables for API keys
- Configuration file for preferences
- Runtime detection of available providers
- User preference persistence