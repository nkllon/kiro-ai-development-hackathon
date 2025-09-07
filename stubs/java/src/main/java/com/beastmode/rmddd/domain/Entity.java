package com.beastmode.rmddd.domain;

import com.beastmode.rmddd.core.DomainReflectiveModule;
import com.beastmode.rmddd.core.ModuleHealth;
import com.beastmode.rmddd.core.ModuleStatus;
import com.beastmode.rmddd.core.ModuleCapability;
import com.beastmode.rmddd.utilities.ValidationResult;

import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;

/**
 * Base class for domain entities.
 * Provides identity, equality, and RM compliance.
 * 
 * @param <ID> The type of the entity identifier
 */
public abstract class Entity<ID> implements DomainReflectiveModule {
    
    private final ID id;
    private final String domainContext;
    private final String moduleId;
    private int version;
    private final Instant createdAt;
    private Instant updatedAt;
    
    protected Entity(ID id, String domainContext) {
        this.id = Objects.requireNonNull(id, "Entity ID cannot be null");
        this.domainContext = Objects.requireNonNull(domainContext, "Domain context cannot be null");
        this.moduleId = generateModuleId();
        this.version = 1;
        this.createdAt = Instant.now();
        this.updatedAt = Instant.now();
    }
    
    private String generateModuleId() {
        return "entity_" + getClass().getSimpleName().toLowerCase() + "_" + UUID.randomUUID().toString();
    }
    
    public ID getId() {
        return id;
    }
    
    @Override
    public String getDomainContext() {
        return domainContext;
    }
    
    @Override
    public String getModuleId() {
        return moduleId;
    }
    
    public int getVersion() {
        return version;
    }
    
    public Instant getCreatedAt() {
        return createdAt;
    }
    
    public Instant getUpdatedAt() {
        return updatedAt;
    }
    
    protected void updateVersion() {
        this.version++;
        this.updatedAt = Instant.now();
    }
    
    @Override
    public CompletableFuture<ModuleHealth> getModuleStatus() {
        ValidationResult validation = validateDomainInvariants();
        ModuleStatus status = validation.isValid() ? ModuleStatus.AVAILABLE : ModuleStatus.DEGRADED;
        
        ModuleHealth health = new ModuleHealth(
            status,
            "Entity: " + getClass().getSimpleName(),
            List.of(new ModuleCapability(
                "domain_entity",
                "Domain entity with identity and invariants",
                validation.isValid(),
                "1.0.0"
            )),
            getDomainHealth(),
            Map.of(
                "entity_type", getClass().getSimpleName(),
                "version", version,
                "created_at", createdAt.toString(),
                "updated_at", updatedAt.toString()
            )
        );
        
        return CompletableFuture.completedFuture(health);
    }
    
    @Override
    public CompletableFuture<List<ModuleCapability>> getModuleCapabilities() {
        return CompletableFuture.completedFuture(List.of(
            new ModuleCapability(
                "domain_entity",
                "Domain entity with identity and invariants",
                true,
                "1.0.0"
            )
        ));
    }
    
    @Override
    public CompletableFuture<Boolean> isHealthy() {
        return CompletableFuture.completedFuture(validateDomainInvariants().isValid());
    }
    
    @Override
    public CompletableFuture<Map<String, Object>> getHealthIndicators() {
        return CompletableFuture.completedFuture(Map.of(
            "entity_type", getClass().getSimpleName(),
            "version", version,
            "domain_context", domainContext,
            "invariants_valid", validateDomainInvariants().isValid()
        ));
    }
    
    @Override
    public CompletableFuture<Void> initialize() {
        // Default implementation - entities are typically initialized on creation
        return CompletableFuture.completedFuture(null);
    }
    
    @Override
    public CompletableFuture<Void> shutdown() {
        // Default implementation - entities don't typically need shutdown
        return CompletableFuture.completedFuture(null);
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Entity<?> entity = (Entity<?>) o;
        return Objects.equals(id, entity.id);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(getClass(), id);
    }
    
    @Override
    public String toString() {
        return getClass().getSimpleName() + "{" +
               "id=" + id +
               ", domainContext='" + domainContext + '\'' +
               ", version=" + version +
               '}';
    }
}