import logging
import os
import time
import base64
from typing import Any, AsyncGenerator

import httpx
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# Module-level singleton for the AsyncOpenAI client
_client: AsyncOpenAI | None = None

def _get_client() -> AsyncOpenAI:
    """Initializes and returns the AsyncOpenAI client singleton."""
    global _client
    if _client is not None:
        return _client
    
    api_key = os.getenv("PROVIDER_API_KEY")
    base_url = os.getenv("PROVIDER_BASE_URL", "https://openrouter.ai/api/v1")
    
    if not api_key:
        logger.error("PROVIDER_API_KEY is missing from environment variables.")
        raise ValueError("PROVIDER_API_KEY is not set.")
        
    # Define the OpenRouter attribution headers
    default_headers = {
        "X-OpenRouter-Title": "BOUGH",
        "HTTP-Referer": "https://github.com/erfee7/BOUGH", 
    }
        
    _client = AsyncOpenAI(
        api_key=api_key, 
        base_url=base_url,
        default_headers=default_headers
    )
    logger.info("AsyncOpenAI client initialized.")
    return _client

def _build_content_parts(content: str | None, attachments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Assembles the multimodal content array from a message's text and its enriched
    attachment dicts (raw bytes under the "data" key, injected by the stream manager).
    Text first (OpenRouter's recommendation), then attachments in the user's chosen
    order. The text part is omitted entirely for attachment-only messages.
    """
    parts: list[dict[str, Any]] = []

    text = content or ""
    if text:
        parts.append({"type": "text", "text": text})

    for att in attachments:
        mime_type = att["mime_type"]
        b64 = base64.b64encode(att["data"]).decode("utf-8")

        if mime_type in ("image/png", "image/jpeg", "image/webp", "image/gif"):
            parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{b64}"}
            })
        elif mime_type == "application/pdf":
            parts.append({
                "type": "file",
                "file": {
                    "filename": att["filename"],
                    "file_data": f"data:application/pdf;base64,{b64}"
                }
            })
        else:
            # Internal failure, not a provider failure: unknown types must
            # never be silently dropped. Escapes the generator (before the try block)
            # and lands in the stream manager's outer except -> honest error status.
            raise ValueError(f"Cannot assemble provider content for unsupported MIME type: {mime_type}")

    return parts

def _format_history(messages_history: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Strips database metadata and formats the history for the OpenAI SDK.
    Text-only messages (the common case) stay plain strings; messages carrying
    attachments become multimodal content arrays, text part first.
    """
    formatted = []
    for msg in messages_history:
        # .get(): titler-built payloads lack the "attachments" key entirely
        attachments = msg.get("attachments") or []
        if attachments:
            formatted.append({
                "role": msg["role"],
                "content": _build_content_parts(msg["content"], attachments)
            })
        else:
            formatted.append({
                "role": msg["role"],
                "content": msg["content"] or ""
            })
    return formatted

async def generate_stream(
    messages_history: list[dict[str, Any]], 
    model: str | None = None,
    parameters: dict[str, Any] | None = None,
    client: AsyncOpenAI | None = None
) -> AsyncGenerator[dict[str, Any], None]:
    """
    Calls the LLM provider and yields structured events.
    
    Custom parameters are merged into the request body as-is (via extra_body).
    Reserved keys are already filtered at the router layer.
    
    Yields:
        {"type": "token", "content": "..."} for text chunks.
        {"type": "reasoning", "content": "..."} for reasoning chunks.
        {"type": "done", "metadata": {...}} at the end of the stream.
        {"type": "error", "error_data": {...}} if an exception occurs.
    """
    active_client = client or _get_client()
    target_model = model or os.getenv("DEFAULT_MODEL", "openrouter/free")
    
    # Format the history right before sending to the provider
    formatted_history = _format_history(messages_history)
    
    logger.info("Dispatching request to LLM provider (Model: %s, Messages: %d)", target_model, len(formatted_history))
    
    usage_metadata = {}
    
    try:
        # stream_options={"include_usage": True} is critical to get the final cost chunk
        stream = await active_client.chat.completions.create(
            model=target_model,
            messages=formatted_history,
            stream=True,
            stream_options={"include_usage": True},
            extra_body=parameters or None
        )
        
        try:
            async for chunk in stream:
                if chunk.usage:
                    usage_metadata = chunk.usage.model_dump()
                
                if chunk.choices and chunk.choices[0].delta:
                    delta_dict = chunk.choices[0].delta.model_dump()
                    content = delta_dict.get('content')
                    reasoning = delta_dict.get('reasoning') or delta_dict.get('reasoning_content')
                    
                    if content:
                        yield {"type": "token", "content": content}
                    if reasoning:
                        yield {"type": "reasoning", "content": reasoning}
        finally:
            # Explicitly close the OpenAI AsyncStream to drop the HTTP connection immediately.
            # This triggers GeneratorExit unwinding when cancelled from the outside.
            await stream.close()
                
        # If the loop finishes without exception, yield done exactly once
        yield {"type": "done", "metadata": usage_metadata}
                
    except Exception as e:
        # Catching generic Exception to ensure the background task doesn't die abruptly
        logger.error("LLM provider stream failed: %s", e)
        
        # Extract the structured body if it exists (OpenAI SDK puts the JSON dict in e.body)
        error_body = {}
        if hasattr(e, 'body') and isinstance(e.body, dict):
            error_body = e.body
            
        yield {
            "type": "error", 
            "error_data": {
                "message": str(e), 
                "type": type(e).__name__,
                "body": error_body
            }
        }

async def generate_completion(
    messages_history: list[dict[str, Any]], 
    model: str | None = None, 
    client: AsyncOpenAI | None = None
) -> dict[str, Any]:
    """
    Calls the LLM provider with a non-streaming request.
    Returns a dict: {"content": str, "usage": dict}.
    """
    active_client = client or _get_client()
    target_model = model or os.getenv("TITLER_MODEL", os.getenv("DEFAULT_MODEL", "openrouter/free"))
    
    formatted_history = _format_history(messages_history)
    
    logger.info("Dispatching non-streaming request to LLM provider (Model: %s, Messages: %d)", target_model, len(formatted_history))
    
    try:
        response = await active_client.chat.completions.create(
            model=target_model,
            messages=formatted_history,
            stream=False
        )
        
        content = response.choices[0].message.content or ""
        usage = response.usage.model_dump() if response.usage else {}
        
        return {
            "content": content,
            "usage": usage
        }
        
    except Exception as e:
        logger.error("LLM provider completion failed: %s", e)
        return {
            "content": "",
            "usage": {},
            "error": str(e)
        }

# Module-level cache for models list
_models_cache: list[dict] | None = None
_models_cache_at: float | None = None
_MODELS_CACHE_TTL = 24 * 3600  # 24 hours in seconds

async def list_models(force: bool = False) -> list[dict]:
    """
    Fetches the list of available models from the provider.
    Uses an in-memory cache with a 24h TTL. Fails honestly if the fetch fails.
    """
    global _models_cache, _models_cache_at
    now = time.time()
    
    if not force and _models_cache is not None and _models_cache_at is not None:
        if now - _models_cache_at < _MODELS_CACHE_TTL:
            logger.info("Returning models from in-memory cache.")
            return _models_cache
            
    logger.info("Fetching fresh models from provider (force=%s)...", force)
    base_url = os.getenv("PROVIDER_BASE_URL", "https://openrouter.ai/api/v1")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/models")
            response.raise_for_status()
            data = response.json()
            
        # Minimal mapping: just id and name
        models = [
            {"id": m["id"], "name": m["name"]}
            for m in data.get("data", [])
        ]
        
        _models_cache = models
        _models_cache_at = time.time()
        logger.info("Successfully fetched and cached %d models.", len(models))
        return models
        
    except Exception as e:
        logger.error("Failed to fetch models from provider: %s", e)
        raise Exception("Failed to fetch models from provider.") from e