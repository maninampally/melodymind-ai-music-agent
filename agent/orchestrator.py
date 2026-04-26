import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from agent.schemas import UserQuery, QueryPlan, Recommendation, AgentTrace
from agent.guardrails import validate_input

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")

ROOT = Path(__file__).parent.parent
DB_DIR = ROOT / "chroma_db"
LOGS_DIR = ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("agent")

client = OpenAI(api_key=OPENAI_API_KEY)
chroma_client = chromadb.PersistentClient(path=str(DB_DIR))
embed_fn = OpenAIEmbeddingFunction(api_key=OPENAI_API_KEY, model_name=EMBED_MODEL)


def step_1_plan(query: str) -> QueryPlan:
    logger.info(f"STEP 1 PLAN: parsing query '{query}'")
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": (
                "You parse music recommendation queries. Return JSON with these fields: "
                "intent (string), desired_mood (string or null), desired_genre (string or null), "
                "desired_energy (string: 'low', 'medium', 'high', or null), "
                "keywords (list of strings)."
            )},
            {"role": "user", "content": query},
        ],
    )
    data = json.loads(response.choices[0].message.content)
    plan = QueryPlan(**data)
    logger.info(f"STEP 1 OUTPUT: {plan.model_dump()}")
    return plan


def step_2_retrieve(query: str, plan: QueryPlan, n: int = 10) -> list[dict]:
    logger.info(f"STEP 2 RETRIEVE: searching for top {n} candidates")
    collection = chroma_client.get_collection("songs", embedding_function=embed_fn)
    search_text = f"{query}. Genre: {plan.desired_genre}. Mood: {plan.desired_mood}."
    results = collection.query(query_texts=[search_text], n_results=n)

    candidates = []
    for i, doc in enumerate(results["documents"][0]):
        candidates.append({
            "document": doc,
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i],
        })
    logger.info(f"STEP 2 OUTPUT: retrieved {len(candidates)} candidates")
    return candidates


def step_3_rag_context(plan: QueryPlan) -> list[str]:
    logger.info("STEP 3 RAG: retrieving corpus context")
    collection = chroma_client.get_collection("corpus", embedding_function=embed_fn)
    queries = []
    if plan.desired_genre:
        queries.append(plan.desired_genre)
    if plan.desired_mood:
        queries.append(plan.desired_mood)
    if not queries:
        queries = [plan.intent]

    context_chunks = []
    for q in queries:
        results = collection.query(query_texts=[q], n_results=2)
        for doc in results["documents"][0]:
            if doc not in context_chunks:
                context_chunks.append(doc)
    logger.info(f"STEP 3 OUTPUT: retrieved {len(context_chunks)} context chunks")
    return context_chunks


def step_4_rerank_and_explain(
    query: str, plan: QueryPlan, candidates: list[dict], rag_context: list[str]
) -> list[Recommendation]:
    logger.info(f"STEP 4 RERANK: scoring {len(candidates)} candidates with LLM")

    candidate_text = "\n".join([
        f"{i+1}. {c['metadata']['title']} by {c['metadata']['artist']} "
        f"[{c['metadata']['genre']} / {c['metadata']['mood']}, "
        f"energy={c['metadata']['energy']}, valence={c['metadata']['valence']}]"
        for i, c in enumerate(candidates)
    ])

    rag_text = "\n\n".join(rag_context) if rag_context else "No additional context."

    prompt = f"""User query: "{query}"
User intent: {plan.intent}

Reference knowledge:
{rag_text}

Candidate songs:
{candidate_text}

Pick the top 5 best matches for the user. For each, provide:
- The 1-based index number from the candidate list
- A confidence score from 0.0 to 1.0
- A 1-2 sentence explanation grounded in the reference knowledge above

Return JSON: {{"picks": [{{"index": int, "confidence": float, "explanation": str}}, ...]}}
"""

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a music recommendation expert. Pick songs that match the user's intent and explain why using the reference knowledge."},
            {"role": "user", "content": prompt},
        ],
    )

    data = json.loads(response.choices[0].message.content)
    recommendations = []
    for pick in data.get("picks", [])[:5]:
        idx = pick["index"] - 1
        if 0 <= idx < len(candidates):
            meta = candidates[idx]["metadata"]
            recommendations.append(Recommendation(
                title=meta["title"],
                artist=meta["artist"],
                genre=meta["genre"],
                mood=meta["mood"],
                confidence=pick["confidence"],
                explanation=pick["explanation"],
            ))
    logger.info(f"STEP 4 OUTPUT: {len(recommendations)} final recommendations")
    return recommendations


def step_5_critique(recommendations: list[Recommendation]) -> list[Recommendation]:
    logger.info("STEP 5 CRITIQUE: reviewing confidence scores")
    for rec in recommendations:
        if rec.confidence < 0.5:
            rec.explanation += " [Low confidence: may not be a strong match.]"
    return recommendations


def step_6_log_trace(trace: AgentTrace) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    trace_file = LOGS_DIR / f"trace_{timestamp}.json"
    with open(trace_file, "w", encoding="utf-8") as f:
        json.dump(trace.model_dump(), f, indent=2)
    logger.info(f"STEP 6 LOG: trace saved to {trace_file}")
    return trace_file


def run_agent(raw_query: str) -> tuple[bool, str, AgentTrace | None]:
    start = time.time()

    is_valid, msg, validated = validate_input(raw_query)
    if not is_valid:
        logger.warning(f"GUARDRAIL: rejected input - {msg}")
        return False, msg, None

    try:
        plan = step_1_plan(validated.query)
        candidates = step_2_retrieve(validated.query, plan, n=10)
        rag_context = step_3_rag_context(plan)
        recs = step_4_rerank_and_explain(validated.query, plan, candidates, rag_context)
        recs = step_5_critique(recs)

        trace = AgentTrace(
            query=validated.query,
            plan=plan,
            retrieved_count=len(candidates),
            rag_context_used=rag_context,
            recommendations=recs,
            total_steps=6,
            duration_seconds=round(time.time() - start, 2),
        )
        step_6_log_trace(trace)
        return True, "OK", trace
    except Exception as e:
        logger.error(f"AGENT ERROR: {e}")
        return False, f"Agent failure: {e}", None


if __name__ == "__main__":
    success, msg, trace = run_agent("I want chill lofi for studying")
    if success:
        print(f"\n=== SUCCESS in {trace.duration_seconds}s ===\n")
        for r in trace.recommendations:
            print(f"  [{r.confidence:.2f}] {r.title} - {r.artist}")
            print(f"         {r.explanation}\n")
    else:
        print(f"FAILED: {msg}")
