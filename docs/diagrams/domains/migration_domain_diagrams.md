# Migration Domain Architecture

**Total Classes**: 9

## Section 1

```mermaid
classDiagram
    class LiveMigrationManager {
        +__init__()
        +get_module_status()
        +is_healthy()
        +get_health_indicators()
        +_get_primary_responsibility()
    }
    class MigrationCore {
        +__init__()
        +get_info()
    }
    class MigrationCoreCore {
        +__init__()
        +get_info()
    }
    class MigrationManager {
        +__init__()
        +get_info()
    }
    class MigrationManagerCore {
        +__init__()
        +get_info()
    }
    class MigrationManagerServices {
        +__init__()
        +get_info()
    }
    class MigrationResult {
    }
    class MigrationState {
    }
```

## Section 2

```mermaid
classDiagram
    class MigrationStep {
    }
```

## All Classes in Domain

- `LiveMigrationManager`
- `MigrationCore`
- `MigrationCoreCore`
- `MigrationManager`
- `MigrationManagerCore`
- `MigrationManagerServices`
- `MigrationResult`
- `MigrationState`
- `MigrationStep`
