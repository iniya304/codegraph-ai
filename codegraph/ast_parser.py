"""Parse Python source code into a structured code map using AST."""

import ast
from pathlib import Path
from typing import Any, Dict, List


def parse_source(source: str) -> Dict[str, Any]:
    """
    Parse Python source code into a code map.
    Returns empty structures if the code has syntax errors.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {
            "functions": [],
            "classes": [],
            "imports": [],
        }

    functions: List[Dict[str, Any]] = []
    classes: List[Dict[str, Any]] = []
    imports: List[str] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(
                {
                    "name": node.name,
                    "line": node.lineno,
                    "args": [arg.arg for arg in node.args.args],
                }
            )
        elif isinstance(node, ast.ClassDef):
            methods = [
                n.name
                for n in node.body
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            classes.append(
                {
                    "name": node.name,
                    "line": node.lineno,
                    "methods": methods,
                }
            )
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    return {
        "functions": functions,
        "classes": classes,
        "imports": imports,
    }


def parse_file(file_path: str) -> Dict[str, Any]:
    """
    Parse a Python file into a code map.
    """
    path = Path(file_path)

    if not path.exists():
        return {
            "error": f"File not found: {file_path}",
            "functions": [],
            "classes": [],
            "imports": [],
        }

    source = path.read_text(encoding="utf-8")
    code_map = parse_source(source)
    code_map["file"] = str(path)

    return code_map