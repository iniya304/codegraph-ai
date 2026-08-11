from pathlib import Path

from codegraph.ast_parser import parse_source
from codegraph.test_generator import generate_tests, rule_based_tests, save_tests

ROOT = Path(__file__).resolve().parent.parent
SAMPLE_FILE = ROOT / "samples" / "buggy_code.py"


def test_rule_based_tests_contains_functions():
    code_map = parse_source(SAMPLE_FILE.read_text(encoding="utf-8"))

    test_code = rule_based_tests(str(SAMPLE_FILE), code_map)

    assert "def test_login_is_callable():" in test_code
    assert "def test_divide_is_callable():" in test_code
    assert "def test_delete_file_is_callable():" in test_code


def test_generate_tests_rule_based():
    result = generate_tests(str(SAMPLE_FILE))

    assert result["source"] == "rule-based"
    assert "def test_" in result["test_code"]


def test_generate_tests_missing_file():
    result = generate_tests("no_such_file.py")

    assert "error" in result


def test_save_tests(tmp_path):
    out = tmp_path / "generated" / "test_sample.py"

    saved = save_tests("def test_x():\n    assert True\n", str(out))

    assert Path(saved).exists()
    assert "def test_x" in Path(saved).read_text(encoding="utf-8")