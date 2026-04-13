"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

try:
    from src.recommender import load_songs, recommend_songs
except ImportError:
    from recommender import load_songs, recommend_songs


# --- User Profiles ---

PROFILES = {
    "High-Energy Pop Lover": {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.9,
        "target_valence": 0.85,
    },
    "Chill Lofi Student": {
        "favorite_genre": "lofi",
        "favorite_mood": "focused",
        "target_energy": 0.35,
        "target_valence": 0.55,
    },
    "Deep Intense Rock Fan": {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.9,
        "target_valence": 0.45,
    },
    "Conflicted User": {
        # High energy but sad mood — contradictory preferences
        "favorite_genre": "edm",
        "favorite_mood": "moody",
        "target_energy": 0.9,
        "target_valence": 0.35,
    },
    "Edge Case (All Center)": {
        # All numeric preferences at exactly 0.5 — reveals genre dominance
        "favorite_genre": "indie pop",
        "favorite_mood": "happy",
        "target_energy": 0.5,
        "target_valence": 0.5,
    },
}


def format_recommendations(results, profile_name: str, k: int = 5) -> None:
    """Format recommendations for terminal display with reasons."""
    separator = "=" * 60
    print(f"\n{separator}")
    print(f"TOP {min(k, len(results))} RECOMMENDATIONS FOR: {profile_name.upper()}")
    print(f"{separator}")

    for i, rec in enumerate(results, 1):
        song = rec["song"]
        score = rec["score"]
        reasons = rec["reasons"]

        # Format: #1  Title — Artist  [Genre / Mood]
        print(f"#{i}  {song['title']} — {song['artist']}  [{song['genre']} / {song['mood']}]")
        print(f"    Score: {score:.2f}")
        print(f"    Why: {', '.join(reasons)}")
        print()

    print(separator)
    print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"\nLoaded {len(songs)} songs from data/songs.csv")

    for profile_name, user_prefs in PROFILES.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        format_recommendations(recommendations, profile_name, k=5)


if __name__ == "__main__":
    main()
