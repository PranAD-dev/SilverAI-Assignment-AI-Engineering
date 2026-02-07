"""Grok 4.1 LLM client using OpenAI-compatible API."""

from openai import OpenAI
from app.config import XAI_API_KEY, XAI_BASE_URL, GROK_MODEL


def get_client() -> OpenAI:
    return OpenAI(api_key=XAI_API_KEY, base_url=XAI_BASE_URL)


def chat(
    prompt: str,
    *,
    system: str | None = None,
    model: str = GROK_MODEL,
    max_tokens: int = 4096,
    temperature: float = 0.7,
) -> str:
    """Send a single-turn chat request to Grok and return the response text."""
    client = get_client()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message.content or ""


def chat_stream(
    prompt: str,
    *,
    system: str | None = None,
    model: str = GROK_MODEL,
    max_tokens: int = 4096,
    temperature: float = 0.7,
):
    """Stream a chat response from Grok, yielding text chunks."""
    client = get_client()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
