import csv
import sys
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from config import OPENAI_API_KEY, OPENAI_EMBED_MODEL as EMBED_MODEL, SONGS_CSV, CORPUS_DIR, DB_DIR

if not OPENAI_API_KEY:
    print("ERROR: OPENAI_API_KEY not found in .env file")
    sys.exit(1)


def song_to_text(row: dict) -> str:
    """Convert a song row into a rich text representation for embedding."""
    return (
        f"Title: {row['title']}. Artist: {row['artist']}. "
        f"Genre: {row['genre']}. Mood: {row['mood']}. "
        f"Energy: {row['energy']} (0=calm, 1=intense). "
        f"Tempo: {row['tempo_bpm']} BPM. "
        f"Valence: {row['valence']} (0=sad, 1=happy)."
    )


def build_song_index(client):
    """Embed and store all songs."""
    print("Building song index...")
    embed_fn = OpenAIEmbeddingFunction(
        api_key=OPENAI_API_KEY,
        model_name=EMBED_MODEL,
    )
    collection = client.get_or_create_collection(
        name="songs",
        embedding_function=embed_fn,
    )

    documents = []
    metadatas = []
    ids = []

    with open(SONGS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            documents.append(song_to_text(row))
            metadatas.append({
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": int(row["tempo_bpm"]),
                "valence": float(row["valence"]),
            })
            ids.append(f"song_{i}")

    collection.add(documents=documents, metadatas=metadatas, ids=ids)
    print(f"Indexed {len(documents)} songs.")


def build_corpus_index(client):
    """Embed and store the RAG knowledge corpus."""
    print("Building corpus index...")
    embed_fn = OpenAIEmbeddingFunction(
        api_key=OPENAI_API_KEY,
        model_name=EMBED_MODEL,
    )
    collection = client.get_or_create_collection(
        name="corpus",
        embedding_function=embed_fn,
    )

    documents = []
    metadatas = []
    ids = []

    for md_file in CORPUS_DIR.glob("*.md"):
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        # Split by ## headers into sections
        sections = content.split("\n## ")
        for i, section in enumerate(sections):
            if not section.strip():
                continue
            documents.append(section.strip())
            metadatas.append({
                "source": md_file.name,
                "section_index": i,
            })
            ids.append(f"{md_file.stem}_{i}")

    collection.add(documents=documents, metadatas=metadatas, ids=ids)
    print(f"Indexed {len(documents)} corpus sections.")


def main():
    print(f"Initializing ChromaDB at {DB_DIR}...")
    DB_DIR.mkdir(exist_ok=True)
    client = chromadb.PersistentClient(path=str(DB_DIR))

    # Clear old collections
    try:
        client.delete_collection("songs")
    except Exception:
        pass
    try:
        client.delete_collection("corpus")
    except Exception:
        pass

    build_song_index(client)
    build_corpus_index(client)
    print("Index build complete.")


if __name__ == "__main__":
    main()