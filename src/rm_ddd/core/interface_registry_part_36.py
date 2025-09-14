from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


class SearchbyubiquitouslanguageClass:
    """Auto-generated class for functions."""

    def search_by_ubiquitous_language(self, terms: List[str], context: str = "") -> List[InterfaceSearchResult]:
    """Search interfaces using ubiquitous language terms"""
    results = []
    for interface in self.interfaces.values():
    if interface.status == InterfaceStatus.DEPRECATED:
    continue

    matched_terms = []
    relevance_score = 0.0

    # Check domain terms
    for term in terms:
    term_lower = term.lower()
    for domain_term in interface.domain_terms:
    if term_lower in domain_term.lower() or domain_term.lower() in term_lower:
    matched_terms.append(term)
    relevance_score += 1.0

    # Check interface name
    for term in terms:
    if term.lower() in interface.interface_name.lower():
    matched_terms.append(term)
    relevance_score += 0.8

    # Check description
    for term in terms:
    if term.lower() in interface.description.lower():
    matched_terms.append(term)
    relevance_score += 0.6

    # Check capabilities
    for term in terms:
    for capability in interface.capabilities:
    if term.lower() in capability.lower():
    matched_terms.append(term)
    relevance_score += 0.4

    if matched_terms:
    results.append(InterfaceSearchResult(
    interface=interface,
    relevance_score=relevance_score,
    matched_terms=list(set(matched_terms)),
    search_context=context
    ))

    # Sort by relevance score
    results.sort(key=lambda x: x.relevance_score, reverse=True)
    return results

    def register_module(self, registry):
    """Register module with registry."""
    metadata = self.get_interface_metadata()
    if hasattr(registry, 'register'):
    registry.register(metadata)

    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }

