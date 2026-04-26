from src.recommender import Song, UserProfile, Recommender, load_songs, score_song, recommend_songs
from pathlib import Path
import pytest

SONGS_CSV = str(Path(__file__).parent.parent / "data" / "songs.csv")


def make_songs() -> list[Song]:
    return [
        Song(id=1, title="Pop Track", artist="A", genre="pop", mood="happy",
             energy=0.8, tempo_bpm=120, valence=0.9, danceability=0.8, acousticness=0.2),
        Song(id=2, title="Lofi Loop", artist="B", genre="lofi", mood="chill",
             energy=0.4, tempo_bpm=80, valence=0.6, danceability=0.5, acousticness=0.9),
        Song(id=3, title="Rock Storm", artist="C", genre="rock", mood="intense",
             energy=0.95, tempo_bpm=160, valence=0.3, danceability=0.6, acousticness=0.1),
    ]


# --- OOP Recommender tests ---

def test_recommend_returns_correct_count():
    rec = Recommender(make_songs())
    user = UserProfile("pop", "happy", 0.8, False)
    assert len(rec.recommend(user, k=2)) == 2


def test_recommend_sorted_by_score():
    rec = Recommender(make_songs())
    user = UserProfile("pop", "happy", 0.8, False)
    results = rec.recommend(user, k=3)
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_recommend_genre_match_dominates():
    rec = Recommender(make_songs())
    user = UserProfile("lofi", "chill", 0.4, True)
    results = rec.recommend(user, k=1)
    assert results[0].genre == "lofi"


def test_explain_recommendation_non_empty():
    rec = Recommender(make_songs())
    user = UserProfile("pop", "happy", 0.8, False)
    explanation = rec.explain_recommendation(user, rec.songs[0])
    assert isinstance(explanation, str)
    assert len(explanation) > 0


def test_explain_includes_genre_match():
    rec = Recommender(make_songs())
    user = UserProfile("pop", "happy", 0.8, False)
    explanation = rec.explain_recommendation(user, rec.songs[0])
    assert "genre match" in explanation


# --- Functional score_song tests ---

def test_score_song_genre_match_adds_two():
    song = {"genre": "pop", "mood": "happy", "energy": 0.8, "valence": 0.9}
    prefs = {"favorite_genre": "pop", "favorite_mood": "chill", "target_energy": 0.8}
    score, reasons = score_song(prefs, song)
    assert any("genre match" in r for r in reasons)
    assert score >= 2.0


def test_score_song_mood_match_adds_one():
    song = {"genre": "rock", "mood": "happy", "energy": 0.5, "valence": 0.5}
    prefs = {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.5}
    score, reasons = score_song(prefs, song)
    assert any("mood match" in r for r in reasons)


def test_score_song_no_match_still_returns_score():
    song = {"genre": "metal", "mood": "aggressive", "energy": 0.9, "valence": 0.2}
    prefs = {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.5}
    score, reasons = score_song(prefs, song)
    assert score >= 0.0
    assert len(reasons) > 0


def test_score_song_with_valence():
    song = {"genre": "pop", "mood": "happy", "energy": 0.8, "valence": 0.9}
    prefs = {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.8, "target_valence": 0.9}
    score, reasons = score_song(prefs, song)
    assert any("valence" in r for r in reasons)


# --- Functional recommend_songs tests ---

def test_recommend_songs_returns_top_k():
    songs = load_songs(SONGS_CSV)
    prefs = {"favorite_genre": "lofi", "favorite_mood": "chill", "target_energy": 0.3}
    results = recommend_songs(prefs, songs, k=3)
    assert len(results) == 3


def test_recommend_songs_sorted_descending():
    songs = load_songs(SONGS_CSV)
    prefs = {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.8}
    results = recommend_songs(prefs, songs, k=5)
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_recommend_songs_result_has_required_keys():
    songs = load_songs(SONGS_CSV)
    prefs = {"favorite_genre": "lofi", "favorite_mood": "focused", "target_energy": 0.3}
    results = recommend_songs(prefs, songs, k=1)
    assert "song" in results[0]
    assert "score" in results[0]
    assert "reasons" in results[0]


# --- load_songs tests ---

def test_load_songs_returns_20():
    songs = load_songs(SONGS_CSV)
    assert len(songs) == 20


def test_load_songs_field_types():
    songs = load_songs(SONGS_CSV)
    s = songs[0]
    assert isinstance(s["energy"], float)
    assert isinstance(s["valence"], float)
    assert isinstance(s["tempo_bpm"], int)
    assert isinstance(s["title"], str)


def test_load_songs_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_songs("nonexistent/path/songs.csv")


# --- Guardrail tests ---

def test_guardrail_accepts_music_query():
    from agent.guardrails import validate_input
    ok, msg, q = validate_input("I want chill lofi for studying")
    assert ok is True
    assert q.query == "I want chill lofi for studying"


def test_guardrail_rejects_stock_query():
    from agent.guardrails import validate_input
    ok, msg, _ = validate_input("give me stock tips")
    assert ok is False
    assert "stock" in msg


def test_guardrail_rejects_too_short():
    from agent.guardrails import validate_input
    ok, msg, _ = validate_input("hi")
    assert ok is False


def test_guardrail_no_false_positive_on_diagnostic():
    from agent.guardrails import validate_input
    ok, _, _ = validate_input("diagnostic jazz music for focus")
    assert ok is True


def test_guardrail_no_false_positive_on_investment_of_time():
    from agent.guardrails import validate_input
    ok, _, _ = validate_input("music worth investing time in")
    assert ok is True
