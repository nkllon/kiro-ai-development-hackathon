package com.beastmode.rmddd.examples.ecommerce;

import com.beastmode.rmddd.domain.ValueObject;
import com.beastmode.rmddd.utilities.ValidationResult;

import java.util.Objects;
import java.util.UUID;

/**
 * Value object representing an Order identifier.
 * Demonstrates proper value object implementation in Java.
 */
public class OrderId extends ValueObject {
    
    private final UUID value;
    
    public OrderId(UUID value) {
        this.value = Objects.requireNonNull(value, "Order ID value cannot be null");
        validateOnConstruction();
    }
    
    public OrderId(String value) {
        this(UUID.fromString(value));
    }
    
    public static OrderId generate() {
        return new OrderId(UUID.randomUUID());
    }
    
    public UUID getValue() {
        return value;
    }
    
    @Override
    public ValidationResult validate() {
        ValidationResult result = new ValidationResult();
        
        if (value == null) {
            result.addError("Order ID value cannot be null");
        }
        
        return result;
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        OrderId orderId = (OrderId) o;
        return Objects.equals(value, orderId.value);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(value);
    }
    
    @Override
    public String toString() {
        return "OrderId{" + value + '}';
    }
}