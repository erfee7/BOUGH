import logging
import uuid
from fastapi import APIRouter, HTTPException
from typing import Optional

from app.db import prompts as db_prompts
from app.schemas.chat import (
    PromptCreateRequest, 
    PromptUpdateRequest, 
    PromptResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["prompts"])

@router.get("/prompts", response_model=list[PromptResponse])
async def list_prompts(role: Optional[str] = None):
    """Fetches all prompts, optionally filtered by role."""
    records = await db_prompts.fetch_all_prompts(role=role)
    return [PromptResponse.model_validate(rec) for rec in records]

@router.post("/prompts", response_model=PromptResponse)
async def create_prompt(payload: PromptCreateRequest):
    """Creates a new prompt."""
    prompt_id = await db_prompts.create_prompt(
        name=payload.name,
        content=payload.content,
        role=payload.role,
        description=payload.description
    )
    prompt_record = await db_prompts.fetch_prompt(prompt_id)
    return PromptResponse.model_validate(prompt_record)

@router.get("/prompts/{prompt_id}", response_model=PromptResponse)
async def get_prompt(prompt_id: uuid.UUID):
    """Fetches a single prompt by ID."""
    record = await db_prompts.fetch_prompt(prompt_id)
    if not record:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return PromptResponse.model_validate(record)

@router.patch("/prompts/{prompt_id}", response_model=PromptResponse)
async def update_prompt(prompt_id: uuid.UUID, payload: PromptUpdateRequest):
    """Updates a prompt."""
    record = await db_prompts.fetch_prompt(prompt_id)
    if not record:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    update_data = payload.model_dump(exclude_unset=True)

    # If there are fields to update, call the DB layer
    if update_data:
        await db_prompts.update_prompt(prompt_id, **update_data)

    # Fetch the updated record and return it
    updated_record = await db_prompts.fetch_prompt(prompt_id)
    return PromptResponse.model_validate(updated_record)

@router.delete("/prompts/{prompt_id}")
async def delete_prompt(prompt_id: uuid.UUID):
    """Deletes a prompt."""
    record = await db_prompts.fetch_prompt(prompt_id)
    if not record:
        raise HTTPException(status_code=404, detail="Prompt not found")

    await db_prompts.delete_prompt(prompt_id)