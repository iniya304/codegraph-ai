from codegraph.sandbox import run_tests_in_sandbox


def test_sandbox_passing_test():
    result = run_tests_in_sandbox("def test_ok():\n    assert True\n")

    assert result["success"] is True


def test_sandbox_failing_test():
    result = run_tests_in_sandbox("def test_bad():\n    assert False\n")

    assert result["success"] is False


def test_sandbox_timeout():
    code = "import time\n\ndef test_slow():\n    time.sleep(5)\n"

    result = run_tests_in_sandbox(code, timeout=1)

    assert result["success"] is False
    assert "timed out" in result["stderr"]