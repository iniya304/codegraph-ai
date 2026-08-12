"""Analyze real GitHub pull requests."""

import json
import os
import re
import tempfile
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from codegraph.analyzer import analyze_file
from codegraph.normalizer import normalize_report
from codegraph.reviewer import review

API = "https://api.github.com"


def parse_pr_url(url: str) -> Tuple[str, str, int]:
    """
    Extract owner, repo, and PR number from a GitHub pull request URL.
    """
    match = re.search(r"github\.com/([^/]+)/([^/]+)/pull/(\d+)", url)

    if not match:
        raise ValueError(f"Not a valid pull request URL: {url}")

    return match.group(1), match.group(2), int(match.group(3))


def _headers() -> Dict[str, str]:
    """
    Build request headers, adding a token when available.
    """
    headers = {
        "User-Agent": "codegraph-ai",
        "Accept": "application/vnd.github+json",
    }

    token = os.environ.get("GITHUB_TOKEN")

    if token:
        headers["Authorization"] = f"Bearer {token}"

    return headers


def _get_json(url: str) -> Any:
    request = urllib.request.Request(url, headers=_headers())

    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_pr_info(owner: str, repo: str, number: int) -> Dict[str, Any]:
    """
    Fetch pull request metadata.
    """
    return _get_json(f"{API}/repos/{owner}/{repo}/pulls/{number}")


def fetch_pr_files(owner: str, repo: str, number: int) -> List[Dict[str, Any]]:
    """
    Fetch the list of files changed in a pull request.
    """
    return _get_json(f"{API}/repos/{owner}/{repo}/pulls/{number}/files")


def fetch_raw_file(owner: str, repo: str, sha: str, path: str) -> Optional[str]:
    """
    Fetch the raw content of a file at a specific commit.
    """
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{sha}/{path}"

    request = urllib.request.Request(url, headers=_headers())

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read().decode("utf-8")
    except Exception:
        return None


def review_pull_request(pr_url: str) -> Dict[str, Any]:
    """
    Review all changed Python files in a pull request.
    """
    owner, repo, number = parse_pr_url(pr_url)

    info = fetch_pr_info(owner, repo, number)
    head_sha = info["head"]["sha"]

    files = fetch_pr_files(owner, repo, number)

    reports = []

    for item in files:
        path = item.get("filename", "")

        if not path.endswith(".py"):
            continue

        if item.get("status") == "removed":
            continue

        source = fetch_raw_file(owner, repo, head_sha, path)

        if source is None:
            continue

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_file = Path(tmp_dir) / Path(path).name
            tmp_file.write_text(source, encoding="utf-8")

            report = analyze_file(str(tmp_file))
            issues = normalize_report(report)
            result = review(issues)

            reports.append(
                {"file": path, "comments": result.get("comments", [])}
            )

    return {
        "owner": owner,
        "repo": repo,
        "number": number,
        "title": info.get("title", ""),
        "changed_files": len(files),
        "reviewed_files": len(reports),
        "reports": reports,
    }