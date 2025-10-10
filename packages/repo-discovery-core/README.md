# Repository Discovery Core

This package contains the reflective modules that power the repository
content discovery pipeline used throughout the Beast Mode ecosystem. It
includes:

- `ContentClassifier` – heuristics-driven content type classification.
- `ContentMetadataExtractor` – rich metadata extraction with graceful
  degradation support.
- `ContentInventoryManager` – aggregation helpers for large repository
  analyses.
- `ContentScanner` – orchestration logic for scanning directory trees.

## Installation

```bash
pip install repo-discovery-core
```

## Optional RM-DDD Integration

The classes expose the same interfaces as the in-repo versions. To enable
advanced RM-DDD monitoring and metrics, install the optional dependency:

```bash
pip install repo-discovery-core[rm-ddd]
```

## Usage

```python
from repo_discovery_core import ContentScanner

scanner = ContentScanner()
report = scanner.scan_repository("./my-repo")
```

The modules are shipped exactly as used in production so downstream agents
can benefit from the same validated workflows without importing the entire
platform.

