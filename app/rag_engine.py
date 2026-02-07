"""LightRAG knowledge graph engine with local storage."""

import asyncio
import os
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import openai_complete, openai_embed
from lightrag.utils import EmbeddingFunc
from app import config


# Module-level RAG instance (initialized lazily)
_rag: LightRAG | None = None


async def _create_rag() -> LightRAG:
    """Create and initialize a LightRAG instance."""
    os.makedirs(config.RAG_WORKING_DIR, exist_ok=True)

    rag = LightRAG(
        working_dir=config.RAG_WORKING_DIR,
        llm_model_func=openai_complete,
        llm_model_name=config.GROK_MODEL,
        llm_model_kwargs={
            "base_url": config.XAI_BASE_URL,
            "api_key": config.XAI_API_KEY,
        },
        embedding_func=EmbeddingFunc(
            embedding_dim=1536,
            max_token_size=8192,
            func=lambda texts: openai_embed.func(
                texts, api_key=config.OPENAI_API_KEY
            ),
        ),
        chunk_token_size=config.CHUNK_TOKEN_SIZE,
        chunk_overlap_token_size=config.CHUNK_OVERLAP_TOKEN_SIZE,
    )
    await rag.initialize_storages()
    return rag


async def get_rag() -> LightRAG:
    """Get or create the singleton RAG instance."""
    global _rag
    if _rag is None:
        _rag = await _create_rag()
    return _rag


async def insert_document(text: str) -> None:
    """Insert document text into the knowledge graph."""
    rag = await get_rag()
    await rag.ainsert(text)


async def query(question: str, mode: str = "hybrid") -> str:
    """Query the knowledge graph. Modes: naive, local, global, hybrid, mix."""
    rag = await get_rag()
    return await rag.aquery(question, param=QueryParam(mode=mode))


def insert_document_sync(text: str) -> None:
    """Synchronous wrapper for insert_document."""
    asyncio.get_event_loop().run_until_complete(insert_document(text))


def query_sync(question: str, mode: str = "hybrid") -> str:
    """Synchronous wrapper for query."""
    return asyncio.get_event_loop().run_until_complete(query(question, mode))
