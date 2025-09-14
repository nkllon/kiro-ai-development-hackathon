"""
Query Engine Processing

This module was extracted from query_engine.py
as part of RM-DDD compliance refactoring.
"""

import re
import time
from typing import List, Dict, Optional, Any, Set
from datetime import datetime
from pathlib import Path
from .base import CachedComponent
from .interfaces import QueryEngineInterface
from .models import Domain, QueryResult
from .exceptions import QueryEngineError, InvalidQueryError, QueryTimeoutError
from .config import get_config
from src.rm_ddd.core.health import ModuleHealth


def _parse_partial_query(self, partial_query: str) -> Dict[str, Any]:
    """Parse partial query to understand user intent"""
    partial_info = {'tokens': partial_query.split(), 'last_token': partial_query.split()[-1] if partial_query.split() else '', 'intent_indicators': [], 'entity_hints': [], 'incomplete_type': 'unknown'}
    intent_words = {'pattern': ['pattern', 'file', 'path', '*.py', 'src/'], 'content': ['contains', 'content', 'indicator', 'has'], 'capability': ['can', 'tool', 'capability', 'run', 'support'], 'relationship': ['depend', 'similar', 'related', 'connect'], 'analysis': ['analyze', 'metrics', 'health', 'report']}
    for intent, indicators in intent_words.items():
        if any((indicator in partial_query for indicator in indicators)):
            partial_info['intent_indicators'].append(intent)
    if '_domain' in partial_query or 'domain' in partial_query:
        partial_info['entity_hints'].append('domain_name')
    if any((ext in partial_query for ext in ['.py', '.js', '.md', '.yaml'])):
        partial_info['entity_hints'].append('file_pattern')
    if partial_query.endswith(' '):
        partial_info['incomplete_type'] = 'expecting_next_word'
    elif partial_query.split()[-1] if partial_query.split() else '':
        partial_info['incomplete_type'] = 'partial_word'
    else:
        partial_info['incomplete_type'] = 'empty'
    return partial_info

def _parse_natural_language_query(self, query: str) -> Dict[str, Any]:
    """Parse natural language query into structured components"""
    query_lower = query.lower().strip()
    parsed_query = {'original_query': query, 'keywords': [], 'entities': {}, 'intent': 'general_search', 'query_type': 'search', 'filters': {}, 'modifiers': [], 'relationship_type': None, 'target_domain': None}
    entities = self._extract_entities(query_lower)
    parsed_query['entities'] = entities
    keywords = self._extract_enhanced_keywords(query_lower)
    parsed_query['keywords'] = keywords
    intent = self._determine_enhanced_intent(query_lower, entities)
    parsed_query['intent'] = intent
    query_type = self._determine_query_type(query_lower)
    parsed_query['query_type'] = query_type
    filters = self._extract_query_filters(query_lower)
    parsed_query['filters'] = filters
    modifiers = self._extract_query_modifiers(query_lower)
    parsed_query['modifiers'] = modifiers
    if query_type == 'relationship':
        relationship_info = self._extract_relationship_info(query_lower, entities)
        parsed_query.update(relationship_info)
    return parsed_query

def _execute_parsed_query(self, parsed_query: Dict[str, Any]) -> List[Domain]:
    """Execute the parsed query"""
    query_type = parsed_query['query_type']
    intent = parsed_query['intent']
    keywords = parsed_query['keywords']
    entities = parsed_query['entities']
    if query_type == 'relationship':
        target_domain = parsed_query.get('target_domain')
        relationship_type = parsed_query.get('relationship_type')
        if target_domain and relationship_type:
            return self.relationship_query(target_domain, relationship_type)
        else:
            return self._combined_search(keywords)
    elif query_type == 'analysis':
        return self._combined_search(keywords)
    elif intent == 'pattern_search':
        domains = []
        for pattern in entities.get('patterns', []):
            domains.extend(self.pattern_search(pattern))
        if not domains:
            domains = self._search_by_patterns(keywords)
        return domains
    elif intent == 'content_search':
        return self._search_by_content(keywords)
    elif intent == 'capability_search':
        domains = []
        for capability in entities.get('capabilities', []):
            domains.extend(self.capability_search(capability))
        if not domains:
            domains = self._search_by_capabilities(keywords)
        return domains
    else:
        return self._combined_search(keywords)

def _apply_parsed_filters(self, domains: List[Domain], filters: Dict[str, Any]) -> List[Domain]:
    """Apply filters extracted from the parsed query"""
    filtered_domains = []
    for domain in domains:
        if 'category' in filters:
            if domain.metadata.demo_role != filters['category']:
                continue
        if 'status' in filters:
            if not domain.health_status or domain.health_status.status.value != filters['status']:
                continue
        if 'complexity_level' in filters:
            pass
        filtered_domains.append(domain)
    return filtered_domains
