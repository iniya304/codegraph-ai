import json

from codegraph.evaluation import evaluate_sample, load_benchmark, run_benchmark


def test_load_benchmark_missing_file():
    assert load_benchmark("missing.json") == []


def test_load_benchmark_valid(tmp_path):
    bench = tmp_path / "bench.json"
    bench.write_text(
        json.dumps([{"file": "x.py", "expected_lines": [1]}]),
        encoding="utf-8",
    )

    data = load_benchmark(str(bench))

    assert len(data) == 1


def test_evaluate_sample_detects_bug(tmp_path):
    buggy = tmp_path / "buggy.py"
    buggy.write_text('"""Small buggy sample."""\n\nimport os\n\nos.system("ls")\n', encoding="utf-8")

    result = evaluate_sample({"file": str(buggy), "expected_lines": [5]})

    assert result["true_positives"] >= 1
    assert result["recall"] == 1.0


def test_run_benchmark_aggregates(tmp_path):
    buggy = tmp_path / "buggy.py"
    buggy.write_text('"""Small buggy sample."""\n\nimport os\n\nos.system("ls")\n', encoding="utf-8")

    bench = tmp_path / "bench.json"
    bench.write_text(
        json.dumps([{"file": str(buggy), "expected_lines": [5]}]),
        encoding="utf-8",
    )

    report = run_benchmark(str(bench))

    assert report["samples"] == 1
    assert "precision" in report
    assert "recall" in report
    assert "f1" in report