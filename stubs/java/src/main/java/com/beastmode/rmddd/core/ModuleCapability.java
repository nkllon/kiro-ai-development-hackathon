package com.beastmode.rmddd.core;

import java.util.Objects;

/**
 * Represents a capability provided by a module.
 */
public class ModuleCapability {
    
    private final String name;
    private final String description;
    private final boolean available;
    private final String version;
    
    public ModuleCapability(String name, String description, boolean available, String version) {
        this.name = Objects.requireNonNull(name, "Name cannot be null");
        this.description = Objects.requireNonNull(description, "Description cannot be null");
        this.available = available;
        this.version = Objects.requireNonNull(version, "Version cannot be null");
    }
    
    public String getName() {
        return name;
    }
    
    public String getDescription() {
        return description;
    }
    
    public boolean isAvailable() {
        return available;
    }
    
    public String getVersion() {
        return version;
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        ModuleCapability that = (ModuleCapability) o;
        return available == that.available &&
               Objects.equals(name, that.name) &&
               Objects.equals(description, that.description) &&
               Objects.equals(version, that.version);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(name, description, available, version);
    }
    
    @Override
    public String toString() {
        return "ModuleCapability{" +
               "name='" + name + '\'' +
               ", description='" + description + '\'' +
               ", available=" + available +
               ", version='" + version + '\'' +
               '}';
    }
}