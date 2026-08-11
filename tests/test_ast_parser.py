from codegraph.ast_parser import parse_file, parse_source

SAMPLE_SOURCE = '''
import os
from pathlib import Path


def add(a, b):
    return a + b


class Calculator:
    def subtract(self, a, b):
        return a - b
'''


def test_parse_source_functions():
    code_map = parse_source(SAMPLE_SOURCE)

    names = [f["name"] for f in code_map["functions"]]

    assert "add" in names
    assert "subtract" in names


def test_parse_source_classes():
    code_map = parse_source(SAMPLE_SOURCE)

    assert len(code_map["classes"]) == 1
    assert code_map["classes"][0]["name"] == "Calculator"
    assert "subtract" in code_map["classes"][0]["methods"]


def test_parse_source_imports():
    code_map = parse_source(SAMPLE_SOURCE)

    assert "os" in code_map["imports"]
    assert "pathlib" in code_map["imports"]


def test_parse_source_syntax_error():
    code_map = parse_source("def broken(:")

    assert code_map["functions"] == []
    assert code_map["classes"] == []
    assert code_map["imports"] == []


def test_parse_file_missing():
    code_map = parse_file("no_such_file.py")

    assert "error" in code_map