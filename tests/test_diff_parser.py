from codegraph.diff_parser import parse_diff, run_git_diff, summarize_diff

SAMPLE_DIFF = """diff --git a/app.py b/app.py
index 1234567..89abcde 100644
--- a/app.py
+++ b/app.py
@@ -1,3 +1,4 @@
 import os
+import sys

 def main():
-    pass
+    print("hello")
"""


def test_parse_diff_empty():
    assert parse_diff("") == []


def test_parse_diff_single_file():
    files = parse_diff(SAMPLE_DIFF)

    assert len(files) == 1
    assert files[0]["file"] == "app.py"
    assert "import sys" in files[0]["added_lines"]
    assert '    print("hello")' in files[0]["added_lines"]
    assert "    pass" in files[0]["removed_lines"]
    assert files[0]["hunks"] == 1


def test_summarize_diff_counts():
    summary = summarize_diff(SAMPLE_DIFF)

    assert summary["changed_files"] == 1
    assert summary["files"][0]["file"] == "app.py"
    assert summary["files"][0]["added"] == 2
    assert summary["files"][0]["removed"] == 1


def test_run_git_diff_returns_string():
    diff_text = run_git_diff("HEAD~1")

    assert isinstance(diff_text, str)