from codegraph.normalizer import (
    normalize_bandit,
    normalize_flake8,
    normalize_pylint,
    normalize_report,
)


def test_normalize_pylint():
    raw = [
        {
            "line": 5,
            "column": 4,
            "type": "warning",
            "message-id": "W0612",
            "message": "Unused variable",
        }
    ]

    issues = normalize_pylint(raw)

    assert len(issues) == 1
    assert issues[0]["tool"] == "pylint"
    assert issues[0]["line"] == 5
    assert issues[0]["severity"] == "warning"
    assert issues[0]["code"] == "W0612"
    assert issues[0]["message"] == "Unused variable"


def test_normalize_bandit():
    raw = [
        {
            "line_number": 6,
            "issue_severity": "HIGH",
            "test_id": "B608",
            "issue_text": "Possible SQL injection",
        }
    ]

    issues = normalize_bandit(raw)

    assert len(issues) == 1
    assert issues[0]["tool"] == "bandit"
    assert issues[0]["line"] == 6
    assert issues[0]["severity"] == "high"
    assert issues[0]["code"] == "B608"
    assert issues[0]["message"] == "Possible SQL injection"


def test_normalize_flake8():
    raw = ["samples/buggy_code.py:5:80: E501 line too long (92 > 79 characters)"]

    issues = normalize_flake8(raw)

    assert len(issues) == 1
    assert issues[0]["tool"] == "flake8"
    assert issues[0]["line"] == 5
    assert issues[0]["column"] == 80
    assert issues[0]["code"] == "E501"
    assert issues[0]["severity"] == "style"


def test_normalize_report_combines_and_sorts():
    report = {
        "file": "x.py",
        "pylint": [
            {
                "line": 10,
                "column": 0,
                "type": "convention",
                "message-id": "C0116",
                "message": "Missing docstring",
            }
        ],
        "bandit": [
            {
                "line_number": 6,
                "issue_severity": "HIGH",
                "test_id": "B608",
                "issue_text": "Possible SQL injection",
            }
        ],
        "flake8": [],
    }

    issues = normalize_report(report)

    assert len(issues) == 2
    assert issues[0]["line"] == 6
    assert issues[1]["line"] == 10


def test_normalize_report_handles_error():
    report = {"error": "File not found: x.py"}

    assert normalize_report(report) == []