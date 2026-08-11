"""CLI entry point for CodeGraph AI."""

import json
import sys

from codegraph.analyzer import analyze_file
from codegraph.diff_parser import run_git_diff, summarize_diff
from codegraph.normalizer import normalize_report


def print_usage():
    print("Usage:")
    print("  python -m codegraph.main <file.py> [--unified]")
    print("  python -m codegraph.main --diff [ref]")


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