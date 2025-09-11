package com.beastmode.rmddd.examples.ecommerce;

import com.beastmode.rmddd.domain.AggregateRoot;
import com.beastmode.rmddd.domain.DomainBoundaries;
import com.beastmode.rmddd.domain.AggregateBoundaries;
import com.beastmode.rmddd.utilities.ValidationResult;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Objects;

/**
 * Order aggregate root demonstrating proper DDD patterns in Java.
 * Shows how to implement domain logic, invariants, and event generation.
 */
public class Order extends AggregateRoot<OrderId> {
    
    private final CustomerId customerId;
    private final List<OrderLine> orderLines;
    private OrderStatus status;
    private Instant orderDate;
    private BigDecimal totalAmount;
    
    public Order(OrderId id, CustomerId customerId) {
        super(id, "order_management");
        this.customerId = Objects.requireNonNull(customerId, "Customer ID cannot be null");
        this.orderLines = new ArrayList<>();
        this.status = OrderStatus.PENDING;
        this.orderDate = Instant.now();
        this.totalAmount = BigDecimal.ZERO;
        
        // Generate domain event
        addDomainEvent(new OrderCreatedEvent(id, customerId));
    }
    
    public void addOrderLine(ProductId productId, int quantity, BigDecimal unitPrice) {
        if (status != OrderStatus.PENDING) {
            throw new IllegalStateException("Cannot modify order that is not pending");
        }
        
        OrderLine orderLine = new OrderLine(productId, quantity, unitPrice);
        orderLines.add(orderLine);
        recalculateTotal();
        updateVersion();
        
        addDomainEvent(new OrderLineAddedEvent(getId(), productId, quantity, unitPrice));
    }
    
    public void removeOrderLine(ProductId productId) {
        if (status != OrderStatus.PENDING) {
            throw new IllegalStateException("Cannot modify order that is not pending");
        }
        
        boolean removed = orderLines.removeIf(line -> line.getProductId().equals(productId));
        if (removed) {
            recalculateTotal();
            updateVersion();
            addDomainEvent(new OrderLineRemovedEvent(getId(), productId));
        }
    }
    
    public void confirm() {
        if (status != OrderStatus.PENDING) {
            throw new IllegalStateException("Can only confirm pending orders");
        }
        
        if (orderLines.isEmpty()) {
            throw new IllegalStateException("Cannot confirm order with no order lines");
        }
        
        status = OrderStatus.CONFIRMED;
        updateVersion();
        
        addDomainEvent(new OrderConfirmedEvent(getId(), totalAmount));
    }
    
    public void cancel() {
        if (status == OrderStatus.SHIPPED || status == OrderStatus.DELIVERED) {
            throw new IllegalStateException("Cannot cancel shipped or delivered orders");
        }
        
        status = OrderStatus.CANCELLED;
        updateVersion();
        
        addDomainEvent(new OrderCancelledEvent(getId()));
    }
    
    private void recalculateTotal() {
        totalAmount = orderLines.stream()
            .map(OrderLine::getLineTotal)
            .reduce(BigDecimal.ZERO, BigDecimal::add);
    }
    
    // Getters
    public CustomerId getCustomerId() {
        return customerId;
    }
    
    public List<OrderLine> getOrderLines() {
        return Collections.unmodifiableList(orderLines);
    }
    
    public OrderStatus getStatus() {
        return status;
    }
    
    public Instant getOrderDate() {
        return orderDate;
    }
    
    public BigDecimal getTotalAmount() {
        return totalAmount;
    }
    
    @Override
    public DomainBoundaries getDomainBoundaries() {
        return DomainBoundaries.builder()
            .context("order_management")
            .aggregateType("Order")
            .capability("order_creation")
            .capability("order_modification")
            .capability("order_confirmation")
            .constraint("no_modification_after_confirmation")
            .constraint("minimum_one_order_line")
            .build();
    }
    
    @Override
    public AggregateBoundaries getAggregateBoundaries() {
        return AggregateBoundaries.builder()
            .aggregateType("Order")
            .entityType("Order")
            .entityType("OrderLine")
            .invariant("order_must_have_customer")
            .invariant("confirmed_order_must_have_lines")
            .invariant("total_amount_must_match_lines")
            .maxSize(50) // Maximum 50 order lines
            .enforceConsistency(true)
            .build();
    }
    
    @Override
    protected ValidationResult validateAggregateRules() {
        ValidationResult result = new ValidationResult();
        
        // Validate customer ID
        if (customerId == null) {
            result.addError("Order must have a customer");
        }
        
        // Validate order lines for confirmed orders
        if (status == OrderStatus.CONFIRMED && orderLines.isEmpty()) {
            result.addError("Confirmed order must have at least one order line");
        }
        
        // Validate total amount calculation
        BigDecimal calculatedTotal = orderLines.stream()
            .map(OrderLine::getLineTotal)
            .reduce(BigDecimal.ZERO, BigDecimal::add);
        
        if (totalAmount.compareTo(calculatedTotal) != 0) {
            result.addError("Total amount does not match sum of order lines");
        }
        
        // Validate aggregate size
        if (orderLines.size() > 50) {
            result.addError("Order cannot have more than 50 order lines");
        }
        
        return result;
    }
    
    @Override
    public ValidationResult validateDomainInvariants() {
        ValidationResult result = super.validateDomainInvariants();
        
        // Additional entity-level validation
        if (orderDate == null) {
            result.addError("Order must have an order date");
        }
        
        if (totalAmount == null || totalAmount.compareTo(BigDecimal.ZERO) < 0) {
            result.addError("Order total amount cannot be negative");
        }
        
        return result;
    }
}