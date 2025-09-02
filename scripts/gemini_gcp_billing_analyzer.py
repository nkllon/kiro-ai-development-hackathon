#!/usr/bin/env python3
"""
🤖 Gemini GCP Billing Analyzer with LangGraph/LangChain

Uses Gemini LLM to analyze GCP billing data with 1Password credential management.
Creates a comprehensive Jupyter notebook with the analysis.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import pandas as pd

# LangChain imports
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph


class GeminiGCPBillingAnalyzer:
    """Gemini-powered GCP billing analyzer using LangGraph/LangChain"""

    def __init__(self):
        self.project_id = None
        self.billing_account = None
        self.gemini_api_key = None
        self.analysis_data = {}
        self.notebook_content = ""

    def get_1password_credential(
        self,
        item_name: str,
        field_name: str = "credential",
    ) -> Optional[str]:
        """Get credential from 1Password using established patterns"""
        try:
            result = subprocess.run(
                ["op", "item", "get", item_name, "--fields", field_name, "--reveal"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def setup_credentials(self) -> bool:
        """Setup Gemini API credentials from 1Password"""
        print("🔐 Setting up Gemini API credentials...")

        # Try different possible item names for Google/Gemini API key
        possible_items = [
            "Google API Key",
            "Gemini API Key",
            "Google AI API Key",
            "GOOGLE_API_KEY",
            "GEMINI_API_KEY",
        ]

        for item_name in possible_items:
            api_key = self.get_1password_credential(item_name)
            if api_key:
                self.gemini_api_key = api_key
                print(f"✅ Found Gemini API key in '{item_name}'")
                os.environ["GOOGLE_API_KEY"] = api_key
                return True

        print("❌ Could not find Gemini API key in 1Password")
        print("💡 Try creating an item named 'Google API Key' or 'Gemini API Key'")
        return False

    def get_project_info(self) -> dict[str, str]:
        """Get GCP project information"""
        try:
            result = subprocess.run(
                ["gcloud", "config", "get-value", "project"],
                capture_output=True,
                text=True,
                check=True,
            )
            self.project_id = result.stdout.strip()

            # Get billing account
            result = subprocess.run(
                ["gcloud", "billing", "accounts", "list", "--format=value(name)"],
                capture_output=True,
                text=True,
                check=True,
            )
            self.billing_account = result.stdout.strip().split("\n")[0] if result.stdout.strip() else None

            return {
                "project_id": self.project_id,
                "billing_account": self.billing_account,
            }
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to get project info: {e}")
            return {}

    def load_billing_data(self) -> dict[str, Any]:
        """Load the billing data from our generated files"""
        data_dir = Path("data/billing_reports/analysis_data")

        if not data_dir.exists():
            print("❌ Billing data directory not found")
            return {}

        data = {}

        # Load CSV data
        csv_file = data_dir / "daily_billing_data.csv"
        if csv_file.exists():
            data["daily_data"] = pd.read_csv(csv_file)
            print(f"✅ Loaded daily billing data: {len(data['daily_data'])} records")

        # Load summary data
        summary_file = data_dir / "daily_summary.csv"
        if summary_file.exists():
            data["summary_data"] = pd.read_csv(summary_file)
            print(f"✅ Loaded summary data: {len(data['summary_data'])} records")

        # Load JSON data
        json_file = data_dir / "daily_billing_data.json"
        if json_file.exists():
            with open(json_file) as f:
                data["json_data"] = json.load(f)
            print("✅ Loaded JSON billing data")

        return data

    def create_langgraph_workflow(self) -> StateGraph:
        """Create LangGraph workflow for billing analysis"""

        # Define the state
        class AnalysisState:
            def __init__(self):
                self.billing_data = {}
                self.project_info = {}
                self.analysis_results = {}
                self.recommendations = []
                self.cost_breakdown = {}
                self.trends = {}
                self.anomalies = []

        # Initialize LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=self.gemini_api_key,
            temperature=0.1,
        )

        # Define tools
        @tool
        def analyze_cost_trends(billing_data: dict) -> dict:
            """Analyze cost trends and patterns in billing data"""
            prompt = ChatPromptTemplate.from_template(
                """
            Analyze the following GCP billing data for cost trends and patterns:

            {billing_data}

            Provide analysis in JSON format with:
            - overall_trend (increasing/decreasing/stable)
            - daily_average_cost
            - highest_cost_day
            - lowest_cost_day
            - cost_variance
            - seasonal_patterns
            - unusual_spikes
            """,
            )

            chain = prompt | llm | JsonOutputParser()
            return chain.invoke({"billing_data": json.dumps(billing_data)})

        @tool
        def identify_cost_optimization_opportunities(billing_data: dict) -> dict:
            """Identify specific cost optimization opportunities"""
            prompt = ChatPromptTemplate.from_template(
                """
            Analyze the following GCP billing data to identify cost optimization opportunities:

            {billing_data}

            Provide analysis in JSON format with:
            - high_cost_services (list of services with highest costs)
            - underutilized_resources (services that might be over-provisioned)
            - optimization_recommendations (specific actions to reduce costs)
            - potential_savings (estimated monthly savings)
            - quick_wins (easy fixes that can be implemented immediately)
            """,
            )

            chain = prompt | llm | JsonOutputParser()
            return chain.invoke({"billing_data": json.dumps(billing_data)})

        @tool
        def analyze_service_usage_patterns(billing_data: dict) -> dict:
            """Analyze usage patterns for different GCP services"""
            prompt = ChatPromptTemplate.from_template(
                """
            Analyze the usage patterns for different GCP services in this billing data:

            {billing_data}

            Provide analysis in JSON format with:
            - service_usage_trends (how each service usage changes over time)
            - service_cost_efficiency (cost per usage unit for each service)
            - service_correlations (which services are used together)
            - peak_usage_times (when services are used most)
            - idle_resources (services that might be running unnecessarily)
            """,
            )

            chain = prompt | llm | JsonOutputParser()
            return chain.invoke({"billing_data": json.dumps(billing_data)})

        @tool
        def generate_cost_forecast(billing_data: dict) -> dict:
            """Generate cost forecast based on historical data"""
            prompt = ChatPromptTemplate.from_template(
                """
            Based on the following GCP billing data, generate a cost forecast:

            {billing_data}

            Provide analysis in JSON format with:
            - next_month_forecast (predicted cost for next month)
            - forecast_confidence (high/medium/low)
            - forecast_factors (what drives the forecast)
            - seasonal_adjustments (accounting for seasonal patterns)
            - growth_trends (if costs are growing and why)
            """,
            )

            chain = prompt | llm | JsonOutputParser()
            return chain.invoke({"billing_data": json.dumps(billing_data)})

        # Create the workflow
        workflow = StateGraph(AnalysisState)

        # Add nodes
        workflow.add_node("analyze_trends", analyze_cost_trends)
        workflow.add_node(
            "identify_optimizations",
            identify_cost_optimization_opportunities,
        )
        workflow.add_node("analyze_usage", analyze_service_usage_patterns)
        workflow.add_node("generate_forecast", generate_cost_forecast)

        # Define edges
        workflow.set_entry_point("analyze_trends")
        workflow.add_edge("analyze_trends", "identify_optimizations")
        workflow.add_edge("identify_optimizations", "analyze_usage")
        workflow.add_edge("analyze_usage", "generate_forecast")
        workflow.add_edge("generate_forecast", END)

        return workflow.compile()

    def create_analysis_notebook(self, analysis_results: dict[str, Any]) -> str:
        """Create a comprehensive Jupyter notebook with the analysis"""

        # Create notebook content with proper escaping
        generated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        project_id = self.project_id or "Unknown"
        billing_account = self.billing_account or "Unknown"

        # Build notebook content as a dictionary
        notebook_dict = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "# 🤖 Gemini GCP Billing Analysis\n",
                        "\n",
                        f"**Generated**: {generated_time}\n",
                        f"**Project**: {project_id}\n",
                        f"**Billing Account**: {billing_account}\n",
                        "\n",
                        "This notebook contains comprehensive analysis of your GCP billing data using Gemini LLM.",
                    ],
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": ["## 📊 Data Loading and Setup"],
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "import pandas as pd\n",
                        "import numpy as np\n",
                        "import matplotlib.pyplot as plt\n",
                        "import seaborn as sns\n",
                        "import plotly.express as px\n",
                        "import plotly.graph_objects as go\n",
                        "from plotly.subplots import make_subplots\n",
                        "import json\n",
                        "from pathlib import Path\n",
                        "\n",
                        "# Set up plotting\n",
                        "plt.style.use('seaborn-v0_8')\n",
                        'sns.set_palette("husl")\n',
                        "\n",
                        "print('✅ Libraries loaded')",
                    ],
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Load billing data\n",
                        "data_dir = Path('data/billing_reports/analysis_data')\n",
                        "\n",
                        "# Load daily data\n",
                        "daily_data = pd.read_csv(data_dir / 'daily_billing_data.csv')\n",
                        "print(f'📊 Loaded {len(daily_data)} days of billing data')\n",
                        "\n",
                        "# Load summary data\n",
                        "summary_data = pd.read_csv(data_dir / 'daily_summary.csv')\n",
                        "print(f'📋 Loaded summary data')\n",
                        "\n",
                        "# Display first few rows\n",
                        "daily_data.head()",
                    ],
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": ["## 🤖 Gemini LLM Analysis Results"],
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Load Gemini analysis results\n",
                        f"analysis_results = {json.dumps(analysis_results, indent=2)}\n",
                        "\n",
                        "print('🤖 Gemini Analysis Results:')\n",
                        "print('=' * 50)",
                    ],
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": ["### 📈 Cost Trends Analysis"],
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Display cost trends\n",
                        "if 'analyze_trends' in analysis_results:\n",
                        "    trends = analysis_results['analyze_trends']\n",
                        "    print(f\"📈 Overall Trend: {trends.get('overall_trend', 'Unknown')}\")\n",
                        "    print(f\"💰 Daily Average Cost: ${trends.get('daily_average_cost', 0):.2f}\")\n",
                        "    print(f\"📊 Cost Variance: {trends.get('cost_variance', 'Unknown')}\")\n",
                        "    print(f\"🔍 Unusual Spikes: {trends.get('unusual_spikes', [])}\")\n",
                        "else:\n",
                        "    print('❌ No trend analysis available')",
                    ],
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": ["### 💰 Cost Optimization Opportunities"],
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Display optimization opportunities\n",
                        "if 'identify_optimizations' in analysis_results:\n",
                        "    optimizations = analysis_results['identify_optimizations']\n",
                        "    \n",
                        "    print('🔍 High Cost Services:')\n",
                        "    for service in optimizations.get('high_cost_services', []):\n",
                        '        print(f"  - {service}")\n',
                        "    \n",
                        "    print('\\n💡 Optimization Recommendations:')\n",
                        "    for rec in optimizations.get('optimization_recommendations', []):\n",
                        '        print(f"  - {rec}")\n',
                        "    \n",
                        "    print( \
    f\"\\n💰 Potential Monthly Savings: ${optimizations.get('potential_savings', 0):.2f}\")\n",
                        "    \n",
                        "    print('🚀 Quick Wins:')\n",
                        "    for win in optimizations.get('quick_wins', []):\n",
                        '        print(f"  - {win}")\n',
                        "else:\n",
                        "    print('❌ No optimization analysis available')",
                    ],
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": ["### 📊 Service Usage Patterns"],
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Display service usage patterns\n",
                        "if 'analyze_usage' in analysis_results:\n",
                        "    usage = analysis_results['analyze_usage']\n",
                        "    \n",
                        "    print('📈 Service Usage Trends:')\n",
                        "    for trend in usage.get('service_usage_trends', []):\n",
                        '        print(f"  - {trend}")\n',
                        "    \n",
                        "    print('\\n⚡ Peak Usage Times:')\n",
                        "    for time in usage.get('peak_usage_times', []):\n",
                        '        print(f"  - {time}")\n',
                        "    \n",
                        "    print('\\n💤 Idle Resources:')\n",
                        "    for resource in usage.get('idle_resources', []):\n",
                        '        print(f"  - {resource}")\n',
                        "else:\n",
                        "    print('❌ No usage analysis available')",
                    ],
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": ["### 🔮 Cost Forecast"],
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Display cost forecast\n",
                        "if 'generate_forecast' in analysis_results:\n",
                        "    forecast = analysis_results['generate_forecast']\n",
                        "    \n",
                        "    print( \
    f\"🔮 Next Month Forecast: ${forecast.get('next_month_forecast', 0):.2f}\")\n",
                        "    print( \
    f\"📊 Forecast Confidence: {forecast.get('forecast_confidence', 'Unknown')}\")\n",
                        "    print(f\"📈 Growth Trend: {forecast.get('growth_trends', 'Unknown')}\")\n",
                        "    \n",
                        "    print('\\n📋 Forecast Factors:')\n",
                        "    for factor in forecast.get('forecast_factors', []):\n",
                        '        print(f"  - {factor}")\n',
                        "else:\n",
                        "    print('❌ No forecast available')",
                    ],
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": ["## 📊 Interactive Visualizations"],
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Create interactive cost trend visualization\n",
                        "fig = px.line(daily_data, x='date', y='total_cost', \n",
                        "              title='Daily GCP Cost Trend',\n",
                        "              labels={'total_cost': 'Cost ($)', 'date': 'Date'})\n",
                        "fig.update_layout(\n",
                        "    xaxis_title='Date',\n",
                        "    yaxis_title='Cost ($)',\n",
                        "    hovermode='x unified'\n",
                        ")\n",
                        "fig.show()",
                    ],
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Create service breakdown visualization\n",
                        "service_columns  = \
     [col for col in daily_data.columns if col not in ['date', 'total_cost']]\n",
                        "\n",
                        "# Calculate total cost per service\n",
                        "service_totals = daily_data[service_columns].sum().sort_values(ascending=False)\n",
                        "\n",
                        "fig = px.pie(values=service_totals.values, names=service_totals.index,\n",
                        "              title='GCP Service Cost Breakdown')\n",
                        "fig.update_traces(textposition='inside', textinfo='percent+label')\n",
                        "fig.show()",
                    ],
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Create heatmap of service costs over time\n",
                        "heatmap_data = daily_data.set_index('date')[service_columns].T\n",
                        "\n",
                        "fig = px.imshow(heatmap_data, \n",
                        "                title='Service Cost Heatmap Over Time',\n",
                        "                labels={'x': 'Date', 'y': 'Service', 'color': 'Cost ($)'},\n",
                        "                aspect='auto')\n",
                        "fig.update_layout(\n",
                        "    xaxis_title='Date',\n",
                        "    yaxis_title='Service'\n",
                        ")\n",
                        "fig.show()",
                    ],
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": ["## 🎯 Action Items and Recommendations"],
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Generate action items based on analysis\n",
                        "print('🎯 Recommended Actions:')\n",
                        "print('=' * 30)\n",
                        "\n",
                        "if 'identify_optimizations' in analysis_results:\n",
                        "    optimizations = analysis_results['identify_optimizations']\n",
                        "    \n",
                        "    print('\\n🚀 Immediate Actions (Quick Wins):')\n",
                        "    for i, win in enumerate(optimizations.get('quick_wins', []), 1):\n",
                        '        print(f"{i}. {win}")\n',
                        "    \n",
                        "    print('\\n💡 Strategic Optimizations:')\n",
                        "    for i, rec in enumerate( \
    optimizations.get('optimization_recommendations', []), 1):\n",
                        '        print(f"{i}. {rec}")\n',
                        "    \n",
                        "    print( \
    f\"\\n💰 Expected Monthly Savings: ${optimizations.get('potential_savings', 0):.2f}\")\n",
                        "else:\n",
                        "    print('❌ No optimization recommendations available')",
                    ],
                },
                {"cell_type": "markdown", "metadata": {}, "source": ["## 📝 Summary"]},
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "print('📊 Analysis Summary:')\n",
                        "print('=' * 20)\n",
                        'print( \
    f\'📅 Analysis Period: {daily_data["date"].min()} to {daily_data["date"].max()}\')\n',
                        "print(f'💰 Total Cost: ${daily_data[\"total_cost\"].sum():.2f}')\n",
                        "print(f'📈 Average Daily Cost: ${daily_data[\"total_cost\"].mean():.2f}')\n",
                        "print(f'🔍 Services Analyzed: {len(service_columns)}')\n",
                        "print(f'🤖 Analysis Method: Gemini LLM with LangGraph/LangChain')\n",
                        "\n",
                        "print('\\n✅ Analysis complete! Use the insights above to optimize your GCP costs.')",
                    ],
                },
            ],
            "metadata": {
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
            },
            "nbformat": 4,
            "nbformat_minor": 4,
        }

        # Convert to JSON string
        return json.dumps(notebook_dict, indent=2)

    def run_analysis(self) -> bool:
        """Run the complete Gemini analysis workflow"""
        print("🤖 Gemini GCP Billing Analyzer")
        print("=" * 50)

        # Setup credentials
        if not self.setup_credentials():
            return False

        # Get project info
        project_info = self.get_project_info()
        if not project_info:
            print("❌ Failed to get project information")
            return False

        print(f"✅ Project: {project_info['project_id']}")
        print(f"✅ Billing Account: {project_info['billing_account']}")

        # Load billing data
        billing_data = self.load_billing_data()
        if not billing_data:
            print("❌ Failed to load billing data")
            return False

        print("✅ Billing data loaded successfully")

        # Create and run LangGraph workflow
        try:
            workflow = self.create_langgraph_workflow()

            # Prepare initial state
            initial_state = {"billing_data": billing_data, "project_info": project_info}

            print("🤖 Running Gemini analysis with LangGraph...")
            result = workflow.invoke(initial_state)

            # Extract results
            analysis_results = {}
            for node_name, node_result in result.items():
                if isinstance(node_result, dict):
                    analysis_results[node_name] = node_result

            print("✅ Gemini analysis completed")

            # Create notebook
            notebook_content = self.create_analysis_notebook(analysis_results)

            # Save notebook
            notebook_path = Path(
                "data/billing_reports/analysis_data/gemini_billing_analysis.ipynb",
            )
            notebook_path.parent.mkdir(parents=True, exist_ok=True)

            with open(notebook_path, "w") as f:
                f.write(notebook_content)

            print(f"📓 Notebook saved: {notebook_path}")

            # Save analysis results
            results_path = Path(
                "data/billing_reports/analysis_data/gemini_analysis_results.json",
            )
            with open(results_path, "w") as f:
                json.dump(analysis_results, f, indent=2)

            print(f"📊 Analysis results saved: {results_path}")

            return True

        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return False

    def launch_notebook(self) -> bool:
        """Launch Jupyter notebook with the analysis"""
        try:
            notebook_path = Path(
                "data/billing_reports/analysis_data/gemini_billing_analysis.ipynb",
            )

            if not notebook_path.exists():
                print("❌ Notebook not found. Run analysis first.")
                return False

            print("🚀 Launching Jupyter notebook with Gemini analysis...")
            print(f"📓 Notebook: {notebook_path.absolute()}")
            print("🌐 Jupyter will be available at: http://localhost:8888")

            # Launch Jupyter
            result = subprocess.run(
                ["jupyter", "notebook", "--no-browser", "--port=8888"],
                cwd=notebook_path.parent,
            )

            return result.returncode == 0

        except Exception as e:
            print(f"❌ Failed to launch notebook: {e}")
            return False


def main():
    """Main function to run Gemini analysis"""
    analyzer = GeminiGCPBillingAnalyzer()

    # Run analysis
    if analyzer.run_analysis():
        print("\n✅ Gemini analysis completed successfully!")
        print("\n🎯 Next steps:")
        print(
            "1. Open the notebook: data/billing_reports/analysis_data/gemini_billing_analysis.ipynb",
        )
        print("2. Run all cells to see the analysis")
        print("3. Use the insights to optimize your GCP costs")

        # Ask if user wants to launch notebook
        response = input("\n🚀 Launch Jupyter notebook now? (y/n): ")
        if response.lower() in ["y", "yes"]:
            analyzer.launch_notebook()
    else:
        print("\n❌ Analysis failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
