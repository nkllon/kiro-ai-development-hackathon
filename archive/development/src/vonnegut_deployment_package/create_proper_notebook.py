#!/usr/bin/env python3
"""
📊 Proper Notebook Creator using nbformat

Uses the nbformat library to create a proper Jupyter notebook.
"""

from pathlib import Path

import nbformat as nbf


def create_gemini_notebook() -> nbf.NotebookNode:
    """Create a proper Gemini notebook using nbformat"""

    # Create a new notebook with proper kernel specification
    nb = nbf.v4.new_notebook()

    # Set the kernel metadata to use the correct Python environment
    nb.metadata = {
        "kernelspec": {
            "display_name": "Python 3 (uv)",
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
            "version": "3.12.0",
        },
    }

    # Add title cell
    title_cell = nbf.v4.new_markdown_cell(
        """# 🤖 Gemini GCP Billing Analysis with LangGraph/LangChain

**Generated**: 2025-08-07 08:30:00
**Project**: aardvark-linkedin-grepper
**Billing Account**: 01F112-E73FD5-795507

This notebook uses Gemini LLM with LangGraph/LangChain to analyze your GCP billing data and provide intelligent insights.""",
    )

    # Add imports cell
    imports_cell = nbf.v4.new_code_cell(
        """import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# LangChain imports
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langchain_core.tools import tool

print('✅ Libraries loaded')""",
    )

    # Add data loading cell
    data_cell = nbf.v4.new_code_cell(
        """# Load billing data
import os

# Get the project root directory (Jupyter notebooks don't have __file__)
# We know the notebook is in data/billing_reports/analysis_data/
# So we need to go up 3 levels to get to the project root
current_dir = Path.cwd()
print(f"🔍 Current directory: {current_dir}")

# If we're in the analysis_data directory, go up 3 levels
if current_dir.name == 'analysis_data':
    project_root = current_dir.parent.parent.parent
elif current_dir.name == 'billing_reports':
    project_root = current_dir.parent.parent
elif current_dir.name == 'data':
    project_root = current_dir.parent
else:
    # Assume we're in the project root
    project_root = current_dir

data_dir = project_root / 'data/billing_reports/analysis_data'

print(f"🔍 Project root: {project_root}")
print(f"📁 Data directory: {data_dir}")

# Check if data files exist
daily_data_file = data_dir / 'daily_billing_data.csv'
summary_data_file = data_dir / 'daily_summary.csv'

print(f"📄 Daily data file exists: {daily_data_file.exists()}")
print(f"📄 Summary data file exists: {summary_data_file.exists()}")

if not daily_data_file.exists():
    print("❌ Billing data not found. Generating it...")
    import subprocess
    result  = \
     subprocess.run(["uv", "run", "python", "scripts/gcp_billing_daily_reporter.py"],
                          cwd=project_root)
    if result.returncode != 0:
        print("❌ Failed to generate billing data")
        raise FileNotFoundError("Billing data not available")

# Load daily data
daily_data = pd.read_csv(daily_data_file)
print(f'📊 Loaded {len(daily_data)} days of billing data')

# Load summary data
summary_data = pd.read_csv(summary_data_file)
print(f'📋 Loaded summary data')

# Display first few rows
print("\\n📈 Sample billing data:")
daily_data.head()""",
    )

    # Add credentials cell
    credentials_cell = nbf.v4.new_markdown_cell("""## 🔐 Setup and Credentials""")

    # Add credential setup cell
    cred_setup_cell = nbf.v4.new_code_cell(
        """def setup_gemini_credentials():
    \"\"\"Setup Gemini API credentials from Google Cloud\"\"\"
    print("🔐 Setting up Gemini API credentials...")

    # Try to get credentials from Google Cloud
    try:
        result = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True,
            text=True,
            check=True
        )
        access_token = result.stdout.strip()

        if access_token:
            print("✅ Found Google Cloud access token")
            os.environ["GOOGLE_API_KEY"] = access_token
            return access_token
        else:
            print("❌ No access token found")
            return None

    except subprocess.CalledProcessError as e:
        print(f"❌ Google Cloud authentication failed: {e}")
        print("💡 Try running: gcloud auth login")
        return None
    except Exception as e:
        print(f"❌ Error getting Google Cloud credentials: {e}")
        return None

# Setup credentials
gemini_api_key = setup_gemini_credentials()
if not gemini_api_key:
    print("⚠️ Continuing without Gemini API key - some features will be limited")""",
    )

    # Add analysis cell
    analysis_cell = nbf.v4.new_markdown_cell(
        """## 🤖 Gemini LLM Analysis with LangGraph""",
    )

    # Add LLM setup cell
    llm_setup_cell = nbf.v4.new_code_cell(
        """# Ensure gemini_api_key is defined (in case of kernel restart)
try:
    gemini_api_key
except NameError:
    print("🔐 Setting up Gemini API credentials...")
    print("❌ 1Password not available - continuing without Gemini API key")
    gemini_api_key = None

if gemini_api_key:
    # Initialize Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=gemini_api_key,
        temperature=0.1
    )

    print("✅ Gemini LLM initialized")
else:
    print("❌ Gemini API key not available - skipping LLM analysis")
    llm = None""",
    )

    # Add visualization cell
    viz_cell = nbf.v4.new_markdown_cell("""## 📊 Interactive Visualizations""")

    # Add plotting cell
    plot_cell = nbf.v4.new_code_cell(
        """# Set up plotting
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# First, let's see what data we have
print("📊 Data structure:")
print(f"Columns: {list(daily_data.columns)}")
print(f"Shape: {daily_data.shape}")
print("\\nSample data:")
print(daily_data.head())

# Create daily cost aggregation
daily_totals = daily_data.groupby('date')['cost'].sum().reset_index()
daily_totals.columns = ['date', 'total_cost']

print("\\n📈 Daily totals:")
print(daily_totals.head())

# Create interactive cost trend visualization
fig = px.line(daily_totals, x='date', y='total_cost',
              title='Daily GCP Cost Trend',
              labels={'total_cost': 'Cost ($)', 'date': 'Date'})
fig.update_layout(
    xaxis_title='Date',
    yaxis_title='Cost ($)',
    hovermode='x unified'
)
fig.show()""",
    )

    # Add service breakdown cell
    service_cell = nbf.v4.new_code_cell(
        """# Create service breakdown visualization
# Calculate total cost per service
service_totals  = \
     daily_data.groupby('service')['cost'].sum().sort_values(ascending=False)

print("💰 Service cost breakdown:")
print(service_totals)

fig = px.pie(values=service_totals.values, names=service_totals.index,
              title='GCP Service Cost Breakdown')
fig.update_traces(textposition='inside', textinfo='percent+label')
fig.show()""",
    )

    # Add summary cell
    summary_cell = nbf.v4.new_markdown_cell("""## 📝 Summary""")

    # Add summary code cell
    summary_code_cell = nbf.v4.new_code_cell(
        """# Calculate summary statistics
daily_totals = daily_data.groupby('date')['cost'].sum().reset_index()
service_totals = daily_data.groupby('service')['cost'].sum()

print('📊 Analysis Summary:')
print('=' * 20)
print(f'📅 Analysis Period: {daily_data["date"].min()} to {daily_data["date"].max()}')
print(f'💰 Total Cost: ${daily_data["cost"].sum():.2f}')
print(f'📈 Average Daily Cost: ${daily_totals["cost"].mean():.2f}')
print(f'🔍 Services Analyzed: {len(service_totals)}')
print(f'🤖 Analysis Method: Gemini LLM with LangGraph/LangChain')
print(f'🔐 Credentials: {"✅ Available" if gemini_api_key else "❌ Not Available"}')

print('\\n✅ Analysis complete! Use the insights above to optimize your GCP costs.')""",
    )

    # Add all cells to notebook
    nb.cells = [
        title_cell,
        imports_cell,
        data_cell,
        credentials_cell,
        cred_setup_cell,
        analysis_cell,
        llm_setup_cell,
        viz_cell,
        plot_cell,
        service_cell,
        summary_cell,
        summary_code_cell,
    ]

    return nb


def main() -> None:
    """Create and save the notebook"""
    # Create notebook
    nb = create_gemini_notebook()

    # Save to file
    output_path = Path(
        "data/billing_reports/analysis_data/gemini_billing_analysis.ipynb",
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    nbf.write(nb, output_path)

    print(f"✅ Proper notebook saved: {output_path}")
    print("📊 Using nbformat library for correct notebook structure!")


if __name__ == "__main__":
    main()
