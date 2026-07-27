import logging
import os
from typing import Any, AsyncGenerator

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
        "X-Title": "BOUGH",
        "HTTP-Referer": "https://github.com/erfee7/BOUGH", 
    }
        
    _client = AsyncOpenAI(
        api_key=api_key, 
        base_url=base_url,
        default_headers=default_headers
    )
    logger.info("AsyncOpenAI client initialized.")
    return _client

def _format_history(messages_history: list[dict[str, Any]]) -> list[dict[str, str]]:
    """
    Strips database metadata and formats the history into the strict 
    [{"role": "...", "content": "..."}] format required by the OpenAI SDK.
    """
    formatted = []
    for msg in messages_history:
        # Only include role and content. We also ensure content is a string (handles None)
        formatted.append({
            "role": msg["role"],
            "content": msg["content"] or ""
        })
    return formatted

async def generate_stream(
    messages_history: list[dict[str, Any]], 
    model: str | None = None, 
    client: AsyncOpenAI | None = None
) -> AsyncGenerator[dict[str, Any], None]:
    """
    Calls the LLM provider and yields structured events.
    
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
    
    try:
        # stream_options={"include_usage": True} is critical to get the final cost chunk
        stream = await active_client.chat.completions.create(
            model=target_model,
            messages=formatted_history,
            stream=True,
            stream_options={"include_usage": True}
        )
        
        async for chunk in stream:
            # Extract usage metadata if it exists (final chunk)
            if chunk.usage:
                # Convert pydantic model to dict for easy JSON serialization later
                yield {
                    "type": "done", 
                    "metadata": chunk.usage.model_dump()
                }
            
            # Extract text token if it exists
            if chunk.choices and chunk.choices[0].delta:
                # Use model_dump() to capture non-standard fields like 'reasoning'
                delta_dict = chunk.choices[0].delta.model_dump()
                content = delta_dict.get('content')
                reasoning = delta_dict.get('reasoning') or delta_dict.get('reasoning_content')
                
                if content:
                    yield {"type": "token", "content": content}
                if reasoning:
                    yield {"type": "reasoning", "content": reasoning}
                
    except Exception as e:
        # Catching generic Exception to ensure the background task doesn't die abruptly
        logger.error("LLM provider stream failed: %s", e)
        yield {
            "type": "error", 
            "error_data": {
                "message": str(e), 
                "type": type(e).__name__
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