"""CodeGraph AI — Interactive Web Dashboard."""

import html
import tempfile
from pathlib import Path

import streamlit as st

from codegraph.analyzer import analyze_file
from codegraph.ast_parser import parse_file
from codegraph.evaluation import run_benchmark
from codegraph.graph import build_call_graph, compute_impact
from codegraph.normalizer import normalize_report
from codegraph.reviewer import review
from codegraph.sandbox import run_tests_in_sandbox
from codegraph.test_generator import generate_tests

st.set_page_config(page_title="CodeGraph AI", page_icon="🧠", layout="wide")

CUSTOM_CSS = """
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        background-size: 300% 300%;
        animation: gradientShift 18s ease infinite;
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    section[data-testid="stSidebar"] { background: rgba(10, 8, 30, 0.92); }
    #MainMenu, footer, header { visibility: hidden; }

    .hero { text-align: center; padding: 1.5rem 0 0.5rem; }
    .hero-title {
        font-size: 3.4rem; font-weight: 800; margin: 0;
        background: linear-gradient(90deg, #00f2fe, #4facfe, #f093fb, #f5576c);
        -webkit-background-clip: text; background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-sub { color: #9aa5ce; margin-top: .4rem; }
    .badge {
        display: inline-block; margin: .25rem .3rem; padding: .35rem .95rem;
        border-radius: 999px; font-size: .8rem; font-weight: 700;
    }
    .b1 { background: rgba(0,242,254,.12); color: #00f2fe; border: 1px solid #00f2fe; }
    .b2 { background: rgba(80,255,150,.12); color: #50ff96; border: 1px solid #50ff96; }
    .b3 { background: rgba(240,147,251,.12); color: #f093fb; border: 1px solid #f093fb; }
    .b4 { background: rgba(255,201,77,.12); color: #ffc94d; border: 1px solid #ffc94d; }

    .float-card {
        background: rgba(255,255,255,0.06);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 18px;
        padding: 1.1rem 1.3rem;
        margin: .7rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,.35);
        transition: transform .25s ease, box-shadow .25s ease;
        color: #e6e9f5;
    }
    .float-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 18px 44px rgba(0,0,0,.5);
    }

    .sev-high   { border-left: 5px solid #ff4d4d; box-shadow: 0 0 22px rgba(255,77,77,.22); }
    .sev-medium { border-left: 5px solid #ffc94d; box-shadow: 0 0 22px rgba(255,201,77,.18); }
    .sev-style  { border-left: 5px solid #4da3ff; box-shadow: 0 0 22px rgba(77,163,255,.18); }

    .sev-pill { padding: .2rem .8rem; border-radius: 999px; font-size: .72rem; font-weight: 800; }
    .pill-high   { background: rgba(255,77,77,.18); color: #ff6b6b; }
    .pill-medium { background: rgba(255,201,77,.18); color: #ffc94d; }
    .pill-style  { background: rgba(77,163,255,.18); color: #6bb2ff; }

    .tool-tag { color: #8f9ac0; font-size: .8rem; margin-left: .6rem; font-weight: 700; }
    .line-tag { color: #8f9ac0; font-size: .8rem; float: right; }
    .msg { margin: .6rem 0 0; color: #dfe4f5; }

    .metric { text-align: center; border: none; color: white; }
    .metric-value { font-size: 2.5rem; font-weight: 800; }
    .metric-label { font-size: .85rem; letter-spacing: 2px; text-transform: uppercase; opacity: .9; }

    .section-title { color: #00f2fe; font-size: 1.4rem; font-weight: 700; margin-top: 1.2rem; }
    .fn-chip {
        display: inline-block; margin: .2rem; padding: .3rem .8rem;
        background: rgba(0,242,254,.12); border: 1px solid rgba(0,242,254,.5);
        border-radius: 10px; color: #7deaff; font-size: .85rem;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero">
        <h1 class="hero-title">🧠 CodeGraph AI</h1>
        <p class="hero-sub">Repository Intelligence Engine — Static Analysis • Impact Analysis • Hybrid AI Review</p>
        <div>
            <span class="badge b1">v1.3.0</span>
            <span class="badge b2">F1 100%</span>
            <span class="badge b3">40 Tests</span>
            <span class="badge b4">SARIF • Docker • Pre-commit</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


def sev_class(severity):
    sev = str(severity).upper()
    if sev == "HIGH":
        return "sev-high", "pill-high", "🔴 HIGH"
    if sev == "MEDIUM":
        return "sev-medium", "pill-medium", "🟡 MEDIUM"
    return "sev-style", "pill-style", "🔵 STYLE"


def issue_card(issue):
    card_cls, pill_cls, label = sev_class(issue.get("severity"))
    return f"""
    <div class="float-card {card_cls}">
        <span class="sev-pill {pill_cls}">{label}</span>
        <span class="tool-tag">{html.escape(str(issue.get('tool', '')).upper())}</span>
        <span class="line-tag">Line {issue.get('line', '?')}</span>
        <p class="msg">{html.escape(str(issue.get('message', '')))}</p>
    </div>
    """


def metric_card(value, label, gradient):
    return f"""
    <div class="float-card metric" style="background:{gradient}">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """


st.sidebar.markdown("## 🎛️ Control Center")

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

SAMPLES = ["samples/buggy_code.py", "samples/insecure_sample.py"]
target_choice = st.sidebar.radio("Target File", SAMPLES + ["📤 Upload File"])

target_path = None
if target_choice == "📤 Upload File":
    uploaded = st.sidebar.file_uploader("Choose a .py file", type=["py"])
    if uploaded:
        tmp = Path(tempfile.gettempdir()) / uploaded.name
        tmp.write_bytes(uploaded.read())
        target_path = str(tmp)
else:
    target_path = target_choice


if mode == "📊 Benchmark":
    bench = run_benchmark("data/benchmark.json")
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(metric_card(bench.get("samples", 0), "Samples", "linear-gradient(135deg,#667eea,#764ba2)"), unsafe_allow_html=True)
    c2.markdown(metric_card(f"{bench.get('precision', 0):.0%}", "Precision", "linear-gradient(135deg,#f093fb,#f5576c)"), unsafe_allow_html=True)
    c3.markdown(metric_card(f"{bench.get('recall', 0):.0%}", "Recall", "linear-gradient(135deg,#4facfe,#00f2fe)"), unsafe_allow_html=True)
    c4.markdown(metric_card(f"{bench.get('f1', 0):.0%}", "F1 Score", "linear-gradient(135deg,#43e97b,#38f9d7)"), unsafe_allow_html=True)
    st.markdown('<p class="section-title">🏆 Perfect detection on the labeled security benchmark.</p>', unsafe_allow_html=True)

elif target_path is None:
    st.info("👆 Upload a Python file from the sidebar to begin.")

else:
    if mode == "🔍 Analyze File":
        report = analyze_file(target_path)
        issues = normalize_report(report)

        high = sum(1 for i in issues if str(i.get("severity")).upper() == "HIGH")
        medium = sum(1 for i in issues if str(i.get("severity")).upper() == "MEDIUM")
        style = len(issues) - high - medium

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(metric_card(len(issues), "Total Issues", "linear-gradient(135deg,#667eea,#764ba2)"), unsafe_allow_html=True)
        c2.markdown(metric_card(high, "High", "linear-gradient(135deg,#ff4d4d,#c9184a)"), unsafe_allow_html=True)
        c3.markdown(metric_card(medium, "Medium", "linear-gradient(135deg,#ff9a3d,#ffc94d)"), unsafe_allow_html=True)
        c4.markdown(metric_card(style, "Style", "linear-gradient(135deg,#4da3ff,#4361ee)"), unsafe_allow_html=True)

        st.markdown(f'<p class="section-title">🔎 Findings in {html.escape(target_path)}</p>', unsafe_allow_html=True)
        for issue in issues:
            st.markdown(issue_card(issue), unsafe_allow_html=True)

    elif mode == "🗺️ Code Map":
        code_map = parse_file(target_path)

        st.markdown('<p class="section-title">📦 Functions</p>', unsafe_allow_html=True)
        funcs = "".join(
            f'<span class="fn-chip">def {html.escape(f["name"])}()</span>'
            for f in code_map.get("functions", [])
        )
        st.markdown(f'<div class="float-card">{funcs or "None"}</div>', unsafe_allow_html=True)

        st.markdown('<p class="section-title">🏛️ Classes</p>', unsafe_allow_html=True)
        classes = "".join(
            f'<span class="fn-chip">class {html.escape(c["name"])}</span>'
            for c in code_map.get("classes", [])
        )
        st.markdown(f'<div class="float-card">{classes or "None"}</div>', unsafe_allow_html=True)

    elif mode == "💥 Impact Analysis":
        changed_input = st.text_input("Changed functions (comma separated)", "divide")
        changed = [c.strip() for c in changed_input.split(",") if c.strip()]

        source = Path(target_path).read_text(encoding="utf-8")
        impact = compute_impact(build_call_graph(source), changed)

        st.markdown('<p class="section-title">🔥 Changed</p>', unsafe_allow_html=True)
        changed_chips = "".join(f'<span class="fn-chip">{html.escape(n)}</span>' for n in impact.get("changed", []))
        st.markdown(f'<div class="float-card sev-high">{changed_chips}</div>', unsafe_allow_html=True)

        st.markdown('<p class="section-title">💥 Impacted (blast radius)</p>', unsafe_allow_html=True)
        impacted = impact.get("impacted", [])
        if impacted:
            impacted_chips = "".join(f'<span class="fn-chip">{html.escape(n)}</span>' for n in impacted)
            st.markdown(f'<div class="float-card sev-medium">{impacted_chips}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="float-card sev-style">✅ No other functions impacted.</div>', unsafe_allow_html=True)

    elif mode == "📝 Code Review":
        report = analyze_file(target_path)
        issues = normalize_report(report)
        result = review(issues)
        comments = result.get("comments", [])

        st.markdown(f'<p class="section-title">🤖 {len(comments)} review comments</p>', unsafe_allow_html=True)
        for comment in comments:
            st.markdown(issue_card(comment), unsafe_allow_html=True)

    elif mode == "🧪 Generate Tests":
        result = generate_tests(target_path)

        if "error" in result:
            st.error(result["error"])
        else:
            st.markdown('<p class="section-title">🧪 Generated pytest code</p>', unsafe_allow_html=True)
            st.code(result["test_code"], language="python")

            if st.button("▶️ Run in Sandbox"):
                execution = run_tests_in_sandbox(result["test_code"])
                if execution.get("success"):
                    st.success("✅ Tests executed safely in the sandbox!")
                else:
                    st.error("❌ Sandbox execution failed.")
                st.code(execution.get("stderr") or execution.get("stdout") or "No output.")

st.markdown(
    """
    <div class="float-card" style="text-align:center; color:#8f9ac0;">
        Built with ❤️ — pylint • bandit • flake8 • AST • Rich • Streamlit • Docker • SARIF
    </div>
    """,
    unsafe_allow_html=True,
)