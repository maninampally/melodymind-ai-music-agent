# Reflection — Profile Comparisons

## Profile 1 vs Profile 2: High-Energy Pop Lover vs Chill Lofi Student

These two profiles produced almost completely opposite results. The Pop Lover got Sunrise City (#1, score 5.37) while the Lofi Student got Focus Flow (#1, score 5.38). Not a single song appeared in both top-5 lists. This makes intuitive sense: one profile is targeting genre=pop, energy≈0.9, and the other is targeting genre=lofi, energy≈0.35. Since the genre weight (+2.0) is the largest single scoring dimension, any song that doesn't match the stated genre is already at a 2-point disadvantage before energy or valence even come into play. Two people can both say "I like energetic music," but if one means pop and the other means lofi, the algorithm treats them as completely different users — which feels correct.

## Profile 2 vs Profile 3: Chill Lofi Student vs Deep Intense Rock Fan

Both profiles got completely different top results, but the rock fan's list was notably weaker after position #1. The lofi student got four lofi songs in the top 4 (scores 5.38 → 4.34), while the rock fan got only one rock song (#1 Storm Runner at 5.45) and then dropped to pop and synthwave songs scoring around 2–3 points. This is directly because the catalog has 4 lofi songs but only 1 rock song — the genre distribution in `data/songs.csv` directly shapes who gets "good" vs "mediocre" recommendations. A real lofi fan is well-served; a real rock fan is underserved after the first result.

## Profile 3 vs Profile 4: Deep Intense Rock Fan vs Conflicted User

The rock fan has internally consistent preferences (high energy + intense mood), while the conflicted user asks for high energy but a moody/sad emotional tone — a contradictory combination. The rock fan's #1 (Storm Runner, 5.45) is a strong match on all dimensions. The conflicted user's #1 (Golden Hour Rush, 3.97) is a weaker match because the mood dimension never aligns — EDM songs are categorized as "happy" or "euphoric," not "moody." The system cannot tell the conflicted user "you're asking for something that doesn't exist in the catalog"; it just finds the closest numeric match and returns it. This is where the algorithm feels most "wrong" to a real human — the results look reasonable on paper but wouldn't feel right in practice.

## Profile 4 vs Profile 5: Conflicted User vs Edge Case (All Center)

The conflicted user got EDM-heavy results (genre match dominated), while the edge case user with all preferences at 0.5 got indie pop at #1 purely from genre+mood match, with no strong energy/valence pull. What's interesting about the edge case is that even with the most "neutral" possible numeric preferences, the genre weight still created a clear #1 (score 4.80) far ahead of #2 (score 2.68). This reveals that the system is never truly neutral — genre bias is baked in structurally. A user with no strong numeric preferences still gets pulled toward their stated genre, and the runner-up songs are not close behind. Both profiles show that genre is the real decision-maker in this recommender, no matter what the numeric preferences are.
