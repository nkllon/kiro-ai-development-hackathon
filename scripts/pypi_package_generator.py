#!/usr/bin/env python3
"""
PyPI Package Generator

Generates PyPI packages from high-scoring domains in the project model.
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class PackageConfig:
    """Configuration for a PyPI package"""

    name: str
    version: str
    description: str
    author: str
    author_email: str
    packages: list[str]
    install_requires: list[str]
    python_requires: str
    classifiers: list[str]
    keywords: list[str]
    project_urls: dict[str, str]


class PyPIPackageGenerator:
    """Generates PyPI packages from project model domains"""

    def __init__(self, model_file: str = "project_model_registry.json"):
        self.model_file = Path(model_file)
        self.model_data = None
        self.packages_dir = Path("generated_packages")

    def load_model(self) -> None:
        """Load the project model"""
        if not self.model_file.exists():
            msg = f"Model file not found: {self.model_file}"
            raise FileNotFoundError(msg)

        with open(self.model_file) as f:
            self.model_data = json.load(f)
        print(f"✅ Loaded model: {self.model_file}")

    def get_high_scoring_domains(self, min_score: int = 8) -> list[dict[str, Any]]:
        """Get domains with high package potential scores"""
        high_scoring = []

        for domain_name, domain_data in self.model_data.get("domains", {}).items():
            if isinstance(domain_data, dict) and "package_potential" in domain_data:
                package_info = domain_data["package_potential"]
                if package_info.get("score", 0) >= min_score:
                    high_scoring.append(
                        {
                            "domain": domain_name,
                            "package_name": package_info.get("package_name", f"openflow-{domain_name}"),
                            "score": package_info.get("score", 0),
                            "pypi_ready": package_info.get("pypi_ready", False),
                            "reasons": package_info.get("reasons", []),
                            "domain_data": domain_data,
                        }
                    )

        return sorted(high_scoring, key=lambda x: x["score"], reverse=True)

    def generate_package_structure(self, package_info: dict[str, Any]) -> None:
        """Generate the complete package structure"""
        package_name = package_info["package_name"]
        package_info["domain"]
        package_info["domain_data"]

        package_dir = self.packages_dir / package_name
        package_dir.mkdir(parents=True, exist_ok=True)

        print(f"📦 Generating package: {package_name}")

        # Create package structure
        self._create_pyproject_toml(package_dir, package_info)
        self._create_readme(package_dir, package_info)
        self._create_init_files(package_dir, package_info)
        self._create_setup_py(package_dir, package_info)
        self._create_license(package_dir)
        self._create_manifest(package_dir)

        print(f"✅ Package {package_name} generated successfully")

    def _create_pyproject_toml(self, package_dir: Path, package_info: dict[str, Any]) -> None:
        """Create pyproject.toml for the package"""
        package_name = package_info["package_name"]
        domain_name = package_info["domain"]

        content = f"""[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{package_name}"
version = "0.1.0"
description = "OpenFlow {domain_name.replace("_", " ").title()} package"
readme = "README.md"
license = {{text = "MIT"}}
authors = [
    {{name = "OpenFlow Team", email = "team@openflow.dev"}}
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]
keywords = ["openflow", "{domain_name}", "development", "tools"]
requires-python = ">=3.8"
dependencies = [
    "pydantic>=2.0.0",
    "typing-extensions>=4.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
]

[project.urls]
Homepage = "https://github.com/openflow/openflow-{domain_name}"
Repository = "https://github.com/openflow/openflow-{domain_name}"
Documentation = "https://openflow-{domain_name}.readthedocs.io"
"""

        with open(package_dir / "pyproject.toml", "w") as f:
            f.write(content)

    def _create_readme(self, package_dir: Path, package_info: dict[str, Any]) -> None:
        """Create README.md for the package"""
        package_name = package_info["package_name"]
        domain_name = package_info["domain"]
        score = package_info["score"]

        content = f"""# {package_name}

OpenFlow {domain_name.replace("_", " ").title()} Package

## Package Potential Score: {score}/10

This package was automatically generated from the OpenFlow project model based on high package potential scoring.

## Features

- **High Reusability**: Designed for maximum reusability across projects
- **Quality Assured**: Follows OpenFlow quality standards
- **Well Documented**: Comprehensive documentation and examples
- **PyPI Ready**: Fully configured for PyPI distribution

## Installation

```bash
pip install {package_name}
```

## Development Installation

```bash
git clone https://github.com/openflow/{package_name}.git
cd {package_name}
pip install -e .
```

## Usage

```python
from {package_name} import main

# Use the package
result = main()
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Generated By

This package was automatically generated by the OpenFlow PyPI Package Generator as part of the project model-driven development process.
"""

        with open(package_dir / "README.md", "w") as f:
            f.write(content)

    def _create_init_files(self, package_dir: Path, package_info: dict[str, Any]) -> None:
        """Create __init__.py files for the package"""
        package_name = package_info["package_name"]
        domain_name = package_info["domain"]

        # Create src directory structure
        src_dir = package_dir / "src" / package_name.replace("-", "_")
        src_dir.mkdir(parents=True, exist_ok=True)

        # Main __init__.py
        init_content = f'''"""
{package_name}

OpenFlow {domain_name.replace("_", " ").title()} Package

Generated from project model with package potential score: {package_info["score"]}/10
"""

__version__ = "0.1.0"
__author__ = "OpenFlow Team"
__email__ = "team@openflow.dev"

def main():
    """Main entry point for the package"""
    return f"Hello from {package_name}!"

if __name__ == "__main__":
    print(main())
'''

        with open(src_dir / "__init__.py", "w") as f:
            f.write(init_content)

        # Create a simple main module
        main_content = f'''"""
Main module for {package_name}
"""

def main():
    """Main function"""
    return f"Hello from {package_name}!"

if __name__ == "__main__":
    print(main())
'''

        with open(src_dir / "main.py", "w") as f:
            f.write(main_content)

    def _create_setup_py(self, package_dir: Path, package_info: dict[str, Any]) -> None:
        """Create setup.py for the package"""
        package_name = package_info["package_name"]

        content = f'''#!/usr/bin/env python3
"""
Setup script for {package_name}
"""

from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        name="{package_name}",
        packages=find_packages(where="src"),
        package_dir={{"": "src"}},
    )
'''

        with open(package_dir / "setup.py", "w") as f:
            f.write(content)

    def _create_license(self, package_dir: Path) -> None:
        """Create LICENSE file"""
        license_content = """MIT License

Copyright (c) 2025 OpenFlow Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

        with open(package_dir / "LICENSE", "w") as f:
            f.write(license_content)

    def _create_manifest(self, package_dir: Path) -> None:
        """Create MANIFEST.in file"""
        manifest_content = """include README.md
include LICENSE
include pyproject.toml
recursive-include src *.py
recursive-exclude * __pycache__
recursive-exclude * *.py[co]
"""

        with open(package_dir / "MANIFEST.in", "w") as f:
            f.write(manifest_content)

    def generate_all_packages(self) -> None:
        """Generate all high-scoring packages"""
        high_scoring = self.get_high_scoring_domains()

        if not high_scoring:
            print("❌ No high-scoring domains found")
            return

        print(f"🚀 Generating {len(high_scoring)} PyPI packages...")

        for package_info in high_scoring:
            self.generate_package_structure(package_info)

        print(f"\n✅ Generated {len(high_scoring)} packages in {self.packages_dir}")

        # Create package summary
        self._create_package_summary(high_scoring)

    def _create_package_summary(self, packages: list[dict[str, Any]]) -> None:
        """Create a summary of all generated packages"""
        summary_content = f"""# PyPI Package Generation Summary

Generated {len(packages)} packages from high-scoring domains.

## Package Details

"""

        for package in packages:
            summary_content += f"""### {package["package_name"]}
- **Domain**: {package["domain"]}
- **Score**: {package["score"]}/10
- **PyPI Ready**: {package["pypi_ready"]}
- **Reasons**: {", ".join(package["reasons"]) if package["reasons"] else "High package potential score"}

"""

        summary_content += """## Next Steps

1. **Review Packages**: Examine each generated package
2. **Customize**: Add domain-specific functionality
3. **Test**: Run tests and validation
4. **Publish**: Upload to PyPI when ready

## Generated By

OpenFlow PyPI Package Generator
Part of the project model-driven development process
"""

        with open(self.packages_dir / "PACKAGE_SUMMARY.md", "w") as f:
            f.write(summary_content)

        print(f"📄 Package summary created: {self.packages_dir}/PACKAGE_SUMMARY.md")


def main():
    """Main execution function"""
    generator = PyPIPackageGenerator()

    try:
        generator.load_model()
        generator.generate_all_packages()

        print("\n🎉 PyPI Package Generation Complete!")
        print("📁 Check the 'generated_packages' directory for results")

    except Exception as e:
        print(f"❌ Package generation failed: {e}")


if __name__ == "__main__":
    main()
