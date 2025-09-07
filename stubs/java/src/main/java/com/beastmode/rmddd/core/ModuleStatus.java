package com.beastmode.rmddd.core;

/**
 * Enumeration of possible module status values.
 */
public enum ModuleStatus {
    
    /**
     * Module is fully available and operational
     */
    AVAILABLE("Available"),
    
    /**
     * Module is operational but with reduced functionality
     */
    DEGRADED("Degraded"),
    
    /**
     * Module is temporarily unavailable
     */
    UNAVAILABLE("Unavailable"),
    
    /**
     * Module is in error state
     */
    ERROR("Error"),
    
    /**
     * Module is starting up
     */
    STARTING("Starting"),
    
    /**
     * Module is shutting down
     */
    STOPPING("Stopping");
    
    private final String displayName;
    
    ModuleStatus(String displayName) {
        this.displayName = displayName;
    }
    
    public String getDisplayName() {
        return displayName;
    }
    
    public boolean isOperational() {
        return this == AVAILABLE || this == DEGRADED;
    }
    
    public boolean isHealthy() {
        return this == AVAILABLE;
    }
}