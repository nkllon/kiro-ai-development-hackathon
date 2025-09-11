package com.beastmode.rmddd.examples.ecommerce;

import com.beastmode.rmddd.domain.DomainEvent;

import java.util.Map;

/**
 * Domain event fired when an order is cancelled.
 */
public class OrderCancelledEvent extends DomainEvent {
    
    public OrderCancelledEvent(OrderId orderId) {
        super(orderId);
    }
    
    public OrderId getOrderId() {
        return (OrderId) getAggregateId();
    }
    
    @Override
    public Map<String, Object> getEventData() {
        return Map.of(
            "order_id", getOrderId().getValue().toString()
        );
    }
}