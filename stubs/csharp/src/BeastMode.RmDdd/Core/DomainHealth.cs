using System;

namespace BeastMode.RmDdd.Core
{
    /// <summary>
    /// Domain-specific health information.
    /// </summary>
    public class DomainHealth
    {
        public string DomainContext { get; }
        public bool BoundaryIntegrity { get; }
        public bool InvariantCompliance { get; }
        public double LanguageConsistency { get; }
        public double ComplexityScore { get; }
        
        public DomainHealth(
            string domainContext,
            bool boundaryIntegrity,
            bool invariantCompliance,
            double languageConsistency,
            double complexityScore)
        {
            DomainContext = domainContext ?? throw new ArgumentNullException(nameof(domainContext));
            BoundaryIntegrity = boundaryIntegrity;
            InvariantCompliance = invariantCompliance;
            LanguageConsistency = ValidatePercentage(languageConsistency, nameof(languageConsistency));
            ComplexityScore = ValidateNonNegative(complexityScore, nameof(complexityScore));
        }
        
        private static double ValidatePercentage(double value, string parameterName)
        {
            if (value < 0.0 || value > 1.0)
            {
                throw new ArgumentOutOfRangeException(parameterName, value, "Value must be between 0.0 and 1.0");
            }
            return value;
        }
        
        private static double ValidateNonNegative(double value, string parameterName)
        {
            if (value < 0.0)
            {
                throw new ArgumentOutOfRangeException(parameterName, value, "Value must be non-negative");
            }
            return value;
        }
        
        /// <summary>
        /// Gets whether the domain is healthy
        /// </summary>
        public bool IsHealthy => BoundaryIntegrity && 
                                InvariantCompliance && 
                                LanguageConsistency >= 0.8 && 
                                ComplexityScore <= 10.0;
        
        public override bool Equals(object? obj)
        {
            if (obj is not DomainHealth other) return false;
            
            return DomainContext == other.DomainContext &&
                   BoundaryIntegrity == other.BoundaryIntegrity &&
                   InvariantCompliance == other.InvariantCompliance &&
                   Math.Abs(LanguageConsistency - other.LanguageConsistency) < 0.001 &&
                   Math.Abs(ComplexityScore - other.ComplexityScore) < 0.001;
        }
        
        public override int GetHashCode()
        {
            return HashCode.Combine(DomainContext, BoundaryIntegrity, InvariantCompliance, 
                                  LanguageConsistency, ComplexityScore);
        }
        
        public override string ToString()
        {
            return $"DomainHealth {{ DomainContext = '{DomainContext}', BoundaryIntegrity = {BoundaryIntegrity}, " +
                   $"InvariantCompliance = {InvariantCompliance}, LanguageConsistency = {LanguageConsistency:F2}, " +
                   $"ComplexityScore = {ComplexityScore:F2} }}";
        }
    }
}