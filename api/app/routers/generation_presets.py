import logging
import uuid
from fastapi import APIRouter, HTTPException

from app.db import generation_presets as db_presets
from app.schemas.chat import (
    PresetCreateRequest, 
    PresetUpdateRequest, 
    PresetResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["generation-presets"])

@router.get("/presets", response_model=list[PresetResponse])
async def list_presets():
    """Fetches all generation presets."""
    records = await db_presets.fetch_all_presets()
    return [PresetResponse.model_validate(rec) for rec in records]

@router.post("/presets", response_model=PresetResponse)
async def create_preset(payload: PresetCreateRequest):
    """Creates a new generation preset."""
    # Ensure parameters is a dict, default to empty dict if None
    params = payload.parameters if payload.parameters is not None else {}
    preset_id = await db_presets.create_preset(
        name=payload.name,
        model=payload.model,
        parameters=params
    )
    record = await db_presets.fetch_preset(preset_id)
    return PresetResponse.model_validate(record)

@router.get("/presets/{preset_id}", response_model=PresetResponse)
async def get_preset(preset_id: uuid.UUID):
    """Fetches a single generation preset by ID."""
    record = await db_presets.fetch_preset(preset_id)
    if not record:
        raise HTTPException(status_code=404, detail="Generation preset not found")
    return PresetResponse.model_validate(record)

@router.patch("/presets/{preset_id}", response_model=PresetResponse)
async def update_preset(preset_id: uuid.UUID, payload: PresetUpdateRequest):
    """Updates a generation preset."""
    record = await db_presets.fetch_preset(preset_id)
    if not record:
        raise HTTPException(status_code=404, detail="Generation preset not found")
    
    update_data = payload.model_dump(exclude_unset=True)

    # Ensure parameters is a dict if provided
    if 'parameters' in update_data and update_data['parameters'] is None:
        update_data['parameters'] = {}

    if update_data:
        await db_presets.update_preset(preset_id, **update_data)

    updated_record = await db_presets.fetch_preset(preset_id)
    return PresetResponse.model_validate(updated_record)

@router.delete("/presets/{preset_id}")
async def delete_preset(preset_id: uuid.UUID):
    """Deletes a generation preset."""
    record = await db_presets.fetch_preset(preset_id)
    if not record:
        raise HTTPException(status_code=404, detail="Generation preset not found")

    await db_presets.delete_preset(preset_id)