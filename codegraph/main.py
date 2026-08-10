"""CLI entry point for CodeGraph AI."""

import json
import sys

from codegraph.analyzer import analyze_file


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m codegraph.main <file.py>")
        sys.exit(1)

    file_path = sys.argv[1]
    report = analyze_file(file_path)

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()