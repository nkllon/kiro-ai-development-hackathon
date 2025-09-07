package com.beastmode.rmddd.domain;

import java.util.Objects;
import java.util.Set;
import java.util.HashSet;
import java.util.Collections;

/**
 * Defines domain boundaries for a component.
 * Specifies the domain context, capabilities, and constraints.
 */
public class DomainBoundaries {
    
    private final String context;
    private final String aggregateType;
    private final Set<String> capabilities;
    private final Set<String> constraints;
    private final String ubiquitousLanguage;
    
    private DomainBoundaries(Builder builder) {
        this.context = Objects.requireNonNull(builder.context, "Context cannot be null");
        this.aggregateType = builder.aggregateType;
        this.capabilities = Collections.unmodifiableSet(new HashSet<>(builder.capabilities));
        this.constraints = Collections.unmodifiableSet(new HashSet<>(builder.constraints));
        this.ubiquitousLanguage = builder.ubiquitousLanguage;
    }
    
    public String getContext() {
        return context;
    }
    
    public String getAggregateType() {
        return aggregateType;
    }
    
    public Set<String> getCapabilities() {
        return capabilities;
    }
    
    public Set<String> getConstraints() {
        return constraints;
    }
    
    public String getUbiquitousLanguage() {
        return ubiquitousLanguage;
    }
    
    public boolean hasCapability(String capability) {
        return capabilities.contains(capability);
    }
    
    public boolean hasConstraint(String constraint) {
        return constraints.contains(constraint);
    }
    
    public static Builder builder() {
        return new Builder();
    }
    
    public static class Builder {
        private String context;
        private String aggregateType;
        private Set<String> capabilities = new HashSet<>();
        private Set<String> constraints = new HashSet<>();
        private String ubiquitousLanguage;
        
        public Builder context(String context) {
            this.context = context;
            return this;
        }
        
        public Builder aggregateType(String aggregateType) {
            this.aggregateType = aggregateType;
            return this;
        }
        
        public Builder capability(String capability) {
            this.capabilities.add(capability);
            return this;
        }
        
        public Builder capabilities(Set<String> capabilities) {
            this.capabilities.addAll(capabilities);
            return this;
        }
        
        public Builder constraint(String constraint) {
            this.constraints.add(constraint);
            return this;
        }
        
        public Builder constraints(Set<String> constraints) {
            this.constraints.addAll(constraints);
            return this;
        }
        
        public Builder ubiquitousLanguage(String ubiquitousLanguage) {
            this.ubiquitousLanguage = ubiquitousLanguage;
            return this;
        }
        
        public DomainBoundaries build() {
            return new DomainBoundaries(this);
        }
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        DomainBoundaries that = (DomainBoundaries) o;
        return Objects.equals(context, that.context) &&
               Objects.equals(aggregateType, that.aggregateType) &&
               Objects.equals(capabilities, that.capabilities) &&
               Objects.equals(constraints, that.constraints) &&
               Objects.equals(ubiquitousLanguage, that.ubiquitousLanguage);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(context, aggregateType, capabilities, constraints, ubiquitousLanguage);
    }
    
    @Override
    public String toString() {
        return "DomainBoundaries{" +
               "context='" + context + '\'' +
               ", aggregateType='" + aggregateType + '\'' +
               ", capabilities=" + capabilities +
               ", constraints=" + constraints +
               ", ubiquitousLanguage='" + ubiquitousLanguage + '\'' +
               '}';
    }
}