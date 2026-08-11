"""Parse git diff output into structured change data."""

import subprocess
from typing import Any, Dict, List, Optional


def run_git_diff(ref: str = "HEAD~1") -> str:
    """
    Run git diff against a ref and return raw diff text.
    """
    try:
        result = subprocess.run(
            ["git", "diff", ref],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout
    except Exception:
        return ""


def parse_diff(diff_text: str) -> List[Dict[str, Any]]:
    """
    Parse unified diff text into per-file change data.
    """
    files: List[Dict[str, Any]] = []
    current: Optional[Dict[str, Any]] = None

    for line in diff_text.splitlines():
        if line.startswith("+++ b/"):
            if current:
                files.append(current)

            current = {
                "file": line[6:],
                "added_lines": [],
                "removed_lines": [],
                "hunks": 0,
            }
        elif line.startswith("@@"):
            if current:
                current["hunks"] += 1
        elif line.startswith("+") and not line.startswith("+++"):
            if current:
                current["added_lines"].append(line[1:])
        elif line.startswith("-") and not line.startswith("---"):
            if current:
                current["removed_lines"].append(line[1:])

    if current:
        files.append(current)

    return files


def summarize_diff(diff_text: str) -> Dict[str, Any]:
    """
    Create a compact summary of a diff.
    """
    files = parse_diff(diff_text)

    return {
        "changed_files": len(files),
        "files": [
            {
                "file": f["file"],
                "added": len(f["added_lines"]),
                "removed": len(f["removed_lines"]),
                "hunks": f["hunks"],
            }
            for f in files
        ],
    }