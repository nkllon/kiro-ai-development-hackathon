package com.beastmode.rmddd.core;

import com.beastmode.rmddd.domain.DomainBoundaries;
import com.beastmode.rmddd.utilities.ValidationResult;

/**
 * Enhanced RM interface with domain awareness.
 * Extends ReflectiveModule with domain-specific capabilities.
 */
public interface DomainReflectiveModule extends ReflectiveModule {
    
    /**
     * Get the domain context this module operates in
     * @return Domain context name
     */
    String getDomainContext();
    
    /**
     * Get domain boundaries for this module
     * @return Domain boundaries definition
     */
    DomainBoundaries getDomainBoundaries();
    
    /**
     * Validate domain invariants
     * @return Validation result with any violations
     */
    ValidationResult validateDomainInvariants();
    
    /**
     * Get domain-specific health information
     * @return Domain health status
     */
    DomainHealth getDomainHealth();
}