"""CodeGraph AI - Interactive Web Dashboard."""

import streamlit as st

from codegraph.analyzer import analyze_file
from codegraph.ast_parser import parse_file
from codegraph.evaluation import run_benchmark
from codegraph.graph import build_call_graph, compute_impact
from codegraph.normalizer import normalize_report
from codegraph.reviewer import review
from codegraph.sandbox import run_tests_in_sandbox
from codegraph.test_generator import generate_tests

st.set_page_config(
    page_title="CodeGraph AI",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 CodeGraph AI")
st.caption("Repository Intelligence Engine — Static Analysis, Impact Analysis & Review")

# Sidebar
st.sidebar.header("⚙️ Controls")
mode = st.sidebar.radio(
    "Select Mode",
    [
        "🔍 Analyze File",
        "🗺️ Code Map",
        "💥 Impact Analysis",
        "📝 Code Review",
        "🧪 Generate Tests",
        "📊 Benchmark",
    ],
)

file_choice = st.sidebar.radio(
    "Target File",
    ["samples/buggy_code.py", "samples/insecure_sample.py", "Upload File"],
)

target_file = None

if file_choice == "Upload File":
    uploaded = st.sidebar.file_uploader("Upload a Python file", type=["py"])
    if uploaded is not None:
        with open("uploaded_temp.py", "wb") as f:
            f.write(uploaded.getbuffer())
        target_file = "uploaded_temp.py"
    else:
        st.info("⬅️ Upload a file to begin.")
        st.stop()
else:
    target_file = file_choice

# ─── MODE: Analyze File ───────────────────────────────────────────────
if mode == "🔍 Analyze File":
    st.header(f"🔍 Analysis: `{target_file}`")

    with st.spinner("Running pylint, bandit, flake8..."):
        report = analyze_file(target_file)
        issues = normalize_report(report)

    if not issues:
        st.success("✅ No issues found!")
    else:
        st.warning(f"⚠️ Found **{len(issues)}** issues")

        for issue in issues:
            severity = issue.get("severity", "info")
            line = issue.get("line", "?")
            tool = issue.get("tool", "unknown")
            message = issue.get("message", "")

            if severity == "high":
                st.error(f"🔴 **[{tool.upper()}] Line {line}** — {message}")
            elif severity == "medium":
                st.warning(f"🟡 **[{tool.upper()}] Line {line}** — {message}")
            else:
                st.info(f"🔵 **[{tool.upper()}] Line {line}** — {message}")

# ─── MODE: Code Map ───────────────────────────────────────────────────
elif mode == "🗺️ Code Map":
    st.header(f"🗺️ Code Map: `{target_file}`")

    code_map = parse_file(target_file)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📦 Functions")
        functions = code_map.get("functions", [])
        if functions:
            for func in functions:
                args_str = ", ".join(func.get("args", []))
                st.markdown(f"- `def {func['name']}({args_str})` — line {func['line']}")
        else:
            st.info("No functions found.")

    with col2:
        st.subheader("🏛️ Classes")
        classes = code_map.get("classes", [])
        if classes:
            for cls in classes:
                st.markdown(f"- `class {cls['name']}` — line {cls['line']}")
                for method in cls.get("methods", []):
                    st.markdown(f"&nbsp;&nbsp;└─ `{method}()`")
        else:
            st.info("No classes found.")

    st.subheader("📥 Imports")
    imports = code_map.get("imports", [])
    if imports:
        st.code(", ".join(imports))
    else:
        st.info("No imports found.")

# ─── MODE: Impact Analysis ───────────────────────────────────────────
elif mode == "💥 Impact Analysis":
    st.header(f"💥 Impact Analysis: `{target_file}`")

    code_map = parse_file(target_file)
    functions = [
        f["name"]
        for f in code_map.get("functions", [])
        if not f.get("args") or f["args"][0] != "self"
    ]

    if not functions:
        st.info("No functions found for impact analysis.")
        st.stop()

    changed_fn = st.selectbox("Which function changed?", functions)

    with open(target_file, "r", encoding="utf-8") as f:
        source = f.read()

    call_graph = build_call_graph(source)
    impact = compute_impact(call_graph, [changed_fn])

    st.subheader("📞 Call Graph")
    for caller, callees in call_graph.items():
        if callees:
            st.markdown(f"- `{caller}()` → {', '.join(f'`{c}()`' for c in callees)}")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔧 Changed")
        for fn in impact.get("changed", []):
            st.markdown(f"- `{fn}()`")

    with col2:
        st.subheader("💥 Impacted")
        impacted = impact.get("impacted", [])
        if impacted:
            for fn in impacted:
                st.error(f"- `{fn}()` may break!")
        else:
            st.success("✅ No other functions are impacted.")

# ─── MODE: Code Review ───────────────────────────────────────────────
elif mode == "📝 Code Review":
    st.header(f"📝 Code Review: `{target_file}`")

    with st.spinner("Reviewing code..."):
        report = analyze_file(target_file)
        issues = normalize_report(report)
        result = review(issues)

    st.subheader(f"Review Source: `{result.get('source', 'unknown')}`")

    comments = result.get("comments", [])
    if not comments:
        st.success("✅ No review comments.")
    else:
        for comment in comments:
            severity = comment.get("severity", "info")
            confidence = comment.get("confidence", 0)
            message = comment.get("message", "")
            line = comment.get("line", "?")
            tool = comment.get("tool", "")

            badge = f"`{tool}` | confidence: {confidence:.0%}"

            if severity == "high":
                st.error(f"🔴 **Line {line}** {badge}\n\n{message}")
            elif severity == "medium":
                st.warning(f"🟡 **Line {line}** {badge}\n\n{message}")
            else:
                st.info(f"🔵 **Line {line}** {badge}\n\n{message}")

# ─── MODE: Generate Tests ───────────────────────────────────────────
elif mode == "🧪 Generate Tests":
    st.header(f"🧪 Test Generation: `{target_file}`")

    with st.spinner("Generating tests..."):
        result = generate_tests(target_file)

    if "error" in result:
        st.error(result["error"])
        st.stop()

    st.subheader("📄 Generated Test Code")
    st.code(result.get("test_code", ""), language="python")

    run_it = st.button("🚀 Run Tests in Sandbox")

    if run_it:
        with st.spinner("Executing in sandbox..."):
            execution = run_tests_in_sandbox(result.get("test_code", ""))

        if execution.get("success"):
            st.success("✅ All generated tests passed!")
        else:
            st.error("❌ Some tests failed.")

        with st.expander("📋 Full Output"):
            st.text(execution.get("stdout", ""))
            if execution.get("stderr"):
                st.text(execution.get("stderr", ""))

# ─── MODE: Benchmark ─────────────────────────────────────────────────
elif mode == "📊 Benchmark":
    st.header("📊 Evaluation Benchmark")

    with st.spinner("Running benchmark..."):
        bench = run_benchmark("data/benchmark.json")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Samples", bench.get("samples", 0))
    with col2:
        st.metric("Precision", f"{bench.get('precision', 0):.1%}")
    with col3:
        st.metric("Recall", f"{bench.get('recall', 0):.1%}")
    with col4:
        st.metric("F1 Score", f"{bench.get('f1', 0):.1%}")

    st.divider()

    results = bench.get("results", [])
    for r in results:
        st.markdown(
            f"**`{r.get('file', '')}`** — "
            f"TP: {r.get('true_positives', 0)} | "
            f"FP: {r.get('false_positives', 0)} | "
            f"FN: {r.get('false_negatives', 0)} | "
            f"Precision: {r.get('precision', 0):.1%} | "
            f"Recall: {r.get('recall', 0):.1%}"
        )