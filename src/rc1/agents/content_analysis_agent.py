"""
Content Analysis Agent - Analyze document quality
"""

from typing import Dict, List, Any
from .base_agent import BaseAgent, AgentResult


class ContentAnalysisAgent(BaseAgent):
    """Independent agent for content quality analysis"""
    
    def __init__(self):
        super().__init__("ContentAnalysisAgent")
        self.quality_metrics = [
            'readability', 'completeness', 'accuracy', 'consistency', 
            'structure', 'language_quality', 'technical_accuracy'
        ]
    
    def execute(self) -> AgentResult:
        """Independent execution of content analysis"""
        self._start_execution()
        
        try:
            # Analyze document quality and structure
            quality_analysis = self._analyze_document_quality()
            self._set_data("quality_analysis", quality_analysis)
            
            # Detect content issues and improvements
            issues = self._detect_content_issues(quality_analysis)
            self._set_data("content_issues", issues)
            
            # Generate quality reports
            reports = self._generate_quality_reports(quality_analysis, issues)
            self._set_data("quality_reports", reports)
            
            # Self-validate analysis accuracy
            validation = self._validate_analysis_accuracy(quality_analysis)
            self._set_data("validation_result", validation)
            
            self._add_metric("documents_analyzed", len(quality_analysis.get("documents", [])))
            self._add_metric("issues_found", len(issues))
            self._add_metric("quality_score", quality_analysis.get("overall_quality", 0.0))
            
            return self._end_execution(success=True)
            
        except Exception as e:
            self._add_error(f"Critical error in content analysis: {e}")
            return self._end_execution(success=False)
    
    def _analyze_document_quality(self) -> Dict[str, Any]:
        """Analyze document quality and structure"""
        documents = self.discover_files(".", ["*.md", "*.txt", "*.py", "*.yaml", "*.json"])
        
        quality_data = {
            "overall_quality": 0.0,
            "documents": [],
            "metrics_summary": {}
        }
        
        total_quality = 0.0
        analyzed_count = 0
        
        for doc_path in documents[:20]:  # Limit analysis for performance
            try:
                content = self.read_file_safely(doc_path)
                if content:
                    doc_quality = self._analyze_single_document(doc_path, content)
                    quality_data["documents"].append(doc_quality)
                    total_quality += doc_quality.get("quality_score", 0.0)
                    analyzed_count += 1
            except Exception as e:
                self._add_warning(f"Could not analyze {doc_path}: {e}")
        
        if analyzed_count > 0:
            quality_data["overall_quality"] = total_quality / analyzed_count
        
        return quality_data
    
    def _analyze_single_document(self, doc_path: str, content: str) -> Dict[str, Any]:
        """Analyze quality of a single document"""
        analysis = {
            "path": doc_path,
            "quality_score": 0.0,
            "metrics": {},
            "issues": [],
            "recommendations": []
        }
        
        # Readability analysis
        readability = self._analyze_readability(content)
        analysis["metrics"]["readability"] = readability
        
        # Completeness analysis
        completeness = self._analyze_completeness(content, doc_path)
        analysis["metrics"]["completeness"] = completeness
        
        # Structure analysis
        structure = self._analyze_structure(content)
        analysis["metrics"]["structure"] = structure
        
        # Language quality
        language = self._analyze_language_quality(content)
        analysis["metrics"]["language_quality"] = language
        
        # Calculate overall quality score
        scores = [readability, completeness, structure, language]
        analysis["quality_score"] = sum(scores) / len(scores) if scores else 0.0
        
        return analysis
    
    def _analyze_readability(self, content: str) -> float:
        """Analyze content readability"""
        if not content:
            return 0.0
        
        lines = content.split('\n')
        words = content.split()
        
        # Simple readability metrics
        avg_words_per_line = len(words) / len(lines) if lines else 0
        avg_chars_per_word = len(content) / len(words) if words else 0
        
        # Ideal ranges
        ideal_words_per_line = 10-15
        ideal_chars_per_word = 4-6
        
        words_score = 1.0 - abs(avg_words_per_line - ideal_words_per_line) / ideal_words_per_line
        chars_score = 1.0 - abs(avg_chars_per_word - ideal_chars_per_word) / ideal_chars_per_word
        
        return max(0.0, min(1.0, (words_score + chars_score) / 2))
    
    def _analyze_completeness(self, content: str, doc_path: str) -> float:
        """Analyze content completeness"""
        if not content:
            return 0.0
        
        score = 0.0
        
        # Check for essential elements based on document type
        if doc_path.endswith('.md'):
            # Markdown documents should have headers
            if '#' in content:
                score += 0.3
            if '##' in content:
                score += 0.2
            if '```' in content:  # Code blocks
                score += 0.2
            if len(content) > 100:  # Minimum length
                score += 0.3
        
        elif doc_path.endswith('.py'):
            # Python files should have docstrings and comments
            if '"""' in content or "'''" in content:
                score += 0.4
            if '#' in content:
                score += 0.3
            if 'def ' in content or 'class ' in content:
                score += 0.3
        
        elif doc_path.endswith('.yaml') or doc_path.endswith('.yml'):
            # YAML files should be well-structured
            if content.strip().startswith(('name:', 'version:', 'description:')):
                score += 0.5
            if len(content.split('\n')) > 5:
                score += 0.5
        
        return min(1.0, score)
    
    def _analyze_structure(self, content: str) -> float:
        """Analyze content structure"""
        if not content:
            return 0.0
        
        score = 0.0
        lines = content.split('\n')
        
        # Check for proper formatting
        non_empty_lines = [line for line in lines if line.strip()]
        if len(non_empty_lines) > 0:
            score += 0.3
        
        # Check for logical structure (headers, sections)
        if any(line.strip().startswith('#') for line in lines):
            score += 0.4
        
        # Check for consistent indentation
        indentations = [len(line) - len(line.lstrip()) for line in lines if line.strip()]
        if indentations and len(set(indentations)) <= 3:  # Consistent indentation
            score += 0.3
        
        return min(1.0, score)
    
    def _analyze_language_quality(self, content: str) -> float:
        """Analyze language quality"""
        if not content:
            return 0.0
        
        score = 0.0
        
        # Check for common issues
        if content.count('TODO') > 0:
            score -= 0.1
        if content.count('FIXME') > 0:
            score -= 0.1
        if content.count('XXX') > 0:
            score -= 0.1
        
        # Check for positive indicators
        if 'please' in content.lower():
            score += 0.1
        if content.count('.') > 0:  # Proper sentences
            score += 0.2
        if len(content.split()) > 10:  # Substantial content
            score += 0.3
        
        # Check for typos (simple check)
        common_typos = ['teh', 'adn', 'recieve', 'seperate']
        typo_count = sum(content.lower().count(typo) for typo in common_typos)
        score -= typo_count * 0.1
        
        return max(0.0, min(1.0, score))
    
    def _detect_content_issues(self, quality_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect content issues and improvements"""
        issues = []
        
        for doc in quality_analysis.get("documents", []):
            doc_issues = []
            
            if doc.get("quality_score", 0.0) < 0.5:
                doc_issues.append({
                    "type": "low_quality",
                    "severity": "high",
                    "message": "Document quality score below threshold"
                })
            
            if doc.get("metrics", {}).get("readability", 0.0) < 0.3:
                doc_issues.append({
                    "type": "readability",
                    "severity": "medium",
                    "message": "Poor readability detected"
                })
            
            if doc.get("metrics", {}).get("completeness", 0.0) < 0.4:
                doc_issues.append({
                    "type": "completeness",
                    "severity": "medium",
                    "message": "Document appears incomplete"
                })
            
            if doc_issues:
                issues.append({
                    "document": doc.get("path", ""),
                    "issues": doc_issues
                })
        
        return issues
    
    def _generate_quality_reports(self, quality_analysis: Dict[str, Any], issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate quality reports"""
        return {
            "summary": {
                "total_documents": len(quality_analysis.get("documents", [])),
                "overall_quality": quality_analysis.get("overall_quality", 0.0),
                "total_issues": len(issues),
                "quality_distribution": self._calculate_quality_distribution(quality_analysis)
            },
            "detailed_analysis": quality_analysis,
            "issues": issues,
            "recommendations": self._generate_improvement_recommendations(quality_analysis, issues)
        }
    
    def _calculate_quality_distribution(self, quality_analysis: Dict[str, Any]) -> Dict[str, int]:
        """Calculate quality score distribution"""
        distribution = {"excellent": 0, "good": 0, "fair": 0, "poor": 0}
        
        for doc in quality_analysis.get("documents", []):
            score = doc.get("quality_score", 0.0)
            if score >= 0.8:
                distribution["excellent"] += 1
            elif score >= 0.6:
                distribution["good"] += 1
            elif score >= 0.4:
                distribution["fair"] += 1
            else:
                distribution["poor"] += 1
        
        return distribution
    
    def _generate_improvement_recommendations(self, quality_analysis: Dict[str, Any], issues: List[Dict[str, Any]]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        if quality_analysis.get("overall_quality", 0.0) < 0.6:
            recommendations.append("Overall document quality needs improvement")
        
        readability_issues = sum(1 for issue_group in issues 
                               for issue in issue_group.get("issues", []) 
                               if issue.get("type") == "readability")
        if readability_issues > 0:
            recommendations.append(f"Improve readability in {readability_issues} documents")
        
        completeness_issues = sum(1 for issue_group in issues 
                                for issue in issue_group.get("issues", []) 
                                if issue.get("type") == "completeness")
        if completeness_issues > 0:
            recommendations.append(f"Complete {completeness_issues} incomplete documents")
        
        return recommendations
    
    def _validate_analysis_accuracy(self, quality_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate analysis accuracy"""
        validation = {
            "is_accurate": True,
            "score": 0.0,
            "issues": [],
            "recommendations": []
        }
        
        # Check if analysis was performed
        documents = quality_analysis.get("documents", [])
        if not documents:
            validation["issues"].append("No documents were analyzed")
            validation["is_accurate"] = False
        
        # Check if quality scores are reasonable
        quality_scores = [doc.get("quality_score", 0.0) for doc in documents]
        if quality_scores:
            avg_score = sum(quality_scores) / len(quality_scores)
            if avg_score < 0.0 or avg_score > 1.0:
                validation["issues"].append("Quality scores outside valid range")
                validation["is_accurate"] = False
        
        # Calculate validation score
        score = 0.0
        score += 0.5 if len(documents) > 0 else 0.0
        score += 0.3 if validation["is_accurate"] else 0.0
        score += 0.2 if quality_scores and all(0.0 <= s <= 1.0 for s in quality_scores) else 0.0
        
        validation["score"] = round(score, 3)
        
        return validation
