"""CLI entry point for CodeGraph AI."""

import json
import sys
from pathlib import Path

from codegraph.analyzer import analyze_file
from codegraph.ast_parser import parse_file
from codegraph.diff_parser import run_git_diff, summarize_diff
from codegraph.evaluation import run_benchmark
from codegraph.graph import build_call_graph, compute_impact
from codegraph.normalizer import normalize_report
from codegraph.pr_reviewer import review_pull_request
from codegraph.printer import (
    print_benchmark,
    print_code_map,
    print_impact,
    print_issues,
    print_pr_report,
    print_test_code,
)
from codegraph.reviewer import review
from codegraph.sarif import generate_sarif
from codegraph.sandbox import run_tests_in_sandbox
from codegraph.test_generator import generate_tests, save_tests


def print_usage():
    print("Usage:")
    print("  python -m codegraph.main <file.py> [--unified] [--sarif]")
    print("  python -m codegraph.main --diff [ref]")
    print("  python -m codegraph.main --map <file.py>")
    print("  python -m codegraph.main --impact <file.py> --changed fn1,fn2")
    print("  python -m codegraph.main --review <file.py> [--llm]")
    print("  python -m codegraph.main --generate-tests <file.py> [--out path] [--run] [--llm]")
    print("  python -m codegraph.main --evaluate [benchmark.json]")
    print("  python -m codegraph.main --pr <github-pr-url>")


def main():
    args = sys.argv[1:]

    if len(args) < 1:
        print_usage()
        sys.exit(1)

    if args[0] == "--diff":
        ref = args[1] if len(args) > 1 else "HEAD~1"
        summary = summarize_diff(run_git_diff(ref))
        print(json.dumps(summary, indent=2))
        return

    if args[0] == "--map":
        if len(args) < 2:
            print_usage()
            sys.exit(1)

        print_code_map(parse_file(args[1]))
        return

    if args[0] == "--impact":
        if len(args) < 4 or "--changed" not in args:
            print_usage()
            sys.exit(1)

        file_path = Path(args[1])

        if not file_path.exists():
            print(json.dumps({"error": f"File not found: {args[1]}"}, indent=2))
            return

        changed_arg = args[args.index("--changed") + 1]
        changed = [c.strip() for c in changed_arg.split(",") if c.strip()]

        source = file_path.read_text(encoding="utf-8")
        call_graph = build_call_graph(source)

        print_impact(compute_impact(call_graph, changed))
        return

    if args[0] == "--review":
        if len(args) < 2:
            print_usage()
            sys.exit(1)

        report = analyze_file(args[1])
        issues = normalize_report(report)
        result = review(issues, use_llm="--llm" in args)

        print_issues(result.get("comments", []))
        return

    if args[0] == "--generate-tests":
        if len(args) < 2:
            print_usage()
            sys.exit(1)

        result = generate_tests(args[1], use_llm="--llm" in args)

        if "error" in result:
            print(json.dumps(result, indent=2))
            return

        if "--run" in args:
            execution = run_tests_in_sandbox(result["test_code"])
            print(
                json.dumps(
                    {"source": result["source"], "execution": execution},
                    indent=2,
                )
            )
            return

        if "--out" in args:
            out_path = args[args.index("--out") + 1]
            saved = save_tests(result["test_code"], out_path)
            print(json.dumps({"source": result["source"], "saved_to": saved}, indent=2))
        else:
            print_test_code(result["test_code"])
        return

    if args[0] == "--evaluate":
        bench_path = args[1] if len(args) > 1 else "data/benchmark.json"
        print_benchmark(run_benchmark(bench_path))
        return

    if args[0] == "--pr":
        if len(args) < 2:
            print_usage()
            sys.exit(1)

        try:
            result = review_pull_request(args[1])
        except Exception as error:
            print(json.dumps({"error": str(error)}, indent=2))
            return

        print_pr_report(result)
        return

    file_path = args[0]
    unified = "--unified" in args
    sarif = "--sarif" in args

    report = analyze_file(file_path)

    if sarif:
        issues = normalize_report(report)
        sarif_output = generate_sarif(issues, file_path)

        with open("results.sarif", "w", encoding="utf-8") as f:
            json.dump(sarif_output, f, indent=2)

        print(f"✅ SARIF report saved to results.sarif ({len(issues)} issues)")
        return

    if unified:
        issues = normalize_report(report)
        print_issues(issues)
    else:
        print_issues(normalize_report(report))


if __name__ == "__main__":
    main()