import logging
from fastapi import APIRouter, HTTPException

from app.llm.provider import list_models
from app.schemas.chat import ModelResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["models"])

@router.get("/models", response_model=list[ModelResponse])
async def get_models(force: bool = False):
    """Fetches the list of available models from the provider."""
    try:
        models = await list_models(force=force)
        return [ModelResponse.model_validate(m) for m in models]
    except Exception as e:
        logger.error("Failed to fetch models from provider: %s", e)
        raise HTTPException(status_code=502, detail="Failed to fetch models from provider.")