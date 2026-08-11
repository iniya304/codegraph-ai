from pathlib import Path

from codegraph.analyzer import analyze_file

ROOT = Path(__file__).resolve().parent.parent
SAMPLE_FILE = ROOT / "samples" / "buggy_code.py"


def test_sample_file_exists():
    assert SAMPLE_FILE.exists()


def test_analyze_file_returns_report():
    report = analyze_file(str(SAMPLE_FILE))

    assert "file" in report
    assert "pylint" in report
    assert "bandit" in report
    assert "flake8" in report


def test_analyze_missing_file():
    report = analyze_file("missing_file.py")

    assert "error" in report


def test_bandit_detects_security_issues():
    report = analyze_file(str(SAMPLE_FILE))

    assert isinstance(report["bandit"], list)
    assert len(report["bandit"]) > 0


def test_flake8_detects_style_issues():
    report = analyze_file(str(SAMPLE_FILE))

    assert isinstance(report["flake8"], list)
    assert len(report["flake8"]) > 0