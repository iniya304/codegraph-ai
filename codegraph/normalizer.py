"""Normalize static analysis tool outputs into a unified issue schema."""

import re
from typing import Any, Dict, List

FLAKE8_PATTERN = re.compile(
    r"^(?P<path>.+?):(?P<line>\d+):(?P<column>\d+):\s*(?P<rest>.+)$"
)


def normalize_pylint(results: Any) -> List[Dict[str, Any]]:
    """Convert raw pylint JSON output into unified issues."""
    issues: List[Dict[str, Any]] = []

    if not isinstance(results, list):
        return issues

    for item in results:
        issues.append(
            {
                "tool": "pylint",
                "line": item.get("line"),
                "column": item.get("column"),
                "severity": item.get("type", "info"),
                "code": item.get("message-id", ""),
                "message": item.get("message", ""),
            }
        )

    return issues


def normalize_bandit(results: Any) -> List[Dict[str, Any]]:
    """Convert raw bandit JSON results into unified issues."""
    issues: List[Dict[str, Any]] = []

    if not isinstance(results, list):
        return issues

    for item in results:
        issues.append(
            {
                "tool": "bandit",
                "line": item.get("line_number"),
                "column": None,
                "severity": str(item.get("issue_severity", "medium")).lower(),
                "code": item.get("test_id", ""),
                "message": item.get("issue_text", ""),
            }
        )

    return issues


def normalize_flake8(results: Any) -> List[Dict[str, Any]]:
    """Convert raw flake8 text lines into unified issues."""
    issues: List[Dict[str, Any]] = []

    if not isinstance(results, list):
        return issues

    for line in results:
        match = FLAKE8_PATTERN.match(line)

        if match:
            rest = match.group("rest")
            code = rest.split(" ", 1)[0] if rest else ""
            issues.append(
                {
                    "tool": "flake8",
                    "line": int(match.group("line")),
                    "column": int(match.group("column")),
                    "severity": "style",
                    "code": code,
                    "message": rest,
                }
            )
        else:
            issues.append(
                {
                    "tool": "flake8",
                    "line": None,
                    "column": None,
                    "severity": "style",
                    "code": "",
                    "message": line,
                }
            )

    return issues


def normalize_report(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert a raw analyzer report into a sorted unified issue list."""
    if not isinstance(report, dict) or "error" in report:
        return []

    issues: List[Dict[str, Any]] = []
    issues += normalize_pylint(report.get("pylint", []))
    issues += normalize_bandit(report.get("bandit", []))
    issues += normalize_flake8(report.get("flake8", []))

    issues.sort(key=lambda issue: issue.get("line") or 0)

    return issues
