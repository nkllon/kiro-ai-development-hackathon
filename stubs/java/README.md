# RM-DDD Java Interfaces and Stubs

This directory contains Java interfaces and base classes that mirror the Python RM-DDD SDK patterns, following Java conventions and best practices.

## Overview

The Java stubs provide:
- Interface definitions for ReflectiveModule and DDD patterns
- Base classes for Entity, ValueObject, and AggregateRoot
- Repository interfaces and domain service abstractions
- Domain event system interfaces and implementations

## Package Structure

```
com.beastmode.rmddd/
├── core/                       # Core RM functionality
│   ├── ReflectiveModule.java
│   ├── DomainReflectiveModule.java
│   ├── ModuleHealth.java
│   └── HealthMonitor.java
├── domain/                     # DDD pattern implementations
│   ├── Entity.java
│   ├── ValueObject.java
│   ├── AggregateRoot.java
│   ├── DomainService.java
│   ├── Repository.java
│   └── DomainEvent.java
├── utilities/                  # Convenience utilities
│   ├── DomainValidator.java
│   ├── ValidationResult.java
│   └── ComplexityMonitor.java
└── examples/                   # Reference implementations
    ├── ecommerce/
    ├── banking/
    └── inventory/
```

## Usage

### Basic Entity Example

```java
@DomainEntity(context = "order_management")
public class Order extends AggregateRoot<OrderId> {
    
    private CustomerId customerId;
    private List<OrderLine> orderLines;
    private OrderStatus status;
    
    public Order(OrderId id, CustomerId customerId) {
        super(id, "order_management");
        this.customerId = customerId;
        this.orderLines = new ArrayList<>();
        this.status = OrderStatus.PENDING;
    }
    
    @Override
    public DomainBoundaries getDomainBoundaries() {
        return DomainBoundaries.builder()
            .context("order_management")
            .aggregateType("Order")
            .build();
    }
    
    @Override
    public ValidationResult validateDomainInvariants() {
        ValidationResult result = new ValidationResult();
        
        if (orderLines.isEmpty()) {
            result.addError("Order must have at least one order line");
        }
        
        return result;
    }
}
```

### Repository Example

```java
public interface OrderRepository extends Repository<Order, OrderId> {
    
    CompletableFuture<List<Order>> findByCustomerId(CustomerId customerId);
    
    CompletableFuture<List<Order>> findByStatus(OrderStatus status);
    
    CompletableFuture<List<Order>> findByDateRange(LocalDate startDate, LocalDate endDate);
}

@Component
public class OrderRepositoryImpl extends RepositoryRM<Order, OrderId> 
    implements OrderRepository {
    
    public OrderRepositoryImpl() {
        super("order_management", "Order");
    }
    
    @Override
    public CompletableFuture<Optional<Order>> getById(OrderId entityId) {
        // Implementation using JPA, MongoDB, etc.
        return CompletableFuture.completedFuture(Optional.empty());
    }
    
    @Override
    protected CompletableFuture<Void> performHealthCheck() {
        // Database connectivity check
        return CompletableFuture.completedFuture(null);
    }
}
```

## Integration with Spring Boot

The Java stubs are designed to work seamlessly with Spring Boot and other Java frameworks:

```java
@Configuration
@EnableRMDDD
public class RMDDDConfiguration {
    
    @Bean
    public DomainEventPublisher domainEventPublisher() {
        return new DomainEventPublisher("order_management");
    }
    
    @Bean
    public HealthMonitor healthMonitor() {
        return new HealthMonitor();
    }
}
```

## Ontology Validation & SHACL Integration

The Java stubs include comprehensive ontology validation capabilities:

### SHACL Validation
```java
// Validate RDF data against SHACL shapes
ValidationResult result = ValidateShacl.validateFile(
    new File("examples/usps-sun.ttl"),
    new File("ontology/shacl/core.shacl.ttl"),
    new File("ontology/shacl/governance.shacl.ttl")
);

if (result.isValid()) {
    System.out.println("Validation passed ✅");
} else {
    result.getErrors().forEach(System.err::println);
}
```

### SPARQL Queries
```java
// Query personal ontology for alternative labels
Model model = RDFDataMgr.loadModel("examples/personal-ontology.ttl");
ResultSet results = QueryExample.findAlternativeLabels(model, "Accounts Payable Module");

results.forEachRemaining(solution -> 
    System.out.println("Alternative: " + solution.getLiteral("altLabel").getString())
);
```

### Protégé Integration
```java
// Set up Protégé-compatible ontology environment
ProtegeIntegration.setupProtegeEnvironment(new File("."));

// Validate ontology for Protégé compatibility
ValidationResult compatibility = ProtegeIntegration.validateProtegeCompatibility(
    new File("ontology/beastmaster-core.ttl")
);
```

## Quick Start Commands

Use the validation script for common tasks:

```bash
# Run complete validation suite
./validate-ontology.sh validate-all

# Set up Protégé environment
./validate-ontology.sh setup-protege

# Run SHACL validation only
./validate-ontology.sh validate-shacl

# Check TTL syntax
./validate-ontology.sh check-syntax
```

## Maven Profiles

### Standard Testing
```bash
mvn test  # Run all ontology validation tests
```

### SHACL Validation Profile
```bash
mvn test -P ontology-validation  # Run with SHACL validation
```

### Protégé Setup Profile
```bash
mvn generate-resources -P protege-setup  # Set up Protégé environment
```

## CI/CD Integration

The test suite is designed for continuous integration:

```yaml
# Example GitHub Actions workflow
- name: Validate Ontologies
  run: |
    cd stubs/java
    mvn test
    ./validate-ontology.sh validate-all
```

## Protégé Workflow

1. **Setup**: Run `./validate-ontology.sh setup-protege`
2. **Open**: Load `ontology/beastmaster-profile.ttl` in Protégé
3. **Edit**: Make ontology changes with reasoning enabled
4. **Validate**: Run `mvn test` to ensure SHACL compliance
5. **Commit**: Push changes after validation passes

## Requirements Mapping

This implementation addresses the following requirements:
- **Requirement 10.1**: Java interfaces and stubs that mirror Python SDK patterns
- **Requirement 10.4**: Multi-language consistency with proper Java idioms  
- **Requirement 10.5**: Cross-platform domain model consistency
- **SHACL Integration**: Complete RDF4J-based validation framework
- **SPARQL Support**: Apache Jena integration for semantic queries
- **Protégé Compatibility**: Ontology preparation and validation tools