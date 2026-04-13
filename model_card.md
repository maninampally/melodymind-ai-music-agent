# 🎧 Model Card: VibeFinder 1.0

## 1. Model Name  

**VibeFinder 1.0** — A lightweight content-based music recommender that discovers personalized songs based on genre, mood, and audio features (energy and valence).

---

## 2. Intended Use  

VibeFinder is designed as an **educational demonstration**, not a production tool. It shows how simple weighted scoring can mimic real recommendation behavior and is used to teach the difference between collaborative filtering and content-based approaches. It is intended for classroom exploration of algorithmic bias and filter bubbles, particularly for users whose preferences are well-defined and mainstream (e.g., "I like high-energy pop" or "I want chill lofi studying music").

**Assumptions about the user:** The system assumes users have clear, stable preferences in a single genre and mood, and that energy/valence are good proxies for musical fit. It does NOT assume the user will provide feedback or allow learning from behavior.

**Non-Intended Use:** VibeFinder should NOT be used as a production recommendation engine for real users. It is not suitable for personalized playlist generation in any commercial product, for making decisions about what content creators or artists to promote, or for any use case where fairness, diversity, or scale matters. The catalog is too small (20 songs), the scoring is purely rule-based with no learning, and it lacks safeguards against filter bubbles or underrepresentation of genres.

---

## 3. How the Model Works  

When you give the recommender a user profile (genre, mood, target energy, target valence), it scores every song in the catalog on four dimensions:

1. **Genre Match:** Does the song match your favorite genre? If yes, +2.0 points. If no, +0.0.
2. **Mood Match:** Does the song match your favorite mood? If yes, +1.0 point. If no, +0.0.
3. **Energy Proximity:** How close is the song's energy to your target? It calculates `1.5 * (1 - |song_energy - target_energy|)`, so a perfect match scores 1.5 and a complete opposite (you want calm, song is intense) scores 0.0.
4. **Valence Match:** How close is the song's emotional brightness to your target? Similar formula: `1.0 * (1 - |song_valence - target_valence|)`.

The system adds up all four scores and ranks songs from highest to lowest. It returns the top 5 with an explanation of why each song scored well.

**Why these weights?** Genre (2.0) is weighted heaviest because it's the most intuitive filter—people usually start by saying "I want rock" or "I want jazz." Mood (1.0) matters but is secondary. Energy and valence together make up the "vibe" and can partially compensate if genre is missing.

---

## 4. Data  

The catalog starts with 10 songs and was expanded to **20 songs** representing 10 genres: pop, lofi, rock, edm, jazz, ambient, synthwave, folk, metal, classical, r&b, hip hop, indie pop, soul, and indie folk.

**Genres and distribution:**
- Well-represented: lofi (4 songs, 20%), pop (3 songs), edm (2 songs)
- Underrepresented: folk, metal, classical, r&b, soul, indie folk (1 song each)
- Missing entirely: reggae, country, electronic, K-pop, etc.

**Moods represented:** happy, intense, chill, moody, focused, melancholic, aggressive, euphoric, nostalgic, romantic, relaxed

**What's missing:**
- Lyrics and language
- Artist popularity or trending status
- User listening history or feedback
- Song release date or era
- Instrumental vs. vocal distinction
- Sub-genre granularity (e.g., "sludge metal" vs. just "metal")

---

## 5. Strengths  

**Case 1: Mainstream single-genre users (high energy pop lovers, chill lofi students)**  
The recommender excels here. A user who says "I like high-energy happy pop" consistently gets pop songs with high energy and bright mood at the top. Score: 5/5 for accuracy.

**Case 2: Users with strong mood preferences**  
A user who wants calm, focused studying music gets lofi and ambient tracks ranked high even if genre doesn't match perfectly, because energy and valence align.

**Case 3: Clear contradictions are handled transparently**  
A user who wants "aggressive rock" sees Storm Runner (rock, intense) at the top with +2.0 for genre and +1.0 for mood. The system is honest: genre and mood dominate, energy and valence are secondary.

---

## 6. Limitations and Bias 

**Limitation 1: Genre Dominance (Filter Bubble)**  
The +2.0 genre weight creates strong categorical silos. A rock fan might see 4 of the top 5 results be rock songs, even if other genres have better energy/valence matches. Users never explore outside their stated preference. This is a **deliberate trade-off**: clear, predictable results in exchange for creativity.

**Limitation 2: Dataset Skew**  
Four lofi songs (20%) means lofi users get spoiled for choice, while classical, metal, and folk users (1 song each) get minimal recommendations. The system cannot suggest "try folk" if there's only one folk song.

**Limitation 3: No Exploration or Serendipity**  
Run the recommender 100 times with the same profile, and you get the exact same top 5 every time. There is zero randomness, no "maybe try something different," no learning from feedback. The system is pure exploitation; it never explores.

**Limitation 4: Energy/Valence Cliff Effects**  
If you want high-energy songs (0.9) but a song has energy 0.0, it scores only 0.0 from energy—a harsh penalty. A song at 0.7 scores 1.35, which is better than a perfect mood/genre match without good energy coverage. This creates unintuitive tie-breaking.

**Limitation 5: Conflicting Preferences Are Not Resolved**  
If a user likes "high-energy sad music" (energy=0.9 but valence=0.35), the system treats these as independent demands and scores accordingly. There's no logic to say "okay, you want intense sad songs—that's a specific subgenre."

**Limitation 6: No Cold-Start for Underrepresented Genres**  
A user whose favorite genre is "metal" sees only one song rank first, then defaults to other genres. The system cannot infer that "rock" or "synthwave" are reasonable alternatives.

---

## 7. Evaluation  

**Tested Profiles:**

1. **High-Energy Pop Lover** (pop, happy, energy=0.9, valence=0.85)  
   Top result: Sunrise City (pop, 5.37/5.5 points) ✓ Correct. Pop + happy + high energy matches perfectly.

2. **Chill Lofi Student** (lofi, focused, energy=0.35, valence=0.55)  
   Top results: All lofi. Perfectly captured. Focus Flow scores 5.38. ✓ Correct.

3. **Deep Intense Rock Fan** (rock, intense, energy=0.9, valence=0.45)  
   Top result: Storm Runner (rock, 5.45/5.5) ✓ Correct. But positions 2–5 drop sharply to non-rock options (Gym Hero, pop, scores 3.13). **Observation:** Genre is the primary differentiator; without it, profiles collapse into energy/valence matching.

4. **Conflicted User** (edm, moody, energy=0.9, valence=0.35)  
   Top results: Golden Hour Rush and Neon Heartbeat (both edm) because genre dominates. **Observation:** The system cannot resolve the contradiction "high-energy but sad"—it just scores genre match highest and lets energy/valence fight it out secondarily.

5. **Edge Case User** (indie pop, happy, all numeric pref = 0.5)  
   Top result: Rooftop Lights (indie pop, 4.80/5.5). **Observation:** Even with middling preferences, genre match + a weak mood match pushes one song to dominate, showing genre bias is fundamental.

**Surprises:**
- How consistently genre (2.0) outweighs everything else—it's truly the dominant feature.
- How little the energy/valence formulas spread the scores; most songs between top 5 differ by only 1–2 points.
- How underrepresentation hurts: rock has only 1 song in the catalog, so rock fans get bottom ranking after that one hit.

---

## 8. Future Work  

**Idea 1: Add Diversity Penalty**  
After sorting, check if the top 5 are too homogeneous (all pop, all lofi). Penalize songs whose genre is already in the top 3, forcing the recommender to suggest cross-genre variety.

**Idea 2: Implement Genre Fallbacks**  
Create a genre similarity matrix (rock ← → metal, lofi ← → ambient) so that when a user's favorite genre has few songs, the system gracefully switches to similar genres.

**Idea 3: Add Collaborative Filtering Layer**  
Ask "Do other users with similar taste to me like songs outside my usual genre?" and give those a small boost. This enables emergent cross-genre discovery without breaking the content-based foundation.

**Idea 4: Support Feedback & Reranking**  
Let the user say "I didn't like that recommendation" and reweight the features dynamically (e.g., "okay, maybe genre isn't as important to you as I thought").

---

## 9. Personal Reflection  

Building VibeFinder taught me that recommendation systems are much simpler (and much more biased) than I expected. I thought collaborative filtering would be magic, but after implementing basic content-based scoring, I realized the real complexity is in handling edge cases, conflicting preferences, and dataset bias—not in the formula itself.

The biggest surprise was watching the genre weight (2.0) completely dominate outcomes. Even with perfect energy and valence matches from different genres, same-genre songs always ranked higher. This showed me why real platforms spend so much effort on diversity mechanics and why filter bubbles are such a hard problem: the math naturally concentrates results.

I needed to double-check our energy/valence formulas several times because Copilot's first suggestion used squared differences, which I questioned and tested against. The absolute-difference formula felt more intuitive and worked better in practice.

What struck me about even this simple algorithm is that it "feels" like real recommendations—users intuitively understand why they're ranked a certain way. The reasons printed out ("+2.0 genre match, +1.5 energy proximity") make sense. But underneath, the system is purely mechanical and reproducible, with no serendipity. This makes me appreciate why TikTok and Spotify invest in randomization and exploration features; without them, you're trapped in a hall of mirrors.

Next, I'd implement collaborative filtering to see if real user behavior data reduces filter bubbles better than content-based alone. I'd also want to add explicit diversity penalties and test whether they improve perceived recommendation quality without feeling random.
