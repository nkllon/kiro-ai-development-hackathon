"""
Mama Discovery Protocol Implementation

Implements automatic discovery of accountability chains based on the fundamental
principle that "everyone has a mama" - systematic accountability relationship mapping.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import asyncio
from dataclasses import dataclass

from ..interfaces import MamaDiscoverer
from ..models import (
    AccountabilityChain, AccountabilityRelationship, ConstraintSource,
    IndependenceClaim, ResearchResult, ChainChange, MappingUpdate, HumanEscalation
)


@dataclass
class DiscoverySource:
    """Source of accountability information."""
    source_type: str
    confidence: float
    data: Dict[str, Any]
    last_updated: datetime


class MamaDiscovererImpl(MamaDiscoverer):
    """
    Implementation of the Mama Discovery Protocol.
    
    Systematically discovers and maps accountability relationships,
    implementing the core principle that "everyone has a mama."
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Discovery configuration
        self.discovery_timeout = timedelta(hours=self.config.get('discovery_timeout_hours', 24))
        self.confidence_threshold = self.config.get('confidence_threshold', 0.7)
        self.max_chain_depth = self.config.get('max_chain_depth', 10)
        
        # Discovery sources and their weights
        self.discovery_sources = {
            'organizational_chart': {'weight': 0.9, 'enabled': True},
            'financial_dependencies': {'weight': 0.8, 'enabled': True},
            'regulatory_filings': {'weight': 0.85, 'enabled': True},
            'legal_documents': {'weight': 0.9, 'enabled': True},
            'social_networks': {'weight': 0.4, 'enabled': True},
            'public_records': {'weight': 0.7, 'enabled': True},
            'contract_analysis': {'weight': 0.8, 'enabled': True}
        }
        
        # Cache for discovered chains
        self._chain_cache = {}
        self._cache_ttl = timedelta(hours=6)
    
    def discover_accountability_chain(self, actor_id: str) -> AccountabilityChain:
        """
        Discover the complete accountability chain for an actor.
        
        Implements systematic discovery across multiple sources to map
        the complete "mama chain" for any actor in the system.
        """
        self.logger.info(f"Initiating Mama Discovery Protocol for actor {actor_id}")
        
        # Check cache first
        cached_chain = self._get_cached_chain(actor_id)
        if cached_chain:
            self.logger.info(f"Using cached accountability chain for {actor_id}")
            return cached_chain
        
        # Discover from multiple sources
        discovery_results = self._discover_from_all_sources(actor_id)
        
        # Analyze and consolidate results
        immediate_accountability = self._extract_immediate_relationships(discovery_results)
        ultimate_accountability = self._extract_ultimate_relationships(discovery_results)
        constraint_sources = self._extract_constraint_sources(discovery_results)
        
        # Calculate confidence score
        confidence = self._calculate_discovery_confidence(discovery_results)
        
        # Determine discovery method
        discovery_method = self._determine_primary_discovery_method(discovery_results)
        
        # Create accountability chain
        chain = AccountabilityChain(
            actor_id=actor_id,
            immediate_accountability=immediate_accountability,
            ultimate_accountability=ultimate_accountability,
            constraint_sources=constraint_sources,
            last_verified=datetime.now(),
            verification_confidence=confidence,
            discovery_method=discovery_method,
            metadata={
                'discovery_sources': [r.source_type for r in discovery_results],
                'discovery_duration': str(datetime.now() - datetime.now()),  # Would track actual duration
                'total_sources_checked': len(discovery_results)
            }
        )
        
        # Cache the result
        self._cache_chain(actor_id, chain)
        
        self.logger.info(f"Mama Discovery completed for {actor_id} with confidence {confidence:.2f}")
        return chain
    
    def research_independence_claims(self, actor_id: str, claim: IndependenceClaim) -> ResearchResult:
        """
        Research and validate claims of independence from accountability.
        
        Systematically investigates independence claims to determine their validity,
        because "if you think you don't have a mama, you haven't met her yet."
        """
        self.logger.info(f"Researching independence claim {claim.claim_id} for actor {actor_id}")
        
        # Discover actual accountability chain
        actual_chain = self.discover_accountability_chain(actor_id)
        
        # Analyze the independence claim against discovered reality
        research_findings = {
            'claimed_independence_type': claim.claimed_independence_type,
            'actual_immediate_accountability': len(actual_chain.immediate_accountability),
            'actual_ultimate_accountability': len(actual_chain.ultimate_accountability),
            'actual_constraint_sources': len(actual_chain.constraint_sources),
            'discovery_confidence': actual_chain.verification_confidence
        }
        
        # Check specific independence claim types
        independence_validity = self._validate_independence_claim(claim, actual_chain)
        
        # Calculate confidence in research results
        confidence_score = min(
            actual_chain.verification_confidence,
            self._calculate_research_confidence(claim, actual_chain)
        )
        
        # Determine research method used
        research_method = f"systematic_discovery_via_{actual_chain.discovery_method}"
        
        return ResearchResult(
            claim_id=claim.claim_id,
            research_findings=research_findings,
            actual_constraints=actual_chain.constraint_sources,
            independence_validity=independence_validity,
            confidence_score=confidence_score,
            research_method=research_method
        )
    
    def update_governance_mappings(self, chain_changes: List[ChainChange]) -> MappingUpdate:
        """
        Update governance mappings when accountability chains change.
        
        Maintains systematic consistency across all governance systems
        when accountability relationships evolve.
        """
        self.logger.info(f"Updating governance mappings for {len(chain_changes)} chain changes")
        
        affected_actors = []
        changes_applied = []
        errors = []
        
        for change in chain_changes:
            try:
                # Update cached chain if exists
                if change.actor_id in self._chain_cache:
                    self._apply_change_to_cache(change)
                
                # Track affected actors
                if change.actor_id not in affected_actors:
                    affected_actors.append(change.actor_id)
                
                changes_applied.append(change)
                
                self.logger.debug(f"Applied chain change {change.change_id} for actor {change.actor_id}")
                
            except Exception as e:
                error_msg = f"Failed to apply change {change.change_id}: {str(e)}"
                errors.append(error_msg)
                self.logger.error(error_msg)
        
        # Determine synchronization status
        if not errors:
            sync_status = "complete"
        elif len(errors) < len(chain_changes):
            sync_status = "partial"
        else:
            sync_status = "failed"
        
        return MappingUpdate(
            affected_actors=affected_actors,
            changes_applied=changes_applied,
            synchronization_status=sync_status,
            errors=errors
        )
    
    def escalate_discovery_failures(self, actor_id: str, failure_reason: str) -> HumanEscalation:
        """
        Escalate accountability chain discovery failures to human oversight.
        
        When systematic discovery fails, escalate to human investigators
        because "everyone has a mama" - we just need to find her.
        """
        self.logger.warning(f"Escalating discovery failure for actor {actor_id}: {failure_reason}")
        
        # Determine priority based on failure type
        priority = "high"
        if "security" in failure_reason.lower() or "critical" in failure_reason.lower():
            priority = "critical"
        elif "timeout" in failure_reason.lower():
            priority = "medium"
        
        # Set investigation deadline
        deadline = datetime.now() + timedelta(hours=48)
        if priority == "critical":
            deadline = datetime.now() + timedelta(hours=8)
        
        # Create detailed issue description
        issue_description = f"""
        Mama Discovery Protocol failed for actor {actor_id}.
        
        Failure Reason: {failure_reason}
        
        Discovery Attempts Made:
        - Organizational chart analysis
        - Financial dependency mapping
        - Regulatory filing search
        - Legal document analysis
        - Public records search
        
        Next Steps Required:
        1. Manual investigation of actor's actual accountability relationships
        2. Verification of any claimed independence or autonomy
        3. Documentation of discovered accountability chain
        4. Update of discovery algorithms based on findings
        
        Remember: Everyone has a mama. If systematic discovery failed,
        human investigation is required to find the accountability chain.
        """
        
        return HumanEscalation(
            escalation_type="accountability_discovery_failure",
            actor_id=actor_id,
            issue_description=issue_description,
            priority=priority,
            deadline=deadline,
            status="open"
        )
    
    def _discover_from_all_sources(self, actor_id: str) -> List[DiscoverySource]:
        """Discover accountability information from all available sources."""
        results = []
        
        # Organizational chart discovery
        if self.discovery_sources['organizational_chart']['enabled']:
            org_result = self._discover_organizational_relationships(actor_id)
            if org_result:
                results.append(org_result)
        
        # Financial dependency discovery
        if self.discovery_sources['financial_dependencies']['enabled']:
            financial_result = self._discover_financial_dependencies(actor_id)
            if financial_result:
                results.append(financial_result)
        
        # Regulatory filing discovery
        if self.discovery_sources['regulatory_filings']['enabled']:
            regulatory_result = self._discover_regulatory_relationships(actor_id)
            if regulatory_result:
                results.append(regulatory_result)
        
        # Legal document discovery
        if self.discovery_sources['legal_documents']['enabled']:
            legal_result = self._discover_legal_constraints(actor_id)
            if legal_result:
                results.append(legal_result)
        
        # Public records discovery
        if self.discovery_sources['public_records']['enabled']:
            public_result = self._discover_public_records(actor_id)
            if public_result:
                results.append(public_result)
        
        return results
    
    def _discover_organizational_relationships(self, actor_id: str) -> Optional[DiscoverySource]:
        """Discover organizational accountability relationships."""
        # Simulated organizational chart analysis
        # In real implementation, would integrate with HR systems, org charts, etc.
        
        org_data = {
            'direct_manager': f"manager_{actor_id}",
            'department_head': f"dept_head_{actor_id}",
            'division_vp': f"vp_{actor_id}",
            'reporting_chain': [f"manager_{actor_id}", f"dept_head_{actor_id}", f"vp_{actor_id}"],
            'matrix_relationships': [f"project_lead_{actor_id}"],
            'organizational_level': 'individual_contributor'
        }
        
        return DiscoverySource(
            source_type='organizational_chart',
            confidence=0.9,
            data=org_data,
            last_updated=datetime.now()
        )
    
    def _discover_financial_dependencies(self, actor_id: str) -> Optional[DiscoverySource]:
        """Discover financial accountability relationships."""
        # Simulated financial dependency analysis
        
        financial_data = {
            'salary_payer': f"company_{actor_id}",
            'budget_approver': f"finance_manager_{actor_id}",
            'expense_limits': {'daily': 500, 'monthly': 5000},
            'financial_authorities': [f"cfo_{actor_id}", f"finance_director_{actor_id}"],
            'contract_dependencies': [f"vendor_contract_{actor_id}"]
        }
        
        return DiscoverySource(
            source_type='financial_dependencies',
            confidence=0.8,
            data=financial_data,
            last_updated=datetime.now()
        )
    
    def _discover_regulatory_relationships(self, actor_id: str) -> Optional[DiscoverySource]:
        """Discover regulatory accountability relationships."""
        # Simulated regulatory analysis
        
        regulatory_data = {
            'regulatory_bodies': ['SEC', 'FTC', 'State_Regulators'],
            'compliance_officers': [f"compliance_officer_{actor_id}"],
            'regulatory_constraints': ['SOX_compliance', 'GDPR_compliance'],
            'audit_authorities': [f"external_auditor_{actor_id}"],
            'licensing_bodies': [f"professional_board_{actor_id}"]
        }
        
        return DiscoverySource(
            source_type='regulatory_filings',
            confidence=0.85,
            data=regulatory_data,
            last_updated=datetime.now()
        )
    
    def _discover_legal_constraints(self, actor_id: str) -> Optional[DiscoverySource]:
        """Discover legal accountability constraints."""
        # Simulated legal constraint analysis
        
        legal_data = {
            'employment_contract': f"contract_{actor_id}",
            'non_compete_agreements': [f"noncompete_{actor_id}"],
            'fiduciary_duties': ['duty_of_care', 'duty_of_loyalty'],
            'legal_counsel': [f"corporate_counsel_{actor_id}"],
            'court_jurisdictions': ['Delaware_Corporate', 'Federal_District']
        }
        
        return DiscoverySource(
            source_type='legal_documents',
            confidence=0.9,
            data=legal_data,
            last_updated=datetime.now()
        )
    
    def _discover_public_records(self, actor_id: str) -> Optional[DiscoverySource]:
        """Discover public record accountability information."""
        # Simulated public records analysis
        
        public_data = {
            'corporate_filings': [f"corp_filing_{actor_id}"],
            'professional_licenses': [f"license_{actor_id}"],
            'board_memberships': [f"board_{actor_id}"],
            'public_statements': [f"statement_{actor_id}"],
            'media_coverage': [f"article_{actor_id}"]
        }
        
        return DiscoverySource(
            source_type='public_records',
            confidence=0.7,
            data=public_data,
            last_updated=datetime.now()
        )
    
    def _extract_immediate_relationships(self, results: List[DiscoverySource]) -> List[AccountabilityRelationship]:
        """Extract immediate accountability relationships from discovery results."""
        relationships = []
        
        for result in results:
            if result.source_type == 'organizational_chart':
                if 'direct_manager' in result.data:
                    relationships.append(AccountabilityRelationship(
                        accountable_to=result.data['direct_manager'],
                        relationship_type='organizational_direct',
                        strength=0.9,
                        verified=True,
                        last_verified=datetime.now()
                    ))
            
            elif result.source_type == 'financial_dependencies':
                if 'budget_approver' in result.data:
                    relationships.append(AccountabilityRelationship(
                        accountable_to=result.data['budget_approver'],
                        relationship_type='financial_direct',
                        strength=0.8,
                        verified=True,
                        last_verified=datetime.now()
                    ))
        
        return relationships
    
    def _extract_ultimate_relationships(self, results: List[DiscoverySource]) -> List[AccountabilityRelationship]:
        """Extract ultimate accountability relationships from discovery results."""
        relationships = []
        
        for result in results:
            if result.source_type == 'regulatory_filings':
                for body in result.data.get('regulatory_bodies', []):
                    relationships.append(AccountabilityRelationship(
                        accountable_to=body,
                        relationship_type='regulatory_ultimate',
                        strength=1.0,
                        verified=True,
                        last_verified=datetime.now()
                    ))
        
        return relationships
    
    def _extract_constraint_sources(self, results: List[DiscoverySource]) -> List[ConstraintSource]:
        """Extract constraint sources from discovery results."""
        constraints = []
        
        for result in results:
            if result.source_type == 'legal_documents':
                constraints.append(ConstraintSource(
                    source_type='legal',
                    description='Employment contract and fiduciary duties',
                    enforcement_mechanism='Legal system',
                    strength=1.0,
                    active=True
                ))
        
        return constraints
    
    def _calculate_discovery_confidence(self, results: List[DiscoverySource]) -> float:
        """Calculate overall confidence in discovery results."""
        if not results:
            return 0.0
        
        weighted_confidence = sum(
            result.confidence * self.discovery_sources[result.source_type]['weight']
            for result in results
        )
        total_weight = sum(
            self.discovery_sources[result.source_type]['weight']
            for result in results
        )
        
        return weighted_confidence / total_weight if total_weight > 0 else 0.0
    
    def _determine_primary_discovery_method(self, results: List[DiscoverySource]) -> str:
        """Determine the primary discovery method used."""
        if not results:
            return 'none'
        
        # Return the highest confidence source
        best_result = max(results, key=lambda r: r.confidence)
        return best_result.source_type
    
    def _validate_independence_claim(self, claim: IndependenceClaim, chain: AccountabilityChain) -> bool:
        """Validate independence claim against discovered accountability chain."""
        # Independence is invalid if we found significant accountability relationships
        has_immediate_accountability = len(chain.immediate_accountability) > 0
        has_ultimate_accountability = len(chain.ultimate_accountability) > 0
        has_constraints = len(chain.constraint_sources) > 0
        
        # High confidence discovery that found accountability = invalid independence claim
        if chain.verification_confidence > 0.8 and (has_immediate_accountability or has_ultimate_accountability or has_constraints):
            return False
        
        return True  # Benefit of doubt if discovery confidence is low
    
    def _calculate_research_confidence(self, claim: IndependenceClaim, chain: AccountabilityChain) -> float:
        """Calculate confidence in independence claim research."""
        # Base confidence on discovery confidence and evidence strength
        base_confidence = chain.verification_confidence
        
        # Adjust based on claim evidence quality
        evidence_quality = len(claim.supporting_evidence) / 5.0  # Normalize to 0-1
        evidence_quality = min(1.0, evidence_quality)
        
        return (base_confidence + evidence_quality) / 2.0
    
    def _get_cached_chain(self, actor_id: str) -> Optional[AccountabilityChain]:
        """Get cached accountability chain if still valid."""
        if actor_id not in self._chain_cache:
            return None
        
        cached_entry = self._chain_cache[actor_id]
        if datetime.now() - cached_entry['timestamp'] > self._cache_ttl:
            del self._chain_cache[actor_id]
            return None
        
        return cached_entry['chain']
    
    def _cache_chain(self, actor_id: str, chain: AccountabilityChain):
        """Cache accountability chain for future use."""
        self._chain_cache[actor_id] = {
            'chain': chain,
            'timestamp': datetime.now()
        }
    
    def _apply_change_to_cache(self, change: ChainChange):
        """Apply a chain change to cached data."""
        if change.actor_id in self._chain_cache:
            # Invalidate cache - simpler than trying to apply changes
            del self._chain_cache[change.actor_id]