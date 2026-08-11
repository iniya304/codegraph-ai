"""Generate pytest code for analyzed Python files."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from codegraph.ast_parser import parse_source
from codegraph.reviewer import call_llm, load_env_file

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"


def build_test_prompt(source: str) -> str:
    """
    Build a prompt asking an LLM to generate pytest tests.
    """
    return (
        "You are a senior Python test engineer.\n"
        "Write pytest tests for the following Python source code.\n"
        "Return ONLY valid Python code, no explanations.\n\n"
        f"SOURCE CODE:\n{source}\n"
    )


def rule_based_tests(file_path: str, code_map: Dict[str, Any]) -> str:
    """
    Generate simple pytest code verifying each top-level function
    exists and is callable.
    """
    path = Path(file_path)
    module_name = path.stem

    lines = [
        "import importlib.util",
        "",
        f'SPEC = importlib.util.spec_from_file_location("{module_name}", r"{path}")',
        "MODULE = importlib.util.module_from_spec(SPEC)",
        "SPEC.loader.exec_module(MODULE)",
        "",
        "",
    ]

    for func in code_map.get("functions", []):
        args = func.get("args", [])

        # Skip methods (they receive self)
        if args and args[0] == "self":
            continue

        name = func["name"]
        lines.append(f"def test_{name}_is_callable():")
        lines.append(f'    assert callable(getattr(MODULE, "{name}"))')
        lines.append("")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def save_tests(test_code: str, output_path: str) -> str:
    """
    Write generated test code to disk and return the path.
    """
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(test_code, encoding="utf-8")
    return str(out)


def generate_tests(
    file_path: str,
    use_llm: bool = False,
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate pytest code for a Python file.
    Uses the LLM when requested and available,
    otherwise falls back to rule-based generation.
    """
    load_env_file()

    path = Path(file_path)

    if not path.exists():
        return {"error": f"File not found: {file_path}"}

    source = path.read_text(encoding="utf-8")
    code_map = parse_source(source)

    api_key = api_key or os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("CODEGRAPH_LLM_BASE_URL", DEFAULT_BASE_URL)
    model = os.environ.get("CODEGRAPH_LLM_MODEL", DEFAULT_MODEL)

    if use_llm and api_key:
        text = call_llm(
            build_test_prompt(source), api_key, base_url=base_url, model=model
        )

        if text and "def test_" in text:
            return {"source": "llm", "test_code": text}

    return {
        "source": "rule-based",
        "test_code": rule_based_tests(file_path, code_map),
    }