package com.beastmode.rmddd.examples.ecommerce;

import com.beastmode.rmddd.domain.DomainEvent;

import java.math.BigDecimal;
import java.util.Map;

/**
 * Domain event fired when an order line is added to an order.
 */
public class OrderLineAddedEvent extends DomainEvent {
    
    private final ProductId productId;
    private final int quantity;
    private final BigDecimal unitPrice;
    
    public OrderLineAddedEvent(OrderId orderId, ProductId productId, int quantity, BigDecimal unitPrice) {
        super(orderId);
        this.productId = productId;
        this.quantity = quantity;
        this.unitPrice = unitPrice;
    }
    
    public OrderId getOrderId() {
        return (OrderId) getAggregateId();
    }
    
    public ProductId getProductId() {
        return productId;
    }
    
    public int getQuantity() {
        return quantity;
    }
    
    public BigDecimal getUnitPrice() {
        return unitPrice;
    }
    
    @Override
    public Map<String, Object> getEventData() {
        return Map.of(
            "order_id", getOrderId().getValue().toString(),
            "product_id", productId.getValue().toString(),
            "quantity", quantity,
            "unit_price", unitPrice.toString(),
            "line_total", unitPrice.multiply(BigDecimal.valueOf(quantity)).toString()
        );
    }
}