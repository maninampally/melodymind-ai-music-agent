"""MelodyMind Streamlit UI: baseline vs agentic music recommender."""
import streamlit as st
from pathlib import Path
from src.recommender import recommend_songs, load_songs
from agent.orchestrator import run_agent

DATA_PATH = str(Path(__file__).parent / "data" / "songs.csv")

st.set_page_config(page_title="MelodyMind", page_icon="🎵", layout="wide")

st.title("🎵 MelodyMind: AI Music Recommendation Agent")
st.caption("Module 3 baseline (rule-based) vs Project 4 agentic LLM system")

tab1, tab2, tab3 = st.tabs(["🧠 Agentic Mode", "📊 Baseline Mode", "📜 Agent Trace"])

with tab1:
    st.subheader("Ask in plain language")
    query = st.text_input(
        "What kind of music do you want?",
        placeholder="e.g. chill lofi for studying late at night",
    )
    if st.button("Recommend", type="primary"):
        if not query:
            st.warning("Please enter a query.")
        else:
            with st.spinner("Agent is thinking..."):
                success, msg, trace = run_agent(query)
            if not success:
                st.error(msg)
            else:
                st.success(f"Got 5 recommendations in {trace.duration_seconds}s")
                for i, rec in enumerate(trace.recommendations, 1):
                    with st.container(border=True):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**#{i} {rec.title}** — *{rec.artist}*")
                            st.caption(f"{rec.genre} / {rec.mood}")
                            st.write(rec.explanation)
                        with col2:
                            st.metric("Confidence", f"{rec.confidence:.2f}")
                st.session_state["last_trace"] = trace

with tab2:
    st.subheader("Original Module 3 Rule-Based Recommender")
    col1, col2 = st.columns(2)
    with col1:
        genre = st.selectbox("Favorite genre", ["pop", "lofi", "rock", "edm", "indie pop", "hip hop", "synthwave", "metal"])
        mood = st.selectbox("Favorite mood", ["happy", "chill", "focused", "intense", "moody", "nostalgic", "euphoric", "aggressive"])
    with col2:
        energy = st.slider("Target energy", 0.0, 1.0, 0.5)
        valence = st.slider("Target valence", 0.0, 1.0, 0.5)

    if st.button("Get Baseline Recommendations"):
        songs = load_songs(DATA_PATH)
        user_prefs = {
            "favorite_genre": genre,
            "favorite_mood": mood,
            "target_energy": energy,
            "target_valence": valence,
        }
        results = recommend_songs(user_prefs, songs, k=5)
        for i, r in enumerate(results, 1):
            with st.container(border=True):
                st.markdown(f"**#{i} {r['song']['title']}** — *{r['song']['artist']}*")
                st.caption(f"{r['song']['genre']} / {r['song']['mood']}")
                st.write(f"Score: {r['score']:.2f}")
                st.write("  •  ".join(r["reasons"]))

with tab3:
    st.subheader("Last Agent Trace (Observability)")
    trace = st.session_state.get("last_trace")
    if trace is None:
        st.info("Run an agent query first to see its full reasoning trace here.")
    else:
        st.json(trace.model_dump())
