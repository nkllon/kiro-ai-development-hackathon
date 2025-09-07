# RM-DDD C# Interfaces and Implementations

This directory contains C# interfaces and base classes that mirror the Python RM-DDD SDK patterns, following .NET conventions and best practices.

## Overview

The C# stubs provide:
- Interface definitions for ReflectiveModule and DDD patterns following .NET conventions
- Base classes for Entity, ValueObject, and AggregateRoot with proper .NET idioms
- Repository patterns with Entity Framework integration hints
- Domain event system with async/await support

## Package Structure

```
BeastMode.RmDdd/
├── Core/                       # Core RM functionality
│   ├── IReflectiveModule.cs
│   ├── IDomainReflectiveModule.cs
│   ├── ModuleHealth.cs
│   └── HealthMonitor.cs
├── Domain/                     # DDD pattern implementations
│   ├── Entity.cs
│   ├── ValueObject.cs
│   ├── AggregateRoot.cs
│   ├── DomainService.cs
│   ├── IRepository.cs
│   └── DomainEvent.cs
├── Utilities/                  # Convenience utilities
│   ├── DomainValidator.cs
│   ├── ValidationResult.cs
│   └── ComplexityMonitor.cs
└── Examples/                   # Reference implementations
    ├── ECommerce/
    ├── Banking/
    └── Inventory/
```

## Usage

### Basic Entity Example

```csharp
[DomainEntity(Context = "OrderManagement")]
public class Order : AggregateRoot<OrderId>
{
    private readonly List<OrderLine> _orderLines;
    
    public CustomerId CustomerId { get; private set; }
    public IReadOnlyList<OrderLine> OrderLines => _orderLines.AsReadOnly();
    public OrderStatus Status { get; private set; }
    
    public Order(OrderId id, CustomerId customerId) : base(id, "OrderManagement")
    {
        CustomerId = customerId ?? throw new ArgumentNullException(nameof(customerId));
        _orderLines = new List<OrderLine>();
        Status = OrderStatus.Pending;
        
        AddDomainEvent(new OrderCreatedEvent(id, customerId));
    }
    
    public override DomainBoundaries GetDomainBoundaries()
    {
        return DomainBoundaries.Builder()
            .WithContext("OrderManagement")
            .WithAggregateType("Order")
            .Build();
    }
    
    public override ValidationResult ValidateDomainInvariants()
    {
        var result = new ValidationResult();
        
        if (!_orderLines.Any())
        {
            result.AddError("Order must have at least one order line");
        }
        
        return result;
    }
}
```

### Repository Example

```csharp
public interface IOrderRepository : IRepository<Order, OrderId>
{
    Task<IEnumerable<Order>> FindByCustomerIdAsync(CustomerId customerId, CancellationToken cancellationToken = default);
    
    Task<IEnumerable<Order>> FindByStatusAsync(OrderStatus status, CancellationToken cancellationToken = default);
    
    Task<IEnumerable<Order>> FindByDateRangeAsync(DateTime startDate, DateTime endDate, CancellationToken cancellationToken = default);
}

public class OrderRepository : RepositoryRM<Order, OrderId>, IOrderRepository
{
    private readonly DbContext _context;
    
    public OrderRepository(DbContext context) : base("OrderManagement", "Order")
    {
        _context = context ?? throw new ArgumentNullException(nameof(context));
    }
    
    public override async Task<Order?> GetByIdAsync(OrderId entityId, CancellationToken cancellationToken = default)
    {
        return await _context.Set<Order>()
            .Include(o => o.OrderLines)
            .FirstOrDefaultAsync(o => o.Id == entityId, cancellationToken);
    }
    
    protected override async Task PerformHealthCheckAsync(CancellationToken cancellationToken = default)
    {
        // Database connectivity check
        await _context.Database.CanConnectAsync(cancellationToken);
    }
}
```

## Integration with ASP.NET Core

The C# stubs are designed to work seamlessly with ASP.NET Core and Entity Framework:

```csharp
// Startup.cs or Program.cs
public void ConfigureServices(IServiceCollection services)
{
    services.AddRmDdd(options =>
    {
        options.DefaultDomainContext = "OrderManagement";
        options.EnableHealthMonitoring = true;
    });
    
    services.AddScoped<IDomainEventPublisher, DomainEventPublisher>();
    services.AddScoped<IOrderRepository, OrderRepository>();
}
```

## Async/Await Support

All operations support async/await patterns:

```csharp
// Async domain service example
public class OrderProcessingService : DomainService
{
    private readonly IOrderRepository _orderRepository;
    
    public OrderProcessingService(IOrderRepository orderRepository) 
        : base("OrderProcessing", "OrderManagement")
    {
        _orderRepository = orderRepository;
    }
    
    public async Task<ValidationResult> ProcessOrderAsync(OrderId orderId, CancellationToken cancellationToken = default)
    {
        var order = await _orderRepository.GetByIdAsync(orderId, cancellationToken);
        
        if (order == null)
        {
            return ValidationResult.Failure("Order not found");
        }
        
        // Process order logic
        order.Confirm();
        
        await _orderRepository.SaveAsync(order, cancellationToken);
        
        return ValidationResult.Success();
    }
}
```

## Entity Framework Integration

Built-in support for Entity Framework Core:

```csharp
public class OrderManagementDbContext : DbContext
{
    public DbSet<Order> Orders { get; set; }
    public DbSet<Customer> Customers { get; set; }
    
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        // Configure Order aggregate
        modelBuilder.Entity<Order>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Id)
                .HasConversion(id => id.Value, value => new OrderId(value));
            
            entity.OwnsMany(e => e.OrderLines, orderLine =>
            {
                orderLine.Property(ol => ol.ProductId)
                    .HasConversion(id => id.Value, value => new ProductId(value));
            });
        });
        
        base.OnModelCreating(modelBuilder);
    }
}
```

## Requirements Mapping

This implementation addresses the following requirements:
- **Requirement 10.2**: C# interfaces and implementations following .NET conventions
- **Requirement 10.4**: Multi-language consistency with proper C# idioms
- **Requirement 10.5**: Cross-platform domain model consistency
- **Entity Framework Integration**: Seamless integration with EF Core
- **Async/Await Support**: Full async support throughout the framework
- **ASP.NET Core Integration**: Built-in dependency injection and configuration support