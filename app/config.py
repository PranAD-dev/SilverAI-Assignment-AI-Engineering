"""Application configuration loaded from environment variables."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
RAG_WORKING_DIR = os.getenv("LIGHTRAG_WORKING_DIR", str(PROJECT_ROOT / "rag_storage"))

# xAI / Grok
XAI_API_KEY = os.getenv("XAI_API_KEY", "")
XAI_BASE_URL = "https://api.x.ai/v1"
GROK_MODEL = "grok-4-1-fast-non-reasoning"  # 2M context, cheapest variant

# OpenAI (for embeddings)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

# PostgreSQL (Supabase direct connection for LightRAG)
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE", "postgres")

# LightRAG tuning
CHUNK_TOKEN_SIZE = 1200
CHUNK_OVERLAP_TOKEN_SIZE = 100


def validate():
    """Check that required env vars are set. Returns list of missing keys."""
    required = {
        "XAI_API_KEY": XAI_API_KEY,
        "OPENAI_API_KEY": OPENAI_API_KEY,
    }
    missing = [k for k, v in required.items() if not v]
    return missing
