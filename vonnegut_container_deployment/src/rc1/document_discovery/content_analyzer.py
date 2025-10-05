#!/usr/bin/env python3
"""
RC1 Content Analyzer
===================

Implements the Content Analysis Engine for analyzing document content,
detecting dependencies, and identifying duplicates.

Part of the Beast Mode parallel execution orchestration.
"""

import re
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Set, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ContentAnalysis:
    """Analysis results for document content"""
    document_path: str
    content_hash: str
    word_count: int
    line_count: int
    heading_structure: List[Dict[str, Any]]
    links: List[Dict[str, str]]
    dependencies: List[str]
    topics: List[str]
    complexity_score: float
    quality_score: float
    readability_score: float


@dataclass
class DuplicateGroup:
    """Group of documents with similar content"""
    group_id: str
    documents: List[str]
    similarity_score: float
    common_content: str
    duplicate_type: str  # "exact", "near", "structural"


class ContentAnalyzer:
    """
    Content Analysis Engine
    
    Analyzes document content for structure, dependencies, and quality.
    Part of the Beast Mode parallel execution system.
    """
    
    def __init__(self, scan_results_path: str = "rc1_scan_results.json"):
        self.scan_results_path = Path(scan_results_path)
        self.documents = []
        self.content_analyses = []
        self.duplicate_groups = []
        self.dependency_graph = {}
        
    def load_scan_results(self) -> bool:
        """Load document scan results"""
        if not self.scan_results_path.exists():
            print(f"❌ Scan results not found: {self.scan_results_path}")
            return False
            
        try:
            with open(self.scan_results_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.documents = data.get('documents', [])
                print(f"📄 Loaded {len(self.documents)} documents for analysis")
                return True
        except Exception as e:
            print(f"❌ Error loading scan results: {e}")
            return False
    
    def analyze_all_documents(self) -> List[ContentAnalysis]:
        """Analyze content of all documents"""
        if not self.documents:
            print("⚠️ No documents loaded. Run load_scan_results() first.")
            return []
        
        print(f"🔍 Analyzing content of {len(self.documents)} documents...")
        
        analyses = []
        for i, doc_data in enumerate(self.documents):
            try:
                analysis = self._analyze_document_content(doc_data)
                if analysis:
                    analyses.append(analysis)
                    
                if (i + 1) % 100 == 0:
                    print(f"   Processed {i + 1}/{len(self.documents)} documents")
                    
            except Exception as e:
                print(f"⚠️ Error analyzing {doc_data.get('path', 'unknown')}: {e}")
        
        self.content_analyses = analyses
        print(f"✅ Content analysis complete: {len(analyses)} documents analyzed")
        return analyses
    
    def _analyze_document_content(self, doc_data: Dict[str, Any]) -> Optional[ContentAnalysis]:
        """Analyze content of a single document"""
        try:
            content = doc_data.get('content_preview', '') + doc_data.get('content', '')
            if not content:
                return None
            
            # Basic content analysis
            word_count = len(content.split())
            line_count = len(content.splitlines())
            content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            
            # Extract structure
            heading_structure = self._extract_heading_structure(content)
            links = self._extract_links(content)
            dependencies = self._extract_dependencies(content, doc_data['path'])
            topics = self._extract_topics(content)
            
            # Calculate scores
            complexity_score = self._calculate_complexity_score(content, heading_structure)
            quality_score = self._calculate_quality_score(content, links, heading_structure)
            readability_score = self._calculate_readability_score(content, word_count, line_count)
            
            return ContentAnalysis(
                document_path=doc_data['path'],
                content_hash=content_hash,
                word_count=word_count,
                line_count=line_count,
                heading_structure=heading_structure,
                links=links,
                dependencies=dependencies,
                topics=topics,
                complexity_score=complexity_score,
                quality_score=quality_score,
                readability_score=readability_score
            )
            
        except Exception as e:
            print(f"⚠️ Error analyzing document content: {e}")
            return None
    
    def _extract_heading_structure(self, content: str) -> List[Dict[str, Any]]:
        """Extract markdown heading structure"""
        headings = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines):
            # Match markdown headings (# ## ### etc.)
            match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            if match:
                level = len(match.group(1))
                text = match.group(2).strip()
                headings.append({
                    'level': level,
                    'text': text,
                    'line_number': i + 1,
                    'anchor': self._create_anchor(text)
                })
        
        return headings
    
    def _extract_links(self, content: str) -> List[Dict[str, str]]:
        """Extract links from content"""
        links = []
        
        # Markdown links [text](url)
        markdown_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        for match in re.finditer(markdown_pattern, content):
            links.append({
                'type': 'markdown',
                'text': match.group(1),
                'url': match.group(2),
                'context': self._get_link_context(content, match.start())
            })
        
        # Direct URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        for match in re.finditer(url_pattern, content):
            links.append({
                'type': 'direct',
                'text': match.group(0),
                'url': match.group(0),
                'context': self._get_link_context(content, match.start())
            })
        
        return links
    
    def _extract_dependencies(self, content: str, doc_path: str) -> List[str]:
        """Extract document dependencies"""
        dependencies = []
        
        # Find references to other documents
        # Look for patterns like [Document Name](path) or mentions of file names
        doc_patterns = [
            r'\[([^\]]+\.md)\]\(([^)]+)\)',  # [doc.md](path)
            r'`([^`]+\.md)`',  # `doc.md`
            r'([A-Z][A-Z0-9_]+\.md)',  # RC1_DOCUMENT.md
            r'([a-z_]+\.md)',  # document.md
        ]
        
        for pattern in doc_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                dep = match.group(1) if match.groups() else match.group(0)
                if dep and dep != doc_path:
                    dependencies.append(dep)
        
        return list(set(dependencies))  # Remove duplicates
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract topics from content"""
        topics = []
        
        # Common technical topics
        topic_patterns = {
            'implementation': r'\b(implement|implementation|implementing)\b',
            'architecture': r'\b(architecture|architect|design pattern)\b',
            'testing': r'\b(test|testing|test suite|unit test)\b',
            'documentation': r'\b(documentation|document|docs)\b',
            'security': r'\b(security|secure|authentication|authorization)\b',
            'performance': r'\b(performance|optimize|optimization|speed)\b',
            'api': r'\b(api|endpoint|interface|service)\b',
            'database': r'\b(database|db|sql|query)\b',
            'frontend': r'\b(frontend|ui|user interface|react|vue)\b',
            'backend': r'\b(backend|server|api|service)\b',
        }
        
        content_lower = content.lower()
        for topic, pattern in topic_patterns.items():
            if re.search(pattern, content_lower):
                topics.append(topic)
        
        return topics
    
    def _calculate_complexity_score(self, content: str, headings: List[Dict]) -> float:
        """Calculate content complexity score (0-1)"""
        if not content:
            return 0.0
        
        # Factors: length, heading depth, code blocks, lists
        word_count = len(content.split())
        max_heading_level = max([h['level'] for h in headings], default=0)
        code_blocks = content.count('```')
        lists = content.count('- ') + content.count('* ') + content.count('1. ')
        
        # Normalize factors
        length_factor = min(word_count / 1000, 1.0)  # Cap at 1000 words
        depth_factor = min(max_heading_level / 6, 1.0)  # Cap at level 6
        code_factor = min(code_blocks / 10, 1.0)  # Cap at 10 code blocks
        list_factor = min(lists / 20, 1.0)  # Cap at 20 list items
        
        # Weighted average
        complexity = (length_factor * 0.4 + depth_factor * 0.3 + 
                     code_factor * 0.2 + list_factor * 0.1)
        
        return round(complexity, 3)
    
    def _calculate_quality_score(self, content: str, links: List[Dict], headings: List[Dict]) -> float:
        """Calculate content quality score (0-1)"""
        if not content:
            return 0.0
        
        # Factors: structure, links, completeness
        has_structure = len(headings) > 0
        has_links = len(links) > 0
        has_content = len(content.strip()) > 100
        
        # Simple scoring
        score = 0.0
        if has_structure:
            score += 0.4
        if has_links:
            score += 0.3
        if has_content:
            score += 0.3
        
        return round(score, 3)
    
    def _calculate_readability_score(self, content: str, word_count: int, line_count: int) -> float:
        """Calculate readability score (0-1)"""
        if word_count == 0 or line_count == 0:
            return 0.0
        
        # Simple readability: average words per line
        avg_words_per_line = word_count / line_count
        
        # Optimal range: 10-20 words per line
        if 10 <= avg_words_per_line <= 20:
            return 1.0
        elif avg_words_per_line < 10:
            return avg_words_per_line / 10
        else:
            return max(0.0, 1.0 - (avg_words_per_line - 20) / 20)
    
    def detect_duplicates(self) -> List[DuplicateGroup]:
        """Detect duplicate or similar documents"""
        if not self.content_analyses:
            print("⚠️ No content analyses available. Run analyze_all_documents() first.")
            return []
        
        print(f"🔍 Detecting duplicates among {len(self.content_analyses)} documents...")
        
        duplicate_groups = []
        processed = set()
        
        for i, analysis1 in enumerate(self.content_analyses):
            if analysis1.document_path in processed:
                continue
                
            similar_docs = [analysis1.document_path]
            
            for j, analysis2 in enumerate(self.content_analyses[i+1:], i+1):
                if analysis2.document_path in processed:
                    continue
                
                similarity = self._calculate_similarity(analysis1, analysis2)
                if similarity > 0.8:  # 80% similarity threshold
                    similar_docs.append(analysis2.document_path)
                    processed.add(analysis2.document_path)
            
            if len(similar_docs) > 1:
                group = DuplicateGroup(
                    group_id=f"duplicate_group_{len(duplicate_groups) + 1}",
                    documents=similar_docs,
                    similarity_score=0.8,  # Simplified
                    common_content="",  # Would extract common content
                    duplicate_type="near"
                )
                duplicate_groups.append(group)
            
            processed.add(analysis1.document_path)
        
        self.duplicate_groups = duplicate_groups
        print(f"✅ Duplicate detection complete: {len(duplicate_groups)} groups found")
        return duplicate_groups
    
    def _calculate_similarity(self, analysis1: ContentAnalysis, analysis2: ContentAnalysis) -> float:
        """Calculate similarity between two document analyses"""
        # Simple similarity based on topics and structure
        topics1 = set(analysis1.topics)
        topics2 = set(analysis2.topics)
        
        if not topics1 and not topics2:
            return 0.0
        
        topic_similarity = len(topics1 & topics2) / len(topics1 | topics2) if topics1 or topics2 else 0.0
        
        # Structure similarity (heading levels)
        levels1 = [h['level'] for h in analysis1.heading_structure]
        levels2 = [h['level'] for h in analysis2.heading_structure]
        
        if levels1 == levels2:
            structure_similarity = 1.0
        elif not levels1 or not levels2:
            structure_similarity = 0.0
        else:
            # Simple structure comparison
            structure_similarity = 0.5
        
        # Weighted average
        similarity = topic_similarity * 0.7 + structure_similarity * 0.3
        return round(similarity, 3)
    
    def build_dependency_graph(self) -> Dict[str, List[str]]:
        """Build dependency graph from analyses"""
        if not self.content_analyses:
            print("⚠️ No content analyses available. Run analyze_all_documents() first.")
            return {}
        
        print("🔗 Building dependency graph...")
        
        dependency_graph = {}
        
        for analysis in self.content_analyses:
            dependency_graph[analysis.document_path] = analysis.dependencies
        
        self.dependency_graph = dependency_graph
        print(f"✅ Dependency graph built: {len(dependency_graph)} documents")
        return dependency_graph
    
    def save_analysis_results(self, output_path: str = "rc1_content_analysis.json") -> None:
        """Save analysis results to JSON file"""
        if not self.content_analyses:
            print("⚠️ No analysis results to save. Run analyze_all_documents() first.")
            return
        
        results_data = {
            "analysis_timestamp": datetime.now().isoformat(),
            "total_documents_analyzed": len(self.content_analyses),
            "total_duplicate_groups": len(self.duplicate_groups),
            "dependency_graph_size": len(self.dependency_graph),
            "content_analyses": [asdict(analysis) for analysis in self.content_analyses],
            "duplicate_groups": [asdict(group) for group in self.duplicate_groups],
            "dependency_graph": self.dependency_graph,
            "summary_statistics": self._generate_summary_statistics()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Content analysis results saved to: {output_path}")
    
    def _generate_summary_statistics(self) -> Dict[str, Any]:
        """Generate summary statistics from analyses"""
        if not self.content_analyses:
            return {}
        
        total_words = sum(a.word_count for a in self.content_analyses)
        total_lines = sum(a.line_count for a in self.content_analyses)
        avg_complexity = sum(a.complexity_score for a in self.content_analyses) / len(self.content_analyses)
        avg_quality = sum(a.quality_score for a in self.content_analyses) / len(self.content_analyses)
        avg_readability = sum(a.readability_score for a in self.content_analyses) / len(self.content_analyses)
        
        # Topic distribution
        all_topics = []
        for analysis in self.content_analyses:
            all_topics.extend(analysis.topics)
        
        topic_counts = {}
        for topic in all_topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        return {
            "total_words": total_words,
            "total_lines": total_lines,
            "average_complexity_score": round(avg_complexity, 3),
            "average_quality_score": round(avg_quality, 3),
            "average_readability_score": round(avg_readability, 3),
            "topic_distribution": dict(sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)),
            "documents_with_links": len([a for a in self.content_analyses if a.links]),
            "documents_with_dependencies": len([a for a in self.content_analyses if a.dependencies]),
            "documents_with_structure": len([a for a in self.content_analyses if a.heading_structure])
        }
    
    def _create_anchor(self, text: str) -> str:
        """Create anchor from heading text"""
        # Simple anchor creation
        anchor = re.sub(r'[^\w\s-]', '', text.lower())
        anchor = re.sub(r'[-\s]+', '-', anchor)
        return anchor.strip('-')
    
    def _get_link_context(self, content: str, position: int) -> str:
        """Get context around a link position"""
        start = max(0, position - 50)
        end = min(len(content), position + 50)
        return content[start:end]


def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="RC1 Content Analyzer")
    parser.add_argument("--input", default="rc1_scan_results.json", help="Input scan results file")
    parser.add_argument("--output", default="rc1_content_analysis.json", help="Output analysis file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = ContentAnalyzer(args.input)
    
    # Load scan results
    if not analyzer.load_scan_results():
        return
    
    # Analyze all documents
    analyses = analyzer.analyze_all_documents()
    
    # Detect duplicates
    duplicates = analyzer.detect_duplicates()
    
    # Build dependency graph
    dependencies = analyzer.build_dependency_graph()
    
    # Save results
    analyzer.save_analysis_results(args.output)
    
    # Print summary
    if args.verbose:
        print(f"\n📊 Content Analysis Summary:")
        print(f"   Documents Analyzed: {len(analyses)}")
        print(f"   Duplicate Groups: {len(duplicates)}")
        print(f"   Documents with Dependencies: {len(dependencies)}")
        
        if duplicates:
            print(f"\n🔍 Duplicate Groups Found:")
            for group in duplicates[:5]:  # Show first 5
                print(f"   Group {group.group_id}: {len(group.documents)} documents")


if __name__ == "__main__":
    main()
