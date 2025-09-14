#!/usr/bin/env python3
"""
Comprehensive GitHub Repository Discovery and Analysis Tool

This tool can analyze any GitHub repository URL and provide:
1. Repository structure and metadata
2. File type discovery and classification
3. Schema inference and pattern recognition
4. Quality analysis and recommendations
5. Dependency and ecosystem analysis
"""

import asyncio
import json
import logging
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse

from artifact_forge.agents.artifact_detector import ArtifactDetector, ArtifactInfo
from mcp_integration.github_mcp_client import GitHubMCPClient

# Import our existing tools
sys.path.append(str(Path(__file__).parent.parent / "src"))


@dataclass
class RepositoryAnalysis:
    """Comprehensive analysis of a GitHub repository"""

    repo_url: str
    repo_name: str
    owner: str
    clone_url: str
    analysis_timestamp: str

    # Basic metadata
    description: Optional[str] = None
    language: Optional[str] = None
    stars: Optional[int] = None
    forks: Optional[int] = None
    last_updated: Optional[str] = None

    # Structure analysis
    total_files: int = 0
    total_size: int = 0
    file_types: dict[str, int] = field(default_factory=dict)
    directory_structure: dict[str, Any] = field(default_factory=dict)

    # Artifact discovery
    artifacts: list[ArtifactInfo] = field(default_factory=list)
    artifact_summary: dict[str, Any] = field(default_factory=dict)

    # Schema inference
    detected_schemas: dict[str, Any] = field(default_factory=dict)
    configuration_files: list[str] = field(default_factory=list)
    dependency_files: list[str] = field(default_factory=list)

    # Quality analysis
    quality_score: float = 0.0
    quality_issues: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    # Analysis metadata
    analysis_duration: float = 0.0
    errors: list[str] = field(default_factory=list)


class ComprehensiveGitHubDiscovery:
    """
    Comprehensive GitHub repository discovery and analysis

    This tool provides deep insights into any GitHub repository by:
    1. Cloning and analyzing the repository structure
    2. Discovering and classifying all artifacts
    3. Inferring schemas and patterns
    4. Analyzing quality and providing recommendations
    """

    def __init__(self, workspace_path: str = "."):
        self.workspace_path = Path(workspace_path)
        self.temp_dir = None
        self.artifact_detector = ArtifactDetector()
        self.github_client = GitHubMCPClient()

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def analyze_repository(self, repo_url: str) -> RepositoryAnalysis:
        """
        Comprehensive analysis of a GitHub repository

        Args:
            repo_url: GitHub repository URL (e.g., https://github.com/user/repo)

        Returns:
            RepositoryAnalysis with comprehensive insights
        """
        import time

        start_time = time.time()

        # Parse repository URL
        repo_info = self._parse_github_url(repo_url)
        if not repo_info:
            msg = f"Invalid GitHub URL: {repo_url}"
            raise ValueError(msg)

        # Create analysis object
        analysis = RepositoryAnalysis(
            repo_url=repo_url,
            repo_name=repo_info["repo_name"],
            owner=repo_info["owner"],
            clone_url=repo_info["clone_url"],
            analysis_timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        )

        try:
            # Phase 1: Clone repository
            self.logger.info(f"🔍 Phase 1: Cloning repository {repo_info['repo_name']}")
            clone_path = await self._clone_repository(repo_info["clone_url"])

            # Phase 2: Basic metadata analysis
            self.logger.info("📊 Phase 2: Analyzing repository metadata")
            await self._analyze_metadata(analysis, repo_info)

            # Phase 3: Structure analysis
            self.logger.info("📁 Phase 3: Analyzing repository structure")
            await self._analyze_structure(analysis, clone_path)

            # Phase 4: Artifact discovery
            self.logger.info("🔍 Phase 4: Discovering and classifying artifacts")
            await self._discover_artifacts(analysis, clone_path)

            # Phase 5: Schema inference
            self.logger.info("🧠 Phase 5: Inferring schemas and patterns")
            await self._infer_schemas(analysis, clone_path)

            # Phase 6: Quality analysis
            self.logger.info("⭐ Phase 6: Analyzing quality and generating recommendations")
            await self._analyze_quality(analysis)

        except Exception as e:
            analysis.errors.append(f"Analysis failed: {str(e)}")
            self.logger.error(f"❌ Analysis failed: {e}")

        finally:
            # Cleanup
            if self.temp_dir and self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)

        # Calculate analysis duration
        analysis.analysis_duration = time.time() - start_time

        return analysis

    def _parse_github_url(self, repo_url: str) -> Optional[dict[str, str]]:
        """Parse GitHub URL to extract repository information"""
        try:
            parsed = urlparse(repo_url)
            if parsed.netloc != "github.com":
                return None

            # Extract owner and repo name from path
            path_parts = parsed.path.strip("/").split("/")
            if len(path_parts) < 2:
                return None

            owner = path_parts[0]
            repo_name = path_parts[1]

            # Remove .git suffix if present
            if repo_name.endswith(".git"):
                repo_name = repo_name[:-4]

            # Construct clone URL
            clone_url = f"https://github.com/{owner}/{repo_name}.git"

            return {"owner": owner, "repo_name": repo_name, "clone_url": clone_url}

        except Exception as e:
            self.logger.error(f"Failed to parse GitHub URL: {e}")
            return None

    async def _clone_repository(self, clone_url: str) -> Path:
        """Clone repository to temporary directory"""
        try:
            # Create temporary directory
            self.temp_dir = Path(tempfile.mkdtemp(prefix="github_analysis_"))
            self.logger.info(f"📁 Created temporary directory: {self.temp_dir}")

            # Clone repository
            result = await self._execute_command(f"git clone {clone_url} {self.temp_dir}", cwd=self.temp_dir.parent)

            if not result["success"]:
                msg = f"Failed to clone repository: {result['error']}"
                raise Exception(msg)

            # Find the cloned repository directory
            repo_dirs = [d for d in self.temp_dir.iterdir() if d.is_dir()]
            if not repo_dirs:
                msg = "No repository directory found after cloning"
                raise Exception(msg)

            return repo_dirs[0]

        except Exception as e:
            self.logger.error(f"Failed to clone repository: {e}")
            raise

    async def _analyze_metadata(self, analysis: RepositoryAnalysis, repo_info: dict[str, str]):
        """Analyze basic repository metadata"""
        try:
            # Try to get metadata from GitHub API or MCP
            # For now, we'll use basic information from the URL
            analysis.description = f"Repository: {repo_info['repo_name']} by {repo_info['owner']}"
            analysis.language = "Unknown"  # Will be determined by file analysis

        except Exception as e:
            analysis.errors.append(f"Metadata analysis failed: {str(e)}")
            self.logger.warning(f"Metadata analysis failed: {e}")

    async def _analyze_structure(self, analysis: RepositoryAnalysis, repo_path: Path):
        """Analyze repository structure"""
        try:
            # Get directory structure
            structure = await self._get_directory_structure(repo_path)
            analysis.directory_structure = structure

            # Count files and calculate sizes
            file_count = 0
            total_size = 0
            file_types = {}

            for file_path in repo_path.rglob("*"):
                if file_path.is_file():
                    file_count += 1
                    total_size += file_path.stat().st_size

                    # Count file types
                    suffix = file_path.suffix.lower()
                    if suffix:
                        file_types[suffix] = file_types.get(suffix, 0) + 1
                    else:
                        file_types["no_extension"] = file_types.get("no_extension", 0) + 1

            analysis.total_files = file_count
            analysis.total_size = total_size
            analysis.file_types = file_types

        except Exception as e:
            analysis.errors.append(f"Structure analysis failed: {str(e)}")
            self.logger.warning(f"Structure analysis failed: {e}")

    async def _get_directory_structure(self, repo_path: Path) -> dict[str, Any]:
        """Get directory structure in a tree-like format"""
        structure = {}

        try:
            # Use tree command if available
            result = await self._execute_command("tree -a -I '.git'", cwd=repo_path)
            if result["success"]:
                structure["tree_output"] = result["output"]
                structure["tree_available"] = True
            else:
                # Fallback: manual directory traversal
                structure["tree_available"] = False
                structure["directories"] = self._manual_directory_traversal(repo_path)

        except Exception as e:
            structure["error"] = str(e)

        return structure

    def _manual_directory_traversal(self, repo_path: Path) -> dict[str, Any]:
        """Manual directory traversal when tree command is not available"""
        structure = {}

        for item in repo_path.iterdir():
            if item.name == ".git":
                continue

            if item.is_dir():
                structure[item.name] = {
                    "type": "directory",
                    "contents": self._manual_directory_traversal(item),
                }
            else:
                structure[item.name] = {"type": "file", "size": item.stat().st_size}

        return structure

    async def _discover_artifacts(self, analysis: RepositoryAnalysis, repo_path: Path):
        """Discover and classify artifacts in the repository"""
        try:
            # Use our existing artifact detector
            artifacts = self.artifact_detector.detect_artifacts(str(repo_path))
            analysis.artifacts = artifacts

            # Generate artifact summary
            artifact_summary = {}
            for artifact in artifacts:
                artifact_type = artifact.artifact_type
                if artifact_type not in artifact_summary:
                    artifact_summary[artifact_type] = {
                        "count": 0,
                        "total_size": 0,
                        "files": [],
                    }

                artifact_summary[artifact_type]["count"] += 1
                artifact_summary[artifact_type]["total_size"] += artifact.size
                artifact_summary[artifact_type]["files"].append(artifact.path)

            analysis.artifact_summary = artifact_summary

            # Determine primary language based on artifacts
            if "python" in artifact_summary:
                analysis.language = "Python"
            elif "javascript" in artifact_summary:
                analysis.language = "JavaScript"
            elif "go" in artifact_summary:
                analysis.language = "Go"
            elif "rust" in artifact_summary:
                analysis.language = "Rust"

        except Exception as e:
            analysis.errors.append(f"Artifact discovery failed: {str(e)}")
            self.logger.warning(f"Artifact discovery failed: {e}")

    async def _infer_schemas(self, analysis: RepositoryAnalysis, repo_path: Path):
        """Infer schemas and patterns from repository contents"""
        try:
            # Look for configuration files
            config_files = [
                "pyproject.toml",
                "setup.py",
                "requirements.txt",  # Python
                "package.json",
                "package-lock.json",
                "yarn.lock",  # Node.js
                "go.mod",
                "go.sum",  # Go
                "Cargo.toml",
                "Cargo.lock",  # Rust
                "docker-compose.yml",
                "Dockerfile",  # Docker
                "Makefile",
                "makefile",  # Make
                ".env",
                ".env.example",  # Environment
                "README.md",
                "README.rst",
                "README.txt",  # Documentation
            ]

            for config_file in config_files:
                config_path = repo_path / config_file
                if config_path.exists():
                    analysis.configuration_files.append(config_file)

                    # Analyze specific configuration files
                    if config_file in [
                        "pyproject.toml",
                        "package.json",
                        "go.mod",
                        "Cargo.toml",
                    ]:
                        analysis.dependency_files.append(config_file)
                        await self._analyze_dependency_file(analysis, config_path, config_file)

            # Infer schemas from file patterns
            await self._infer_file_schemas(analysis, repo_path)

        except Exception as e:
            analysis.errors.append(f"Schema inference failed: {str(e)}")
            self.logger.warning(f"Schema inference failed: {e}")

    async def _analyze_dependency_file(self, analysis: RepositoryAnalysis, file_path: Path, file_type: str):
        """Analyze dependency files for insights"""
        try:
            content = file_path.read_text(encoding="utf-8")

            if file_type == "pyproject.toml":
                # Basic TOML parsing for dependencies
                dependencies = re.findall(r'(\w+)\s*=\s*["\']([^"\']+)["\']', content)
                analysis.detected_schemas["python_dependencies"] = {
                    "type": "python",
                    "dependencies": [{"name": name, "version": version} for name, version in dependencies],
                }

            elif file_type == "package.json":
                # Basic JSON parsing for dependencies
                try:
                    data = json.loads(content)
                    deps = data.get("dependencies", {})
                    dev_deps = data.get("devDependencies", {})

                    analysis.detected_schemas["node_dependencies"] = {
                        "type": "node",
                        "dependencies": deps,
                        "dev_dependencies": dev_deps,
                        "scripts": data.get("scripts", {}),
                    }
                except json.JSONDecodeError:
                    pass

        except Exception as e:
            self.logger.warning(f"Failed to analyze {file_type}: {e}")

    async def _infer_file_schemas(self, analysis: RepositoryAnalysis, repo_path: Path):
        """Infer schemas from file patterns and contents"""
        try:
            # Look for common patterns
            patterns = {
                "api_schema": ["*.yaml", "*.yml", "*.json"],  # OpenAPI, etc.
                "database_schema": ["*.sql", "*.db", "*.sqlite"],  # Database files
                "test_files": [
                    "test_*.py",
                    "*_test.py",
                    "*.test.js",
                    "*.spec.js",
                ],  # Test files
                "documentation": ["*.md", "*.rst", "*.txt", "docs/*"],  # Documentation
                "ci_cd": [
                    ".github/*",
                    ".gitlab-ci.yml",
                    ".travis.yml",
                    "Jenkinsfile",
                ],  # CI/CD
                "deployment": [
                    "docker-compose.yml",
                    "kubernetes/*",
                    "terraform/*",
                ],  # Deployment
            }

            for pattern_name, pattern_list in patterns.items():
                matching_files = []
                for pattern in pattern_list:
                    if "*" in pattern:
                        # Handle glob patterns
                        if pattern.startswith("*"):
                            # File pattern
                            for file_path in repo_path.rglob(pattern[1:]):
                                if file_path.is_file():
                                    matching_files.append(str(file_path.relative_to(repo_path)))
                        else:
                            # Directory pattern
                            dir_pattern = pattern.split("/*")[0]
                            dir_path = repo_path / dir_pattern
                            if dir_path.exists():
                                for file_path in dir_path.rglob("*"):
                                    if file_path.is_file():
                                        matching_files.append(str(file_path.relative_to(repo_path)))
                    else:
                        # Exact file
                        file_path = repo_path / pattern
                        if file_path.exists():
                            matching_files.append(pattern)

                if matching_files:
                    analysis.detected_schemas[pattern_name] = {
                        "type": pattern_name,
                        "files": matching_files,
                        "count": len(matching_files),
                    }

        except Exception as e:
            self.logger.warning(f"File schema inference failed: {e}")

    async def _analyze_quality(self, analysis: RepositoryAnalysis):
        """Analyze repository quality and generate recommendations"""
        try:
            quality_score = 0.0
            quality_issues = []
            recommendations = []

            # Check for essential files
            essential_files = ["README.md", "LICENSE", ".gitignore"]
            missing_essential = [f for f in essential_files if f not in analysis.configuration_files]

            if missing_essential:
                quality_issues.append(f"Missing essential files: {', '.join(missing_essential)}")
                recommendations.append(f"Add missing essential files: {', '.join(missing_essential)}")
            else:
                quality_score += 20.0

            # Check documentation
            if "documentation" in analysis.detected_schemas:
                quality_score += 15.0
                doc_count = analysis.detected_schemas["documentation"]["count"]
                if doc_count >= 3:
                    quality_score += 10.0
                elif doc_count >= 1:
                    quality_score += 5.0
            else:
                quality_issues.append("No documentation files detected")
                recommendations.append("Add documentation files (README.md, docs/)")

            # Check for tests
            if "test_files" in analysis.detected_schemas:
                quality_score += 15.0
                test_count = analysis.detected_schemas["test_files"]["count"]
                if test_count >= 5:
                    quality_score += 10.0
                elif test_count >= 1:
                    quality_score += 5.0
            else:
                quality_issues.append("No test files detected")
                recommendations.append("Add test files for better code quality")

            # Check for CI/CD
            if "ci_cd" in analysis.detected_schemas:
                quality_score += 15.0
            else:
                quality_issues.append("No CI/CD configuration detected")
                recommendations.append("Add CI/CD configuration (.github/workflows/, .gitlab-ci.yml)")

            # Check for deployment configuration
            if "deployment" in analysis.detected_schemas:
                quality_score += 15.0
            else:
                quality_issues.append("No deployment configuration detected")
                recommendations.append("Add deployment configuration (Docker, Kubernetes, Terraform)")

            # Check repository size and structure
            if analysis.total_files >= 100:
                quality_score += 10.0
            elif analysis.total_files >= 50:
                quality_score += 5.0

            # Normalize score to 0-100
            quality_score = min(100.0, quality_score)

            analysis.quality_score = quality_score
            analysis.quality_issues = quality_issues
            analysis.recommendations = recommendations

        except Exception as e:
            analysis.errors.append(f"Quality analysis failed: {str(e)}")
            self.logger.warning(f"Quality analysis failed: {e}")

    async def _execute_command(self, command: str, cwd: Optional[Path] = None) -> dict[str, Any]:
        """Execute a shell command and return results"""
        try:
            process = await asyncio.create_subprocess_exec(
                *command.split(),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
            )

            stdout, stderr = await process.communicate()

            return {
                "success": process.returncode == 0,
                "output": stdout.decode("utf-8") if stdout else "",
                "error": stderr.decode("utf-8") if stderr else "",
                "return_code": process.returncode,
            }

        except Exception as e:
            return {"success": False, "output": "", "error": str(e), "return_code": -1}

    def generate_report(self, analysis: RepositoryAnalysis, output_format: str = "markdown") -> str:
        """Generate a comprehensive report from analysis results"""
        if output_format == "markdown":
            return self._generate_markdown_report(analysis)
        if output_format == "json":
            return self._generate_json_report(analysis)
        return self._generate_text_report(analysis)

    def _generate_markdown_report(self, analysis: RepositoryAnalysis) -> str:
        """Generate markdown report"""
        report_lines = [
            f"# GitHub Repository Analysis Report",
            "",
            f"**Repository:** [{analysis.repo_name}]({analysis.repo_url})",
            f"**Owner:** {analysis.owner}",
            f"**Analysis Date:** {analysis.analysis_timestamp}",
            f"**Analysis Duration:** {analysis.analysis_duration:.2f} seconds",
            "",
            "## 📊 Repository Overview",
            "",
        ]

        # Basic metadata
        if analysis.description:
            report_lines.append(f"- **Description:** {analysis.description}")
        if analysis.language:
            report_lines.append(f"- **Primary Language:** {analysis.language}")

        report_lines.extend(
            [
                f"- **Total Files:** {analysis.total_files:,}",
                f"- **Total Size:** {analysis.total_size / 1024 / 1024:.2f} MB",
                f"- **Quality Score:** {analysis.quality_score:.1f}/100",
                "",
            ]
        )

        # File types
        report_lines.append("## 📁 File Types")
        report_lines.append("")
        for file_type, count in sorted(analysis.file_types.items(), key=lambda x: x[1], reverse=True)[:10]:
            report_lines.append(f"- **{file_type}:** {count:,} files")
        report_lines.append("")

        # Artifacts
        if analysis.artifact_summary:
            report_lines.append("## 🔍 Artifact Discovery")
            report_lines.append("")
            for artifact_type, info in analysis.artifact_summary.items():
                report_lines.append(f"### {artifact_type.title()}")
                report_lines.append(f"- **Count:** {info['count']}")
                report_lines.append(f"- **Total Size:** {info['total_size'] / 1024:.2f} KB")
                report_lines.append("")

        # Schemas
        if analysis.detected_schemas:
            report_lines.append("## 🧠 Detected Schemas")
            report_lines.append("")
            for schema_name, schema_info in analysis.detected_schemas.items():
                report_lines.append(f"### {schema_name.replace('_', ' ').title()}")
                report_lines.append(f"- **Type:** {schema_info['type']}")
                if "count" in schema_info:
                    report_lines.append(f"- **Count:** {schema_info['count']}")
                if "files" in schema_info:
                    report_lines.append(f"- **Files:** {', '.join(schema_info['files'][:5])}")
                    if len(schema_info["files"]) > 5:
                        report_lines.append(f"  - *... and {len(schema_info['files']) - 5} more*")
                report_lines.append("")

        # Quality analysis
        report_lines.append("## ⭐ Quality Analysis")
        report_lines.append("")
        report_lines.append(f"**Overall Score:** {analysis.quality_score:.1f}/100")
        report_lines.append("")

        if analysis.quality_issues:
            report_lines.append("### Issues Found")
            for issue in analysis.quality_issues:
                report_lines.append(f"- ❌ {issue}")
            report_lines.append("")

        if analysis.recommendations:
            report_lines.append("### Recommendations")
            for rec in analysis.recommendations:
                report_lines.append(f"- 💡 {rec}")
            report_lines.append("")

        # Errors
        if analysis.errors:
            report_lines.append("## ⚠️ Analysis Errors")
            report_lines.append("")
            for error in analysis.errors:
                report_lines.append(f"- ⚠️ {error}")
            report_lines.append("")

        return "\n".join(report_lines)

    def _generate_json_report(self, analysis: RepositoryAnalysis) -> str:
        """Generate JSON report"""
        # Convert dataclass to dict for JSON serialization
        analysis_dict = {
            "repo_url": analysis.repo_url,
            "repo_name": analysis.repo_name,
            "owner": analysis.owner,
            "clone_url": analysis.clone_url,
            "analysis_timestamp": analysis.analysis_timestamp,
            "description": analysis.description,
            "language": analysis.language,
            "total_files": analysis.total_files,
            "total_size": analysis.total_size,
            "file_types": analysis.file_types,
            "artifact_summary": analysis.artifact_summary,
            "detected_schemas": analysis.detected_schemas,
            "configuration_files": analysis.configuration_files,
            "dependency_files": analysis.dependency_files,
            "quality_score": analysis.quality_score,
            "quality_issues": analysis.quality_issues,
            "recommendations": analysis.recommendations,
            "analysis_duration": analysis.analysis_duration,
            "errors": analysis.errors,
        }

        return json.dumps(analysis_dict, indent=2)

    def _generate_text_report(self, analysis: RepositoryAnalysis) -> str:
        """Generate plain text report"""
        report_lines = [
            "GitHub Repository Analysis Report",
            "=" * 50,
            "",
            f"Repository: {analysis.repo_name}",
            f"URL: {analysis.repo_url}",
            f"Owner: {analysis.owner}",
            f"Analysis Date: {analysis.analysis_timestamp}",
            f"Quality Score: {analysis.quality_score:.1f}/100",
            "",
            f"Total Files: {analysis.total_files:,}",
            f"Total Size: {analysis.total_size / 1024 / 1024:.2f} MB",
            "",
        ]

        # File types
        report_lines.append("File Types:")
        for file_type, count in sorted(analysis.file_types.items(), key=lambda x: x[1], reverse=True)[:10]:
            report_lines.append(f"  {file_type}: {count:,}")

        report_lines.append("")

        # Quality issues
        if analysis.quality_issues:
            report_lines.append("Quality Issues:")
            for issue in analysis.quality_issues:
                report_lines.append(f"  - {issue}")
            report_lines.append("")

        # Recommendations
        if analysis.recommendations:
            report_lines.append("Recommendations:")
            for rec in analysis.recommendations:
                report_lines.append(f"  - {rec}")

        return "\n".join(report_lines)


async def main():
    """Main entry point for the comprehensive GitHub discovery tool"""
    import argparse

    parser = argparse.ArgumentParser(description="Comprehensive GitHub Repository Discovery and Analysis")
    parser.add_argument("repo_url", help="GitHub repository URL to analyze")
    parser.add_argument(
        "--output",
        choices=["markdown", "json", "text"],
        default="markdown",
        help="Output format",
    )
    parser.add_argument("--save-report", help="Save report to file")

    args = parser.parse_args()

    # Create discovery tool
    discovery = ComprehensiveGitHubDiscovery()

    print(f"🔍 Comprehensive GitHub Repository Analysis")
    print(f"📁 Repository: {args.repo_url}")
    print(f"⏱️  Starting analysis...")
    print()

    try:
        # Analyze repository
        analysis = await discovery.analyze_repository(args.repo_url)

        # Generate report
        report = discovery.generate_report(analysis, args.output)

        # Output report
        if args.save_report:
            with open(args.save_report, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"✅ Report saved to: {args.save_report}")
        else:
            print(report)

        # Summary
        print(f"\n📊 Analysis Complete!")
        print(f"   Repository: {analysis.repo_name}")
        print(f"   Files: {analysis.total_files:,}")
        print(f"   Quality Score: {analysis.quality_score:.1f}/100")
        print(f"   Duration: {analysis.analysis_duration:.2f}s")

        if analysis.errors:
            print(f"   Errors: {len(analysis.errors)}")

    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
