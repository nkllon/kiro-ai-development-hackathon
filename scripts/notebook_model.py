#!/usr/bin/env python3
"""
📊 Structured Notebook Model Generator

Uses JSON modeling instead of string manipulation for notebook generation.
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class ImportStatement:
    """Structured import statement"""

    statement_type: str  # "import" or "from"
    module: str
    alias: Optional[str] = None
    submodules: Optional[list[str]] = None


@dataclass
class CodeCell:
    """Structured code cell"""

    cell_type: str = "code"
    execution_count: Optional[int] = None
    metadata: dict[str, Any] = None
    outputs: list[dict[str, Any]] = None
    source: list[str] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}
        if self.outputs is None:
            self.outputs = []
        if self.source is None:
            self.source = []


@dataclass
class MarkdownCell:
    """Structured markdown cell"""

    cell_type: str = "markdown"
    metadata: dict[str, Any] = None
    source: list[str] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}
        if self.source is None:
            self.source = []


@dataclass
class NotebookModel:
    """Structured notebook model"""

    cells: list[dict[str, Any]]
    metadata: dict[str, Any]
    nbformat: int = 4
    nbformat_minor: int = 4

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(asdict(self), indent=2)


class NotebookBuilder:
    """Structured notebook builder using JSON modeling"""

    def __init__(self):
        self.cells = []
        self.metadata = {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.8.5",
            },
        }

    def add_imports_cell(self, imports: list[ImportStatement]) -> None:
        """Add imports cell using structured data"""
        source_lines = []

        # Convert structured imports to code
        for imp in imports:
            if imp.statement_type == "import":
                if imp.alias:
                    source_lines.append(f"import {imp.module} as {imp.alias}")
                else:
                    source_lines.append(f"import {imp.module}")
            elif imp.statement_type == "from":
                if imp.submodules:
                    modules_str = ", ".join(imp.submodules)
                    source_lines.append(f"from {imp.module} import {modules_str}")
                else:
                    source_lines.append(f"from {imp.module} import {imp.alias}")

        source_lines.append("")
        source_lines.append("print('✅ Libraries loaded')")

        cell = CodeCell(source=source_lines)
        self.cells.append(asdict(cell))

    def add_markdown_cell(self, title: str, content: list[str]) -> None:
        """Add markdown cell using structured data"""
        source_lines = [f"# {title}"] + content
        cell = MarkdownCell(source=source_lines)
        self.cells.append(asdict(cell))

    def add_code_cell(self, code_lines: list[str]) -> None:
        """Add code cell using structured data"""
        cell = CodeCell(source=code_lines)
        self.cells.append(asdict(cell))

    def build_notebook(self) -> NotebookModel:
        """Build the complete notebook model"""
        return NotebookModel(cells=self.cells, metadata=self.metadata)


def create_gemini_notebook() -> str:
    """Create Gemini notebook using structured JSON modeling"""

    # Define imports as structured data
    imports = [
        ImportStatement("import", "json"),
        ImportStatement("import", "os"),
        ImportStatement("import", "subprocess"),
        ImportStatement("import", "sys"),
        ImportStatement("from", "datetime", submodules=["datetime"]),
        ImportStatement("from", "pathlib", submodules=["Path"]),
        ImportStatement("from", "typing", submodules=["Dict", "Any", "Optional"]),
        ImportStatement("import", "pandas", "pd"),
        ImportStatement("import", "numpy", "np"),
        ImportStatement("import", "matplotlib.pyplot", "plt"),
        ImportStatement("import", "seaborn", "sns"),
        ImportStatement("import", "plotly.express", "px"),
        ImportStatement("import", "plotly.graph_objects", "go"),
        ImportStatement("from", "plotly.subplots", submodules=["make_subplots"]),
        ImportStatement(
            "from",
            "langchain_core.output_parsers",
            submodules=["JsonOutputParser"],
        ),
        ImportStatement(
            "from",
            "langchain_core.prompts",
            submodules=["ChatPromptTemplate"],
        ),
        ImportStatement(
            "from",
            "langchain_google_genai",
            submodules=["ChatGoogleGenerativeAI"],
        ),
        ImportStatement("from", "langgraph.graph", submodules=["StateGraph", "END"]),
        ImportStatement("from", "langchain_core.tools", submodules=["tool"]),
    ]

    # Build notebook using structured approach
    builder = NotebookBuilder()

    # Add header
    builder.add_markdown_cell(
        "🤖 Gemini GCP Billing Analysis with LangGraph/LangChain",
        [
            "",
            "**Generated**: 2025-08-07 08:30:00",
            "**Project**: aardvark-linkedin-grepper",
            "**Billing Account**: 01F112-E73FD5-795507",
            "",
            "This notebook uses Gemini LLM with LangGraph/LangChain to analyze your GCP billing data.",
        ],
    )

    # Add imports cell
    builder.add_imports_cell(imports)

    # Add data loading cell
    builder.add_code_cell(
        [
            "# Load billing data",
            "data_dir = Path('data/billing_reports/analysis_data')",
            "",
            "# Load daily data",
            "daily_data = pd.read_csv(data_dir / 'daily_billing_data.csv')",
            "print(f'📊 Loaded {len(daily_data)} days of billing data')",
            "",
            "# Display first few rows",
            "daily_data.head()",
        ],
    )

    # Build and return JSON
    notebook = builder.build_notebook()
    return notebook.to_json()


if __name__ == "__main__":
    # Generate notebook JSON
    notebook_json = create_gemini_notebook()

    # Save to file
    output_path = Path(
        "data/billing_reports/analysis_data/gemini_billing_analysis.ipynb",
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        f.write(notebook_json)

    print(f"✅ Notebook saved: {output_path}")
    print("📊 Using structured JSON modeling instead of string manipulation!")
