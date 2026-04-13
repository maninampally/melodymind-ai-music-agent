from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Score all songs against user profile and return top k sorted by score."""
        def song_score(song: Song) -> float:
            score = 0.0
            if song.genre == user.favorite_genre:
                score += 2.0
            if song.mood == user.favorite_mood:
                score += 1.0
            score += 1.5 * (1 - abs(song.energy - user.target_energy))
            if user.likes_acoustic:
                score += song.acousticness
            else:
                score += (1 - song.acousticness)
            return score

        return sorted(self.songs, key=song_score, reverse=True)[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation of why a song was recommended."""
        reasons = []
        if song.genre == user.favorite_genre:
            reasons.append("genre match (+2.0)")
        if song.mood == user.favorite_mood:
            reasons.append("mood match (+1.0)")
        energy_score = 1.5 * (1 - abs(song.energy - user.target_energy))
        reasons.append(f"energy proximity (+{energy_score:.2f})")
        acoustic_score = song.acousticness if user.likes_acoustic else (1 - song.acousticness)
        reasons.append(f"acousticness fit (+{acoustic_score:.2f})")
        return ", ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from CSV file and return list of dictionaries with properly typed fields."""
    import csv
    import os
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Songs CSV file not found at: {csv_path}")
    
    songs = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert numerical fields to appropriate types
                row['id'] = int(row['id'])
                row['energy'] = float(row['energy'])
                row['tempo_bpm'] = int(row['tempo_bpm'])
                row['valence'] = float(row['valence'])
                row['danceability'] = float(row['danceability'])
                row['acousticness'] = float(row['acousticness'])
                
                # Leave string fields as-is: title, artist, genre, mood
                songs.append(row)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Cannot read CSV file at {csv_path}: {e}")
    
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a song against user preferences and return (total_score, reasons list)."""
    total_score = 0.0
    reasons = []
    
    # Genre match: +2.0
    if song['genre'] == user_prefs['favorite_genre']:
        total_score += 2.0
        reasons.append("genre match (+2.0)")
    
    # Mood match: +1.0
    if song['mood'] == user_prefs['favorite_mood']:
        total_score += 1.0
        reasons.append("mood match (+1.0)")
    
    # Energy similarity: 1.5 * (1 - abs difference)
    energy_score = 1.5 * (1 - abs(song['energy'] - user_prefs['target_energy']))
    total_score += energy_score
    reasons.append(f"energy proximity (+{energy_score:.2f})")
    
    # Valence similarity (if target_valence exists)
    if 'target_valence' in user_prefs:
        valence_score = 1.0 * (1 - abs(song['valence'] - user_prefs['target_valence']))
        total_score += valence_score
        reasons.append(f"valence match (+{valence_score:.2f})")
    
    return (round(total_score, 2), reasons)

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Dict]:
    """Score all songs against user preferences and return top k ranked recommendations."""
    # Loop through all songs, score each one, and collect results
    results = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        results.append({
            "song": song,
            "score": score,
            "reasons": reasons
        })
    
    # Sort using sorted() (not .sort()) because:
    # - sorted() returns a new list (immutable, preserves original)
    # - .sort() modifies the list in-place (mutates state, less predictable)
    # - sorted() is more functional and easier to test/reason about
    ranked_results = sorted(results, key=lambda x: x["score"], reverse=True)
    
    # Return top k results (highest score first)
    return ranked_results[:k]
