package com.beastmode.rmddd.examples.ecommerce;

import com.beastmode.rmddd.domain.ValueObject;
import com.beastmode.rmddd.utilities.ValidationResult;

import java.util.Objects;
import java.util.UUID;

/**
 * Value object representing a Customer identifier.
 */
public class CustomerId extends ValueObject {
    
    private final UUID value;
    
    public CustomerId(UUID value) {
        this.value = Objects.requireNonNull(value, "Customer ID value cannot be null");
        validateOnConstruction();
    }
    
    public CustomerId(String value) {
        this(UUID.fromString(value));
    }
    
    public static CustomerId generate() {
        return new CustomerId(UUID.randomUUID());
    }
    
    public UUID getValue() {
        return value;
    }
    
    @Override
    public ValidationResult validate() {
        ValidationResult result = new ValidationResult();
        
        if (value == null) {
            result.addError("Customer ID value cannot be null");
        }
        
        return result;
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        CustomerId that = (CustomerId) o;
        return Objects.equals(value, that.value);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(value);
    }
    
    @Override
    public String toString() {
        return "CustomerId{" + value + '}';
    }
}