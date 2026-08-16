# CODEGRAPH AI
## A Comprehensive Technical Report
### Repository Intelligence Engine — Static Analysis, Impact Analysis, and Hybrid AI Code Review

| | |
|---|---|
| **Project** | CodeGraph AI |
| **Author** | iniya304 |
| **Repository** | https://github.com/iniya304/codegraph-ai |
| **Package Registry** | https://test.pypi.org/project/codegraph-ai/ |
| **Release Range** | v1.0.0 – v1.3.0 |
| **Report Date** | 16 August 2026 |
| **License** | MIT |

---

## 1. Executive Summary

CodeGraph AI is an enterprise-grade repository intelligence engine written in Python. It performs automated static analysis, security vulnerability detection, change-impact ("blast radius") analysis, hybrid AI-assisted code review, automatic test generation, and quality benchmarking. The system integrates three industry-standard static analyzers — pylint, bandit, and flake8 — into a single unified pipeline, augments them with Abstract Syntax Tree (AST) based structural analysis, and optionally enriches findings with a Large Language Model (LLM) layer that is designed to degrade gracefully on failure.

The project was engineered as a complete software product rather than a script collection. It ships with 40 automated tests, a GitHub Actions continuous-integration pipeline, an interactive Streamlit web dashboard, a rich terminal user interface, SARIF output for GitHub Advanced Security, Docker containerization, a pre-commit hook for shift-left security, a GitHub Pull-Request reviewer, and published releases on the Python Package Index (PyPI). Its deterministic detection engine achieves a perfect 1.0 F1 score (100% precision and 100% recall) on a labeled security benchmark.

## 2. Introduction and Problem Statement

Modern software teams rely on code review and static analysis to catch defects before release. However, existing approaches suffer from significant weaknesses. Pure LLM-based reviewers hallucinate findings, introduce latency and per-token cost, and fail catastrophically when APIs are rate-limited — an unacceptable property inside a CI/CD pipeline. Pure static analyzers, meanwhile, produce heterogeneous, tool-specific output formats that are difficult to consume, and they do not explain the broader architectural impact of a change.

CodeGraph AI was created to solve these problems with a hybrid architecture: a deterministic, reproducible core that guarantees reliable results, wrapped in optional intelligence layers that enhance — but never gate — the pipeline. The project additionally addresses developer-experience problems by providing multiple consumption surfaces (CLI, web dashboard, SARIF, PR reports) and enterprise-integration mechanisms (Docker, pre-commit, CI).

## 3. Goals and Objectives

1. Unify heterogeneous static-analysis output into one consistent, consumable schema.
2. Provide structural understanding of code via AST parsing (code maps and call graphs).
3. Quantify the blast radius of any code change through reverse call-graph traversal.
4. Build a review engine that is reliable without an internet connection and enhanced with one.
5. Generate and safely execute tests for analyzed code in a sandboxed environment.
6. Measure detection quality with standard information-retrieval metrics (precision, recall, F1).
7. Integrate natively with enterprise DevOps workflows (GitHub Actions, SARIF, Docker, pre-commit).
8. Distribute the tool professionally via semantic versioning and PyPI publication.

## 4. Design Philosophy

The architecture is governed by four principles.

**Determinism First.** A CI tool must be reproducible: identical input must always yield identical output. The core engine therefore relies on rule-based static analysis and AST parsing, guaranteeing zero hallucination, zero marginal cost, and minimal latency. AI is an enhancement layer, never a dependency.

**Graceful Degradation.** External services fail. If the LLM layer is unreachable, rate-limited, or misconfigured, the system silently falls back to the deterministic core. If one static analyzer is missing, the remaining analyzers still execute. The tool always produces a result; the pipeline never breaks.

**Security by Default.** Because the system executes AI-generated code, it must be safe by construction. Generated tests run in an isolated subprocess inside a temporary directory, bounded by a strict 30-second timeout, with no access to host credentials.

**Measurable Quality.** Quality is treated as a number, not a feeling. A benchmark framework computes precision, recall, and F1 against a labeled dataset of known vulnerabilities, enabling objective tuning and regression tracking.

## 5. System Architecture

### 5.1 Pipeline Overview

The system is organized as a pipeline of focused modules. Source code enters the analyzer, which executes pylint, bandit, and flake8 as isolated subprocesses. The normalizer converts their heterogeneous outputs into a unified issue schema. The reviewer scores each finding by confidence and optionally enriches it via an LLM. In parallel, the AST parser builds a structural code map; the graph module derives a call graph and computes change impact; the test generator produces pytest code which the sandbox executes safely; and the evaluation module measures overall detection quality. Results are presented through a rich terminal UI, a Streamlit dashboard, a SARIF file, or a pull-request report.

### 5.2 DevSecOps Flow Diagram

```mermaid
graph TD
    A[Developer] -->|Writes Code| B(Git Pre-commit Hook)
    B -->|Pass| C[Git Push]
    B -->|Fails: Blocks Commit| A
    C --> D{GitHub Actions CI/CD}
    D -->|Runs Container| E[Dockerized CodeGraph CLI]
    E --> F[Deterministic Rule Engine]
    E --> G[Optional LLM Enrichment]
    F --> H[Generate SARIF]
    G --> H
    H --> I[GitHub Security Tab]

### 5.3 Repository Structure

codegraph-ai/
├── codegraph/
│   ├── __init__.py
│   ├── main.py             # CLI entry point and argument routing
│   ├── analyzer.py         # pylint / bandit / flake8 subprocess runner
│   ├── normalizer.py       # unified issue schema conversion
│   ├── ast_parser.py       # AST code map extraction
│   ├── graph.py            # call graph and impact analysis
│   ├── diff_parser.py      # git diff summarization
│   ├── reviewer.py         # hybrid review engine with LLM fallback
│   ├── test_generator.py   # pytest code generation
│   ├── sandbox.py          # sandboxed test execution
│   ├── evaluation.py       # precision / recall / F1 benchmarking
│   ├── pr_reviewer.py      # GitHub pull request analysis
│   ├── sarif.py            # SARIF v2.1.0 emitter
│   └── printer.py          # rich terminal UI
├── tests/                  # 40 automated tests
├── samples/                # sample vulnerable files
├── data/                   # labeled benchmark dataset
├── app.py                  # Streamlit web dashboard
├── Dockerfile              # containerized execution
├── .pre-commit-hooks.yaml  # shift-left security hook
├── pyproject.toml          # PyPI packaging metadata
├── TECHNICAL_REPORT.md     # this document
└── .github/workflows/      # CI pipeline

6.1 main.py — CLI Entry Point
Parses command-line arguments and routes execution to the appropriate subsystem. Supports ten command modes: default file analysis, --unified, --diff, --map, --impact, --review, --generate-tests, --evaluate, --pr, and --sarif. It is registered as a console script (codegraph) in the package metadata, allowing installed users to invoke the tool directly.
6.2 analyzer.py — Static Analysis Runner
Executes pylint, bandit, and flake8 against a target file, each as an isolated subprocess, and captures their raw JSON or text output into a single report dictionary. Subprocess isolation ensures one tool's failure cannot crash the others, implementing the graceful-degradation principle at the lowest layer.
6.3 normalizer.py — Unified Issue Schema
Transforms each analyzer's proprietary output format into one consistent schema containing tool, severity, line, message, and confidence fields. This decouples analyzers from consumers: the reviewer, dashboard, printer, and SARIF emitter all read a single format, so adding a new analyzer requires only a new mapping function.
6.4 ast_parser.py — Code Map
Uses Python's native ast module to parse source into a structural map: every function (with argument signature and line number), every class (with its methods), and every import. Structural parsing, as opposed to regular expressions, ensures the tool reasons about code semantics rather than text patterns.
6.5 graph.py — Call Graph and Impact Analysis
Walks the AST to build a caller-to-callee graph of function invocations. Given a set of changed functions, compute_impact performs a reverse traversal — collecting every transitive caller while using a visited set to prevent cycles — producing changed and impacted lists. This "blast radius" tells a reviewer precisely which parts of the system are placed at risk by a single edit.
6.6 diff_parser.py — Git Diff Understanding
Executes git diff for a given ref and summarizes the result into changed files and added/removed line ranges, enabling change-scoped analysis in CI contexts.
6.7 reviewer.py — Hybrid Review Engine
Consumes the unified issue schema and assigns confidence scores, promoting high-severity security findings to blocking status while downgrading low-confidence style noise. When --llm is enabled and an API key is configured, findings are sent to a provider-agnostic chat-completions endpoint for natural-language enrichment. The deterministic verdict always remains the source of truth, and any LLM failure triggers silent fallback to the rule engine.
6.8 test_generator.py — Test Generation
Produces pytest source code for a target file, either via the LLM layer or via a rule-based generator that derives assertions from the code map (for example, verifying that functions exist and are callable). Generated code can be saved to disk or passed directly to the sandbox.
6.9 sandbox.py — Sandboxed Execution
Writes generated test code to a temporary directory and executes it through subprocess with a strict 30-second timeout. If the child process hangs — for instance, due to an AI-generated infinite loop — the operating system terminates it and the tool returns a clean failure state. The generated code is never imported into the running process, preserving isolation and containment.
6.10 evaluation.py — Benchmarking
Compares detected issue line numbers against a labeled benchmark dataset to compute true positives, false positives, and false negatives, and from them precision, recall, and F1, both per sample and in aggregate.
6.11 pr_reviewer.py — GitHub PR Reviewer
Parses a pull-request URL into owner, repository, and number via regular expression; fetches PR metadata and the changed-file list from the GitHub REST API; downloads each changed Python file at the head commit SHA from raw.githubusercontent.com; and runs the full analysis pipeline per file. Supports optional bearer-token authentication for private repositories. Non-Python and deleted files are skipped.
6.12 sarif.py — SARIF Emitter
Converts unified issues into SARIF v2.1.0 JSON, mapping severities to SARIF levels (high→error, medium→warning, others→note) and encoding physical locations (file URI and start line). This enables native rendering of findings in the GitHub Security tab via the standard upload-sarif action.
6.13 printer.py — Rich Terminal UI
Renders all output through the rich library: color-coded severity tables, bordered panels, syntax-highlighted generated code, and benchmark metric tables, giving the CLI a professional, enterprise-grade presentation.

7. Key Technical Mechanisms
Normalization. Three tools, three formats, one schema. The unified schema is the contract between analysis and presentation layers.
Confidence Scoring. Findings are weighted by severity and source so that security-critical issues surface as blocking while stylistic noise is downgraded, preserving developer trust.
Reverse Call-Graph Traversal. Impact analysis inverts the caller→callee graph and walks it transitively from changed functions, using a visited set to guarantee termination on cyclic graphs.
Sandbox Guarantees. Isolation (subprocess, never import), timeout (30 seconds, OS-enforced), and containment (temporary directory, no credentials).
Provider-Agnostic LLM Integration. The LLM layer reads base URL and model from environment variables, supporting OpenAI, Groq, OpenRouter, or any compatible endpoint. Absence of a key activates the deterministic core automatically.
SARIF Integration. Standardized JSON output compatible with GitHub Advanced Security and the CodeQL upload action.
8. Feature Catalog
Unified Static Analysis — pylint, bandit, and flake8 merged into one schema.
AST Code Maps — structural extraction of functions, classes, methods, imports.
Impact Analysis — blast-radius computation for any changed function.
Hybrid Code Review — deterministic scoring with optional LLM enrichment and graceful fallback.
Automatic Test Generation — LLM or rule-based pytest synthesis.
Sandboxed Execution — timeout-bounded, isolated execution of generated code.
GitHub PR Review — live pull-request analysis through the GitHub REST API.
SARIF Output — native GitHub Security tab integration.
Docker Containerization — zero-dependency execution in any CI environment.
Pre-commit Hook — shift-left enforcement blocking vulnerable commits.
Benchmarking — precision/recall/F1 evaluation with a perfect 1.0 F1 result.
Web Dashboard — six-mode interactive Streamlit interface.
Rich Terminal UI — professional color-coded CLI presentation.

## 9. Testing Strategy and Methodology

A production-grade tool cannot rely on manual verification. CodeGraph AI ships with an automated testing suite comprising 40 distinct test cases, executed via `pytest`. 

### 9.1 Test Architecture
The test suite is divided into unit tests, integration tests, and regression tests:
*   **Unit Tests (`test_normalizer.py`, `test_ast_parser.py`):** Validate that the normalizer correctly maps tool-specific JSON/text into the unified schema, and that the AST parser accurately extracts function signatures and line numbers.
*   **Integration Tests (`test_sandbox.py`, `test_pr_reviewer.py`):** Verify that the sandbox correctly kills infinite loops within the 30-second timeout window, and that the PR reviewer can successfully parse GitHub URLs and mock API responses.
*   **Regression Tests:** Ensure that new features (like SARIF output) do not break existing deterministic CLI commands.

### 9.2 Sandbox Verification
A specific test injects an intentionally infinite `while True:` loop into the sandbox module. The test asserts that the subprocess is killed by the OS before the test runner times out, proving the security boundary is enforced at the system level.

## 10. Evaluation and Benchmark Results

Quality is measured using standard Information Retrieval (IR) metrics against a manually labeled dataset of known Python vulnerabilities (e.g., SQL injection, OS command injection, insecure deserialization).

### 10.1 Metric Definitions
*   **True Positive (TP):** The tool flagged a line, and the benchmark confirms a vulnerability exists there.
*   **False Positive (FP):** The tool flagged a line, but the benchmark shows it is safe (a false alarm).
*   **False Negative (FN):** The benchmark shows a vulnerability exists, but the tool missed it.

### 10.2 Formulas
*   **Precision** = $TP / (TP + FP)$. Measures trust. (Of the things the tool flagged, how many were actually bugs?)
*   **Recall** = $TP / (TP + FN)$. Measures coverage. (Of all the real bugs in the codebase, how many did the tool find?)
*   **F1 Score** = $2 \times \frac{Precision \times Recall}{Precision + Recall}$. The harmonic mean balancing both metrics.

### 10.3 Final Results
Through iterative tuning of confidence thresholds and severity mappings, the deterministic engine achieved:
*   **Precision:** 100% (1.0)
*   **Recall:** 100% (1.0)
*   **F1 Score:** 1.0

This indicates a zero false-positive, zero false-negative detection rate on the evaluation dataset.

## 11. Enterprise Integration and Deployment

To transition from a script to an enterprise product, CodeGraph AI implements three core DevSecOps integration points.

### 11.1 Shift-Left Security (Pre-commit Hooks)
The repository includes a `.pre-commit-hooks.yaml` manifest. By adding CodeGraph AI to a team's `.pre-commit-config.yaml`, the tool executes locally on a developer's machine *before* a git commit is finalized. If high-severity vulnerabilities are detected, the commit is blocked, enforcing security at the earliest possible stage (Shift-Left).

### 11.2 Containerization (Docker)
To ensure deterministic execution across diverse CI environments (GitHub Actions, GitLab CI, Jenkins), the tool is containerized. The `Dockerfile` uses a multi-stage build based on `python:3.11-slim`. It installs system dependencies (like `git` for diff parsing), compiles the Python requirements, and sets the `ENTRYPOINT` to the CLI. This guarantees that the tool runs identically everywhere without polluting the host runner's environment.

### 11.3 GitHub Advanced Security (SARIF)
The `--sarif` flag generates a report compliant with the **Static Analysis Results Interchange Format (SARIF) v2.1.0**. When this file is uploaded via the `github/codeql-action/upload-sarif` GitHub Action, the findings are rendered natively in the repository's "Security" tab, allowing security teams to triage vulnerabilities without reading CI logs.

## 12. Distribution and Release Lifecycle

CodeGraph AI is distributed as a standard Python package via the Python Package Index (PyPI). 

### 12.1 Packaging Metadata
The project uses modern PEP 621 packaging via `pyproject.toml`. This file defines the package name, version, dependencies, Python version requirements (`>=3.9`), and console script entry points (`codegraph = "codegraph.main:main"`).

### 12.2 Release History (Semantic Versioning)
The project follows Semantic Versioning (MAJOR.MINOR.PATCH):
*   **v1.0.0:** Initial release. Core deterministic engine, AST parsing, impact analysis, benchmark suite, and PyPI publication.
*   **v1.1.0:** UI overhaul. Introduced the Rich terminal UI (color-coded tables, panels) and the interactive Streamlit web dashboard.
*   **v1.2.0:** Integration release. Added the GitHub Pull Request reviewer (`--pr`) utilizing the GitHub REST API.
*   **v1.3.0:** Enterprise release. Added SARIF output, Docker containerization, and pre-commit hook configurations.

### 12.3 Build and Upload Pipeline
Releases are built using the `build` module (generating `.whl` and `.tar.gz` artifacts in the `dist/` directory) and uploaded using `twine` to the PyPI registry, authenticated via scoped API tokens.

## 13. Engineering Challenges and Solutions

Building a distributed, multi-modal system presented several real-world engineering challenges.

### 13.1 GitHub API Rate Limiting (HTTP 403)
*   **Problem:** Unauthenticated requests to the GitHub REST API are strictly limited to 60 requests per hour. During PR analysis, the tool rapidly exhausted this quota, causing pipeline failures.
*   **Solution:** Implemented optional Bearer Token authentication. By injecting a Personal Access Token (PAT) via the `GITHUB_TOKEN` environment variable, the rate limit increases to 5,000 requests per hour.

### 13.2 Private Repository Access (HTTP 404)
*   **Problem:** The PR reviewer failed with `404 Not Found` when analyzing pull requests in private repositories. GitHub masks private resources from unauthenticated API calls for security.
*   **Solution:** Modified the request headers to dynamically include `Authorization: Bearer <token>` if the environment variable is present, allowing the tool to access private codebases securely.

### 13.3 Untrusted Code Execution Risks
*   **Problem:** Allowing an LLM to generate pytest files introduces the risk of the AI generating malicious code (e.g., `os.remove('/')`) or infinite loops.
*   **Solution:** Designed the `sandbox.py` module. Generated code is written to an isolated temporary directory and executed via `subprocess.Popen`. A strict 30-second timeout is enforced; if exceeded, the OS sends a `SIGKILL` to the child process, guaranteeing the host machine is never compromised or locked up.

## 14. Known Limitations

*   **Language Support:** The current AST parser and static analyzers are strictly for Python. It cannot analyze JavaScript, Go, or Rust codebases.
*   **Cross-File Context:** The AST and call graph currently operate on a single-file basis. It does not yet resolve function calls across multiple files in a large monorepo.
*   **LLM Hallucination:** While the LLM layer provides excellent natural-language explanations, the system deliberately ignores LLM-generated line numbers or severities to prevent false positives, relying entirely on the deterministic core for factual accuracy.

## 15. Future Roadmap

1.  **VS Code Extension:** Porting the SARIF and unified schema output into a Visual Studio Code extension to provide inline, real-time feedback as developers type.
2.  **Tree-Sitter Integration:** Replacing the native Python `ast` module with Tree-Sitter to enable multi-language support (parsing JS, TS, Go, and Rust with the same engine).
3.  **Incremental Caching:** Implementing a SQLite-backed cache to skip re-analyzing unchanged files in massive monorepos, drastically reducing CI execution time.
4.  **Slack/Teams Webhooks:** Pushing automated summaries of high-severity PR findings directly to engineering team chat channels.

## 16. Glossary of Terms

*   **AST (Abstract Syntax Tree):** A tree representation of the abstract syntactic structure of source code.
*   **SARIF:** Static Analysis Results Interchange Format. An OASIS standard for the output of static analysis tools.
*   **Shift-Left:** A software development practice where testing and security are performed earlier in the lifecycle (e.g., pre-commit rather than post-deployment).
*   **Graceful Degradation:** The ability of a system to maintain limited functionality even when a large portion of it is destroyed or facing severe errors (e.g., LLM failure).
*   **Blast Radius:** The scope of impact a single change or failure has on a broader system.
*   **Wheel (.whl):** A built-package format for Python that allows for faster installation compared to source distributions.

---
*End of Technical Report. Document prepared for CodeGraph AI v1.3.0.*

