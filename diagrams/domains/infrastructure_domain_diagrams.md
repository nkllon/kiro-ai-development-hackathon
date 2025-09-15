# Infrastructure Domain Architecture

**Total Classes**: 17

## Section 1

```mermaid
classDiagram
    class ChatDeepInfra {
        +_default_params()
        +_client_params()
        +completion_with_retry()
        +init_defaults()
        +validate_environment()
    }
    class ChatDeepInfraException {
    }
    class DeepInfra {
        +validate_environment()
        +_identifying_params()
        +_llm_type()
        +_url()
        +_headers()
    }
    class DeepInfraEmbeddings {
        +validate_environment()
        +_identifying_params()
        +_embed()
        +embed_documents()
        +embed_query()
    }
    class InfrastructureAssessment {
    }
    class InfrastructureComponent {
    }
    class InfrastructureIntegrationManager {
        +__init__()
        +get_info()
    }
    class InfrastructureIntegrationManagerServices {
        +__init__()
        +get_info()
    }
```

## Section 2

```mermaid
classDiagram
    class InfrastructureIntegrationManagerServicesCore {
        +__init__()
        +get_info()
    }
    class InfrastructureIntegrationManagerServicesServices {
        +__init__()
        +get_info()
    }
    class InfrastructureIntegrationManagerServicesServicesCore {
        +__init__()
        +get_info()
    }
    class InfrastructureIssue {
    }
    class InfrastructureService {
        +__init__()
        +record_external_call()
        +get_service_capabilities()
    }
    class ProductionInfrastructureModel {
        +__init__()
        +get_info()
    }
    class ProductionInfrastructureModelCore {
        +__init__()
        +get_info()
    }
    class ProductionInfrastructureModelModels {
        +__init__()
        +get_info()
    }
```

## Section 3

```mermaid
classDiagram
    class SimplifiedInfrastructureModel {
        +__init__()
        +get_module_status()
        +_get_primary_responsibility()
        +is_healthy()
        +get_health_indicators()
    }
```

## All Classes in Domain

- `ChatDeepInfra`
- `ChatDeepInfraException`
- `DeepInfra`
- `DeepInfraEmbeddings`
- `InfrastructureAssessment`
- `InfrastructureComponent`
- `InfrastructureIntegrationManager`
- `InfrastructureIntegrationManagerServices`
- `InfrastructureIntegrationManagerServicesCore`
- `InfrastructureIntegrationManagerServicesServices`
- `InfrastructureIntegrationManagerServicesServicesCore`
- `InfrastructureIssue`
- `InfrastructureService`
- `ProductionInfrastructureModel`
- `ProductionInfrastructureModelCore`
- `ProductionInfrastructureModelModels`
- `SimplifiedInfrastructureModel`
