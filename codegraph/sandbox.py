"""Safely execute generated test code with timeouts."""

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict


def run_tests_in_sandbox(test_code: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Write test code to a temporary folder and execute it with pytest.
    Returns execution results including pass/fail and output.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_file = Path(tmp_dir) / "test_generated.py"
        test_file.write_text(test_code, encoding="utf-8")

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_file), "-q"],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": f"Test execution timed out after {timeout} seconds",
            }