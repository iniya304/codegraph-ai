"""Generate code review comments from analysis results."""

import json
import os
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

SEVERITY_ORDER = {"high": 3, "medium": 2, "low": 1, "style": 0, "info": 0}

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"


def load_env_file(path: str = ".env") -> None:
    """
    Load environment variables from a .env file if it exists.
    Never overrides variables that are already set.
    """
    env_path = Path(path)

    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def build_review_prompt(
    issues: List[Dict[str, Any]], diff_summary: Dict[str, Any]
) -> str:
    """
    Build a prompt for an LLM code reviewer.
    """
    return (
        "You are a senior code reviewer.\n"
        "Below is a diff summary and static analysis issues.\n"
        "Produce a JSON list of review comments with fields:\n"
        "file, line, severity, message, confidence.\n\n"
        f"DIFF SUMMARY:\n{json.dumps(diff_summary, indent=2)}\n\n"
        f"STATIC ISSUES:\n{json.dumps(issues, indent=2)}\n"
    )


def rule_based_review(issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert unified issues into review comments without an LLM.
    """
    comments = []

    for issue in issues:
        severity = issue.get("severity", "info")

        comments.append(
            {
                "file": None,
                "line": issue.get("line"),
                "severity": severity,
                "tool": issue.get("tool"),
                "message": issue.get("message"),
                "confidence": 0.9 if severity in ("high", "medium") else 0.6,
            }
        )

    comments.sort(
        key=lambda c: SEVERITY_ORDER.get(str(c["severity"]).lower(), 0),
        reverse=True,
    )

    return comments


def call_llm(
    prompt: str,
    api_key: str,
    base_url: str = DEFAULT_BASE_URL,
    model: str = DEFAULT_MODEL,
) -> Optional[str]:
    """
    Call any OpenAI-compatible chat completions API.
    Returns the assistant text, or None on failure.
    """
    url = base_url.rstrip("/") + "/chat/completions"

    payload = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except Exception:
        return None


def parse_llm_review(text: str) -> List[Dict[str, Any]]:
    """
    Parse LLM output text into a list of review comments.
    Returns an empty list if parsing fails.
    """
    if not text:
        return []

    text = text.strip()

    if text.startswith("```"):
        text = text.strip("`")

        if text.startswith("json"):
            text = text[4:]

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []

    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]

    return []


def review(
    issues: List[Dict[str, Any]],
    diff_summary: Optional[Dict[str, Any]] = None,
    use_llm: bool = False,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Produce a review report.
    Uses the LLM when requested and an API key is available,
    otherwise falls back to rule-based review.
    """
    load_env_file()

    diff_summary = diff_summary or {}
    api_key = api_key or os.environ.get("OPENAI_API_KEY")
    base_url = base_url or os.environ.get(
        "CODEGRAPH_LLM_BASE_URL", DEFAULT_BASE_URL
    )
    model = model or os.environ.get("CODEGRAPH_LLM_MODEL", DEFAULT_MODEL)

    if use_llm and api_key:
        prompt = build_review_prompt(issues, diff_summary)
        text = call_llm(prompt, api_key, base_url=base_url, model=model)
        comments = parse_llm_review(text)

        if comments:
            return {
                "source": "llm",
                "model": model,
                "comments": comments,
            }

    return {"source": "rule-based", "comments": rule_based_review(issues)}