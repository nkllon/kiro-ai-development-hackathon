package com.beastmode.rmddd.examples.ecommerce;

/**
 * Enumeration of possible order status values.
 */
public enum OrderStatus {
    
    PENDING("Pending"),
    CONFIRMED("Confirmed"),
    SHIPPED("Shipped"),
    DELIVERED("Delivered"),
    CANCELLED("Cancelled");
    
    private final String displayName;
    
    OrderStatus(String displayName) {
        this.displayName = displayName;
    }
    
    public String getDisplayName() {
        return displayName;
    }
    
    public boolean isModifiable() {
        return this == PENDING;
    }
    
    public boolean isCancellable() {
        return this == PENDING || this == CONFIRMED;
    }
    
    public boolean isFinal() {
        return this == DELIVERED || this == CANCELLED;
    }
}