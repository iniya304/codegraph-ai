# CodeGraph AI

CodeGraph AI is an enterprise-grade repository intelligence engine that analyzes code changes, detects vulnerabilities, and auto-generates tests. It uses a **hybrid review architecture** combining a deterministic rule engine with optional LLM enrichment.

## Architecture & DevSecOps Pipeline

CodeGraph AI integrates natively into modern CI/CD workflows through shift-left security, containerization, and standard SARIF reporting.

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