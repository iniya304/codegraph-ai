"""Static analysis module for CodeGraph AI."""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


def run_command(command: List[str]) -> Tuple[int, str, str]:
    """
    Run a shell command and return:
    - return code
    - standard output
    - standard error
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as error:
        return -1, "", str(error)


def parse_json_output(output: str) -> Any:
    """
    Try to parse command output as JSON.
    If parsing fails, return an empty list.
    """
    output = output.strip()
    if not output:
        return []
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return []


def run_pylint(file_path: Path) -> Any:
    """
    Run pylint on a Python file and return JSON output.
    """
    _, stdout, _ = run_command(
        [
            sys.executable,
            "-m",
            "pylint",
            str(file_path),
            "--output-format=json",
        ]
    )
    return parse_json_output(stdout)


def run_bandit(file_path: Path) -> Any:
    """
    Run bandit security analysis on a Python file.
    Return only the results list.
    """
    _, stdout, _ = run_command(
        [
            sys.executable,
            "-m",
            "bandit",
            "-f",
            "json",
            "-q",
            str(file_path),
        ]
    )
    data = parse_json_output(stdout)

    if isinstance(data, dict):
        return data.get("results", [])

    return data


def analyze_file(file_path: str) -> Dict[str, Any]:
    """
    Analyze one Python file using static analysis tools.
    """
    path = Path(file_path)

    if not path.exists():
        return {
            "error": f"File not found: {file_path}"
        }

    return {
        "file": str(path),
        "pylint": run_pylint(path),
        "bandit": run_bandit(path),
    }