package com.beastmode.rmddd.examples.ecommerce;

import com.beastmode.rmddd.domain.DomainEvent;

import java.util.Map;

/**
 * Domain event fired when an order is created.
 */
public class OrderCreatedEvent extends DomainEvent {
    
    private final CustomerId customerId;
    
    public OrderCreatedEvent(OrderId orderId, CustomerId customerId) {
        super(orderId);
        this.customerId = customerId;
    }
    
    public OrderId getOrderId() {
        return (OrderId) getAggregateId();
    }
    
    public CustomerId getCustomerId() {
        return customerId;
    }
    
    @Override
    public Map<String, Object> getEventData() {
        return Map.of(
            "order_id", getOrderId().getValue().toString(),
            "customer_id", customerId.getValue().toString()
        );
    }
}