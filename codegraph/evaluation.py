"""Evaluate review quality using labeled benchmarks."""

import json
from pathlib import Path
from typing import Any, Dict, List

from codegraph.analyzer import analyze_file
from codegraph.normalizer import normalize_report


def load_benchmark(path: str) -> List[Dict[str, Any]]:
    """
    Load a benchmark dataset: list of {file, expected_lines}.
    """
    bench_path = Path(path)

    if not bench_path.exists():
        return []

    try:
        data = json.loads(bench_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    if not isinstance(data, list):
        return []

    return data


def evaluate_sample(sample: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate one benchmark sample by comparing detected issue lines
    against expected lines.
    """
    file_path = sample.get("file", "")
    expected = set(sample.get("expected_lines", []))

    report = analyze_file(file_path)
    issues = normalize_report(report)
    detected = {issue.get("line") for issue in issues if issue.get("line")}

    true_positives = len(expected & detected)
    false_positives = len(detected - expected)
    false_negatives = len(expected - detected)

    precision = (
        true_positives / (true_positives + false_positives)
        if (true_positives + false_positives)
        else 0.0
    )
    recall = (
        true_positives / (true_positives + false_negatives)
        if (true_positives + false_negatives)
        else 0.0
    )

    return {
        "file": file_path,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
    }


def run_benchmark(path: str) -> Dict[str, Any]:
    """
    Run the full benchmark and aggregate metrics.
    """
    samples = load_benchmark(path)

    results = [evaluate_sample(s) for s in samples]

    total_tp = sum(r["true_positives"] for r in results)
    total_fp = sum(r["false_positives"] for r in results)
    total_fn = sum(r["false_negatives"] for r in results)

    precision = (
        total_tp / (total_tp + total_fp) if (total_tp + total_fp) else 0.0
    )
    recall = (
        total_tp / (total_tp + total_fn) if (total_tp + total_fn) else 0.0
    )
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall)
        else 0.0
    )

    return {
        "samples": len(results),
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "results": results,
    }