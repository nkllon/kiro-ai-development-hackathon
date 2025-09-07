using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using BeastMode.RmDdd.Core;
using BeastMode.RmDdd.Domain;
using BeastMode.RmDdd.Utilities;
using BeastMode.RmDdd.Examples.ECommerce;

namespace ConsumptionExample
{
    /// <summary>
    /// Example: How to consume the RM-DDD implementation in C#
    /// Demonstrates practical usage of the systematic patterns we built.
    /// </summary>
    class Program
    {
        // Example 1: Create a new domain using RM-DDD patterns
        public class BookingId : ValueObject
        {
            public string Value { get; }
            
            public BookingId(string value)
            {
                Value = value;
                ValidateOnConstruction();
            }
            
            public override ValidationResult Validate()
            {
                var result = new ValidationResult();
                if (string.IsNullOrEmpty(Value) || Value.Length < 5)
                {
                    result.AddError("Booking ID must be at least 5 characters");
                }
                return result;
            }
            
            protected override IEnumerable<object?> GetEqualityComponents()
            {
                yield return Value;
            }
        }
        
        public class Booking : AggregateRoot<BookingId>
        {
            private readonly List<BookingItem> _items = new();
            
            public CustomerId CustomerId { get; }
            public string Status { get; private set; }
            public IReadOnlyList<BookingItem> Items => _items.AsReadOnly();
            
            public Booking(BookingId id, CustomerId customerId) : base(id, "booking_management")
            {
                CustomerId = customerId;
                Status = "pending";
            }
            
            public void AddItem(string itemId, int quantity)
            {
                if (Status != "pending")
                {
                    throw new InvalidOperationException("Cannot modify confirmed booking");
                }
                
                _items.Add(new BookingItem(itemId, quantity));
                UpdateVersion();
                
                // Generate domain event (systematic pattern)
                AddDomainEvent(new BookingItemAddedEvent(Id, itemId, quantity));
            }
            
            public override DomainBoundaries GetDomainBoundaries()
            {
                return DomainBoundaries.Builder()
                    .WithContext("booking_management")
                    .WithCapability("booking_creation")
                    .WithCapability("item_management")
                    .WithConstraint("no_modification_after_confirmation")
                    .Build();
            }
            
            protected override ValidationResult ValidateAggregateRules()
            {
                var result = new ValidationResult();
                if (CustomerId == null)
                {
                    result.AddError("Booking must have a customer");
                }
                return result;
            }
            
            public override AggregateBoundaries GetAggregateBoundaries()
            {
                return AggregateBoundaries.Builder()
                    .WithAggregateType("Booking")
                    .WithEntityType("Booking")
                    .WithEntityType("BookingItem")
                    .Build();
            }
        }
        
        public class BookingItem
        {
            public string ItemId { get; }
            public int Quantity { get; }
            
            public BookingItem(string itemId, int quantity)
            {
                ItemId = itemId;
                Quantity = quantity;
            }
        }
        
        public class BookingItemAddedEvent : DomainEvent
        {
            public string ItemId { get; }
            public int Quantity { get; }
            
            public BookingItemAddedEvent(BookingId bookingId, string itemId, int quantity) 
                : base(bookingId)
            {
                ItemId = itemId;
                Quantity = quantity;
            }
            
            public override IDictionary<string, object> GetEventData()
            {
                return new Dictionary<string, object>
                {
                    ["booking_id"] = AggregateId.ToString(),
                    ["item_id"] = ItemId,
                    ["quantity"] = Quantity
                };
            }
        }
        
        public class BookingService : DomainService
        {
            public BookingService() : base("booking_processor", "booking_management")
            {
            }
            
            public async Task<ValidationResult> ProcessBookingAsync(Booking booking)
            {
                // Validate using systematic patterns
                var validation = booking.ValidateDomainInvariants();
                if (!validation.IsValid)
                {
                    return validation;
                }
                
                // Apply business rules systematically
                typeof(Booking).GetProperty("Status")!.SetValue(booking, "confirmed");
                booking.UpdateVersion();
                
                return ValidationResult.Success();
            }
            
            public override DomainBoundaries GetDomainBoundaries()
            {
                return DomainBoundaries.Builder()
                    .WithContext("booking_management")
                    .WithAggregateType("BookingService")
                    .Build();
            }
        }
        
        // Example 2: Use existing e-commerce patterns
        static Order DemonstrateECommerceUsage()
        {
            // Create systematic domain objects
            var orderId = OrderId.Generate();
            var customerId = CustomerId.Generate();
            var productId = ProductId.Generate();
            
            // Create order using systematic patterns
            var order = new Order(orderId, customerId);
            
            // Add items systematically
            order.AddOrderLine(productId, 2, 25.99m);
            
            // Validate using systematic validation
            var validation = order.ValidateDomainInvariants();
            Console.WriteLine($"Order validation: {validation.IsValid}");
            
            // Confirm order (business logic)
            order.Confirm();
            
            // Check domain events (systematic event handling)
            var events = order.GetDomainEvents();
            Console.WriteLine($"Generated {events.Count} domain events");
            
            return order;
        }
        
        // Example 3: Health monitoring and RM compliance
        static async Task<ModuleHealth> DemonstrateHealthMonitoringAsync()
        {
            var bookingService = new BookingService();
            
            // Get systematic health information
            var health = await bookingService.GetModuleStatusAsync();
            Console.WriteLine($"Service health: {health.Status}");
            Console.WriteLine($"Capabilities: {health.Capabilities.Count}");
            
            // Check RM compliance
            var isHealthy = await bookingService.IsHealthyAsync();
            Console.WriteLine($"RM compliance: {isHealthy}");
            
            return health;
        }
        
        static async Task Main(string[] args)
        {
            Console.WriteLine("=== RM-DDD C# Consumption Example ===");
            
            try
            {
                // Demonstrate systematic domain creation
                var bookingId = new BookingId("BOOK-12345");
                var customerId = CustomerId.Generate();
                var booking = new Booking(bookingId, customerId);
                booking.AddItem("ITEM-001", 2);
                
                Console.WriteLine($"Created booking: {booking.Id.Value}");
                Console.WriteLine($"Domain context: {booking.DomainContext}");
                
                // Demonstrate e-commerce usage
                var order = DemonstrateECommerceUsage();
                Console.WriteLine($"Created order: {order.Id}");
                
                // Demonstrate health monitoring
                var health = await DemonstrateHealthMonitoringAsync();
                Console.WriteLine($"System health: {health}");
                
                Console.WriteLine("\n✅ RM-DDD systematic patterns working correctly!");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
                Console.WriteLine(ex.StackTrace);
            }
        }
    }
}