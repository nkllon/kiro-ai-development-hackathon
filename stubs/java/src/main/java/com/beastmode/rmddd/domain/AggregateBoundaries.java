package com.beastmode.rmddd.domain;

import java.util.Objects;
import java.util.Set;
import java.util.HashSet;
import java.util.Collections;

/**
 * Defines aggregate boundaries and consistency rules.
 * Specifies what entities belong to the aggregate and consistency constraints.
 */
public class AggregateBoundaries {
    
    private final String aggregateType;
    private final Set<String> entityTypes;
    private final Set<String> invariants;
    private final int maxSize;
    private final boolean enforceConsistency;
    
    private AggregateBoundaries(Builder builder) {
        this.aggregateType = Objects.requireNonNull(builder.aggregateType, "Aggregate type cannot be null");
        this.entityTypes = Collections.unmodifiableSet(new HashSet<>(builder.entityTypes));
        this.invariants = Collections.unmodifiableSet(new HashSet<>(builder.invariants));
        this.maxSize = builder.maxSize;
        this.enforceConsistency = builder.enforceConsistency;
    }
    
    public String getAggregateType() {
        return aggregateType;
    }
    
    public Set<String> getEntityTypes() {
        return entityTypes;
    }
    
    public Set<String> getInvariants() {
        return invariants;
    }
    
    public int getMaxSize() {
        return maxSize;
    }
    
    public boolean isEnforceConsistency() {
        return enforceConsistency;
    }
    
    public boolean containsEntityType(String entityType) {
        return entityTypes.contains(entityType);
    }
    
    public boolean hasInvariant(String invariant) {
        return invariants.contains(invariant);
    }
    
    public static Builder builder() {
        return new Builder();
    }
    
    public static class Builder {
        private String aggregateType;
        private Set<String> entityTypes = new HashSet<>();
        private Set<String> invariants = new HashSet<>();
        private int maxSize = 100; // Default max size
        private boolean enforceConsistency = true;
        
        public Builder aggregateType(String aggregateType) {
            this.aggregateType = aggregateType;
            return this;
        }
        
        public Builder entityType(String entityType) {
            this.entityTypes.add(entityType);
            return this;
        }
        
        public Builder entityTypes(Set<String> entityTypes) {
            this.entityTypes.addAll(entityTypes);
            return this;
        }
        
        public Builder invariant(String invariant) {
            this.invariants.add(invariant);
            return this;
        }
        
        public Builder invariants(Set<String> invariants) {
            this.invariants.addAll(invariants);
            return this;
        }
        
        public Builder maxSize(int maxSize) {
            if (maxSize <= 0) {
                throw new IllegalArgumentException("Max size must be positive");
            }
            this.maxSize = maxSize;
            return this;
        }
        
        public Builder enforceConsistency(boolean enforceConsistency) {
            this.enforceConsistency = enforceConsistency;
            return this;
        }
        
        public AggregateBoundaries build() {
            return new AggregateBoundaries(this);
        }
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        AggregateBoundaries that = (AggregateBoundaries) o;
        return maxSize == that.maxSize &&
               enforceConsistency == that.enforceConsistency &&
               Objects.equals(aggregateType, that.aggregateType) &&
               Objects.equals(entityTypes, that.entityTypes) &&
               Objects.equals(invariants, that.invariants);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(aggregateType, entityTypes, invariants, maxSize, enforceConsistency);
    }
    
    @Override
    public String toString() {
        return "AggregateBoundaries{" +
               "aggregateType='" + aggregateType + '\'' +
               ", entityTypes=" + entityTypes +
               ", invariants=" + invariants +
               ", maxSize=" + maxSize +
               ", enforceConsistency=" + enforceConsistency +
               '}';
    }
}