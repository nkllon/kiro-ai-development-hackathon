package com.beastmode.rmddd.core;

import java.util.Objects;

/**
 * Domain-specific health information.
 */
public class DomainHealth {
    
    private final String domainContext;
    private final boolean boundaryIntegrity;
    private final boolean invariantCompliance;
    private final double languageConsistency;
    private final double complexityScore;
    
    public DomainHealth(String domainContext,
                       boolean boundaryIntegrity,
                       boolean invariantCompliance,
                       double languageConsistency,
                       double complexityScore) {
        this.domainContext = Objects.requireNonNull(domainContext, "Domain context cannot be null");
        this.boundaryIntegrity = boundaryIntegrity;
        this.invariantCompliance = invariantCompliance;
        this.languageConsistency = validatePercentage(languageConsistency, "Language consistency");
        this.complexityScore = validateNonNegative(complexityScore, "Complexity score");
    }
    
    private double validatePercentage(double value, String fieldName) {
        if (value < 0.0 || value > 1.0) {
            throw new IllegalArgumentException(fieldName + " must be between 0.0 and 1.0");
        }
        return value;
    }
    
    private double validateNonNegative(double value, String fieldName) {
        if (value < 0.0) {
            throw new IllegalArgumentException(fieldName + " must be non-negative");
        }
        return value;
    }
    
    public String getDomainContext() {
        return domainContext;
    }
    
    public boolean isBoundaryIntegrity() {
        return boundaryIntegrity;
    }
    
    public boolean isInvariantCompliance() {
        return invariantCompliance;
    }
    
    public double getLanguageConsistency() {
        return languageConsistency;
    }
    
    public double getComplexityScore() {
        return complexityScore;
    }
    
    public boolean isHealthy() {
        return boundaryIntegrity && 
               invariantCompliance && 
               languageConsistency >= 0.8 && 
               complexityScore <= 10.0;
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        DomainHealth that = (DomainHealth) o;
        return boundaryIntegrity == that.boundaryIntegrity &&
               invariantCompliance == that.invariantCompliance &&
               Double.compare(that.languageConsistency, languageConsistency) == 0 &&
               Double.compare(that.complexityScore, complexityScore) == 0 &&
               Objects.equals(domainContext, that.domainContext);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(domainContext, boundaryIntegrity, invariantCompliance, 
                          languageConsistency, complexityScore);
    }
    
    @Override
    public String toString() {
        return "DomainHealth{" +
               "domainContext='" + domainContext + '\'' +
               ", boundaryIntegrity=" + boundaryIntegrity +
               ", invariantCompliance=" + invariantCompliance +
               ", languageConsistency=" + languageConsistency +
               ", complexityScore=" + complexityScore +
               '}';
    }
}