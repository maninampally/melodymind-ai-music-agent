# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

This version implements a content-based music recommender in Python. It loads a 20-song catalog from a CSV file, scores each song against a user taste profile using weighted dimensions (genre, mood, energy, valence), and returns the top 5 ranked recommendations with a plain-language explanation of why each song scored the way it did. Five distinct user profiles are tested — from a high-energy pop lover to a conflicted user with contradictory preferences — to evaluate the system's strengths and bias patterns.

---

## How The System Works

Real-world platforms like Spotify and TikTok recommend music at scale by combining several kinds of signals. A major part of this is collaborative filtering, which looks at patterns across many users to find tracks that people with similar behavior tend to enjoy, while content signals come from the song itself, such as genre, mood, tempo, and audio characteristics. These systems also depend on implicit feedback like plays, skips, replays, likes, watch time, and completion rate, because those actions reveal preference even when users never explicitly rate a song. The result is a ranking system that learns from both the content of songs and the behavior of large user populations.

This simulator is intentionally simpler and uses a content-based approach only. Instead of learning from user history, it scores each song directly against a user profile using weighted features like genre, mood, energy, tempo, and valence, then recommends the highest-scoring matches. That means the system can work without interaction logs or a trained model, because it compares song attributes to the preferences you provide. It intentionally trades away large-scale personalization, behavioral learning, and real-world complexity in exchange for transparency, simplicity, and easy-to-understand scoring.

To answer the design prompts directly, each `Song` in this simulator uses the columns `genre`, `mood`, `energy`, `tempo_bpm`, and `valence`, while the `UserProfile` stores `favorite_genre`, `favorite_mood`, `target_energy`, and `target_valence`. The `Recommender` computes a score by giving higher points to songs whose genre and mood match the user's preferences and whose numeric features are close to the user's target values, then it sorts all songs by that score and returns the top results. In other words, the recommendation step is just a weighted comparison between the song data in `data/songs.csv` and the user's taste profile.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Terminal Output

Output from running `python -m src.main` across all 5 user profiles:

```
$ python -m src.main

Loaded 20 songs from data/songs.csv

============================================================
TOP 5 RECOMMENDATIONS FOR: HIGH-ENERGY POP LOVER
============================================================
#1  Sunrise City — Neon Echo  [pop / happy]
    Score: 5.37
    Why: genre match (+2.0), mood match (+1.0), energy proximity (+1.38), valence match (+0.99)

#2  Gym Hero — Max Pulse  [pop / intense]
    Score: 4.38
    Why: genre match (+2.0), energy proximity (+1.46), valence match (+0.92)

#3  Golden Hour Rush — Solar Drift  [edm / happy]
    Score: 3.47
    Why: mood match (+1.0), energy proximity (+1.48), valence match (+0.99)

#4  Rooftop Lights — Indigo Parade  [indie pop / happy]
    Score: 3.25
    Why: mood match (+1.0), energy proximity (+1.29), valence match (+0.96)

#5  Neon Heartbeat — Astra Nova  [edm / euphoric]
    Score: 2.40
    Why: energy proximity (+1.43), valence match (+0.97)

============================================================

============================================================
TOP 5 RECOMMENDATIONS FOR: CHILL LOFI STUDENT
============================================================
#1  Focus Flow — LoRoom  [lofi / focused]
    Score: 5.38
    Why: genre match (+2.0), mood match (+1.0), energy proximity (+1.42), valence match (+0.96)

#2  Library Rain — Paper Lanterns  [lofi / chill]
    Score: 4.45
    Why: genre match (+2.0), energy proximity (+1.50), valence match (+0.95)

#3  Midnight Coding — LoRoom  [lofi / chill]
    Score: 4.38
    Why: genre match (+2.0), energy proximity (+1.40), valence match (+0.99)

#4  Cloud Memoir — Soft Static  [lofi / nostalgic]
    Score: 4.34
    Why: genre match (+2.0), energy proximity (+1.38), valence match (+0.96)

#5  Streetlight Cipher — North Block  [hip hop / focused]
    Score: 3.09
    Why: mood match (+1.0), energy proximity (+1.11), valence match (+0.98)

============================================================

============================================================
TOP 5 RECOMMENDATIONS FOR: DEEP INTENSE ROCK FAN
============================================================
#1  Storm Runner — Voltline  [rock / intense]
    Score: 5.45
    Why: genre match (+2.0), mood match (+1.0), energy proximity (+1.48), valence match (+0.97)

#2  Gym Hero — Max Pulse  [pop / intense]
    Score: 3.13
    Why: mood match (+1.0), energy proximity (+1.46), valence match (+0.68)

#3  Night Drive Loop — Neon Echo  [synthwave / moody]
    Score: 2.23
    Why: energy proximity (+1.27), valence match (+0.96)

#4  Iron Pulse — Crimson Vale  [metal / aggressive]
    Score: 2.23
    Why: energy proximity (+1.40), valence match (+0.84)

#5  Golden Hour Rush — Solar Drift  [edm / happy]
    Score: 2.08
    Why: energy proximity (+1.48), valence match (+0.59)

============================================================

============================================================
TOP 5 RECOMMENDATIONS FOR: CONFLICTED USER
============================================================
#1  Golden Hour Rush — Solar Drift  [edm / happy]
    Score: 3.97
    Why: genre match (+2.0), energy proximity (+1.48), valence match (+0.49)

#2  Neon Heartbeat — Astra Nova  [edm / euphoric]
    Score: 3.89
    Why: genre match (+2.0), energy proximity (+1.43), valence match (+0.47)

#3  Night Drive Loop — Neon Echo  [synthwave / moody]
    Score: 3.13
    Why: mood match (+1.0), energy proximity (+1.27), valence match (+0.86)

#4  Storm Runner — Voltline  [rock / intense]
    Score: 2.35
    Why: energy proximity (+1.48), valence match (+0.87)

#5  Iron Pulse — Crimson Vale  [metal / aggressive]
    Score: 2.33
    Why: energy proximity (+1.40), valence match (+0.94)

============================================================

============================================================
TOP 5 RECOMMENDATIONS FOR: EDGE CASE (ALL CENTER)
============================================================
#1  Rooftop Lights — Indigo Parade  [indie pop / happy]
    Score: 4.80
    Why: genre match (+2.0), mood match (+1.0), energy proximity (+1.11), valence match (+0.69)

#2  Sunrise City — Neon Echo  [pop / happy]
    Score: 2.68
    Why: mood match (+1.0), energy proximity (+1.02), valence match (+0.66)

#3  Golden Hour Rush — Solar Drift  [edm / happy]
    Score: 2.56
    Why: mood match (+1.0), energy proximity (+0.92), valence match (+0.64)

#4  Midnight Coding — LoRoom  [lofi / chill]
    Score: 2.32
    Why: energy proximity (+1.38), valence match (+0.94)

#5  Streetlight Cipher — North Block  [hip hop / focused]
    Score: 2.27
    Why: energy proximity (+1.33), valence match (+0.93)

============================================================
```

---

## Experiments You Tried

**Experiment 1 — Five Distinct User Profiles**

I ran five different profiles through the recommender: High-Energy Pop Lover, Chill Lofi Student, Deep Intense Rock Fan, Conflicted User (high energy + sad mood), and an Edge Case with all numeric preferences at 0.5. Each returned very different top-5 lists, confirming the scoring dimensions are meaningfully differentiated.

**Experiment 2 — Genre Dominance Observation**

The genre weight of +2.0 consistently dominated rankings. For the Rock Fan profile, Storm Runner scored 5.45 (genre + mood + energy all aligned). The second-place song was Gym Hero at 3.13 — a gap of over 2 points — simply because there is only one rock song in the catalog. Genre match is the single largest score differentiator.

**Experiment 3 — Conflicted User (energy=0.9, mood=moody)**

A user who wants high-energy but sad/moody music got EDM songs at the top because the genre match dominated, even though the mood (moody) didn't match EDM's typical vibe. This revealed the algorithm cannot resolve contradictions — it just scores each dimension independently and sums them.

**Experiment 4 — Edge Case (all numerics at 0.5)**

With every numeric preference at the midpoint, the system still confidently ranked Rooftop Lights #1 (score 4.80) purely because it matched the genre ("indie pop") and mood ("happy"). This shows genre bias is structural: even with no strong numeric preferences, genre match alone is worth more than perfect energy + valence alignment from a different genre.

---

## Limitations and Risks

- **Tiny catalog (20 songs):** Underrepresented genres like rock, metal, classical, and folk have only one song each, so users with those preferences see the genre match once and then fall through to generic energy/valence ranking.
- **No learning or feedback:** The system gives the exact same top-5 every time for the same profile. There is no randomness, no exploration, and no way to say "I didn't like that song."
- **Genre creates a filter bubble:** The +2.0 genre weight means a genre match outweighs even perfect energy and valence alignment from a different genre, trapping users inside their stated preference.
- **Cannot resolve conflicting preferences:** A user who wants high energy but a sad mood will get high-energy songs regardless, because energy and mood are scored independently with no cross-feature logic.
- **No lyric, language, or cultural context:** Two songs can have identical energy and valence but feel completely different based on language, instrumentation, or cultural origin — features the system ignores entirely.

See `model_card.md` for a deeper analysis.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Building this recommender made it clear how quickly simple math creates the "feeling" of intelligence. Assigning a +2.0 for a genre match and a proximity formula for energy produced results that genuinely surprised me — they felt like real recommendations, not just arithmetic. But that feeling is an illusion: the system is fully deterministic, has no memory of what worked, and cannot discover anything outside the user's stated preferences. The gap between "feels smart" and "is smart" turned out to be very small to produce, and very large to close.

The most important lesson about bias came from watching genre dominate every single ranking. I expected energy and valence to matter more, but a 2-point genre bonus consistently outweighed a 1.5-point maximum energy score plus a 1.0-point valence score combined. Real platforms spend enormous engineering effort fighting this kind of categorical lock-in — diversity penalties, exploration boosts, serendipity mechanics — because left alone, any scoring system concentrates results around whatever dimension has the heaviest weight.
