"""
Beast Mode Spore Management System

Handles spore storage, retrieval, validation, and distribution.
"""

import json
import os
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field, ValidationError
import yaml

from .models import BeastModeMessage, MessageType


logger = logging.getLogger(__name__)


class SporeMetadata(BaseModel):
    """Metadata for a Beast Mode spore"""

    name: str
    version: str
    author: str
    description: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list)
    capabilities_required: List[str] = Field(default_factory=list)
    compatibility_version: str = "1.0"
    checksum: str = ""
    file_path: str = ""
    validation_criteria: Dict[str, Any] = Field(default_factory=dict)
    usage_count: int = 0
    success_rate: float = 0.0


class SporeContent(BaseModel):
    """Complete spore with metadata and implementation"""

    metadata: SporeMetadata
    implementation: str
    validation_tests: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)


class SporeManager:
    """Manages spore storage, retrieval, validation, and distribution"""

    def __init__(self, spore_directory: str = "spores"):
        """
        Initialize SporeManager

        Args:
            spore_directory: Directory to store spores
        """
        self.spore_directory = Path(spore_directory)
        self.spore_directory.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        self.metadata_dir = self.spore_directory / "metadata"
        self.content_dir = self.spore_directory / "content"
        self.versions_dir = self.spore_directory / "versions"

        for directory in [self.metadata_dir, self.content_dir, self.versions_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        self._spore_cache: Dict[str, SporeContent] = {}
        self._load_existing_spores()

    def _load_existing_spores(self) -> None:
        """Load existing spores from disk into cache"""
        try:
            for metadata_file in self.metadata_dir.glob("*.json"):
                spore_name = metadata_file.stem
                try:
                    spore = self.load_spore(spore_name)
                    if spore:
                        self._spore_cache[spore_name] = SporeContent(**spore)
                except Exception as e:
                    logger.warning(f"Failed to load spore {spore_name}: {e}")
        except Exception as e:
            logger.error(f"Failed to load existing spores: {e}")

    def _calculate_checksum(self, content: str) -> str:
        """Calculate SHA-256 checksum of content"""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _get_spore_paths(self, spore_name: str) -> Tuple[Path, Path]:
        """Get metadata and content file paths for a spore"""
        metadata_path = self.metadata_dir / f"{spore_name}.json"
        content_path = self.content_dir / f"{spore_name}.py"
        return metadata_path, content_path

    def save_spore(self, spore_content: str, metadata: Dict[str, Any]) -> str:
        """
        Save a spore with metadata and content

        Args:
            spore_content: The implementation content of the spore
            metadata: Spore metadata dictionary

        Returns:
            str: The spore identifier/name

        Raises:
            ValueError: If spore validation fails
        """
        try:
            # Validate and create metadata
            spore_metadata = SporeMetadata(**metadata)
            spore_name = spore_metadata.name

            # Calculate checksum
            checksum = self._calculate_checksum(spore_content)
            spore_metadata.checksum = checksum
            spore_metadata.updated_at = datetime.now()

            # Get file paths
            metadata_path, content_path = self._get_spore_paths(spore_name)
            spore_metadata.file_path = str(content_path)

            # Validate spore content
            if not self.validate_spore(spore_content):
                raise ValueError(f"Spore validation failed for {spore_name}")

            # Handle versioning if spore already exists
            if spore_name in self._spore_cache:
                self._create_version_backup(spore_name)

            # Save metadata
            with open(metadata_path, "w") as f:
                json.dump(spore_metadata.model_dump(), f, indent=2, default=str)

            # Save content
            with open(content_path, "w") as f:
                f.write(spore_content)

            # Create complete spore object
            spore = SporeContent(metadata=spore_metadata, implementation=spore_content)

            # Update cache
            self._spore_cache[spore_name] = spore

            logger.info(f"Successfully saved spore: {spore_name}")
            return spore_name

        except ValidationError as e:
            logger.error(f"Metadata validation failed: {e}")
            raise ValueError(f"Invalid spore metadata: {e}")
        except Exception as e:
            logger.error(f"Failed to save spore: {e}")
            raise

    def load_spore(self, spore_name: str) -> Optional[Dict[str, Any]]:
        """
        Load a spore by name

        Args:
            spore_name: Name of the spore to load

        Returns:
            Dict containing spore data or None if not found
        """
        try:
            # Check cache first
            if spore_name in self._spore_cache:
                spore = self._spore_cache[spore_name]
                return spore.model_dump()

            # Load from disk
            metadata_path, content_path = self._get_spore_paths(spore_name)

            if not metadata_path.exists() or not content_path.exists():
                logger.warning(f"Spore not found: {spore_name}")
                return None

            # Load metadata
            with open(metadata_path, "r") as f:
                metadata_dict = json.load(f)

            # Load content
            with open(content_path, "r") as f:
                content = f.read()

            # Verify checksum
            expected_checksum = metadata_dict.get("checksum", "")
            actual_checksum = self._calculate_checksum(content)

            if expected_checksum and expected_checksum != actual_checksum:
                logger.warning(f"Checksum mismatch for spore {spore_name}")

            # Create spore object
            metadata = SporeMetadata(**metadata_dict)
            spore = SporeContent(metadata=metadata, implementation=content)

            # Update cache
            self._spore_cache[spore_name] = spore

            return spore.model_dump()

        except Exception as e:
            logger.error(f"Failed to load spore {spore_name}: {e}")
            return None

    def list_spores(self) -> List[Dict[str, Any]]:
        """
        List all available spores with their metadata

        Returns:
            List of spore metadata dictionaries
        """
        spores = []

        try:
            # Get all spores from cache and disk
            all_spore_names = set(self._spore_cache.keys())

            # Add spores from disk that might not be in cache
            for metadata_file in self.metadata_dir.glob("*.json"):
                all_spore_names.add(metadata_file.stem)

            for spore_name in all_spore_names:
                spore_data = self.load_spore(spore_name)
                if spore_data:
                    # Return just metadata for listing
                    spores.append(spore_data["metadata"])

            # Sort by name
            spores.sort(key=lambda x: x["name"])

        except Exception as e:
            logger.error(f"Failed to list spores: {e}")

        return spores

    def validate_spore(self, spore_content: str) -> bool:
        """
        Validate spore content for basic syntax and structure

        Args:
            spore_content: The spore implementation content

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Basic Python syntax validation
            compile(spore_content, "<spore>", "exec")

            # Check for required spore structure
            required_elements = [
                "def execute(",  # Must have an execute function
                "class",  # Should define at least one class
            ]

            has_required = any(
                element in spore_content for element in required_elements
            )

            if not has_required:
                logger.warning(
                    "Spore missing required structure (execute function or class)"
                )
                return False

            # Check for dangerous operations (basic security)
            dangerous_patterns = [
                "import os",
                "import subprocess",
                "exec(",
                "eval(",
                "__import__",
                "open(",
            ]

            for pattern in dangerous_patterns:
                if pattern in spore_content:
                    logger.warning(
                        f"Spore contains potentially dangerous pattern: {pattern}"
                    )
                    # Don't fail validation, but log warning

            return True

        except SyntaxError as e:
            logger.error(f"Spore syntax error: {e}")
            return False
        except Exception as e:
            logger.error(f"Spore validation error: {e}")
            return False

    def _create_version_backup(self, spore_name: str) -> None:
        """Create a versioned backup of an existing spore"""
        try:
            if spore_name not in self._spore_cache:
                return

            current_spore = self._spore_cache[spore_name]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            version_name = f"{spore_name}_v{timestamp}"

            # Create version directory
            version_dir = self.versions_dir / version_name
            version_dir.mkdir(parents=True, exist_ok=True)

            # Copy current files to version directory
            metadata_path, content_path = self._get_spore_paths(spore_name)

            if metadata_path.exists():
                version_metadata = version_dir / "metadata.json"
                version_metadata.write_text(metadata_path.read_text())

            if content_path.exists():
                version_content = version_dir / "content.py"
                version_content.write_text(content_path.read_text())

            logger.info(f"Created version backup: {version_name}")

        except Exception as e:
            logger.error(f"Failed to create version backup for {spore_name}: {e}")

    def get_spore_versions(self, spore_name: str) -> List[str]:
        """
        Get all versions of a spore

        Args:
            spore_name: Name of the spore

        Returns:
            List of version identifiers
        """
        versions = []
        try:
            version_pattern = f"{spore_name}_v*"
            for version_dir in self.versions_dir.glob(version_pattern):
                if version_dir.is_dir():
                    versions.append(version_dir.name)

            versions.sort(reverse=True)  # Most recent first

        except Exception as e:
            logger.error(f"Failed to get versions for {spore_name}: {e}")

        return versions

    def delete_spore(self, spore_name: str) -> bool:
        """
        Delete a spore and its versions

        Args:
            spore_name: Name of the spore to delete

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Remove from cache
            if spore_name in self._spore_cache:
                del self._spore_cache[spore_name]

            # Remove files
            metadata_path, content_path = self._get_spore_paths(spore_name)

            if metadata_path.exists():
                metadata_path.unlink()

            if content_path.exists():
                content_path.unlink()

            # Remove versions
            version_pattern = f"{spore_name}_v*"
            for version_dir in self.versions_dir.glob(version_pattern):
                if version_dir.is_dir():
                    for file in version_dir.iterdir():
                        file.unlink()
                    version_dir.rmdir()

            logger.info(f"Successfully deleted spore: {spore_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete spore {spore_name}: {e}")
            return False

    def search_spores(
        self, query: str, tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search spores by name, description, or tags

        Args:
            query: Search query string
            tags: Optional list of tags to filter by

        Returns:
            List of matching spore metadata
        """
        results = []

        try:
            all_spores = self.list_spores()

            for spore in all_spores:
                # Check query match
                query_match = (
                    query.lower() in spore["name"].lower()
                    or query.lower() in spore["description"].lower()
                )

                # Check tag match
                tag_match = True
                if tags:
                    spore_tags = spore.get("tags", [])
                    tag_match = any(tag in spore_tags for tag in tags)

                if query_match and tag_match:
                    results.append(spore)

        except Exception as e:
            logger.error(f"Failed to search spores: {e}")

        return results

    def update_spore_stats(self, spore_name: str, success: bool) -> None:
        """
        Update spore usage statistics

        Args:
            spore_name: Name of the spore
            success: Whether the spore execution was successful
        """
        try:
            if spore_name not in self._spore_cache:
                return

            spore = self._spore_cache[spore_name]
            metadata = spore.metadata

            # Update usage count
            metadata.usage_count += 1

            # Update success rate
            if metadata.usage_count == 1:
                metadata.success_rate = 1.0 if success else 0.0
            else:
                # Calculate new success rate
                total_successes = metadata.success_rate * (metadata.usage_count - 1)
                if success:
                    total_successes += 1
                metadata.success_rate = total_successes / metadata.usage_count

            # Save updated metadata
            metadata_path, _ = self._get_spore_paths(spore_name)
            with open(metadata_path, "w") as f:
                json.dump(metadata.model_dump(), f, indent=2, default=str)

        except Exception as e:
            logger.error(f"Failed to update stats for {spore_name}: {e}")

    def export_spore(self, spore_name: str, export_path: str) -> bool:
        """
        Export a spore to a file for sharing

        Args:
            spore_name: Name of the spore to export
            export_path: Path to export the spore to

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            spore_data = self.load_spore(spore_name)
            if not spore_data:
                return False

            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)

            with open(export_file, "w") as f:
                json.dump(spore_data, f, indent=2, default=str)

            logger.info(f"Exported spore {spore_name} to {export_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export spore {spore_name}: {e}")
            return False

    def import_spore(self, import_path: str) -> Optional[str]:
        """
        Import a spore from a file

        Args:
            import_path: Path to the spore file to import

        Returns:
            str: Name of imported spore or None if failed
        """
        try:
            import_file = Path(import_path)
            if not import_file.exists():
                logger.error(f"Import file not found: {import_path}")
                return None

            with open(import_file, "r") as f:
                spore_data = json.load(f)

            # Extract metadata and implementation
            metadata = spore_data["metadata"]
            implementation = spore_data["implementation"]

            # Save the imported spore
            spore_name = self.save_spore(implementation, metadata)

            logger.info(f"Imported spore: {spore_name}")
            return spore_name

        except Exception as e:
            logger.error(f"Failed to import spore from {import_path}: {e}")
            return None
