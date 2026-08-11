from codegraph.reviewer import (
    build_review_prompt,
    parse_llm_review,
    review,
    rule_based_review,
)


def test_rule_based_review_sorts_by_severity():
    issues = [
        {"tool": "flake8", "line": 1, "severity": "style", "message": "long line"},
        {"tool": "bandit", "line": 6, "severity": "high", "message": "sql injection"},
    ]

    comments = rule_based_review(issues)

    assert comments[0]["severity"] == "high"
    assert comments[1]["severity"] == "style"
    assert comments[0]["confidence"] == 0.9


def test_build_review_prompt_contains_data():
    prompt = build_review_prompt([{"message": "x"}], {"changed_files": 1})

    assert "senior code reviewer" in prompt
    assert "changed_files" in prompt


def test_parse_llm_review_valid_json():
    text = '[{"file": "a.py", "line": 1, "severity": "high", "message": "bug"}]'

    comments = parse_llm_review(text)

    assert len(comments) == 1
    assert comments[0]["message"] == "bug"


def test_parse_llm_review_markdown_fences():
    text = '```json\n[{"message": "bug"}]\n```'

    comments = parse_llm_review(text)

    assert len(comments) == 1


def test_parse_llm_review_invalid():
    assert parse_llm_review("not json") == []


def test_review_falls_back_to_rule_based():
    result = review(
        [{"tool": "bandit", "line": 6, "severity": "high", "message": "x"}]
    )

    assert result["source"] == "rule-based"
    assert len(result["comments"]) == 1