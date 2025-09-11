package com.beastmode.rmddd.examples.ecommerce;

import com.beastmode.rmddd.domain.DomainEvent;

import java.math.BigDecimal;
import java.util.Map;

/**
 * Domain event fired when an order is confirmed.
 */
public class OrderConfirmedEvent extends DomainEvent {
    
    private final BigDecimal totalAmount;
    
    public OrderConfirmedEvent(OrderId orderId, BigDecimal totalAmount) {
        super(orderId);
        this.totalAmount = totalAmount;
    }
    
    public OrderId getOrderId() {
        return (OrderId) getAggregateId();
    }
    
    public BigDecimal getTotalAmount() {
        return totalAmount;
    }
    
    @Override
    public Map<String, Object> getEventData() {
        return Map.of(
            "order_id", getOrderId().getValue().toString(),
            "total_amount", totalAmount.toString()
        );
    }
}