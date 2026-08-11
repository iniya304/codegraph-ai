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
from codegraph.reviewer import review
from codegraph.sandbox import run_tests_in_sandbox
from codegraph.test_generator import generate_tests, save_tests


def print_usage():
    print("Usage:")
    print("  python -m codegraph.main <file.py> [--unified]")
    print("  python -m codegraph.main --diff [ref]")
    print("  python -m codegraph.main --map <file.py>")
    print("  python -m codegraph.main --impact <file.py> --changed fn1,fn2")
    print("  python -m codegraph.main --review <file.py> [--llm]")
    print("  python -m codegraph.main --generate-tests <file.py> [--out path] [--run] [--llm]")
    print("  python -m codegraph.main --evaluate [benchmark.json]")


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

        print(json.dumps(parse_file(args[1]), indent=2))
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

        print(json.dumps(compute_impact(call_graph, changed), indent=2))
        return

    if args[0] == "--review":
        if len(args) < 2:
            print_usage()
            sys.exit(1)

        report = analyze_file(args[1])
        issues = normalize_report(report)
        result = review(issues, use_llm="--llm" in args)

        print(json.dumps(result, indent=2))
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
            print(result["test_code"])
        return

    if args[0] == "--evaluate":
        bench_path = args[1] if len(args) > 1 else "data/benchmark.json"
        print(json.dumps(run_benchmark(bench_path), indent=2))
        return

    file_path = args[0]
    unified = "--unified" in args

    report = analyze_file(file_path)

    if unified:
        issues = normalize_report(report)
        print(json.dumps(issues, indent=2))
    else:
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()