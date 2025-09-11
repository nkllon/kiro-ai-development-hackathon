package com.beastmode.rmddd.core;

import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.Objects;

/**
 * Comprehensive module health information.
 */
public class ModuleHealth {
    
    private final ModuleStatus status;
    private final String message;
    private final List<ModuleCapability> capabilities;
    private final DomainHealth domainHealth;
    private final Map<String, Object> healthIndicators;
    private final Instant timestamp;
    
    public ModuleHealth(ModuleStatus status, 
                       String message, 
                       List<ModuleCapability> capabilities,
                       DomainHealth domainHealth,
                       Map<String, Object> healthIndicators) {
        this.status = Objects.requireNonNull(status, "Status cannot be null");
        this.message = Objects.requireNonNull(message, "Message cannot be null");
        this.capabilities = Objects.requireNonNull(capabilities, "Capabilities cannot be null");
        this.domainHealth = domainHealth;
        this.healthIndicators = Objects.requireNonNull(healthIndicators, "Health indicators cannot be null");
        this.timestamp = Instant.now();
    }
    
    public ModuleStatus getStatus() {
        return status;
    }
    
    public String getMessage() {
        return message;
    }
    
    public List<ModuleCapability> getCapabilities() {
        return capabilities;
    }
    
    public DomainHealth getDomainHealth() {
        return domainHealth;
    }
    
    public Map<String, Object> getHealthIndicators() {
        return healthIndicators;
    }
    
    public Instant getTimestamp() {
        return timestamp;
    }
    
    public boolean isHealthy() {
        return status == ModuleStatus.AVAILABLE;
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        ModuleHealth that = (ModuleHealth) o;
        return status == that.status &&
               Objects.equals(message, that.message) &&
               Objects.equals(capabilities, that.capabilities) &&
               Objects.equals(domainHealth, that.domainHealth) &&
               Objects.equals(healthIndicators, that.healthIndicators);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(status, message, capabilities, domainHealth, healthIndicators);
    }
    
    @Override
    public String toString() {
        return "ModuleHealth{" +
               "status=" + status +
               ", message='" + message + '\'' +
               ", capabilities=" + capabilities +
               ", domainHealth=" + domainHealth +
               ", healthIndicators=" + healthIndicators +
               ", timestamp=" + timestamp +
               '}';
    }
}