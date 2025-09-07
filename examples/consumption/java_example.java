package com.example.consumption;

import com.beastmode.rmddd.core.*;
import com.beastmode.rmddd.domain.*;
import com.beastmode.rmddd.utilities.ValidationResult;
import com.beastmode.rmddd.examples.ecommerce.*;

import java.util.concurrent.CompletableFuture;
import java.util.UUID;

/**
 * Example: How to consume the RM-DDD implementation in Java
 * Demonstrates practical usage of the systematic patterns we built.
 */
public class JavaConsumptionExample {
    
    // Example 1: Create a new domain using RM-DDD patterns
    public static class BookingId extends ValueObject {
        private final String value;
        
        public BookingId(String value) {
            this.value = value;
            validateOnConstruction();
        }
        
        public String getValue() {
            return value;
        }
        
        @Override
        public ValidationResult validate() {
            ValidationResult result = new ValidationResult();
            if (value == null || value.length() < 5) {
                result.addError("Booking ID must be at least 5 characters");
            }
            return result;
        }
        
        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (!(o instanceof BookingId)) return false;
            BookingId bookingId = (BookingId) o;
            return value.equals(bookingId.value);
        }
        
        @Override
        public int hashCode() {
            return value.hashCode();
        }
    }
    
    public static class Booking extends AggregateRoot<BookingId> {
        private final CustomerId customerId;
        private String status;
        private final java.util.List<BookingItem> items;
        
        public Booking(BookingId id, CustomerId customerId) {
            super(id, "booking_management");
            this.customerId = customerId;
            this.status = "pending";
            this.items = new java.util.ArrayList<>();
        }
        
        public void addItem(String itemId, int quantity) {
            if (!"pending".equals(status)) {
                throw new IllegalStateException("Cannot modify confirmed booking");
            }
            
            items.add(new BookingItem(itemId, quantity));
            updateVersion();
            
            // Generate domain event (systematic pattern)
            addDomainEvent(new BookingItemAddedEvent(getId(), itemId, quantity));
        }
        
        @Override
        public DomainBoundaries getDomainBoundaries() {
            return DomainBoundaries.builder()
                .withContext("booking_management")
                .withCapability("booking_creation")
                .withCapability("item_management")
                .withConstraint("no_modification_after_confirmation")
                .build();
        }
        
        @Override
        protected ValidationResult validateAggregateRules() {
            ValidationResult result = new ValidationResult();
            if (customerId == null) {
                result.addError("Booking must have a customer");
            }
            return result;
        }
        
        @Override
        public AggregateBoundaries getAggregateBoundaries() {
            return AggregateBoundaries.builder()
                .withAggregateType("Booking")
                .withEntityType("Booking")
                .withEntityType("BookingItem")
                .build();
        }
        
        // Getters
        public CustomerId getCustomerId() { return customerId; }
        public String getStatus() { return status; }
        public java.util.List<BookingItem> getItems() { return new java.util.ArrayList<>(items); }
    }
    
    public static class BookingItem {
        private final String itemId;
        private final int quantity;
        
        public BookingItem(String itemId, int quantity) {
            this.itemId = itemId;
            this.quantity = quantity;
        }
        
        public String getItemId() { return itemId; }
        public int getQuantity() { return quantity; }
    }
    
    public static class BookingItemAddedEvent extends DomainEvent {
        private final String itemId;
        private final int quantity;
        
        public BookingItemAddedEvent(BookingId bookingId, String itemId, int quantity) {
            super(bookingId);
            this.itemId = itemId;
            this.quantity = quantity;
        }
        
        @Override
        public java.util.Map<String, Object> getEventData() {
            return java.util.Map.of(
                "booking_id", getAggregateId().toString(),
                "item_id", itemId,
                "quantity", quantity
            );
        }
    }
    
    public static class BookingService extends DomainService {
        
        public BookingService() {
            super("booking_processor", "booking_management");
        }
        
        public CompletableFuture<ValidationResult> processBooking(Booking booking) {
            return CompletableFuture.supplyAsync(() -> {
                // Validate using systematic patterns
                ValidationResult validation = booking.validateDomainInvariants();
                if (!validation.isValid()) {
                    return validation;
                }
                
                // Apply business rules systematically
                booking.status = "confirmed";
                booking.updateVersion();
                
                return ValidationResult.success();
            });
        }
        
        @Override
        public DomainBoundaries getDomainBoundaries() {
            return DomainBoundaries.builder()
                .withContext("booking_management")
                .withAggregateType("BookingService")
                .build();
        }
    }
    
    // Example 2: Use existing e-commerce patterns
    public static Order demonstrateECommerceUsage() {
        // Create systematic domain objects
        OrderId orderId = OrderId.generate();
        CustomerId customerId = CustomerId.generate();
        ProductId productId = ProductId.generate();
        
        // Create order using systematic patterns
        Order order = new Order(orderId, customerId);
        
        // Add items systematically
        order.addOrderLine(productId, 2, java.math.BigDecimal.valueOf(25.99));
        
        // Validate using systematic validation
        ValidationResult validation = order.validateDomainInvariants();
        System.out.println("Order validation: " + validation.isValid());
        
        // Confirm order (business logic)
        order.confirm();
        
        // Check domain events (systematic event handling)
        var events = order.getDomainEvents();
        System.out.println("Generated " + events.size() + " domain events");
        
        return order;
    }
    
    // Example 3: Health monitoring and RM compliance
    public static CompletableFuture<ModuleHealth> demonstrateHealthMonitoring() {
        BookingService bookingService = new BookingService();
        
        return bookingService.getModuleStatusAsync().thenApply(health -> {
            System.out.println("Service health: " + health.getStatus());
            System.out.println("Capabilities: " + health.getCapabilities());
            
            // Check RM compliance
            bookingService.isHealthyAsync().thenAccept(isHealthy -> 
                System.out.println("RM compliance: " + isHealthy)
            );
            
            return health;
        });
    }
    
    public static void main(String[] args) {
        System.out.println("=== RM-DDD Java Consumption Example ===");
        
        try {
            // Demonstrate systematic domain creation
            BookingId bookingId = new BookingId("BOOK-12345");
            CustomerId customerId = CustomerId.generate();
            Booking booking = new Booking(bookingId, customerId);
            booking.addItem("ITEM-001", 2);
            
            System.out.println("Created booking: " + booking.getId().getValue());
            System.out.println("Domain context: " + booking.getDomainContext());
            
            // Demonstrate e-commerce usage
            Order order = demonstrateECommerceUsage();
            System.out.println("Created order: " + order.getId());
            
            // Demonstrate health monitoring
            ModuleHealth health = demonstrateHealthMonitoring().get();
            System.out.println("System health: " + health);
            
            System.out.println("\n✅ RM-DDD systematic patterns working correctly!");
            
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}