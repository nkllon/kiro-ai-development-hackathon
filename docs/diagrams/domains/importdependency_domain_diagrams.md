# ImportDependency Domain Architecture

**Total Classes**: 128

## Section 1

```mermaid
classDiagram
    class AbstractEntityRegistry {
        +__init__()
        +_truncate_recursive()
        +root_entity()
        +entity_path()
        +mapper()
    }
    class AgentRegistry {
        +__init__()
        +start_background_cleanup()
        +stop_background_cleanup()
        +register_agent_discovery()
        +register_agent_response()
    }
    class AgentRegistryCore {
        +__init__()
        +get_info()
    }
    class AgentRegistryCoreCore {
        +__init__()
        +get_info()
    }
    class BacklogDependencyManager {
        +__init__()
        +get_module_status()
        +is_healthy()
        +get_health_indicators()
        +_get_primary_responsibility()
    }
    class BeastModeRegistry {
        +__init__()
        +_init_database()
        +register_module()
        +discover_modules()
        +get_module()
    }
    class BeastModeRegistryIntegration {
        +__init__()
        +analyze_module_registry_compliance()
        +integrate_with_registry()
        +_enhance_registry_integration()
        +fix_single_module()
    }
    class CLIRegistry {
        +__new__()
        +get_instance()
        +register_cli()
        +get_cli()
        +get_all_clis()
    }
```

## Section 2

```mermaid
classDiagram
    class CachingEntityRegistry {
        +__init__()
        +pop()
        +_getitem()
    }
    class CantImport {
        +__init__()
    }
    class CircularDependencyDetector {
        +__init__()
        +_build_dependency_graph()
        +detect_cycles_dfs()
        +detect_cycles_tarjan()
        +analyze_cycle_impact()
    }
    class CircularDependencyError {
        +__init__()
        +__reduce__()
    }
    class CircularDependencyReport {
    }
    class ClsRegistryToken {
    }
    class ComprehensiveDependencyAnalyzer {
        +__init__()
        +set_registry_manager()
        +set_project_root()
        +perform_comprehensive_analysis()
        +_initialize_analyzers()
    }
    class DAGRegistry {
        +__init__()
        +register_module()
        +_would_create_cycle()
        +get_dependencies()
        +get_dependents()
    }
```

## Section 3

```mermaid
classDiagram
    class DependencyAnalyzer {
        +__init__()
        +validate_ecosystem_integrity()
        +_create_specification_nodes()
        +_create_ecosystem_dag()
    }
    class DependencyAnalyzerCore {
        +__init__()
        +get_info()
    }
    class DependencyAnalyzerCoreCore {
        +__init__()
        +get_info()
    }
    class DependencyAnalyzerValidation {
        +__init__()
        +get_info()
    }
    class DependencyChecker {
        +validate_core_dependencies()
        +validate_optional_dependencies()
        +generate_installation_commands()
        +print_validation_report()
    }
    class DependencyConflict {
    }
    class DependencyFinderVisitor {
        +__init__()
        +visit_Filter()
        +visit_Test()
        +visit_Block()
    }
    class DependencyGraph {
        +get_dependencies()
        +get_dependents()
    }
```

## Section 4

```mermaid
classDiagram
    class DependencyImpactAnalyzer {
        +__init__()
        +_build_dependency_graph()
        +_build_reverse_graph()
        +analyze_change_impact()
        +_find_affected_domains()
    }
    class DependencyManagerCore {
        +__init__()
        +get_info()
    }
    class DependencyManagerCoreCore {
        +__init__()
        +get_info()
    }
    class DependencyManagerServices {
        +__init__()
        +get_info()
    }
    class DependencyManagerServicesCore {
        +__init__()
        +get_info()
    }
    class DependencyManagerServicesCoreCore {
        +__init__()
        +get_info()
    }
    class DependencyManagerServicesServices {
        +__init__()
        +get_info()
    }
    class DependencyManagerServicesServicesCore {
        +__init__()
        +get_info()
    }
```

## Section 5

```mermaid
classDiagram
    class DependencyManagerServicesServicesValidation {
        +__init__()
        +get_info()
    }
    class DependencyManagerServicesValidation {
        +__init__()
        +get_info()
    }
    class DependencyManagerValidation {
        +__init__()
        +get_info()
    }
    class DependencyMapper {
        +__init__()
        +create_dependency_graph()
        +validate_dependencies()
        +resolve_dependency_conflicts()
        +_resolve_spec_dependencies()
    }
    class DependencyMapperCore {
        +__init__()
        +get_info()
    }
    class DependencyMapperCoreCore {
        +__init__()
        +get_info()
    }
    class DependencyMapperCoreCoreValidation {
        +__init__()
        +get_info()
    }
    class DependencyMapperCoreValidation {
        +__init__()
        +get_info()
    }
```

## Section 6

```mermaid
classDiagram
    class DependencyMapperValidation {
        +__init__()
        +get_info()
    }
    class DependencyProcessor {
        +__init__()
        +from_relationship()
        +hasparent()
        +per_property_preprocessors()
        +per_property_flush_actions()
    }
    class DependencyRelationship {
    }
    class DependencyResult {
    }
    class DependencyStatus {
    }
    class DependencyValidator {
        +__init__()
        +_initialize_allowed_dependencies()
        +validate_class_dependencies()
        +validate_module_dependencies()
        +_determine_class_layer()
    }
    class DependencyVisitor {
        +__init__()
        +visit_mypy_file()
        +visit_func_def()
        +visit_decorator()
        +visit_class_def()
    }
    class DependencyWarning {
    }
```

## Section 7

```mermaid
classDiagram
    class DomainRegistryManager {
        +__init__()
        +load_registry()
        +_parse_domains()
        +_create_domain_from_registry()
        +get_domain()
    }
    class EnhancedInterfaceRegistry {
        +__init__()
        +get_info()
    }
    class ExtendedInstrumentationRegistry {
        +_locate_extended_factory()
        +_check_conflicts()
        +_extended_class_manager()
        +_collect_management_factories_for()
        +unregister()
    }
    class FileSystemRegistryChecker {
        +__init__()
        +check_availability()
        +_can_read_files()
        +_can_write_files()
        +_can_create_directories()
    }
    class FromImport {
    }
    class FutureImportation {
        +__init__()
    }
    class GitRegistryChecker {
        +__init__()
        +check_availability()
        +_can_access_git_repo()
        +_can_sync_to_remote()
        +_can_create_commits()
    }
    class GlobalRegistry {
        +__init__()
        +register_module()
        +unregister_module()
        +get_module()
        +get_all_modules()
    }
```

## Section 8

```mermaid
classDiagram
    class HTTPFailedDependency {
    }
    class HasAnyFromUnimportedType {
        +__init__()
        +visit_any()
        +visit_typeddict_type()
    }
    class Import {
        +__init__()
        +accept()
    }
    class ImportAll {
        +__init__()
        +accept()
    }
    class ImportBase {
        +__init__()
    }
    class ImportDependency {
    }
    class ImportDependencyRegistry {
        +__init__()
        +_init_database()
        +scan_module_imports()
        +register_module_imports()
        +_would_create_circular_import()
    }
    class ImportFrom {
        +__init__()
        +accept()
    }
    Import --|> ImportBase
    ImportAll --|> ImportBase
    ImportFrom --|> ImportBase
```

## Section 9

```mermaid
classDiagram
    class ImportKey {
    }
    class ImportResolverFixer {
        +__init__()
        +fix_import_issues()
        +_fix_test_file_imports()
        +create_missing_import_modules()
        +_create_missing_module()
    }
    class ImportSetting {
    }
    class ImportShadowedByLoopVar {
        +__init__()
    }
    class ImportStarNotPermitted {
        +__init__()
    }
    class ImportStarUsage {
        +__init__()
    }
    class ImportStarUsed {
        +__init__()
    }
    class ImportStatement {
    }
```

## Section 10

```mermaid
classDiagram
    class ImportString {
        +__class_getitem__()
        +__get_pydantic_core_schema__()
        +__get_pydantic_json_schema__()
        +_serialize()
        +__repr__()
    }
    class ImportTracker {
        +__init__()
        +add_import_from()
        +add_import()
        +require_name()
        +reexport()
    }
    class Importation {
        +__init__()
        +redefines()
        +_has_alias()
        +source_statement()
        +__str__()
    }
    class ImportationFrom {
        +__init__()
        +__str__()
        +source_statement()
    }
    class ImportedName {
    }
    class InterfaceRegistry {
        +__init__()
        +get_info()
    }
    class LateFutureImport {
    }
    class MakeAnyNonUnimported {
        +visit_any()
        +visit_type_alias_type()
    }
    ImportationFrom --|> Importation
```

## Section 11

```mermaid
classDiagram
    class MarkImportsMypyOnlyVisitor {
        +visit_import()
        +visit_import_from()
        +visit_import_all()
        +visit_func_def()
    }
    class MarkImportsUnreachableVisitor {
        +visit_import()
        +visit_import_from()
        +visit_import_all()
    }
    class MemoryRegistryChecker {
        +__init__()
        +check_availability()
        +_can_write_to_memory()
        +_can_read_from_memory()
        +_can_persist_memory()
    }
    class MessageTypeRegistry {
        +__init__()
        +_build_type_info()
        +get_type_info()
        +validate_payload()
        +get_all_types()
    }
    class MockModelRegistry {
        +list_available_domains()
        +get_domain_intelligence()
        +get_learning_insights()
    }
    class ModelRegistry {
        +__init__()
        +get_info()
    }
    class ModelRegistryOperations {
        +__init__()
        +register_model()
        +unregister_model()
        +list_models()
        +get_model_info()
    }
    class ModelRegistryUtils {
        +__init__()
        +get_info()
    }
```

## Section 12

```mermaid
classDiagram
    class ModelRegistryValidation {
        +__init__()
        +get_info()
    }
    class ModuleDependency {
        +__post_init__()
    }
    class PathRegistry {
        +__eq__()
        +__ne__()
        +_path_for_compare()
        +odd_element()
        +set()
    }
    class PayloadRegistry {
        +__init__()
        +get()
        +register()
    }
    class PersistentDAGRegistry {
        +__init__()
        +_init_database()
        +register_module()
        +_would_create_cycle()
        +get_dependencies()
    }
    class ProactiveInterfaceRegistry {
        +__init__()
        +get_info()
    }
    class PropRegistry {
        +__init__()
        +_truncate_recursive()
        +entity_path()
        +_getitem()
    }
    class PydanticImportError {
        +__init__()
    }
    PropRegistry --|> PathRegistry
```

## Section 13

```mermaid
classDiagram
    class ReflectiveModuleRegistry {
        +__init__()
        +register()
        +get()
        +list_modules()
    }
    class Registry {
        +__init__()
        +get_info()
    }
    class RegistryAvailabilityChecker {
        +check_availability()
        +get_critical_dependencies()
    }
    class RegistryAvailabilityStatus {
    }
    class RegistryCore {
        +__init__()
        +get_info()
    }
    class RegistryCoreCore {
        +__init__()
        +get_info()
    }
    class RegistryDashboard {
        +__init__()
        +get_info()
    }
    class RegistryError {
    }
```

## Section 14

```mermaid
classDiagram
    class RegistryHealthMonitor {
        +__init__()
        +check_registry_health()
        +is_field_modification_safe()
        +get_graceful_shutdown_message()
        +get_boot_time_check_results()
    }
    class RegistryHealthReport {
    }
    class RegistryIntegrationResult {
    }
    class RegistryIntegrationSystem {
        +__init__()
        +scan_modules_needing_registry()
        +_needs_registry_integration()
        +implement_registry_integration()
        +_implement_registry_in_file()
    }
    class RegistryIntelligenceEngine {
        +__init__()
        +get_info()
    }
    class RegistryManager {
        +__init__()
        +get_info()
    }
    class RegistryManagerCore {
        +__init__()
        +get_info()
    }
    class RegistryManagerProcessing {
        +__init__()
        +get_info()
    }
```

## Section 15

```mermaid
classDiagram
    class RegistryManagerValidation {
        +__init__()
        +get_info()
    }
    class RequestsDependencyWarning {
    }
    class RequirementsInheritanceRegistry {
        +__init__()
        +register_module()
        +add_requirement()
        +abdicate_parent()
        +_inherit_requirements()
    }
    class RootRegistry {
        +_getitem()
        +_truncate_recursive()
    }
    class ScopedRegistry {
        +__init__()
        +__call__()
        +has()
        +set()
        +clear()
    }
    class SharedKernelRegistry {
        +__init__()
        +register_kernel()
        +get_kernels_for_context()
        +detect_conflicts()
        +get_registry_summary()
    }
    class SimpleRegistry {
        +__init__()
        +register()
        +_would_create_cycle()
        +get_dependencies()
        +get_dependents()
    }
    class SlotsEntityRegistry {
    }
```

## Section 16

```mermaid
classDiagram
    class StarImportation {
        +__init__()
        +source_statement()
        +__str__()
    }
    class SubmoduleImportation {
        +__init__()
        +redefines()
        +__str__()
        +source_statement()
    }
    class TemplateRegistry {
        +__init__()
        +register_template()
        +get_template()
        +_get_parent_content()
        +_merge_template_content()
    }
    class ThreadLocalRegistry {
        +__init__()
        +__call__()
        +has()
        +set()
        +clear()
    }
    class TokenRegistry {
        +__init__()
        +generate_for_superclasses()
        +_generate_natural_for_superclasses()
        +_getitem()
    }
    class UnusedImport {
        +__init__()
    }
    class _ModuleRegistry {
        +__init__()
        +preload_module()
        +import_prefix()
    }
    class registry {
        +__init__()
        +update_type_annotation_map()
        +_resolve_type()
        +mappers()
        +_set_depends_on()
    }
```

## All Classes in Domain

- `AbstractEntityRegistry`
- `AgentRegistry`
- `AgentRegistryCore`
- `AgentRegistryCoreCore`
- `BacklogDependencyManager`
- `BeastModeRegistry`
- `BeastModeRegistryIntegration`
- `CLIRegistry`
- `CachingEntityRegistry`
- `CantImport`
- `CircularDependencyDetector`
- `CircularDependencyError`
- `CircularDependencyReport`
- `ClsRegistryToken`
- `ComprehensiveDependencyAnalyzer`
- `DAGRegistry`
- `DependencyAnalyzer`
- `DependencyAnalyzerCore`
- `DependencyAnalyzerCoreCore`
- `DependencyAnalyzerValidation`
- `DependencyChecker`
- `DependencyConflict`
- `DependencyFinderVisitor`
- `DependencyGraph`
- `DependencyImpactAnalyzer`
- `DependencyManagerCore`
- `DependencyManagerCoreCore`
- `DependencyManagerServices`
- `DependencyManagerServicesCore`
- `DependencyManagerServicesCoreCore`
- `DependencyManagerServicesServices`
- `DependencyManagerServicesServicesCore`
- `DependencyManagerServicesServicesValidation`
- `DependencyManagerServicesValidation`
- `DependencyManagerValidation`
- `DependencyMapper`
- `DependencyMapperCore`
- `DependencyMapperCoreCore`
- `DependencyMapperCoreCoreValidation`
- `DependencyMapperCoreValidation`
- `DependencyMapperValidation`
- `DependencyProcessor`
- `DependencyRelationship`
- `DependencyResult`
- `DependencyStatus`
- `DependencyValidator`
- `DependencyVisitor`
- `DependencyWarning`
- `DomainRegistryManager`
- `EnhancedInterfaceRegistry`
- `ExtendedInstrumentationRegistry`
- `FileSystemRegistryChecker`
- `FromImport`
- `FutureImportation`
- `GitRegistryChecker`
- `GlobalRegistry`
- `HTTPFailedDependency`
- `HasAnyFromUnimportedType`
- `Import`
- `ImportAll`
- `ImportBase`
- `ImportDependency`
- `ImportDependencyRegistry`
- `ImportFrom`
- `ImportKey`
- `ImportResolverFixer`
- `ImportSetting`
- `ImportShadowedByLoopVar`
- `ImportStarNotPermitted`
- `ImportStarUsage`
- `ImportStarUsed`
- `ImportStatement`
- `ImportString`
- `ImportTracker`
- `Importation`
- `ImportationFrom`
- `ImportedName`
- `InterfaceRegistry`
- `LateFutureImport`
- `MakeAnyNonUnimported`
- `MarkImportsMypyOnlyVisitor`
- `MarkImportsUnreachableVisitor`
- `MemoryRegistryChecker`
- `MessageTypeRegistry`
- `MockModelRegistry`
- `ModelRegistry`
- `ModelRegistryOperations`
- `ModelRegistryUtils`
- `ModelRegistryValidation`
- `ModuleDependency`
- `PathRegistry`
- `PayloadRegistry`
- `PersistentDAGRegistry`
- `ProactiveInterfaceRegistry`
- `PropRegistry`
- `PydanticImportError`
- `ReflectiveModuleRegistry`
- `Registry`
- `RegistryAvailabilityChecker`
- `RegistryAvailabilityStatus`
- `RegistryCore`
- `RegistryCoreCore`
- `RegistryDashboard`
- `RegistryError`
- `RegistryHealthMonitor`
- `RegistryHealthReport`
- `RegistryIntegrationResult`
- `RegistryIntegrationSystem`
- `RegistryIntelligenceEngine`
- `RegistryManager`
- `RegistryManagerCore`
- `RegistryManagerProcessing`
- `RegistryManagerValidation`
- `RequestsDependencyWarning`
- `RequirementsInheritanceRegistry`
- `RootRegistry`
- `ScopedRegistry`
- `SharedKernelRegistry`
- `SimpleRegistry`
- `SlotsEntityRegistry`
- `StarImportation`
- `SubmoduleImportation`
- `TemplateRegistry`
- `ThreadLocalRegistry`
- `TokenRegistry`
- `UnusedImport`
- `_ModuleRegistry`
- `registry`
