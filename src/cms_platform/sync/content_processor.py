#!/usr/bin/env python3
"""
Content Processing Pipeline
Automated content extraction and processing from repositories.
"""

import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import git
import tempfile
import shutil

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class ContentProcessor(ReflectiveModule):
    """Content processing pipeline for repository synchronization."""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = {
            '.md': 'markdown',
            '.txt': 'text',
            '.json': 'json',
            '.yml': 'yaml',
            '.yaml': 'yaml',
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.rst': 'restructuredtext'
        }
    
    async def process_repository(self, repository_info: Dict[str, Any]) -> Dict[str, Any]:
        """Process repository content."""
        try:
            # Clone repository to temporary directory
            temp_dir = await self._clone_repository(repository_info)
            
            if not temp_dir:
                return {"status": "error", "message": "Failed to clone repository"}
            
            try:
                # Extract content from repository
                extracted_content = await self._extract_content(temp_dir, repository_info)
                
                # Process and categorize content
                processed_content = await self._process_content(extracted_content)
                
                # Store processed content
                storage_result = await self._store_content(processed_content, repository_info)
                
                return {
                    "status": "success",
                    "repository": repository_info["name"],
                    "files_processed": len(processed_content),
                    "storage_result": storage_result,
                    "timestamp": datetime.now().isoformat()
                }
                
            finally:
                # Cleanup temporary directory
                if temp_dir and Path(temp_dir).exists():
                    shutil.rmtree(temp_dir)
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _clone_repository(self, repository_info: Dict[str, Any]) -> Optional[str]:
        """Clone repository to temporary directory."""
        try:
            temp_dir = tempfile.mkdtemp(prefix="cms_repo_")
            
            # Clone repository
            git.Repo.clone_from(
                repository_info["url"],
                temp_dir,
                branch=repository_info.get("branch", "main"),
                depth=1  # Shallow clone for efficiency
            )
            
            return temp_dir
            
        except Exception as e:
            print(f"Repository clone error: {e}")
            return None
    
    async def _extract_content(self, repo_path: str, repository_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract content from repository files."""
        extracted_files = []
        repo_path_obj = Path(repo_path)
        
        for file_path in repo_path_obj.rglob("*"):
            if file_path.is_file() and not self._should_ignore_file(file_path):
                try:
                    content = self._read_file_content(file_path)
                    if content:
                        relative_path = file_path.relative_to(repo_path_obj)
                        
                        file_info = {
                            "file_path": str(relative_path),
                            "file_name": file_path.name,
                            "file_type": self._get_file_type(file_path),
                            "content": content,
                            "size": file_path.stat().st_size,
                            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                        }
                        
                        extracted_files.append(file_info)
                        
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")
                    continue
        
        return extracted_files
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored."""
        ignore_patterns = [
            '.git', '__pycache__', '.pytest_cache', 'node_modules',
            '.DS_Store', '.env', '.venv', 'venv', '.idea', '.vscode'
        ]
        
        # Check if any part of the path contains ignore patterns
        for part in file_path.parts:
            if any(pattern in part for pattern in ignore_patterns):
                return True
        
        # Check file size (ignore files > 1MB)
        try:
            if file_path.stat().st_size > 1024 * 1024:
                return True
        except:
            return True
        
        return False
    
    def _read_file_content(self, file_path: Path) -> Optional[str]:
        """Read file content safely."""
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                # Try latin-1 as fallback
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except:
                return None
        except Exception:
            return None
    
    def _get_file_type(self, file_path: Path) -> str:
        """Get file type based on extension."""
        extension = file_path.suffix.lower()
        return self.supported_extensions.get(extension, 'other')
    
    async def _process_content(self, extracted_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and categorize extracted content."""
        processed_files = []
        
        for file_info in extracted_files:
            # Determine stakeholder type based on file content and path
            stakeholder_type = self._determine_stakeholder_type(file_info)
            
            # Extract metadata
            metadata = self._extract_metadata(file_info)
            
            # Create processed content entry
            processed_file = {
                **file_info,
                "stakeholder_type": stakeholder_type,
                "metadata": metadata,
                "processed_at": datetime.now().isoformat()
            }
            
            processed_files.append(processed_file)
        
        return processed_files
    
    def _determine_stakeholder_type(self, file_info: Dict[str, Any]) -> str:
        """Determine stakeholder type based on file characteristics."""
        file_path = file_info["file_path"].lower()
        content = file_info["content"].lower()
        
        # Developer-focused files
        if any(keyword in file_path for keyword in ['src/', 'lib/', 'test/', 'spec/']):
            return "developer"
        
        # DevOps-focused files
        if any(keyword in file_path for keyword in ['deploy', 'docker', 'k8s', 'terraform', 'ansible']):
            return "devops"
        
        # Architecture-focused files
        if any(keyword in file_path for keyword in ['arch', 'design', 'adr/', 'rfc/']):
            return "architect"
        
        # Executive-focused files
        if any(keyword in file_path for keyword in ['business', 'strategy', 'roadmap', 'budget']):
            return "executive"
        
        # Content-based detection
        if any(keyword in content for keyword in ['deployment', 'infrastructure', 'monitoring']):
            return "devops"
        elif any(keyword in content for keyword in ['architecture', 'design pattern', 'system design']):
            return "architect"
        elif any(keyword in content for keyword in ['roi', 'budget', 'business case']):
            return "executive"
        else:
            return "developer"  # Default
    
    def _extract_metadata(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from file content."""
        metadata = {
            "word_count": len(file_info["content"].split()),
            "line_count": len(file_info["content"].splitlines()),
            "has_code": self._contains_code(file_info),
            "has_documentation": self._contains_documentation(file_info),
            "complexity_score": self._calculate_complexity(file_info)
        }
        
        return metadata
    
    def _contains_code(self, file_info: Dict[str, Any]) -> bool:
        """Check if file contains code."""
        code_indicators = ['def ', 'function ', 'class ', 'import ', 'from ', '#!/']
        content = file_info["content"]
        return any(indicator in content for indicator in code_indicators)
    
    def _contains_documentation(self, file_info: Dict[str, Any]) -> bool:
        """Check if file contains documentation."""
        doc_indicators = ['# ', '## ', '### ', 'docstring', 'comment', '/*', '<!--']
        content = file_info["content"]
        return any(indicator in content for indicator in doc_indicators)
    
    def _calculate_complexity(self, file_info: Dict[str, Any]) -> int:
        """Calculate content complexity score (1-10)."""
        content = file_info["content"]
        
        # Simple complexity calculation based on various factors
        factors = [
            len(content.splitlines()),  # Line count
            len(content.split()),       # Word count
            content.count('{'),         # Brace count (code complexity)
            content.count('if '),       # Conditional statements
            content.count('for '),      # Loops
            content.count('class '),    # Classes
            content.count('def ')       # Functions
        ]
        
        # Normalize to 1-10 scale
        complexity = min(10, max(1, sum(factors) // 100))
        return complexity
    
    async def _store_content(self, processed_content: List[Dict[str, Any]], repository_info: Dict[str, Any]) -> Dict[str, Any]:
        """Store processed content."""
        try:
            # Store in JSON file (in real implementation, this would go to database)
            storage_file = Path(f"src/cms_platform/sync/processed_content_{repository_info['name']}.json")
            storage_file.parent.mkdir(parents=True, exist_ok=True)
            
            storage_data = {
                "repository": repository_info,
                "processed_at": datetime.now().isoformat(),
                "content": processed_content
            }
            
            with open(storage_file, 'w') as f:
                json.dump(storage_data, f, indent=2)
            
            return {
                "status": "success",
                "files_stored": len(processed_content),
                "storage_location": str(storage_file)
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
