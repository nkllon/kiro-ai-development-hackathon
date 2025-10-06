# Domain Domain Architecture

**Total Classes**: 47

## Section 1

```mermaid
classDiagram
    class BoundedContext {
        +__init__()
        +add_aggregate()
        +get_aggregate()
        +add_domain_service()
        +get_domain_service()
    }
    class BoundedContextConfig {
        +validate_config()
    }
    class CreateDomainType {
    }
    class CrossDomainPattern {
        +to_dict()
    }
    class DOMAIN {
        +__init__()
        +__test_init__()
    }
    class Domain {
        +__init__()
        +canonical()
        +validation()
        +match_domain()
        +get_info()
    }
    class DomainAdapter {
        +__init__()
        +get_adaptation_metrics()
        +get_domain_boundaries()
        +validate_domain_invariants()
    }
    class DomainCache {
        +__init__()
        +get()
        +set()
        +delete()
        +clear()
    }
```

## Section 2

```mermaid
classDiagram
    class DomainCacheCore {
        +__init__()
        +get_info()
    }
    class DomainCacheCoreCore {
        +__init__()
        +get_info()
    }
    class DomainContextInitializer {
        +__init__()
        +initialize_bounded_context()
        +_setup_context_structure()
        +_create_entity_file()
        +_create_value_object_file()
    }
    class DomainDiagramGenerator {
        +__init__()
        +discover_domains()
        +generate_domain_diagrams()
        +_generate_domain_markdown()
        +_generate_mermaid_diagram()
    }
    class DomainDropper {
        +visit_DOMAIN()
    }
    class DomainEvent {
    }
    class DomainEventHandler {
        +__init__()
        +can_handle()
        +get_handler_metrics()
    }
    class DomainEventPublisher {
        +__init__()
        +subscribe()
        +subscribe_to_all()
        +unsubscribe()
        +get_subscription_info()
    }
```

## Section 3

```mermaid
classDiagram
    class DomainGenerator {
        +visit_DOMAIN()
    }
    class DomainIndex {
        +__init__()
        +build_index()
        +update_index()
        +search_index()
        +search_by_pattern()
    }
    class DomainIndexCore {
        +__init__()
        +get_module_info()
        +get_capabilities()
        +get_health_status()
        +graceful_degradation()
    }
    class DomainIndexCoreCore {
        +__init__()
        +get_info()
    }
    class DomainInfo {
    }
    class DomainInitializerCore {
        +__init__()
        +get_info()
    }
    class DomainInitializerCoreCore {
        +__init__()
        +get_info()
    }
    class DomainInitializerCoreCoreUtils {
        +__init__()
        +get_info()
    }
```

## Section 4

```mermaid
classDiagram
    class DomainInitializerCoreUtils {
        +__init__()
        +get_info()
    }
    class DomainInitializerUtils {
        +__init__()
        +get_info()
    }
    class DomainModel {
    }
    class DomainOperations {
        +__init__()
        +load_project_model()
        +list_domains()
        +list_domain_requirements()
        +_format_json_with_traceability()
    }
    class DomainQueryEngine {
        +__init__()
        +set_registry_manager()
        +_ensure_indexes_built()
        +_build_search_indexes()
        +natural_language_query()
    }
    class DomainReflectiveModule {
        +__init__()
        +get_domain_boundaries()
        +validate_domain_invariants()
        +_calculate_complexity_score()
        +get_domain_info()
    }
    class DomainService {
        +__init__()
        +execute_service()
        +get_service_info()
        +__str__()
        +__repr__()
    }
    class DomainSetupResult {
        +success()
    }
```

## Section 5

```mermaid
classDiagram
    class DomainSpecificCache {
        +__init__()
        +cache_domain()
        +get_domain()
        +cache_domain_collection()
        +get_domain_collection()
    }
    class DomainType {
    }
    class DomainVocabularyExpander {
        +__init__()
        +_initialize_base_vocabulary()
        +extract_terms_from_code()
        +_extract_terms_from_text()
        +build_term_relationships()
    }
    class DropDomainType {
    }
    class MaskDomain {
        +__init__()
        +canonical()
        +match_domain()
    }
    class ReflectedDomain {
    }
    class ReflectedDomainConstraint {
    }
    class SimpleDomainExpander {
        +__init__()
        +_initialize_base_vocabulary()
        +extract_terms_from_code()
        +_extract_terms_from_text()
        +build_term_relationships()
    }
```

## Section 6

```mermaid
classDiagram
    class UnixDomainSocketConnection {
        +__init__()
        +repr_pieces()
        +_host_error()
    }
    class _DomainCheckInterval {
        +__init__()
        +__call__()
    }
    class _DomainGreater {
        +__init__()
        +__call__()
    }
    class _DomainGreaterEqual {
        +__init__()
        +__call__()
    }
    class _DomainSafeDivide {
        +__init__()
        +__call__()
    }
    class _DomainTan {
        +__init__()
        +__call__()
    }
    class _DomainedBinaryOperation {
        +__init__()
        +__call__()
    }
```

## All Classes in Domain

- `BoundedContext`
- `BoundedContextConfig`
- `CreateDomainType`
- `CrossDomainPattern`
- `DOMAIN`
- `Domain`
- `DomainAdapter`
- `DomainCache`
- `DomainCacheCore`
- `DomainCacheCoreCore`
- `DomainContextInitializer`
- `DomainDiagramGenerator`
- `DomainDropper`
- `DomainEvent`
- `DomainEventHandler`
- `DomainEventPublisher`
- `DomainGenerator`
- `DomainIndex`
- `DomainIndexCore`
- `DomainIndexCoreCore`
- `DomainInfo`
- `DomainInitializerCore`
- `DomainInitializerCoreCore`
- `DomainInitializerCoreCoreUtils`
- `DomainInitializerCoreUtils`
- `DomainInitializerUtils`
- `DomainModel`
- `DomainOperations`
- `DomainQueryEngine`
- `DomainReflectiveModule`
- `DomainService`
- `DomainSetupResult`
- `DomainSpecificCache`
- `DomainType`
- `DomainVocabularyExpander`
- `DropDomainType`
- `MaskDomain`
- `ReflectedDomain`
- `ReflectedDomainConstraint`
- `SimpleDomainExpander`
- `UnixDomainSocketConnection`
- `_DomainCheckInterval`
- `_DomainGreater`
- `_DomainGreaterEqual`
- `_DomainSafeDivide`
- `_DomainTan`
- `_DomainedBinaryOperation`
