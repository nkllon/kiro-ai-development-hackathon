# Implementation Plan - Recursive Descent Architecture

Convert the Repository Content Discovery and Indexing design into a series of prompts for a code-generation LLM that will implement each step in a test-driven manner using recursive descent methodology. Each component is implemented by first ensuring all its dependencies exist, following a systematic top-down approach that builds complete vertical slices before moving to the next component.

## Recursive Descent Implementation Strategy

**Principle**: For each target component, recursively implement all dependencies first, then implement the component itself. This ensures no orphaned code and complete integration at each step.

**Pattern**: 
1. **Identify Target Component**
2. **Recursively Implement Dependencies** (if not already implemented)
3. **Implement Target Component** 
4. **Integration Test** complete vertical slice
5. **Move to Next Component**

## Phase 1: Foundation Layer (Recursive Descent Root)

### 1.1 Foundation Dependencies Resolution

- [ ] 1.1.1 Implement ReflectiveModule base infrastructure
  - **Target**: ReflectiveModule base class (200 lines)
  - **Dependencies**: None (root dependency)
  - Create ReflectiveModule base class with health monitoring, status reporting, and capability interfaces
  - Implement ModuleHealth, ModuleStatus, and ModuleCapability enums and data classes
  - Write unit tests for base RM-DDD infrastructure
  - **Integration Test**: Verify ReflectiveModule can be instantiated and health-checked
  - _Requirements: 16.1, 22.1, 18.1_

- [ ] 1.1.2 Recover existing Directus implementation
  - **Target**: Directus Schema Recovery (150 lines)
  - **Dependencies**: None (parallel root dependency)
  - Restore Directus schema design and migration files from git commit 4d2a4e62 to current working directory
  - Validate that existing interface registry implementation works and can be extended
  - Create test suite to verify existing Directus functionality before extension
  - **Integration Test**: Verify Directus schema can be loaded and queried
  - _Requirements: 30.1, 3.1, 18.1_

### 1.2 Infrastructure Layer Dependencies

- [ ] 1.2.1 Implement ContentMetadataExtractor
  - **Target**: ContentMetadataExtractor (200 lines)
  - **Dependencies**: ReflectiveModule (from 1.1.1)
  - **Recursive Check**: Ensure ReflectiveModule is implemented and tested
  - Create ContentMetadataExtractor class inheriting from ReflectiveModule
  - Implement metadata extraction for file size, dates, encoding, and basic relationships
  - Write unit tests for metadata extraction functionality
  - **Integration Test**: Verify metadata can be extracted from sample repository files
  - _Requirements: 1.3, 16.1, 18.1_

- [ ] 1.2.2 Extend Directus schema for repository content with referential integrity
  - **Target**: Directus Schema Extension with Physics-Informed Referential Integrity (300 lines)
  - **Dependencies**: Directus Schema Recovery (from 1.1.2)
  - **Recursive Check**: Ensure Directus recovery is complete and tested
  - Add repository_items, specifications, requirements, analysis_artifacts, and operation_traces collections
  - Implement physics-informed referential integrity with CASCADE DELETE for strong dependencies and SET NULL for weak dependencies
  - Create comprehensive migration scripts with explicit foreign key constraints, indexes, and validation functions
  - Add referential integrity validation functions and data consistency triggers
  - Write integration tests to verify extended schema maintains data consistency under all failure conditions
  - **Integration Test**: Verify referential integrity constraints prevent orphaned data and maintain consistency
  - _Requirements: 8.1, 30.1, 30.2, 30.3, 30.4, 30.5, 18.2_

## Phase 2: Content Discovery Layer (Recursive Descent)

### 2.1 Content Discovery Components

- [ ] 2.1.1 Implement ContentScanner
  - **Target**: ContentScanner (150 lines)
  - **Dependencies**: ReflectiveModule (1.1.1), ContentMetadataExtractor (1.2.1)
  - **Recursive Check**: Verify ReflectiveModule and ContentMetadataExtractor are implemented and tested
  - Create ContentScanner class inheriting from ReflectiveModule
  - Implement discover_all_content() method to systematically scan repository filesystem
  - Add file system traversal with filtering and exclusion patterns
  - Write unit tests for content scanning functionality
  - **Integration Test**: Verify ContentScanner can discover and catalog sample repository structure
  - _Requirements: 1.1, 16.1, 18.1_

- [ ] 2.1.2 Implement ContentClassifier
  - **Target**: ContentClassifier (150 lines)
  - **Dependencies**: ReflectiveModule (1.1.1), ContentMetadataExtractor (1.2.1)
  - **Recursive Check**: Verify ReflectiveModule and ContentMetadataExtractor are implemented and tested
  - Create ContentClassifier class inheriting from ReflectiveModule
  - Implement classify_content_types() method to categorize discovered content (specs, source code, docs, analysis, scripts)
  - Add pattern matching and heuristic classification logic
  - Write unit tests for content classification functionality
  - **Integration Test**: Verify ContentClassifier can correctly classify sample repository files
  - _Requirements: 1.2, 16.1, 18.1_

### 2.2 Inventory Management Layer

- [ ] 2.2.1 Implement ContentInventoryManager
  - **Target**: ContentInventoryManager (150 lines)
  - **Dependencies**: ContentScanner (2.1.1), ContentClassifier (2.1.2)
  - **Recursive Check**: Verify ContentScanner and ContentClassifier are implemented and tested
  - Create ContentInventoryManager class inheriting from ReflectiveModule
  - Implement comprehensive inventory management combining scanning and classification results
  - Add change detection using git integration for automatic content updates
  - Write unit tests for inventory management functionality
  - **Integration Test**: Verify complete content discovery workflow from scanning through inventory
  - _Requirements: 1.4, 1.5, 16.1, 18.1_

### 2.3 Specification Analysis Layer

- [ ] 2.3.1 Implement SpecificationParser
  - **Target**: SpecificationParser (200 lines)
  - **Dependencies**: ContentScanner (2.1.1), ContentClassifier (2.1.2)
  - **Recursive Check**: Verify content discovery components are implemented and tested
  - Create SpecificationParser class inheriting from ReflectiveModule
  - Implement analyze_specification() method to extract requirements, user stories, and acceptance criteria
  - Add markdown parsing and structured requirement extraction
  - Write unit tests for specification parsing functionality
  - **Integration Test**: Verify SpecificationParser can extract structured data from sample spec files
  - _Requirements: 2.1, 16.1, 18.1_

## Phase 3: Advanced Analysis Layer (Recursive Descent)

### 3.1 Dependency Analysis Components

- [ ] 3.1.1 Implement DependencyAnalyzer
  - **Target**: DependencyAnalyzer (200 lines)
  - **Dependencies**: SpecificationParser (2.3.1), ContentInventoryManager (2.2.1)
  - **Recursive Check**: Verify SpecificationParser and ContentInventoryManager are implemented and tested
  - Create DependencyAnalyzer class inheriting from ReflectiveModule
  - Implement identify_dependencies() method to find relationships between specifications
  - Add circular dependency detection and dependency graph construction
  - Write unit tests for dependency analysis functionality
  - **Integration Test**: Verify DependencyAnalyzer can map relationships in sample specification set
  - _Requirements: 2.2, 16.1, 18.1_

- [ ] 3.1.2 Implement OverlapDetector
  - **Target**: OverlapDetector (300 lines)
  - **Dependencies**: SpecificationParser (2.3.1), ContentInventoryManager (2.2.1)
  - **Recursive Check**: Verify SpecificationParser and ContentInventoryManager are implemented and tested
  - Create OverlapDetector class inheriting from ReflectiveModule
  - Implement detect_overlaps() method to identify overlapping functionality and conflicting objectives
  - Add create_searchable_index() method to build searchable knowledge base of requirements
  - Create SpecificationAnalysis and OverlapMatrix domain models following RM-DDD patterns
  - Write unit tests for overlap detection and search indexing
  - **Integration Test**: Verify OverlapDetector can identify conflicts in sample specification set
  - _Requirements: 2.3, 2.4, 16.2, 18.1_

### 3.2 Foundational Tools Integration Layer

- [ ] 3.2.1 Implement GhostbustersIntegration
  - **Target**: GhostbustersIntegration (250 lines)
  - **Dependencies**: ReflectiveModule (1.1.1)
  - **Recursive Check**: Verify ReflectiveModule base is implemented and tested
  - Create GhostbustersIntegration class that uses existing ghostbusters_consultation_refactored.py
  - Implement multi-perspective validation using existing Ghostbusters framework
  - Add error handling for Ghostbusters tool failures with graceful degradation
  - Write integration tests to verify Ghostbusters tools work as expected per their requirements
  - **Integration Test**: Verify GhostbustersIntegration can coordinate multi-perspective analysis
  - _Requirements: 14.1, 15.1, 24.1, 18.1_

- [ ] 3.2.2 Implement RCAIntegration
  - **Target**: RCAIntegration (200 lines)
  - **Dependencies**: ReflectiveModule (1.1.1)
  - **Recursive Check**: Verify ReflectiveModule base is implemented and tested
  - Create RCAIntegration class that uses existing rca_cli.py and root cause analysis implementations
  - Implement systematic root cause analysis for discovery conflicts and issues
  - Add RCA-based error recovery following existing RCA patterns
  - Write integration tests to verify RCA tools meet their requirements for automatic failure analysis
  - **Integration Test**: Verify RCAIntegration can perform systematic root cause analysis
  - _Requirements: 14.3, 15.4, 17.1, 18.1_

- [ ] 3.2.3 Implement PDCAIntegration
  - **Target**: PDCAIntegration (200 lines)
  - **Dependencies**: ReflectiveModule (1.1.1)
  - **Recursive Check**: Verify ReflectiveModule base is implemented and tested
  - Create PDCAIntegration class that uses existing pdca_orchestrator_core.py
  - Implement systematic PDCA cycles for discovery workflows instead of ad-hoc processes
  - Add PDCA-based workflow orchestration for repository analysis
  - Write integration tests to verify PDCA orchestrator meets systematic cycle execution requirements
  - **Integration Test**: Verify PDCAIntegration can orchestrate systematic analysis workflows
  - _Requirements: 14.4, 15.2, 20.1, 18.1_

## Phase 4: Intelligence Coordination Layer (Recursive Descent)

### 4.1 Multi-Perspective Analysis Components

- [ ] 4.1.1 Implement PerspectiveCoordinator
  - **Target**: PerspectiveCoordinator (250 lines)
  - **Dependencies**: DependencyAnalyzer (3.1.1), OverlapDetector (3.1.2), GhostbustersIntegration (3.2.1), RCAIntegration (3.2.2), PDCAIntegration (3.2.3)
  - **Recursive Check**: Verify all analysis and integration components are implemented and tested
  - Create PerspectiveCoordinator class inheriting from ReflectiveModule
  - Implement engage_diverse_perspectives() method to coordinate multiple LLM expert perspectives
  - Add validate_with_ghostbusters() method integrating with GhostbustersIntegration
  - Write unit tests for multi-perspective coordination functionality
  - **Integration Test**: Verify PerspectiveCoordinator can orchestrate multi-perspective analysis using all foundational tools
  - _Requirements: 4.1, 4.2, 16.1, 18.1_

- [ ] 4.1.2 Implement DeterministicValidator
  - **Target**: DeterministicValidator (300 lines)
  - **Dependencies**: ReflectiveModule (1.1.1)
  - **Recursive Check**: Verify ReflectiveModule base is implemented and tested
  - Create DeterministicValidator class inheriting from ReflectiveModule
  - Implement deterministic validation methods to validate heuristic insights where possible
  - Add confidence calibration system to balance heuristic vs deterministic approaches
  - Add uncertainty quantification and confidence levels for all intelligence outputs
  - Write unit tests for validation methods and confidence calibration
  - **Integration Test**: Verify DeterministicValidator can validate and calibrate analysis results
  - _Requirements: 13.1, 13.2, 28.1, 18.1_

### 4.2 Intelligence Synthesis Layer

- [ ] 4.2.1 Implement IntelligenceSynthesizer
  - **Target**: IntelligenceSynthesizer (250 lines)
  - **Dependencies**: PerspectiveCoordinator (4.1.1), DeterministicValidator (4.1.2)
  - **Recursive Check**: Verify PerspectiveCoordinator and DeterministicValidator are implemented and tested
  - Create IntelligenceSynthesizer class inheriting from ReflectiveModule
  - Implement synthesize_perspectives() method to combine diverse viewpoints while preserving unique insights
  - Add resolve_conflicts() method with systematic conflict resolution protocols and confidence scoring
  - Create PerspectiveAnalysis and ConflictResolution domain models following RM-DDD patterns
  - Write unit tests for perspective synthesis and conflict resolution
  - **Integration Test**: Verify complete intelligence pipeline from perspective coordination through synthesis
  - _Requirements: 4.4, 11.1, 11.2, 18.1_

## Phase 5: Repository Intelligence API Layer (Recursive Descent)

### 5.1 Core API Components

- [ ] 5.1.1 Implement ContentQueryAPI with referential integrity validation
  - **Target**: ContentQueryAPI with Referential Integrity Support (250 lines)
  - **Dependencies**: Directus Schema Extension (1.2.2), ContentInventoryManager (2.2.1)
  - **Recursive Check**: Verify Directus schema extension with referential integrity and content inventory are implemented and tested
  - Create ContentQueryAPI class inheriting from ReflectiveModule
  - Implement get_content_by_type() method with filtering, sorting, and referential integrity validation
  - Add search_content() method for full-text search across repository content with relationship traversal
  - Implement referential integrity validation for all query operations to prevent accessing orphaned data
  - Write unit tests for core API functionality including referential integrity edge cases
  - **Integration Test**: Verify ContentQueryAPI maintains referential integrity during concurrent access and data modifications
  - _Requirements: 8.2, 30.1, 30.4, 16.1, 18.1_

- [ ] 5.1.2 Implement RelationshipAPI
  - **Target**: RelationshipAPI (200 lines)
  - **Dependencies**: Directus Schema Extension (1.2.2), DependencyAnalyzer (3.1.1), OverlapDetector (3.1.2)
  - **Recursive Check**: Verify Directus schema extension and analysis components are implemented and tested
  - Create RelationshipAPI class inheriting from ReflectiveModule
  - Implement query_relationships() method for traversing dependencies and relationships
  - Add GraphQL-style relationship queries for dependencies and overlaps
  - Write unit tests for relationship API functionality
  - **Integration Test**: Verify RelationshipAPI can traverse and query complex repository relationships
  - _Requirements: 8.4, 16.1, 18.1_

### 5.2 Real-Time Services Layer

- [ ] 5.2.0 Implement ReferentialIntegrityValidator
  - **Target**: ReferentialIntegrityValidator (200 lines)
  - **Dependencies**: Directus Schema Extension (1.2.2)
  - **Recursive Check**: Verify Directus schema extension with referential integrity is implemented and tested
  - Create ReferentialIntegrityValidator class inheriting from ReflectiveModule
  - Implement validate_repository_integrity() function to check for orphaned records across all tables
  - Add constraint validation functions for specifications, requirements, and analysis_artifacts relationships
  - Implement data consistency triggers for audit logging and cleanup operations
  - Add physics-informed consistency validation: conservation of information, cascade propagation, temporal consistency
  - Write comprehensive tests for all referential integrity validation scenarios
  - **Integration Test**: Verify referential integrity validator detects and prevents all data consistency violations
  - _Requirements: 30.1, 30.2, 30.3, 30.4, 30.5, 16.1, 18.1_

- [ ] 5.2.1 Implement RealTimeService
  - **Target**: RealTimeService (250 lines)
  - **Dependencies**: ContentQueryAPI (5.1.1), RelationshipAPI (5.1.2), IntelligenceSynthesizer (4.2.1)
  - **Recursive Check**: Verify API components and intelligence synthesis are implemented and tested
  - Create RealTimeService class inheriting from ReflectiveModule
  - Implement get_real_time_updates() method using WebSocket integration with Directus infrastructure
  - Add real-time notifications for repository changes and intelligence updates
  - Write integration tests for real-time update functionality
  - **Integration Test**: Verify complete real-time intelligence pipeline from content changes to notifications
  - _Requirements: 8.5, 29.2, 18.1_

- [ ] 5.2.2 Implement ChangeTracker with referential integrity enforcement
  - **Target**: ChangeTracker with Physics-Informed Consistency (350 lines)
  - **Dependencies**: RealTimeService (5.2.1), ContentInventoryManager (2.2.1)
  - **Recursive Check**: Verify RealTimeService and ContentInventoryManager are implemented and tested
  - Create ChangeTracker class inheriting from ReflectiveModule
  - Implement change tracking and versioning using Directus built-in capabilities with referential integrity enforcement
  - Add CRUD operations for specifications, requirements, and analysis artifacts with cascade behavior validation
  - Implement physics-informed consistency rules: conservation of information, cascade propagation laws, temporal consistency
  - Add comprehensive validation and consistency checking for all repository content modifications
  - Implement audit logging for all referential integrity operations using operation_traces table
  - Write integration tests for CRUD operations, change tracking, and referential integrity enforcement
  - **Integration Test**: Verify complete change tracking workflow maintains referential integrity under all modification scenarios
  - _Requirements: 8.3, 8.5, 7.1, 30.1, 30.2, 30.3, 30.4, 30.5, 18.1_

## Phase 6: Security and Operations Layer (Recursive Descent)

### 6.1 Security Architecture

- [ ] 6.1.1 Implement SecurityManager
  - **Target**: SecurityManager (300 lines)
  - **Dependencies**: ContentQueryAPI (5.1.1), RelationshipAPI (5.1.2), RealTimeService (5.2.1)
  - **Recursive Check**: Verify all API components are implemented and tested
  - Create SecurityManager class inheriting from ReflectiveModule
  - Add authentication and role-based authorization for repository intelligence access
  - Implement data encryption at rest for indexed content and analysis results
  - Add comprehensive security audit trails for all operations with correlation IDs
  - Write security tests to verify access controls and audit logging
  - **Integration Test**: Verify complete security architecture protects all API endpoints and data
  - _Requirements: 9.1, 9.2, 23.1, 18.1_

### 6.2 Operational Resilience

- [ ] 6.2.1 Implement DisasterRecovery
  - **Target**: DisasterRecovery (300 lines)
  - **Dependencies**: SecurityManager (6.1.1), ChangeTracker (5.2.2)
  - **Recursive Check**: Verify SecurityManager and ChangeTracker are implemented and tested
  - Create DisasterRecovery class inheriting from ReflectiveModule
  - Implement graceful degradation when foundational tools fail (fallback strategies for all integrations)
  - Add automated disaster recovery with backup and restore capabilities
  - Implement health monitoring and status reporting for all RM-DDD components
  - Write chaos engineering tests to verify system resilience under failure scenarios
  - **Integration Test**: Verify complete disaster recovery workflow including graceful degradation
  - _Requirements: 24.1, 24.2, 22.4, 25.1_

## Phase 7: Performance and Monitoring Layer (Recursive Descent)

### 7.1 Performance Optimization

- [ ] 7.1.1 Implement PerformanceOptimizer
  - **Target**: PerformanceOptimizer (250 lines)
  - **Dependencies**: RealTimeService (5.2.1), ChangeTracker (5.2.2)
  - **Recursive Check**: Verify RealTimeService and ChangeTracker are implemented and tested
  - Create PerformanceOptimizer class inheriting from ReflectiveModule
  - Add incremental indexing and change detection to minimize processing overhead
  - Implement intelligent caching strategies for frequently accessed content
  - Add performance monitoring and optimization for large repositories (69+ specs)
  - Write load tests to validate performance under concurrent multi-agent access patterns
  - **Integration Test**: Verify performance optimization improves system throughput and response times
  - _Requirements: 10.1, 10.2, 25.4, 18.1_

### 7.2 Monitoring and Observability

- [ ] 7.2.1 Implement MonitoringDashboard with referential integrity monitoring
  - **Target**: MonitoringDashboard with Physics-Informed Consistency Monitoring (300 lines)
  - **Dependencies**: PerformanceOptimizer (7.1.1), SecurityManager (6.1.1), ReferentialIntegrityValidator (5.2.0)
  - **Recursive Check**: Verify PerformanceOptimizer, SecurityManager, and ReferentialIntegrityValidator are implemented and tested
  - Create MonitoringDashboard class inheriting from ReflectiveModule
  - Implement usage tracking and performance metrics for all ReflectiveModule operations
  - Add comprehensive logging with correlation IDs for operation traceability including referential integrity operations
  - Implement real-time monitoring of referential integrity health and constraint violations
  - Add physics-informed consistency monitoring: conservation of information violations, cascade propagation failures, temporal consistency issues
  - Create monitoring dashboards for repository intelligence system health including referential integrity status
  - Write monitoring tests to verify tracking, logging, and referential integrity monitoring functionality
  - **Integration Test**: Verify complete monitoring pipeline provides comprehensive system observability including referential integrity health
  - _Requirements: 22.1, 22.2, 22.5, 30.4, 30.5, 18.1_

## Phase 8: System Integration Layer (Recursive Descent)

### 8.1 CLI Generation

- [ ] 8.1.1 Implement CLIGenerator
  - **Target**: CLIGenerator (200 lines)
  - **Dependencies**: ReflectiveModule (1.1.1), ContentQueryAPI (5.1.1), RelationshipAPI (5.1.2)
  - **Recursive Check**: Verify ReflectiveModule base and API components are implemented and tested
  - Create CLIGenerator class inheriting from ReflectiveModule
  - Implement dynamic CLI generation using ReflectiveModule introspection to generate command-line interfaces
  - Add lazy instantiation so unused CLIs are never created unless invoked
  - Add automatic help documentation generation from RM-DDD interface metadata
  - Write tests for dynamic CLI generation and help documentation
  - **Integration Test**: Verify CLIGenerator can create functional CLI interfaces for all API components
  - _Requirements: 21.1, 21.2, 21.4, 18.1_

### 8.2 System Integration

- [ ] 8.2.1 Implement SystemIntegrator
  - **Target**: SystemIntegrator (200 lines)
  - **Dependencies**: IntelligenceSynthesizer (4.2.1), RealTimeService (5.2.1), ChangeTracker (5.2.2), CLIGenerator (8.1.1)
  - **Recursive Check**: Verify all intelligence, API, and CLI components are implemented and tested
  - Create SystemIntegrator class inheriting from ReflectiveModule
  - Wire together all components into unified repository intelligence system
  - Create main RepositoryIntelligence aggregate root that coordinates all discovery and analysis operations
  - Add system-wide configuration and initialization
  - Write end-to-end integration tests for complete repository discovery workflow
  - **Integration Test**: Verify complete system integration from content discovery through intelligence synthesis to API access
  - _Requirements: 5.1, 5.2, 6.1, 18.4_

## Phase 9: Validation and Deployment Layer (Recursive Descent)

### 9.1 Comprehensive Validation

- [ ] 9.1.1 Implement ValidationSuite
  - **Target**: ValidationSuite (150 lines)
  - **Dependencies**: SystemIntegrator (8.2.1), MonitoringDashboard (7.2.1)
  - **Recursive Check**: Verify complete system integration and monitoring are implemented and tested
  - Create ValidationSuite class inheriting from ReflectiveModule
  - Create comprehensive test suite covering unit, integration, and system tests with >90% coverage
  - Add RDI traceability validation to ensure every implementation traces back to specific requirements
  - Implement systematic validation methods to prove the system follows its own systematic principles
  - Write validation tests that demonstrate measurable superiority over ad-hoc discovery methods
  - **Integration Test**: Verify complete system validation including RDI traceability and systematic compliance
  - _Requirements: 25.5, 19.4, 20.5, 18.5_

### 9.2 Production Deployment

- [ ] 9.2.1 Implement DeploymentManager
  - **Target**: DeploymentManager (150 lines)
  - **Dependencies**: ValidationSuite (9.1.1), DisasterRecovery (6.2.1)
  - **Recursive Check**: Verify complete system validation and disaster recovery are implemented and tested
  - Create DeploymentManager class inheriting from ReflectiveModule
  - Create deployment scripts and configuration for production repository intelligence system
  - Add comprehensive API documentation with examples for multi-agent access
  - Create user guides for Beast Master operations and multi-agent collaboration
  - Write deployment tests to verify production readiness and operational capability
  - **Integration Test**: Verify complete production deployment including all operational capabilities
  - _Requirements: 29.1, 5.1, 24.5, 18.1_

## Recursive Descent Validation

### Dependency Chain Verification
Each implementation task includes a **Recursive Check** step that verifies all dependencies are implemented and tested before proceeding. This ensures:

1. **No Orphaned Code**: Every component is integrated with its dependencies
2. **Complete Vertical Slices**: Each phase delivers working functionality
3. **Systematic Integration**: Dependencies are resolved in proper order
4. **Testable Increments**: Each component can be tested with its dependencies

### Integration Test Strategy
Each component includes an **Integration Test** that verifies:
- The component works with all its dependencies
- The complete vertical slice functions correctly
- No regression in previously implemented functionality
- RDI traceability is maintained throughout

This recursive descent approach ensures systematic implementation with complete integration at every step.