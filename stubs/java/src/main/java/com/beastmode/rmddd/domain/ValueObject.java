package com.beastmode.rmddd.domain;

import com.beastmode.rmddd.utilities.ValidationResult;

/**
 * Base class for value objects.
 * Provides value-based equality and immutability enforcement.
 */
public abstract class ValueObject {
    
    /**
     * Validate value object constraints
     * @return Validation result
     */
    public abstract ValidationResult validate();
    
    /**
     * Value objects are equal if all their attributes are equal
     */
    @Override
    public abstract boolean equals(Object o);
    
    /**
     * Hash code based on all attributes
     */
    @Override
    public abstract int hashCode();
    
    /**
     * String representation of the value object
     */
    @Override
    public abstract String toString();
    
    /**
     * Validate the value object during construction
     * Throws IllegalArgumentException if validation fails
     */
    protected void validateOnConstruction() {
        ValidationResult result = validate();
        if (!result.isValid()) {
            throw new IllegalArgumentException(
                "Invalid value object: " + String.join(", ", result.getErrors())
            );
        }
    }
}