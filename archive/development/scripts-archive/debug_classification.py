#!/usr/bin/env python3
"""Debug content classification issue"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.repository_discovery.core.content_metadata_extractor import ContentMetadataExtractor

def main():
    extractor = ContentMetadataExtractor()
    
    test_files = [
        Path("src/rm_ddd/core/unified_reflective_module.py"),  # Source code
        Path(".kiro/specs/repository-content-discovery-indexing/requirements.md"),  # Spec
        Path("pyproject.toml"),  # Config
        Path("Makefile")  # Script
    ]
    
    for file_path in test_files:
        if file_path.exists():
            result = extractor.extract_metadata(file_path)
            print(f"File: {file_path}")
            print(f"  Success: {result.success}")
            if result.success and result.metadata:
                print(f"  File Type: {result.metadata.file_type}")
                print(f"  MIME Type: {result.metadata.mime_type}")
            else:
                print(f"  Error: {result.error_message}")
            print()

if __name__ == "__main__":
    main()