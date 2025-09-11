package com.beastmode.rmddd.core;

import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

/**
 * Base interface for all RM-DDD components in Java.
 * Provides the core Reflective Module capabilities.
 */
public interface ReflectiveModule {
    
    /**
     * Get the unique module identifier
     * @return Module ID
     */
    String getModuleId();
    
    /**
     * Get current module status
     * @return CompletableFuture containing module health information
     */
    CompletableFuture<ModuleHealth> getModuleStatus();
    
    /**
     * Get module capabilities
     * @return CompletableFuture containing list of module capabilities
     */
    CompletableFuture<List<ModuleCapability>> getModuleCapabilities();
    
    /**
     * Check if module is healthy
     * @return CompletableFuture containing health status
     */
    CompletableFuture<Boolean> isHealthy();
    
    /**
     * Get detailed health indicators
     * @return CompletableFuture containing health indicators map
     */
    CompletableFuture<Map<String, Object>> getHealthIndicators();
    
    /**
     * Initialize the module
     * @return CompletableFuture that completes when initialization is done
     */
    CompletableFuture<Void> initialize();
    
    /**
     * Shutdown the module gracefully
     * @return CompletableFuture that completes when shutdown is done
     */
    CompletableFuture<Void> shutdown();
}