import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from agent.orchestrator import run_agent

console = Console()


def main():
    if len(sys.argv) < 2:
        console.print("[bold red]Usage:[/] python -m agent.cli \"your query here\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    console.print(Panel(f"[bold cyan]Query:[/] {query}", title="MelodyMind Agent"))

    success, msg, trace = run_agent(query)

    if not success:
        console.print(Panel(f"[bold red]{msg}[/]", title="Refused"))
        return

    console.print(Panel(
        f"Intent: {trace.plan.intent}\n"
        f"Genre: {trace.plan.desired_genre}\n"
        f"Mood: {trace.plan.desired_mood}\n"
        f"Energy: {trace.plan.desired_energy}\n"
        f"Keywords: {', '.join(trace.plan.keywords)}",
        title="Step 1: Plan",
    ))

    console.print(f"[dim]Step 2: Retrieved {trace.retrieved_count} candidates[/]")
    console.print(f"[dim]Step 3: Loaded {len(trace.rag_context_used)} RAG context chunks[/]")

    table = Table(title="Top 5 Recommendations", show_lines=True)
    table.add_column("#", style="cyan", no_wrap=True)
    table.add_column("Song", style="bold")
    table.add_column("Genre / Mood")
    table.add_column("Confidence", justify="right")
    table.add_column("Explanation")

    for i, rec in enumerate(trace.recommendations, 1):
        table.add_row(
            str(i),
            f"{rec.title}\n[dim]{rec.artist}[/]",
            f"{rec.genre} / {rec.mood}",
            f"{rec.confidence:.2f}",
            rec.explanation,
        )

    console.print(table)
    console.print(f"\n[green]Completed in {trace.duration_seconds}s.[/]")


if __name__ == "__main__":
    main()
