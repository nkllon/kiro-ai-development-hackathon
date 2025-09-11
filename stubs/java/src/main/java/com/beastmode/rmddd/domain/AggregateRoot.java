package com.beastmode.rmddd.domain;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.CompletableFuture;

/**
 * Base class for aggregate roots.
 * Extends Entity with domain event management and aggregate boundary enforcement.
 * 
 * @param <ID> The type of the aggregate root identifier
 */
public abstract class AggregateRoot<ID> extends Entity<ID> {
    
    private final List<DomainEvent> domainEvents;
    
    protected AggregateRoot(ID id, String domainContext) {
        super(id, domainContext);
        this.domainEvents = new ArrayList<>();
    }
    
    /**
     * Add a domain event to be published
     * @param event The domain event to add
     */
    protected void addDomainEvent(DomainEvent event) {
        if (event != null) {
            domainEvents.add(event);
        }
    }
    
    /**
     * Get pending domain events
     * @return Unmodifiable list of pending domain events
     */
    public List<DomainEvent> getDomainEvents() {
        return Collections.unmodifiableList(domainEvents);
    }
    
    /**
     * Clear domain events after publishing
     */
    public void clearDomainEvents() {
        domainEvents.clear();
    }
    
    /**
     * Get aggregate boundaries definition
     * @return Aggregate boundaries
     */
    public abstract AggregateBoundaries getAggregateBoundaries();
    
    /**
     * Validate aggregate-specific rules
     * @return Validation result for aggregate rules
     */
    protected abstract ValidationResult validateAggregateRules();
    
    @Override
    public ValidationResult validateDomainInvariants() {
        ValidationResult entityValidation = super.validateDomainInvariants();
        ValidationResult aggregateValidation = validateAggregateRules();
        
        ValidationResult combined = new ValidationResult();
        
        // Combine validation results
        if (!entityValidation.isValid()) {
            entityValidation.getErrors().forEach(combined::addError);
        }
        
        if (!aggregateValidation.isValid()) {
            aggregateValidation.getErrors().forEach(combined::addError);
        }
        
        entityValidation.getWarnings().forEach(combined::addWarning);
        aggregateValidation.getWarnings().forEach(combined::addWarning);
        
        return combined;
    }
    
    @Override
    public CompletableFuture<ModuleHealth> getModuleStatus() {
        return super.getModuleStatus().thenApply(health -> {
            // Enhance with aggregate-specific information
            health.getHealthIndicators().put("pending_events", domainEvents.size());
            health.getHealthIndicators().put("aggregate_type", getClass().getSimpleName());
            return health;
        });
    }
    
    /**
     * Apply business operation and generate domain events
     * This is a template method that subclasses can override
     * @param operation The business operation to apply
     * @return CompletableFuture that completes when operation is applied
     */
    protected CompletableFuture<Void> applyBusinessOperation(BusinessOperation operation) {
        return CompletableFuture.runAsync(() -> {
            // Template method - subclasses should override
            updateVersion();
        });
    }
    
    /**
     * Marker interface for business operations
     */
    public interface BusinessOperation {
        String getOperationName();
    }
}