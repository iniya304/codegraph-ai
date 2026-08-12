"""Beautiful terminal output using Rich."""

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

console = Console()


def print_issues(issues):
    if not issues:
        console.print("[bold green]✅ No issues found! Code is clean.[/bold green]")
        return

    table = Table(
        title=f"⚠️ Found {len(issues)} Issues",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Severity", style="bold")
    table.add_column("Tool")
    table.add_column("Line", justify="right")
    table.add_column("Message", style="cyan")

    for issue in issues:
        severity = str(issue.get("severity", "info")).upper()
        tool = issue.get("tool", "unknown")
        line = str(issue.get("line", "?"))
        message = issue.get("message", "")

        if severity == "HIGH":
            sev_style = "[bold red]🔴 HIGH[/bold red]"
        elif severity == "MEDIUM":
            sev_style = "[bold yellow]🟡 MEDIUM[/bold yellow]"
        else:
            sev_style = "[bold blue]🔵 STYLE[/bold blue]"

        table.add_row(sev_style, tool, line, message)

    console.print(table)


def print_code_map(code_map):
    console.print(Panel("[bold]🗺️ Code Map[/bold]", border_style="blue"))

    functions = code_map.get("functions", [])
    if functions:
        console.print("[bold]📦 Functions:[/bold]")
        for func in functions:
            console.print(
                f"  [green]def[/green] [cyan]{func['name']}[/cyan]() - [dim]line {func['line']}[/dim]"
            )

    classes = code_map.get("classes", [])
    if classes:
        console.print("\n[bold]🏛️ Classes:[/bold]")
        for cls in classes:
            console.print(f"  [magenta]class[/magenta] [cyan]{cls['name']}[/cyan]")


def print_impact(impact):
    changed = impact.get("changed", [])
    impacted = impact.get("impacted", [])

    console.print(
        Panel(
            f"[bold]💥 Impact Analysis[/bold]\nChanged: [red]{', '.join(changed)}[/red]",
            border_style="red",
        )
    )

    if impacted:
        console.print(
            f"\n[bold yellow]⚠️ Impacted Functions ({len(impacted)}):[/bold yellow]"
        )
        for fn in impacted:
            console.print(f"  [yellow]→ {fn}()[/yellow]")
    else:
        console.print("\n[bold green]✅ No other functions are impacted.[/bold green]")


def print_test_code(code):
    console.print(Panel("[bold]🧪 Generated Test Code[/bold]", border_style="green"))
    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)


def print_benchmark(bench):
    table = Table(
        title="📊 Benchmark Results", show_header=True, header_style="bold cyan"
    )
    table.add_column("Metric")
    table.add_column("Score", justify="right")

    table.add_row("Samples", str(bench.get("samples", 0)))
    table.add_row("Precision", f"{bench.get('precision', 0):.1%}")
    table.add_row("Recall", f"{bench.get('recall', 0):.1%}")
    table.add_row("F1 Score", f"[bold green]{bench.get('f1', 0):.1%}[/bold green]")

    console.print(table)


def print_pr_report(result):
    """
    Print a full pull request review report.
    """
    console.print(
        Panel(
            f"[bold]🤖 PR #{result['number']}: {result['title']}[/bold]\n"
            f"[dim]{result['owner']}/{result['repo']} — "
            f"{result['changed_files']} changed files, "
            f"{result['reviewed_files']} reviewed[/dim]",
            border_style="magenta",
        )
    )

    for report in result.get("reports", []):
        console.print(f"\n[bold cyan]📄 {report['file']}[/bold cyan]")
        print_issues(report.get("comments", []))