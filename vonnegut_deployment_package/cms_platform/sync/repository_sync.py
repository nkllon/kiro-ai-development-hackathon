"""Repository Synchronization Service"""

from typing import Dict, List, Optional
from pathlib import Path
import hashlib
from datetime import datetime
import git


class RepositorySyncService:
    """Synchronize repository changes with CMS."""

    def __init__(self, repo_path: str, cms_client):
        self.repo_path = Path(repo_path)
        self.cms_client = cms_client
        self.repo = git.Repo(repo_path)

    def get_changed_files(self, since_commit: Optional[str] = None) -> List[Dict]:
        """Get list of changed files since commit."""
        changed_files = []

        if since_commit:
            commits = list(self.repo.iter_commits(f'{since_commit}..HEAD'))
        else:
            commits = list(self.repo.iter_commits(max_count=1))

        for commit in commits:
            for item in commit.tree.traverse():
                if item.type == 'blob':
                    changed_files.append({
                        'path': item.path,
                        'size': item.size,
                        'hash': item.hexsha,
                        'commit': commit.hexsha
                    })

        return changed_files

    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file."""
        hasher = hashlib.sha256()
        with open(self.repo_path / file_path, 'rb') as f:
            hasher.update(f.read())
        return hasher.hexdigest()

    def sync_code_file(self, file_path: str) -> bool:
        """Sync code file to CMS."""
        try:
            full_path = self.repo_path / file_path
            if not full_path.exists():
                return False

            file_hash = self.calculate_file_hash(file_path)
            file_size = full_path.stat().st_size
            language = full_path.suffix.lstrip('.')

            # Check if file already exists in CMS
            existing = self.cms_client.get_code_file_by_path(file_path)

            if existing and existing['content_hash'] == file_hash:
                # No changes, skip
                return True

            # Sync to CMS
            data = {
                'file_path': file_path,
                'content_hash': file_hash,
                'language': language,
                'size_bytes': file_size,
                'updated_at': datetime.now().isoformat()
            }

            if existing:
                self.cms_client.update_code_file(existing['id'], data)
            else:
                self.cms_client.create_code_file(data)

            return True

        except Exception as e:
            print(f"Error syncing file {file_path}: {e}")
            return False

    def sync_document(self, file_path: str) -> bool:
        """Sync markdown document to CMS."""
        try:
            full_path = self.repo_path / file_path
            if not full_path.exists():
                return False

            content = full_path.read_text()
            title = full_path.stem.replace('-', ' ').replace('_', ' ').title()

            # Extract document type from path
            doc_type = 'general'
            if '.kiro/specs/' in file_path:
                doc_type = 'specification'
            elif 'docs/' in file_path:
                doc_type = 'documentation'

            data = {
                'title': title,
                'content': content,
                'document_type': doc_type,
                'updated_at': datetime.now().isoformat()
            }

            # Check if document exists
            existing = self.cms_client.get_document_by_title(title)

            if existing:
                self.cms_client.update_document(existing['id'], data)
            else:
                self.cms_client.create_document(data)

            return True

        except Exception as e:
            print(f"Error syncing document {file_path}: {e}")
            return False

    def sync_specification(self, spec_path: str) -> bool:
        """Sync specification directory to CMS."""
        try:
            spec_dir = self.repo_path / spec_path
            if not spec_dir.is_dir():
                return False

            spec_name = spec_dir.name

            # Read specification files
            requirements_file = spec_dir / 'requirements.md'
            design_file = spec_dir / 'design.md'
            tasks_file = spec_dir / 'tasks.md'

            description = ""
            if requirements_file.exists():
                # Extract first paragraph as description
                content = requirements_file.read_text()
                lines = [l for l in content.split('\n') if l.strip()]
                if lines:
                    description = lines[0][:500]

            data = {
                'name': spec_name,
                'description': description,
                'version': '1.0',
                'status': 'active',
                'updated_at': datetime.now().isoformat()
            }

            # Check if spec exists
            existing = self.cms_client.get_specification_by_name(spec_name)

            if existing:
                self.cms_client.update_specification(existing['id'], data)
            else:
                self.cms_client.create_specification(data)

            return True

        except Exception as e:
            print(f"Error syncing specification {spec_path}: {e}")
            return False

    def perform_full_sync(self) -> Dict:
        """Perform full repository sync."""
        results = {
            'code_files': 0,
            'documents': 0,
            'specifications': 0,
            'errors': []
        }

        # Sync code files
        for file_path in self.repo_path.rglob('*.py'):
            rel_path = file_path.relative_to(self.repo_path)
            if self.sync_code_file(str(rel_path)):
                results['code_files'] += 1

        # Sync documents
        for file_path in self.repo_path.rglob('*.md'):
            rel_path = file_path.relative_to(self.repo_path)
            if self.sync_document(str(rel_path)):
                results['documents'] += 1

        # Sync specifications
        specs_dir = self.repo_path / '.kiro' / 'specs'
        if specs_dir.exists():
            for spec_dir in specs_dir.iterdir():
                if spec_dir.is_dir():
                    rel_path = spec_dir.relative_to(self.repo_path)
                    if self.sync_specification(str(rel_path)):
                        results['specifications'] += 1

        return results
