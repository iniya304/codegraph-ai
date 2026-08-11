"""Build call graphs and compute change impact radius."""

import ast
from typing import Any, Dict, List, Set


def build_call_graph(source: str) -> Dict[str, List[str]]:
    """
    Build a mapping: function name -> list of functions it calls.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {}

    defined: Set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defined.add(node.name)

    graph: Dict[str, List[str]] = {}

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            calls: Set[str] = set()

            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    func = child.func

                    if isinstance(func, ast.Name):
                        calls.add(func.id)
                    elif isinstance(func, ast.Attribute):
                        calls.add(func.attr)

            graph[node.name] = sorted(
                c for c in calls if c in defined and c != node.name
            )

    return graph


def compute_impact(
    call_graph: Dict[str, List[str]], changed: List[str]
) -> Dict[str, Any]:
    """
    Given changed function names, compute which functions are impacted.
    A function is impacted if it (transitively) calls a changed function.
    """
    reverse: Dict[str, List[str]] = {name: [] for name in call_graph}

    for caller, callees in call_graph.items():
        for callee in callees:
            reverse.setdefault(callee, []).append(caller)

    impacted: Set[str] = set()
    stack = list(changed)

    while stack:
        current = stack.pop()

        for caller in reverse.get(current, []):
            if caller not in impacted and caller not in changed:
                impacted.add(caller)
                stack.append(caller)

    return {
        "changed": sorted(changed),
        "impacted": sorted(impacted),
    }