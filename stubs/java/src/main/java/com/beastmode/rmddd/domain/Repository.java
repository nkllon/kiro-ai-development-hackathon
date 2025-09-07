package com.beastmode.rmddd.domain;

import java.util.List;
import java.util.Optional;
import java.util.concurrent.CompletableFuture;

/**
 * Abstract repository interface for domain layer.
 * Provides domain-appropriate data access patterns.
 * 
 * @param <T> The entity type
 * @param <ID> The entity identifier type
 */
public interface Repository<T extends Entity<ID>, ID> {
    
    /**
     * Get entity by ID
     * @param entityId The entity identifier
     * @return CompletableFuture containing optional entity
     */
    CompletableFuture<Optional<T>> getById(ID entityId);
    
    /**
     * Save entity
     * @param entity The entity to save
     * @return CompletableFuture containing saved entity
     */
    CompletableFuture<T> save(T entity);
    
    /**
     * Delete entity
     * @param entityId The entity identifier
     * @return CompletableFuture containing deletion success status
     */
    CompletableFuture<Boolean> delete(ID entityId);
    
    /**
     * Find entities by domain criteria
     * @param criteria The domain criteria
     * @return CompletableFuture containing list of matching entities
     */
    CompletableFuture<List<T>> findByCriteria(DomainCriteria criteria);
    
    /**
     * Check if entity exists
     * @param entityId The entity identifier
     * @return CompletableFuture containing existence status
     */
    CompletableFuture<Boolean> exists(ID entityId);
    
    /**
     * Count entities matching criteria
     * @param criteria The domain criteria
     * @return CompletableFuture containing count
     */
    CompletableFuture<Long> count(DomainCriteria criteria);
    
    /**
     * Find all entities (use with caution for large datasets)
     * @return CompletableFuture containing all entities
     */
    CompletableFuture<List<T>> findAll();
}