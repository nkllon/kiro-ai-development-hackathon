# GKE Domain Architecture

**Total Classes**: 50

## Section 1

```mermaid
classDiagram
    class GKEConfig {
    }
    class GKEImpactReport {
    }
    class GKEIntegrationGuide {
    }
    class GKEPlatformOrchestrator {
        +__init__()
        +deploy_for_scale()
        +auto_scale_agents()
        +monitor_cloud_costs()
        +_configure_auto_scaling()
    }
    class GKEServiceConsumer {
        +__init__()
        +get_module_status()
        +is_healthy()
        +get_health_indicators()
        +_get_primary_responsibility()
    }
    class GKEServiceImpactMeasurer {
        +__init__()
        +get_module_status()
        +is_healthy()
        +get_health_indicators()
        +_get_primary_responsibility()
    }
    class GKEServiceInterface {
        +__init__()
        +get_module_status()
        +is_healthy()
        +get_health_indicators()
        +_get_primary_responsibility()
    }
    class GKEServiceMetrics {
    }
```

## Section 2

```mermaid
classDiagram
    class GKEServiceProvider {
        +__init__()
        +get_module_status()
        +is_healthy()
        +get_health_indicators()
        +_get_primary_responsibility()
    }
    class GKEServiceProviderSimple {
        +__init__()
        +get_module_status()
        +is_healthy()
        +get_health_indicators()
        +_get_primary_responsibility()
    }
    class GKEServiceRequest {
    }
    class GKEServiceResponse {
    }
    class GKETeamMetrics {
    }
    class GKETeamProfile {
    }
    class GkeServiceConsumerCore {
        +__init__()
        +get_info()
    }
    class GkeServiceConsumerCoreCore {
        +__init__()
        +get_info()
    }
```

## Section 3

```mermaid
classDiagram
    class GkeServiceConsumerServices {
        +__init__()
        +get_info()
    }
    class GkeServiceConsumerServicesCore {
        +__init__()
        +get_info()
    }
    class GkeServiceConsumerServicesCoreCore {
        +__init__()
        +get_info()
    }
    class GkeServiceConsumerServicesServices {
        +__init__()
        +get_info()
    }
    class GkeServiceConsumerServicesServicesCore {
        +__init__()
        +get_info()
    }
    class GkeServiceConsumerServicesServicesUtils {
        +__init__()
        +get_info()
    }
    class GkeServiceConsumerServicesServicesValidation {
        +__init__()
        +get_info()
    }
    class GkeServiceConsumerServicesUtils {
        +__init__()
        +get_info()
    }
```

## Section 4

```mermaid
classDiagram
    class GkeServiceConsumerServicesValidation {
        +__init__()
        +get_info()
    }
    class GkeServiceConsumerUtils {
        +__init__()
        +get_info()
    }
    class GkeServiceConsumerValidation {
        +__init__()
        +get_info()
    }
    class GkeServiceImpactMeasurer {
        +__init__()
        +get_info()
    }
    class GkeServiceInterface {
        +__init__()
        +get_info()
    }
    class GkeServiceInterfaceProcessing {
        +__init__()
        +get_info()
    }
    class GkeServiceInterfaceUtils {
        +__init__()
        +get_info()
    }
    class GkeServiceInterfaceValidation {
        +__init__()
        +get_info()
    }
```

## Section 5

```mermaid
classDiagram
    class GkeServiceProviderCore {
        +__init__()
        +get_info()
    }
    class GkeServiceProviderCoreCore {
        +__init__()
        +get_info()
    }
    class GkeServiceProviderServices {
        +__init__()
        +get_info()
    }
    class GkeServiceProviderServicesCore {
        +__init__()
        +get_info()
    }
    class GkeServiceProviderServicesCoreCore {
        +__init__()
        +get_info()
    }
    class GkeServiceProviderServicesServices {
        +__init__()
        +get_info()
    }
    class GkeServiceProviderServicesServicesCore {
        +__init__()
        +get_info()
    }
    class GkeServiceProviderServicesServicesUtils {
        +__init__()
        +get_info()
    }
```

## Section 6

```mermaid
classDiagram
    class GkeServiceProviderServicesServicesValidation {
        +__init__()
        +get_info()
    }
    class GkeServiceProviderServicesUtils {
        +__init__()
        +get_info()
    }
    class GkeServiceProviderServicesValidation {
        +__init__()
        +get_info()
    }
    class GkeServiceProviderSimple {
        +__init__()
        +get_info()
    }
    class GkeServiceProviderSimpleUtils {
        +__init__()
        +get_info()
    }
    class GkeServiceProviderUtils {
        +__init__()
        +get_info()
    }
    class GkeServiceProviderValidation {
        +__init__()
        +get_info()
    }
    class HasGettableStringKeys {
        +keys()
        +__getitem__()
    }
```

## Section 7

```mermaid
classDiagram
    class ROMappingKeysValuesView {
    }
    class _ReturnsStringKey {
        +_implicit_coercions()
        +_literal_coercion()
    }
```

## All Classes in Domain

- `GKEConfig`
- `GKEImpactReport`
- `GKEIntegrationGuide`
- `GKEPlatformOrchestrator`
- `GKEServiceConsumer`
- `GKEServiceImpactMeasurer`
- `GKEServiceInterface`
- `GKEServiceMetrics`
- `GKEServiceProvider`
- `GKEServiceProviderSimple`
- `GKEServiceRequest`
- `GKEServiceResponse`
- `GKETeamMetrics`
- `GKETeamProfile`
- `GkeServiceConsumerCore`
- `GkeServiceConsumerCoreCore`
- `GkeServiceConsumerServices`
- `GkeServiceConsumerServicesCore`
- `GkeServiceConsumerServicesCoreCore`
- `GkeServiceConsumerServicesServices`
- `GkeServiceConsumerServicesServicesCore`
- `GkeServiceConsumerServicesServicesUtils`
- `GkeServiceConsumerServicesServicesValidation`
- `GkeServiceConsumerServicesUtils`
- `GkeServiceConsumerServicesValidation`
- `GkeServiceConsumerUtils`
- `GkeServiceConsumerValidation`
- `GkeServiceImpactMeasurer`
- `GkeServiceInterface`
- `GkeServiceInterfaceProcessing`
- `GkeServiceInterfaceUtils`
- `GkeServiceInterfaceValidation`
- `GkeServiceProviderCore`
- `GkeServiceProviderCoreCore`
- `GkeServiceProviderServices`
- `GkeServiceProviderServicesCore`
- `GkeServiceProviderServicesCoreCore`
- `GkeServiceProviderServicesServices`
- `GkeServiceProviderServicesServicesCore`
- `GkeServiceProviderServicesServicesUtils`
- `GkeServiceProviderServicesServicesValidation`
- `GkeServiceProviderServicesUtils`
- `GkeServiceProviderServicesValidation`
- `GkeServiceProviderSimple`
- `GkeServiceProviderSimpleUtils`
- `GkeServiceProviderUtils`
- `GkeServiceProviderValidation`
- `HasGettableStringKeys`
- `ROMappingKeysValuesView`
- `_ReturnsStringKey`
