import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")

DB_DIR = ROOT / "chroma_db"
LOGS_DIR = ROOT / "logs"
SONGS_CSV = ROOT / "data" / "songs.csv"
CORPUS_DIR = ROOT / "rag" / "corpus"

LOGS_DIR.mkdir(exist_ok=True)

RETRIEVAL_CANDIDATES = 10
RAG_CONTEXT_PER_QUERY = 2
MAX_RECOMMENDATIONS = 5
LOW_CONFIDENCE_THRESHOLD = 0.5
