from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..models.schemas import Interaction, Medicine
from ..services.data_store import get_store


router = APIRouter(prefix="/api/medicines", tags=["medicines"])


@router.get("/{drug_id}", response_model=Medicine)
def get_medicine(drug_id: int) -> Medicine:
    medicine = get_store().medicine(drug_id)
    if medicine is None:
        raise HTTPException(status_code=404, detail=f"Drug {drug_id} not found")
    return medicine


@router.get("/{drug_id}/interactions", response_model=list[Interaction])
def get_interactions(drug_id: int, limit: int = 25) -> list[Interaction]:
    store = get_store()
    if store.medicine(drug_id) is None:
        raise HTTPException(status_code=404, detail=f"Drug {drug_id} not found")
    return store.interactions_for(drug_id, limit=limit)
