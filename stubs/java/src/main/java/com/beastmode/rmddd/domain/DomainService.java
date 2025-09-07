package com.beastmode.rmddd.domain;

import com.beastmode.rmddd.core.DomainReflectiveModule;
import com.beastmode.rmddd.core.ModuleHealth;
import com.beastmode.rmddd.core.ModuleStatus;
import com.beastmode.rmddd.core.ModuleCapability;
import com.beastmode.rmddd.core.DomainHealth;
import com.beastmode.rmddd.utilities.ValidationResult;

import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;

/**
 * Base class for domain services.
 * Provides stateless domain logic encapsulation with RM compliance.
 */
public abstract class DomainService implements DomainReflectiveModule {
    
    private final String serviceName;
    private final String domainContext;
    private final String moduleId;
    
    protected DomainService(String serviceName, String domainContext) {
        this.serviceName = Objects.requireNonNull(serviceName, "Service name cannot be null");
        this.domainContext = Objects.requireNonNull(domainContext, "Domain context cannot be null");
        this.moduleId = generateModuleId();
    }
    
    private String generateModuleId() {
        return "domain_service_" + serviceName.toLowerCase() + "_" + UUID.randomUUID().toString();
    }
    
    public String getServiceName() {
        return serviceName;
    }
    
    @Override
    public String getDomainContext() {
        return domainContext;
    }
    
    @Override
    public String getModuleId() {
        return moduleId;
    }
    
    @Override
    public CompletableFuture<ModuleHealth> getModuleStatus() {
        ValidationResult validation = validateDomainInvariants();
        ModuleStatus status = validation.isValid() ? ModuleStatus.AVAILABLE : ModuleStatus.DEGRADED;
        
        ModuleHealth health = new ModuleHealth(
            status,
            "Domain Service: " + serviceName,
            List.of(new ModuleCapability(
                "domain_service_" + serviceName,
                "Domain service: " + serviceName,
                validation.isValid(),
                "1.0.0"
            )),
            getDomainHealth(),
            Map.of(
                "service_name", serviceName,
                "domain_context", domainContext,
                "stateless", true
            )
        );
        
        return CompletableFuture.completedFuture(health);
    }
    
    @Override
    public CompletableFuture<List<ModuleCapability>> getModuleCapabilities() {
        return CompletableFuture.completedFuture(List.of(
            new ModuleCapability(
                "domain_service_" + serviceName,
                "Domain service: " + serviceName,
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
            "service_name", serviceName,
            "domain_context", domainContext,
            "stateless", true,
            "invariants_valid", validateDomainInvariants().isValid()
        ));
    }
    
    @Override
    public CompletableFuture<Void> initialize() {
        // Domain services are typically stateless and don't need initialization
        return CompletableFuture.completedFuture(null);
    }
    
    @Override
    public CompletableFuture<Void> shutdown() {
        // Domain services are typically stateless and don't need shutdown
        return CompletableFuture.completedFuture(null);
    }
    
    @Override
    public ValidationResult validateDomainInvariants() {
        ValidationResult result = new ValidationResult();
        
        // Validate that service operates within domain boundaries
        DomainBoundaries boundaries = getDomainBoundaries();
        if (!boundaries.getContext().equals(domainContext)) {
            result.addError("Service domain context mismatch");
        }
        
        // Additional domain-specific validation can be added by subclasses
        return result;
    }
    
    @Override
    public DomainHealth getDomainHealth() {
        ValidationResult validation = validateDomainInvariants();
        
        return new DomainHealth(
            domainContext,
            true, // Domain services maintain boundary integrity by design
            validation.isValid(),
            1.0, // Services should have perfect language consistency
            calculateComplexityScore()
        );
    }
    
    /**
     * Calculate complexity score for this domain service
     * Subclasses can override to provide more sophisticated complexity calculation
     * @return Complexity score (lower is better)
     */
    protected double calculateComplexityScore() {
        // Default implementation - can be overridden
        return 1.0;
    }
}