"""Evaluation harness: compare baseline (Module 3) vs agentic system across 5 user profiles."""
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.recommender import recommend_songs, load_songs
from agent.orchestrator import run_agent

console = Console()

ROOT = Path(__file__).parent.parent
SONGS_CSV = str(ROOT / "data" / "songs.csv")

TEST_CASES = [
    {
        "name": "High-Energy Pop Lover",
        "user_prefs": {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.85, "target_valence": 0.9},
        "query": "Upbeat pop songs that make me feel happy and energetic",
    },
    {
        "name": "Chill Lofi Student",
        "user_prefs": {"favorite_genre": "lofi", "favorite_mood": "focused", "target_energy": 0.3, "target_valence": 0.5},
        "query": "Calm lofi music for studying and focusing",
    },
    {
        "name": "Deep Intense Rock Fan",
        "user_prefs": {"favorite_genre": "rock", "favorite_mood": "intense", "target_energy": 0.9, "target_valence": 0.4},
        "query": "Hard rock with intense energy",
    },
    {
        "name": "Conflicted User",
        "user_prefs": {"favorite_genre": "edm", "favorite_mood": "moody", "target_energy": 0.9, "target_valence": 0.2},
        "query": "High energy but sad and moody music",
    },
    {
        "name": "Edge Case (All Center)",
        "user_prefs": {"favorite_genre": "indie pop", "favorite_mood": "happy", "target_energy": 0.5, "target_valence": 0.5},
        "query": "Something balanced and happy",
    },
]


def diversity_score(genres: list[str]) -> float:
    if not genres:
        return 0.0
    return len(set(genres)) / len(genres)


def run_baseline(user_prefs: dict, songs: list) -> list[dict]:
    results = recommend_songs(user_prefs, songs, k=5)
    return [{
        "title": r["song"]["title"],
        "artist": r["song"]["artist"],
        "genre": r["song"]["genre"],
        "mood": r["song"]["mood"],
        "score": r["score"],
    } for r in results]


def run_agent_system(query: str) -> list[dict]:
    success, _, trace = run_agent(query)
    if not success or trace is None:
        return []
    return [{
        "title": r.title,
        "artist": r.artist,
        "genre": r.genre,
        "mood": r.mood,
        "score": r.confidence,
    } for r in trace.recommendations]


def main():
    console.print("[bold cyan]MelodyMind Evaluation Harness[/]\n")
    console.print("Comparing baseline (Module 3 rule-based) vs agentic LLM system\n")

    songs = load_songs(SONGS_CSV)

    summary_table = Table(title="Baseline vs Agentic Comparison", show_lines=True)
    summary_table.add_column("Profile", style="bold")
    summary_table.add_column("Baseline Diversity", justify="right")
    summary_table.add_column("Agentic Diversity", justify="right")
    summary_table.add_column("Baseline Top Genre")
    summary_table.add_column("Agentic Top Genre")
    summary_table.add_column("Status", style="green")

    pass_count = 0
    total = len(TEST_CASES)

    for case in TEST_CASES:
        console.print(f"[yellow]Running: {case['name']}[/]")

        baseline_results = run_baseline(case["user_prefs"], songs)
        agent_results = run_agent_system(case["query"])

        baseline_genres = [r["genre"] for r in baseline_results]
        agent_genres = [r["genre"] for r in agent_results]

        baseline_div = diversity_score(baseline_genres)
        agent_div = diversity_score(agent_genres)

        status = "PASS" if agent_results else "FAIL"
        if status == "PASS":
            pass_count += 1

        summary_table.add_row(
            case["name"],
            f"{baseline_div:.2f}",
            f"{agent_div:.2f}",
            baseline_genres[0] if baseline_genres else "—",
            agent_genres[0] if agent_genres else "—",
            status,
        )

    console.print()
    console.print(summary_table)
    console.print(f"\n[bold]Result: {pass_count}/{total} tests passed[/]")


if __name__ == "__main__":
    main()
