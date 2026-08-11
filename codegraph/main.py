"""CLI entry point for CodeGraph AI."""

import json
import sys

from codegraph.analyzer import analyze_file
from codegraph.normalizer import normalize_report


def main():
    args = sys.argv[1:]

    if len(args) < 1:
        print("Usage: python -m codegraph.main <file.py> [--unified]")
        sys.exit(1)

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