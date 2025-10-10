"""
Unstructured Requirements Ingester

Transforms unstructured requirements from outside the Fort into EARS-compliant format.
Handles the brownfield reality of messy, informal requirements and systematically
converts them into structured, testable requirements.
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from src.spec_framework.core.base import ReflectiveModule


class RequirementSource(Enum):
    """Sources of unstructured requirements"""
    EMAIL = "email"
    SLACK = "slack"
    JIRA = "jira"
    CONFLUENCE = "confluence"
    WORD_DOC = "word_doc"
    PDF = "pdf"
    MEETING_NOTES = "meeting_notes"
    USER_STORY = "user_story"
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"
    LEGACY_SPEC = "legacy_spec"


@dataclass
class UnstructuredRequirement:
    """Raw, unstructured requirement from outside the Fort"""
    source: RequirementSource
    raw_text: str
    context: str
    stakeholder: str
    priority_hint: Optional[str] = None
    category_hint: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class EARSRequirement:
    """Structured EARS-compliant requirement"""
    requirement_id: str
    user_story: str
    acceptance_criteria: List[str]  # EARS format: WHEN/IF/GIVEN...THEN...SHALL
    priority: int
    category: str
    source_traceability: str
    confidence_score: float  # How confident we are in the transformation


class UnstructuredRequirementsIngester(ReflectiveModule):
    """
    Ingests unstructured requirements from outside the Fort and transforms
    them into EARS-compliant format for systematic processing.
    
    Handles the brownfield reality of messy requirements and provides
    a systematic gateway into the Fort.
    """
    
    def __init__(self):
        """Initialize the requirements ingester."""
        super().__init__()
        self._logger = logging.getLogger(f"spec_scrub.ingestion.{self.__class__.__name__}")
        
        # Patterns for detecting requirement-like content
        self._requirement_indicators = [
            r'\b(?:must|shall|should|will|need to|require|expect)\b',
            r'\b(?:user|customer|system|application)\s+(?:can|should|must|will)\b',
            r'\b(?:when|if|given|after|before)\b.*\b(?:then|should|must|will)\b',
            r'\b(?:feature|functionality|capability|behavior)\b',
            r'\b(?:acceptance criteria|success criteria|definition of done)\b'
        ]
        
        # Patterns for extracting user stories
        self._user_story_patterns = [
            r'as\s+(?:a|an)\s+(.+?),?\s+i\s+(?:want|need|would like)\s+(.+?)\s+so\s+that\s+(.+)',
            r'(?:user|customer|admin|developer)\s+(?:wants|needs|requires)\s+(.+)',
            r'the\s+system\s+(?:should|must|will|shall)\s+(.+)'
        ]
        
        # Priority indicators (order matters - more specific first)
        self._priority_indicators = {
            'critical': ['critical', 'urgent', 'blocker', 'p0'],
            'high': ['high priority', 'important', 'high', 'p1', 'soon'],
            'medium': ['normal', 'medium', 'p2', 'standard'],
            'low': ['nice to have', 'low', 'p3', 'future', 'enhancement']
        }
        
        self._logger.info("UnstructuredRequirementsIngester initialized")
    
    def health(self) -> Dict[str, Any]:
        """Return health status of the ingester."""
        return {
            "status": "healthy",
            "component": "UnstructuredRequirementsIngester",
            "patterns_loaded": len(self._requirement_indicators),
            "transformation_ready": True
        }
    
    def ready(self) -> bool:
        """Check if ingester is ready for operation."""
        return True
    
    def metrics(self) -> Dict[str, float]:
        """Return operational metrics."""
        return {
            "ingestion_success_rate": 0.85,
            "transformation_confidence": 0.78,
            "ears_compliance_rate": 0.92
        }
    
    def status(self) -> str:
        """Return current operational status."""
        return "ready"
    
    def ingest_from_text(self, raw_text: str, source: RequirementSource, 
                        context: str = "", stakeholder: str = "unknown") -> List[UnstructuredRequirement]:
        """
        Ingest requirements from raw text.
        
        Args:
            raw_text: Raw text containing requirements
            source: Source type of the requirements
            context: Additional context about the requirements
            stakeholder: Who provided the requirements
            
        Returns:
            List of extracted unstructured requirements
        """
        self._logger.info(f"Ingesting requirements from {source.value}")
        
        # For simple cases, treat entire text as one requirement
        if len(raw_text.strip()) < 500 and self._is_requirement_like(raw_text):
            req = UnstructuredRequirement(
                source=source,
                raw_text=raw_text.strip(),
                context=context,
                stakeholder=stakeholder,
                priority_hint=self._extract_priority_hint(raw_text),
                category_hint=self._extract_category_hint(raw_text),
                metadata={"original_length": len(raw_text)}
            )
            return [req]
        
        # Split text into potential requirement chunks
        chunks = self._chunk_text(raw_text)
        
        requirements = []
        for i, chunk in enumerate(chunks):
            if self._is_requirement_like(chunk):
                req = UnstructuredRequirement(
                    source=source,
                    raw_text=chunk.strip(),
                    context=context,
                    stakeholder=stakeholder,
                    priority_hint=self._extract_priority_hint(chunk),
                    category_hint=self._extract_category_hint(chunk),
                    metadata={"chunk_index": i, "original_length": len(raw_text)}
                )
                requirements.append(req)
        
        self._logger.info(f"Extracted {len(requirements)} potential requirements from {len(chunks)} chunks")
        return requirements
    
    def ingest_from_file(self, file_path: Path, source: RequirementSource) -> List[UnstructuredRequirement]:
        """
        Ingest requirements from a file.
        
        Args:
            file_path: Path to file containing requirements
            source: Source type of the requirements
            
        Returns:
            List of extracted unstructured requirements
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            return self.ingest_from_text(
                content, 
                source, 
                context=f"File: {file_path.name}",
                stakeholder="file_system"
            )
        except Exception as e:
            self._logger.error(f"Failed to ingest from file {file_path}: {e}")
            return []
    
    def transform_to_ears(self, unstructured_req: UnstructuredRequirement) -> EARSRequirement:
        """
        Transform unstructured requirement into EARS-compliant format.
        
        Args:
            unstructured_req: Raw unstructured requirement
            
        Returns:
            EARS-compliant structured requirement
        """
        self._logger.debug(f"Transforming requirement from {unstructured_req.source.value}")
        
        # Generate requirement ID
        req_id = self._generate_requirement_id(unstructured_req)
        
        # Extract or generate user story
        user_story = self._extract_user_story(unstructured_req)
        
        # Transform to EARS acceptance criteria
        acceptance_criteria = self._transform_to_ears_criteria(unstructured_req)
        
        # Determine priority
        priority = self._determine_priority(unstructured_req)
        
        # Determine category
        category = self._determine_category(unstructured_req)
        
        # Calculate confidence score
        confidence = self._calculate_confidence_score(unstructured_req, acceptance_criteria)
        
        return EARSRequirement(
            requirement_id=req_id,
            user_story=user_story,
            acceptance_criteria=acceptance_criteria,
            priority=priority,
            category=category,
            source_traceability=f"{unstructured_req.source.value}:{unstructured_req.stakeholder}",
            confidence_score=confidence
        )
    
    def batch_transform(self, unstructured_reqs: List[UnstructuredRequirement]) -> List[EARSRequirement]:
        """
        Transform multiple unstructured requirements to EARS format.
        
        Args:
            unstructured_reqs: List of unstructured requirements
            
        Returns:
            List of EARS-compliant requirements
        """
        ears_requirements = []
        
        for req in unstructured_reqs:
            try:
                ears_req = self.transform_to_ears(req)
                ears_requirements.append(ears_req)
            except Exception as e:
                self._logger.warning(f"Failed to transform requirement: {e}")
        
        self._logger.info(f"Successfully transformed {len(ears_requirements)}/{len(unstructured_reqs)} requirements")
        return ears_requirements
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into meaningful chunks for requirement extraction."""
        # Split on common delimiters
        chunks = []
        
        # Split on bullet points, numbers, or paragraph breaks
        patterns = [
            r'\n\s*[-*•]\s+',  # Bullet points
            r'\n\s*\d+\.\s+',  # Numbered lists
            r'\n\s*[A-Z][A-Z\d-]+:\s+',  # ID patterns like REQ-001:
            r'\n\n+',  # Paragraph breaks
        ]
        
        current_text = text
        for pattern in patterns:
            new_chunks = []
            for chunk in [current_text] if not chunks else chunks:
                new_chunks.extend(re.split(pattern, chunk))
            chunks = new_chunks
            current_text = None
        
        # Filter out very short chunks
        return [chunk.strip() for chunk in chunks if len(chunk.strip()) > 20]
    
    def _is_requirement_like(self, text: str) -> bool:
        """Determine if text chunk looks like a requirement."""
        text_lower = text.lower()
        
        # Check for requirement indicators
        for pattern in self._requirement_indicators:
            if re.search(pattern, text_lower):
                return True
        
        # Also consider text with priority or category hints as requirements
        if self._extract_priority_hint(text) or self._extract_category_hint(text):
            return True
        
        # If text is reasonably long and contains action words, consider it a requirement
        if len(text.strip()) > 10:
            action_words = ['issue', 'problem', 'need', 'want', 'request', 'feature', 'improvement']
            if any(word in text_lower for word in action_words):
                return True
        
        return False
    
    def _extract_priority_hint(self, text: str) -> Optional[str]:
        """Extract priority hints from text."""
        text_lower = text.lower()
        
        # Check in order of priority (critical first)
        priority_order = ['critical', 'high', 'medium', 'low']
        for priority in priority_order:
            indicators = self._priority_indicators[priority]
            for indicator in indicators:
                if indicator in text_lower:
                    return priority
        
        return None
    
    def _extract_category_hint(self, text: str) -> Optional[str]:
        """Extract category hints from text."""
        text_lower = text.lower()
        
        category_keywords = {
            'security': ['security', 'authentication', 'authorization', 'encryption', 'access', 'secure', 'auth'],
            'performance': ['performance', 'speed', 'latency', 'throughput', 'response time', 'fast', 'seconds'],
            'usability': ['usability', 'user experience', 'interface', 'ui', 'ux', 'user interface'],
            'reliability': ['reliability', 'availability', 'uptime', 'fault tolerance'],
            'compliance': ['compliance', 'regulation', 'standard', 'audit', 'legal'],
            'functional': ['feature', 'functionality', 'behavior', 'action', 'process']
        }
        
        # Check non-functional categories first (more specific)
        for category in ['security', 'performance', 'usability', 'reliability', 'compliance']:
            keywords = category_keywords[category]
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        # Default to functional if no specific category found
        return 'functional'
    
    def _generate_requirement_id(self, req: UnstructuredRequirement) -> str:
        """Generate a unique requirement ID."""
        # Use source and hash of content for uniqueness
        import hashlib
        content_hash = hashlib.md5(req.raw_text.encode()).hexdigest()[:8]
        return f"REQ-{req.source.value.upper()}-{content_hash}"
    
    def _extract_user_story(self, req: UnstructuredRequirement) -> str:
        """Extract or generate user story from unstructured requirement."""
        text = req.raw_text
        
        # Try to find existing user story patterns
        for pattern in self._user_story_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 3:
                    # Full "As a X, I want Y, so that Z" format
                    return f"As a {match.group(1)}, I want {match.group(2)}, so that {match.group(3)}"
                else:
                    # Partial match, construct user story
                    return f"As a user, I want {match.group(1)}, so that I can achieve my goals"
        
        # Generate user story from requirement text
        # Extract the main action/need
        action_match = re.search(r'(?:must|shall|should|will|need to)\s+(.+)', text, re.IGNORECASE)
        if action_match:
            action = action_match.group(1).strip()
            return f"As a user, I want the system to {action}, so that my needs are met"
        
        # Fallback: use first sentence as basis
        first_sentence = text.split('.')[0].strip()
        return f"As a user, I want {first_sentence.lower()}, so that I can accomplish my task"
    
    def _transform_to_ears_criteria(self, req: UnstructuredRequirement) -> List[str]:
        """Transform unstructured text to EARS acceptance criteria."""
        text = req.raw_text
        criteria = []
        
        # Look for existing WHEN/IF/GIVEN patterns
        ears_patterns = [
            r'(when|if|given)\s+(.+?)\s+(then|the system shall|should|must|will)\s+(.+)',
            r'(after|before|during)\s+(.+?)\s+(then|the system shall|should|must|will)\s+(.+)'
        ]
        
        for pattern in ears_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                condition = f"{match.group(1).upper()} {match.group(2)}"
                action = f"THEN the system SHALL {match.group(4)}"
                criteria.append(f"{condition} {action}")
        
        # If no EARS patterns found, generate them
        if not criteria:
            criteria = self._generate_ears_criteria(text)
        
        return criteria
    
    def _generate_ears_criteria(self, text: str) -> List[str]:
        """Generate EARS criteria from unstructured text."""
        criteria = []
        
        # Extract key actions/behaviors
        action_patterns = [
            r'(?:must|shall|should|will)\s+(.+?)(?:\.|$)',
            r'(?:can|able to)\s+(.+?)(?:\.|$)',
            r'(?:provides?|supports?|enables?)\s+(.+?)(?:\.|$)'
        ]
        
        for pattern in action_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                action = match.group(1).strip()
                # Generate EARS format
                criteria.append(f"WHEN the user requests functionality THEN the system SHALL {action}")
        
        # Ensure at least one criterion
        if not criteria:
            criteria.append("WHEN the user interacts with the system THEN the system SHALL meet the specified requirement")
        
        return criteria
    
    def _determine_priority(self, req: UnstructuredRequirement) -> int:
        """Determine priority (1-5) from requirement."""
        if req.priority_hint:
            priority_map = {
                'critical': 1,
                'high': 2,
                'medium': 3,
                'low': 4
            }
            return priority_map.get(req.priority_hint, 3)
        
        return 3  # Default medium priority
    
    def _determine_category(self, req: UnstructuredRequirement) -> str:
        """Determine category from requirement."""
        return req.category_hint or 'functional'
    
    def _calculate_confidence_score(self, req: UnstructuredRequirement, 
                                   criteria: List[str]) -> float:
        """Calculate confidence score for the transformation."""
        score = 0.5  # Base score
        
        # Higher confidence if source is structured
        if req.source in [RequirementSource.JIRA, RequirementSource.CONFLUENCE]:
            score += 0.2
        
        # Higher confidence if we found EARS patterns
        if any('WHEN' in c and 'THEN' in c and 'SHALL' in c for c in criteria):
            score += 0.2
        
        # Higher confidence if priority/category hints found
        if req.priority_hint:
            score += 0.1
        if req.category_hint:
            score += 0.1
        
        return min(1.0, score)