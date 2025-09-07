package com.beastmode.rmddd.examples.ecommerce;

import java.math.BigDecimal;
import java.util.Objects;

/**
 * Order line entity representing a line item in an order.
 * This is an entity within the Order aggregate.
 */
public class OrderLine {
    
    private final ProductId productId;
    private int quantity;
    private BigDecimal unitPrice;
    
    public OrderLine(ProductId productId, int quantity, BigDecimal unitPrice) {
        this.productId = Objects.requireNonNull(productId, "Product ID cannot be null");
        this.unitPrice = Objects.requireNonNull(unitPrice, "Unit price cannot be null");
        
        if (quantity <= 0) {
            throw new IllegalArgumentException("Quantity must be positive");
        }
        
        if (unitPrice.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("Unit price cannot be negative");
        }
        
        this.quantity = quantity;
    }
    
    public ProductId getProductId() {
        return productId;
    }
    
    public int getQuantity() {
        return quantity;
    }
    
    public void setQuantity(int quantity) {
        if (quantity <= 0) {
            throw new IllegalArgumentException("Quantity must be positive");
        }
        this.quantity = quantity;
    }
    
    public BigDecimal getUnitPrice() {
        return unitPrice;
    }
    
    public void setUnitPrice(BigDecimal unitPrice) {
        if (unitPrice == null || unitPrice.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("Unit price cannot be null or negative");
        }
        this.unitPrice = unitPrice;
    }
    
    public BigDecimal getLineTotal() {
        return unitPrice.multiply(BigDecimal.valueOf(quantity));
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        OrderLine orderLine = (OrderLine) o;
        return Objects.equals(productId, orderLine.productId);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(productId);
    }
    
    @Override
    public String toString() {
        return "OrderLine{" +
               "productId=" + productId +
               ", quantity=" + quantity +
               ", unitPrice=" + unitPrice +
               ", lineTotal=" + getLineTotal() +
               '}';
    }
}