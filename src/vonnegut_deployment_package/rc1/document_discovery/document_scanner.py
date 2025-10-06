#!/usr/bin/env python3
"""
RC1 Document Scanner
===================

Implements the Document Discovery DAG component for scanning and cataloging
all 1,947 markdown files in the repository.

This is the first critical implementation component that bridges the gap
between planning and actual document processing.
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class DocumentMetadata:
    """Metadata extracted from a document"""
    path: str
    filename: str
    size: int
    created_date: str
    modified_date: str
    hash: str
    line_count: int
    word_count: int
    character_count: int
    file_type: str
    encoding: str


@dataclass
class Document:
    """Representation of a document with metadata and content"""
    path: str
    filename: str
    content: str
    metadata: DocumentMetadata
    category: Optional[str] = None
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class DocumentScanner:
    """
    Document Discovery Engine
    
    Scans the repository for all markdown files and extracts metadata.
    This is the first step in the DAG-driven document management system.
    """
    
    def __init__(self, repository_root: str = "."):
        self.repository_root = Path(repository_root).resolve()
        self.documents: List[Document] = []
        self.scan_results: Dict[str, Any] = {}
        
    def scan_repository(self) -> List[Document]:
        """
        Scan repository for all markdown files
        
        Returns:
            List[Document]: All discovered documents with metadata
        """
        print(f"🔍 Scanning repository: {self.repository_root}")
        
        # Find all markdown files
        markdown_files = list(self.repository_root.rglob("*.md"))
        print(f"📄 Found {len(markdown_files)} markdown files")
        
        documents = []
        for file_path in markdown_files:
            try:
                document = self._process_document(file_path)
                if document:
                    documents.append(document)
            except Exception as e:
                print(f"⚠️ Error processing {file_path}: {e}")
                
        self.documents = documents
        self._generate_scan_results()
        
        print(f"✅ Successfully processed {len(documents)} documents")
        return documents
    
    def _process_document(self, file_path: Path) -> Optional[Document]:
        """Process a single document file"""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Calculate file hash
            file_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            
            # Get file statistics
            stat = file_path.stat()
            
            # Extract metadata
            metadata = DocumentMetadata(
                path=str(file_path.relative_to(self.repository_root)),
                filename=file_path.name,
                size=stat.st_size,
                created_date=datetime.fromtimestamp(stat.st_ctime).isoformat(),
                modified_date=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                hash=file_hash,
                line_count=len(content.splitlines()),
                word_count=len(content.split()),
                character_count=len(content),
                file_type="markdown",
                encoding="utf-8"
            )
            
            # Create document object
            document = Document(
                path=str(file_path.relative_to(self.repository_root)),
                filename=file_path.name,
                content=content,
                metadata=metadata
            )
            
            return document
            
        except Exception as e:
            print(f"❌ Failed to process {file_path}: {e}")
            return None
    
    def _generate_scan_results(self) -> None:
        """Generate scan results summary"""
        if not self.documents:
            return
            
        total_size = sum(doc.metadata.size for doc in self.documents)
        total_lines = sum(doc.metadata.line_count for doc in self.documents)
        total_words = sum(doc.metadata.word_count for doc in self.documents)
        
        # Categorize by filename patterns
        categories = {
            "RC1": len([d for d in self.documents if d.filename.startswith("RC1_")]),
            "README": len([d for d in self.documents if d.filename.upper().startswith("README")]),
            "Task": len([d for d in self.documents if "task" in d.filename.lower()]),
            "Summary": len([d for d in self.documents if "summary" in d.filename.lower()]),
            "Other": len([d for d in self.documents if not any(pattern in d.filename.lower() 
                        for pattern in ["rc1_", "readme", "task", "summary"])])
        }
        
        self.scan_results = {
            "scan_timestamp": datetime.now().isoformat(),
            "repository_root": str(self.repository_root),
            "total_documents": len(self.documents),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "total_lines": total_lines,
            "total_words": total_words,
            "categories": categories,
            "document_hashes": {doc.metadata.hash: doc.metadata.path for doc in self.documents}
        }
    
    def save_scan_results(self, output_path: str = "rc1_scan_results.json") -> None:
        """Save scan results to JSON file"""
        if not self.scan_results:
            print("⚠️ No scan results to save. Run scan_repository() first.")
            return
            
        # Convert documents to serializable format
        documents_data = []
        for doc in self.documents:
            doc_data = {
                "path": doc.path,
                "filename": doc.filename,
                "metadata": asdict(doc.metadata),
                "category": doc.category,
                "dependencies": doc.dependencies,
                "content_preview": doc.content[:500] + "..." if len(doc.content) > 500 else doc.content
            }
            documents_data.append(doc_data)
        
        results_data = {
            "scan_results": self.scan_results,
            "documents": documents_data
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Scan results saved to: {output_path}")
    
    def get_document_by_hash(self, document_hash: str) -> Optional[Document]:
        """Find document by its hash"""
        for doc in self.documents:
            if doc.metadata.hash == document_hash:
                return doc
        return None
    
    def get_documents_by_category(self, category: str) -> List[Document]:
        """Get documents by category"""
        return [doc for doc in self.documents if doc.category == category]
    
    def get_scan_summary(self) -> Dict[str, Any]:
        """Get summary of scan results"""
        return self.scan_results.copy()


def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="RC1 Document Scanner")
    parser.add_argument("--repository-root", default=".", help="Repository root directory")
    parser.add_argument("--output", default="rc1_scan_results.json", help="Output file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Initialize scanner
    scanner = DocumentScanner(args.repository_root)
    
    # Scan repository
    documents = scanner.scan_repository()
    
    # Save results
    scanner.save_scan_results(args.output)
    
    # Print summary
    summary = scanner.get_scan_summary()
    print("\n📊 Scan Summary:")
    print(f"   Total Documents: {summary['total_documents']}")
    print(f"   Total Size: {summary['total_size_mb']} MB")
    print(f"   Total Lines: {summary['total_lines']:,}")
    print(f"   Total Words: {summary['total_words']:,}")
    print("\n📁 Document Categories:")
    for category, count in summary['categories'].items():
        print(f"   {category}: {count}")
    
    if args.verbose:
        print("\n📄 Document List:")
        for doc in documents[:10]:  # Show first 10
            print(f"   {doc.metadata.path} ({doc.metadata.size} bytes)")
        if len(documents) > 10:
            print(f"   ... and {len(documents) - 10} more documents")


if __name__ == "__main__":
    main()
