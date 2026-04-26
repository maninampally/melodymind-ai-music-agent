# Model Card — MelodyMind

## Project Goals

MelodyMind is an agentic LLM music recommendation system that extends the Module 3 rule-based recommender. The original prototype scored songs using hardcoded weights and identified bias problems — specifically, the +2.0 genre weight dominated rankings and created filter bubbles. This project re-architects the system as a 6-step agentic workflow with vector retrieval, RAG-grounded explanations, and an evaluation harness that quantifies the improvement.

---

## Reflection on AI Collaboration

### How AI Was Used in This Project

I used Claude (Anthropic) as the primary AI collaborator throughout this project. AI was used for:

- Architecture brainstorming (reasoning through which Module 1-3 project to extend and why)
- Scaffolding the agent orchestrator (initial 6-step structure)
- Debugging Pydantic validation issues
- Drafting the README and model card
- Suggesting evaluation metrics (diversity, bias gap)

### One Helpful AI Suggestion

When I asked Claude how to make the agent's intermediate reasoning observable for the rubric's "Agentic Workflow Enhancement" stretch feature, it suggested writing each agent step as a separately-named function (`step_1_plan`, `step_2_retrieve`, etc.) and persisting the full `AgentTrace` as JSON to `/logs`. This was more useful than my original plan to just print logs to stdout, because it made the trace inspectable in the Streamlit UI's "Agent Trace" tab and turned the observability into a real product feature, not just debug output.

### One Flawed AI Suggestion

Claude initially recommended using LangChain for the agent framework. After I explained the time constraint (4 hours), it agreed that LangChain would add unnecessary abstraction and dependency overhead for a 6-step pipeline that could be written as plain Python functions. The flaw was that the initial suggestion optimized for "what's industry-standard" rather than "what fits this project's constraints." I had to push back to get the right answer. Lesson: AI defaults toward popular frameworks even when simpler solutions are better.

---

## System Limitations and Biases

### Known Limitations

- **Tiny catalog:** Only 20 songs. Underrepresented genres (rock, metal, classical) have one or two songs each, so the agent has limited material to choose from for those queries.
- **Single LLM dependency:** The system depends entirely on OpenAI's API. Outages or rate limits will break the pipeline. A multi-model fallback would improve robustness.
- **Cost per query:** Each query makes 2-3 LLM calls. At scale this becomes expensive. Caching common query patterns would help.
- **No user feedback loop:** The system cannot learn from "I didn't like this" signals. A real recommender would track user behavior and adjust over time.
- **Embedding model bias:** The OpenAI embedding model has its own biases about what "chill" or "moody" means, inherited from its training data.

### Bias Patterns Observed

- The baseline system consistently overweighted genre match (a +2.0 dominance documented in Module 3).
- The agentic system reduces this bias because the LLM weighs all signals together rather than summing fixed weights, but it introduces a new bias: the LLM tends to over-trust the natural-language descriptions in the RAG corpus, which were written by me.
- For ambiguous queries, the agent shows a slight preference for popular genres (pop, lofi) over niche ones, likely reflecting the embedding model's training data.

---

## Could the System Be Misused?

Possible misuse vectors:

- **Prompt injection in queries:** A malicious user could try to inject instructions into the natural-language query to alter the agent's behavior. Current guardrails handle this with scope filtering, but a more sophisticated attack could bypass it.
- **API key exhaustion:** Without rate limiting, an attacker could spam queries to drain the OpenAI account. Production deployments would need request throttling.
- **Recommendation manipulation:** If the RAG corpus were editable by users, someone could inject promotional text to bias recommendations toward specific artists.

### Mitigations Implemented

- Input length capped at 300 characters
- Out-of-scope keyword filter (refuses non-music queries)
- API key stored in `.env`, never committed
- Trace logging makes manipulation attempts auditable

### Mitigations Recommended for Production

- Rate limiting per user/IP
- LLM-based content moderation on inputs
- Sandboxed corpus updates with review process
- Monitoring for anomalous query patterns

---

## What Surprised Me

The biggest surprise was how dramatically the agentic system fixed the genre filter bubble identified in Module 3. The baseline almost always returned 5 songs from the user's preferred genre. The agentic system returns a more diverse mix because the LLM treats genre as one signal among many rather than a hard +2.0 weight. The bias didn't go away — it just shifted from "categorical lock-in" to "LLM has its own biases" — but the kinds of recommendations the user sees feel more useful and less repetitive.

The second surprise was how much the structured output (Pydantic + JSON mode) constrained the agent's failure modes. When I let the LLM return free-form text, it was unpredictable. When I forced JSON output matching a schema, the failures became visible and recoverable. Schema-first design is underrated for LLM systems.

---

## Testing Summary

- **5/5 evaluation profiles** completed end-to-end without errors
- **Diversity score** improved on 4 of 5 profiles (baseline often returned 5 songs of the same genre)
- **Guardrails** correctly rejected 100% of out-of-scope queries in manual testing
- **Confidence scores** averaged 0.72 across all profiles, with low-confidence flags appearing for 2 of the 25 total recommendations
- **Latency** averaged 4-6 seconds per query (3 LLM calls + 2 vector searches)

---

## Future Improvements

- Add a multi-turn conversation mode (refine recommendations based on follow-ups)
- Replace the 20-song catalog with a real Spotify playlist via API
- Add a feedback loop where the user can thumbs-up/down recommendations and the agent adjusts its re-ranking weights
- Add LLM-as-judge evaluation in the harness to score explanation quality automatically
- Add Anthropic Claude as a fallback model for cost/availability resilience
