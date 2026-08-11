# CodeGraph AI

CodeGraph AI is a repository intelligence engine that analyzes code changes, detects bugs and security issues, explains impact, generates tests, and reviews code with optional LLM intelligence.

## Features

- Static analysis using pylint, bandit, and flake8
- Unified issue normalization across tools
- Git diff parsing for pull request analysis
- AST-based code maps (functions, classes, imports)
- Call graph and change impact analysis
- LLM code review with rule-based fallback (provider-agnostic)
- Automatic pytest generation with sandboxed execution
- Benchmark evaluation with precision, recall, and F1 metrics
- GitHub Action for automated PR review

## Installation

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt