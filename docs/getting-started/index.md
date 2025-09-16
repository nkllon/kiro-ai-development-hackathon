---
layout: default
title: Getting Started
description: Quick setup guide for Kiro AI Development Hackathon
---

# 🚀 Getting Started

Welcome to Kiro AI Development Hackathon! This guide will help you get up and running quickly.

## Prerequisites

- Python 3.9+
- Git
- pip or UV package manager

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/nkllon/kiro-ai-development-hackathon.git
cd kiro-ai-development-hackathon
```

### 2. Install Dependencies
```bash
# Using pip
pip install -r requirements-rc1.txt

# Or using UV (recommended)
uv pip install -r requirements-rc1.txt
```

### 3. Verify Installation
```bash
python -m src.rc1.cli.beast_mode_cli --help
```

## First Steps

### Diagnose System Health
```bash
# Quick system health check
python -m src.rc1.cli.beast_mode_cli status

# Comprehensive system analysis
python -m src.rc1.cli.beast_mode_cli diagnose system
```

### Fix Issues Automatically
```bash
# Fix identified issues
python -m src.rc1.cli.beast_mode_cli fix system --auto-fix

# Generate detailed report
python -m src.rc1.cli.beast_mode_cli report --format json
```

### Monitor System Health
```bash
# Start real-time monitoring
python -m src.rc1.cli.beast_mode_cli monitor --interval 30
```

## Next Steps

- [Documentation](/documentation/) - Comprehensive documentation
- [Examples](/examples/) - Usage examples and demos
- [API Reference](/api-reference/) - Technical API documentation
