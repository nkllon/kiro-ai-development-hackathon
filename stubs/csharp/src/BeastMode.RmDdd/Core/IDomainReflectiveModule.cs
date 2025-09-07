using BeastMode.RmDdd.Domain;
using BeastMode.RmDdd.Utilities;

namespace BeastMode.RmDdd.Core
{
    /// <summary>
    /// Enhanced RM interface with domain awareness.
    /// Extends IReflectiveModule with domain-specific capabilities.
    /// </summary>
    public interface IDomainReflectiveModule : IReflectiveModule
    {
        /// <summary>
        /// Gets the domain context this module operates in
        /// </summary>
        string DomainContext { get; }
        
        /// <summary>
        /// Get domain boundaries for this module
        /// </summary>
        /// <returns>Domain boundaries definition</returns>
        DomainBoundaries GetDomainBoundaries();
        
        /// <summary>
        /// Validate domain invariants
        /// </summary>
        /// <returns>Validation result with any violations</returns>
        ValidationResult ValidateDomainInvariants();
        
        /// <summary>
        /// Get domain-specific health information
        /// </summary>
        /// <returns>Domain health status</returns>
        DomainHealth GetDomainHealth();
    }
}