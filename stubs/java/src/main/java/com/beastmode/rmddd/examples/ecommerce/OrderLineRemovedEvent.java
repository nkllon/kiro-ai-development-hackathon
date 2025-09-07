package com.beastmode.rmddd.examples.ecommerce;

import com.beastmode.rmddd.domain.DomainEvent;

import java.util.Map;

/**
 * Domain event fired when an order line is removed from an order.
 */
public class OrderLineRemovedEvent extends DomainEvent {
    
    private final ProductId productId;
    
    public OrderLineRemovedEvent(OrderId orderId, ProductId productId) {
        super(orderId);
        this.productId = productId;
    }
    
    public OrderId getOrderId() {
        return (OrderId) getAggregateId();
    }
    
    public ProductId getProductId() {
        return productId;
    }
    
    @Override
    public Map<String, Object> getEventData() {
        return Map.of(
            "order_id", getOrderId().getValue().toString(),
            "product_id", productId.getValue().toString()
        );
    }
}