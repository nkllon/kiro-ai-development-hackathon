package com.beastmode.rmddd.examples.ecommerce;

import com.beastmode.rmddd.domain.ValueObject;
import com.beastmode.rmddd.utilities.ValidationResult;

import java.util.Objects;
import java.util.UUID;

/**
 * Value object representing a Product identifier.
 */
public class ProductId extends ValueObject {
    
    private final UUID value;
    
    public ProductId(UUID value) {
        this.value = Objects.requireNonNull(value, "Product ID value cannot be null");
        validateOnConstruction();
    }
    
    public ProductId(String value) {
        this(UUID.fromString(value));
    }
    
    public static ProductId generate() {
        return new ProductId(UUID.randomUUID());
    }
    
    public UUID getValue() {
        return value;
    }
    
    @Override
    public ValidationResult validate() {
        ValidationResult result = new ValidationResult();
        
        if (value == null) {
            result.addError("Product ID value cannot be null");
        }
        
        return result;
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        ProductId productId = (ProductId) o;
        return Objects.equals(value, productId.value);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(value);
    }
    
    @Override
    public String toString() {
        return "ProductId{" + value + '}';
    }
}